"""
工艺路线模板模型
"""
from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime
from app.database import Base


class ProductionFlow(Base):
    """工艺路线模板表"""
    __tablename__ = "production_flows"

    id = Column(Integer, primary_key=True, autoincrement=True)
    flow_code = Column(String(50), unique=True, nullable=False, index=True, comment='流程编码')
    flow_name = Column(String(100), nullable=False, comment='流程名称')
    description = Column(Text, comment='描述')
    status = Column(Text, default='active', comment='状态: active/inactive')
    nodes_data = Column(Text, comment='流程图节点数据 (JSON)')
    edges_data = Column(Text, comment='流程图连线数据 (JSON)')
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    __table_args__ = (
        {'comment': '工艺路线模板表'}
    )

    def __repr__(self):
        return f"<ProductionFlow(id={self.id}, code={self.flow_code}, name={self.flow_name})>"
