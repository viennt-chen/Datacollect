"""
订单加工关联触发器
功能：在 event_data 保存时自动触发关联到订单
复用 event_relation_trigger.py 的模式
"""
import logging
import threading
import os
from typing import Optional
from sqlalchemy import event

from app.models.event_data import EventData
from app.database import get_db_session

logger = logging.getLogger(__name__)


class OrderProcessingTrigger:
    """订单加工关联触发器"""

    _instance = None
    _lock = threading.Lock()

    def __init__(self):
        self._enabled = os.getenv('ORDER_PROCESSING_TRIGGER_ENABLED', 'true').lower() == 'true'
        self._pending_events = []
        self._processing = False

    @classmethod
    def get_instance(cls) -> 'OrderProcessingTrigger':
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def enable(self):
        self._enabled = True
        logger.info("订单加工关联触发器已启用")

    def disable(self):
        self._enabled = False
        logger.info("订单加工关联触发器已禁用")

    def on_event_data_after_insert(self, mapper, connection, target):
        """EventData 插入后的回调"""
        if not self._enabled:
            return

        if not target.id:
            return

        self._pending_events.append(target.id)

        if not self._processing:
            threading.Thread(target=self._process_pending_events, daemon=True).start()

    def _process_pending_events(self):
        """处理待关联的事件"""
        self._processing = True

        while self._pending_events:
            event_id = self._pending_events.pop(0)

            try:
                from app.services.order_processing_linker import link_event_to_order
                result = link_event_to_order(event_id)
                logger.debug(f"订单关联完成：event_id={event_id}, result={result}")
            except Exception as e:
                logger.error(f"订单关联失败：event_id={event_id}, error={e}")

        self._processing = False

    def register_trigger(self):
        event.listen(EventData, 'after_insert', self.on_event_data_after_insert)
        logger.info("订单加工关联触发器已注册")

    def unregister_trigger(self):
        try:
            event.remove(EventData, 'after_insert', self.on_event_data_after_insert)
            logger.info("订单加工关联触发器已注销")
        except Exception as e:
            logger.error(f"注销触发器失败：{e}")

    def get_status(self) -> dict:
        return {
            "enabled": self._enabled,
            "pending_events": len(self._pending_events),
            "processing": self._processing,
        }


def init_order_processing_trigger():
    """初始化订单加工关联触发器"""
    trigger = OrderProcessingTrigger.get_instance()
    trigger.register_trigger()
    return trigger


def get_order_processing_trigger() -> OrderProcessingTrigger:
    """获取触发器实例"""
    return OrderProcessingTrigger.get_instance()
