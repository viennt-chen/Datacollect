"""
产品加工信息 Schema 定义
基于 event_data 表（加工事件数据表）
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ProcessingEventQuery(BaseModel):
    """产品加工事件查询参数"""
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    start_code: Optional[str] = None
    skin_code: Optional[str] = None
    machine_id: Optional[str] = None
    operator_id: Optional[str] = None
    operator_name: Optional[str] = None
    group_code: Optional[str] = None
    factory_code: Optional[str] = None
    line_code: Optional[str] = None
    process_no: Optional[str] = None
    page: int = 1
    page_size: int = 20


class ProcessingEventBase(BaseModel):
    """产品加工事件基础信息"""
    event_uid: str
    start_code: str
    skin_code: Optional[str] = None
    start_time: Optional[int] = None  # 毫秒时间戳
    end_time: Optional[int] = None  # 毫秒时间戳
    start_signal: Optional[int] = None  # 毫秒时间戳
    end_signal: Optional[int] = None  # 毫秒时间戳
    duringtime: Optional[int] = None
    machine_duringtime: Optional[int] = None
    machine_id: Optional[str] = None
    operator_id: Optional[str] = None
    operator_name: Optional[str] = None
    group_code: Optional[str] = None
    group_name: Optional[str] = None
    group_short_name: Optional[str] = None
    factory_code: Optional[str] = None
    factory_name: Optional[str] = None
    line_code: Optional[str] = None
    process_no: Optional[str] = None
    
    class Config:
        from_attributes = True


class ProcessingEventDetail(ProcessingEventBase):
    """产品加工事件详情"""
    id: int
    extra_data: Optional[str] = None  # JSON 字符串
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ProcessingEventList(BaseModel):
    """产品加工事件列表响应"""
    total: int
    items: List[ProcessingEventDetail]


class ProcessingEventStats(BaseModel):
    """产品加工统计信息"""
    total: int
    avg_duringtime: float
    avg_machine_duringtime: float
    machine_count: int
    operator_count: int
    line_count: int


class ProcessingEventTrend(BaseModel):
    """产品加工趋势数据点"""
    time_point: str
    event_count: int
    avg_duringtime: float
    avg_machine_duringtime: float
