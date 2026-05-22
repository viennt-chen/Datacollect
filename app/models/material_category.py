"""
物料分类模型 - 两级分类配置
"""
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.database import Base


class MaterialCategory(Base):
    """物料分类表"""
    __tablename__ = "material_categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    type_key = Column(String(50), nullable=False, index=True, comment='物料类型键: product/material/auxiliary')
    type_name = Column(String(50), nullable=False, comment='物料类型名称: 产品/原材料/辅料')
    category_name = Column(String(100), nullable=False, comment='分类名称')
    sort_order = Column(Integer, default=0, comment='排序')
    created_at = Column(DateTime, server_default=func.now(), comment='创建时间')
