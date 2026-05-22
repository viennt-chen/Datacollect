"""
MQTT 数据转发服务
功能：
- 订阅设备相关的MQTT Topic
- 将实时数据通过WebSocket推送给前端
- 管理设备与Topic的订阅关系
"""
import json
import asyncio
import logging
from typing import Dict, List, Set, Optional, Any, Callable
from datetime import datetime

from app.services.mqtt_collector import get_collector, MQTTDataCollector
from app.services.websocket_service import websocket_manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MQTTDataForwarder:
    """MQTT数据转发服务"""
    
    def __init__(self):
        self._device_subscriptions: Dict[int, Set[str]] = {}
        self._topic_subscribers: Dict[str, Set[str]] = {}
        self._forwarding_tasks: Dict[str, asyncio.Task] = {}
        self._is_running = False
        self._message_queue: asyncio.Queue = asyncio.Queue()
    
    async def start(self):
        """启动数据转发服务"""
        if self._is_running:
            logger.warning("数据转发服务已在运行")
            return
        
        self._is_running = True
        logger.info("MQTT数据转发服务已启动")
        
        # 启动消息处理任务
        task = asyncio.create_task(self._process_message_queue())
        self._forwarding_tasks['main'] = task
    
    async def stop(self):
        """停止数据转发服务"""
        if not self._is_running:
            return
        
        self._is_running = False
        
        # 取消所有转发任务
        for task_name, task in self._forwarding_tasks.items():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        
        self._forwarding_tasks.clear()
        self._device_subscriptions.clear()
        self._topic_subscribers.clear()
        
        logger.info("MQTT数据转发服务已停止")
    
    async def subscribe_device(self, device_code: str, topic_name: str, websocket_id: str) -> bool:
        """
        订阅设备数据

        Args:
            device_code: 设备编号
            topic_name: Topic名称
            websocket_id: WebSocket连接ID

        Returns:
            是否订阅成功
        """
        try:
            # 记录设备订阅
            if device_code not in self._device_subscriptions:
                self._device_subscriptions[device_code] = set()
            self._device_subscriptions[device_code].add(topic_name)

            # 记录Topic订阅
            if topic_name not in self._topic_subscribers:
                self._topic_subscribers[topic_name] = set()
            self._topic_subscribers[topic_name].add(websocket_id)

            logger.info(f"设备 {device_code} 订阅 Topic {topic_name} 成功 (WebSocket: {websocket_id})")
            return True
            
        except Exception as e:
            logger.error(f"订阅设备数据失败：{e}")
            return False
    
    async def unsubscribe_device(self, device_code: str, topic_name: str, websocket_id: str) -> bool:
        """
        取消订阅设备数据

        Args:
            device_code: 设备编号
            topic_name: Topic名称
            websocket_id: WebSocket连接ID

        Returns:
            是否取消成功
        """
        try:
            # 移除设备订阅
            if device_code in self._device_subscriptions:
                self._device_subscriptions[device_code].discard(topic_name)
                if not self._device_subscriptions[device_code]:
                    del self._device_subscriptions[device_code]
            
            # 移除Topic订阅
            if topic_name in self._topic_subscribers:
                self._topic_subscribers[topic_name].discard(websocket_id)
                if not self._topic_subscribers[topic_name]:
                    del self._topic_subscribers[topic_name]
            
            logger.info(f"设备 {device_code} 取消订阅 Topic {topic_name} (WebSocket: {websocket_id})")
            return True
            
        except Exception as e:
            logger.error(f"取消订阅设备数据失败：{e}")
            return False
    
    async def forward_message(self, topic: str, payload: Dict[str, Any]):
        """
        转发消息到订阅的WebSocket
        
        Args:
            topic: MQTT Topic
            payload: 消息内容
        """
        if topic not in self._topic_subscribers:
            return
        
        message = {
            'type': 'device_data',
            'topic': topic,
            'payload': payload,
            'timestamp': datetime.now().isoformat()
        }
        
        # 发送到所有订阅该Topic的WebSocket
        websocket_ids = self._topic_subscribers[topic].copy()
        for websocket_id in websocket_ids:
            try:
                await websocket_manager.send_to_client(websocket_id, message)
            except Exception as e:
                logger.error(f"发送消息到WebSocket {websocket_id} 失败：{e}")
                # 移除失效的连接
                self._topic_subscribers[topic].discard(websocket_id)
    
    async def _process_message_queue(self):
        """处理消息队列"""
        while self._is_running:
            try:
                message = await self._message_queue.get()
                topic = message.get('topic')
                payload = message.get('payload')
                
                if topic and payload:
                    await self.forward_message(topic, payload)
                
                self._message_queue.task_done()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"处理消息队列失败：{e}")
                await asyncio.sleep(0.1)
    
    def on_mqtt_message(self, topic: str, payload: Dict[str, Any]):
        """
        MQTT消息回调（由MQTT采集器调用）
        
        Args:
            topic: MQTT Topic
            payload: 消息内容
        """
        if not self._is_running:
            return
        
        # 检查是否有订阅者
        if topic not in self._topic_subscribers:
            return
        
        # 添加到消息队列
        try:
            self._message_queue.put_nowait({
                'topic': topic,
                'payload': payload
            })
        except asyncio.QueueFull:
            logger.warning("消息队列已满，丢弃消息")
    
    def get_device_subscriptions(self, device_code: str) -> List[str]:
        """获取设备的订阅列表"""
        return list(self._device_subscriptions.get(device_code, []))
    
    def get_topic_subscribers(self, topic_name: str) -> List[str]:
        """获取Topic的订阅者列表"""
        return list(self._topic_subscribers.get(topic_name, []))
    
    def get_status(self) -> Dict[str, Any]:
        """获取转发服务状态"""
        return {
            'is_running': self._is_running,
            'device_subscriptions': {
                str(device_code): list(topics)
                for device_code, topics in self._device_subscriptions.items()
            },
            'topic_subscribers': {
                topic: list(subscribers)
                for topic, subscribers in self._topic_subscribers.items()
            },
            'queue_size': self._message_queue.qsize()
        }


# 全局实例
_data_forwarder: Optional[MQTTDataForwarder] = None


def get_data_forwarder() -> MQTTDataForwarder:
    """获取数据转发器实例（单例模式）"""
    global _data_forwarder
    if _data_forwarder is None:
        _data_forwarder = MQTTDataForwarder()
    return _data_forwarder


async def init_data_forwarder():
    """初始化数据转发器"""
    forwarder = get_data_forwarder()
    await forwarder.start()
    
    # 注册到MQTT采集器
    try:
        collector = get_collector()
        
        # 保存原始的消息处理函数
        original_process_message = getattr(collector, '_process_message', None)
        
        def wrapped_process_message(message_data):
            """包装的消息处理函数"""
            # 调用原始处理函数
            if original_process_message:
                original_process_message(message_data)
            
            # 转发消息
            topic = message_data.get('topic')
            payload = message_data.get('payload')
            if topic and payload:
                forwarder.on_mqtt_message(topic, payload)
        
        collector._process_message = wrapped_process_message
        logger.info("数据转发器已注册到MQTT采集器")
        
    except Exception as e:
        logger.error(f"注册数据转发器失败：{e}")
