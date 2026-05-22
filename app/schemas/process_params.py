"""
工艺参数 Pydantic 模型
用于 API 请求和响应的数据验证
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


class ProcessParamBase(BaseModel):
    """工艺参数基础模型"""
    process_type: Optional[str] = None
    machine_id: Optional[str] = None
    product_model: Optional[str] = None
    param_name: str
    param_value: float
    unit: Optional[str] = None
    start_code: Optional[str] = None
    process_no: Optional[str] = None
    batch_no: Optional[str] = None
    operator: Optional[str] = None
    remark: Optional[str] = None


class ProcessParam(ProcessParamBase):
    """工艺参数响应模型"""
    id: int
    create_time: datetime
    
    class Config:
        from_attributes = True


class ProcessParamList(BaseModel):
    """工艺参数列表响应"""
    total: int
    items: List[ProcessParam]


class ProcessParamQuery(BaseModel):
    """工艺参数查询参数"""
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    process_type: Optional[str] = None
    machine_id: Optional[str] = None
    product_model: Optional[str] = None
    param_name: Optional[str] = None
    param_value_min: Optional[float] = None
    param_value_max: Optional[float] = None
    start_code: Optional[str] = None
    process_no: Optional[str] = None
    page: int = 1
    page_size: int = 20


class ProcessParamStats(BaseModel):
    """工艺参数统计信息"""
    total: int
    avg_value: float
    max_value: float
    min_value: float
    machine_count: int
    process_type_count: int


class ProcessParamTrend(BaseModel):
    """工艺参数趋势数据点"""
    time_point: str
    avg_value: float
    max_value: float
    min_value: float
    count: int


class ProcessParamCreate(BaseModel):
    """工艺参数创建请求"""
    process_type: Optional[str] = None
    machine_id: Optional[str] = None
    product_model: Optional[str] = None
    param_name: str
    param_value: float
    unit: Optional[str] = None
    start_code: Optional[str] = None
    process_no: Optional[str] = None
    batch_no: Optional[str] = None
    operator: Optional[str] = None
    remark: Optional[str] = None


class ProcessParamUpdate(BaseModel):
    """工艺参数更新请求"""
    process_type: Optional[str] = None
    machine_id: Optional[str] = None
    product_model: Optional[str] = None
    param_name: Optional[str] = None
    param_value: Optional[float] = None
    unit: Optional[str] = None
    start_code: Optional[str] = None
    process_no: Optional[str] = None
    batch_no: Optional[str] = None
    operator: Optional[str] = None
    remark: Optional[str] = None
