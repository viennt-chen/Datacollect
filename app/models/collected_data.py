"""
动态数据表模型
用于存储根据映射定义采集的 MQTT 数据
"""
from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, Text, Index
from datetime import datetime
from app.database import Base, engine
from sqlalchemy.types import TypeDecorator


class JSONString(TypeDecorator):
    """JSON 字符串类型"""
    impl = Text
    
    def process_bind_param(self, value, dialect):
        if value is not None:
            import json
            return json.dumps(value, ensure_ascii=False)
        return value
    
    def process_result_value(self, value, dialect):
        if value is not None:
            import json
            return json.loads(value)
        return value


class CollectedData(Base):
    """采集数据动态表 - 根据映射定义存储数据"""
    __tablename__ = "collected_data"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    topic_name = Column(String(200), nullable=False, index=True, comment="MQTT Topic 名称")
    message_id = Column(String(100), index=True, comment="消息 ID")
    
    # 时间字段
    event_time = Column(DateTime, comment="事件时间")
    collect_time = Column(DateTime, default=datetime.now, comment="采集时间")
    
    # 数据字段（动态）
    data_string = Column(String(500), comment="字符串数据")
    data_float = Column(Float, comment="浮点数数据")
    data_int = Column(Integer, comment="整数数据")
    data_boolean = Column(Boolean, comment="布尔数据")
    data_json = Column(Text, comment="JSON 数据或 Protobuf 二进制数据")
    
    # 元数据
    quality = Column(String(20), default="GOOD", comment="数据质量")
    source_ip = Column(String(50), comment="来源 IP")
    
    # 索引
    __table_args__ = (
        Index('idx_topic_time', 'topic_name', 'event_time'),
        Index('idx_collect_time', 'collect_time'),
        {'comment': 'MQTT 采集数据表'}
    )


def create_dynamic_table(table_name: str, columns: dict):
    """
    创建动态数据表
    
    Args:
        table_name: 表名
        columns: 列定义字典 {column_name: column_type}
    """
    from sqlalchemy import Table, MetaData
    
    metadata = MetaData()
    
    # 创建表
    table = Table(
        table_name,
        metadata,
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('topic_name', String(200), nullable=False, index=True),
        Column('message_id', String(100), index=True),
        Column('event_time', DateTime),
        Column('collect_time', DateTime, default=datetime.now),
        *columns,
        extend_existing=True
    )
    
    # 创建表
    metadata.create_all(engine)
    
    return table
