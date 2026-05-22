"""
项目管理 Schema
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ProjectBase(BaseModel):
    """项目基础信息"""
    name: str = Field(..., description='项目名称')
    code: str = Field(..., description='项目编码')
    description: Optional[str] = Field(None, description='项目描述')
    customer: Optional[str] = Field(None, description='客户名称')
    manager: Optional[str] = Field(None, description='项目经理')
    start_date: Optional[str] = Field(None, description='开始日期')
    end_date: Optional[str] = Field(None, description='结束日期')
    status: str = Field('active', description='状态')
    sort_order: int = Field(0, description='排序')

    class Config:
        from_attributes = True


class ProjectCreate(ProjectBase):
    """创建项目"""
    pass


class ProjectUpdate(BaseModel):
    """更新项目"""
    name: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None
    customer: Optional[str] = None
    manager: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    status: Optional[str] = None
    sort_order: Optional[int] = None


class ProjectDetail(ProjectBase):
    """项目详情"""
    id: int
    created_at: datetime
    updated_at: datetime


class ProjectList(BaseModel):
    """项目列表"""
    total: int
    items: List[ProjectDetail]
