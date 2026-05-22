"""
事件数据关联模型
用于存储 EventData 与 SV/PV/Alarm 的关联关系
"""
from sqlalchemy import Column, Integer, String, BigInteger, DateTime, Text, JSON, Index, ForeignKey
from datetime import datetime

from app.database import Base


class EventSVRelation(Base):
    """
    事件-SV关联表
    存储加工事件与SV(设定工艺参数)的关联关系
    """
    __tablename__ = "event_sv_relations"
    
    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键 ID")
    
    # 关联的事件ID
    event_id = Column(BigInteger, nullable=False, index=True, comment="关联的事件ID")
    
    # 设备编号
    machine_id = Column(String(100), nullable=False, index=True, comment="设备编号")
    
    # SV Topic名称
    sv_topic = Column(String(200), nullable=False, index=True, comment="SV Topic名称")
    
    # SV记录ID
    sv_record_id = Column(BigInteger, nullable=False, index=True, comment="SV记录ID")
    
    # SV数据快照（解压后的关键参数）
    sv_data_snapshot = Column(JSON, comment="SV数据快照")
    
    # 时间匹配信息
    sv_timestamp = Column(DateTime(6), comment="SV数据时间戳")
    time_offset_ms = Column(Integer, comment="时间偏移量（毫秒）")
    
    # 创建时间
    created_at = Column(DateTime(6), default=datetime.now, comment="创建时间")
    
    __table_args__ = (
        Index('idx_event_sv_event_id', 'event_id'),
        Index('idx_event_sv_machine_time', 'machine_id', 'sv_timestamp'),
        {'comment': '事件-SV关联表'}
    )


class EventPVRelation(Base):
    """
    事件-PV关联表
    存储加工事件与PV(过程变量)的关联关系
    """
    __tablename__ = "event_pv_relations"
    
    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键 ID")
    
    # 关联的事件ID
    event_id = Column(BigInteger, nullable=False, index=True, comment="关联的事件ID")
    
    # 设备编号
    machine_id = Column(String(100), nullable=False, index=True, comment="设备编号")
    
    # PV Topic名称
    pv_topic = Column(String(200), nullable=False, index=True, comment="PV Topic名称")
    
    # PV记录ID
    pv_record_id = Column(BigInteger, nullable=False, index=True, comment="PV记录ID")
    
    # PV数据快照（解压后的关键参数）
    pv_data_snapshot = Column(JSON, comment="PV数据快照")
    
    # 时间匹配信息
    pv_timestamp = Column(DateTime(6), comment="PV数据时间戳")
    time_offset_ms = Column(Integer, comment="时间偏移量（毫秒）")
    
    # 对应的SV点位信息
    sv_point_id = Column(String(100), comment="对应的SV点位ID")
    sv_value_range = Column(JSON, comment="对应的SV值范围")
    
    # 创建时间
    created_at = Column(DateTime(6), default=datetime.now, comment="创建时间")
    
    __table_args__ = (
        Index('idx_event_pv_event_id', 'event_id'),
        Index('idx_event_pv_machine_time', 'machine_id', 'pv_timestamp'),
        {'comment': '事件-PV关联表'}
    )


class EventAlarmRelation(Base):
    """
    事件-报警关联表
    存储加工事件期间的报警记录
    """
    __tablename__ = "event_alarm_relations"
    
    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键 ID")
    
    # 关联的事件ID
    event_id = Column(BigInteger, nullable=False, index=True, comment="关联的事件ID")
    
    # 设备编号
    machine_id = Column(String(100), nullable=False, index=True, comment="设备编号")
    
    # 报警记录ID
    alarm_record_id = Column(BigInteger, nullable=False, index=True, comment="报警记录ID")
    
    # 报警信息快照
    alarm_code = Column(String(100), comment="报警编号")
    alarm_level = Column(String(20), comment="报警级别")
    alarm_type = Column(String(100), comment="报警类型")
    alarm_title = Column(String(255), comment="报警标题")
    alarm_value = Column(String(100), comment="报警值")
    
    # 报警时间
    alarm_time = Column(DateTime(6), comment="报警时间")
    
    # 时间偏移（相对于事件开始时间）
    time_offset_from_start_ms = Column(Integer, comment="相对于事件开始时间的偏移量（毫秒）")
    
    # 创建时间
    created_at = Column(DateTime(6), default=datetime.now, comment="创建时间")
    
    __table_args__ = (
        Index('idx_event_alarm_event_id', 'event_id'),
        Index('idx_event_alarm_machine_time', 'machine_id', 'alarm_time'),
        {'comment': '事件-报警关联表'}
    )


class EventDataRelationSummary(Base):
    """
    事件关联汇总表
    存储事件的关联统计信息和状态
    """
    __tablename__ = "event_data_relation_summary"
    
    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键 ID")
    
    # 事件ID
    event_id = Column(BigInteger, nullable=False, unique=True, index=True, comment="事件ID")
    
    # 设备编号
    machine_id = Column(String(100), nullable=False, index=True, comment="设备编号")
    
    # 事件时间范围
    event_start_time = Column(BigInteger, comment="事件开始时间（毫秒时间戳）")
    event_end_time = Column(BigInteger, comment="事件结束时间（毫秒时间戳）")
    
    # 关联统计
    sv_count = Column(Integer, default=0, comment="关联的SV数量")
    pv_count = Column(Integer, default=0, comment="关联的PV数量")
    alarm_count = Column(Integer, default=0, comment="关联的报警数量")
    
    # 关联状态
    sv_matched = Column(Integer, default=0, comment="SV是否已匹配：0-未匹配，1-已匹配")
    pv_matched = Column(Integer, default=0, comment="PV是否已匹配：0-未匹配，1-已匹配")
    alarm_matched = Column(Integer, default=0, comment="报警是否已匹配：0-未匹配，1-已匹配")
    
    # 最后匹配时间
    last_match_time = Column(DateTime(6), comment="最后匹配时间")
    
    # 创建和更新时间
    created_at = Column(DateTime(6), default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime(6), default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    __table_args__ = (
        Index('idx_relation_summary_event_id', 'event_id'),
        Index('idx_relation_summary_machine_id', 'machine_id'),
        Index('idx_relation_summary_match_status', 'sv_matched', 'pv_matched', 'alarm_matched'),
        {'comment': '事件关联汇总表'}
    )
