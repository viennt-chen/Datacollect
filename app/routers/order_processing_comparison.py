"""
订单完工比对 API 路由
功能：本地完工数据 vs U9 完工数据比对、状态同步、补漏
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.schemas.order_processing_record import (
    CompletionComparisonResponse,
    CompletionComparisonSummary,
    CompletionComparisonItem,
    OrderTimelineResponse,
    BackfillResult,
    ReconcileResult,
    LinkStatusResponse,
)

router = APIRouter(prefix="/order-processing-comparison", tags=["订单完工比对"])


@router.get("/comparison", response_model=CompletionComparisonResponse)
def get_comparison(
    record_date: Optional[str] = Query(None, description="比对日期 YYYY-MM-DD，默认今日"),
    db: Session = Depends(get_db),
):
    """指定日期的全部订单完工比对"""
    from app.services.order_processing_linker import get_completion_comparison
    result = get_completion_comparison(record_date)
    return CompletionComparisonResponse(
        summary=CompletionComparisonSummary(**result.get('summary', {})),
        items=[CompletionComparisonItem(**item) for item in result.get('items', [])],
    )


@router.post("/reconcile", response_model=ReconcileResult)
def trigger_reconcile(
    record_date: Optional[str] = Query(None, description="同步日期 YYYY-MM-DD，默认今日"),
    db: Session = Depends(get_db),
):
    """手动触发订单状态同步"""
    from app.services.order_processing_linker import reconcile_order_statuses
    result = reconcile_order_statuses(record_date)
    return ReconcileResult(**result)


@router.post("/link-backfill", response_model=BackfillResult)
def trigger_backfill(
    batch_size: int = Query(100, ge=1, le=1000, description="补漏批次大小"),
    db: Session = Depends(get_db),
):
    """手动触发事件关联补漏"""
    from app.services.order_processing_linker import batch_link_unlinked_events
    result = batch_link_unlinked_events(batch_size)
    return BackfillResult(**result)


@router.get("/link-status", response_model=LinkStatusResponse)
def get_link_status():
    """获取关联服务状态"""
    trigger_status = {}
    scheduler_status = {}

    try:
        from app.services.order_processing_trigger import get_order_processing_trigger
        trigger_status = get_order_processing_trigger().get_status()
    except Exception:
        trigger_status = {"error": "触发器未初始化"}

    try:
        from app.services.order_processing_scheduler import get_order_processing_scheduler
        scheduler_status = get_order_processing_scheduler().get_status()
    except Exception:
        scheduler_status = {"error": "调度器未初始化"}

    return LinkStatusResponse(trigger=trigger_status, scheduler=scheduler_status)


@router.get("/comparison/{doc_no}", response_model=OrderTimelineResponse)
def get_order_comparison_detail(
    doc_no: str,
    record_date: Optional[str] = Query(None, description="日期 YYYY-MM-DD，默认今日"),
    db: Session = Depends(get_db),
):
    """单个订单详细比对（含按小时产量时间线）"""
    from app.services.order_processing_linker import get_order_timeline
    result = get_order_timeline(doc_no, record_date)
    return OrderTimelineResponse(**result)
