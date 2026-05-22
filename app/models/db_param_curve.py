"""
DB参数曲线数据模型
用于存储设备加工时的标准DB参数时间-值曲线
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON, Index, ForeignKey
from datetime import datetime
from app.database import Base


class DBParamCurve(Base):
    """
    DB参数曲线表
    存储设备加工时的标准DB参数时间-值曲线数据
    """
    __tablename__ = "db_param_curves"
    
    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键 ID")
    
    # 设备编号
    device_code = Column(String(100), ForeignKey('devices.device_code'), nullable=False, index=True, comment='设备编号')
    
    # 曲线名称
    curve_name = Column(String(200), nullable=False, comment='曲线名称')
    
    # 产品零件号（可选，用于区分不同产品的曲线）
    part_number = Column(String(100), nullable=True, index=True, comment='产品零件号')
    
    # 伺服轴名称/DB块名称
    servo_axis = Column(String(100), nullable=False, comment='伺服轴名称/DB块名称')
    
    # 曲线数据点（JSON格式）
    # 格式：[{"time": 0, "value": 0}, {"time": 100, "value": 50}, ...]
    # time单位：毫秒，value单位：mm或编码器脉冲或DB参数值
    curve_data = Column(JSON, nullable=False, comment='曲线数据点')
    
    # 曲线元数据
    total_duration_ms = Column(Integer, comment='总时长（毫秒）')
    max_value = Column(Float, comment='最大值')
    min_value = Column(Float, comment='最小值')
    data_points_count = Column(Integer, comment='数据点数量')
    
    # 匹配容差配置
    value_tolerance = Column(Float, default=5.0, comment='值容差（mm或脉冲或参数值）')
    time_tolerance_ms = Column(Integer, default=100, comment='时间容差（毫秒）')
    
    # 是否启用
    enabled = Column(Integer, default=1, comment='是否启用：0-禁用，1-启用')
    
    # 备注说明
    description = Column(Text, comment='备注说明')
    
    # 创建时间
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')
    
    # 更新时间
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    
    __table_args__ = (
        Index('idx_db_param_curves_device_code', 'device_code'),
        Index('idx_db_param_curves_part_number', 'part_number'),
        Index('idx_db_param_curves_enabled', 'enabled'),
        {'comment': 'DB参数曲线表'}
    )
