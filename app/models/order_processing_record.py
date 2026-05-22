"""
订单加工记录模型
记录每台设备当天的订单加工情况（本地记录，区别于 ERP U9 订单）
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, UniqueConstraint, Index
from datetime import datetime
from app.database import Base
from app.models.device import Device


class OrderProcessingRecord(Base):
    """订单加工记录表"""
    __tablename__ = "order_processing_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    device_code = Column(String(100), ForeignKey('devices.device_code'), nullable=False, index=True, comment='设备编号')
    part_number = Column(String(100), index=True, comment='零件号')
    u9_material_code = Column(String(100), comment='U9物料号')
    doc_no = Column(String(100), comment='订单单据号')
    planned_qty = Column(Integer, comment='计划数量')
    completed_qty = Column(Integer, default=0, comment='已完成数量')
    eligible_qty = Column(Integer, default=0, comment='合格数量')
    scrap_qty = Column(Integer, default=0, comment='报废数量')
    status = Column(String(20), default='in_progress', comment='状态: in_progress/completed/paused')
    start_time = Column(DateTime, comment='开始加工时间')
    end_time = Column(DateTime, comment='结束加工时间')
    record_date = Column(String(10), nullable=False, index=True, comment='记录日期 YYYY-MM-DD')
    notes = Column(Text, comment='备注')
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    __table_args__ = (
        UniqueConstraint('device_code', 'record_date', 'doc_no', name='uq_device_date_docno'),
        Index('idx_opr_device_date', 'device_code', 'record_date'),
        Index('idx_opr_status', 'status'),
        {'comment': '订单加工记录表'}
    )

    def __repr__(self):
        return f"<OrderProcessingRecord(id={self.id}, device={self.device_code}, doc_no={self.doc_no}, date={self.record_date})>"
