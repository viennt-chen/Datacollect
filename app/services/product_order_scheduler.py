"""
定时任务服务 - 定期自动遍历产品表并查询订单
"""
import asyncio
import logging
import uuid
from datetime import datetime, timedelta
from typing import Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session
from app.models.material import Material
from app.models.product_order_log import ProductOrderQueryLog
from app.routers.erp_orders import query_u9_order_with_details, save_order_to_db_with_upsert
from app.core.redis_client import get_redis
from app.services.u9_service import U9ServiceError, U9NetworkError, U9TimeoutError, U9DataError

logger = logging.getLogger(__name__)


class DistributedLock:
    """基于 Redis 的分布式锁"""
    
    def __init__(self, lock_key: str, expire_seconds: int = 3600):
        self.lock_key = f"lock:product_order_scheduler:{lock_key}"
        self.expire_seconds = expire_seconds
        self.lock_value = str(uuid.uuid4())
        self.redis_client = get_redis()
    
    async def acquire(self) -> bool:
        """尝试获取锁"""
        if not self.redis_client:
            logger.warning("Redis 未启用，跳过分布式锁")
            return True
        
        try:
            # 使用 SET NX EX 命令实现分布式锁
            result = self.redis_client.set(
                self.lock_key,
                self.lock_value,
                nx=True,
                ex=self.expire_seconds
            )
            if result:
                logger.info(f"成功获取分布式锁: {self.lock_key}")
                return True
            else:
                logger.warning(f"获取分布式锁失败，可能有其他实例正在执行: {self.lock_key}")
                return False
        except Exception as e:
            logger.error(f"获取分布式锁异常: {e}")
            return False
    
    async def release(self):
        """释放锁"""
        if not self.redis_client:
            return
        
        try:
            # 使用 Lua 脚本确保只释放自己的锁
            lua_script = """
            if redis.call("get", KEYS[1]) == ARGV[1] then
                return redis.call("del", KEYS[1])
            else
                return 0
            end
            """
            self.redis_client.eval(lua_script, 1, self.lock_key, self.lock_value)
            logger.info(f"成功释放分布式锁: {self.lock_key}")
        except Exception as e:
            logger.error(f"释放分布式锁异常: {e}")


class ProductOrderScheduler:
    """产品订单定时任务调度器"""
    
    def __init__(self, db_session_func):
        """
        初始化调度器
        
        Args:
            db_session_func: 数据库 session 工厂函数
        """
        self.db_session_func = db_session_func
        self.scheduler = AsyncIOScheduler()
        self.is_running = False
        self.last_run_time: Optional[datetime] = None
        self.last_run_stats: dict = {}
        
    def start(self, cron_expression: str = "*/30 * * * *"):
        """
        启动定时任务
        
        Args:
            cron_expression: Cron 表达式，默认为每30分钟执行一次
                           格式：分 时 日 月 星期
        """
        try:
            # 添加定时任务
            self.scheduler.add_job(
                self.run_auto_query,
                trigger=CronTrigger.from_crontab(cron_expression),
                id='auto_product_order_query',
                name='自动遍历产品表查询订单',
                replace_existing=True
            )
            
            # 启动调度器
            self.scheduler.start()
            self.is_running = True
            
            logger.info(f"产品订单定时任务已启动，Cron 表达式：{cron_expression}")
            logger.info(f"下次执行时间：{self.get_next_run_time()}")
            
        except Exception as e:
            logger.error(f"启动定时任务失败：{e}")
            raise
    
    def stop(self):
        """停止定时任务"""
        try:
            if self.scheduler.running:
                self.scheduler.shutdown(wait=False)
                self.is_running = False
                logger.info("产品订单定时任务已停止")
        except Exception as e:
            logger.error(f"停止定时任务失败：{e}")
    
    def get_next_run_time(self) -> Optional[datetime]:
        """获取下次运行时间"""
        try:
            job = self.scheduler.get_job('auto_product_order_query')
            if job:
                return job.next_run_time
        except Exception as e:
            logger.error(f"获取下次运行时间失败：{e}")
        return None
    
    async def run_auto_query(self):
        """执行自动查询任务"""
        # 尝试获取分布式锁
        lock = DistributedLock("auto_query", expire_seconds=3600)
        lock_acquired = await lock.acquire()
        
        if not lock_acquired:
            logger.warning("跳过本次定时任务执行：其他实例正在执行中")
            return
        
        try:
            await self._execute_query()
        finally:
            # 确保释放锁
            await lock.release()
    
    async def _execute_query(self):
        """执行实际的查询任务（使用并发优化）"""
        logger.info("=" * 60)
        logger.info("开始执行定时任务：自动遍历产品表查询订单")
        logger.info(f"执行时间：{datetime.now()}")
        
        start_time = datetime.now()
        
        db = None
        try:
            db = next(self.db_session_func())
            
            # 只查询产品和半成品类型的物料（作为U9订单查询依据）
            products = db.query(Material).filter(
                Material.status == 'active',
                Material.material_type.in_(['product', 'semi_finished']),
                Material.u9_material_code.isnot(None),
                Material.u9_material_code != ''
            ).all()
            
            unique_materials = {}
            for product in products:
                material_code = product.u9_material_code
                if material_code not in unique_materials:
                    unique_materials[material_code] = product
            
            total_materials = len(unique_materials)
            logger.info(f"找到 {total_materials} 个唯一 U9 料号（共 {len(products)} 个物料）")
            
            success_count = 0
            failed_count = 0
            total_saved = 0
            
            # 使用并发处理（最多并发3个，避免对U9系统造成过大压力）
            semaphore = asyncio.Semaphore(3)
            
            async def query_single_material(material_code, product):
                """查询单个物料的订单"""
                nonlocal success_count, failed_count, total_saved
                
                async with semaphore:
                    product_start = datetime.now()
                    product_db = next(self.db_session_func())
                    
                    try:
                        logger.info(f"正在查询 U9 料号：{material_code}")
                        
                        query_date = datetime.now()
                        date_str = query_date.strftime("%Y-%m-%d")
                        
                        order_data = await query_u9_order_with_details(
                            specs="",
                            start_date=date_str,
                            end_date=date_str,
                            item_code=material_code
                        )
                        
                        product_duration = (datetime.now() - product_start).total_seconds()
                        
                        if order_data.get('details'):
                            saved_count = await save_order_to_db_with_upsert(
                                db=product_db,
                                part_number=product.part_number,
                                u9_material_code=material_code,
                                specs=product.specification or product.part_number,
                                order_data=order_data,
                                query_date=date_str
                            )
                            
                            # 累加统计（需要加锁）
                            nonlocal total_saved, success_count
                            total_saved += saved_count
                            success_count += 1
                            
                            logger.info(f"  ✓ 成功：计划产量 {order_data.get('planned_output', 0)}, "
                                      f"订单数 {len(order_data.get('details', []))}, "
                                      f"保存 {saved_count} 条")
                        else:
                            logger.info(f"  - 无订单数据")
                            success_count += 1
                        
                    except U9TimeoutError as e:
                        failed_count += 1
                        logger.error(f"  ✗ U9 接口超时 [{material_code}]: {e}")
                        self._log_query_error(product_db, product, date_str, product_start, str(e), "timeout")
                        
                    except U9NetworkError as e:
                        failed_count += 1
                        logger.error(f"  ✗ U9 网络错误 [{material_code}]: {e}")
                        self._log_query_error(product_db, product, date_str, product_start, str(e), "network_error")
                        
                    except U9DataError as e:
                        failed_count += 1
                        logger.error(f"  ✗ U9 数据格式错误 [{material_code}]: {e}")
                        self._log_query_error(product_db, product, date_str, product_start, str(e), "data_error")
                        
                    except U9ServiceError as e:
                        failed_count += 1
                        logger.error(f"  ✗ U9 服务异常 [{material_code}]: {e}")
                        self._log_query_error(product_db, product, date_str, product_start, str(e), "u9_service_error")
                        
                    except Exception as e:
                        failed_count += 1
                        logger.error(f"  ✗ 未知异常 [{material_code}]: {e}", exc_info=True)
                        self._log_query_error(product_db, product, date_str, product_start, str(e), "unknown_error")
                    finally:
                        product_db.close()
            
            # 并发执行所有物料查询
            tasks = []
            for material_code, product in unique_materials.items():
                task = query_single_material(material_code, product)
                tasks.append(task)
            
            # 等待所有任务完成
            await asyncio.gather(*tasks, return_exceptions=True)
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            self.last_run_time = datetime.now()
            self.last_run_stats = {
                "total_materials": total_materials,
                "success_count": success_count,
                "failed_count": failed_count,
                "total_saved": total_saved,
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "duration_seconds": duration
            }
            
            logger.info("=" * 60)
            logger.info("定时任务执行完成")
            logger.info(f"总计：{total_materials} 个唯一物料")
            logger.info(f"成功：{success_count} 个")
            logger.info(f"失败：{failed_count} 个")
            logger.info(f"保存订单：{total_saved} 条")
            logger.info(f"耗时：{duration:.2f} 秒")
            logger.info("=" * 60)
            
        except Exception as e:
            logger.error(f"定时任务执行失败：{e}", exc_info=True)
        finally:
            if db:
                db.close()
    
    def _log_query_error(self, db, product, date_str, product_start, error_message, error_type):
        """记录查询错误日志"""
        try:
            product_duration = (datetime.now() - product_start).total_seconds()
            
            query_log = ProductOrderQueryLog(
                part_number=product.part_number,
                specs=product.specification or product.part_number,
                status='failed',
                error_message=error_message,
                query_date=date_str,
                execution_type='auto',
                duration_seconds=product_duration
            )
            db.add(query_log)
            db.commit()
        except Exception as log_error:
            logger.error(f"记录日志失败：{log_error}")
    
    def get_status(self) -> dict:
        """获取调度器状态"""
        return {
            "is_running": self.is_running,
            "last_run_time": self.last_run_time.isoformat() if self.last_run_time else None,
            "last_run_stats": self.last_run_stats,
            "next_run_time": self.get_next_run_time().isoformat() if self.get_next_run_time() else None
        }


# 全局调度器实例（将在 main.py 中初始化）
_scheduler: Optional[ProductOrderScheduler] = None


def get_scheduler() -> Optional[ProductOrderScheduler]:
    """获取全局调度器实例"""
    return _scheduler


def init_scheduler(db_session_func, cron_expression: str = "0 2 * * *"):
    """
    初始化全局调度器
    
    Args:
        db_session_func: 数据库 session 工厂函数
        cron_expression: Cron 表达式，默认为每天凌晨 2 点执行
    """
    global _scheduler
    _scheduler = ProductOrderScheduler(db_session_func)
    _scheduler.start(cron_expression)
    return _scheduler


def start_scheduler(cron_expression: Optional[str] = None):
    """启动调度器"""
    if _scheduler and not _scheduler.is_running:
        if cron_expression:
            _scheduler.start(cron_expression)
        else:
            _scheduler.scheduler.start()
            _scheduler.is_running = True


def stop_scheduler():
    """停止调度器"""
    if _scheduler:
        _scheduler.stop()
