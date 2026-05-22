"""
订单加工记录 Schema
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class OrderProcessingRecordCreate(BaseModel):
    """创建订单加工记录"""
    device_code: str = Field(..., description="设备编号")
    part_number: str = Field(..., min_length=1, description="零件号")
    u9_material_code: Optional[str] = Field(None, description="U9物料号")
    doc_no: Optional[str] = Field(None, description="订单单据号")
    planned_qty: Optional[int] = Field(None, ge=0, description="计划数量")
    completed_qty: Optional[int] = Field(0, ge=0, description="已完成数量")
    eligible_qty: Optional[int] = Field(0, ge=0, description="合格数量")
    scrap_qty: Optional[int] = Field(0, ge=0, description="报废数量")
    status: Optional[str] = Field('in_progress', description="状态: in_progress/completed/paused")
    start_time: Optional[datetime] = Field(None, description="开始加工时间")
    notes: Optional[str] = Field(None, description="备注")


class OrderProcessingRecordUpdate(BaseModel):
    """更新订单加工记录"""
    part_number: Optional[str] = None
    u9_material_code: Optional[str] = None
    doc_no: Optional[str] = None
    planned_qty: Optional[int] = Field(None, ge=0)
    completed_qty: Optional[int] = Field(None, ge=0)
    eligible_qty: Optional[int] = Field(None, ge=0)
    scrap_qty: Optional[int] = Field(None, ge=0)
    status: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    notes: Optional[str] = None


class OrderProcessingRecordDetail(BaseModel):
    """订单加工记录详情"""
    id: int
    device_code: str
    part_number: Optional[str] = None
    u9_material_code: Optional[str] = None
    doc_no: Optional[str] = None
    planned_qty: Optional[int] = None
    completed_qty: int = 0
    eligible_qty: int = 0
    scrap_qty: int = 0
    status: str = 'in_progress'
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    record_date: str
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class OrderProcessingRecordList(BaseModel):
    """订单加工记录列表"""
    total: int
    items: List[OrderProcessingRecordDetail]


class OrderProcessingStats(BaseModel):
    """订单加工统计"""
    total_records: int = 0
    in_progress: int = 0
    completed: int = 0
    paused: int = 0
    total_planned: int = 0
    total_completed: int = 0
    total_eligible: int = 0
    total_scrap: int = 0
    overall_completion_rate: float = 0.0


# --- 完工比对 Schema ---

class CompletionComparisonItem(BaseModel):
    """单个订单比对结果"""
    doc_no: str
    part_number: Optional[str] = None
    u9_material_code: Optional[str] = None
    planned_qty: int = 0
    local_completed: int = 0
    u9_completed: int = 0
    u9_eligible: int = 0
    u9_scrap: int = 0
    diff: int = 0
    completion_rate: float = 0.0
    status: str = "normal"  # normal / local_ahead / local_behind
    record_count: int = 0


class CompletionComparisonSummary(BaseModel):
    """完工比对汇总"""
    record_date: str
    total_orders: int = 0
    total_planned: int = 0
    total_local_completed: int = 0
    total_u9_completed: int = 0
    total_u9_eligible: int = 0
    total_u9_scrap: int = 0
    total_diff: int = 0
    overall_completion_rate: float = 0.0


class CompletionComparisonResponse(BaseModel):
    """完工比对响应"""
    summary: CompletionComparisonSummary
    items: List[CompletionComparisonItem]


class HourlyTimelineItem(BaseModel):
    """小时产量时间线条目"""
    hour: str
    count: int
    avg_duration_ms: int = 0


class OrderTimelineResponse(BaseModel):
    """订单时间线响应"""
    doc_no: str
    record_date: str
    device_codes: List[str] = []
    total_completed: int = 0
    timeline: List[HourlyTimelineItem] = []


class BackfillResult(BaseModel):
    """补漏结果"""
    success: bool
    processed: int = 0
    created: int = 0
    updated: int = 0
    skipped: int = 0
    errors: int = 0
    detail: Optional[str] = None


class ReconcileResult(BaseModel):
    """状态同步结果"""
    success: bool
    updated: int = 0
    record_date: Optional[str] = None
    detail: Optional[str] = None


class LinkStatusResponse(BaseModel):
    """关联服务状态"""
    trigger: dict = {}
    scheduler: dict = {}
