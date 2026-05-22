"""
车间管理模型
"""
from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime
from app.database import Base


class Workshop(Base):
    """车间表"""
    __tablename__ = "workshops"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False, index=True, comment='车间名称')
    code = Column(String(50), unique=True, nullable=False, index=True, comment='车间编码')
    description = Column(Text, comment='车间描述')
    location = Column(String(200), comment='车间位置')
    manager = Column(String(100), comment='负责人')
    contact = Column(String(100), comment='联系方式')
    status = Column(String(20), default='active', comment='状态：active/inactive')
    sort_order = Column(Integer, default=0, comment='排序')
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    def __repr__(self):
        return f"<Workshop(id={self.id}, name={self.name}, code={self.code})>"
