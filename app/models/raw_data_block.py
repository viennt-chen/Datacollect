"""
原始数据块模型
用于存储压缩的 MQTT 原始数据
"""
from sqlalchemy import Column, Integer, String, BigInteger, LargeBinary, DateTime, Index
from datetime import datetime

from app.database import Base


class RawDataBlock(Base):
    """原始数据块表"""
    __tablename__ = "raw_data_blocks"
    
    # 主键
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # MQTT 主题
    topic = Column(String(255), nullable=False, index=True, comment='MQTT 主题')
    
    # 事件唯一标识
    event_uid = Column(String(255), index=True, comment='事件唯一标识')
    
    # 时间戳（毫秒）
    timestamp_ms = Column(BigInteger, nullable=False, index=True, comment='存储时间戳（毫秒）')
    
    # 原始时间戳
    original_timestamp = Column(BigInteger, index=True, comment='原始数据时间戳')
    
    # 压缩后的数据
    compressed_payload = Column(LargeBinary, comment='压缩后的 payload')
    
    # 创建时间
    created_at = Column(
        DateTime, 
        default=datetime.now, 
        comment='创建时间'
    )
    
    # 索引
    __table_args__ = (
        Index('idx_topic_timestamp', 'topic', 'timestamp_ms'),
        Index('idx_event_uid', 'event_uid'),
    )
