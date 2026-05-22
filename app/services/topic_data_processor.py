"""
MQTT 数据处理服务 - 根据 Topic 类型分类处理
功能：
- 加工事件 Topic：解析 JSON 并写入 event_data 表
- PV 压缩 Topic：压缩存储到 pv_compressed_params 表
- SV 压缩 Topic：压缩存储到 sv_compressed_params 表
- ALARM 压缩 Topic：压缩存储到 alarm_compressed_params 表
使用异步队列 + 后台 worker 模式，防止阻塞 MQTT 消息接收
"""
import json
import gzip
import time
import uuid
import asyncio
import logging
import threading
from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from queue import Queue, Empty

from app.database import get_db_session
from app.models.event_data import EventData
from app.models.pv_compressed_param import PVCompressedParam
from app.models.sv_compressed_param import SVCompressedParam
from app.models.alarm_compressed_param import AlarmCompressedParam
from app.models.collector_log import CollectorLog

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TopicDataProcessor:
    """Topic 数据处理器 - 使用异步队列模式防止阻塞"""
    
    def __init__(self, max_queue_size: int = 10000, worker_count: int = 3):
        self._stats = {
            'event_topics': set(),
            'pv_topics': set(),
            'sv_topics': set(),
            'alarm_topics': set(),
            'total_processed': 0,
            'total_stored': 0,
            'total_failed': 0,
            'queue_size': 0
        }
        self._lock = threading.Lock()
        self._message_queue = Queue(maxsize=max_queue_size)
        self._workers = []
        self._running = False
        self._worker_count = worker_count
        self._init_topic_types()
        self._start_workers()
    
    def _start_workers(self):
        """启动后台工作线程"""
        self._running = True
        for i in range(self._worker_count):
            worker = threading.Thread(
                target=self._worker_loop,
                args=(i,),
                daemon=True,
                name=f"TopicDataWorker-{i}"
            )
            worker.start()
            self._workers.append(worker)
        logger.info(f"已启动 {self._worker_count} 个数据处理工作线程")
    
    def _init_topic_types(self):
        """初始化 Topic 类型"""
        try:
            from app.models.mqtt_topic_config import MQTTTopicConfig

            with get_db_session() as db:
                topics = db.query(MQTTTopicConfig).filter(
                    MQTTTopicConfig.enabled == True
                ).all()

                for topic in topics:
                    if topic.topic_type == 'event':
                        self._stats['event_topics'].add(topic.topic_name)
                    elif topic.topic_type in ('pv_compress', 'pv'):
                        self._stats['pv_topics'].add(topic.topic_name)
                    elif topic.topic_type in ('sv_compress', 'sv'):
                        self._stats['sv_topics'].add(topic.topic_name)
                    elif topic.topic_type in ('alarm_compress', 'alarm'):
                        self._stats['alarm_topics'].add(topic.topic_name)

            logger.info(f"初始化 Topic 类型：加工事件={len(self._stats['event_topics'])}, "
                       f"PV压缩={len(self._stats['pv_topics'])}, "
                       f"SV压缩={len(self._stats['sv_topics'])}, "
                       f"ALARM压缩={len(self._stats['alarm_topics'])}")

        except Exception as e:
            logger.error(f"初始化 Topic 类型失败：{e}")
    
    def _worker_loop(self, worker_id: int):
        """工作线程主循环"""
        logger.info(f"工作线程 {worker_id} 已启动")
        while self._running:
            try:
                message = self._message_queue.get(timeout=1.0)
                if message:
                    self._process_message_sync(message)
                    self._message_queue.task_done()
            except Empty:
                continue
            except Exception as e:
                logger.error(f"工作线程 {worker_id} 处理消息失败：{e}")
    
    def process_message(self, topic: str, payload: Dict[str, Any]):
        """
        处理 MQTT 消息 - 快速入队，不阻塞
        
        Args:
            topic: MQTT Topic
            payload: 消息负载
        """
        try:
            with self._lock:
                self._stats['total_processed'] += 1
                self._stats['queue_size'] = self._message_queue.qsize()
            
            # 快速入队，如果队列满了会阻塞一小段时间
            message = {
                'topic': topic,
                'payload': payload,
                'enqueue_time': time.time()
            }
            
            try:
                self._message_queue.put_nowait(message)
            except:
                logger.warning(f"消息队列已满，丢弃消息：{topic}")
                with self._lock:
                    self._stats['total_failed'] += 1
                
        except Exception as e:
            logger.error(f"消息入队失败：{e}")
            with self._lock:
                self._stats['total_failed'] += 1
    
    def _process_message_sync(self, message: Dict[str, Any]):
        """同步处理消息（在工作线程中执行）"""
        topic = message['topic']
        payload = message['payload']
        
        try:
            # 判断 Topic 类型并处理
            if self._is_event_topic(topic):
                self._process_event_data(topic, payload)
            elif self._is_pv_topic(topic):
                self._process_pv_data(topic, payload)
            elif self._is_sv_topic(topic):
                self._process_sv_data(topic, payload)
            elif self._is_alarm_topic(topic):
                self._process_alarm_data(topic, payload)
            else:
                logger.debug(f"未知类型的 Topic: {topic}")
                
            with self._lock:
                self._stats['total_stored'] += 1
                
        except Exception as e:
            logger.error(f"处理消息失败：{e}")
            with self._lock:
                self._stats['total_failed'] += 1
            self._log_error(topic, str(e))
    
    def _is_event_topic(self, topic: str) -> bool:
        """判断是否为加工事件 Topic"""
        for event_topic in self._stats['event_topics']:
            if topic == event_topic or topic.startswith(event_topic):
                return True
        return False
    
    def _is_pv_topic(self, topic: str) -> bool:
        """判断是否为 PV 压缩 Topic"""
        for pv_topic in self._stats['pv_topics']:
            if topic == pv_topic or topic.startswith(pv_topic):
                return True
        return False
    
    def _is_sv_topic(self, topic: str) -> bool:
        """判断是否为 SV 压缩 Topic"""
        for sv_topic in self._stats['sv_topics']:
            if topic == sv_topic or topic.startswith(sv_topic):
                return True
        return False
    
    def _is_alarm_topic(self, topic: str) -> bool:
        """判断是否为 ALARM 压缩 Topic"""
        for alarm_topic in self._stats['alarm_topics']:
            if topic == alarm_topic or topic.startswith(alarm_topic):
                return True
        return False
    
    def _process_event_data(self, topic: str, payload: Dict[str, Any]):
        """
        处理加工事件数据

        Args:
            topic: MQTT Topic
            payload: 消息负载（JSON 格式）
        """
        try:
            with get_db_session() as db:
                # 生成事件 UID
                event_uid = payload.get('event_uid') or str(uuid.uuid4())

                # 解析时间戳
                timestamps = payload.get('timestamps', {})

                # 解析分组信息
                group_info = payload.get('groupInfo', {})

                # 构建事件数据
                event_data = EventData(
                    event_uid=event_uid,
                    start_code=payload.get('startCode', ''),
                    skin_code=payload.get('skinCode', ''),
                    start_time=timestamps.get('start_time'),
                    end_time=timestamps.get('end_time'),
                    start_signal=timestamps.get('start_signal'),
                    end_signal=timestamps.get('end_signal'),
                    duringtime=payload.get('duringtime', 0),
                    machine_duringtime=payload.get('machine_duringtime', 0),
                    machine_id=payload.get('machine_id', ''),
                    operator_id=payload.get('operator_id', ''),
                    operator_name=payload.get('operator_name', ''),
                    group_code=group_info.get('groupCode', ''),
                    group_name=group_info.get('groupName', ''),
                    group_short_name=group_info.get('groupShortName', ''),
                    factory_code=group_info.get('factory', ''),
                    factory_name=group_info.get('factoryName', ''),
                    line_code=group_info.get('line', ''),
                    process_no=group_info.get('ProcesNo', ''),
                    extra_data=json.dumps(payload, ensure_ascii=False) if payload else None
                )

                # 检查是否已存在（通过 event_uid 或 start_code）
                start_code = event_data.start_code
                existing = db.query(EventData).filter(
                    (EventData.event_uid == event_uid) |
                    (EventData.start_code == start_code)
                ).first()

                if existing:
                    # 更新现有记录
                    existing.event_uid = event_uid
                    existing.skin_code = event_data.skin_code
                    existing.start_time = event_data.start_time
                    existing.end_time = event_data.end_time
                    existing.start_signal = event_data.start_signal
                    existing.end_signal = event_data.end_signal
                    existing.duringtime = event_data.duringtime
                    existing.machine_duringtime = event_data.machine_duringtime
                    existing.machine_id = event_data.machine_id
                    existing.operator_id = event_data.operator_id
                    existing.operator_name = event_data.operator_name
                    existing.group_code = event_data.group_code
                    existing.group_name = event_data.group_name
                    existing.group_short_name = event_data.group_short_name
                    existing.factory_code = event_data.factory_code
                    existing.factory_name = event_data.factory_name
                    existing.line_code = event_data.line_code
                    existing.process_no = event_data.process_no
                    existing.extra_data = event_data.extra_data
                    db.commit()
                    logger.info(f"加工事件已更新：{event_uid}, start_code: {start_code}")
                    return

                # 保存到数据库
                db.add(event_data)
                db.commit()

                with self._lock:
                    self._stats['total_stored'] += 1

                logger.info(f"加工事件已保存：{event_uid}, 设备：{event_data.machine_id}, 耗时：{event_data.duringtime}ms")

        except Exception as e:
            logger.error(f"保存加工事件失败：{e}")
            raise
    
    def _process_pv_data(self, topic: str, payload: Dict[str, Any]):
        """
        处理 PV 压缩参数数据
        
        Args:
            topic: MQTT Topic
            payload: 消息负载
        """
        self._process_compress_data(topic, payload, 'pv')
    
    def _process_sv_data(self, topic: str, payload: Dict[str, Any]):
        """
        处理 SV 压缩参数数据
        
        Args:
            topic: MQTT Topic
            payload: 消息负载
        """
        self._process_compress_data(topic, payload, 'sv')
    
    def _process_alarm_data(self, topic: str, payload: Dict[str, Any]):
        """
        处理 ALARM 压缩参数数据
        
        Args:
            topic: MQTT Topic
            payload: 消息负载
        """
        self._process_compress_data(topic, payload, 'alarm')
    
    def _process_compress_data(self, topic: str, payload: Dict[str, Any], data_type: str):
        """
        处理压缩参数数据（通用方法）

        Args:
            topic: MQTT Topic
            payload: 消息负载
            data_type: 数据类型 'pv', 'sv', 或 'alarm'
        """
        try:
            with get_db_session() as db:
                # 生成事件 UID
                event_uid = payload.get('event_uid') or str(uuid.uuid4())

                # 获取时间戳（毫秒）并转换为 datetime
                timestamp_ms = int(time.time() * 1000)
                timestamp_dt = datetime.fromtimestamp(timestamp_ms / 1000.0)

                original_timestamp_ms = payload.get('timestamp', timestamp_ms)
                original_timestamp_dt = datetime.fromtimestamp(original_timestamp_ms / 1000.0)

                # 压缩 payload 数据
                payload_json = json.dumps(payload, ensure_ascii=False)
                compressed_data = gzip.compress(payload_json.encode('utf-8'))

                # 根据数据类型选择对应的模型和表
                if data_type == 'pv':
                    compress_param = PVCompressedParam(
                        topic=topic,
                        event_uid=event_uid,
                        timestamp=timestamp_dt,
                        original_timestamp=original_timestamp_dt,
                        compressed_payload=compressed_data
                    )
                    table_name = 'pv_compressed_params'
                elif data_type == 'sv':
                    compress_param = SVCompressedParam(
                        topic=topic,
                        event_uid=event_uid,
                        timestamp=timestamp_dt,
                        original_timestamp=original_timestamp_dt,
                        compressed_payload=compressed_data
                    )
                    table_name = 'sv_compressed_params'
                elif data_type == 'alarm':
                    compress_param = AlarmCompressedParam(
                        topic=topic,
                        event_uid=event_uid,
                        timestamp=timestamp_dt,
                        original_timestamp=original_timestamp_dt,
                        compressed_payload=compressed_data
                    )
                    table_name = 'alarm_compressed_params'
                else:
                    raise ValueError(f"不支持的数据类型：{data_type}")

                # 保存到数据库
                db.add(compress_param)
                db.commit()

                with self._lock:
                    self._stats['total_stored'] += 1

                type_name_map = {
                    'pv': 'PV',
                    'sv': 'SV',
                    'alarm': 'ALARM'
                }
                type_label = type_name_map.get(data_type, data_type.upper())

                logger.info(f"{type_label}压缩参数已保存：{topic}, UID: {event_uid}, "
                           f"压缩前：{len(payload_json)}bytes, 压缩后：{len(compressed_data)}bytes")

        except Exception as e:
            logger.error(f"保存压缩参数失败（{data_type}）：{e}")
            raise
    
    def _log_error(self, topic: str, error: str):
        """记录错误日志"""
        try:
            with get_db_session() as db:
                log = CollectorLog(
                    log_level="ERROR",
                    log_type="PROCESS_ERROR",
                    topic_name=topic,
                    error_message=error,
                    summary=f"数据处理失败: {error[:100]}"
                )

                db.add(log)
                db.commit()

        except Exception as e:
            logger.error(f"记录错误日志失败：{e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """获取处理统计信息"""
        return {
            'event_topics_count': len(self._stats['event_topics']),
            'pv_topics_count': len(self._stats['pv_topics']),
            'sv_topics_count': len(self._stats['sv_topics']),
            'alarm_topics_count': len(self._stats['alarm_topics']),
            'total_processed': self._stats['total_processed'],
            'total_stored': self._stats['total_stored'],
            'total_failed': self._stats['total_failed']
        }


# 全局实例
_processor: Optional[TopicDataProcessor] = None


def get_processor() -> TopicDataProcessor:
    """获取处理器实例"""
    global _processor
    if _processor is None:
        _processor = TopicDataProcessor()
    return _processor


def reset_processor():
    """重置处理器实例"""
    global _processor
    _processor = None
