"""
BOM（物料清单）管理 Schema 定义
"""
from pydantic import BaseModel, Field, field_serializer
from typing import Optional, List
from decimal import Decimal
from datetime import datetime, date


# ============ BOM Item Schemas ============

class BomItemBase(BaseModel):
    """BOM 子项基础信息"""
    child_product_id: int = Field(..., description='子物料 ID')
    quantity: Decimal = Field(default=Decimal('1.00000'), description='用量')
    unit: Optional[str] = Field(None, description='单位')
    reference_designator: Optional[str] = Field(None, description='参考位号')
    item_no: int = Field(0, description='行号')
    remark: Optional[str] = Field(None, description='备注')

    @field_serializer('quantity')
    def serialize_quantity(self, value: Decimal) -> str:
        if value is None:
            return '1.00000'
        return f"{value:.5f}"

    class Config:
        from_attributes = True


class BomItemCreate(BomItemBase):
    """创建 BOM 子项"""
    pass


class BomItemUpdate(BaseModel):
    """更新 BOM 子项"""
    child_product_id: Optional[int] = None
    quantity: Optional[Decimal] = None
    unit: Optional[str] = None
    reference_designator: Optional[str] = None
    item_no: Optional[int] = None
    remark: Optional[str] = None

    @field_serializer('quantity')
    def serialize_quantity(self, value: Decimal) -> str:
        if value is None:
            return '1.00000'
        return f"{value:.5f}"

    class Config:
        from_attributes = True


class BomItemDetail(BomItemBase):
    """BOM 子项详情（含关联物料信息）"""
    id: int
    bom_header_id: int
    created_at: datetime
    updated_at: datetime
    # Joined fields from products table (populated by router)
    child_product_name: Optional[str] = None
    child_product_code: Optional[str] = None
    child_part_number: Optional[str] = None
    child_specification: Optional[str] = None
    child_unit: Optional[str] = None


# ============ BOM Header Schemas ============

class BomHeaderQuery(BaseModel):
    """BOM 查询参数"""
    bom_code: Optional[str] = None
    bom_name: Optional[str] = None
    product_id: Optional[int] = None
    status: Optional[str] = None
    page: int = 1
    page_size: int = 20


class BomHeaderBase(BaseModel):
    """BOM 主表基础信息"""
    bom_code: str = Field(..., description='BOM 编号')
    bom_name: str = Field(..., description='BOM 名称')
    product_id: int = Field(..., description='父物料 ID')
    version: str = Field('V1.0', description='版本号')
    status: str = Field('draft', description='状态')
    effective_date: Optional[date] = Field(None, description='生效日期')
    expiry_date: Optional[date] = Field(None, description='失效日期')
    description: Optional[str] = Field(None, description='描述')

    class Config:
        from_attributes = True


class BomHeaderCreate(BomHeaderBase):
    """创建 BOM（可同时包含子项）"""
    created_by: Optional[str] = None
    items: List[BomItemCreate] = Field(default=[], description='BOM 子项列表')


class BomHeaderUpdate(BaseModel):
    """更新 BOM 主表信息"""
    bom_code: Optional[str] = None
    bom_name: Optional[str] = None
    product_id: Optional[int] = None
    version: Optional[str] = None
    effective_date: Optional[date] = None
    expiry_date: Optional[date] = None
    description: Optional[str] = None
    updated_by: Optional[str] = None

    class Config:
        from_attributes = True


class BomHeaderDetail(BomHeaderBase):
    """BOM 主表详情"""
    id: int
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    # Joined fields
    product_name: Optional[str] = None
    product_code: Optional[str] = None
    product_part_number: Optional[str] = None
    item_count: Optional[int] = None


class BomHeaderWithItems(BomHeaderDetail):
    """BOM 主表详情（含子项列表）"""
    items: List[BomItemDetail] = []


class BomHeaderList(BaseModel):
    """BOM 列表响应"""
    total: int
    items: List[BomHeaderDetail]


# ============ Multi-level BOM Tree ============

class BomTreeNode(BaseModel):
    """多级 BOM 树节点"""
    product_id: int
    product_name: str
    product_code: Optional[str] = None
    part_number: Optional[str] = None
    specification: Optional[str] = None
    quantity: Decimal = Decimal('1.00000')
    unit: Optional[str] = None
    reference_designator: Optional[str] = None
    level: int = 0
    has_bom: bool = False
    bom_item_id: Optional[int] = None
    bom_header_id: Optional[int] = None
    children: List['BomTreeNode'] = []

    class Config:
        from_attributes = True


# ============ BOM Copy Schema ============

class BomCopyRequest(BaseModel):
    """复制 BOM 请求"""
    new_bom_code: str = Field(..., description='新 BOM 编号')
    new_bom_name: Optional[str] = Field(None, description='新 BOM 名称')
    new_version: Optional[str] = Field(None, description='新版本号')


class BomItemReorderRequest(BaseModel):
    """BOM 子项排序请求"""
    item_order: List[int] = Field(..., description="按新顺序排列的子项ID列表")


class BomItemMoveRequest(BaseModel):
    """BOM 子项移动请求（用于 MBOM 编辑器拖拽）"""
    item_id: int = Field(..., description='要移动的子项 ID')
    source_bom_id: int = Field(..., description='源 BOM ID')
    target_bom_id: int = Field(..., description='目标 BOM ID')