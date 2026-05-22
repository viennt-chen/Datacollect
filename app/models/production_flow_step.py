"""
工艺路线步骤模型
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class ProductionFlowStep(Base):
    """工艺路线步骤表"""
    __tablename__ = "production_flow_steps"

    id = Column(Integer, primary_key=True, autoincrement=True)
    flow_id = Column(Integer, ForeignKey('production_flows.id'), nullable=False, index=True, comment='所属流程ID')
    step_order = Column(Integer, nullable=False, comment='步骤顺序')
    step_name = Column(String(100), nullable=False, comment='工序名称')
    step_code = Column(String(50), comment='工序编码')
    device_type = Column(String(100), comment='设备类型')
    expected_duration_min = Column(Integer, comment='预计工时（分钟）')
    description = Column(Text, comment='描述')
    is_required = Column(Boolean, default=True, comment='是否必经工序')
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')

    # 关联
    flow = relationship("ProductionFlow", back_populates="steps")

    __table_args__ = (
        UniqueConstraint('flow_id', 'step_order', name='uq_flow_step_order'),
        {'comment': '工艺路线步骤表'}
    )

    def __repr__(self):
        return f"<FlowStep(id={self.id}, flow_id={self.flow_id}, order={self.step_order}, name={self.step_name})>"
