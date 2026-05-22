"""
MQTT Topic 配置模型
用于定义和管理 MQTT 采集主题
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from datetime import datetime

from app.database import Base


class MQTTTopicConfig(Base):
    """MQTT Topic 配置表"""
    __tablename__ = "mqtt_topic_configs"
    
    # 主键
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Topic 名称
    topic_name = Column(String(255), unique=True, nullable=False, index=True, comment='Topic 名称')
    
    # Topic 描述
    description = Column(Text, comment='Topic 描述')
    
    # Topic 类型
    # event: 加工事件（扁平化存储到 event_data 表）
    # pv_compress: PV 压缩存储（存储到 pv_compressed_params 表）
    # sv_compress: SV 压缩存储（存储到 sv_compressed_params 表）
    # alarm_compress: ALARM 压缩存储（存储到 alarm_compressed_params 表）
    # custom: 自定义存储
    topic_type = Column(String(50), nullable=False, default='custom', comment='Topic 类型')
    
    # 是否启用
    enabled = Column(Boolean, default=True, nullable=False, comment='是否启用')
    
    # QoS 级别
    qos = Column(Integer, default=1, comment='MQTT QoS 级别')
    
    # 存储策略
    # save_event: 存储到 processing_events
    # save_raw: 存储到 raw_data_blocks
    # save_both: 同时存储
    # ignore: 忽略
    storage_policy = Column(String(50), default='save_raw', comment='存储策略')
    
    # 解析规则（JSON 格式）
    # 例如：{"event_uid": "path.to.uid", "start_code": "path.to.code"}
    parse_rules = Column(Text, comment='解析规则（JSON 格式）')
    
    # 关联设备编号
    device_code = Column(String(100), comment='关联设备编号')
    
    # 创建时间
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')
    
    # 更新时间
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    
    def __repr__(self):
        return f"<MQTTTopicConfig(id={self.id}, topic_name='{self.topic_name}', enabled={self.enabled})>"
