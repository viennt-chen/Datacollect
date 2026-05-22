"""
物料管理 Schema 定义
"""
from pydantic import BaseModel, Field, field_serializer
from typing import Optional, List
from decimal import Decimal
from datetime import datetime


MATERIAL_TYPE_CHOICES = {
    'product': '产品',
    'semi_finished': '半成品',
    'material': '原材料',
    'auxiliary': '辅料',
}


class MaterialQuery(BaseModel):
    """物料查询参数"""
    keyword: Optional[str] = None
    u9_material_code: Optional[str] = None
    part_number: Optional[str] = None
    product_name: Optional[str] = None
    category: Optional[str] = None
    project: Optional[str] = None
    workshop: Optional[str] = None
    material_type: Optional[str] = None
    status: Optional[str] = None
    page: int = 1
    page_size: int = 20


class MaterialBase(BaseModel):
    """物料基础信息"""
    u9_material_code: str = Field(..., description='U9 物料号')
    part_number: Optional[str] = Field(None, description='零件号')
    product_name: str = Field(..., description='物料名称')
    description: Optional[str] = Field(None, description='物料描述')
    specification: Optional[str] = Field(None, description='规格型号')
    category: Optional[str] = Field(None, description='物料分类')
    project: Optional[str] = Field(None, description='项目')
    workshop: Optional[str] = Field(None, description='车间')
    unit: Optional[str] = Field(None, description='单位')
    unit_work_time: Decimal = Field(default=Decimal('0.00000'), description='单件工时（小时）')
    material_type: str = Field('product', description='物料类型: product/material/semi_finished')
    status: str = Field('active', description='状态')

    @field_serializer('unit_work_time')
    def serialize_unit_work_time(self, value: Decimal) -> float:
        """将 unit_work_time 转换为浮点数"""
        if value is None:
            return 0.0
        return float(value)

    class Config:
        from_attributes = True


class MaterialCreate(MaterialBase):
    """创建物料请求"""
    created_by: Optional[str] = None


class MaterialUpdate(BaseModel):
    """更新物料请求"""
    u9_material_code: Optional[str] = None
    part_number: Optional[str] = None
    product_name: Optional[str] = None
    description: Optional[str] = None
    specification: Optional[str] = None
    category: Optional[str] = None
    project: Optional[str] = None
    workshop: Optional[str] = None
    unit: Optional[str] = None
    unit_work_time: Optional[Decimal] = None
    material_type: Optional[str] = None
    status: Optional[str] = None
    updated_by: Optional[str] = None

    @field_serializer('unit_work_time')
    def serialize_unit_work_time(self, value: Decimal) -> float:
        """将 unit_work_time 转换为浮点数"""
        if value is None:
            return 0.0
        return float(value)


class MaterialDetail(MaterialBase):
    """物料详情"""
    id: int
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None
    updated_by: Optional[str] = None


class MaterialList(BaseModel):
    """物料列表响应"""
    total: int
    items: List[MaterialDetail]
