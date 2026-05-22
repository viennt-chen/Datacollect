"""
订单加工关联定时任务
功能：定时补漏未关联的事件 + 定时同步订单状态
复用 event_relation_scheduler.py 的模式
"""
import logging
import threading
import time
import os
from typing import Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class OrderProcessingScheduler:
    """订单加工关联定时任务调度器"""

    _instance = None
    _lock = threading.Lock()

    def __init__(self):
        self._running = False
        self._thread = None
        self._interval = int(os.getenv('ORDER_PROCESSING_RECONCILE_INTERVAL', '600'))
        self._batch_size = int(os.getenv('ORDER_PROCESSING_BATCH_SIZE', '100'))
        self._last_run = None
        self._total_backfill_runs = 0
        self._total_reconcile_runs = 0
        self._total_errors = 0

    @classmethod
    def get_instance(cls) -> 'OrderProcessingScheduler':
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def start(self, interval: Optional[int] = None, batch_size: Optional[int] = None):
        if self._running:
            logger.warning("订单加工定时任务已在运行中")
            return

        if interval is not None:
            self._interval = interval
        if batch_size is not None:
            self._batch_size = batch_size

        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

        logger.info(f"订单加工定时任务已启动：interval={self._interval}s, batch_size={self._batch_size}")

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=10)
        logger.info("订单加工定时任务已停止")

    def run_once(self) -> dict:
        """立即执行一次"""
        return self._execute()

    def _run(self):
        """定时任务主循环"""
        while self._running:
            try:
                result = self._execute()
                logger.info(f"订单加工定时任务执行完成：{result}")
            except Exception as e:
                logger.error(f"订单加工定时任务执行失败：{e}")
                self._total_errors += 1

            time.sleep(self._interval)

    def _execute(self) -> dict:
        """执行补漏 + 状态同步"""
        self._last_run = datetime.now()
        results = {}

        # 1. 补漏
        try:
            from app.services.order_processing_linker import batch_link_unlinked_events
            backfill = batch_link_unlinked_events(self._batch_size)
            results['backfill'] = backfill
            self._total_backfill_runs += 1
        except Exception as e:
            logger.error(f"补漏执行失败：{e}")
            results['backfill'] = {"success": False, "error": str(e)}
            self._total_errors += 1

        # 2. 状态同步
        try:
            from app.services.order_processing_linker import reconcile_order_statuses
            reconcile = reconcile_order_statuses()
            results['reconcile'] = reconcile
            self._total_reconcile_runs += 1
        except Exception as e:
            logger.error(f"状态同步执行失败：{e}")
            results['reconcile'] = {"success": False, "error": str(e)}
            self._total_errors += 1

        return results

    def get_status(self) -> dict:
        return {
            "running": self._running,
            "interval": self._interval,
            "batch_size": self._batch_size,
            "last_run": self._last_run.isoformat() if self._last_run else None,
            "total_backfill_runs": self._total_backfill_runs,
            "total_reconcile_runs": self._total_reconcile_runs,
            "total_errors": self._total_errors,
        }


def init_order_processing_scheduler(interval: Optional[int] = None, batch_size: Optional[int] = None):
    """初始化订单加工定时任务"""
    scheduler = OrderProcessingScheduler.get_instance()
    scheduler.start(interval=interval, batch_size=batch_size)
    return scheduler


def get_order_processing_scheduler() -> OrderProcessingScheduler:
    """获取定时任务实例"""
    return OrderProcessingScheduler.get_instance()
