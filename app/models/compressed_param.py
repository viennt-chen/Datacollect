"""
压缩参数数据模型
用于存储压缩的 PV/SV/Alarm 等参数数据
"""
from sqlalchemy import Column, Integer, String, DateTime, BigInteger, LargeBinary, Index, Text
from datetime import datetime

from app.database import Base


class CompressedParam(Base):
    """
    压缩参数数据表
    存储压缩的 PV/SV/Alarm 等参数数据
    """
    __tablename__ = "compressed_params"
    
    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键 ID")
    
    # Topic 名称
    topic = Column(String(200), nullable=False, index=True, comment="MQTT Topic 名称")
    
    # 事件唯一标识
    event_uid = Column(String(100), index=True, comment="事件唯一标识")
    
    # 时间信息
    timestamp_ms = Column(BigInteger, nullable=False, index=True, comment="时间戳（毫秒）")
    original_timestamp = Column(BigInteger, comment="原始时间戳（毫秒）")
    
    # 压缩数据
    compressed_payload = Column(LargeBinary, nullable=False, comment="压缩的 payload 数据")
    
    # 元数据
    created_at = Column(DateTime, default=datetime.now, index=True, comment="创建时间")
    
    __table_args__ = (
        Index('idx_topic_timestamp', 'topic', 'timestamp_ms'),
        Index('idx_event_uid', 'event_uid'),
        {'comment': '压缩参数数据表'}
    )
