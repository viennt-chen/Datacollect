"""
质量记录 Schemas
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class QualityRecordBase(BaseModel):
    product_code: str
    product_name: str
    device_code: Optional[str] = None
    status: str = 'passed'
    defect_type: Optional[str] = None
    defect_description: Optional[str] = None
    inspector: Optional[str] = None
    inspect_time: Optional[datetime] = None
    quantity: int = 1
    passed_quantity: int = 0
    failed_quantity: int = 0
    remark: Optional[str] = None


class QualityRecordCreate(QualityRecordBase):
    pass


class QualityRecordUpdate(BaseModel):
    product_code: Optional[str] = None
    product_name: Optional[str] = None
    device_code: Optional[str] = None
    status: Optional[str] = None
    defect_type: Optional[str] = None
    defect_description: Optional[str] = None
    inspector: Optional[str] = None
    inspect_time: Optional[datetime] = None
    quantity: Optional[int] = None
    passed_quantity: Optional[int] = None
    failed_quantity: Optional[int] = None
    remark: Optional[str] = None


class QualityRecordResponse(QualityRecordBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None

    class Config:
        from_attributes = True


class QualityRecordListResponse(BaseModel):
    total: int
    data: list[QualityRecordResponse]


class QualityStatsResponse(BaseModel):
    total: int = 0
    passed: int = 0
    failed: int = 0
    pending: int = 0
    today: int = 0
    week: int = 0
    passRate: float = 0.0
    defect_distribution: list = []
