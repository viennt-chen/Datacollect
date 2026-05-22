"""
数据采集管理 API 路由
功能：管理 MQTT 数据采集服务
基于 event_data 表（加工事件数据表）
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import Optional, List
from datetime import datetime, timedelta
import threading

from app.database import get_db
from app.models.event_data import EventData
from app.models.raw_data_block import RawDataBlock
from app.services.mqtt_collector import get_collector, MQTTDataCollector
from app.schemas.mqtt_collector import (
    CollectorStats, CollectorConfig, CollectorAction,
    ProcessingEventStats, RawDataStats
)

router = APIRouter(tags=["数据采集管理"])


@router.get("/stats", response_model=CollectorStats)
async def get_collector_stats():
    """
    获取采集器状态统计

    Returns:
        采集器运行状态和统计信息
    """
    collector = get_collector()
    stats = collector.get_stats()

    return CollectorStats(**stats)


@router.post("/control")
async def control_collector(action: CollectorAction):
    """
    控制采集器（启动/停止）

    Args:
        action: 控制动作（start/stop）

    Returns:
        操作结果
    """
    collector = get_collector()

    if action.action == "start":
        if collector.running:
            raise HTTPException(status_code=400, detail="采集服务已在运行")

        # 在后台线程启动采集服务
        thread = threading.Thread(target=collector.start, daemon=True)
        thread.start()

        return {"message": "采集服务启动中", "status": "starting"}

    elif action.action == "stop":
        if not collector.running:
            raise HTTPException(status_code=400, detail="采集服务未运行")

        collector.stop()
        return {"message": "采集服务已停止", "status": "stopped"}

    else:
        raise HTTPException(status_code=400, detail="无效的操作")


@router.get("/events/stats", response_model=ProcessingEventStats)
async def get_event_stats(
    days: int = 7,
    db: Session = Depends(get_db)
):
    """
    获取加工事件统计信息

    Args:
        days: 统计天数

    Returns:
        加工事件统计信息
    """
    cutoff_time = datetime.now() - timedelta(days=days)
    cutoff_timestamp = int(cutoff_time.timestamp() * 1000)

    total = db.query(EventData).filter(
        EventData.start_time >= cutoff_timestamp
    ).count()

    result = db.query(
        func.count(EventData.id).label('count'),
        func.avg(EventData.duringtime).label('avg_duringtime'),
        func.avg(EventData.machine_duringtime).label('avg_machine_duringtime'),
        func.count(func.distinct(EventData.machine_id)).label('machine_count'),
        func.count(func.distinct(EventData.operator_id)).label('operator_count')
    ).filter(
        EventData.start_time >= cutoff_timestamp
    ).first()

    return ProcessingEventStats(
        total=total,
        avg_duringtime=result.avg_duringtime or 0,
        avg_machine_duringtime=result.avg_machine_duringtime or 0,
        machine_count=result.machine_count or 0,
        operator_count=result.operator_count or 0,
        period_days=days
    )


@router.get("/raw-data/stats", response_model=RawDataStats)
async def get_raw_data_stats(
    days: int = 7,
    db: Session = Depends(get_db)
):
    """
    获取原始数据块统计信息

    Args:
        days: 统计天数

    Returns:
        原始数据块统计信息
    """
    cutoff_time = datetime.now() - timedelta(days=days)

    total = db.query(RawDataBlock).filter(
        RawDataBlock.timestamp_ms >= int(cutoff_time.timestamp() * 1000)
    ).count()

    result = db.query(
        RawDataBlock.topic,
        func.count(RawDataBlock.id).label('count'),
        func.avg(func.length(RawDataBlock.compressed_payload)).label('avg_size')
    ).filter(
        RawDataBlock.timestamp_ms >= int(cutoff_time.timestamp() * 1000)
    ).group_by(RawDataBlock.topic).all()

    topic_stats = {
        item.topic: {
            'count': item.count,
            'avg_size': float(item.avg_size) if item.avg_size else 0
        }
        for item in result
    }

    return RawDataStats(
        total=total,
        topic_stats=topic_stats,
        period_days=days
    )


@router.get("/recent-events")
async def get_recent_events(
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """
    获取最近的加工事件

    Args:
        limit: 返回数量限制

    Returns:
        最近的加工事件列表
    """
    events = db.query(EventData).order_by(
        desc(EventData.start_time)
    ).limit(limit).all()

    return {
        "total": len(events),
        "items": events
    }


@router.get("/config", response_model=CollectorConfig)
async def get_collector_config():
    """
    获取采集器配置信息

    Returns:
        采集器配置信息
    """
    collector = get_collector()

    return CollectorConfig(
        mqtt_server=collector.config.broker_host,
        mqtt_port=collector.config.broker_port,
        mqtt_user=collector.config.username or "",
        topics=collector.config.topics or []
    )
