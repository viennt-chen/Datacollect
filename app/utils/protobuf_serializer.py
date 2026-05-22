"""
Protobuf 序列化/反序列化工具
用于将映射字段数据序列化为 Protobuf 格式存储
"""
import time
import json
import logging
from typing import Dict, Any, List, Optional
from app.proto import mqtt_data_pb2

logger = logging.getLogger(__name__)


def serialize_detail_data(
    topic: str,
    message_id: str,
    fields: List[Dict[str, Any]],
    metadata: Optional[Dict[str, str]] = None
) -> bytes:
    """
    将字段数据序列化为 Protobuf 格式
    
    Args:
        topic: MQTT Topic
        message_id: 消息 ID
        fields: 字段列表，每个字段包含:
            - field_name: 字段名
            - value: 字段值
            - timestamp: 时间戳（可选）
        metadata: 元数据（可选）
    
    Returns:
        Protobuf 序列化后的字节数据
    """
    detail_data = mqtt_data_pb2.DetailData()
    detail_data.topic = topic
    detail_data.message_id = message_id
    detail_data.timestamp = int(time.time() * 1000)
    
    for field in fields:
        field_value = mqtt_data_pb2.FieldValue()
        field_value.field_name = field.get('field_name', '')
        
        value = field.get('value')
        if value is not None:
            if isinstance(value, str):
                field_value.string_value = value
            elif isinstance(value, bool):
                field_value.bool_value = value
            elif isinstance(value, int):
                field_value.int_value = value
            elif isinstance(value, float):
                field_value.float_value = value
            elif isinstance(value, (dict, list)):
                field_value.json_value = json.dumps(value, ensure_ascii=False).encode('utf-8')
        
        if 'timestamp' in field:
            field_value.timestamp = field['timestamp']
        
        detail_data.fields.append(field_value)
    
    if metadata:
        for key, value in metadata.items():
            detail_data.metadata[key] = value
    
    return detail_data.SerializeToString()


def deserialize_detail_data(data: bytes) -> Dict[str, Any]:
    """
    将 Protobuf 格式数据反序列化为字典
    
    Args:
        data: Protobuf 序列化后的字节数据
    
    Returns:
        反序列化后的字典
    """
    detail_data = mqtt_data_pb2.DetailData()
    detail_data.ParseFromString(data)
    
    result = {
        'topic': detail_data.topic,
        'message_id': detail_data.message_id,
        'timestamp': detail_data.timestamp,
        'fields': [],
        'metadata': dict(detail_data.metadata)
    }
    
    for field in detail_data.fields:
        field_dict = {
            'field_name': field.field_name,
            'timestamp': field.timestamp
        }
        
        if field.HasField('string_value'):
            field_dict['value'] = field.string_value
        elif field.HasField('int_value'):
            field_dict['value'] = field.int_value
        elif field.HasField('float_value'):
            field_dict['value'] = field.float_value
        elif field.HasField('bool_value'):
            field_dict['value'] = field.bool_value
        elif field.HasField('json_value'):
            field_dict['value'] = json.loads(field.json_value.decode('utf-8'))
        
        result['fields'].append(field_dict)
    
    return result


def serialize_mapping_config(
    topic_name: str,
    target_table: str,
    mappings: List[Dict[str, Any]],
    version: int = 1
) -> bytes:
    """
    将映射配置序列化为 Protobuf 格式
    
    Args:
        topic_name: Topic 名称
        target_table: 目标表名
        mappings: 映射列表
        version: 版本号
    
    Returns:
        Protobuf 序列化后的字节数据
    """
    config = mqtt_data_pb2.MappingConfig()
    config.topic_name = topic_name
    config.target_table = target_table
    config.version = version
    
    for mapping in mappings:
        field_mapping = mqtt_data_pb2.FieldMapping()
        field_mapping.mqtt_field = mapping.get('mqtt_field', '')
        field_mapping.db_column = mapping.get('db_column', '')
        field_mapping.data_type = mapping.get('data_type', 'string')
        field_mapping.save_to_detail = mapping.get('save_to_detail', False)
        config.mappings.append(field_mapping)
    
    return config.SerializeToString()


def deserialize_mapping_config(data: bytes) -> Dict[str, Any]:
    """
    将 Protobuf 格式的映射配置反序列化
    
    Args:
        data: Protobuf 序列化后的字节数据
    
    Returns:
        反序列化后的字典
    """
    config = mqtt_data_pb2.MappingConfig()
    config.ParseFromString(data)
    
    result = {
        'topic_name': config.topic_name,
        'target_table': config.target_table,
        'version': config.version,
        'mappings': []
    }
    
    for mapping in config.mappings:
        result['mappings'].append({
            'mqtt_field': mapping.mqtt_field,
            'db_column': mapping.db_column,
            'data_type': mapping.data_type,
            'save_to_detail': mapping.save_to_detail
        })
    
    return result
