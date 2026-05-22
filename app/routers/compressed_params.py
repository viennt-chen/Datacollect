"""
压缩工艺参数追溯 API 路由
基于 compressed_params 表（压缩参数数据表）
功能：查询、解压和展示压缩存储的工艺参数（PV/SV/Alarm）
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import Optional, List, Dict, Any
from datetime import datetime
import gzip
import json

from app.database import get_db
from app.models.compressed_param import CompressedParam

router = APIRouter()


def decompress_payload(compressed_data: bytes) -> Dict[str, Any]:
    """解压缩 payload 数据"""
    try:
        decompressed = gzip.decompress(compressed_data).decode('utf-8')
        return json.loads(decompressed)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"解压缩失败：{str(e)}")


@router.get("/compressed")
async def list_compressed_params(
    topic: Optional[str] = Query(None, description="Topic 名称，如 SHXQ/NO1/KP3/IMG/PV"),
    event_uid: Optional[str] = Query(None, description="事件唯一标识"),
    start_time: Optional[datetime] = Query(None, description="开始时间"),
    end_time: Optional[datetime] = Query(None, description="结束时间"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db)
):
    """
    查询压缩工艺参数列表
    
    支持按 Topic、事件 UID、时间范围筛选
    返回解压缩后的完整数据
    """
    db_query = db.query(CompressedParam)
    
    # Topic 筛选
    if topic:
        db_query = db_query.filter(CompressedParam.topic == topic)
    
    # Event UID 筛选
    if event_uid:
        db_query = db_query.filter(CompressedParam.event_uid == event_uid)
    
    # 时间范围筛选（转换为毫秒时间戳）
    if start_time:
        start_timestamp = int(start_time.timestamp() * 1000)
        db_query = db_query.filter(CompressedParam.timestamp_ms >= start_timestamp)
    if end_time:
        end_timestamp = int(end_time.timestamp() * 1000)
        db_query = db_query.filter(CompressedParam.timestamp_ms <= end_timestamp)
    
    # 获取总数
    total = db_query.count()
    
    # 分页和排序
    offset = (page - 1) * page_size
    items = db_query.order_by(desc(CompressedParam.timestamp_ms)).offset(offset).limit(page_size).all()
    
    # 解压缩数据
    result_items = []
    for item in items:
        try:
            payload_data = decompress_payload(item.compressed_payload)
            result_items.append({
                "id": item.id,
                "topic": item.topic,
                "event_uid": item.event_uid,
                "timestamp_ms": item.timestamp_ms,
                "timestamp": datetime.fromtimestamp(item.timestamp_ms / 1000).isoformat(),
                "original_timestamp": item.original_timestamp,
                "data": payload_data,
                "compressed_size": len(item.compressed_payload),
                "original_size": len(json.dumps(payload_data)),
                "compression_ratio": round(len(json.dumps(payload_data)) / len(item.compressed_payload), 2) if item.compressed_payload else 0,
                "created_at": item.created_at.isoformat() if item.created_at else None
            })
        except Exception as e:
            result_items.append({
                "id": item.id,
                "topic": item.topic,
                "event_uid": item.event_uid,
                "timestamp_ms": item.timestamp_ms,
                "error": f"解压缩失败：{str(e)}"
            })
    
    return {
        "total": total,
        "items": result_items
    }


@router.get("/compressed/stats")
async def get_compressed_params_stats(
    topic: Optional[str] = Query(None, description="Topic 名称"),
    start_time: Optional[datetime] = Query(None, description="开始时间"),
    end_time: Optional[datetime] = Query(None, description="结束时间"),
    db: Session = Depends(get_db)
):
    """
    获取压缩工艺参数统计信息
    
    返回：
    - 总记录数
    - 不同 Topic 数量
    - 平均压缩比
    - 时间范围
    """
    db_query = db.query(CompressedParam)
    
    # Topic 筛选
    if topic:
        db_query = db_query.filter(CompressedParam.topic == topic)
    
    # 时间范围筛选
    if start_time:
        start_timestamp = int(start_time.timestamp() * 1000)
        db_query = db_query.filter(CompressedParam.timestamp_ms >= start_timestamp)
    if end_time:
        end_timestamp = int(end_time.timestamp() * 1000)
        db_query = db_query.filter(CompressedParam.timestamp_ms <= end_timestamp)
    
    # 统计总数
    total = db_query.count()
    
    # 统计不同 Topic 数量
    topic_count = db_query.with_entities(
        func.count(func.distinct(CompressedParam.topic))
    ).scalar() or 0
    
    # 统计不同 Event UID 数量
    event_count = db_query.with_entities(
        func.count(func.distinct(CompressedParam.event_uid))
    ).scalar() or 0
    
    # 获取最早和最晚时间
    time_range = db_query.with_entities(
        func.min(CompressedParam.timestamp_ms),
        func.max(CompressedParam.timestamp_ms)
    ).first()
    
    # 计算平均压缩数据大小
    avg_compressed_size = db_query.with_entities(
        func.avg(func.length(CompressedParam.compressed_payload))
    ).scalar() or 0
    
    return {
        "total": total,
        "topic_count": topic_count,
        "event_count": event_count,
        "avg_compressed_size_kb": round(avg_compressed_size / 1024, 2),
        "earliest_time": datetime.fromtimestamp(time_range[0] / 1000).isoformat() if time_range[0] else None,
        "latest_time": datetime.fromtimestamp(time_range[1] / 1000).isoformat() if time_range[1] else None
    }


@router.get("/compressed/{param_id}")
async def get_compressed_param_detail(
    param_id: int,
    db: Session = Depends(get_db)
):
    """
    获取压缩工艺参数详情
    
    返回解压缩后的完整数据
    """
    param = db.query(CompressedParam).filter(CompressedParam.id == param_id).first()
    if not param:
        raise HTTPException(status_code=404, detail="压缩参数记录不存在")
    
    try:
        payload_data = decompress_payload(param.compressed_payload)
        
        return {
            "id": param.id,
            "topic": param.topic,
            "event_uid": param.event_uid,
            "timestamp_ms": param.timestamp_ms,
            "timestamp": datetime.fromtimestamp(param.timestamp_ms / 1000).isoformat(),
            "original_timestamp": param.original_timestamp,
            "data": payload_data,
            "compressed_size": len(param.compressed_payload),
            "original_size": len(json.dumps(payload_data)),
            "compression_ratio": round(len(json.dumps(payload_data)) / len(param.compressed_payload), 2) if param.compressed_payload else 0,
            "created_at": param.created_at.isoformat() if param.created_at else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"解压缩失败：{str(e)}")


@router.get("/compressed/topic/{topic}/list")
async def list_topics():
    """获取所有 Topic 列表"""
    return {
        "topics": [
            {
                "name": "SHXQ/NO1/KP3/IMG/PV",
                "description": "PV 参数（过程值）",
                "type": "process_value"
            },
            {
                "name": "SHXQ/NO1/KP3/IMG/SV",
                "description": "SV 参数（设定值）",
                "type": "set_value"
            },
            {
                "name": "SHXQ/NO1/KP3/IMG/Alarm",
                "description": "Alarm 参数（报警信息）",
                "type": "alarm"
            }
        ]
    }


@router.get("/compressed/event/{event_uid}")
async def get_event_params(
    event_uid: str,
    db: Session = Depends(get_db)
):
    """
    根据事件 UID 获取所有关联的压缩参数
    
    返回该事件的所有 PV/SV/Alarm 数据
    """
    params = db.query(CompressedParam).filter(
        CompressedParam.event_uid == event_uid
    ).order_by(CompressedParam.timestamp_ms).all()
    
    result = {
        "event_uid": event_uid,
        "total": len(params),
        "pv_data": [],
        "sv_data": [],
        "alarm_data": []
    }
    
    for param in params:
        try:
            payload_data = decompress_payload(param.compressed_payload)
            item = {
                "timestamp": datetime.fromtimestamp(param.timestamp_ms / 1000).isoformat(),
                "data": payload_data
            }
            
            if "PV" in param.topic:
                result["pv_data"].append(item)
            elif "SV" in param.topic:
                result["sv_data"].append(item)
            elif "Alarm" in param.topic:
                result["alarm_data"].append(item)
                
        except Exception as e:
            pass
    
    return result
