"""
报警管理模型 - 基于 alarm_records 表
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Float
from datetime import datetime

from app.database import Base


class AlarmRecord(Base):
    """报警记录表"""
    __tablename__ = "alarm_records"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # 报警编号（唯一标识）
    alarm_code = Column(String(100), unique=True, nullable=False, index=True, comment='报警编号')
    
    # 报警来源（设备/系统/人工）
    alarm_source = Column(String(50), nullable=False, comment='报警来源')
    
    # 报警级别（critical/warning/info）
    alarm_level = Column(String(20), nullable=False, index=True, comment='报警级别')
    
    # 报警类型
    alarm_type = Column(String(100), comment='报警类型')
    
    # 报警标题
    title = Column(String(255), nullable=False, comment='报警标题')
    
    # 报警描述
    description = Column(Text, comment='报警描述')
    
    # 关联设备编号
    device_code = Column(String(100), index=True, comment='关联设备编号')
    
    # 关联设备名称
    device_name = Column(String(255), comment='关联设备名称')
    
    # 报警值
    alarm_value = Column(Float, comment='报警值')
    
    # 阈值
    threshold_value = Column(Float, comment='阈值')
    
    # 报警状态（pending/processing/resolved/ignored）
    status = Column(String(20), default='pending', nullable=False, index=True, comment='报警状态')
    
    # 处理人
    handler = Column(String(100), comment='处理人')
    
    # 处理时间
    handled_at = Column(DateTime, comment='处理时间')
    
    # 处理备注
    handle_remark = Column(Text, comment='处理备注')
    
    # 报警时间
    alarm_time = Column(DateTime, nullable=False, index=True, comment='报警时间')
    
    # 创建时间
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')
    
    # 更新时间
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    
    def __repr__(self):
        return f"<AlarmRecord(id={self.id}, alarm_code='{self.alarm_code}', level='{self.alarm_level}')>"
