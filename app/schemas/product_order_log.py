"""产品订单查询日志 Schema"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class ProductOrderQueryLogBase(BaseModel):
    """产品订单查询日志基础 Schema"""
    part_number: str
    specs: Optional[str] = None
    planned_output: Optional[int] = 0
    order_count: Optional[int] = 0
    saved_count: Optional[int] = 0
    status: Optional[str] = "success"
    error_message: Optional[str] = None
    query_date: str
    execution_type: Optional[str] = "manual"
    duration_seconds: Optional[float] = None


class ProductOrderQueryLogCreate(ProductOrderQueryLogBase):
    """创建日志 Schema"""
    pass


class ProductOrderQueryLogResponse(ProductOrderQueryLogBase):
    """查询日志响应 Schema"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ProductOrderQueryLogListResponse(BaseModel):
    """日志列表响应"""
    total: int
    logs: list[ProductOrderQueryLogResponse]


class ProductOrderQueryLogStats(BaseModel):
    """日志统计信息"""
    total_queries: int = 0
    success_count: int = 0
    failed_count: int = 0
    total_saved: int = 0
    avg_duration: Optional[float] = None
