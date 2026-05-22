"""
项目管理模型
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Date
from datetime import datetime
from app.database import Base


class Project(Base):
    """项目表"""
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), unique=True, nullable=False, index=True, comment='项目名称')
    code = Column(String(50), unique=True, nullable=False, index=True, comment='项目编码')
    description = Column(Text, comment='项目描述')
    customer = Column(String(200), comment='客户名称')
    manager = Column(String(100), comment='项目经理')
    start_date = Column(String(20), comment='开始日期')
    end_date = Column(String(20), comment='结束日期')
    status = Column(String(20), default='active', comment='状态：active/completed/suspended/inactive')
    sort_order = Column(Integer, default=0, comment='排序')
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    def __repr__(self):
        return f"<Project(id={self.id}, name={self.name}, code={self.code})>"
