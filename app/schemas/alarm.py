"""
报警管理 Schema 定义
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class AlarmQuery(BaseModel):
    """报警查询参数"""
    alarm_code: Optional[str] = None
    alarm_source: Optional[str] = None
    alarm_level: Optional[str] = None
    alarm_type: Optional[str] = None
    status: Optional[str] = None
    device_code: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    page: int = 1
    page_size: int = 20


class AlarmBase(BaseModel):
    """报警基础信息"""
    alarm_code: str = Field(..., description='报警编号')
    alarm_source: str = Field(..., description='报警来源')
    alarm_level: str = Field(..., description='报警级别')
    alarm_type: Optional[str] = Field(None, description='报警类型')
    title: str = Field(..., description='报警标题')
    description: Optional[str] = Field(None, description='报警描述')
    device_code: Optional[str] = Field(None, description='关联设备编号')
    device_name: Optional[str] = Field(None, description='关联设备名称')
    alarm_value: Optional[float] = Field(None, description='报警值')
    threshold_value: Optional[float] = Field(None, description='阈值')
    status: str = Field('pending', description='报警状态')
    alarm_time: datetime = Field(..., description='报警时间')
    
    class Config:
        from_attributes = True


class AlarmCreate(AlarmBase):
    """创建报警请求"""
    pass


class AlarmUpdate(BaseModel):
    """更新报警请求"""
    status: Optional[str] = None
    handler: Optional[str] = None
    handle_remark: Optional[str] = None


class AlarmHandle(BaseModel):
    """处理报警请求"""
    status: str = Field(..., description='处理状态')
    handler: Optional[str] = None
    handle_remark: Optional[str] = None


class AlarmDetail(AlarmBase):
    """报警详情"""
    id: int
    handler: Optional[str] = None
    handled_at: Optional[datetime] = None
    handle_remark: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class AlarmList(BaseModel):
    """报警列表响应"""
    total: int
    items: List[AlarmDetail]


class AlarmStats(BaseModel):
    """报警统计信息"""
    total: int = Field(0, description='总报警数')
    pending: int = Field(0, description='待处理')
    processing: int = Field(0, description='处理中')
    resolved: int = Field(0, description='已解决')
    ignored: int = Field(0, description='已忽略')
    critical: int = Field(0, description='严重报警')
    warning: int = Field(0, description='警告')
    info: int = Field(0, description='信息')
