"""
当前加工物料配置数据模型
用于配置从哪个MQTT topic和字段获取当前加工物料的零件号信息
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON, Index, ForeignKey
from datetime import datetime
from app.database import Base

# 导入 Device 模型以确保它在元数据中注册（用于外键关联）
from app.models.device import Device


class CurrentProductConfig(Base):
    """
    当前加工物料配置表
    配置从MQTT消息中获取当前加工物料零件号的规则
    """
    __tablename__ = "current_product_configs"
    
    # 主键 ID
    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键 ID")
    
    # 设备编号
    device_code = Column(String(100), ForeignKey('devices.device_code'), nullable=False, index=True, comment='设备编号')
    
    # MQTT Topic名称
    topic_name = Column(String(255), nullable=False, comment='MQTT Topic名称')
    
    # 字段路径（支持嵌套字段，如：payload.start_code）
    field_path = Column(String(500), nullable=False, comment='字段路径')
    
    # 字段说明
    field_description = Column(String(200), comment='字段说明（如：start_code, part_number等）')
    
    # 截取规则（JSON格式，包含type和params）
    # type: substring, regex_extract, split
    # params: 截取参数，如 "0,10" 或 "\\d+-\\d+" 或 "-$$"
    extraction_rule = Column(JSON, comment='截取规则配置')
    
    # 是否启用
    enabled = Column(Boolean, default=True, nullable=False, comment='是否启用')
    
    # 优先级
    priority = Column(Integer, default=0, comment='优先级（数字越小优先级越高）')
    
    # 备注说明
    description = Column(Text, comment='备注说明')
    
    # 创建时间
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')
    
    # 更新时间
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    
    __table_args__ = (
        Index('idx_cpc_device_code', 'device_code'),
        Index('idx_cpc_enabled', 'enabled'),
        {'comment': '当前加工物料配置表'}
    )
    
    def __repr__(self):
        return f"<CurrentProductConfig(id={self.id}, device_code='{self.device_code}', topic_name='{self.topic_name}', field_path='{self.field_path}')>"
