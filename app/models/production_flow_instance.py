"""
流程执行实例模型
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from datetime import datetime
from app.database import Base


class ProductionFlowInstance(Base):
    """流程执行实例表"""
    __tablename__ = "production_flow_instances"

    id = Column(Integer, primary_key=True, autoincrement=True)
    flow_id = Column(Integer, ForeignKey('production_flows.id'), nullable=False, index=True, comment='使用的工艺路线ID')
    doc_no = Column(String(100), index=True, comment='关联订单单据号')
    part_number = Column(String(100), index=True, comment='零件号')
    device_code = Column(String(100), comment='主设备编号')
    status = Column(String(20), default='in_progress', index=True, comment='状态: in_progress/completed/paused/cancelled')
    node_statuses = Column(Text, comment='各节点执行状态 JSON: {"node-id": "status", ...}')
    planned_qty = Column(Integer, comment='计划数量')
    completed_qty = Column(Integer, default=0, comment='完成数量')
    record_date = Column(String(10), nullable=False, index=True, comment='日期 YYYY-MM-DD')
    start_time = Column(DateTime, comment='开始时间')
    end_time = Column(DateTime, comment='结束时间')
    notes = Column(Text, comment='备注')
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    __table_args__ = (
        {'comment': '流程执行实例表'}
    )

    def __repr__(self):
        return f"<FlowInstance(id={self.id}, doc_no={self.doc_no}, status={self.status})>"
