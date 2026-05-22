"""
事件数据关联管理 API 路由
功能：管理事件数据与SV/PV/报警的关联关系
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any

from app.database import get_db
from app.services.event_data_relation import EventDataRelationService
from app.services.event_relation_scheduler import get_event_relation_scheduler

router = APIRouter(prefix="/event-relations", tags=["事件数据关联管理"])


@router.post("/{event_id}/match")
async def match_event_relations(
    event_id: int,
    db: Session = Depends(get_db)
):
    """
    手动触发事件关联匹配
    
    Args:
        event_id: 事件ID
        
    Returns:
        匹配结果
    """
    service = EventDataRelationService(db)
    result = service.match_and_save_relations(event_id)
    
    return {
        "message": "关联匹配完成",
        "event_id": event_id,
        "result": result
    }


@router.get("/{event_id}")
async def get_event_relations(
    event_id: int,
    db: Session = Depends(get_db)
):
    """
    获取事件的关联数据
    
    Args:
        event_id: 事件ID
        
    Returns:
        事件关联数据
    """
    service = EventDataRelationService(db)
    relations = service.get_event_relations(event_id)
    
    if not relations["summary"]["event_id"]:
        raise HTTPException(status_code=404, detail="事件关联数据不存在")
    
    return relations


@router.post("/batch-match")
async def batch_match_events(
    limit: int = Query(100, ge=1, le=1000, description="处理数量"),
    db: Session = Depends(get_db)
):
    """
    批量匹配未关联的事件
    
    Args:
        limit: 处理数量
        
    Returns:
        批量处理结果
    """
    service = EventDataRelationService(db)
    result = service.batch_match_unmatched_events(limit)
    
    return {
        "message": "批量匹配完成",
        "result": result
    }


@router.get("/scheduler/status")
async def get_scheduler_status():
    """
    获取定时任务状态
    
    Returns:
        定时任务状态
    """
    scheduler = get_event_relation_scheduler()
    return scheduler.get_status()


@router.post("/scheduler/run")
async def run_scheduler_once(
    batch_size: int = Query(100, ge=1, le=1000, description="批次大小")
):
    """
    立即执行一次定时任务
    
    Args:
        batch_size: 批次大小
        
    Returns:
        执行结果
    """
    scheduler = get_event_relation_scheduler()
    result = scheduler.run_once()
    
    return {
        "message": "定时任务执行完成",
        "result": result
    }


@router.post("/scheduler/start")
async def start_scheduler(
    interval: int = Query(300, ge=60, le=3600, description="执行间隔（秒）"),
    batch_size: int = Query(100, ge=1, le=1000, description="批次大小")
):
    """
    启动定时任务
    
    Args:
        interval: 执行间隔（秒）
        batch_size: 批次大小
        
    Returns:
        操作结果
    """
    scheduler = get_event_relation_scheduler()
    scheduler.start(interval=interval, batch_size=batch_size)
    
    return {
        "message": "定时任务已启动",
        "interval": interval,
        "batch_size": batch_size
    }


@router.post("/scheduler/stop")
async def stop_scheduler():
    """
    停止定时任务
    
    Returns:
        操作结果
    """
    scheduler = get_event_relation_scheduler()
    scheduler.stop()
    
    return {
        "message": "定时任务已停止"
    }


@router.get("/stats")
async def get_relation_stats(
    start_time: Optional[int] = Query(None, description="开始时间（毫秒时间戳）"),
    end_time: Optional[int] = Query(None, description="结束时间（毫秒时间戳）"),
    machine_id: Optional[str] = Query(None, description="设备编号"),
    db: Session = Depends(get_db)
):
    """
    获取关联统计信息
    
    Args:
        start_time: 开始时间
        end_time: 结束时间
        machine_id: 设备编号
        
    Returns:
        关联统计
    """
    from app.models.event_relations import EventDataRelationSummary
    from sqlalchemy import func
    
    query = db.query(EventDataRelationSummary)
    
    if machine_id:
        query = query.filter(EventDataRelationSummary.machine_id == machine_id)
    
    if start_time:
        query = query.filter(EventDataRelationSummary.event_start_time >= start_time)
    
    if end_time:
        query = query.filter(EventDataRelationSummary.event_end_time <= end_time)
    
    total_events = query.count()
    sv_matched = query.filter(EventDataRelationSummary.sv_matched == 1).count()
    pv_matched = query.filter(EventDataRelationSummary.pv_matched == 1).count()
    alarm_matched = query.filter(EventDataRelationSummary.alarm_matched == 1).count()
    
    avg_sv = query.with_entities(func.avg(EventDataRelationSummary.sv_count)).scalar() or 0
    avg_pv = query.with_entities(func.avg(EventDataRelationSummary.pv_count)).scalar() or 0
    avg_alarm = query.with_entities(func.avg(EventDataRelationSummary.alarm_count)).scalar() or 0
    
    return {
        "total_events": total_events,
        "sv_matched": sv_matched,
        "pv_matched": pv_matched,
        "alarm_matched": alarm_matched,
        "sv_match_rate": round(sv_matched / total_events * 100, 2) if total_events > 0 else 0,
        "pv_match_rate": round(pv_matched / total_events * 100, 2) if total_events > 0 else 0,
        "alarm_match_rate": round(alarm_matched / total_events * 100, 2) if total_events > 0 else 0,
        "avg_sv_count": round(avg_sv, 2),
        "avg_pv_count": round(avg_pv, 2),
        "avg_alarm_count": round(avg_alarm, 2)
    }
