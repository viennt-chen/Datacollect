"""
产品加工信息关联查询 API
功能：统一的跨模块关联查询接口，以 event_data 为中心枢纽
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import Optional
from datetime import datetime

from app.database import get_db
from app.models.event_data import EventData
from app.models.device import Device
from app.models.material import Material
from app.models.alarm_record import AlarmRecord
from app.models.process_definition import ProcessDefinition
from app.models.process_params import ProcessParameter
from app.models.product_order import ProductOrder
from app.models.order_processing_record import OrderProcessingRecord
from app.models.production_flow_instance import ProductionFlowInstance
from app.models.quality_record import QualityRecord
from app.models.event_relations import (
    EventSVRelation, EventPVRelation, EventAlarmRelation, EventDataRelationSummary
)

router = APIRouter(prefix="/event-associations", tags=["事件关联查询"])


def _get_event_or_404(event_id: int, db: Session) -> EventData:
    """获取事件或抛出 404"""
    event = db.query(EventData).filter(EventData.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="加工事件不存在")
    return event


def _device_to_dict(device: Device) -> dict:
    return {
        "device_code": device.device_code,
        "device_name": device.device_name,
        "device_type": device.device_type,
        "model": device.model,
        "manufacturer": device.manufacturer,
        "line_code": device.line_code,
        "factory_code": device.factory_code,
        "group_code": device.group_code,
        "status": device.status,
        "location": device.location,
        "ip_address": device.ip_address,
    }


def _event_to_dict(event: EventData) -> dict:
    return {
        "id": event.id,
        "event_uid": event.event_uid,
        "start_code": event.start_code,
        "skin_code": event.skin_code,
        "start_time": event.start_time,
        "end_time": event.end_time,
        "duringtime": event.duringtime,
        "machine_duringtime": event.machine_duringtime,
        "machine_id": event.machine_id,
        "operator_id": event.operator_id,
        "operator_name": event.operator_name,
        "group_code": event.group_code,
        "group_name": event.group_name,
        "factory_code": event.factory_code,
        "factory_name": event.factory_name,
        "line_code": event.line_code,
        "process_no": event.process_no,
        "created_at": str(event.created_at) if event.created_at else None,
    }


# ============================================================
# 正向关联：从加工事件查其他模块
# ============================================================

@router.get("/{event_id}/device")
def get_event_device(event_id: int, db: Session = Depends(get_db)):
    """获取加工事件关联的设备"""
    event = _get_event_or_404(event_id, db)
    if not event.machine_id:
        return {"device": None, "message": "该事件未关联设备"}

    device = db.query(Device).filter(Device.device_code == event.machine_id).first()
    if not device:
        return {"device": None, "message": f"设备 {event.machine_id} 不存在"}

    return {"device": _device_to_dict(device)}


@router.get("/{event_id}/material")
def get_event_material(event_id: int, db: Session = Depends(get_db)):
    """获取加工事件关联的物料（通过 start_code 匹配）"""
    event = _get_event_or_404(event_id, db)

    # 尝试通过 start_code 匹配物料
    # start_code 可能是 u9_material_code 或 part_number
    material = None
    if event.start_code:
        material = db.query(Material).filter(
            or_(
                Material.u9_material_code == event.start_code,
                Material.part_number == event.start_code,
            )
        ).first()

    # 也尝试通过 process_no 关联的工艺定义中的 product_codes 查找
    if not material and event.process_no:
        process_def = db.query(ProcessDefinition).filter(
            ProcessDefinition.process_code == event.process_no
        ).first()
        if process_def and process_def.product_codes:
            import json
            try:
                codes = json.loads(process_def.product_codes)
                if codes:
                    material = db.query(Material).filter(
                        Material.u9_material_code.in_(codes)
                    ).first()
            except (json.JSONDecodeError, TypeError):
                pass

    if not material:
        return {"material": None, "message": "未找到关联物料"}

    return {
        "material": {
            "id": material.id,
            "u9_material_code": material.u9_material_code,
            "part_number": material.part_number,
            "product_name": material.product_name,
            "specification": material.specification,
            "category": material.category,
            "material_type": material.material_type,
        }
    }


@router.get("/{event_id}/orders")
def get_event_orders(event_id: int, db: Session = Depends(get_db)):
    """获取加工事件关联的订单（通过物料或设备+日期匹配）"""
    event = _get_event_or_404(event_id, db)
    orders = []

    # 方式1: 通过 start_code (part_number) 查找订单
    if event.start_code:
        orders = db.query(ProductOrder).filter(
            ProductOrder.part_number == event.start_code
        ).all()

    # 方式2: 通过 machine_id + 时间范围查找订单加工记录
    if not orders and event.machine_id:
        # 将毫秒时间戳转为日期字符串
        if event.start_time:
            event_date = datetime.fromtimestamp(event.start_time / 1000).strftime('%Y-%m-%d')
            opr_list = db.query(OrderProcessingRecord).filter(
                and_(
                    OrderProcessingRecord.device_code == event.machine_id,
                    OrderProcessingRecord.record_date == event_date,
                )
            ).all()
            doc_nos = [opr.doc_no for opr in opr_list if opr.doc_no]
            if doc_nos:
                orders = db.query(ProductOrder).filter(
                    ProductOrder.doc_no.in_(doc_nos)
                ).all()

    return {
        "total": len(orders),
        "items": [
            {
                "id": o.id,
                "doc_no": o.doc_no,
                "part_number": o.part_number,
                "u9_material_code": o.u9_material_code,
                "item_name": o.item_name,
                "planned_output": o.planned_output,
                "total_complete_qty": o.total_complete_qty,
                "doc_state": o.doc_state,
                "line_code": o.line_code,
                "machine": o.machine,
            }
            for o in orders
        ]
    }


@router.get("/{event_id}/process-params")
def get_event_process_params(event_id: int, db: Session = Depends(get_db)):
    """获取加工事件关联的工艺参数"""
    event = _get_event_or_404(event_id, db)

    conditions = []
    if event.machine_id:
        conditions.append(ProcessParameter.machine_id == event.machine_id)
    if event.start_code:
        conditions.append(ProcessParameter.start_code == event.start_code)
    if event.process_no:
        conditions.append(ProcessParameter.process_no == event.process_no)

    if not conditions:
        return {"total": 0, "items": [], "message": "无可用关联字段"}

    # 使用 AND 组合所有可用条件
    query = db.query(ProcessParameter).filter(and_(*conditions))

    # 如果事件有时间范围，限定参数时间
    if event.start_time:
        start_dt = datetime.fromtimestamp(event.start_time / 1000)
        query = query.filter(ProcessParameter.create_time >= start_dt)
    if event.end_time:
        end_dt = datetime.fromtimestamp(event.end_time / 1000)
        query = query.filter(ProcessParameter.create_time <= end_dt)

    params = query.order_by(ProcessParameter.create_time.desc()).limit(200).all()

    return {
        "total": len(params),
        "items": [
            {
                "id": p.id,
                "param_name": p.param_name,
                "param_value": p.param_value,
                "unit": p.unit,
                "process_type": p.process_type,
                "machine_id": p.machine_id,
                "product_model": p.product_model,
                "start_code": p.start_code,
                "process_no": p.process_no,
                "batch_no": p.batch_no,
                "create_time": str(p.create_time) if p.create_time else None,
            }
            for p in params
        ]
    }


@router.get("/{event_id}/process-definition")
def get_event_process_definition(event_id: int, db: Session = Depends(get_db)):
    """获取加工事件关联的工艺定义"""
    event = _get_event_or_404(event_id, db)

    if not event.process_no:
        return {"process_definition": None, "message": "该事件未关联工艺编号"}

    process_def = db.query(ProcessDefinition).filter(
        ProcessDefinition.process_code == event.process_no
    ).first()

    if not process_def:
        return {"process_definition": None, "message": f"工艺 {event.process_no} 不存在"}

    return {
        "process_definition": {
            "id": process_def.id,
            "process_code": process_def.process_code,
            "process_name": process_def.process_name,
            "process_type": process_def.process_type,
            "description": process_def.description,
            "status": process_def.status,
        }
    }


@router.get("/{event_id}/alarms")
def get_event_alarms(event_id: int, db: Session = Depends(get_db)):
    """获取加工事件关联的报警（通过设备+时间窗口匹配）"""
    event = _get_event_or_404(event_id, db)

    # 方式1: 通过 event_alarm_relations 关联表
    alarm_relations = db.query(EventAlarmRelation).filter(
        EventAlarmRelation.event_id == event.id
    ).all()

    if alarm_relations:
        alarm_ids = [r.alarm_record_id for r in alarm_relations if r.alarm_record_id]
        alarms = []
        if alarm_ids:
            alarms = db.query(AlarmRecord).filter(AlarmRecord.id.in_(alarm_ids)).all()

        # 补充关系表中的快照信息
        alarm_map = {a.id: a for a in alarms}
        items = []
        for rel in alarm_relations:
            alarm = alarm_map.get(rel.alarm_record_id)
            if alarm:
                items.append({
                    "id": alarm.id,
                    "alarm_code": alarm.alarm_code,
                    "alarm_level": alarm.alarm_level,
                    "alarm_type": alarm.alarm_type,
                    "title": alarm.title,
                    "description": alarm.description,
                    "device_code": alarm.device_code,
                    "alarm_value": alarm.alarm_value,
                    "status": alarm.status,
                    "alarm_time": str(alarm.alarm_time) if alarm.alarm_time else None,
                    "time_offset_ms": rel.time_offset_from_start_ms,
                })
            else:
                # 使用快照数据
                items.append({
                    "alarm_code": rel.alarm_code,
                    "alarm_level": rel.alarm_level,
                    "alarm_type": rel.alarm_type,
                    "title": rel.alarm_title,
                    "alarm_value": rel.alarm_value,
                    "alarm_time": str(rel.alarm_time) if rel.alarm_time else None,
                    "time_offset_ms": rel.time_offset_from_start_ms,
                    "from_snapshot": True,
                })

        return {"total": len(items), "items": items, "source": "relation_table"}

    # 方式2: 通过设备+时间窗口直接查询
    if not event.machine_id:
        return {"total": 0, "items": [], "message": "无关联报警数据"}

    query = db.query(AlarmRecord).filter(AlarmRecord.device_code == event.machine_id)

    if event.start_time:
        start_dt = datetime.fromtimestamp(event.start_time / 1000)
        query = query.filter(AlarmRecord.alarm_time >= start_dt)
    if event.end_time:
        end_dt = datetime.fromtimestamp(event.end_time / 1000)
        query = query.filter(AlarmRecord.alarm_time <= end_dt)

    alarms = query.order_by(AlarmRecord.alarm_time.desc()).limit(100).all()

    return {
        "total": len(alarms),
        "items": [
            {
                "id": a.id,
                "alarm_code": a.alarm_code,
                "alarm_level": a.alarm_level,
                "alarm_type": a.alarm_type,
                "title": a.title,
                "description": a.description,
                "device_code": a.device_code,
                "alarm_value": a.alarm_value,
                "status": a.status,
                "alarm_time": str(a.alarm_time) if a.alarm_time else None,
            }
            for a in alarms
        ],
        "source": "direct_query"
    }


@router.get("/{event_id}/quality")
def get_event_quality(event_id: int, db: Session = Depends(get_db)):
    """获取加工事件关联的质检记录（通过设备+产品编号匹配）"""
    event = _get_event_or_404(event_id, db)

    conditions = []
    if event.machine_id:
        conditions.append(QualityRecord.device_code == event.machine_id)
    if event.start_code:
        conditions.append(
            or_(
                QualityRecord.product_code == event.start_code,
                QualityRecord.product_name.contains(event.start_code),
            )
        )

    if not conditions:
        return {"total": 0, "items": [], "message": "无可用关联字段"}

    query = db.query(QualityRecord).filter(or_(*conditions))

    # 限定时间范围
    if event.start_time:
        start_dt = datetime.fromtimestamp(event.start_time / 1000)
        query = query.filter(QualityRecord.inspect_time >= start_dt)
    if event.end_time:
        end_dt = datetime.fromtimestamp(event.end_time / 1000)
        query = query.filter(QualityRecord.inspect_time <= end_dt)

    records = query.order_by(QualityRecord.created_at.desc()).limit(100).all()

    return {
        "total": len(records),
        "items": [
            {
                "id": r.id,
                "product_code": r.product_code,
                "product_name": r.product_name,
                "device_code": r.device_code,
                "status": r.status,
                "defect_type": r.defect_type,
                "defect_description": r.defect_description,
                "inspector": r.inspector,
                "inspect_time": str(r.inspect_time) if r.inspect_time else None,
                "quantity": r.quantity,
                "passed_quantity": r.passed_quantity,
                "failed_quantity": r.failed_quantity,
            }
            for r in records
        ]
    }


@router.get("/{event_id}/compressed-data")
def get_event_compressed_data(event_id: int, db: Session = Depends(get_db)):
    """获取加工事件关联的压缩数据（SV/PV/Alarm 关系）"""
    event = _get_event_or_404(event_id, db)

    sv_relations = db.query(EventSVRelation).filter(
        EventSVRelation.event_id == event.id
    ).all()

    pv_relations = db.query(EventPVRelation).filter(
        EventPVRelation.event_id == event.id
    ).all()

    alarm_relations = db.query(EventAlarmRelation).filter(
        EventAlarmRelation.event_id == event.id
    ).all()

    # 获取汇总信息
    summary = db.query(EventDataRelationSummary).filter(
        EventDataRelationSummary.event_id == event.id
    ).first()

    return {
        "sv": {
            "count": len(sv_relations),
            "items": [
                {
                    "id": r.id,
                    "sv_topic": r.sv_topic,
                    "sv_timestamp": str(r.sv_timestamp) if r.sv_timestamp else None,
                    "time_offset_ms": r.time_offset_ms,
                    "sv_data_snapshot": r.sv_data_snapshot,
                }
                for r in sv_relations[:50]  # 限制返回数量
            ]
        },
        "pv": {
            "count": len(pv_relations),
            "items": [
                {
                    "id": r.id,
                    "pv_topic": r.pv_topic,
                    "pv_timestamp": str(r.pv_timestamp) if r.pv_timestamp else None,
                    "time_offset_ms": r.time_offset_ms,
                    "pv_data_snapshot": r.pv_data_snapshot,
                    "sv_point_id": r.sv_point_id,
                }
                for r in pv_relations[:50]
            ]
        },
        "alarm": {
            "count": len(alarm_relations),
            "items": [
                {
                    "id": r.id,
                    "alarm_code": r.alarm_code,
                    "alarm_level": r.alarm_level,
                    "alarm_title": r.alarm_title,
                    "alarm_time": str(r.alarm_time) if r.alarm_time else None,
                    "time_offset_from_start_ms": r.time_offset_from_start_ms,
                }
                for r in alarm_relations[:50]
            ]
        },
        "summary": {
            "sv_count": summary.sv_count if summary else 0,
            "pv_count": summary.pv_count if summary else 0,
            "alarm_count": summary.alarm_count if summary else 0,
            "sv_matched": summary.sv_matched if summary else 0,
            "pv_matched": summary.pv_matched if summary else 0,
            "alarm_matched": summary.alarm_matched if summary else 0,
            "last_match_time": str(summary.last_match_time) if summary and summary.last_match_time else None,
        }
    }


@router.get("/{event_id}/flow-instance")
def get_event_flow_instance(event_id: int, db: Session = Depends(get_db)):
    """获取加工事件关联的流程实例"""
    event = _get_event_or_404(event_id, db)

    conditions = []
    if event.machine_id:
        conditions.append(ProductionFlowInstance.device_code == event.machine_id)

    # 尝试通过 start_code 匹配 part_number
    if event.start_code:
        conditions.append(ProductionFlowInstance.part_number == event.start_code)

    if not conditions:
        return {"total": 0, "items": [], "message": "无可用关联字段"}

    query = db.query(ProductionFlowInstance).filter(or_(*conditions))

    # 限定时间范围
    if event.start_time:
        event_date = datetime.fromtimestamp(event.start_time / 1000).strftime('%Y-%m-%d')
        query = query.filter(ProductionFlowInstance.record_date == event_date)

    instances = query.order_by(ProductionFlowInstance.created_at.desc()).limit(50).all()

    return {
        "total": len(instances),
        "items": [
            {
                "id": inst.id,
                "flow_id": inst.flow_id,
                "doc_no": inst.doc_no,
                "part_number": inst.part_number,
                "device_code": inst.device_code,
                "status": inst.status,
                "planned_qty": inst.planned_qty,
                "completed_qty": inst.completed_qty,
                "record_date": inst.record_date,
                "start_time": str(inst.start_time) if inst.start_time else None,
                "end_time": str(inst.end_time) if inst.end_time else None,
            }
            for inst in instances
        ]
    }


@router.get("/{event_id}/all")
def get_event_all_associations(event_id: int, db: Session = Depends(get_db)):
    """获取加工事件的所有关联数据（聚合接口）"""
    event = _get_event_or_404(event_id, db)

    # 基本信息
    event_info = _event_to_dict(event)

    # 设备
    device = None
    if event.machine_id:
        device = db.query(Device).filter(Device.device_code == event.machine_id).first()

    # 物料
    material = None
    if event.start_code:
        material = db.query(Material).filter(
            or_(
                Material.u9_material_code == event.start_code,
                Material.part_number == event.start_code,
            )
        ).first()

    # 工艺定义
    process_def = None
    if event.process_no:
        process_def = db.query(ProcessDefinition).filter(
            ProcessDefinition.process_code == event.process_no
        ).first()

    # 工艺参数（简化版）
    param_conditions = []
    if event.machine_id:
        param_conditions.append(ProcessParameter.machine_id == event.machine_id)
    if event.start_code:
        param_conditions.append(ProcessParameter.start_code == event.start_code)
    params_count = 0
    if param_conditions:
        params_count = db.query(func.count(ProcessParameter.id)).filter(
            and_(*param_conditions)
        ).scalar() or 0

    # 报警（通过关系表）
    alarm_count = db.query(func.count(EventAlarmRelation.id)).filter(
        EventAlarmRelation.event_id == event.id
    ).scalar() or 0

    # 质检记录
    quality_conditions = []
    if event.machine_id:
        quality_conditions.append(QualityRecord.device_code == event.machine_id)
    if event.start_code:
        quality_conditions.append(QualityRecord.product_code == event.start_code)
    quality_count = 0
    if quality_conditions:
        quality_count = db.query(func.count(QualityRecord.id)).filter(
            or_(*quality_conditions)
        ).scalar() or 0

    # 订单
    orders = []
    if event.start_code:
        orders = db.query(ProductOrder).filter(
            ProductOrder.part_number == event.start_code
        ).limit(10).all()

    # 关系汇总
    summary = db.query(EventDataRelationSummary).filter(
        EventDataRelationSummary.event_id == event.id
    ).first()

    return {
        "event": event_info,
        "device": _device_to_dict(device) if device else None,
        "material": {
            "id": material.id,
            "u9_material_code": material.u9_material_code,
            "part_number": material.part_number,
            "product_name": material.product_name,
            "specification": material.specification,
        } if material else None,
        "process_definition": {
            "id": process_def.id,
            "process_code": process_def.process_code,
            "process_name": process_def.process_name,
            "process_type": process_def.process_type,
        } if process_def else None,
        "counts": {
            "process_params": params_count,
            "alarms": alarm_count,
            "quality_records": quality_count,
            "orders": len(orders),
            "sv_relations": summary.sv_count if summary else 0,
            "pv_relations": summary.pv_count if summary else 0,
        },
        "orders": [
            {
                "id": o.id,
                "doc_no": o.doc_no,
                "part_number": o.part_number,
                "item_name": o.item_name,
                "doc_state": o.doc_state,
            }
            for o in orders
        ]
    }


# ============================================================
# 反向关联：从其他模块查加工事件
# ============================================================

@router.get("/by-device/{device_code}")
def get_events_by_device(
    device_code: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    start_time: Optional[int] = None,
    end_time: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """按设备查询加工事件"""
    query = db.query(EventData).filter(EventData.machine_id == device_code)

    if start_time:
        query = query.filter(EventData.start_time >= start_time)
    if end_time:
        query = query.filter(EventData.start_time <= end_time)

    total = query.count()
    items = query.order_by(EventData.start_time.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()

    return {
        "total": total,
        "items": [_event_to_dict(e) for e in items],
    }


@router.get("/by-material/{start_code}")
def get_events_by_material(
    start_code: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """按物料编号查询加工事件"""
    query = db.query(EventData).filter(EventData.start_code == start_code)

    total = query.count()
    items = query.order_by(EventData.start_time.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()

    return {
        "total": total,
        "items": [_event_to_dict(e) for e in items],
    }


@router.get("/by-order/{doc_no}")
def get_events_by_order(
    doc_no: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """按订单号查询加工事件（通过订单→物料→事件 或 订单→设备+日期→事件）"""
    # 先查订单
    order = db.query(ProductOrder).filter(ProductOrder.doc_no == doc_no).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")

    # 方式1: 通过 part_number 匹配 start_code
    events = []
    if order.part_number:
        query = db.query(EventData).filter(EventData.start_code == order.part_number)
        total = query.count()
        items = query.order_by(EventData.start_time.desc()).offset(
            (page - 1) * page_size
        ).limit(page_size).all()
        events = [_event_to_dict(e) for e in items]
        return {"total": total, "items": events, "match_method": "part_number"}

    # 方式2: 通过订单加工记录找设备+日期
    opr_list = db.query(OrderProcessingRecord).filter(
        OrderProcessingRecord.doc_no == doc_no
    ).all()

    if opr_list:
        all_events = []
        for opr in opr_list:
            opr_events = db.query(EventData).filter(
                EventData.machine_id == opr.device_code
            )
            if opr.record_date:
                day_start = datetime.strptime(opr.record_date, '%Y-%m-%d')
                day_end = day_start.replace(hour=23, minute=59, second=59)
                ts_start = int(day_start.timestamp() * 1000)
                ts_end = int(day_end.timestamp() * 1000)
                opr_events = opr_events.filter(
                    and_(
                        EventData.start_time >= ts_start,
                        EventData.start_time <= ts_end,
                    )
                )
            all_events.extend(opr_events.all())

        # 去重
        seen = set()
        unique_events = []
        for e in all_events:
            if e.id not in seen:
                seen.add(e.id)
                unique_events.append(e)

        total = len(unique_events)
        start = (page - 1) * page_size
        end = start + page_size
        paged = unique_events[start:end]

        return {"total": total, "items": [_event_to_dict(e) for e in paged], "match_method": "device_date"}

    return {"total": 0, "items": [], "match_method": "none"}


@router.get("/by-process/{process_code}")
def get_events_by_process(
    process_code: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """按工艺编号查询加工事件"""
    query = db.query(EventData).filter(EventData.process_no == process_code)

    total = query.count()
    items = query.order_by(EventData.start_time.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()

    return {
        "total": total,
        "items": [_event_to_dict(e) for e in items],
    }
