"""
物料管理模型 - 基于 products 表
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Numeric
from datetime import datetime

from app.database import Base


class Material(Base):
    """物料表"""
    __tablename__ = "products"

    # 主键
    id = Column(Integer, primary_key=True, autoincrement=True)

    # U9 物料号（唯一标识）
    u9_material_code = Column(String(100), unique=True, nullable=False, index=True, comment='U9 物料号')

    # 零件号
    part_number = Column(String(100), nullable=True, index=True, comment='零件号')

    # 物料名称
    product_name = Column(String(255), nullable=False, comment='物料名称')

    # 物料描述
    description = Column(Text, comment='物料描述')

    # 规格型号
    specification = Column(String(255), comment='规格型号')

    # 物料分类
    category = Column(String(100), comment='物料分类')

    # 项目
    project = Column(String(255), comment='项目')

    # 车间
    workshop = Column(String(100), comment='车间')

    # 单位
    unit = Column(String(50), comment='单位')

    # 单件工时
    unit_work_time = Column(Numeric(10, 5), comment='单件工时（小时）')

    # 物料类型（product=产品, semi_finished=半成品, material=原材料, auxiliary=辅料）
    material_type = Column(String(20), default='product', nullable=False, index=True, comment='物料类型: product/semi_finished/material/auxiliary')

    # 状态（启用/禁用）
    status = Column(String(20), default='active', comment='状态')

    # 创建时间
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')

    # 更新时间
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    # 创建人
    created_by = Column(String(100), comment='创建人')

    # 更新人
    updated_by = Column(String(100), comment='更新人')
