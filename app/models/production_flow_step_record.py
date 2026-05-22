"""
工序执行记录模型
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class ProductionFlowStepRecord(Base):
    """工序执行记录表"""
    __tablename__ = "production_flow_step_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    instance_id = Column(Integer, ForeignKey('production_flow_instances.id'), nullable=False, index=True, comment='所属实例ID')
    step_id = Column(Integer, ForeignKey('production_flow_steps.id'), nullable=False, comment='工序定义ID')
    step_order = Column(Integer, nullable=False, comment='步骤顺序')
    device_code = Column(String(100), comment='实际使用设备')
    status = Column(String(20), default='pending', index=True, comment='状态: pending/in_progress/completed/skipped')
    start_time = Column(DateTime, comment='开始时间')
    end_time = Column(DateTime, comment='结束时间')
    completed_qty = Column(Integer, default=0, comment='该工序完成数量')
    notes = Column(Text, comment='备注')
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    # 关联
    instance = relationship("ProductionFlowInstance", back_populates="step_records")

    __table_args__ = (
        UniqueConstraint('instance_id', 'step_order', name='uq_instance_step_order'),
        {'comment': '工序执行记录表'}
    )

    def __repr__(self):
        return f"<StepRecord(id={self.id}, instance={self.instance_id}, order={self.step_order}, status={self.status})>"
