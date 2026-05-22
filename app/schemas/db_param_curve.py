"""
DB参数曲线 Schema 定义
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime


class DBParamCurveBase(BaseModel):
    """DB参数曲线基础信息"""
    device_code: str = Field(..., description="设备编号")
    curve_name: str = Field(..., description="曲线名称")
    part_number: Optional[str] = Field(None, description="产品零件号")
    servo_axis: str = Field(..., description="伺服轴名称/DB块名称")
    curve_data: List[Dict[str, Any]] = Field(..., description="曲线数据点")
    value_tolerance: float = Field(default=5.0, description="值容差")
    time_tolerance_ms: int = Field(default=100, description="时间容差（毫秒）")
    enabled: bool = Field(default=True, description="是否启用")
    description: Optional[str] = Field(None, description="备注说明")

    @validator('curve_data')
    def validate_curve_data(cls, v):
        """验证曲线数据格式"""
        if not v:
            raise ValueError("曲线数据不能为空")
        for point in v:
            if 'time' not in point or 'value' not in point:
                raise ValueError("每个数据点必须包含time和value字段")
            if not isinstance(point['time'], (int, float)):
                raise ValueError("time必须是数字")
            if not isinstance(point['value'], (int, float)):
                raise ValueError("value必须是数字")
        return v


class DBParamCurveCreate(DBParamCurveBase):
    """创建DB参数曲线"""
    pass


class DBParamCurveUpdate(BaseModel):
    """更新DB参数曲线"""
    curve_name: Optional[str] = Field(None, description="曲线名称")
    part_number: Optional[str] = Field(None, description="产品零件号")
    servo_axis: Optional[str] = Field(None, description="伺服轴名称/DB块名称")
    curve_data: Optional[List[Dict[str, Any]]] = Field(None, description="曲线数据点")
    value_tolerance: Optional[float] = Field(None, description="值容差")
    time_tolerance_ms: Optional[int] = Field(None, description="时间容差（毫秒）")
    enabled: Optional[bool] = Field(None, description="是否启用")
    description: Optional[str] = Field(None, description="备注说明")


class DBParamCurveDetail(DBParamCurveBase):
    """DB参数曲线详情"""
    id: int
    total_duration_ms: Optional[int]
    max_value: Optional[float]
    min_value: Optional[float]
    data_points_count: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DBParamCurveList(BaseModel):
    """DB参数曲线列表响应"""
    total: int
    items: List[DBParamCurveDetail]


class CurveMatchResult(BaseModel):
    """曲线匹配结果"""
    is_matched: bool = Field(..., description="是否匹配")
    match_score: float = Field(..., description="匹配度（0-100）")
    max_deviation: float = Field(..., description="最大偏差")
    avg_deviation: float = Field(..., description="平均偏差")
    matched_points: int = Field(..., description="匹配的数据点数")
    total_points: int = Field(..., description="总数据点数")
    details: Optional[str] = Field(None, description="详细信息")
