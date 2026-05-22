"""物料订单查询日志 API 路由"""
import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.product_order_log import ProductOrderQueryLog
from app.schemas.product_order_log import (
    ProductOrderQueryLogResponse,
    ProductOrderQueryLogListResponse,
    ProductOrderQueryLogStats
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/product-order-logs", tags=["产品订单查询日志"])


@router.get("/", response_model=ProductOrderQueryLogListResponse)
def get_query_logs(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    part_number: Optional[str] = Query(None, description="零件号"),
    execution_type: Optional[str] = Query(None, description="执行类型"),
    status: Optional[str] = Query(None, description="状态"),
    start_date: Optional[str] = Query(None, description="开始日期"),
    end_date: Optional[str] = Query(None, description="结束日期"),
    db: Session = Depends(get_db)
):
    """获取查询日志列表"""
    query = db.query(ProductOrderQueryLog)
    
    if part_number:
        query = query.filter(ProductOrderQueryLog.part_number.contains(part_number))
    if execution_type:
        query = query.filter(ProductOrderQueryLog.execution_type == execution_type)
    if status:
        query = query.filter(ProductOrderQueryLog.status == status)
    if start_date:
        query = query.filter(ProductOrderQueryLog.query_date >= start_date)
    if end_date:
        query = query.filter(ProductOrderQueryLog.query_date <= end_date)
    
    total = query.count()
    
    logs = query.order_by(
        ProductOrderQueryLog.created_at.desc()
    ).offset((page - 1) * page_size).limit(page_size).all()
    
    return ProductOrderQueryLogListResponse(
        total=total,
        logs=[ProductOrderQueryLogResponse.model_validate(log) for log in logs]
    )


@router.get("/stats", response_model=ProductOrderQueryLogStats)
def get_query_logs_stats(
    start_date: Optional[str] = Query(None, description="开始日期"),
    end_date: Optional[str] = Query(None, description="结束日期"),
    db: Session = Depends(get_db)
):
    """获取查询日志统计信息"""
    query = db.query(ProductOrderQueryLog)
    
    if start_date:
        query = query.filter(ProductOrderQueryLog.query_date >= start_date)
    if end_date:
        query = query.filter(ProductOrderQueryLog.query_date <= end_date)
    
    total_queries = query.count()
    
    success_count = query.filter(
        ProductOrderQueryLog.status == "success"
    ).count()
    
    failed_count = query.filter(
        ProductOrderQueryLog.status == "failed"
    ).count()
    
    total_saved_result = query.with_entities(
        func.sum(ProductOrderQueryLog.saved_count)
    ).scalar() or 0
    
    avg_duration_result = query.with_entities(
        func.avg(ProductOrderQueryLog.duration_seconds)
    ).scalar()
    
    return ProductOrderQueryLogStats(
        total_queries=total_queries,
        success_count=success_count,
        failed_count=failed_count,
        total_saved=total_saved_result,
        avg_duration=round(avg_duration_result, 2) if avg_duration_result else None
    )


@router.get("/{log_id}", response_model=ProductOrderQueryLogResponse)
def get_query_log(
    log_id: int,
    db: Session = Depends(get_db)
):
    """获取单条查询日志"""
    log = db.query(ProductOrderQueryLog).filter(
        ProductOrderQueryLog.id == log_id
    ).first()
    
    if not log:
        raise HTTPException(status_code=404, detail="日志不存在")
    
    return ProductOrderQueryLogResponse.model_validate(log)


@router.delete("/clear")
def clear_query_logs(
    days: Optional[int] = Query(None, ge=1, description="保留最近 N 天的数据"),
    db: Session = Depends(get_db)
):
    """清空查询日志"""
    from datetime import datetime, timedelta

    if days:
        # 删除 N 天前的数据
        cutoff_date = datetime.now() - timedelta(days=days)
        query = db.query(ProductOrderQueryLog).filter(
            ProductOrderQueryLog.created_at < cutoff_date
        )
        count = query.count()
        query.delete(synchronize_session=False)
    else:
        # 删除所有数据
        count = db.query(ProductOrderQueryLog).count()
        db.query(ProductOrderQueryLog).delete()

    db.commit()

    return {"message": f"删除成功", "deleted_count": count}


@router.delete("/{log_id}")
def delete_query_log(
    log_id: int,
    db: Session = Depends(get_db)
):
    """删除单条查询日志"""
    log = db.query(ProductOrderQueryLog).filter(
        ProductOrderQueryLog.id == log_id
    ).first()

    if not log:
        raise HTTPException(status_code=404, detail="日志不存在")

    db.delete(log)
    db.commit()

    return {"message": "删除成功"}
