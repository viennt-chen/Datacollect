"""
工艺定义 Schemas
"""
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class ProcessDefinitionBase(BaseModel):
    process_code: str
    process_name: str
    description: Optional[str] = None
    process_type: str = 'other'
    device_codes: Optional[List[str]] = []
    mqtt_topic_ids: Optional[List[int]] = []
    product_codes: Optional[List[str]] = []
    parameters: Optional[Dict[str, Any]] = {}
    status: str = 'active'
    created_by: Optional[str] = None
    updated_by: Optional[str] = None


class ProcessDefinitionCreate(ProcessDefinitionBase):
    pass


class ProcessDefinitionUpdate(BaseModel):
    process_code: Optional[str] = None
    process_name: Optional[str] = None
    description: Optional[str] = None
    process_type: Optional[str] = None
    device_codes: Optional[List[str]] = None
    mqtt_topic_ids: Optional[List[int]] = None
    product_codes: Optional[List[str]] = None
    parameters: Optional[Dict[str, Any]] = None
    status: Optional[str] = None
    updated_by: Optional[str] = None


class ProcessDefinitionResponse(ProcessDefinitionBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # 关联的设备和 Topic 详情（可选填充）
    devices: Optional[List[Dict[str, Any]]] = None
    topics: Optional[List[Dict[str, Any]]] = None

    class Config:
        from_attributes = True


class ProcessDefinitionListResponse(BaseModel):
    total: int
    items: List[ProcessDefinitionResponse]
