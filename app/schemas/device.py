"""
设备管理 Schema 定义
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import json


class DeviceQuery(BaseModel):
    """设备查询参数"""
    device_code: Optional[str] = None
    device_name: Optional[str] = None
    device_type: Optional[str] = None
    status: Optional[str] = None
    line_code: Optional[str] = None
    factory_code: Optional[str] = None
    page: int = 1
    page_size: int = 20


class DeviceBase(BaseModel):
    """设备基础信息"""
    device_code: str = Field(..., description='设备编号')
    device_name: str = Field(..., description='设备名称')
    device_type: Optional[str] = Field(None, description='设备类型')
    model: Optional[str] = Field(None, description='设备型号')
    manufacturer: Optional[str] = Field(None, description='制造商')
    line_code: Optional[str] = Field(None, description='所属产线')
    factory_code: Optional[str] = Field(None, description='所属工厂')
    group_code: Optional[str] = Field(None, description='所属集团')
    description: Optional[str] = Field(None, description='设备描述')
    location: Optional[str] = Field(None, description='安装位置')
    status: str = Field('active', description='设备状态')
    is_enabled: bool = Field(True, description='是否启用')
    show_on_dashboard: bool = Field(False, description='是否在看板显示')
    ip_address: Optional[str] = Field(None, description='IP 地址')
    mqtt_topics: Optional[List[str]] = Field(None, description='关联的 MQTT Topic 列表')
    
    class Config:
        from_attributes = True


class DeviceCreate(DeviceBase):
    """创建设备请求"""
    created_by: Optional[str] = None


class DeviceUpdate(BaseModel):
    """更新设备请求"""
    device_code: Optional[str] = None
    device_name: Optional[str] = None
    device_type: Optional[str] = None
    model: Optional[str] = None
    manufacturer: Optional[str] = None
    line_code: Optional[str] = None
    factory_code: Optional[str] = None
    group_code: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    status: Optional[str] = None
    is_enabled: Optional[bool] = None
    show_on_dashboard: Optional[bool] = None
    ip_address: Optional[str] = None
    mqtt_topics: Optional[List[str]] = Field(None, description='关联的 MQTT Topic 列表')
    updated_by: Optional[str] = None


class DeviceDetail(DeviceBase):
    """设备详情"""
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None
    updated_by: Optional[str] = None


class DeviceList(BaseModel):
    """设备列表响应"""
    total: int
    items: List[DeviceDetail]
