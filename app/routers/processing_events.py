"""
产品加工信息追溯 API 路由
功能：查询产品加工历史、追溯加工过程信息
基于 event_data 表（加工事件数据表）
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, and_, or_
from typing import Optional, List
from datetime import datetime
import csv
import io

from app.database import get_db
from app.models.event_data import EventData
from app.schemas.processing_events import (
    ProcessingEventQuery, ProcessingEventList, ProcessingEventDetail,
    ProcessingEventStats, ProcessingEventTrend
)

router = APIRouter()


@router.get("/", response_model=ProcessingEventList)
async def list_processing_events(
    query: ProcessingEventQuery = Depends(),
    db: Session = Depends(get_db)
):
    """
    查询产品加工事件列表（支持多条件组合查询）
    
    查询条件包括：
    - 时间范围：start_time, end_time
    - 启动码：start_code
    - 表皮码：skin_code
    - 设备编号：machine_id
    - 操作员：operator_id, operator_name
    - 集团/工厂：group_code, factory_code
    - 工艺编号：process_no
    """
    db_query = db.query(EventData)
    
    # 时间范围筛选（将 datetime 转换为毫秒时间戳）
    if query.start_time:
        start_timestamp = int(query.start_time.timestamp() * 1000)
        db_query = db_query.filter(EventData.start_time >= start_timestamp)
    if query.end_time:
        end_timestamp = int(query.end_time.timestamp() * 1000)
        db_query = db_query.filter(EventData.end_time <= end_timestamp)
    
    # 启动码筛选（支持模糊查询）
    if query.start_code:
        db_query = db_query.filter(EventData.start_code.contains(query.start_code))
    
    # 表皮码筛选
    if query.skin_code:
        db_query = db_query.filter(EventData.skin_code.contains(query.skin_code))
    
    # 设备编号筛选
    if query.machine_id:
        db_query = db_query.filter(EventData.machine_id == query.machine_id)
    
    # 操作员筛选
    if query.operator_id:
        db_query = db_query.filter(EventData.operator_id == query.operator_id)
    if query.operator_name:
        db_query = db_query.filter(EventData.operator_name.contains(query.operator_name))
    
    # 集团/工厂筛选
    if query.group_code:
        db_query = db_query.filter(EventData.group_code == query.group_code)
    if query.factory_code:
        db_query = db_query.filter(EventData.factory_code == query.factory_code)
    
    # 工艺编号筛选
    if query.process_no:
        db_query = db_query.filter(EventData.process_no == query.process_no)
    
    # 产线筛选
    if query.line_code:
        db_query = db_query.filter(EventData.line_code == query.line_code)
    
    # 获取总数
    total = db_query.count()
    
    # 分页和排序
    offset = (query.page - 1) * query.page_size
    items = db_query.order_by(desc(EventData.start_time)).offset(offset).limit(query.page_size).all()
    
    return {"total": total, "items": items}


@router.get("/stats", response_model=ProcessingEventStats)
async def get_processing_event_stats(
    start_time: Optional[datetime] = Query(None, description="开始时间"),
    end_time: Optional[datetime] = Query(None, description="结束时间"),
    machine_id: Optional[str] = Query(None, description="设备编号"),
    group_code: Optional[str] = Query(None, description="集团编码"),
    factory_code: Optional[str] = Query(None, description="工厂编码"),
    db: Session = Depends(get_db)
):
    """
    获取产品加工统计信息
    """
    db_query = db.query(EventData)
    
    # 应用筛选条件（将 datetime 转换为毫秒时间戳）
    if start_time:
        start_timestamp = int(start_time.timestamp() * 1000)
        db_query = db_query.filter(EventData.start_time >= start_timestamp)
    if end_time:
        end_timestamp = int(end_time.timestamp() * 1000)
        db_query = db_query.filter(EventData.start_time <= end_timestamp)
    if machine_id:
        db_query = db_query.filter(EventData.machine_id == machine_id)
    if group_code:
        db_query = db_query.filter(EventData.group_code == group_code)
    if factory_code:
        db_query = db_query.filter(EventData.factory_code == factory_code)
    
    # 统计总数
    total = db_query.count()
    
    # 统计平均加工时长
    avg_duringtime = db_query.with_entities(func.avg(EventData.duringtime)).scalar()
    
    # 统计平均机器工作时间
    avg_machine_duringtime = db_query.with_entities(func.avg(EventData.machine_duringtime)).scalar()
    
    # 统计设备数量
    machine_count = db_query.with_entities(func.count(func.distinct(EventData.machine_id))).scalar()
    
    # 统计操作员数量
    operator_count = db_query.with_entities(func.count(func.distinct(EventData.operator_id))).scalar()
    
    # 统计产线数量
    line_count = db_query.with_entities(func.count(func.distinct(EventData.line_code))).scalar()
    
    return {
        "total": total,
        "avg_duringtime": round(float(avg_duringtime), 2) if avg_duringtime else 0,
        "avg_machine_duringtime": round(float(avg_machine_duringtime), 2) if avg_machine_duringtime else 0,
        "machine_count": machine_count,
        "operator_count": operator_count,
        "line_count": line_count
    }


@router.get("/trend", response_model=List[ProcessingEventTrend])
async def get_processing_event_trend(
    interval: str = Query("hour", description="时间间隔：minute, hour, day"),
    machine_id: Optional[str] = Query(None, description="设备编号"),
    start_time: Optional[datetime] = Query(None, description="开始时间"),
    end_time: Optional[datetime] = Query(None, description="结束时间"),
    db: Session = Depends(get_db)
):
    """
    获取加工事件趋势数据（用于图表展示）
    """
    from sqlalchemy import case
    
    db_query = db.query(EventData)
    
    if machine_id:
        db_query = db_query.filter(EventData.machine_id == machine_id)
    if start_time:
        start_timestamp = int(start_time.timestamp() * 1000)
        db_query = db_query.filter(EventData.start_time >= start_timestamp)
    if end_time:
        end_timestamp = int(end_time.timestamp() * 1000)
        db_query = db_query.filter(EventData.start_time <= end_timestamp)
    
    # 获取所有数据
    events = db_query.with_entities(
        EventData.start_time,
        EventData.duringtime,
        EventData.machine_duringtime
    ).all()
    
    # 在 Python 中按时间间隔分组
    from collections import defaultdict
    grouped_data = defaultdict(lambda: {"count": 0, "total_duration": 0, "total_machine_duration": 0})
    
    for event in events:
        # 将毫秒时间戳转换为 datetime
        dt = datetime.fromtimestamp(event.start_time / 1000)
        
        # 按时间间隔格式化
        if interval == "minute":
            time_point = dt.strftime("%Y-%m-%d %H:%M")
        elif interval == "hour":
            time_point = dt.strftime("%Y-%m-%d %H:00")
        else:  # day
            time_point = dt.strftime("%Y-%m-%d")
        
        grouped_data[time_point]["count"] += 1
        if event.duringtime:
            grouped_data[time_point]["total_duration"] += event.duringtime
        if event.machine_duringtime:
            grouped_data[time_point]["total_machine_duration"] += event.machine_duringtime
    
    # 转换为列表并计算平均值
    result = []
    for time_point in sorted(grouped_data.keys()):
        data = grouped_data[time_point]
        count = data["count"]
        avg_duration = round(data["total_duration"] / count, 2) if count > 0 and data["total_duration"] > 0 else 0
        avg_machine_duration = round(data["total_machine_duration"] / count, 2) if count > 0 and data["total_machine_duration"] > 0 else 0
        
        result.append({
            "time_point": time_point,
            "event_count": count,
            "avg_duringtime": avg_duration,
            "avg_machine_duringtime": avg_machine_duration
        })
    
    return result


@router.get("/export")
async def export_processing_events(
    query: ProcessingEventQuery = Depends(),
    db: Session = Depends(get_db)
):
    """
    导出产品加工事件数据为 CSV 格式
    """
    from fastapi.responses import Response
    
    db_query = db.query(EventData)
    
    # 应用所有筛选条件（将 datetime 转换为毫秒时间戳）
    if query.start_time:
        start_timestamp = int(query.start_time.timestamp() * 1000)
        db_query = db_query.filter(EventData.start_time >= start_timestamp)
    if query.end_time:
        end_timestamp = int(query.end_time.timestamp() * 1000)
        db_query = db_query.filter(EventData.end_time <= end_timestamp)
    if query.start_code:
        db_query = db_query.filter(EventData.start_code.contains(query.start_code))
    if query.skin_code:
        db_query = db_query.filter(EventData.skin_code.contains(query.skin_code))
    if query.machine_id:
        db_query = db_query.filter(EventData.machine_id == query.machine_id)
    if query.operator_id:
        db_query = db_query.filter(EventData.operator_id == query.operator_id)
    if query.group_code:
        db_query = db_query.filter(EventData.group_code == query.group_code)
    if query.factory_code:
        db_query = db_query.filter(EventData.factory_code == query.factory_code)
    if query.process_no:
        db_query = db_query.filter(EventData.process_no == query.process_no)
    
    # 获取所有数据
    items = db_query.order_by(desc(EventData.start_time)).all()
    
    # 创建 CSV 文件
    output = io.StringIO()
    writer = csv.writer(output)
    
    # 写入表头
    writer.writerow([
        'ID', '事件 UID', '启动码', '表皮码', '开始时间', '结束时间',
        '加工时长 (ms)', '机器工作时间 (ms)', '设备 ID', '操作员 ID',
        '操作员姓名', '集团编码', '工厂编码', '产线编码', '工艺编号'
    ])
    
    # 写入数据
    for item in items:
        # 将毫秒时间戳转换为 datetime
        start_time = datetime.fromtimestamp(item.start_time / 1000) if item.start_time else None
        end_time = datetime.fromtimestamp(item.end_time / 1000) if item.end_time else None
        
        writer.writerow([
            item.id,
            item.event_uid,
            item.start_code,
            item.skin_code or '',
            start_time.strftime('%Y-%m-%d %H:%M:%S') if start_time else '',
            end_time.strftime('%Y-%m-%d %H:%M:%S') if end_time else '',
            item.duringtime or '',
            item.machine_duringtime or '',
            item.machine_id or '',
            item.operator_id or '',
            item.operator_name or '',
            item.group_code or '',
            item.factory_code or '',
            item.line_code or '',
            item.process_no or ''
        ])
    
    # 生成响应
    output.seek(0)
    filename = f"processing_events_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    return Response(
        content=output.getvalue(),
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )


@router.get("/{event_id}", response_model=ProcessingEventDetail)
async def get_processing_event(event_id: int, db: Session = Depends(get_db)):
    """根据 ID 查询产品加工事件详情"""
    event = db.query(EventData).filter(EventData.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="加工事件记录不存在")
    return event


@router.get("/start-code/{start_code}", response_model=ProcessingEventDetail)
async def get_event_by_start_code(start_code: str, db: Session = Depends(get_db)):
    """根据启动码查询产品加工事件"""
    event = db.query(EventData).filter(EventData.start_code == start_code).first()
    if not event:
        raise HTTPException(status_code=404, detail="加工事件记录不存在")
    return event
