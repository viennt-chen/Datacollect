"""
MQTT 数据采集 Schema 定义
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class CollectorStats(BaseModel):
    """采集器状态统计"""
    is_connected: bool = Field(..., description="MQTT 连接状态")
    is_running: bool = Field(..., description="是否正在运行")
    connected_at: Optional[str] = Field(None, description="连接时间")
    disconnected_at: Optional[str] = Field(None, description="断开时间")
    messages_received: int = Field(0, description="接收消息数")
    messages_processed: int = Field(0, description="处理消息数")
    errors: int = Field(0, description="错误计数")
    uptime: float = Field(0.0, description="运行时间（秒）")
    last_message_time: Optional[str] = Field(None, description="最后一条消息时间")
    total_events: int = Field(0, description="总事件数")
    processed_events: int = Field(0, description="已处理事件数")
    failed_events: int = Field(0, description="失败事件数")
    total_records: int = Field(0, description="总记录数")
    stored_records: int = Field(0, description="已存储记录数")
    failed_records: int = Field(0, description="失败记录数")


class CollectorConfig(BaseModel):
    """采集器配置信息"""
    mqtt_server: str = Field(..., description="MQTT 服务器地址")
    mqtt_port: int = Field(..., description="MQTT 端口")
    mqtt_user: str = Field(..., description="MQTT 用户名")
    topics: List[str] = Field(..., description="订阅的主题列表")


class CollectorAction(BaseModel):
    """采集器控制动作"""
    action: str = Field(..., description="控制动作：start/stop")


class ProcessingEventStats(BaseModel):
    """加工事件统计"""
    total: int = Field(..., description="总事件数")
    avg_duringtime: float = Field(..., description="平均加工时长 (ms)")
    avg_machine_duringtime: float = Field(..., description="平均机器工作时间 (ms)")
    machine_count: int = Field(..., description="设备数量")
    operator_count: int = Field(..., description="操作员数量")
    period_days: int = Field(..., description="统计周期（天）")


class RawDataStats(BaseModel):
    """原始数据块统计"""
    total: int = Field(..., description="总数据块数")
    topic_stats: Dict[str, Dict[str, Any]] = Field(..., description="各主题统计")
    period_days: int = Field(..., description="统计周期（天）")
