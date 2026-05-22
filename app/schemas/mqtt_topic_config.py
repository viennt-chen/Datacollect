"""
MQTT Topic 配置 Schema
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class MQTTTopicConfigBase(BaseModel):
    """Topic 配置基础信息"""
    topic_name: str = Field(..., description="Topic 名称")
    description: Optional[str] = Field(None, description="Topic 描述")
    topic_type: str = Field(default='custom', description="Topic 类型：event/compress/custom")
    enabled: bool = Field(default=True, description="是否启用")
    qos: int = Field(default=1, ge=0, le=2, description="MQTT QoS 级别")
    storage_policy: str = Field(default='save_raw', description="存储策略")
    parse_rules: Optional[Dict[str, Any]] = Field(None, description="解析规则")
    device_code: Optional[str] = Field(None, description="关联设备编号")


class MQTTTopicConfigCreate(MQTTTopicConfigBase):
    """创建 Topic 配置"""
    pass


class MQTTTopicConfigUpdate(BaseModel):
    """更新 Topic 配置"""
    description: Optional[str] = None
    topic_type: Optional[str] = None
    enabled: Optional[bool] = None
    qos: Optional[int] = None
    storage_policy: Optional[str] = None
    parse_rules: Optional[Dict[str, Any]] = None
    device_code: Optional[str] = None


class MQTTTopicConfigDetail(MQTTTopicConfigBase):
    """Topic 配置详情"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    device_code: Optional[str] = None
    device_name: Optional[str] = None
    
    class Config:
        from_attributes = True


class MQTTTopicConfigList(BaseModel):
    """Topic 配置列表"""
    total: int
    items: list[MQTTTopicConfigDetail]


class TopicFieldItem(BaseModel):
    """Topic 字段项"""
    name: str
    path: str
    type: str
    unit: Optional[str] = ""
    sample_value: Optional[Any] = None
    label: Optional[str] = None


class TopicFieldsResult(BaseModel):
    """单个 Topic 的字段提取结果"""
    topic_id: int
    topic_name: str
    source: str  # "parse_rules" | "mqtt_buffer" | "none"
    fields: List[TopicFieldItem]


class TopicFieldsResponse(BaseModel):
    """Topic 字段提取响应"""
    topics: List[TopicFieldsResult]
