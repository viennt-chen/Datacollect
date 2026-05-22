"""
当前加工物料配置 API 路由
功能：管理从MQTT topic获取当前加工物料零件号的配置
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from typing import Optional, List
import json
import logging

from app.database import get_db
from app.models.current_product_config import CurrentProductConfig
from app.models.device import Device
from app.schemas.current_product_config import (
    CurrentProductConfigCreate,
    CurrentProductConfigUpdate,
    CurrentProductConfigDetail,
    CurrentProductConfigList,
    ConfigTestResult,
    BatchToggleRequest,
    BatchToggleResult,
    TopicFieldInfo,
)
from app.services.product_resolver import test_config, get_nested_value
from app.services.mqtt_collector import get_collector

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/devices/current-product-configs", tags=["当前加工产品配置"])


@router.get("/device/{device_code}", response_model=CurrentProductConfigList)
async def get_device_current_product_configs(
    device_code: str,
    enabled: Optional[bool] = Query(None, description="是否启用"),
    db: Session = Depends(get_db)
):
    """获取设备的当前加工产品配置列表"""
    device = db.query(Device).filter(Device.device_code == device_code).first()
    if not device:
        raise HTTPException(status_code=404, detail="设备不存在")

    query = db.query(CurrentProductConfig).filter(
        CurrentProductConfig.device_code == device_code
    )

    if enabled is not None:
        query = query.filter(CurrentProductConfig.enabled == enabled)

    configs = query.order_by(CurrentProductConfig.priority).all()

    return CurrentProductConfigList(total=len(configs), items=configs)


@router.get("/device/{device_code}/topics", response_model=List[TopicFieldInfo])
async def get_device_available_topics(
    device_code: str,
    db: Session = Depends(get_db)
):
    """获取设备关联的 MQTT Topic 列表及其可用字段"""
    device = db.query(Device).filter(Device.device_code == device_code).first()
    if not device:
        raise HTTPException(status_code=404, detail="设备不存在")

    # 获取设备关联的 topic 列表
    topics = []
    if device.mqtt_topics:
        try:
            topics = json.loads(device.mqtt_topics) if isinstance(device.mqtt_topics, str) else device.mqtt_topics
        except (json.JSONDecodeError, TypeError):
            topics = []

    # 从 MQTT 缓冲区获取每个 topic 的字段信息
    mqtt_collector = get_collector()
    mqtt_buffer = mqtt_collector.data_buffer if mqtt_collector else []

    result = []
    for topic_name in topics:
        fields = []
        sample_message = None

        # 从缓冲区找最新消息
        for msg in reversed(mqtt_buffer):
            if msg.get('topic') == topic_name:
                payload = msg.get('payload', {})
                sample_message = payload
                fields = _extract_fields_from_payload(payload)
                break

        result.append(TopicFieldInfo(
            topic_name=topic_name,
            fields=fields,
            sample_message=sample_message,
        ))

    return result


def _extract_fields_from_payload(payload: dict, prefix: str = "", max_depth: int = 3) -> List[dict]:
    """递归提取 payload 中的字段路径和示例值"""
    fields = []
    if max_depth <= 0 or not isinstance(payload, dict):
        return fields

    for key, value in payload.items():
        full_path = f"{prefix}.{key}" if prefix else key
        if isinstance(value, dict):
            fields.append({
                "path": full_path,
                "type": "object",
                "sample": "{...}",
                "children_count": len(value),
            })
            fields.extend(_extract_fields_from_payload(value, full_path, max_depth - 1))
        else:
            fields.append({
                "path": full_path,
                "type": type(value).__name__,
                "sample": str(value)[:100] if value is not None else None,
            })

    return fields


@router.post("/", response_model=CurrentProductConfigDetail)
async def create_current_product_config(
    config: CurrentProductConfigCreate,
    db: Session = Depends(get_db)
):
    """创建当前加工产品配置"""
    device = db.query(Device).filter(Device.device_code == config.device_code).first()
    if not device:
        raise HTTPException(status_code=404, detail="设备不存在")

    db_config = CurrentProductConfig(
        device_code=config.device_code,
        topic_name=config.topic_name,
        field_path=config.field_path,
        field_description=config.field_description,
        extraction_rule=config.extraction_rule,
        enabled=config.enabled,
        priority=config.priority,
        description=config.description
    )

    db.add(db_config)
    db.commit()
    db.refresh(db_config)

    return db_config


@router.put("/{config_id}", response_model=CurrentProductConfigDetail)
async def update_current_product_config(
    config_id: int,
    config: CurrentProductConfigUpdate,
    db: Session = Depends(get_db)
):
    """更新当前加工产品配置"""
    db_config = db.query(CurrentProductConfig).filter(
        CurrentProductConfig.id == config_id
    ).first()

    if not db_config:
        raise HTTPException(status_code=404, detail="配置不存在")

    update_data = config.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_config, key, value)

    db.commit()
    db.refresh(db_config)

    return db_config


@router.delete("/{config_id}")
async def delete_current_product_config(
    config_id: int,
    db: Session = Depends(get_db)
):
    """删除当前加工产品配置"""
    db_config = db.query(CurrentProductConfig).filter(
        CurrentProductConfig.id == config_id
    ).first()

    if not db_config:
        raise HTTPException(status_code=404, detail="配置不存在")

    db.delete(db_config)
    db.commit()

    return {"message": "删除成功"}


@router.post("/{config_id}/toggle")
async def toggle_current_product_config(
    config_id: int,
    db: Session = Depends(get_db)
):
    """切换配置启用状态"""
    db_config = db.query(CurrentProductConfig).filter(
        CurrentProductConfig.id == config_id
    ).first()

    if not db_config:
        raise HTTPException(status_code=404, detail="配置不存在")

    db_config.enabled = not db_config.enabled
    db.commit()
    db.refresh(db_config)

    return {
        "message": f"配置已{'启用' if db_config.enabled else '禁用'}",
        "enabled": db_config.enabled
    }


@router.post("/batch/toggle", response_model=BatchToggleResult)
async def batch_toggle_configs(
    req: BatchToggleRequest,
    db: Session = Depends(get_db)
):
    """批量切换配置启用状态"""
    configs = db.query(CurrentProductConfig).filter(
        CurrentProductConfig.id.in_(req.config_ids)
    ).all()

    if not configs:
        raise HTTPException(status_code=404, detail="未找到指定配置")

    for config in configs:
        config.enabled = req.enabled

    db.commit()

    return BatchToggleResult(updated=len(configs), enabled=req.enabled)


@router.post("/{config_id}/test", response_model=ConfigTestResult)
async def test_current_product_config(
    config_id: int,
    db: Session = Depends(get_db)
):
    """测试配置规则，返回解析结果（使用最新的 MQTT 消息）"""
    db_config = db.query(CurrentProductConfig).filter(
        CurrentProductConfig.id == config_id
    ).first()

    if not db_config:
        raise HTTPException(status_code=404, detail="配置不存在")

    mqtt_collector = get_collector()
    mqtt_buffer = mqtt_collector.data_buffer if mqtt_collector else []

    result = test_config(db, db_config, mqtt_buffer)
    return ConfigTestResult(**result)


@router.get("/stats/summary")
async def get_config_stats(
    device_code: Optional[str] = Query(None, description="设备编号"),
    db: Session = Depends(get_db)
):
    """获取配置统计信息"""
    query = db.query(CurrentProductConfig)
    if device_code:
        query = query.filter(CurrentProductConfig.device_code == device_code)

    all_configs = query.all()
    total = len(all_configs)
    enabled = sum(1 for c in all_configs if c.enabled)
    disabled = total - enabled

    # 按设备分组
    device_counts = {}
    for c in all_configs:
        device_counts[c.device_code] = device_counts.get(c.device_code, 0) + 1

    return {
        "total": total,
        "enabled": enabled,
        "disabled": disabled,
        "device_count": len(device_counts),
        "configs_per_device": device_counts,
    }
