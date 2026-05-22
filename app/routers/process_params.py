"""
工艺参数追溯 API 路由
功能：查询、提取和展示工艺参数相关历史数据
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, and_
from typing import Optional, List
from datetime import datetime
import csv
import io
import json

from app.database import get_db
from app.models.process_params import ProcessParameter
from app.schemas.process_params import (
    ProcessParamQuery, ProcessParamList, ProcessParam,
    ProcessParamStats, ProcessParamTrend
)

router = APIRouter()


@router.get("/", response_model=ProcessParamList)
async def list_process_params(
    query: ProcessParamQuery = Depends(),
    db: Session = Depends(get_db)
):
    """
    查询工艺参数列表（支持多条件组合查询）
    
    查询条件包括：
    - 时间范围：start_time, end_time
    - 工艺类型：process_type
    - 设备编号：machine_id
    - 产品型号：product_model
    - 参数名称：param_name
    - 参数值范围：param_value_min, param_value_max
    """
    db_query = db.query(ProcessParameter)
    
    # 时间范围筛选
    if query.start_time:
        db_query = db_query.filter(ProcessParameter.create_time >= query.start_time)
    if query.end_time:
        db_query = db_query.filter(ProcessParameter.create_time <= query.end_time)
    
    # 工艺类型筛选
    if query.process_type:
        db_query = db_query.filter(ProcessParameter.process_type == query.process_type)
    
    # 设备编号筛选
    if query.machine_id:
        db_query = db_query.filter(ProcessParameter.machine_id == query.machine_id)
    
    # 产品型号筛选
    if query.product_model:
        db_query = db_query.filter(ProcessParameter.product_model == query.product_model)
    
    # 参数名称筛选
    if query.param_name:
        db_query = db_query.filter(ProcessParameter.param_name.contains(query.param_name))
    
    # 参数值范围筛选
    if query.param_value_min is not None:
        db_query = db_query.filter(ProcessParameter.param_value >= query.param_value_min)
    if query.param_value_max is not None:
        db_query = db_query.filter(ProcessParameter.param_value <= query.param_value_max)
    
    # 启动码筛选
    if query.start_code:
        db_query = db_query.filter(ProcessParameter.start_code == query.start_code)
    
    # 工艺编号筛选
    if query.process_no:
        db_query = db_query.filter(ProcessParameter.process_no == query.process_no)
    
    # 获取总数
    total = db_query.count()
    
    # 分页和排序
    offset = (query.page - 1) * query.page_size
    items = db_query.order_by(desc(ProcessParameter.create_time)).offset(offset).limit(query.page_size).all()
    
    return {"total": total, "items": items}


@router.get("/stats", response_model=ProcessParamStats)
async def get_process_param_stats(
    query: ProcessParamQuery = Depends(),
    db: Session = Depends(get_db)
):
    """
    获取工艺参数统计信息
    
    返回：
    - 总记录数
    - 参数平均值
    - 参数最大值
    - 参数最小值
    - 不同设备数量
    - 不同工艺类型数量
    """
    db_query = db.query(ProcessParameter)
    
    # 应用筛选条件
    if query.start_time:
        db_query = db_query.filter(ProcessParameter.create_time >= query.start_time)
    if query.end_time:
        db_query = db_query.filter(ProcessParameter.create_time <= query.end_time)
    if query.process_type:
        db_query = db_query.filter(ProcessParameter.process_type == query.process_type)
    if query.machine_id:
        db_query = db_query.filter(ProcessParameter.machine_id == query.machine_id)
    if query.product_model:
        db_query = db_query.filter(ProcessParameter.product_model == query.product_model)
    if query.param_name:
        db_query = db_query.filter(ProcessParameter.param_name.contains(query.param_name))
    if query.start_code:
        db_query = db_query.filter(ProcessParameter.start_code == query.start_code)
    if query.process_no:
        db_query = db_query.filter(ProcessParameter.process_no == query.process_no)
    
    # 统计信息
    total = db_query.count()
    
    if total > 0:
        avg_value = db_query.with_entities(func.avg(ProcessParameter.param_value)).scalar()
        max_value = db_query.with_entities(func.max(ProcessParameter.param_value)).scalar()
        min_value = db_query.with_entities(func.min(ProcessParameter.param_value)).scalar()
        machine_count = db_query.with_entities(func.count(func.distinct(ProcessParameter.machine_id))).scalar()
        process_type_count = db_query.with_entities(func.count(func.distinct(ProcessParameter.process_type))).scalar()
    else:
        avg_value = max_value = min_value = 0
        machine_count = process_type_count = 0
    
    return {
        "total": total,
        "avg_value": round(float(avg_value), 2) if avg_value else 0,
        "max_value": round(float(max_value), 2) if max_value else 0,
        "min_value": round(float(min_value), 2) if min_value else 0,
        "machine_count": machine_count,
        "process_type_count": process_type_count
    }


@router.get("/trend", response_model=List[ProcessParamTrend])
async def get_process_param_trend(
    param_name: str = Query(..., description="参数名称"),
    machine_id: Optional[str] = Query(None, description="设备编号"),
    start_time: Optional[datetime] = Query(None, description="开始时间"),
    end_time: Optional[datetime] = Query(None, description="结束时间"),
    process_type: Optional[str] = Query(None, description="工艺类型"),
    interval: str = Query("hour", description="时间间隔：minute, hour, day"),
    db: Session = Depends(get_db)
):
    """
    获取工艺参数趋势数据（用于图表展示）
    
    支持按不同时间间隔聚合数据
    """
    db_query = db.query(ProcessParameter)
    
    # 基础筛选
    db_query = db_query.filter(ProcessParameter.param_name == param_name)
    
    if machine_id:
        db_query = db_query.filter(ProcessParameter.machine_id == machine_id)
    if start_time:
        db_query = db_query.filter(ProcessParameter.create_time >= start_time)
    if end_time:
        db_query = db_query.filter(ProcessParameter.create_time <= end_time)
    if process_type:
        db_query = db_query.filter(ProcessParameter.process_type == process_type)
    
    # 按时间间隔分组统计
    if interval == "minute":
        time_format = "%Y-%m-%d %H:%i"
    elif interval == "hour":
        time_format = "%Y-%m-%d %H:00"
    else:  # day
        time_format = "%Y-%m-%d"
    
    # 使用 SQLAlchemy 的 func 进行时间格式化
    from sqlalchemy import text
    time_expr = func.date_format(ProcessParameter.create_time, time_format)
    
    trend_data = db_query.with_entities(
        time_expr.label("time_point"),
        func.avg(ProcessParameter.param_value).label("avg_value"),
        func.max(ProcessParameter.param_value).label("max_value"),
        func.min(ProcessParameter.param_value).label("min_value"),
        func.count().label("count")
    ).group_by(time_expr).order_by(time_expr).all()
    
    return [
        {
            "time_point": row[0],
            "avg_value": round(float(row[1]), 2) if row[1] else 0,
            "max_value": round(float(row[2]), 2) if row[2] else 0,
            "min_value": round(float(row[3]), 2) if row[3] else 0,
            "count": row[4]
        }
        for row in trend_data
    ]


@router.get("/export")
async def export_process_params(
    query: ProcessParamQuery = Depends(),
    db: Session = Depends(get_db)
):
    """
    导出工艺参数数据为 CSV 格式
    
    支持所有查询条件，导出筛选后的全部数据
    """
    db_query = db.query(ProcessParameter)
    
    # 应用所有筛选条件
    if query.start_time:
        db_query = db_query.filter(ProcessParameter.create_time >= query.start_time)
    if query.end_time:
        db_query = db_query.filter(ProcessParameter.create_time <= query.end_time)
    if query.process_type:
        db_query = db_query.filter(ProcessParameter.process_type == query.process_type)
    if query.machine_id:
        db_query = db_query.filter(ProcessParameter.machine_id == query.machine_id)
    if query.product_model:
        db_query = db_query.filter(ProcessParameter.product_model == query.product_model)
    if query.param_name:
        db_query = db_query.filter(ProcessParameter.param_name.contains(query.param_name))
    if query.param_value_min is not None:
        db_query = db_query.filter(ProcessParameter.param_value >= query.param_value_min)
    if query.param_value_max is not None:
        db_query = db_query.filter(ProcessParameter.param_value <= query.param_value_max)
    if query.start_code:
        db_query = db_query.filter(ProcessParameter.start_code == query.start_code)
    if query.process_no:
        db_query = db_query.filter(ProcessParameter.process_no == query.process_no)
    
    # 获取所有数据
    items = db_query.order_by(desc(ProcessParameter.create_time)).all()
    
    # 创建 CSV 文件
    output = io.StringIO()
    writer = csv.writer(output)
    
    # 写入表头
    writer.writerow([
        'ID', '创建时间', '工艺类型', '设备编号', '产品型号',
        '参数名称', '参数值', '单位', '启动码', '工艺编号',
        '批次号', '操作员', '备注'
    ])
    
    # 写入数据
    for item in items:
        writer.writerow([
            item.id,
            item.create_time.strftime('%Y-%m-%d %H:%M:%S') if item.create_time else '',
            item.process_type or '',
            item.machine_id or '',
            item.product_model or '',
            item.param_name or '',
            item.param_value if item.param_value is not None else '',
            item.unit or '',
            item.start_code or '',
            item.process_no or '',
            item.batch_no or '',
            item.operator or '',
            item.remark or ''
        ])
    
    # 生成响应
    output.seek(0)
    # 使用英文文件名避免编码问题
    filename = f"process_params_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    return Response(
        content=output.getvalue(),
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )


@router.get("/{param_id}", response_model=ProcessParam)
async def get_process_param(param_id: int, db: Session = Depends(get_db)):
    """根据 ID 查询工艺参数详情"""
    param = db.query(ProcessParameter).filter(ProcessParameter.id == param_id).first()
    if not param:
        raise HTTPException(status_code=404, detail="工艺参数记录不存在")
    return param


@router.get("/machine/{machine_id}/params", response_model=ProcessParamList)
async def get_machine_params(
    machine_id: str,
    query: ProcessParamQuery = Depends(),
    db: Session = Depends(get_db)
):
    """查询指定设备的工艺参数"""
    db_query = db.query(ProcessParameter).filter(ProcessParameter.machine_id == machine_id)
    
    if query.start_time:
        db_query = db_query.filter(ProcessParameter.create_time >= query.start_time)
    if query.end_time:
        db_query = db_query.filter(ProcessParameter.create_time <= query.end_time)
    if query.process_type:
        db_query = db_query.filter(ProcessParameter.process_type == query.process_type)
    
    total = db_query.count()
    
    offset = (query.page - 1) * query.page_size
    items = db_query.order_by(desc(ProcessParameter.create_time)).offset(offset).limit(query.page_size).all()
    
    return {"total": total, "items": items}


@router.get("/process-type/{process_type}/params", response_model=ProcessParamList)
async def get_process_type_params(
    process_type: str,
    query: ProcessParamQuery = Depends(),
    db: Session = Depends(get_db)
):
    """查询指定工艺类型的参数"""
    db_query = db.query(ProcessParameter).filter(ProcessParameter.process_type == process_type)
    
    if query.start_time:
        db_query = db_query.filter(ProcessParameter.create_time >= query.start_time)
    if query.end_time:
        db_query = db_query.filter(ProcessParameter.create_time <= query.end_time)
    if query.machine_id:
        db_query = db_query.filter(ProcessParameter.machine_id == query.machine_id)
    
    total = db_query.count()
    
    offset = (query.page - 1) * query.page_size
    items = db_query.order_by(desc(ProcessParameter.create_time)).offset(offset).limit(query.page_size).all()
    
    return {"total": total, "items": items}
