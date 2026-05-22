"""
WebSocket 服务
功能：提供实时数据推送功能
"""
import asyncio
import json
from typing import List
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect
from collections import defaultdict
import threading


class ConnectionManager:
    """WebSocket 连接管理器"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.topic_connections = defaultdict(list)  # 按主题分类的连接
        self._lock = threading.Lock()
    
    async def connect(self, websocket: WebSocket, topic: str = None):
        """建立连接"""
        await websocket.accept()
        with self._lock:
            self.active_connections.append(websocket)
            if topic:
                self.topic_connections[topic].append(websocket)
    
    def disconnect(self, websocket: WebSocket, topic: str = None):
        """断开连接"""
        with self._lock:
            if websocket in self.active_connections:
                self.active_connections.remove(websocket)
            if topic and websocket in self.topic_connections[topic]:
                self.topic_connections[topic].remove(websocket)
    
    async def broadcast(self, message: dict):
        """广播消息到所有连接"""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except WebSocketDisconnect:
                disconnected.append(connection)
        
        # 清理断开的连接
        with self._lock:
            for conn in disconnected:
                if conn in self.active_connections:
                    self.active_connections.remove(conn)
    
    async def send_to_topic(self, topic: str, message: dict):
        """发送消息到特定主题的连接"""
        disconnected = []
        connections = self.topic_connections.get(topic, []).copy()
        
        for connection in connections:
            try:
                await connection.send_text(json.dumps(message))
            except WebSocketDisconnect:
                disconnected.append(connection)
        
        # 清理断开的连接
        with self._lock:
            for conn in disconnected:
                if conn in self.active_connections:
                    self.active_connections.remove(conn)
                for t, conn_list in self.topic_connections.items():
                    if conn in conn_list:
                        conn_list.remove(conn)


manager = ConnectionManager()


async def websocket_endpoint(websocket: WebSocket, topic: str = "general"):
    """WebSocket 端点"""
    await manager.connect(websocket, topic)
    try:
        while True:
            # 等待客户端消息（可选，根据需求决定是否需要接收客户端消息）
            try:
                data = await websocket.receive_text()
                # 可以在这里处理从客户端接收到的消息
                message = {
                    "type": "client_message",
                    "data": data,
                    "timestamp": datetime.now().isoformat()
                }
                await manager.broadcast(message)
            except:
                # 如果不需要接收客户端消息，可以简单地保持连接
                await asyncio.sleep(1)
    except WebSocketDisconnect:
        manager.disconnect(websocket, topic)
        await manager.broadcast({
            "type": "disconnect",
            "message": "客户端断开连接",
            "timestamp": datetime.now().isoformat()
        })


async def send_realtime_data(topic: str, data: dict):
    """发送实时数据到指定主题"""
    message = {
        "type": "realtime_data",
        "topic": topic,
        "data": data,
        "timestamp": datetime.now().isoformat()
    }
    await manager.send_to_topic(topic, message)


async def send_system_notification(message: str, level: str = "info"):
    """发送系统通知"""
    notification = {
        "type": "notification",
        "level": level,
        "message": message,
        "timestamp": datetime.now().isoformat()
    }
    await manager.broadcast(notification)


# 后台任务示例
async def background_data_push():
    """后台数据推送任务示例"""
    while True:
        try:
            # 示例：定期推送系统状态
            status_data = {
                "cpu_usage": 45.2,
                "memory_usage": 67.8,
                "active_connections": len(manager.active_connections),
                "timestamp": datetime.now().isoformat()
            }
            await send_realtime_data("system_status", status_data)
            await asyncio.sleep(10)  # 每10秒推送一次
        except Exception as e:
            print(f"后台任务出错: {e}")
            await asyncio.sleep(5)