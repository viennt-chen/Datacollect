"""
设备管理模型 - 基于 devices 表
"""
from sqlalchemy import Column, String, DateTime, Text, Boolean
from datetime import datetime
from app.database import Base


class Device(Base):
    """设备表"""
    __tablename__ = "devices"
    
    # 主键 - 设备编号
    device_code = Column(String(100), primary_key=True, comment='设备编号')
    
    # 设备名称
    device_name = Column(String(255), nullable=False, comment='设备名称')
    
    # 设备类型
    device_type = Column(String(100), comment='设备类型')
    
    # 设备型号
    model = Column(String(255), comment='设备型号')
    
    # 制造商
    manufacturer = Column(String(255), comment='制造商')
    
    # 所属产线
    line_code = Column(String(100), comment='所属产线')
    
    # 所属工厂
    factory_code = Column(String(100), comment='所属工厂')
    
    # 所属集团
    group_code = Column(String(100), comment='所属集团')
    
    # 设备描述
    description = Column(Text, comment='设备描述')
    
    # 安装位置
    location = Column(String(255), comment='安装位置')
    
    # 设备状态（active/inactive/maintenance，多状态逗号分隔如 processing,alarm）
    status = Column(String(100), default='active', comment='设备状态')
    
    # 是否启用
    is_enabled = Column(Boolean, default=True, comment='是否启用')

    # 是否在看板显示
    show_on_dashboard = Column(Boolean, default=False, comment='是否在看板显示')

    # IP 地址
    ip_address = Column(String(50), comment='IP 地址')
    
    # 关联的 MQTT Topic（JSON 数组格式）
    # 例如：["SHXQ/NO1/KP3/IMG/ProcesEvent", "SHXQ/NO1/KP3/IMG/PV"]
    mqtt_topics = Column(Text, comment='关联的 MQTT Topic 列表（JSON 数组）')
    
    # 创建时间
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')
    
    # 更新时间
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    
    # 创建人
    created_by = Column(String(100), comment='创建人')
    
    # 更新人
    updated_by = Column(String(100), comment='更新人')
    
    def __repr__(self):
        return f"<Device(device_code='{self.device_code}', device_name='{self.device_name}')>"
