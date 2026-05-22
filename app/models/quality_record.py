"""
质量记录模型
管理产品质量检验记录
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Float
from datetime import datetime
from app.database import Base


class QualityRecord(Base):
    """质量记录表"""
    __tablename__ = "quality_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # 产品信息
    product_code = Column(String(100), nullable=False, index=True, comment="产品编号")
    product_name = Column(String(200), nullable=False, comment="产品名称")

    # 设备信息
    device_code = Column(String(100), index=True, comment="设备编号")

    # 检验信息
    status = Column(String(20), nullable=False, default='passed', index=True,
                    comment="检验状态: passed/failed/pending")
    defect_type = Column(String(100), index=True, comment="缺陷类型")
    defect_description = Column(Text, comment="缺陷描述")

    # 检验员
    inspector = Column(String(100), comment="检验员")

    # 检验时间
    inspect_time = Column(DateTime, default=datetime.now, index=True, comment="检验时间")

    # 数量信息
    quantity = Column(Integer, default=1, comment="检验数量")
    passed_quantity = Column(Integer, default=0, comment="合格数量")
    failed_quantity = Column(Integer, default=0, comment="不合格数量")

    # 备注
    remark = Column(Text, comment="备注")

    # 时间戳
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    # 操作人
    created_by = Column(String(100), comment="创建人")
    updated_by = Column(String(100), comment="更新人")

    __table_args__ = {
        'comment': '质量检验记录表'
    }

    def __repr__(self):
        return f"<QualityRecord(id={self.id}, product={self.product_code}, status={self.status})>"
