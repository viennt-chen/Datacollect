"""
事件数据关联定时任务
功能：定时批量处理未关联的事件数据
"""
import logging
import threading
import time
from typing import Optional
from datetime import datetime

from app.database import get_db_session
from app.services.event_data_relation import EventDataRelationService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EventRelationScheduler:
    """事件关联定时任务调度器"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __init__(self):
        self._running = False
        self._thread = None
        self._interval = 300
        self._batch_size = 100
        self._last_run = None
        self._total_processed = 0
        self._total_errors = 0
    
    @classmethod
    def get_instance(cls) -> 'EventRelationScheduler':
        """获取单例实例"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance
    
    def start(self, interval: int = 300, batch_size: int = 100):
        """
        启动定时任务
        
        Args:
            interval: 执行间隔（秒），默认5分钟
            batch_size: 每批处理的事件数量，默认100
        """
        if self._running:
            logger.warning("定时任务已在运行中")
            return
        
        self._interval = interval
        self._batch_size = batch_size
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        
        logger.info(f"事件关联定时任务已启动：interval={interval}s, batch_size={batch_size}")
    
    def stop(self):
        """停止定时任务"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=10)
        logger.info("事件关联定时任务已停止")
    
    def run_once(self) -> dict:
        """立即执行一次批量处理"""
        return self._process_batch()
    
    def _run(self):
        """定时任务主循环"""
        while self._running:
            try:
                result = self._process_batch()
                self._last_run = datetime.now()
                self._total_processed += result.get("processed_events", 0)
                self._total_errors += result.get("errors", 0)
                
                logger.info(f"定时任务执行完成：{result}")
                
            except Exception as e:
                logger.error(f"定时任务执行失败：{e}")
                self._total_errors += 1
            
            time.sleep(self._interval)
    
    def _process_batch(self) -> dict:
        """处理一批未关联的事件"""
        try:
            with get_db_session() as db:
                service = EventDataRelationService(db)

                result = service.batch_match_unmatched_events(self._batch_size)

                return {
                    "processed_events": result.get("processed_events", 0),
                    "sv_matched": result.get("sv_matched", 0),
                    "pv_matched": result.get("pv_matched", 0),
                    "alarm_matched": result.get("alarm_matched", 0),
                    "errors": 0
                }

        except Exception as e:
            logger.error(f"批量处理失败：{e}")
            return {
                "processed_events": 0,
                "sv_matched": 0,
                "pv_matched": 0,
                "alarm_matched": 0,
                "errors": 1
            }
    
    def get_status(self) -> dict:
        """获取定时任务状态"""
        return {
            "running": self._running,
            "interval": self._interval,
            "batch_size": self._batch_size,
            "last_run": self._last_run.isoformat() if self._last_run else None,
            "total_processed": self._total_processed,
            "total_errors": self._total_errors
        }


def init_event_relation_scheduler(interval: int = 300, batch_size: int = 100):
    """
    初始化事件关联定时任务
    
    Args:
        interval: 执行间隔（秒）
        batch_size: 每批处理数量
    """
    scheduler = EventRelationScheduler.get_instance()
    scheduler.start(interval=interval, batch_size=batch_size)
    return scheduler


def get_event_relation_scheduler() -> EventRelationScheduler:
    """获取事件关联定时任务实例"""
    return EventRelationScheduler.get_instance()
