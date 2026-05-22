"""
MQTT Topic 配置管理 API 路由
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List
import json

from app.database import get_db, SessionLocal
from app.models.mqtt_topic_config import MQTTTopicConfig
from app.models.device import Device
from app.schemas.mqtt_topic_config import (
    MQTTTopicConfigCreate, MQTTTopicConfigUpdate,
    MQTTTopicConfigDetail, MQTTTopicConfigList,
    TopicFieldsResponse, TopicFieldsResult, TopicFieldItem
)

router = APIRouter(tags=["MQTT Topic 配置"])


@router.get("/", response_model=MQTTTopicConfigList)
async def list_topic_configs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    enabled: Optional[bool] = None,
    topic_type: Optional[str] = None,
    device_code: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    查询 Topic 配置列表
    
    Args:
        page: 页码
        page_size: 每页数量
        enabled: 是否启用筛选
        topic_type: Topic 类型筛选
        device_code: 设备编号筛选
    """
    query = db.query(MQTTTopicConfig)
    
    # 筛选条件
    if enabled is not None:
        query = query.filter(MQTTTopicConfig.enabled == enabled)
    if topic_type:
        query = query.filter(MQTTTopicConfig.topic_type == topic_type)
    if device_code is not None:
        query = query.filter(MQTTTopicConfig.device_code == device_code)
    
    # 总数
    total = query.count()
    
    # 分页
    offset = (page - 1) * page_size
    items = query.order_by(MQTTTopicConfig.created_at.desc()).offset(offset).limit(page_size).all()
    
    # 为每个 Topic 配置添加设备编号信息
    enriched_items = []
    for item in items:
        item_dict = {
            c.name: getattr(item, c.name) for c in item.__table__.columns
        }
        
        # 如果有关联设备，查询设备编号
        if item.device_code:
            device = db.query(Device).filter(Device.device_code == item.device_code).first()
            if device:
                item_dict['device_code'] = device.device_code
                item_dict['device_name'] = device.device_name
            else:
                item_dict['device_code'] = None
                item_dict['device_name'] = None
        else:
            item_dict['device_code'] = None
            item_dict['device_name'] = None
        
        enriched_items.append(item_dict)
    
    return MQTTTopicConfigList(total=total, items=enriched_items)


@router.post("/", response_model=MQTTTopicConfigDetail)
async def create_topic_config(
    config: MQTTTopicConfigCreate,
    db: Session = Depends(get_db)
):
    """
    创建新的 Topic 配置
    
    Args:
        config: Topic 配置信息
    """
    # 检查是否已存在
    existing = db.query(MQTTTopicConfig).filter(
        MQTTTopicConfig.topic_name == config.topic_name
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Topic '{config.topic_name}' 已存在"
        )
    
    # 创建配置
    db_config = MQTTTopicConfig(
        topic_name=config.topic_name,
        description=config.description,
        topic_type=config.topic_type,
        enabled=config.enabled,
        qos=config.qos,
        storage_policy=config.storage_policy,
        parse_rules=json.dumps(config.parse_rules) if config.parse_rules else None,
        device_code=config.device_code
    )

    db.add(db_config)
    db.commit()
    db.refresh(db_config)

    # 同步更新设备的 mqtt_topics
    if config.device_code:
        device = db.query(Device).filter(Device.device_code == config.device_code).first()
        if device:
            try:
                topics = json.loads(device.mqtt_topics) if device.mqtt_topics else []
                if config.topic_name not in topics:
                    topics.append(config.topic_name)
                    device.mqtt_topics = json.dumps(topics)
                    db.commit()
            except (json.JSONDecodeError, TypeError):
                device.mqtt_topics = json.dumps([config.topic_name])
                db.commit()
    
    return db_config


@router.get("/fields", response_model=TopicFieldsResponse)
async def get_topic_fields(
    topic_ids: List[int] = Query(..., description="Topic ID 列表"),
    db: Session = Depends(get_db)
):
    """
    获取指定 Topic 的可用字段列表

    优先从 parse_rules 中读取，若无则从 MQTT 消息缓冲区动态提取。
    """
    from app.utils.field_extractor import (
        extract_fields_from_parse_rules, extract_fields_from_buffer
    )
    from app.services.mqtt_collector import get_collector

    topic_configs = db.query(MQTTTopicConfig).filter(
        MQTTTopicConfig.id.in_(topic_ids)
    ).all()

    config_map = {c.id: c for c in topic_configs}

    mqtt_collector = get_collector()
    mqtt_buffer = mqtt_collector.data_buffer if mqtt_collector else []

    results = []
    for tid in topic_ids:
        config = config_map.get(tid)
        if not config:
            results.append(TopicFieldsResult(
                topic_id=tid, topic_name="unknown", source="none", fields=[]
            ))
            continue

        # Priority 1: parse_rules
        fields = extract_fields_from_parse_rules(config.parse_rules)
        if fields:
            results.append(TopicFieldsResult(
                topic_id=tid,
                topic_name=config.topic_name,
                source="parse_rules",
                fields=[TopicFieldItem(**f) for f in fields]
            ))
            continue

        # Priority 2: MQTT buffer
        fields = extract_fields_from_buffer(mqtt_buffer, config.topic_name)
        if fields:
            results.append(TopicFieldsResult(
                topic_id=tid,
                topic_name=config.topic_name,
                source="mqtt_buffer",
                fields=[TopicFieldItem(**f) for f in fields]
            ))
            continue

        # No fields found
        results.append(TopicFieldsResult(
            topic_id=tid,
            topic_name=config.topic_name,
            source="none",
            fields=[]
        ))

    return TopicFieldsResponse(topics=results)


@router.get("/{config_id}", response_model=MQTTTopicConfigDetail)
async def get_topic_config(
    config_id: int,
    db: Session = Depends(get_db)
):
    """获取 Topic 配置详情"""
    config = db.query(MQTTTopicConfig).filter(
        MQTTTopicConfig.id == config_id
    ).first()
    
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")
    
    return config


@router.put("/{config_id}", response_model=MQTTTopicConfigDetail)
async def update_topic_config(
    config_id: int,
    update_data: MQTTTopicConfigUpdate,
    db: Session = Depends(get_db)
):
    """
    更新 Topic 配置
    
    Args:
        config_id: 配置 ID
        update_data: 更新数据
    """
    config = db.query(MQTTTopicConfig).filter(
        MQTTTopicConfig.id == config_id
    ).first()
    
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")
    
    # 记录旧的 device_code
    old_device_code = config.device_code
    
    # 更新字段
    update_dict = update_data.model_dump(exclude_unset=True)
    
    # 特殊处理 parse_rules
    if 'parse_rules' in update_dict and update_dict['parse_rules'] is not None:
        update_dict['parse_rules'] = json.dumps(update_dict['parse_rules'])
    
    # 特殊处理 device_code：需要支持设置为 null
    if 'device_code' not in update_dict and hasattr(update_data, 'device_code'):
        update_dict['device_code'] = update_data.device_code
    
    for field, value in update_dict.items():
        setattr(config, field, value)
    
    db.commit()
    db.refresh(config)
    
    # 同步更新设备的 mqtt_topics
    new_device_code = update_dict.get('device_code', config.device_code)
    if old_device_code != new_device_code:
        # 从旧设备中移除该 topic
        if old_device_code:
            old_device = db.query(Device).filter(Device.device_code == old_device_code).first()
            if old_device and old_device.mqtt_topics:
                try:
                    topics = json.loads(old_device.mqtt_topics)
                    if config.topic_name in topics:
                        topics.remove(config.topic_name)
                        old_device.mqtt_topics = json.dumps(topics)
                except (json.JSONDecodeError, TypeError):
                    pass

        # 向新设备中添加该 topic
        if new_device_code:
            new_device = db.query(Device).filter(Device.device_code == new_device_code).first()
            if new_device:
                try:
                    topics = json.loads(new_device.mqtt_topics) if new_device.mqtt_topics else []
                    if config.topic_name not in topics:
                        topics.append(config.topic_name)
                        new_device.mqtt_topics = json.dumps(topics)
                except (json.JSONDecodeError, TypeError):
                    new_device.mqtt_topics = json.dumps([config.topic_name])
        
        db.commit()
    
    return config


@router.delete("/{config_id}")
async def delete_topic_config(
    config_id: int,
    db: Session = Depends(get_db)
):
    """删除 Topic 配置"""
    config = db.query(MQTTTopicConfig).filter(
        MQTTTopicConfig.id == config_id
    ).first()
    
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")
    
    # 同步更新设备的 mqtt_topics：从设备中移除该 topic
    if config.device_code:
        device = db.query(Device).filter(Device.device_code == config.device_code).first()
        if device and device.mqtt_topics:
            try:
                topics = json.loads(device.mqtt_topics)
                if config.topic_name in topics:
                    topics.remove(config.topic_name)
                    device.mqtt_topics = json.dumps(topics)
            except (json.JSONDecodeError, TypeError):
                pass
    
    db.delete(config)
    db.commit()
    
    return {"message": "删除成功"}


@router.post("/{config_id}/toggle")
async def toggle_topic_config(
    config_id: int,
    db: Session = Depends(get_db)
):
    """切换 Topic 启用状态"""
    config = db.query(MQTTTopicConfig).filter(
        MQTTTopicConfig.id == config_id
    ).first()
    
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")
    
    config.enabled = not config.enabled
    db.commit()
    db.refresh(config)
    
    return {
        "message": f"Topic 已{'启用' if config.enabled else '禁用'}",
        "enabled": config.enabled
    }


@router.get("/stats/summary", response_model=dict)
async def get_topic_stats_summary(
    db: Session = Depends(get_db)
):
    """
    获取 Topic 配置统计摘要
    
    Returns:
        统计信息，包括总数、启用数、禁用数、类型分布等
    """
    # 总数统计
    total = db.query(MQTTTopicConfig).count()
    enabled_count = db.query(MQTTTopicConfig).filter(
        MQTTTopicConfig.enabled == True
    ).count()
    disabled_count = total - enabled_count
    
    # 类型分布
    type_distribution = db.query(
        MQTTTopicConfig.topic_type,
        func.count(MQTTTopicConfig.id).label('count')
    ).group_by(MQTTTopicConfig.topic_type).all()
    
    # 存储策略分布
    storage_distribution = db.query(
        MQTTTopicConfig.storage_policy,
        func.count(MQTTTopicConfig.id).label('count')
    ).group_by(MQTTTopicConfig.storage_policy).all()
    
    # 最近创建的 Topic
    recent_topics = db.query(MQTTTopicConfig).order_by(
        MQTTTopicConfig.created_at.desc()
    ).limit(5).all()
    
    return {
        "total": total,
        "enabled": enabled_count,
        "disabled": disabled_count,
        "type_distribution": [
            {"type": item.topic_type, "count": item.count}
            for item in type_distribution
        ],
        "storage_distribution": [
            {"policy": item.storage_policy, "count": item.count}
            for item in storage_distribution
        ],
        "recent_topics": [
            {
                "id": topic.id,
                "topic_name": topic.topic_name,
                "topic_type": topic.topic_type,
                "enabled": topic.enabled,
                "created_at": topic.created_at.isoformat() if topic.created_at else None
            }
            for topic in recent_topics
        ]
    }


@router.post("/batch/delete")
async def batch_delete_topics(
    config_ids: List[int],
    db: Session = Depends(get_db)
):
    """
    批量删除 Topic 配置
    
    Args:
        config_ids: 配置 ID 列表
    """
    deleted_count = db.query(MQTTTopicConfig).filter(
        MQTTTopicConfig.id.in_(config_ids)
    ).delete(synchronize_session=False)
    
    db.commit()
    
    return {
        "message": f"成功删除 {deleted_count} 条配置",
        "deleted_count": deleted_count
    }


@router.post("/batch/toggle")
async def batch_toggle_topics(
    config_ids: List[int],
    enabled: bool,
    db: Session = Depends(get_db)
):
    """
    批量切换 Topic 启用状态
    
    Args:
        config_ids: 配置 ID 列表
        enabled: 目标状态
    """
    db.query(MQTTTopicConfig).filter(
        MQTTTopicConfig.id.in_(config_ids)
    ).update({
        MQTTTopicConfig.enabled: enabled
    }, synchronize_session=False)
    
    db.commit()
    
    return {
        "message": f"成功{'启用' if enabled else '禁用'} {len(config_ids)} 条配置",
        "enabled": enabled,
        "count": len(config_ids)
    }


