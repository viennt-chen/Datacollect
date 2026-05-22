"""
工艺定义模型
管理制造工艺及其与设备、MQTT Topic 的关联
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Index
from app.database import Base
from datetime import datetime


class ProcessDefinition(Base):
    """工艺定义表"""
    __tablename__ = "process_definitions"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # 工艺编码（唯一）
    process_code = Column(String(50), unique=True, nullable=False, index=True, comment='工艺编码')

    # 工艺名称
    process_name = Column(String(100), nullable=False, comment='工艺名称')

    # 工艺描述
    description = Column(Text, comment='工艺描述')

    # 工艺类型
    process_type = Column(String(50), default='other', index=True, comment='工艺类型: injection/cnc/assembly/inspection/other')

    # 关联设备编码列表（JSON）
    device_codes = Column(Text, default='[]', comment='关联设备编码 JSON 列表')

    # 关联 MQTT Topic ID 列表（JSON）
    mqtt_topic_ids = Column(Text, default='[]', comment='关联 MQTT Topic ID JSON 列表')

    # 关联产品/物料编码列表（JSON）
    product_codes = Column(Text, comment='关联产品物料编码 JSON 列表')

    # 工艺参数定义（JSON）
    parameters = Column(Text, default='{}', comment='工艺参数定义 JSON')

    # 状态
    status = Column(String(20), default='active', index=True, comment='状态: active/inactive')

    # 时间戳
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    # 操作人
    created_by = Column(String(100), comment='创建人')
    updated_by = Column(String(100), comment='更新人')

    def __repr__(self):
        return f"<ProcessDefinition(id={self.id}, code={self.process_code}, name={self.process_name})>"
