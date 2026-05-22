"""
订单加工关联服务
将 MQTT 设备加工事件自动关联到 ERP 订单，并维护本地加工记录
"""
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from app.database import get_db_session
from app.models.event_data import EventData
from app.models.order_processing_record import OrderProcessingRecord
from app.models.product_order import ProductOrder
from app.models.material import Material
from app.services.product_resolver import resolve_product_from_value, resolve_order_for_product

logger = logging.getLogger(__name__)


def link_event_to_order(event_id: int, db: Optional[Session] = None) -> Dict[str, Any]:
    """
    将单个加工事件关联到订单

    Args:
        event_id: EventData 的 ID
        db: 可选的数据库会话，不传则自动创建

    Returns:
        {"success": bool, "action": str, "detail": str}
    """
    own_db = db is None
    if own_db:
        ctx = get_db_session()
        db = ctx.__enter__()

    try:
        event = db.query(EventData).filter(EventData.id == event_id).first()
        if not event:
            return {"success": False, "action": "skip", "detail": f"事件 {event_id} 不存在"}

        if not event.start_time:
            return {"success": False, "action": "skip", "detail": f"事件 {event_id} 无 start_time"}

        machine_id = event.machine_id or ''
        start_code = event.start_code or ''

        if not machine_id:
            return {"success": False, "action": "skip", "detail": f"事件 {event_id} 无 machine_id"}

        # 从事件时间戳推算 record_date
        record_date = datetime.fromtimestamp(event.start_time / 1000).strftime('%Y-%m-%d')

        # 尝试匹配物料
        material = resolve_product_from_value(db, start_code) if start_code else None

        # 尝试匹配订单
        order_info = None
        if material and material.u9_material_code:
            order_info = resolve_order_for_product(db, material, query_date=record_date)

        # 确定 doc_no 和 part_number
        doc_no = None
        part_number = None
        u9_material_code = None

        if material:
            part_number = material.part_number
            u9_material_code = material.u9_material_code

        if order_info:
            doc_no = order_info.get('doc_no')

        # 转换事件时间为 datetime
        start_time_dt = datetime.fromtimestamp(event.start_time / 1000) if event.start_time else None
        end_time_dt = datetime.fromtimestamp(event.end_time / 1000) if event.end_time else None

        # Upsert OrderProcessingRecord
        result = _upsert_record(
            db=db,
            device_code=machine_id,
            record_date=record_date,
            doc_no=doc_no,
            part_number=part_number,
            u9_material_code=u9_material_code,
            planned_qty=order_info.get('planned_output') if order_info else None,
            start_time=start_time_dt,
            end_time=end_time_dt,
        )

        db.commit()
        return result

    except Exception as e:
        db.rollback()
        logger.error(f"关联事件 {event_id} 失败: {e}")
        return {"success": False, "action": "error", "detail": str(e)}
    finally:
        if own_db:
            ctx.__exit__(None, None, None)


def _upsert_record(
    db: Session,
    device_code: str,
    record_date: str,
    doc_no: Optional[str],
    part_number: Optional[str],
    u9_material_code: Optional[str],
    planned_qty: Optional[int],
    start_time: Optional[datetime],
    end_time: Optional[datetime],
) -> Dict[str, Any]:
    """
    插入或更新 OrderProcessingRecord
    按 (device_code, record_date, doc_no) 唯一约束 upsert
    """
    # 查询已有记录
    query = db.query(OrderProcessingRecord).filter(
        OrderProcessingRecord.device_code == device_code,
        OrderProcessingRecord.record_date == record_date,
    )
    if doc_no:
        query = query.filter(OrderProcessingRecord.doc_no == doc_no)
    else:
        query = query.filter(OrderProcessingRecord.doc_no.is_(None))

    existing = query.first()

    if existing:
        existing.completed_qty = (existing.completed_qty or 0) + 1
        if end_time:
            existing.end_time = end_time
        if part_number and not existing.part_number:
            existing.part_number = part_number
        if u9_material_code and not existing.u9_material_code:
            existing.u9_material_code = u9_material_code
        if planned_qty and not existing.planned_qty:
            existing.planned_qty = planned_qty
        return {"success": True, "action": "updated", "detail": f"记录 {existing.id} 完成数+1"}
    else:
        record = OrderProcessingRecord(
            device_code=device_code,
            record_date=record_date,
            doc_no=doc_no,
            part_number=part_number,
            u9_material_code=u9_material_code,
            planned_qty=planned_qty,
            completed_qty=1,
            eligible_qty=0,
            scrap_qty=0,
            status='in_progress',
            start_time=start_time,
            end_time=end_time,
        )
        db.add(record)
        db.flush()
        return {"success": True, "action": "created", "detail": f"新建记录 device={device_code} doc={doc_no}"}


def batch_link_unlinked_events(batch_size: int = 100) -> Dict[str, Any]:
    """
    批量补漏：查找今日未关联到订单的 event_data，逐条关联

    "未关联"定义：该事件的 (machine_id, record_date) 组合在 order_processing_records 中
    没有对应记录，或者事件的 start_code 未被匹配过。

    简化实现：查询今日的 event_data，检查是否已有对应的 order_processing_record。
    """
    with get_db_session() as db:
        today = datetime.now().strftime('%Y-%m-%d')
        today_start_ms = int(datetime.strptime(today, '%Y-%m-%d').timestamp() * 1000)
        today_end_ms = today_start_ms + 86400 * 1000

        # 查询今日的事件
        events = db.query(EventData).filter(
            EventData.start_time >= today_start_ms,
            EventData.start_time < today_end_ms,
        ).order_by(EventData.start_time.desc()).limit(batch_size).all()

        processed = 0
        created = 0
        updated = 0
        skipped = 0
        errors = 0

        for event in events:
            # 检查是否已有记录
            record_date = datetime.fromtimestamp(event.start_time / 1000).strftime('%Y-%m-%d')
            existing = db.query(OrderProcessingRecord).filter(
                OrderProcessingRecord.device_code == event.machine_id,
                OrderProcessingRecord.record_date == record_date,
            ).first()

            if existing:
                skipped += 1
                continue

            result = link_event_to_order(event.id, db)
            processed += 1

            if result['success']:
                if result['action'] == 'created':
                    created += 1
                elif result['action'] == 'updated':
                    updated += 1
            else:
                errors += 1

        return {
            "success": True,
            "processed": processed,
            "created": created,
            "updated": updated,
            "skipped": skipped,
            "errors": errors,
        }


def get_completion_comparison(
    record_date: Optional[str] = None,
) -> Dict[str, Any]:
    """
    完工比对：按 doc_no 汇总本地完成数，与 U9 完工数据比较

    Returns:
        {
            "summary": { total_orders, total_planned, total_local_completed, ... },
            "items": [ { doc_no, planned, local_completed, u9_complete, u9_eligible, u9_scrap, diff, status } ]
        }
    """
    with get_db_session() as db:
        if not record_date:
            record_date = datetime.now().strftime('%Y-%m-%d')

        # 查询本地记录，按 doc_no 汇总
        local_records = db.query(
            OrderProcessingRecord.doc_no,
            OrderProcessingRecord.part_number,
            OrderProcessingRecord.u9_material_code,
            func.sum(OrderProcessingRecord.completed_qty).label('local_completed'),
            func.sum(OrderProcessingRecord.eligible_qty).label('local_eligible'),
            func.sum(OrderProcessingRecord.scrap_qty).label('local_scrap'),
            func.max(OrderProcessingRecord.planned_qty).label('planned_qty'),
            func.count(OrderProcessingRecord.id).label('record_count'),
        ).filter(
            OrderProcessingRecord.record_date == record_date,
        ).group_by(
            OrderProcessingRecord.doc_no,
            OrderProcessingRecord.part_number,
            OrderProcessingRecord.u9_material_code,
        ).all()

        items = []
        total_planned = 0
        total_local_completed = 0
        total_u9_complete = 0
        total_u9_eligible = 0
        total_u9_scrap = 0

        for rec in local_records:
            local_completed = int(rec.local_completed or 0)
            planned = int(rec.planned_qty or 0)

            # 查 U9 数据
            u9_complete = 0
            u9_eligible = 0
            u9_scrap = 0
            if rec.doc_no:
                u9_order = db.query(ProductOrder).filter(
                    ProductOrder.doc_no == rec.doc_no
                ).first()
                if u9_order:
                    u9_complete = int(u9_order.total_complete_qty or 0)
                    u9_eligible = int(u9_order.total_eligible_qty or 0)
                    u9_scrap = int(u9_order.total_scrap_qty or 0)

            diff = local_completed - u9_complete
            completion_rate = round(local_completed / planned * 100, 1) if planned > 0 else 0

            status = 'normal'
            if diff > 0:
                status = 'local_ahead'
            elif diff < 0:
                status = 'local_behind'

            items.append({
                "doc_no": rec.doc_no or "(未匹配订单)",
                "part_number": rec.part_number,
                "u9_material_code": rec.u9_material_code,
                "planned_qty": planned,
                "local_completed": local_completed,
                "u9_completed": u9_complete,
                "u9_eligible": u9_eligible,
                "u9_scrap": u9_scrap,
                "diff": diff,
                "completion_rate": completion_rate,
                "status": status,
                "record_count": int(rec.record_count),
            })

            total_planned += planned
            total_local_completed += local_completed
            total_u9_complete += u9_complete
            total_u9_eligible += u9_eligible
            total_u9_scrap += u9_scrap

        summary = {
            "record_date": record_date,
            "total_orders": len(items),
            "total_planned": total_planned,
            "total_local_completed": total_local_completed,
            "total_u9_completed": total_u9_complete,
            "total_u9_eligible": total_u9_eligible,
            "total_u9_scrap": total_u9_scrap,
            "total_diff": total_local_completed - total_u9_complete,
            "overall_completion_rate": round(total_local_completed / total_planned * 100, 1) if total_planned > 0 else 0,
        }

        return {"summary": summary, "items": items}


def get_order_timeline(
    doc_no: str,
    record_date: Optional[str] = None,
) -> Dict[str, Any]:
    """
    单个订单的按小时产量时间线

    从 event_data 按 machine_id + 时间范围聚合
    """
    with get_db_session() as db:
        if not record_date:
            record_date = datetime.now().strftime('%Y-%m-%d')

        # 获取本地记录
        records = db.query(OrderProcessingRecord).filter(
            OrderProcessingRecord.doc_no == doc_no,
            OrderProcessingRecord.record_date == record_date,
        ).all()

        if not records:
            return {"doc_no": doc_no, "record_date": record_date, "timeline": [], "total": 0}

        device_codes = [r.device_code for r in records]
        total_completed = sum(r.completed_qty or 0 for r in records)

        # 按小时聚合 event_data
        today_start_ms = int(datetime.strptime(record_date, '%Y-%m-%d').timestamp() * 1000)
        today_end_ms = today_start_ms + 86400 * 1000

        # 查询关联设备的事件，按小时分组
        hourly_data = []
        for hour in range(24):
            hour_start = today_start_ms + hour * 3600 * 1000
            hour_end = hour_start + 3600 * 1000

            count = db.query(func.count(EventData.id)).filter(
                EventData.machine_id.in_(device_codes),
                EventData.start_time >= hour_start,
                EventData.start_time < hour_end,
            ).scalar() or 0

            avg_duration = db.query(func.avg(EventData.machine_duringtime)).filter(
                EventData.machine_id.in_(device_codes),
                EventData.start_time >= hour_start,
                EventData.start_time < hour_end,
            ).scalar()

            if count > 0:
                hourly_data.append({
                    "hour": f"{hour:02d}:00",
                    "count": count,
                    "avg_duration_ms": round(avg_duration) if avg_duration else 0,
                })

        return {
            "doc_no": doc_no,
            "record_date": record_date,
            "device_codes": device_codes,
            "total_completed": total_completed,
            "timeline": hourly_data,
        }


def reconcile_order_statuses(record_date: Optional[str] = None) -> Dict[str, Any]:
    """
    订单状态同步：完成数 >= 计划数时标记为 completed
    """
    with get_db_session() as db:
        if not record_date:
            record_date = datetime.now().strftime('%Y-%m-%d')

        records = db.query(OrderProcessingRecord).filter(
            OrderProcessingRecord.record_date == record_date,
            OrderProcessingRecord.status == 'in_progress',
        ).all()

        updated = 0
        for record in records:
            if record.planned_qty and record.completed_qty:
                if record.completed_qty >= record.planned_qty:
                    record.status = 'completed'
                    record.end_time = record.end_time or datetime.now()
                    updated += 1

        return {"success": True, "updated": updated, "record_date": record_date}
