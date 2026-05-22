"""
工艺参数变更历史 Schema
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ProcessParamHistoryCreate(BaseModel):
    process_id: int
    change_type: str  # 'mqtt_value_change' | 'definition_change'
    param_name: str
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    source: Optional[str] = None
    operator: Optional[str] = None


class ProcessParamHistoryBatchCreate(BaseModel):
    items: List[ProcessParamHistoryCreate]


class ProcessParamHistoryResponse(BaseModel):
    id: int
    process_id: int
    change_type: str
    param_name: str
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    source: Optional[str] = None
    operator: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ProcessParamHistoryListResponse(BaseModel):
    total: int
    items: List[ProcessParamHistoryResponse]
