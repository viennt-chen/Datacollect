"""
质量管理 API 路由
功能：质量记录的增删改查、统计分析、缺陷类型管理
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, extract
from typing import Optional, List
from datetime import datetime, timedelta
import io
import csv

from app.database import get_db
from app.models.quality_record import QualityRecord
from app.models.event_data import EventData
from sqlalchemy import or_
from app.schemas.quality_record import (
    QualityRecordCreate,
    QualityRecordUpdate,
    QualityRecordResponse,
    QualityRecordListResponse,
    QualityStatsResponse,
)

router = APIRouter(prefix="/quality-records", tags=["质量管理"])


@router.get("/", response_model=QualityRecordListResponse)
def list_quality_records(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    product_code: Optional[str] = None,
    device_code: Optional[str] = None,
    status: Optional[str] = None,
    defect_type: Optional[str] = None,
    inspector: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """获取质量记录列表"""
    query = db.query(QualityRecord)

    if start_time:
        query = query.filter(QualityRecord.inspect_time >= start_time)
    if end_time:
        query = query.filter(QualityRecord.inspect_time <= end_time)
    if product_code:
        query = query.filter(QualityRecord.product_code.contains(product_code))
    if device_code:
        query = query.filter(QualityRecord.device_code.contains(device_code))
    if status:
        query = query.filter(QualityRecord.status == status)
    if defect_type:
        query = query.filter(QualityRecord.defect_type == defect_type)
    if inspector:
        query = query.filter(QualityRecord.inspector.contains(inspector))

    total = query.count()
    items = query.order_by(desc(QualityRecord.created_at)).offset((page - 1) * page_size).limit(page_size).all()

    return QualityRecordListResponse(total=total, data=items)


@router.get("/stats", response_model=QualityStatsResponse)
def get_quality_stats(
    group_by: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    db: Session = Depends(get_db),
):
    """获取质量统计信息"""
    query = db.query(QualityRecord)

    if start_time:
        query = query.filter(QualityRecord.inspect_time >= start_time)
    if end_time:
        query = query.filter(QualityRecord.inspect_time <= end_time)

    total = query.count()
    passed = query.filter(QualityRecord.status == 'passed').count()
    failed = query.filter(QualityRecord.status == 'failed').count()
    pending = query.filter(QualityRecord.status == 'pending').count()

    # 今日统计
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today = query.filter(QualityRecord.created_at >= today_start).count()

    # 本周统计
    week_start = today_start - timedelta(days=datetime.now().weekday())
    week = query.filter(QualityRecord.created_at >= week_start).count()

    # 合格率
    pass_rate = round((passed / total * 100) if total > 0 else 0, 1)

    # 缺陷分布
    defect_distribution = []
    if group_by == 'defect_type':
        results = (
            db.query(
                QualityRecord.defect_type,
                func.count(QualityRecord.id).label('count')
            )
            .filter(QualityRecord.status == 'failed')
            .filter(QualityRecord.defect_type.isnot(None))
            .group_by(QualityRecord.defect_type)
            .order_by(desc('count'))
            .all()
        )
        defect_distribution = [
            {"defect_type": r.defect_type or "未知", "count": r.count}
            for r in results
        ]

    return QualityStatsResponse(
        total=total,
        passed=passed,
        failed=failed,
        pending=pending,
        today=today,
        week=week,
        passRate=pass_rate,
        defect_distribution=defect_distribution,
    )


@router.get("/defect-types")
def get_defect_types(db: Session = Depends(get_db)):
    """获取所有缺陷类型列表"""
    results = (
        db.query(QualityRecord.defect_type)
        .filter(QualityRecord.defect_type.isnot(None))
        .filter(QualityRecord.defect_type != '')
        .distinct()
        .all()
    )
    return [r.defect_type for r in results]


@router.get("/export")
def export_quality_records(
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    product_code: Optional[str] = None,
    device_code: Optional[str] = None,
    status: Optional[str] = None,
    defect_type: Optional[str] = None,
    inspector: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """导出质量记录为 CSV"""
    query = db.query(QualityRecord)

    if start_time:
        query = query.filter(QualityRecord.inspect_time >= start_time)
    if end_time:
        query = query.filter(QualityRecord.inspect_time <= end_time)
    if product_code:
        query = query.filter(QualityRecord.product_code.contains(product_code))
    if device_code:
        query = query.filter(QualityRecord.device_code.contains(device_code))
    if status:
        query = query.filter(QualityRecord.status == status)
    if defect_type:
        query = query.filter(QualityRecord.defect_type == defect_type)
    if inspector:
        query = query.filter(QualityRecord.inspector.contains(inspector))

    records = query.order_by(desc(QualityRecord.created_at)).all()

    # 生成 CSV
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        'ID', '产品编号', '产品名称', '设备编号', '检验状态',
        '缺陷类型', '缺陷描述', '检验员', '检验时间',
        '数量', '合格数', '不合格数', '备注', '创建时间'
    ])

    for r in records:
        writer.writerow([
            r.id, r.product_code, r.product_name, r.device_code,
            r.status, r.defect_type, r.defect_description,
            r.inspector, r.inspect_time,
            r.quantity, r.passed_quantity, r.failed_quantity,
            r.remark, r.created_at,
        ])

    output.seek(0)
    # 添加 BOM 以支持 Excel 打开中文
    bom_output = io.BytesIO()
    bom_output.write(b'\xef\xbb\xbf')
    bom_output.write(output.getvalue().encode('utf-8'))
    bom_output.seek(0)

    filename = f"质量记录_{datetime.now().strftime('%Y%m%d')}.csv"
    return StreamingResponse(
        bom_output,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/{record_id}", response_model=QualityRecordResponse)
def get_quality_record(record_id: int, db: Session = Depends(get_db)):
    """获取单条质量记录"""
    record = db.query(QualityRecord).filter(QualityRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="质量记录不存在")
    return record


@router.post("/", response_model=QualityRecordResponse)
def create_quality_record(data: QualityRecordCreate, db: Session = Depends(get_db)):
    """创建质量记录"""
    record = QualityRecord(**data.model_dump())
    if not record.inspect_time:
        record.inspect_time = datetime.now()
    # 自动计算合格/不合格数
    if record.status == 'passed':
        record.passed_quantity = record.quantity
    elif record.status == 'failed':
        record.failed_quantity = record.quantity

    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.put("/{record_id}", response_model=QualityRecordResponse)
def update_quality_record(record_id: int, data: QualityRecordUpdate, db: Session = Depends(get_db)):
    """更新质量记录"""
    record = db.query(QualityRecord).filter(QualityRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="质量记录不存在")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(record, key, value)

    record.updated_at = datetime.now()
    db.commit()
    db.refresh(record)
    return record


@router.delete("/{record_id}")
def delete_quality_record(record_id: int, db: Session = Depends(get_db)):
    """删除质量记录"""
    record = db.query(QualityRecord).filter(QualityRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="质量记录不存在")

    db.delete(record)
    db.commit()
    return {"message": "删除成功"}


@router.get("/{record_id}/events")
def get_record_events(
    record_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """获取质检记录关联的加工事件（通过设备编号+产品编号匹配）"""
    record = db.query(QualityRecord).filter(QualityRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="质量记录不存在")

    conditions = []
    if record.device_code:
        conditions.append(EventData.machine_id == record.device_code)
    if record.product_code:
        conditions.append(EventData.start_code == record.product_code)

    if not conditions:
        return {"total": 0, "items": [], "message": "无可用关联字段"}

    query = db.query(EventData).filter(or_(*conditions))

    # 限定时间范围
    if record.inspect_time:
        from datetime import timedelta
        time_start = record.inspect_time - timedelta(hours=24)
        time_end = record.inspect_time + timedelta(hours=24)
        ts_start = int(time_start.timestamp() * 1000)
        ts_end = int(time_end.timestamp() * 1000)
        query = query.filter(
            and_(
                EventData.start_time >= ts_start,
                EventData.start_time <= ts_end,
            )
        )

    total = query.count()
    items = query.order_by(EventData.start_time.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()

    return {
        "total": total,
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
            for e in items
        ],
    }
