"""
订单加工记录 API 路由
管理本地订单加工记录（区别于 ERP U9 订单）
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, func
from typing import Optional, List
from datetime import datetime

from app.database import get_db
from app.models.order_processing_record import OrderProcessingRecord
from app.models.device import Device
from app.schemas.order_processing_record import (
    OrderProcessingRecordCreate,
    OrderProcessingRecordUpdate,
    OrderProcessingRecordDetail,
    OrderProcessingRecordList,
    OrderProcessingStats,
)

router = APIRouter(prefix="/order-processing-records", tags=["订单加工记录"])


def _today_str() -> str:
    return datetime.now().strftime('%Y-%m-%d')


@router.get("/", response_model=OrderProcessingRecordList)
async def list_records(
    device_code: Optional[str] = Query(None, description="设备编号"),
    record_date: Optional[str] = Query(None, description="记录日期 YYYY-MM-DD"),
    status: Optional[str] = Query(None, description="状态筛选"),
    part_number: Optional[str] = Query(None, description="零件号"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db)
):
    """列表查询订单加工记录"""
    query = db.query(OrderProcessingRecord)

    if device_code is not None:
        query = query.filter(OrderProcessingRecord.device_code == device_code)
    if record_date:
        query = query.filter(OrderProcessingRecord.record_date == record_date)
    if status:
        query = query.filter(OrderProcessingRecord.status == status)
    if part_number:
        query = query.filter(OrderProcessingRecord.part_number.ilike(f"%{part_number}%"))

    total = query.count()
    items = query.order_by(desc(OrderProcessingRecord.created_at)).offset(
        (page - 1) * page_size
    ).limit(page_size).all()

    return OrderProcessingRecordList(total=total, items=items)


@router.get("/today", response_model=OrderProcessingRecordList)
async def list_today_records(
    db: Session = Depends(get_db)
):
    """获取今日所有设备的加工记录"""
    today = _today_str()
    items = db.query(OrderProcessingRecord).filter(
        OrderProcessingRecord.record_date == today
    ).order_by(OrderProcessingRecord.device_code).all()

    return OrderProcessingRecordList(total=len(items), items=items)


@router.get("/device/{device_code}/today", response_model=List[OrderProcessingRecordDetail])
async def get_device_today_records(
    device_code: str,
    db: Session = Depends(get_db)
):
    """获取指定设备今日加工记录"""
    today = _today_str()
    items = db.query(OrderProcessingRecord).filter(
        OrderProcessingRecord.device_code == device_code,
        OrderProcessingRecord.record_date == today,
    ).order_by(desc(OrderProcessingRecord.start_time)).all()

    return items


@router.get("/stats", response_model=OrderProcessingStats)
async def get_stats(
    record_date: Optional[str] = Query(None, description="统计日期，默认今日"),
    device_code: Optional[str] = Query(None, description="设备编号"),
    db: Session = Depends(get_db)
):
    """获取订单加工统计"""
    date_str = record_date or _today_str()
    query = db.query(OrderProcessingRecord).filter(
        OrderProcessingRecord.record_date == date_str
    )
    if device_code is not None:
        query = query.filter(OrderProcessingRecord.device_code == device_code)

    records = query.all()
    total = len(records)
    in_progress = sum(1 for r in records if r.status == 'in_progress')
    completed = sum(1 for r in records if r.status == 'completed')
    paused = sum(1 for r in records if r.status == 'paused')
    total_planned = sum(r.planned_qty or 0 for r in records)
    total_completed = sum(r.completed_qty or 0 for r in records)
    total_eligible = sum(r.eligible_qty or 0 for r in records)
    total_scrap = sum(r.scrap_qty or 0 for r in records)
    rate = round(total_completed / total_planned * 100, 1) if total_planned > 0 else 0.0

    return OrderProcessingStats(
        total_records=total,
        in_progress=in_progress,
        completed=completed,
        paused=paused,
        total_planned=total_planned,
        total_completed=total_completed,
        total_eligible=total_eligible,
        total_scrap=total_scrap,
        overall_completion_rate=rate,
    )


@router.post("/", response_model=OrderProcessingRecordDetail)
async def create_record(
    record: OrderProcessingRecordCreate,
    db: Session = Depends(get_db)
):
    """创建订单加工记录"""
    device = db.query(Device).filter(Device.device_code == record.device_code).first()
    if not device:
        raise HTTPException(status_code=404, detail="设备不存在")

    date_str = _today_str()

    db_record = OrderProcessingRecord(
        device_code=record.device_code,
        part_number=record.part_number,
        u9_material_code=record.u9_material_code,
        doc_no=record.doc_no,
        planned_qty=record.planned_qty,
        completed_qty=record.completed_qty or 0,
        eligible_qty=record.eligible_qty or 0,
        scrap_qty=record.scrap_qty or 0,
        status=record.status or 'in_progress',
        start_time=record.start_time or datetime.now(),
        record_date=date_str,
        notes=record.notes,
    )

    db.add(db_record)
    db.commit()
    db.refresh(db_record)

    return db_record


@router.put("/{record_id}", response_model=OrderProcessingRecordDetail)
async def update_record(
    record_id: int,
    record: OrderProcessingRecordUpdate,
    db: Session = Depends(get_db)
):
    """更新订单加工记录"""
    db_record = db.query(OrderProcessingRecord).filter(
        OrderProcessingRecord.id == record_id
    ).first()

    if not db_record:
        raise HTTPException(status_code=404, detail="记录不存在")

    update_data = record.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_record, key, value)

    db.commit()
    db.refresh(db_record)

    return db_record


@router.post("/{record_id}/complete", response_model=OrderProcessingRecordDetail)
async def complete_record(
    record_id: int,
    db: Session = Depends(get_db)
):
    """标记订单加工记录为完成"""
    db_record = db.query(OrderProcessingRecord).filter(
        OrderProcessingRecord.id == record_id
    ).first()

    if not db_record:
        raise HTTPException(status_code=404, detail="记录不存在")

    db_record.status = 'completed'
    db_record.end_time = datetime.now()

    db.commit()
    db.refresh(db_record)

    return db_record


@router.delete("/{record_id}")
async def delete_record(
    record_id: int,
    db: Session = Depends(get_db)
):
    """删除订单加工记录"""
    db_record = db.query(OrderProcessingRecord).filter(
        OrderProcessingRecord.id == record_id
    ).first()

    if not db_record:
        raise HTTPException(status_code=404, detail="记录不存在")

    db.delete(db_record)
    db.commit()

    return {"message": "删除成功"}
