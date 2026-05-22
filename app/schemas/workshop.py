"""
车间管理 Schema
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class WorkshopBase(BaseModel):
    """车间基础信息"""
    name: str = Field(..., description='车间名称')
    code: str = Field(..., description='车间编码')
    description: Optional[str] = Field(None, description='车间描述')
    location: Optional[str] = Field(None, description='车间位置')
    manager: Optional[str] = Field(None, description='负责人')
    contact: Optional[str] = Field(None, description='联系方式')
    status: str = Field('active', description='状态')
    sort_order: int = Field(0, description='排序')

    class Config:
        from_attributes = True


class WorkshopCreate(WorkshopBase):
    """创建车间"""
    pass


class WorkshopUpdate(BaseModel):
    """更新车间"""
    name: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    manager: Optional[str] = None
    contact: Optional[str] = None
    status: Optional[str] = None
    sort_order: Optional[int] = None


class WorkshopDetail(WorkshopBase):
    """车间详情"""
    id: int
    created_at: datetime
    updated_at: datetime


class WorkshopList(BaseModel):
    """车间列表"""
    total: int
    items: List[WorkshopDetail]
