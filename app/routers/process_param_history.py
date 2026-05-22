"""
工艺参数变更历史 API
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List

from app.database import get_db
from app.models.process_param_history import ProcessParamHistory
from app.schemas.process_param_history import (
    ProcessParamHistoryCreate,
    ProcessParamHistoryBatchCreate,
    ProcessParamHistoryResponse,
    ProcessParamHistoryListResponse,
)

router = APIRouter()


@router.post("/", response_model=ProcessParamHistoryResponse)
def create_history(data: ProcessParamHistoryCreate, db: Session = Depends(get_db)):
    record = ProcessParamHistory(
        process_id=data.process_id,
        change_type=data.change_type,
        param_name=data.param_name,
        old_value=data.old_value,
        new_value=data.new_value,
        source=data.source,
        operator=data.operator,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.post("/batch")
def batch_create_history(data: ProcessParamHistoryBatchCreate, db: Session = Depends(get_db)):
    records = []
    for item in data.items:
        record = ProcessParamHistory(
            process_id=item.process_id,
            change_type=item.change_type,
            param_name=item.param_name,
            old_value=item.old_value,
            new_value=item.new_value,
            source=item.source,
            operator=item.operator,
        )
        db.add(record)
        records.append(record)
    db.commit()
    return {"message": f"记录 {len(records)} 条历史", "count": len(records)}


@router.get("/{process_id}", response_model=ProcessParamHistoryListResponse)
def list_history(
    process_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    change_type: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(ProcessParamHistory).filter(
        ProcessParamHistory.process_id == process_id
    )
    if change_type:
        query = query.filter(ProcessParamHistory.change_type == change_type)

    total = query.count()
    items = query.order_by(ProcessParamHistory.created_at.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()

    return ProcessParamHistoryListResponse(total=total, items=items)
