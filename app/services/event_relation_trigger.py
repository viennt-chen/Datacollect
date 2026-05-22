"""
事件数据关联触发器
功能：在event_data保存时自动触发关联匹配
"""
import logging
import threading
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import event

from app.models.event_data import EventData
from app.database import get_db_session

logger = logging.getLogger(__name__)


class EventDataRelationTrigger:
    """事件数据关联触发器"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __init__(self):
        self._enabled = True
        self._pending_events = []
        self._processing = False
    
    @classmethod
    def get_instance(cls) -> 'EventDataRelationTrigger':
        """获取单例实例"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance
    
    def enable(self):
        """启用触发器"""
        self._enabled = True
        logger.info("事件数据关联触发器已启用")
    
    def disable(self):
        """禁用触发器"""
        self._enabled = False
        logger.info("事件数据关联触发器已禁用")
    
    def on_event_data_after_insert(self, mapper, connection, target):
        """
        EventData插入后的回调函数
        
        Args:
            mapper: SQLAlchemy mapper
            connection: 数据库连接
            target: 插入的EventData对象
        """
        if not self._enabled:
            return
        
        if not target.id:
            return
        
        logger.info(f"触发事件关联匹配：event_id={target.id}")
        
        self._pending_events.append(target.id)
        
        if not self._processing:
            self._process_pending_events()
    
    def _process_pending_events(self):
        """处理待匹配的事件"""
        if not self._pending_events:
            self._processing = False
            return

        self._processing = True

        while self._pending_events:
            event_id = self._pending_events.pop(0)

            try:
                with get_db_session() as db:
                    from app.services.event_data_relation import EventDataRelationService

                    service = EventDataRelationService(db)
                    result = service.match_and_save_relations(event_id)

                    logger.info(f"事件关联匹配完成：event_id={event_id}, result={result}")

            except Exception as e:
                logger.error(f"事件关联匹配失败：event_id={event_id}, error={e}")

        self._processing = False
    
    def register_trigger(self):
        """注册触发器"""
        event.listen(EventData, 'after_insert', self.on_event_data_after_insert)
        logger.info("事件数据关联触发器已注册")
    
    def unregister_trigger(self):
        """注销触发器"""
        try:
            event.remove(EventData, 'after_insert', self.on_event_data_after_insert)
            logger.info("事件数据关联触发器已注销")
        except Exception as e:
            logger.error(f"注销触发器失败：{e}")


def init_event_relation_trigger():
    """初始化事件关联触发器"""
    trigger = EventDataRelationTrigger.get_instance()
    trigger.register_trigger()
    return trigger


def get_event_relation_trigger() -> EventDataRelationTrigger:
    """获取事件关联触发器实例"""
    return EventDataRelationTrigger.get_instance()
