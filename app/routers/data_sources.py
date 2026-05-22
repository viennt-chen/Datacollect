"""
数据源配置管理 API 路由
功能：管理设备数据源配置，包括MQTT和数据库的切换
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
import json

from app.database import get_db
from app.models.device import Device
from app.models.mqtt_topic_config import MQTTTopicConfig
from app.services.device_data_collector import get_device_data_collector

router = APIRouter(prefix="/data-sources", tags=["数据源配置管理"])


@router.get("/{device_code}/config")
async def get_device_data_source_config(
    device_code: str,
    db: Session = Depends(get_db)
):
    """
    获取设备数据源配置

    Args:
        device_code: 设备编号

    Returns:
        数据源配置信息
    """
    device = db.query(Device).filter(Device.device_code == device_code).first()
    if not device:
        raise HTTPException(status_code=404, detail="设备不存在")
    
    # 获取设备的Topic配置
    mqtt_topics = []
    if device.mqtt_topics:
        try:
            mqtt_topics = json.loads(device.mqtt_topics)
        except (json.JSONDecodeError, TypeError):
            mqtt_topics = []
    
    topic_configs = db.query(MQTTTopicConfig).filter(
        MQTTTopicConfig.topic_name.in_(mqtt_topics)
    ).all() if mqtt_topics else []
    
    # 构建配置信息
    config = {
        "device_code": device.device_code,
        "device_name": device.device_name,
        "data_source_config": {
            "primary_source": "mqtt",  # 默认主数据源为MQTT
            "fallback_source": "database",  # 默认备用数据源为数据库
            "auto_switch": True,  # 是否自动切换
            "mqtt_timeout": 5,  # MQTT超时时间（秒）
            "cache_enabled": True,  # 是否启用缓存
            "cache_ttl": 60  # 缓存有效期（秒）
        },
        "topics": [
            {
                "topic_name": config.topic_name,
                "topic_type": config.topic_type,
                "enabled": config.enabled,
                "description": config.description
            }
            for config in topic_configs
        ]
    }
    
    return config


@router.put("/{device_code}/config")
async def update_device_data_source_config(
    device_code: str,
    config: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """
    更新设备数据源配置

    Args:
        device_code: 设备编号
        config: 配置信息

    Returns:
        更新后的配置
    """
    device = db.query(Device).filter(Device.device_code == device_code).first()
    if not device:
        raise HTTPException(status_code=404, detail="设备不存在")
    
    # 这里可以将配置存储到数据库或配置文件
    # 目前仅返回配置信息
    
    return {
        "message": "配置更新成功",
        "device_code": device_code,
        "config": config
    }


@router.get("/{device_code}/topics/{topic_name}/data")
async def get_topic_data(
    device_code: str,
    topic_name: str,
    source: str = Query("auto", description="数据源：auto/mqtt/database"),
    db: Session = Depends(get_db)
):
    """
    获取指定Topic的数据

    Args:
        device_code: 设备编号
        topic_name: Topic名称
        source: 数据源类型

    Returns:
        Topic数据
    """
    device = db.query(Device).filter(Device.device_code == device_code).first()
    if not device:
        raise HTTPException(status_code=404, detail="设备不存在")
    
    collector = get_device_data_collector()
    
    if source == "mqtt":
        data = collector.get_realtime_data_from_mqtt(device_code, topic_name)
        if not data:
            raise HTTPException(status_code=404, detail="MQTT实时数据不可用")
        return data

    elif source == "database":
        data = collector.get_latest_data_from_db(device_code, topic_name, db)
        if not data:
            raise HTTPException(status_code=404, detail="数据库无数据")
        return data

    else:  # auto
        # 优先尝试MQTT
        data = collector.get_realtime_data_from_mqtt(device_code, topic_name)
        if data:
            return data

        # 降级到数据库
        data = collector.get_latest_data_from_db(device_code, topic_name, db)
        if data:
            return data

        raise HTTPException(status_code=404, detail="无可用数据")
