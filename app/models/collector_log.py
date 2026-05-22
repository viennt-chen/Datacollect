"""
采集日志模型
记录 MQTT 数据采集过程中的日志信息
"""
from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from app.database import Base


class CollectorLog(Base):
    """采集日志表 - 记录采集过程中的各种事件（简化版）"""
    __tablename__ = "collector_logs"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    log_level = Column(String(20), nullable=False, comment="日志级别 (INFO/WARNING/ERROR/DEBUG)")
    log_type = Column(String(50), nullable=False, comment="日志类型 (MESSAGE_RECEIVED/DATA_STORED/DATA_TRANSFORMED/ERROR/SYSTEM)")
    topic_name = Column(String(200), comment="相关的 MQTT Topic")
    message_id = Column(String(100), comment="消息 ID")
    db_operation = Column(String(50), comment="数据库操作 (INSERT/UPDATE/DELETE)")
    table_name = Column(String(100), comment="目标表名")
    affected_rows = Column(Integer, comment="影响行数")
    error_message = Column(Text, comment="错误信息")
    execution_time_ms = Column(Integer, comment="执行时间 (毫秒)")
    summary = Column(String(500), comment="日志摘要")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    
    __table_args__ = {
        'comment': 'MQTT 采集日志表(简化版)'
    }
