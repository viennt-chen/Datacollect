"""
加工事件数据模型
用于存储加工事件的详细信息
"""
from sqlalchemy import Column, Integer, String, DateTime, BigInteger, Text, Index
from datetime import datetime

from app.database import Base


class EventData(Base):
    """
    加工事件数据表
    存储从加工事件 Topic 解析的完整数据
    """
    __tablename__ = "event_data"
    
    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键 ID")
    
    # 事件唯一标识
    event_uid = Column(String(100), unique=True, index=True, comment="事件唯一标识")
    
    # 启动码和皮肤码
    start_code = Column(String(200), comment="启动码")
    skin_code = Column(String(500), comment="皮肤码")
    
    # 时间信息（毫秒时间戳）
    start_time = Column(BigInteger, comment="开始时间（毫秒时间戳）")
    end_time = Column(BigInteger, comment="结束时间（毫秒时间戳）")
    start_signal = Column(BigInteger, comment="开始信号时间（毫秒时间戳）")
    end_signal = Column(BigInteger, comment="结束信号时间（毫秒时间戳）")
    
    # 耗时信息（毫秒）
    duringtime = Column(Integer, comment="总耗时（毫秒）")
    machine_duringtime = Column(Integer, comment="机器耗时（毫秒）")
    
    # 设备和操作员信息
    machine_id = Column(String(100), index=True, comment="设备 ID")
    operator_id = Column(String(100), index=True, comment="操作员 ID")
    operator_name = Column(String(200), comment="操作员姓名")
    
    # 分组信息
    group_code = Column(String(50), comment="集团代码")
    group_name = Column(String(200), comment="集团名称")
    group_short_name = Column(String(100), comment="集团简称")
    factory_code = Column(String(50), comment="工厂代码")
    factory_name = Column(String(200), comment="工厂名称")
    line_code = Column(String(50), comment="产线代码")
    process_no = Column(String(50), comment="工序编号")
    
    # 额外数据（JSON 格式，存储未映射的字段）
    extra_data = Column(Text, comment="额外数据（JSON 格式）")
    
    # 元数据
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    __table_args__ = (
        Index('idx_event_uid', 'event_uid'),
        Index('idx_machine_id', 'machine_id'),
        Index('idx_operator_id', 'operator_id'),
        Index('idx_start_time', 'start_time'),
        Index('idx_start_code', 'start_code', unique=True),
        {'comment': '加工事件数据表'}
    )
