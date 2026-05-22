"""
生产流程管理 Schema（流程图版）
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# --- Flow Template ---

class FlowBase(BaseModel):
    flow_code: str = Field(..., min_length=1, description="流程编码")
    flow_name: str = Field(..., min_length=1, description="流程名称")
    description: Optional[str] = None
    status: str = "active"


class FlowCreate(FlowBase):
    nodes_data: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="Vue Flow 节点数组")
    edges_data: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="Vue Flow 边数组")


class FlowUpdate(BaseModel):
    flow_code: Optional[str] = None
    flow_name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    nodes_data: Optional[List[Dict[str, Any]]] = None
    edges_data: Optional[List[Dict[str, Any]]] = None


class FlowResponse(FlowBase):
    id: int
    nodes_data: Optional[List[Dict[str, Any]]] = []
    edges_data: Optional[List[Dict[str, Any]]] = []
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class FlowListResponse(BaseModel):
    total: int
    items: List[FlowResponse]


class FlowSimpleResponse(BaseModel):
    """简化的流程信息（下拉选择用）"""
    id: int
    flow_code: str
    flow_name: str
    node_count: int = 0

    class Config:
        from_attributes = True


# --- Instance ---

class FlowInstanceCreate(BaseModel):
    flow_id: int = Field(..., description="工艺路线ID")
    doc_no: Optional[str] = None
    part_number: Optional[str] = None
    device_code: Optional[str] = None
    planned_qty: Optional[int] = None
    record_date: Optional[str] = None
    notes: Optional[str] = None


class FlowInstanceResponse(BaseModel):
    id: int
    flow_id: int
    doc_no: Optional[str] = None
    part_number: Optional[str] = None
    device_code: Optional[str] = None
    status: str
    node_statuses: Optional[Dict[str, str]] = {}
    planned_qty: Optional[int] = None
    completed_qty: int = 0
    record_date: str
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class FlowInstanceListResponse(BaseModel):
    total: int
    items: List[FlowInstanceResponse]


class NodeStatusUpdate(BaseModel):
    status: str = Field(..., description="节点状态: pending/in_progress/completed/skipped")
    device_code: Optional[str] = None
    completed_qty: Optional[int] = Field(None, ge=0)
    notes: Optional[str] = None


class FlowInstanceStats(BaseModel):
    total: int = 0
    in_progress: int = 0
    completed: int = 0
    paused: int = 0
    cancelled: int = 0
    total_planned: int = 0
    total_completed: int = 0
