"""
MQTT Topic 字段提取工具
从 parse_rules 或 MQTT 消息缓冲区中提取可用字段
"""
import json
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def flatten_object(obj: Any, prefix: str = '') -> List[Dict[str, Any]]:
    """递归提取 JSON 对象中的所有叶子字段路径"""
    fields = []
    if isinstance(obj, dict):
        for key, value in obj.items():
            full_key = f"{prefix}.{key}" if prefix else key
            if isinstance(value, dict):
                fields.extend(flatten_object(value, full_key))
            else:
                fields.append({
                    "field_path": full_key,
                    "field_value": value,
                    "field_type": type(value).__name__
                })
    return fields


def get_latest_message_for_topic(data_buffer: list, topic_name: str) -> Optional[Dict[str, Any]]:
    """从 MQTT 缓冲区中查找指定 topic 的最新消息"""
    for message in reversed(data_buffer):
        if message.get('topic') == topic_name:
            return message
    return None


def extract_fields_from_parse_rules(parse_rules_json) -> List[Dict[str, Any]]:
    """
    从 parse_rules JSON 中提取字段列表
    parse_rules 格式: {"key_name": {"label": "...", "path": "nested.path", "type": "string|number", "unit": "..."}}
    """
    if not parse_rules_json:
        return []

    try:
        if isinstance(parse_rules_json, str):
            rules = json.loads(parse_rules_json)
        else:
            rules = parse_rules_json
    except (json.JSONDecodeError, TypeError):
        return []

    if not isinstance(rules, dict):
        return []

    fields = []
    for key_name, conf in rules.items():
        if not isinstance(conf, dict):
            continue
        fields.append({
            "name": key_name,
            "path": conf.get("path", key_name),
            "type": conf.get("type", "string"),
            "unit": conf.get("unit", ""),
            "sample_value": None,
            "label": conf.get("label", key_name),
        })
    return fields


def extract_fields_from_buffer(data_buffer: list, topic_name: str) -> List[Dict[str, Any]]:
    """从 MQTT 消息缓冲区中提取指定 topic 的字段列表"""
    message = get_latest_message_for_topic(data_buffer, topic_name)
    if not message:
        return []

    payload = message.get('payload')
    if not isinstance(payload, dict):
        return []

    raw_fields = flatten_object(payload)
    fields = []
    for f in raw_fields:
        path = f["field_path"]
        name = path.split(".")[-1] if "." in path else path
        fields.append({
            "name": name,
            "path": path,
            "type": f["field_type"],
            "unit": "",
            "sample_value": f["field_value"],
            "label": name,
        })
    return fields
