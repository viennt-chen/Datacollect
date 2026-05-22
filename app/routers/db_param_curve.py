"""
DB参数曲线 API 路由
功能：管理设备加工时的标准DB参数时间-值曲线
"""
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc
from typing import Optional, List, Dict, Any
from datetime import datetime
import json
import csv
import io

from app.database import get_db
from app.models.db_param_curve import DBParamCurve
from app.models.device import Device
from app.utils.rule_evaluator import match_curve
from app.schemas.db_param_curve import (
    DBParamCurveCreate,
    DBParamCurveUpdate,
    DBParamCurveDetail,
    DBParamCurveList,
    CurveMatchResult
)

router = APIRouter(prefix="/devices/servo-curves", tags=["DB参数曲线管理"])


@router.post("/", response_model=DBParamCurveDetail)
async def create_db_param_curve(
    curve_data: DBParamCurveCreate,
    db: Session = Depends(get_db)
):
    """
    创建DB参数曲线
    
    接收曲线数据点并自动计算元数据
    """
    try:
        device = db.query(Device).filter(Device.device_code == curve_data.device_code).first()
        if not device:
            raise HTTPException(status_code=404, detail="设备不存在")

        curve_data_list = curve_data.curve_data

        if not curve_data_list or len(curve_data_list) == 0:
            raise HTTPException(status_code=400, detail="曲线数据不能为空")

        sorted_data = sorted(curve_data_list, key=lambda x: x['time'])

        total_duration = int(sorted_data[-1]['time']) if sorted_data else 0
        values = [point['value'] for point in sorted_data]
        max_value = max(values) if values else 0
        min_value = min(values) if values else 0

        db_curve = DBParamCurve(
            device_code=curve_data.device_code,
            curve_name=curve_data.curve_name,
            part_number=curve_data.part_number,
            servo_axis=curve_data.servo_axis,
            curve_data=sorted_data,
            total_duration_ms=total_duration,
            max_value=max_value,
            min_value=min_value,
            data_points_count=len(sorted_data),
            value_tolerance=curve_data.value_tolerance,
            time_tolerance_ms=curve_data.time_tolerance_ms,
            enabled=1 if curve_data.enabled else 0,
            description=curve_data.description
        )
        
        db.add(db_curve)
        db.commit()
        db.refresh(db_curve)
        
        return db_curve
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        import traceback
        print(f"创建伺服曲线失败: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"创建曲线失败: {str(e)}")


@router.get("/", response_model=DBParamCurveList)
async def list_db_param_curves(
    device_code: Optional[str] = Query(None, description="设备编号"),
    part_number: Optional[str] = Query(None, description="产品零件号"),
    enabled_only: bool = Query(False, description="只查询启用的"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db)
):
    """
    查询DB参数曲线列表
    """
    db_query = db.query(DBParamCurve)
    
    if device_code is not None:
        db_query = db_query.filter(DBParamCurve.device_code == device_code)
    
    if part_number:
        db_query = db_query.filter(DBParamCurve.part_number == part_number)
    
    if enabled_only:
        db_query = db_query.filter(DBParamCurve.enabled == 1)
    
    total = db_query.count()
    
    offset = (page - 1) * page_size
    items = db_query.order_by(desc(DBParamCurve.created_at)).offset(offset).limit(page_size).all()
    
    return {
        "total": total,
        "items": items
    }


@router.get("/{curve_id}", response_model=DBParamCurveDetail)
async def get_db_param_curve(
    curve_id: int,
    db: Session = Depends(get_db)
):
    """
    获取DB参数曲线详情
    """
    curve = db.query(DBParamCurve).filter(DBParamCurve.id == curve_id).first()
    if not curve:
        raise HTTPException(status_code=404, detail="曲线不存在")
    
    return curve


@router.put("/{curve_id}", response_model=DBParamCurveDetail)
async def update_db_param_curve(
    curve_id: int,
    update_data: DBParamCurveUpdate,
    db: Session = Depends(get_db)
):
    """
    更新DB参数曲线
    """
    curve = db.query(DBParamCurve).filter(DBParamCurve.id == curve_id).first()
    if not curve:
        raise HTTPException(status_code=404, detail="曲线不存在")
    
    update_dict = update_data.dict(exclude_unset=True)
    
    if 'curve_data' in update_dict:
        curve_data_list = update_dict['curve_data']
        sorted_data = sorted(curve_data_list, key=lambda x: x['time'])
        update_dict['total_duration_ms'] = int(sorted_data[-1]['time']) if sorted_data else 0
        values = [point['value'] for point in sorted_data]
        update_dict['max_value'] = max(values) if values else 0
        update_dict['min_value'] = min(values) if values else 0
        update_dict['data_points_count'] = len(sorted_data)
        update_dict['curve_data'] = sorted_data
    
    if 'enabled' in update_dict:
        update_dict['enabled'] = 1 if update_dict['enabled'] else 0
    
    for key, value in update_dict.items():
        setattr(curve, key, value)
    
    db.commit()
    db.refresh(curve)
    
    return curve


@router.delete("/{curve_id}")
async def delete_db_param_curve(
    curve_id: int,
    db: Session = Depends(get_db)
):
    """
    删除DB参数曲线
    """
    curve = db.query(DBParamCurve).filter(DBParamCurve.id == curve_id).first()
    if not curve:
        raise HTTPException(status_code=404, detail="曲线不存在")
    
    db.delete(curve)
    db.commit()
    
    return {"message": "删除成功"}


@router.post("/import/csv")
async def import_db_param_curve_from_csv(
    device_code: str = Query(..., description="设备编号"),
    curve_name: str = Query(..., description="曲线名称"),
    part_number: Optional[str] = Query(None, description="产品零件号"),
    servo_axis: str = Query(..., description="伺服轴名称"),
    value_tolerance: float = Query(5.0, description="值容差"),
    time_tolerance_ms: int = Query(100, description="时间容差（毫秒）"),
    description: Optional[str] = Query(None, description="备注说明"),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    从CSV文件导入DB参数曲线

    CSV格式：
    time,value
    0,0
    100,50
    200,100
    ...
    """
    device = db.query(Device).filter(Device.device_code == device_code).first()
    if not device:
        raise HTTPException(status_code=404, detail="设备不存在")
    
    content = await file.read()
    content_str = content.decode('utf-8')
    
    csv_reader = csv.DictReader(io.StringIO(content_str))
    
    curve_data = []
    for row in csv_reader:
        try:
            time_val = float(row.get('time', row.get('Time', row.get('TIME', ''))))
            value_val = float(row.get('value', row.get('Value', row.get('VALUE', ''))))
            curve_data.append({
                "time": time_val,
                "value": value_val
            })
        except (ValueError, KeyError) as e:
            raise HTTPException(status_code=400, detail=f"CSV数据格式错误：{str(e)}")
    
    if not curve_data:
        raise HTTPException(status_code=400, detail="曲线数据为空")
    
    sorted_data = sorted(curve_data, key=lambda x: x['time'])
    
    total_duration = int(sorted_data[-1]['time']) if sorted_data else 0
    values = [point['value'] for point in sorted_data]
    max_value = max(values) if values else 0
    min_value = min(values) if values else 0
    
    db_curve = DBParamCurve(
        device_code=device_code,
        curve_name=curve_name,
        part_number=part_number,
        servo_axis=servo_axis,
        curve_data=sorted_data,
        total_duration_ms=total_duration,
        max_value=max_value,
        min_value=min_value,
        data_points_count=len(sorted_data),
        value_tolerance=value_tolerance,
        time_tolerance_ms=time_tolerance_ms,
        enabled=1,
        description=description
    )

    db.add(db_curve)
    db.commit()
    db.refresh(db_curve)

    return {
        "message": "导入成功",
        "curve_id": db_curve.id,
        "data_points_count": len(sorted_data),
        "total_duration_ms": total_duration
    }


@router.post("/import/json")
async def import_db_param_curve_from_json(
    device_code: str = Query(..., description="设备编号"),
    curve_name: str = Query(..., description="曲线名称"),
    part_number: Optional[str] = Query(None, description="产品零件号"),
    servo_axis: str = Query(..., description="伺服轴名称"),
    value_tolerance: float = Query(5.0, description="值容差"),
    time_tolerance_ms: int = Query(100, description="时间容差（毫秒）"),
    description: Optional[str] = Query(None, description="备注说明"),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    从JSON文件导入DB参数曲线
    
    JSON格式：
    [
      {"time": 0, "value": 0},
      {"time": 100, "value": 50},
      ...
    ]
    """
    device = db.query(Device).filter(Device.device_code == device_code).first()
    if not device:
        raise HTTPException(status_code=404, detail="设备不存在")

    content = await file.read()
    content_str = content.decode('utf-8')

    try:
        curve_data = json.loads(content_str)
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"JSON格式错误：{str(e)}")

    if not isinstance(curve_data, list):
        raise HTTPException(status_code=400, detail="JSON数据必须是数组格式")

    for point in curve_data:
        if 'time' not in point or 'value' not in point:
            raise HTTPException(status_code=400, detail="每个数据点必须包含time和value字段")

    sorted_data = sorted(curve_data, key=lambda x: x['time'])

    total_duration = int(sorted_data[-1]['time']) if sorted_data else 0
    values = [point['value'] for point in sorted_data]
    max_value = max(values) if values else 0
    min_value = min(values) if values else 0

    db_curve = DBParamCurve(
        device_code=device_code,
        curve_name=curve_name,
        part_number=part_number,
        servo_axis=servo_axis,
        curve_data=sorted_data,
        total_duration_ms=total_duration,
        max_value=max_value,
        min_value=min_value,
        data_points_count=len(sorted_data),
        value_tolerance=value_tolerance,
        time_tolerance_ms=time_tolerance_ms,
        enabled=1,
        description=description
    )
    
    db.add(db_curve)
    db.commit()
    db.refresh(db_curve)
    
    return {
        "message": "导入成功",
        "curve_id": db_curve.id,
        "data_points_count": len(sorted_data),
        "total_duration_ms": total_duration
    }


@router.post("/match/{curve_id}", response_model=CurveMatchResult)
async def match_db_param_curve(
    curve_id: int,
    realtime_data: List[Dict[str, Any]],
    db: Session = Depends(get_db)
):
    """
    匹配实时数据与标准曲线
    
    计算实时数据与标准曲线的匹配度
    """
    curve = db.query(DBParamCurve).filter(DBParamCurve.id == curve_id).first()
    if not curve:
        raise HTTPException(status_code=404, detail="曲线不存在")
    
    if not curve.enabled:
        raise HTTPException(status_code=400, detail="曲线未启用")
    
    standard_data = curve.curve_data
    value_tolerance = curve.value_tolerance
    time_tolerance = curve.time_tolerance_ms
    
    if not realtime_data:
        return CurveMatchResult(
            is_matched=False,
            match_score=0.0,
            max_deviation=0.0,
            avg_deviation=0.0,
            matched_points=0,
            total_points=0,
            details="实时数据为空"
        )

    result = match_curve(
        realtime_data=realtime_data,
        curve_data=standard_data,
        time_tolerance_ms=time_tolerance,
        value_tolerance=value_tolerance,
        min_points=1
    )

    return CurveMatchResult(
        is_matched=result['matched'],
        match_score=result['score'],
        max_deviation=result['max_deviation'],
        avg_deviation=result['avg_deviation'],
        matched_points=result['matched_points'],
        total_points=result['total_points'],
        details=f"匹配度: {result['score']:.2f}%, 最大偏差: {result['max_deviation']:.2f}" + (f" ({result['reason']})" if result['reason'] else "")
    )


@router.get("/device/{device_code}/curves")
async def get_device_curves(
    device_code: str,
    part_number: Optional[str] = Query(None, description="产品零件号"),
    db: Session = Depends(get_db)
):
    """
    获取设备的所有曲线（用于配置界面展示）
    """
    device = db.query(Device).filter(Device.device_code == device_code).first()
    if not device:
        raise HTTPException(status_code=404, detail="设备不存在")

    db_query = db.query(DBParamCurve).filter(
        DBParamCurve.device_code == device_code
    )
    
    if part_number:
        db_query = db_query.filter(DBParamCurve.part_number == part_number)
    
    curves = db_query.order_by(desc(DBParamCurve.created_at)).all()
    
    return {
        "device_code": device.device_code,
        "device_name": device.device_name,
        "curves": [
            {
                "id": curve.id,
                "curve_name": curve.curve_name,
                "part_number": curve.part_number,
                "servo_axis": curve.servo_axis,
                "data_points_count": curve.data_points_count,
                "total_duration_ms": curve.total_duration_ms,
                "enabled": curve.enabled == 1,
                "created_at": curve.created_at.isoformat() if curve.created_at else None
            }
            for curve in curves
        ]
    }
