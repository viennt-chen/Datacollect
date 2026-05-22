"""
BOM（物料清单）管理模型 - 离散制造
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Numeric, Date
from datetime import datetime
from app.database import Base


class BomHeader(Base):
    """BOM 主表"""
    __tablename__ = "bom_headers"

    id = Column(Integer, primary_key=True, autoincrement=True, comment='BOM 主键')
    bom_code = Column(String(50), unique=True, nullable=False, index=True, comment='BOM 编号')
    bom_name = Column(String(255), nullable=False, comment='BOM 名称')
    product_id = Column(Integer, nullable=False, index=True, comment='父产品 ID')
    version = Column(String(20), nullable=False, default='V1.0', comment='版本号')
    status = Column(String(20), nullable=False, default='draft', index=True, comment='状态：draft/active/archived')
    effective_date = Column(Date, nullable=True, comment='生效日期')
    expiry_date = Column(Date, nullable=True, comment='失效日期')
    description = Column(Text, comment='BOM 描述')
    created_by = Column(String(100), comment='创建人')
    updated_by = Column(String(100), comment='更新人')
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    def __repr__(self):
        return f"<BomHeader(id={self.id}, bom_code={self.bom_code}, version={self.version})>"


class BomItem(Base):
    """BOM 子项表"""
    __tablename__ = "bom_items"

    id = Column(Integer, primary_key=True, autoincrement=True, comment='BOM 行项 ID')
    bom_header_id = Column(Integer, nullable=False, index=True, comment='所属 BOM 主表 ID')
    child_product_id = Column(Integer, nullable=False, index=True, comment='子物料 ID')
    quantity = Column(Numeric(12, 5), nullable=False, default=1.0, comment='用量')
    unit = Column(String(50), comment='单位')
    reference_designator = Column(String(100), comment='参考位号')
    item_no = Column(Integer, default=0, comment='行号')
    remark = Column(Text, comment='备注')
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    def __repr__(self):
        return f"<BomItem(id={self.id}, bom_header_id={self.bom_header_id}, child_product_id={self.child_product_id})>"
