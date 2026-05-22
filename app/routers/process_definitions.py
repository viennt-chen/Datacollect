"""
工艺定义 API
"""
import json
import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional

from app.database import get_db

logger = logging.getLogger(__name__)
from app.models.process_definition import ProcessDefinition
from app.models.device import Device
from app.models.mqtt_topic_config import MQTTTopicConfig
from app.schemas.process_definition import (
    ProcessDefinitionCreate,
    ProcessDefinitionUpdate,
    ProcessDefinitionResponse,
    ProcessDefinitionListResponse,
)

router = APIRouter(prefix="/process-definitions", tags=["工艺管理"])

# 工艺类型 -> 编码前缀
_TYPE_PREFIX_MAP = {
    'injection': 'INJ',
    'cnc': 'CNC',
    'assembly': 'ASM',
    'inspection': 'INS',
    'other': 'P',
}


def _parse_json_field(value, default=None):
    if value is None:
        return default if default is not None else []
    if isinstance(value, (list, dict)):
        return value
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return default if default is not None else []


def _to_response(proc: ProcessDefinition, db: Session = None) -> ProcessDefinitionResponse:
    data = {
        "id": proc.id,
        "process_code": proc.process_code,
        "process_name": proc.process_name,
        "description": proc.description,
        "process_type": proc.process_type,
        "device_codes": _parse_json_field(proc.device_codes, []),
        "mqtt_topic_ids": _parse_json_field(proc.mqtt_topic_ids, []),
        "product_codes": _parse_json_field(proc.product_codes, []),
        "parameters": _parse_json_field(proc.parameters, {}),
        "status": proc.status,
        "created_at": proc.created_at,
        "updated_at": proc.updated_at,
        "created_by": proc.created_by,
        "updated_by": proc.updated_by,
    }

    if db:
        device_codes = data["device_codes"]
        if device_codes:
            devices = db.query(Device).filter(Device.device_code.in_(device_codes)).all()
            data["devices"] = [
                {"device_code": d.device_code, "device_name": d.device_name, "device_type": d.device_type, "status": d.status}
                for d in devices
            ]
        else:
            data["devices"] = []

        topic_ids = data["mqtt_topic_ids"]
        if topic_ids:
            topics = db.query(MQTTTopicConfig).filter(MQTTTopicConfig.id.in_(topic_ids)).all()
            data["topics"] = [
                {"id": t.id, "topic_name": t.topic_name, "topic_type": t.topic_type, "enabled": t.enabled}
                for t in topics
            ]
        else:
            data["topics"] = []

    return ProcessDefinitionResponse(**data)


@router.get("/", response_model=ProcessDefinitionListResponse)
def list_process_definitions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: Optional[str] = None,
    process_type: Optional[str] = None,
    status: Optional[str] = None,
    param_field: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(ProcessDefinition)

    if keyword:
        query = query.filter(
            or_(
                ProcessDefinition.process_code.contains(keyword),
                ProcessDefinition.process_name.contains(keyword),
                ProcessDefinition.description.contains(keyword),
            )
        )
    if process_type:
        query = query.filter(ProcessDefinition.process_type == process_type)
    if status:
        query = query.filter(ProcessDefinition.status == status)
    if param_field:
        query = query.filter(ProcessDefinition.parameters.contains(f'"{param_field}"'))

    total = query.count()
    items = query.order_by(ProcessDefinition.id.desc()).offset((page - 1) * page_size).limit(page_size).all()

    responses = [_to_response(item) for item in items]
    if responses:
        logger.info(f"工艺列表第一条: product_codes={responses[0].product_codes}")
    return ProcessDefinitionListResponse(
        total=total,
        items=responses,
    )


@router.get("/stats/summary")
def get_stats(db: Session = Depends(get_db)):
    total = db.query(ProcessDefinition).count()
    active = db.query(ProcessDefinition).filter(ProcessDefinition.status == 'active').count()
    all_procs = db.query(ProcessDefinition).all()
    device_set = set()
    topic_set = set()
    product_set = set()
    for p in all_procs:
        for dc in _parse_json_field(p.device_codes, []):
            device_set.add(dc)
        for tid in _parse_json_field(p.mqtt_topic_ids, []):
            topic_set.add(tid)
        for pc in _parse_json_field(p.product_codes, []):
            product_set.add(pc)
    return {"total": total, "active": active, "device_count": len(device_set), "topic_count": len(topic_set), "product_count": len(product_set)}


@router.get("/next-code")
def get_next_code(
    process_type: str = Query('other'),
    db: Session = Depends(get_db),
):
    prefix = _TYPE_PREFIX_MAP.get(process_type, 'P')
    # 查询该前缀下最大的编码序号
    pattern = f"{prefix}-%"
    rows = db.query(ProcessDefinition.process_code).filter(
        ProcessDefinition.process_code.like(pattern)
    ).all()

    max_seq = 0
    for (code,) in rows:
        parts = code.split('-')
        if len(parts) >= 2:
            try:
                seq = int(parts[-1])
                if seq > max_seq:
                    max_seq = seq
            except ValueError:
                continue

    next_code = f"{prefix}-{max_seq + 1:03d}"
    return {"code": next_code}


@router.get("/{process_id}", response_model=ProcessDefinitionResponse)
def get_process_definition(process_id: int, db: Session = Depends(get_db)):
    proc = db.query(ProcessDefinition).filter(ProcessDefinition.id == process_id).first()
    if not proc:
        raise HTTPException(status_code=404, detail="工艺定义不存在")
    return _to_response(proc, db)


@router.post("/", response_model=ProcessDefinitionResponse)
def create_process_definition(data: ProcessDefinitionCreate, db: Session = Depends(get_db)):
    existing = db.query(ProcessDefinition).filter(ProcessDefinition.process_code == data.process_code).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"工艺编码 {data.process_code} 已存在")

    logger.info(f"创建工艺: product_codes={data.product_codes}")
    proc = ProcessDefinition(
        process_code=data.process_code,
        process_name=data.process_name,
        description=data.description,
        process_type=data.process_type,
        device_codes=json.dumps(data.device_codes or []),
        mqtt_topic_ids=json.dumps(data.mqtt_topic_ids or []),
        product_codes=json.dumps(data.product_codes or []),
        parameters=json.dumps(data.parameters or {}),
        status=data.status,
        created_by=data.created_by,
        updated_by=data.updated_by,
    )
    db.add(proc)
    db.commit()
    db.refresh(proc)
    logger.info(f"创建工艺成功: id={proc.id}, product_codes列值={proc.product_codes}")
    return _to_response(proc, db)


@router.put("/{process_id}", response_model=ProcessDefinitionResponse)
def update_process_definition(process_id: int, data: ProcessDefinitionUpdate, db: Session = Depends(get_db)):
    proc = db.query(ProcessDefinition).filter(ProcessDefinition.id == process_id).first()
    if not proc:
        raise HTTPException(status_code=404, detail="工艺定义不存在")

    update_data = data.model_dump(exclude_unset=True)
    logger.info(f"更新工艺 id={process_id}: 收到字段={list(update_data.keys())}, product_codes={update_data.get('product_codes')}")

    if "process_code" in update_data and update_data["process_code"] != proc.process_code:
        existing = db.query(ProcessDefinition).filter(ProcessDefinition.process_code == update_data["process_code"]).first()
        if existing:
            raise HTTPException(status_code=400, detail=f"工艺编码 {update_data['process_code']} 已存在")

    for field, value in update_data.items():
        if field in ("device_codes", "mqtt_topic_ids", "product_codes", "parameters"):
            setattr(proc, field, json.dumps(value) if value is not None else None)
        else:
            setattr(proc, field, value)

    db.commit()
    db.refresh(proc)
    logger.info(f"更新工艺成功: id={proc.id}, product_codes列值={proc.product_codes}")
    return _to_response(proc, db)


@router.delete("/{process_id}")
def delete_process_definition(process_id: int, db: Session = Depends(get_db)):
    proc = db.query(ProcessDefinition).filter(ProcessDefinition.id == process_id).first()
    if not proc:
        raise HTTPException(status_code=404, detail="工艺定义不存在")
    db.delete(proc)
    db.commit()
    return {"message": "删除成功"}


@router.get("/{process_id}/devices")
def get_process_devices(process_id: int, db: Session = Depends(get_db)):
    proc = db.query(ProcessDefinition).filter(ProcessDefinition.id == process_id).first()
    if not proc:
        raise HTTPException(status_code=404, detail="工艺定义不存在")

    device_codes = _parse_json_field(proc.device_codes, [])
    if not device_codes:
        return []

    devices = db.query(Device).filter(Device.device_code.in_(device_codes)).all()
    return [
        {
            "device_code": d.device_code,
            "device_name": d.device_name,
            "device_type": d.device_type,
            "model": d.model,
            "manufacturer": d.manufacturer,
            "status": d.status,
            "is_enabled": d.is_enabled,
        }
        for d in devices
    ]


@router.get("/{process_id}/topics")
def get_process_topics(process_id: int, db: Session = Depends(get_db)):
    proc = db.query(ProcessDefinition).filter(ProcessDefinition.id == process_id).first()
    if not proc:
        raise HTTPException(status_code=404, detail="工艺定义不存在")

    topic_ids = _parse_json_field(proc.mqtt_topic_ids, [])
    if not topic_ids:
        return []

    topics = db.query(MQTTTopicConfig).filter(MQTTTopicConfig.id.in_(topic_ids)).all()
    return [
        {
            "id": t.id,
            "topic_name": t.topic_name,
            "topic_type": t.topic_type,
            "enabled": t.enabled,
            "qos": t.qos,
            "storage_policy": t.storage_policy,
        }
        for t in topics
    ]


@router.get("/{process_id}/live-params")
def get_live_params(process_id: int, db: Session = Depends(get_db)):
    """获取工艺定义的实时参数值（由参数同步服务维护）"""
    proc = db.query(ProcessDefinition).filter(ProcessDefinition.id == process_id).first()
    if not proc:
        raise HTTPException(status_code=404, detail="工艺定义不存在")

    from app.services.process_param_sync import get_sync_service
    service = get_sync_service()
    live = service.get_live_params(process_id)

    if live:
        return live

    # 若无实时数据，返回当前 DB 中的参数
    parameters = _parse_json_field(proc.parameters, {})
    return {
        "process_id": proc.id,
        "process_code": proc.process_code,
        "parameters": parameters,
        "last_source": None,
        "last_sync_time": None,
    }
