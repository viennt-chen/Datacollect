"""
采集日志管理 API 路由
功能：查询和分析 MQTT 数据采集日志
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_
from typing import Optional, List
from datetime import datetime, timedelta

from app.database import get_db, SessionLocal
from app.models.collector_log import CollectorLog

router = APIRouter(prefix="/collector-logs", tags=["采集日志管理"])


@router.get("/")
async def get_collector_logs(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    log_level: Optional[str] = Query(None, description="日志级别"),
    log_type: Optional[str] = Query(None, description="日志类型"),
    topic_name: Optional[str] = Query(None, description="Topic 名称"),
    start_time: Optional[datetime] = Query(None, description="开始时间"),
    end_time: Optional[datetime] = Query(None, description="结束时间"),
    db: Session = Depends(get_db)
):
    """
    获取采集日志列表
    
    Args:
        page: 页码
        page_size: 每页数量
        log_level: 日志级别过滤 (INFO/WARNING/ERROR/DEBUG)
        log_type: 日志类型过滤
        topic_name: Topic 名称过滤
        start_time: 开始时间
        end_time: 结束时间
        
    Returns:
        采集日志列表
    """
    # 构建查询
    query = db.query(CollectorLog)
    
    if log_level:
        query = query.filter(CollectorLog.log_level == log_level)
    
    if log_type:
        query = query.filter(CollectorLog.log_type == log_type)
    
    if topic_name:
        query = query.filter(CollectorLog.topic_name.like(f"%{topic_name}%"))
    
    if start_time:
        query = query.filter(CollectorLog.created_at >= start_time)
    
    if end_time:
        query = query.filter(CollectorLog.created_at <= end_time)
    
    # 总数
    total = query.count()
    
    # 分页
    offset = (page - 1) * page_size
    items = query.order_by(desc(CollectorLog.created_at)).offset(offset).limit(page_size).all()
    
    return {
        "total": total,
        "items": items
    }


@router.get("/stats")
async def get_collector_log_stats(
    days: int = Query(7, ge=1, le=30, description="统计天数"),
    db: Session = Depends(get_db)
):
    """
    获取采集日志统计信息
    
    Args:
        days: 统计天数
        
    Returns:
        统计信息
    """
    cutoff_time = datetime.now() - timedelta(days=days)
    
    # 基础查询
    base_query = db.query(CollectorLog).filter(
        CollectorLog.created_at >= cutoff_time
    )
    
    total = base_query.count()
    
    # 按级别分组统计
    level_stats = db.query(
        CollectorLog.log_level,
        func.count(CollectorLog.id).label('count')
    ).filter(
        CollectorLog.created_at >= cutoff_time
    ).group_by(CollectorLog.log_level).all()
    
    # 按类型分组统计
    type_stats = db.query(
        CollectorLog.log_type,
        func.count(CollectorLog.id).label('count')
    ).filter(
        CollectorLog.created_at >= cutoff_time
    ).group_by(CollectorLog.log_type).all()
    
    # 错误和警告统计
    error_count = base_query.filter(CollectorLog.log_level == 'ERROR').count()
    warning_count = base_query.filter(CollectorLog.log_level == 'WARNING').count()
    
    return {
        "total": total,
        "by_level": {item.log_level: item.count for item in level_stats},
        "by_type": {item.log_type: item.count for item in type_stats},
        "error_count": error_count,
        "warning_count": warning_count
    }


@router.get("/{log_id}")
async def get_collector_log(
    log_id: int,
    db: Session = Depends(get_db)
):
    """
    获取单个采集日志
    
    Args:
        log_id: 日志 ID
        
    Returns:
        日志详情
    """
    log = db.query(CollectorLog).filter(
        CollectorLog.id == log_id
    ).first()
    
    if not log:
        raise HTTPException(status_code=404, detail="日志不存在")
    
    return log


@router.get("/topic/{topic_name}")
async def get_logs_by_topic(
    topic_name: str,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db)
):
    """
    根据 Topic 名称获取日志
    
    Args:
        topic_name: Topic 名称
        page: 页码
        page_size: 每页数量
        
    Returns:
        日志列表
    """
    query = db.query(CollectorLog).filter(
        CollectorLog.topic_name.like(f"%{topic_name}%")
    )
    
    total = query.count()
    offset = (page - 1) * page_size
    items = query.order_by(desc(CollectorLog.created_at)).offset(offset).limit(page_size).all()
    
    return {
        "total": total,
        "items": items
    }


@router.get("/errors/recent")
async def get_recent_errors(
    limit: int = Query(50, ge=1, le=200, description="限制数量"),
    db: Session = Depends(get_db)
):
    """
    获取最近的错误日志
    
    Args:
        limit: 限制数量
        
    Returns:
        错误日志列表
    """
    query = db.query(CollectorLog).filter(
        CollectorLog.log_level == 'ERROR'
    ).order_by(desc(CollectorLog.created_at)).limit(limit)
    
    items = query.all()
    
    return {
        "total": len(items),
        "items": items
    }


@router.delete("/clear")
async def clear_collector_logs(
    days: int = Query(30, ge=1, description="清除多少天前的日志"),
    db: Session = Depends(get_db)
):
    """
    清除旧的采集日志
    
    Args:
        days: 清除多少天前的日志
        
    Returns:
        操作结果
    """
    cutoff_time = datetime.now() - timedelta(days=days)
    
    deleted = db.query(CollectorLog).filter(
        CollectorLog.created_at < cutoff_time
    ).delete(synchronize_session=False)
    
    db.commit()
    
    return {"message": f"成功清除 {deleted} 条日志记录"}


@router.post("/cleanup")
async def cleanup_collector_logs(
    db: Session = Depends(get_db)
):
    """
    执行存储过程清理：自动清理旧日志以保持表大小在500M以内
    
    Returns:
        操作结果
    """
    try:
        result = db.execute("CALL cleanup_collector_logs()")
        db.commit()
        
        # 获取清理后的表大小
        size_result = db.execute("""
            SELECT ROUND((data_length + index_length) / 1024 / 1024, 2) AS size_mb, table_rows
            FROM information_schema.tables 
            WHERE table_schema = DATABASE() 
            AND table_name = 'collector_logs'
        """).fetchone()
        
        return {
            "message": "清理完成",
            "current_size_mb": size_result[0] if size_result else 0,
            "total_records": size_result[1] if size_result else 0
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"清理失败: {str(e)}")


@router.get("/size")
async def get_collector_logs_size(
    db: Session = Depends(get_db)
):
    """
    获取采集日志表当前大小
    
    Returns:
        表大小信息
    """
    try:
        result = db.execute("""
            SELECT 
                ROUND((data_length + index_length) / 1024 / 1024, 2) AS size_mb,
                ROUND(data_length / 1024 / 1024, 2) AS data_size_mb,
                ROUND(index_length / 1024 / 1024, 2) AS index_size_mb,
                table_rows,
                ROUND(500 - (data_length + index_length) / 1024 / 1024, 2) AS remaining_mb
            FROM information_schema.tables 
            WHERE table_schema = DATABASE() 
            AND table_name = 'collector_logs'
        """).fetchone()
        
        if result:
            return {
                "total_size_mb": result[0],
                "data_size_mb": result[1],
                "index_size_mb": result[2],
                "total_records": result[3],
                "remaining_mb": result[4],
                "limit_mb": 500,
                "usage_percent": round((result[0] / 500) * 100, 2)
            }
        else:
            raise HTTPException(status_code=404, detail="日志表不存在")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")
