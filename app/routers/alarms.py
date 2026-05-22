"""
报警管理 API 路由
功能：报警记录的增删改查、处理、统计
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from datetime import datetime
import uuid

from app.database import get_db
from app.models.alarm_record import AlarmRecord
from app.models.event_data import EventData
from app.models.event_relations import EventAlarmRelation
from sqlalchemy import and_, or_
from app.schemas.alarm import (
    AlarmQuery, AlarmList, AlarmDetail, AlarmCreate, AlarmUpdate, AlarmHandle, AlarmStats
)

router = APIRouter(prefix="/alarms", tags=["报警管理"])


@router.get("/", response_model=AlarmList)
async def list_alarms(
    query: AlarmQuery = Depends(),
    db: Session = Depends(get_db)
):
    """
    查询报警记录列表（支持多条件组合查询）
    
    查询条件包括：
    - 报警编号：alarm_code（支持模糊查询）
    - 报警来源：alarm_source
    - 报警级别：alarm_level
    - 报警类型：alarm_type
    - 报警状态：status
    - 设备编号：device_code
    - 日期范围：start_date, end_date
    """
    db_query = db.query(AlarmRecord)
    
    if query.alarm_code:
        db_query = db_query.filter(AlarmRecord.alarm_code.contains(query.alarm_code))
    
    if query.alarm_source:
        db_query = db_query.filter(AlarmRecord.alarm_source == query.alarm_source)
    
    if query.alarm_level:
        db_query = db_query.filter(AlarmRecord.alarm_level == query.alarm_level)
    
    if query.alarm_type:
        db_query = db_query.filter(AlarmRecord.alarm_type == query.alarm_type)
    
    if query.status:
        db_query = db_query.filter(AlarmRecord.status == query.status)
    
    if query.device_code:
        db_query = db_query.filter(AlarmRecord.device_code.contains(query.device_code))
    
    if query.start_date:
        try:
            start_dt = datetime.fromisoformat(query.start_date)
            db_query = db_query.filter(AlarmRecord.alarm_time >= start_dt)
        except ValueError:
            pass
    
    if query.end_date:
        try:
            end_dt = datetime.fromisoformat(query.end_date)
            db_query = db_query.filter(AlarmRecord.alarm_time <= end_dt)
        except ValueError:
            pass
    
    total = db_query.count()
    
    offset = (query.page - 1) * query.page_size
    items = db_query.order_by(AlarmRecord.alarm_time.desc()).offset(offset).limit(query.page_size).all()
    
    parsed_items = []
    for item in items:
        item_dict = {c.name: getattr(item, c.name) for c in item.__table__.columns}
        parsed_items.append(AlarmDetail(**item_dict))
    
    return AlarmList(total=total, items=parsed_items)


@router.post("/", response_model=AlarmDetail)
async def create_alarm(alarm: AlarmCreate, db: Session = Depends(get_db)):
    """创建新报警记录"""
    existing = db.query(AlarmRecord).filter(AlarmRecord.alarm_code == alarm.alarm_code).first()
    if existing:
        raise HTTPException(status_code=400, detail="报警编号已存在")
    
    alarm_data = alarm.model_dump()
    db_alarm = AlarmRecord(**alarm_data)
    db.add(db_alarm)
    db.commit()
    db.refresh(db_alarm)
    
    item_dict = {c.name: getattr(db_alarm, c.name) for c in db_alarm.__table__.columns}
    return AlarmDetail(**item_dict)


@router.post("/batch/delete")
async def batch_delete_alarms(alarm_ids: list[int], db: Session = Depends(get_db)):
    """批量删除报警记录"""
    deleted = db.query(AlarmRecord).filter(AlarmRecord.id.in_(alarm_ids)).delete(synchronize_session=False)
    db.commit()
    return {"message": f"已删除 {deleted} 条报警记录", "deleted_count": deleted}


@router.post("/batch/handle")
async def batch_handle_alarms(
    alarm_ids: list[int],
    handle_data: AlarmHandle,
    db: Session = Depends(get_db)
):
    """批量处理报警"""
    alarms = db.query(AlarmRecord).filter(AlarmRecord.id.in_(alarm_ids)).all()
    
    handled_count = 0
    for alarm in alarms:
        if alarm.status not in ['resolved', 'ignored']:
            alarm.status = handle_data.status
            alarm.handler = handle_data.handler or 'system'
            alarm.handle_remark = handle_data.handle_remark
            alarm.handled_at = datetime.now()
            alarm.updated_at = datetime.now()
            handled_count += 1
    
    db.commit()
    return {"message": f"已处理 {handled_count} 条报警记录", "handled_count": handled_count}


@router.get("/stats", response_model=AlarmStats)
async def get_alarm_stats(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取报警统计信息"""
    db_query = db.query(AlarmRecord)
    
    if start_date:
        try:
            start_dt = datetime.fromisoformat(start_date)
            db_query = db_query.filter(AlarmRecord.alarm_time >= start_dt)
        except ValueError:
            pass
    
    if end_date:
        try:
            end_dt = datetime.fromisoformat(end_date)
            db_query = db_query.filter(AlarmRecord.alarm_time <= end_dt)
        except ValueError:
            pass
    
    total = db_query.count()
    pending = db_query.filter(AlarmRecord.status == 'pending').count()
    processing = db_query.filter(AlarmRecord.status == 'processing').count()
    resolved = db_query.filter(AlarmRecord.status == 'resolved').count()
    ignored = db_query.filter(AlarmRecord.status == 'ignored').count()
    
    critical = db_query.filter(AlarmRecord.alarm_level == 'critical').count()
    warning = db_query.filter(AlarmRecord.alarm_level == 'warning').count()
    info = db_query.filter(AlarmRecord.alarm_level == 'info').count()
    
    return AlarmStats(
        total=total,
        pending=pending,
        processing=processing,
        resolved=resolved,
        ignored=ignored,
        critical=critical,
        warning=warning,
        info=info
    )


@router.get("/recent")
async def get_recent_alarms(
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """获取最近的报警记录"""
    items = db.query(AlarmRecord).order_by(AlarmRecord.alarm_time.desc()).limit(limit).all()
    
    parsed_items = []
    for item in items:
        item_dict = {c.name: getattr(item, c.name) for c in item.__table__.columns}
        parsed_items.append(AlarmDetail(**item_dict))
    
    return {"total": len(parsed_items), "items": parsed_items}


@router.delete("/clear")
async def clear_old_alarms(
    days: int = Query(30, ge=1),
    db: Session = Depends(get_db)
):
    """清理历史报警记录"""
    from datetime import timedelta
    
    cutoff_date = datetime.now() - timedelta(days=days)
    deleted = db.query(AlarmRecord).filter(
        AlarmRecord.alarm_time < cutoff_date,
        AlarmRecord.status.in_(['resolved', 'ignored'])
    ).delete(synchronize_session=False)
    
    db.commit()
    return {"message": f"已清理 {days} 天前的 {deleted} 条报警记录", "deleted_count": deleted}


@router.get("/{alarm_id}", response_model=AlarmDetail)
async def get_alarm(alarm_id: int, db: Session = Depends(get_db)):
    """获取报警详情"""
    alarm = db.query(AlarmRecord).filter(AlarmRecord.id == alarm_id).first()
    if not alarm:
        raise HTTPException(status_code=404, detail="报警记录不存在")
    
    item_dict = {c.name: getattr(alarm, c.name) for c in alarm.__table__.columns}
    return AlarmDetail(**item_dict)


@router.put("/{alarm_id}", response_model=AlarmDetail)
async def update_alarm(alarm_id: int, alarm: AlarmUpdate, db: Session = Depends(get_db)):
    """更新报警信息"""
    db_alarm = db.query(AlarmRecord).filter(AlarmRecord.id == alarm_id).first()
    if not db_alarm:
        raise HTTPException(status_code=404, detail="报警记录不存在")
    
    update_data = alarm.model_dump(exclude_unset=True)
    
    if 'status' in update_data:
        if update_data['status'] in ['processing', 'resolved', 'ignored']:
            update_data['handled_at'] = datetime.now()
            if 'handler' not in update_data or not update_data['handler']:
                update_data['handler'] = 'system'
    
    for field, value in update_data.items():
        setattr(db_alarm, field, value)
    
    db_alarm.updated_at = datetime.now()
    db.commit()
    db.refresh(db_alarm)
    
    item_dict = {c.name: getattr(db_alarm, c.name) for c in db_alarm.__table__.columns}
    return AlarmDetail(**item_dict)


@router.post("/{alarm_id}/handle", response_model=AlarmDetail)
async def handle_alarm(alarm_id: int, handle_data: AlarmHandle, db: Session = Depends(get_db)):
    """处理报警"""
    db_alarm = db.query(AlarmRecord).filter(AlarmRecord.id == alarm_id).first()
    if not db_alarm:
        raise HTTPException(status_code=404, detail="报警记录不存在")
    
    if db_alarm.status == 'resolved' or db_alarm.status == 'ignored':
        raise HTTPException(status_code=400, detail="该报警已处理")
    
    db_alarm.status = handle_data.status
    db_alarm.handler = handle_data.handler or 'system'
    db_alarm.handle_remark = handle_data.handle_remark
    db_alarm.handled_at = datetime.now()
    db_alarm.updated_at = datetime.now()
    
    db.commit()
    db.refresh(db_alarm)
    
    item_dict = {c.name: getattr(db_alarm, c.name) for c in db_alarm.__table__.columns}
    return AlarmDetail(**item_dict)


@router.delete("/{alarm_id}")
async def delete_alarm(alarm_id: int, db: Session = Depends(get_db)):
    """删除报警记录"""
    alarm = db.query(AlarmRecord).filter(AlarmRecord.id == alarm_id).first()
    if not alarm:
        raise HTTPException(status_code=404, detail="报警记录不存在")
    
    db.delete(alarm)
    db.commit()
    return {"message": "报警记录已删除"}


@router.get("/{alarm_id}/events")
async def get_alarm_events(
    alarm_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """获取报警关联的加工事件（通过 event_alarm_relations 或设备+时间窗口）"""
    alarm = db.query(AlarmRecord).filter(AlarmRecord.id == alarm_id).first()
    if not alarm:
        raise HTTPException(status_code=404, detail="报警记录不存在")

    # 方式1: 通过 event_alarm_relations 关联表
    alarm_relations = db.query(EventAlarmRelation).filter(
        EventAlarmRelation.alarm_code == alarm.alarm_code
    ).all()

    if alarm_relations:
        event_ids = [r.event_id for r in alarm_relations if r.event_id]
        if event_ids:
            events = db.query(EventData).filter(EventData.id.in_(event_ids)).all()
            return {
                "total": len(events),
                "items": [
                    {
                        "id": e.id,
                        "event_uid": e.event_uid,
                        "start_code": e.start_code,
                        "start_time": e.start_time,
                        "end_time": e.end_time,
                        "duringtime": e.duringtime,
                        "machine_id": e.machine_id,
                        "operator_name": e.operator_name,
                        "process_no": e.process_no,
                    }
                    for e in events
                ],
                "source": "relation_table"
            }

    # 方式2: 通过设备+时间窗口
    if not alarm.device_code:
        return {"total": 0, "items": [], "message": "无关联设备信息"}

    from datetime import timedelta
    time_start = alarm.alarm_time - timedelta(hours=2)
    time_end = alarm.alarm_time + timedelta(hours=2)
    ts_start = int(time_start.timestamp() * 1000)
    ts_end = int(time_end.timestamp() * 1000)

    events = db.query(EventData).filter(
        and_(
            EventData.machine_id == alarm.device_code,
            EventData.start_time >= ts_start,
            EventData.start_time <= ts_end,
        )
    ).order_by(EventData.start_time.desc()).limit(page_size).all()

    return {
        "total": len(events),
        "items": [
            {
                "id": e.id,
                "event_uid": e.event_uid,
                "start_code": e.start_code,
                "start_time": e.start_time,
                "end_time": e.end_time,
                "duringtime": e.duringtime,
                "machine_id": e.machine_id,
                "operator_name": e.operator_name,
                "process_no": e.process_no,
            }
            for e in events
        ],
        "source": "time_window"
    }
