"""
加工信息追溯统一 Schema 定义
包含事件追溯、工艺参数追溯、图表数据等所有追溯相关 Schema
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# ============================================================
# 图表数据 Schema（新增）
# ============================================================

class ChartDataPoint(BaseModel):
    """图表数据点"""
    timestamp_ms: int = Field(..., description="时间戳（毫秒）")
    offset_ms: int = Field(..., description="相对于事件开始时间的偏移（毫秒）")
    value: float = Field(..., description="参数值")


class ChartSeries(BaseModel):
    """图表系列（一条线）"""
    name: str = Field(..., description="参数名称")
    topic: str = Field(..., description="MQTT Topic")
    type: str = Field(..., description="类型: PV/SV/Alarm")
    data_points: List[ChartDataPoint] = Field(default_factory=list, description="数据点列表")


class AlarmDataPoint(BaseModel):
    """报警数据点"""
    timestamp_ms: int = Field(..., description="时间戳（毫秒）")
    offset_ms: int = Field(..., description="相对于事件开始时间的偏移（毫秒）")
    code: Optional[str] = Field(None, description="报警编号")
    level: Optional[str] = Field(None, description="报警级别")
    title: Optional[str] = Field(None, description="报警标题")
    value: Optional[str] = Field(None, description="报警值")


class ChartTimeRange(BaseModel):
    """图表时间范围"""
    start_ms: int = Field(..., description="事件开始时间戳（毫秒）")
    end_ms: int = Field(..., description="事件结束时间戳（毫秒）")


class TraceabilityChartData(BaseModel):
    """图表数据响应"""
    event_uid: str = Field(..., description="事件唯一标识")
    event_time_range: ChartTimeRange = Field(..., description="事件时间范围")
    series: List[ChartSeries] = Field(default_factory=list, description="PV/SV 数据系列")
    alarms: List[AlarmDataPoint] = Field(default_factory=list, description="报警数据点")
    total_points: int = Field(0, description="总数据点数")


class TraceabilityChartQuery(BaseModel):
    """图表查询参数"""
    param_type: str = Field("all", description="参数类型: PV/SV/Alarm/all")
    topic: Optional[str] = Field(None, description="Topic 过滤")


# ============================================================
# 事件追溯 Schema（从 processing_events.py 整合）
# ============================================================

class TraceabilityEventQuery(BaseModel):
    """事件查询参数"""
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


class TraceabilityEventBase(BaseModel):
    """事件基础信息"""
    event_uid: str
    start_code: str
    skin_code: Optional[str] = None
    start_time: Optional[int] = None
    end_time: Optional[int] = None
    start_signal: Optional[int] = None
    end_signal: Optional[int] = None
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


class TraceabilityEventDetail(TraceabilityEventBase):
    """事件详情"""
    id: int
    extra_data: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class TraceabilityEventList(BaseModel):
    """事件列表响应"""
    total: int
    items: List[TraceabilityEventDetail]


class TraceabilityEventStats(BaseModel):
    """事件统计信息"""
    total: int
    avg_duringtime: float
    avg_machine_duringtime: float
    machine_count: int
    operator_count: int
    line_count: int


class TraceabilityEventTrend(BaseModel):
    """事件趋势数据点"""
    time_point: str
    event_count: int
    avg_duringtime: float
    avg_machine_duringtime: float
