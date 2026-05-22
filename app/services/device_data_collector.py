"""
设备数据采集服务
功能：
- 支持从 MQTT Client 服务获取实时数据
- 支持从数据库读取历史数据
- 提供统一的数据访问接口
"""
import json
import time
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from sqlalchemy.orm import Session

from app.database import get_db_session
from app.models.device import Device
from app.models.mqtt_topic_config import MQTTTopicConfig
from app.models.event_data import EventData
from app.models.pv_compressed_param import PVCompressedParam
from app.models.sv_compressed_param import SVCompressedParam
from app.models.alarm_compressed_param import AlarmCompressedParam
from app.services.mqtt_collector import get_collector, MQTTDataCollector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DeviceDataCollector:
    """设备数据采集服务"""
    
    def __init__(self):
        self._mqtt_subscribers: Dict[str, List[Callable]] = {}
        self._real_time_callbacks: Dict[str, List[Callable]] = {}

    def get_device_topics(self, device_code: str, db: Session) -> List[MQTTTopicConfig]:
        """获取设备关联的所有Topic配置"""
        device = db.query(Device).filter(Device.device_code == device_code).first()
        if not device:
            return []
        
        mqtt_topics = []
        if device.mqtt_topics:
            try:
                mqtt_topics = json.loads(device.mqtt_topics)
            except (json.JSONDecodeError, TypeError):
                mqtt_topics = []
        
        topic_configs = db.query(MQTTTopicConfig).filter(
            MQTTTopicConfig.topic_name.in_(mqtt_topics)
        ).all()
        
        return topic_configs
    
    def get_realtime_data_from_mqtt(self, device_code: str, topic_name: str) -> Optional[Dict[str, Any]]:
        """
        从 MQTT Client 服务获取实时数据
        
        Args:
            device_code: 设备编号
            topic_name: Topic名称

        Returns:
            最新的实时数据，如果没有数据则返回 None
        """
        try:
            collector = get_collector()
            
            # 从采集器的数据缓冲区获取最新数据
            for message in reversed(collector.data_buffer):
                if message.get('topic') == topic_name:
                    return {
                        'topic': topic_name,
                        'data': message.get('payload'),
                        'timestamp': message.get('timestamp'),
                        'source': 'mqtt_realtime'
                    }
            
            return None
        except Exception as e:
            logger.error(f"从MQTT获取实时数据失败：{e}")
            return None
    
    def get_latest_data_from_db(self, device_code: str, topic_name: str, db: Session) -> Optional[Dict[str, Any]]:
        """
        从数据库读取最新数据
        
        Args:
            device_code: 设备编号
            topic_name: Topic名称
            db: 数据库会话
            
        Returns:
            最新的数据库记录，如果没有数据则返回 None
        """
        try:
            topic_config = db.query(MQTTTopicConfig).filter(
                MQTTTopicConfig.topic_name == topic_name
            ).first()
            
            if not topic_config:
                return None
            
            latest_record = None
            
            if topic_config.topic_type == 'event':
                device = db.query(Device).filter(Device.device_code == device_code).first()
                if device:
                    latest_record = db.query(EventData).filter(
                        EventData.machine_id == device.device_code
                    ).order_by(EventData.start_time.desc()).first()
                    
                    if latest_record:
                        event_data = {
                            "event_uid": latest_record.event_uid,
                            "start_code": latest_record.start_code,
                            "skin_code": latest_record.skin_code,
                            "start_time": latest_record.start_time,
                            "end_time": latest_record.end_time,
                            "duringtime": latest_record.duringtime,
                            "machine_duringtime": latest_record.machine_duringtime,
                            "machine_id": latest_record.machine_id,
                            "operator_id": latest_record.operator_id,
                            "operator_name": latest_record.operator_name,
                            "group_code": latest_record.group_code,
                            "group_name": latest_record.group_name,
                            "factory_code": latest_record.factory_code,
                            "factory_name": latest_record.factory_name,
                            "line_code": latest_record.line_code,
                            "process_no": latest_record.process_no,
                        }
                        if latest_record.extra_data:
                            event_data["extra_data"] = json.loads(latest_record.extra_data)
                        
                        return {
                            'topic': topic_name,
                            'topic_type': topic_config.topic_type,
                            'data': event_data,
                            'timestamp': datetime.fromtimestamp(latest_record.start_time / 1000).isoformat() if latest_record.start_time else None,
                            'original_timestamp': datetime.fromtimestamp(latest_record.start_time / 1000).isoformat() if latest_record.start_time else None,
                            'source': 'database'
                        }
            
            elif topic_config.topic_type in ('pv_compress', 'pv'):
                latest_record = db.query(PVCompressedParam).filter(
                    PVCompressedParam.topic == topic_name
                ).order_by(PVCompressedParam.timestamp.desc()).first()
                
                if latest_record:
                    decompressed_data = self._decompress_payload(latest_record.compressed_payload)
                    return {
                        'topic': topic_name,
                        'topic_type': topic_config.topic_type,
                        'data': decompressed_data,
                        'timestamp': latest_record.timestamp.isoformat() if latest_record.timestamp else None,
                        'original_timestamp': latest_record.original_timestamp.isoformat() if latest_record.original_timestamp else None,
                        'source': 'database'
                    }
            
            elif topic_config.topic_type in ('sv_compress', 'sv'):
                latest_record = db.query(SVCompressedParam).filter(
                    SVCompressedParam.topic == topic_name
                ).order_by(SVCompressedParam.timestamp.desc()).first()
                
                if latest_record:
                    decompressed_data = self._decompress_payload(latest_record.compressed_payload)
                    return {
                        'topic': topic_name,
                        'topic_type': topic_config.topic_type,
                        'data': decompressed_data,
                        'timestamp': latest_record.timestamp.isoformat() if latest_record.timestamp else None,
                        'original_timestamp': latest_record.original_timestamp.isoformat() if latest_record.original_timestamp else None,
                        'source': 'database'
                    }
            
            elif topic_config.topic_type in ('alarm_compress', 'alarm'):
                latest_record = db.query(AlarmCompressedParam).filter(
                    AlarmCompressedParam.topic == topic_name
                ).order_by(AlarmCompressedParam.timestamp.desc()).first()
                
                if latest_record:
                    decompressed_data = self._decompress_payload(latest_record.compressed_payload)
                    return {
                        'topic': topic_name,
                        'topic_type': topic_config.topic_type,
                        'data': decompressed_data,
                        'timestamp': latest_record.timestamp.isoformat() if latest_record.timestamp else None,
                        'original_timestamp': latest_record.original_timestamp.isoformat() if latest_record.original_timestamp else None,
                        'source': 'database'
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"从数据库读取数据失败：{e}")
            return None
    
    def get_historical_data(self, device_code: str, topic_name: str, 
                           start_time: Optional[str] = None, 
                           end_time: Optional[str] = None,
                           page: int = 1, 
                           page_size: int = 20) -> Dict[str, Any]:
        """
        从数据库读取历史数据（分页）
        
        Args:
            device_code: 设备编号
            topic_name: Topic名称
            start_time: 开始时间
            end_time: 结束时间
            page: 页码
            page_size: 每页数量
            
        Returns:
            历史数据列表
        """
        with get_db_session() as db:
            topic_config = db.query(MQTTTopicConfig).filter(
                MQTTTopicConfig.topic_name == topic_name
            ).first()

            if not topic_config:
                return {'total': 0, 'items': []}

            device = db.query(Device).filter(Device.device_code == device_code).first()
            if not device:
                return {'total': 0, 'items': []}

            items = []
            total = 0

            if topic_config.topic_type == 'event':
                query = db.query(EventData).filter(
                    EventData.machine_id == device.device_code
                )

                if start_time:
                    start_ts = int(datetime.fromisoformat(start_time).timestamp() * 1000)
                    query = query.filter(EventData.start_time >= start_ts)

                if end_time:
                    end_ts = int(datetime.fromisoformat(end_time).timestamp() * 1000)
                    query = query.filter(EventData.start_time <= end_ts)

                total = query.count()
                offset = (page - 1) * page_size
                records = query.order_by(EventData.start_time.desc()).offset(offset).limit(page_size).all()

                for record in records:
                    event_data = {
                        "id": record.id,
                        "event_uid": record.event_uid,
                        "start_code": record.start_code,
                        "start_time": record.start_time,
                        "end_time": record.end_time,
                        "duringtime": record.duringtime,
                        "machine_duringtime": record.machine_duringtime,
                        "machine_id": record.machine_id,
                        "operator_id": record.operator_id,
                        "operator_name": record.operator_name,
                        "process_no": record.process_no,
                        "created_at": record.created_at.isoformat() if record.created_at else None
                    }
                    items.append(event_data)

            elif topic_config.topic_type in ['pv_compress', 'pv', 'sv_compress', 'sv', 'alarm_compress', 'alarm']:
                model_class = {
                    'pv_compress': PVCompressedParam,
                    'pv': PVCompressedParam,
                    'sv_compress': SVCompressedParam,
                    'sv': SVCompressedParam,
                    'alarm_compress': AlarmCompressedParam,
                    'alarm': AlarmCompressedParam
                }[topic_config.topic_type]

                query = db.query(model_class).filter(
                    model_class.topic == topic_name
                )

                if start_time:
                    query = query.filter(model_class.timestamp >= start_time)

                if end_time:
                    query = query.filter(model_class.timestamp <= end_time)

                total = query.count()
                offset = (page - 1) * page_size
                records = query.order_by(model_class.timestamp.desc()).offset(offset).limit(page_size).all()

                for record in records:
                    item_data = {
                        "id": record.id,
                        "topic": record.topic,
                        "event_uid": record.event_uid,
                        "timestamp": record.timestamp.isoformat() if record.timestamp else None,
                        "original_timestamp": record.original_timestamp.isoformat() if record.original_timestamp else None,
                        "created_at": record.created_at.isoformat() if record.created_at else None
                    }
                    items.append(item_data)

            return {
                'total': total,
                'items': items,
                'page': page,
                'page_size': page_size
            }
    
    def subscribe_realtime(self, device_code: str, topic_name: str,
                          callback: Callable[[Dict[str, Any]], None]) -> bool:
        """
        订阅实时数据（通过MQTT）

        Args:
            device_code: 设备编号
            topic_name: Topic名称
            callback: 数据回调函数

        Returns:
            是否订阅成功
        """
        try:
            if device_code not in self._real_time_callbacks:
                self._real_time_callbacks[device_code] = []

            self._real_time_callbacks[device_code].append({
                'topic': topic_name,
                'callback': callback
            })

            # 注册到MQTT采集器
            collector = get_collector()
            if topic_name not in self._mqtt_subscribers:
                self._mqtt_subscribers[topic_name] = []

            self._mqtt_subscribers[topic_name].append(callback)

            logger.info(f"订阅实时数据成功：device_code={device_code}, topic={topic_name}")
            return True
            
        except Exception as e:
            logger.error(f"订阅实时数据失败：{e}")
            return False
    
    def unsubscribe_realtime(self, device_code: str, topic_name: str) -> bool:
        """取消订阅实时数据"""
        try:
            if device_code in self._real_time_callbacks:
                self._real_time_callbacks[device_code] = [
                    sub for sub in self._real_time_callbacks[device_code]
                    if sub['topic'] != topic_name
                ]

            if topic_name in self._mqtt_subscribers:
                self._mqtt_subscribers[topic_name] = []

            logger.info(f"取消订阅实时数据：device_code={device_code}, topic={topic_name}")
            return True
            
        except Exception as e:
            logger.error(f"取消订阅失败：{e}")
            return False
    
    def _decompress_payload(self, compressed_data: bytes) -> Dict[str, Any]:
        """解压缩 payload 数据"""
        import gzip
        try:
            decompressed = gzip.decompress(compressed_data).decode('utf-8')
            return json.loads(decompressed)
        except Exception as e:
            logger.error(f"解压缩失败：{e}")
            return {}
    
    def get_data_source_status(self, device_code: str) -> Dict[str, Any]:
        """
        获取数据源状态

        Args:
            device_code: 设备编号

        Returns:
            数据源状态信息
        """
        with get_db_session() as db:
            device = db.query(Device).filter(Device.device_code == device_code).first()
            if not device:
                return {'error': '设备不存在'}

            topic_configs = self.get_device_topics(device_code, db)

            # 检查MQTT连接状态
            try:
                collector = get_collector()
                mqtt_status = {
                    'connected': collector.stats.is_connected,
                    'running': collector.stats.is_running,
                    'messages_received': collector.stats.messages_received,
                    'last_message_time': collector.stats.last_message_time
                }
            except Exception as e:
                mqtt_status = {
                    'connected': False,
                    'running': False,
                    'error': str(e)
                }

            # 检查数据库连接状态
            db_status = {
                'connected': True,
                'topic_count': len(topic_configs)
            }

            return {
                'device_code': device.device_code,
                'device_name': device.device_name,
                'mqtt_topics': device.mqtt_topics,
                'mqtt_status': mqtt_status,
                'database_status': db_status,
                'topics': [
                    {
                        'topic_name': config.topic_name,
                        'topic_type': config.topic_type,
                        'enabled': config.enabled
                    }
                    for config in topic_configs
                ]
            }


# 全局实例
_device_data_collector: Optional[DeviceDataCollector] = None


def get_device_data_collector() -> DeviceDataCollector:
    """获取设备数据采集器实例（单例模式）"""
    global _device_data_collector
    if _device_data_collector is None:
        _device_data_collector = DeviceDataCollector()
    return _device_data_collector
