"""
MQTT 数据采集器服务
功能：连接 MQTT 代理，订阅主题，收集和处理数据
"""
import asyncio
import json
import time
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import threading
import paho.mqtt.client as mqtt

from app.database import get_db_session

logger = logging.getLogger(__name__)


@dataclass
class CollectorConfig:
    """采集器配置"""
    broker_host: str = "10.10.150.254"
    broker_port: int = 1883
    client_id: str = "pts_data_collector"
    username: Optional[str] = None
    password: Optional[str] = None
    topics: List[str] = None
    reconnect_interval: int = 5  # 重连间隔（秒）
    data_buffer_size: int = 1000  # 数据缓冲区大小
    
    @classmethod
    def from_env(cls):
        """从环境变量创建配置"""
        import os
        return cls(
            broker_host=os.getenv("MQTT_BROKER_HOST", "10.10.150.254"),
            broker_port=int(os.getenv("MQTT_BROKER_PORT", "1883")),
            username=os.getenv("MQTT_USERNAME") or None,
            password=os.getenv("MQTT_PASSWORD") or None,
            topics=os.getenv("MQTT_TOPICS", "SHXQ/NO1/KP3/IMG/ProcesEvent,SHXQ/NO1/KP3/IMG/Alarm,SHXQ/NO1/KP3/IMG/PV,SHXQ/NO1/KP3/IMG/SV").split(",")
        )


@dataclass
class CollectorStats:
    """采集器状态统计"""
    is_connected: bool = False
    is_running: bool = False
    connected_at: Optional[str] = None
    disconnected_at: Optional[str] = None
    messages_received: int = 0
    messages_processed: int = 0
    errors: int = 0
    uptime: float = 0.0
    last_message_time: Optional[str] = None


@dataclass
class ProcessingEventStats:
    """加工事件统计"""
    total_events: int = 0
    processed_events: int = 0
    failed_events: int = 0


@dataclass
class RawDataStats:
    """原始数据统计"""
    total_records: int = 0
    stored_records: int = 0
    failed_records: int = 0


class MQTTDataCollector:
    """MQTT 数据采集器"""
    
    def __init__(self, config: CollectorConfig = None):
        self.config = config or CollectorConfig(topics=["kp3/#"])
        self.client = mqtt.Client(client_id=self.config.client_id)
        
        if self.config.username and self.config.password:
            self.client.username_pw_set(self.config.username, self.config.password)
        
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message
        self.client.on_subscribe = self._on_subscribe
        
        self.stats = CollectorStats()
        self.data_buffer = []  # 数据缓冲区
        self.is_initialized = False
        self._lock = threading.Lock()
        
        # 初始化统计数据
        self.processing_stats = ProcessingEventStats()
        self.raw_data_stats = RawDataStats()
    
    def _on_connect(self, client, userdata, flags, rc):
        """连接回调"""
        if rc == 0:
            self.stats.is_connected = True
            self.stats.connected_at = datetime.now().isoformat()
            print(f"MQTT 连接成功: {self.config.broker_host}:{self.config.broker_port}")
            
            # 订阅配置的主题
            for topic in self.config.topics:
                self.client.subscribe(topic)
                print(f"已订阅主题: {topic}")
        else:
            print(f"MQTT 连接失败: {rc}")
            self.stats.is_connected = False
    
    def _on_disconnect(self, client, userdata, rc):
        """断开连接回调"""
        self.stats.is_connected = False
        self.stats.disconnected_at = datetime.now().isoformat()
        print(f"MQTT 连接断开: {rc}")
    
    def _on_message(self, client, userdata, msg):
        """消息接收回调"""
        try:
            self.stats.messages_received += 1
            self.stats.last_message_time = datetime.now().isoformat()
            
            # 解析消息内容
            payload = msg.payload.decode('utf-8')
            try:
                data = json.loads(payload)
            except json.JSONDecodeError:
                data = {"raw_payload": payload}
            
            # 添加元数据
            message_data = {
                "topic": msg.topic,
                "payload": data,
                "timestamp": datetime.now().isoformat(),
                "qos": msg.qos
            }
            
            # 添加到数据缓冲区
            with self._lock:
                self.data_buffer.append(message_data)
                if len(self.data_buffer) > self.config.data_buffer_size:
                    self.data_buffer.pop(0)  # 移除最旧的数据
            
            self.stats.messages_processed += 1
            
            # 这里可以添加数据处理逻辑
            self._process_message(message_data)
            
        except Exception as e:
            self.stats.errors += 1
            print(f"处理 MQTT 消息时出错: {e}")
    
    def _on_subscribe(self, client, userdata, mid, granted_qos):
        """订阅回调"""
        print(f"成功订阅，QoS: {granted_qos}")
    
    def _process_message(self, message_data: Dict[str, Any]):
        """处理接收到的消息"""
        try:
            # 使用增强的数据处理器存储数据
            from app.services.topic_data_processor import get_processor
            
            processor = get_processor()
            if processor:
                topic = message_data.get('topic', '')
                payload = message_data.get('payload', {})

                # 处理并存储数据
                processor.process_message(topic, payload)
                
        except Exception as e:
            logger.error(f"处理消息失败：{e}")
            self._log_error(topic=message_data.get('topic', 'UNKNOWN'), error=str(e))
            self.stats.errors += 1
    
    def _log_error(self, topic: str, error: str):
        """记录错误日志"""
        try:
            from app.models.collector_log import CollectorLog

            with get_db_session() as db:
                log = CollectorLog(
                    log_level="ERROR",
                    log_type="ERROR",
                    topic_name=topic,
                    error_message=error,
                    summary=f"处理错误: {error[:100]}"
                )
                db.add(log)
                db.commit()
        except Exception as e:
            print(f"记录错误日志失败：{e}")
    
    def start(self):
        """启动采集器"""
        try:
            self.client.connect(self.config.broker_host, self.config.broker_port, 60)
            self.stats.is_running = True
            
            # 在单独的线程中循环处理消息
            self.client.loop_start()
            print("MQTT 数据采集器已启动")
            
        except Exception as e:
            print(f"启动 MQTT 数据采集器失败: {e}")
            self.stats.errors += 1
    
    def stop(self):
        """停止采集器"""
        try:
            self.client.loop_stop()
            self.client.disconnect()
            self.stats.is_running = False
            print("MQTT 数据采集器已停止")
        except Exception as e:
            print(f"停止 MQTT 数据采集器失败: {e}")
            self.stats.errors += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """获取采集器统计信息"""
        if self.stats.connected_at and self.stats.is_connected:
            connected_time = datetime.fromisoformat(self.stats.connected_at.replace('Z', '+00:00'))
            self.stats.uptime = (datetime.now() - connected_time).total_seconds()
        elif self.stats.disconnected_at:
            disconnected_time = datetime.fromisoformat(self.stats.disconnected_at.replace('Z', '+00:00'))
            self.stats.uptime = (datetime.now() - disconnected_time).total_seconds()
        
        # 合并所有统计信息
        all_stats = asdict(self.stats)
        all_stats.update(asdict(self.processing_stats))
        all_stats.update(asdict(self.raw_data_stats))
        
        return all_stats
    
    def get_recent_messages(self, count: int = 10) -> List[Dict[str, Any]]:
        """获取最近的消息"""
        with self._lock:
            return self.data_buffer[-count:] if len(self.data_buffer) >= count else self.data_buffer[:]

    def get_latest_messages(self, topic_filter: Optional[str] = None, count: int = 1) -> List[Dict[str, Any]]:
        """获取最新的消息，可按 topic 过滤"""
        with self._lock:
            if topic_filter:
                filtered = [m for m in self.data_buffer if topic_filter in m.get('topic', '')]
                return filtered[-count:] if len(filtered) >= count else filtered[:]
            return self.data_buffer[-count:] if len(self.data_buffer) >= count else self.data_buffer[:]

    def get_latest_by_topic(self) -> Dict[str, Dict[str, Any]]:
        """获取每个 topic 的最新一条消息"""
        with self._lock:
            latest = {}
            for msg in self.data_buffer:
                topic = msg.get('topic', '')
                if topic:
                    latest[topic] = msg
            return latest
    
    def subscribe_topic(self, topic: str):
        """订阅特定主题"""
        self.client.subscribe(topic)
        if topic not in self.config.topics:
            self.config.topics.append(topic)
    
    def unsubscribe_topic(self, topic: str):
        """取消订阅特定主题"""
        self.client.unsubscribe(topic)
        if topic in self.config.topics:
            self.config.topics.remove(topic)


# 全局采集器实例
_collector: Optional[MQTTDataCollector] = None
_collector_lock = threading.Lock()


def get_collector() -> MQTTDataCollector:
    """获取采集器实例（单例模式）"""
    global _collector
    
    with _collector_lock:
        if _collector is None:
            # 从数据库加载启用的 Topic 配置
            try:
                from app.models.mqtt_topic_config import MQTTTopicConfig

                with get_db_session() as db:
                    topic_configs = db.query(MQTTTopicConfig).filter(
                        MQTTTopicConfig.enabled == True
                    ).all()

                    topics = [config.topic_name for config in topic_configs]

                    # 如果没有配置，使用默认主题
                    if not topics:
                        topics = ["SHXQ/NO1/KP3/IMG/ProcesEvent", "SHXQ/NO1/KP3/IMG/Alarm", "SHXQ/NO1/KP3/IMG/PV", "SHXQ/NO1/KP3/IMG/SV"]

                print(f"MQTT 采集器将订阅以下主题：{', '.join(topics)}")
            except Exception as e:
                print(f"加载 Topic 配置失败，使用默认配置：{e}")
                topics = ["SHXQ/NO1/KP3/IMG/ProcesEvent", "SHXQ/NO1/KP3/IMG/Alarm", "SHXQ/NO1/KP3/IMG/PV", "SHXQ/NO1/KP3/IMG/SV"]
            
            # 使用环境变量创建配置
            config = CollectorConfig.from_env()
            # 覆盖主题（如果从数据库加载成功）
            if topics:
                config.topics = topics
            
            _collector = MQTTDataCollector(config)
        
        return _collector


def init_collector():
    """初始化采集器"""
    global _collector
    
    with _collector_lock:
        if _collector is None:
            # 从数据库加载启用的 Topic 配置
            try:
                from app.models.mqtt_topic_config import MQTTTopicConfig

                with get_db_session() as db:
                    topic_configs = db.query(MQTTTopicConfig).filter(
                        MQTTTopicConfig.enabled == True
                    ).all()

                    topics = [config.topic_name for config in topic_configs]

                    # 如果没有配置，使用默认主题
                    if not topics:
                        topics = ["SHXQ/NO1/KP3/IMG/ProcesEvent", "SHXQ/NO1/KP3/IMG/Alarm", "SHXQ/NO1/KP3/IMG/PV", "SHXQ/NO1/KP3/IMG/SV"]

                print(f"MQTT 采集器将订阅以下主题：{', '.join(topics)}")
            except Exception as e:
                print(f"加载 Topic 配置失败，使用默认配置：{e}")
                topics = ["SHXQ/NO1/KP3/IMG/ProcesEvent", "SHXQ/NO1/KP3/IMG/Alarm", "SHXQ/NO1/KP3/IMG/PV", "SHXQ/NO1/KP3/IMG/SV"]
            
            # 使用环境变量创建配置
            config = CollectorConfig.from_env()
            # 覆盖主题（如果从数据库加载成功）
            if topics:
                config.topics = topics
            
            _collector = MQTTDataCollector(config)
            _collector.is_initialized = True


def cleanup():
    """清理资源"""
    global _collector
    
    with _collector_lock:
        if _collector and _collector.stats.is_running:
            _collector.stop()
        _collector = None


# 在模块加载时初始化
init_collector()

# 导出默认采集器实例
collector = get_collector()