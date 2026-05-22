"""
产品订单查询分析处理 API
功能：提供订单数据的统计分析、趋势分析、完成率分析等
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, text
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

from app.database import get_db
from app.models.product_order import ProductOrder
from pydantic import BaseModel, Field, ConfigDict


router = APIRouter(prefix="/api/product-orders/analysis", tags=["产品订单分析"])


# ==================== Schema 定义 ====================

class DateRangeRequest(BaseModel):
    """日期范围请求"""
    start_date: str = Field(..., description="开始日期 YYYY-MM-DD")
    end_date: str = Field(..., description="结束日期 YYYY-MM-DD")
    part_number: Optional[str] = Field(None, description="零件号（可选）")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "start_date": "2026-04-01",
                "end_date": "2026-04-17",
                "part_number": "1743396-10-E"
            }
        }
    )


class OrderSummaryStats(BaseModel):
    """订单汇总统计"""
    total_orders: int = Field(..., description="订单总数")
    total_planned_output: int = Field(..., description="计划总产量")
    total_product_qty: float = Field(..., description="订单总数量")
    total_complete_qty: float = Field(..., description="累计完工总数")
    total_eligible_qty: float = Field(..., description="合格总数")
    total_scrap_qty: float = Field(..., description="报废总数")
    avg_completion_rate: float = Field(..., description="平均完成率 %")
    avg_eligible_rate: float = Field(..., description="平均合格率 %")
    avg_scrap_rate: float = Field(..., description="平均报废率 %")


class DepartmentStats(BaseModel):
    """部门统计"""
    department_code: str = Field(..., description="部门代码")
    department_name: str = Field(..., description="部门名称")
    order_count: int = Field(..., description="订单数量")
    total_product_qty: float = Field(..., description="订单总数量")
    total_complete_qty: float = Field(..., description="完工总数量")
    total_eligible_qty: float = Field(..., description="合格总数量")
    total_scrap_qty: float = Field(..., description="报废总数量")
    completion_rate: float = Field(..., description="完成率 %")
    eligible_rate: float = Field(..., description="合格率 %")
    scrap_rate: float = Field(..., description="报废率 %")


class ProjectStats(BaseModel):
    """项目统计"""
    project: str = Field(..., description="项目名称")
    order_count: int = Field(..., description="订单数量")
    total_product_qty: float = Field(..., description="订单总数量")
    total_complete_qty: float = Field(..., description="完工总数量")
    total_eligible_qty: float = Field(..., description="合格总数量")
    total_scrap_qty: float = Field(..., description="报废总数量")
    completion_rate: float = Field(..., description="完成率 %")


class DailyTrend(BaseModel):
    """每日趋势"""
    date: str = Field(..., description="日期")
    order_count: int = Field(..., description="订单数量")
    planned_output: int = Field(..., description="计划产量")
    product_qty: float = Field(..., description="订单数量")
    complete_qty: float = Field(..., description="完工数量")
    eligible_qty: float = Field(..., description="合格数量")
    scrap_qty: float = Field(..., description="报废数量")


class PartAnalysis(BaseModel):
    """零件分析"""
    part_number: str = Field(..., description="零件号")
    specs: str = Field(..., description="规格型号")
    order_count: int = Field(..., description="订单数量")
    total_planned_output: int = Field(..., description="计划总产量")
    total_product_qty: float = Field(..., description="订单总数量")
    total_complete_qty: float = Field(..., description="完工总数量")
    total_eligible_qty: float = Field(..., description="合格总数量")
    total_scrap_qty: float = Field(..., description="报废总数量")
    completion_rate: float = Field(..., description="完成率 %")
    eligible_rate: float = Field(..., description="合格率 %")
    scrap_rate: float = Field(..., description="报废率 %")


class DocTypeStats(BaseModel):
    """单据类型统计"""
    doc_type: str = Field(..., description="单据类型")
    doc_type_code: str = Field(..., description="单据类型代码")
    order_count: int = Field(..., description="订单数量")
    total_product_qty: float = Field(..., description="订单总数量")
    total_complete_qty: float = Field(..., description="完工总数量")


class WarehouseStats(BaseModel):
    """仓库统计"""
    warehouse: str = Field(..., description="仓库名称")
    warehouse_code: str = Field(..., description="仓库代码")
    order_count: int = Field(..., description="订单数量")
    total_product_qty: float = Field(..., description="订单总数量")
    total_complete_qty: float = Field(..., description="完工总数量")


class AnalysisResponse(BaseModel):
    """分析响应"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="响应消息")
    data: Dict[str, Any] = Field(..., description="分析数据")


# ==================== 辅助函数 ====================

def calculate_rate(numerator: float, denominator: float) -> float:
    """计算比率，避免除零错误"""
    if denominator == 0:
        return 0.0
    return round((numerator / denominator) * 100, 2)


# ==================== API 端点（分析） ====================

@router.post("/summary", response_model=AnalysisResponse)
async def get_order_summary(
    request: DateRangeRequest,
    db: Session = Depends(get_db)
):
    """获取订单汇总统计"""
    try:
        query = db.query(
            func.count(ProductOrder.id).label('order_count'),
            func.sum(ProductOrder.planned_output).label('total_planned'),
            func.sum(ProductOrder.product_qty).label('total_product'),
            func.sum(ProductOrder.total_complete_qty).label('total_complete'),
            func.sum(ProductOrder.total_eligible_qty).label('total_eligible'),
            func.sum(ProductOrder.total_scrap_qty).label('total_scrap'),
        ).filter(
            and_(
                ProductOrder.query_date >= request.start_date,
                ProductOrder.query_date <= request.end_date
            )
        )

        if request.part_number:
            query = query.filter(ProductOrder.part_number == request.part_number)

        result = query.first()

        total_complete = result.total_complete or 0
        total_product = result.total_product or 0
        total_eligible = result.total_eligible or 0
        total_scrap = result.total_scrap or 0

        completion_rate = calculate_rate(total_complete, total_product)
        eligible_rate = calculate_rate(total_eligible, total_complete)
        scrap_rate = calculate_rate(total_scrap, total_product)

        summary = OrderSummaryStats(
            total_orders=result.order_count or 0,
            total_planned_output=result.total_planned or 0,
            total_product_qty=total_product,
            total_complete_qty=total_complete,
            total_eligible_qty=total_eligible,
            total_scrap_qty=total_scrap,
            avg_completion_rate=completion_rate,
            avg_eligible_rate=eligible_rate,
            avg_scrap_rate=scrap_rate
        )
        
        return AnalysisResponse(
            success=True,
            message="获取订单汇总统计成功",
            data=summary.model_dump()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取汇总统计失败：{str(e)}")


@router.post("/by-department", response_model=AnalysisResponse)
async def get_department_stats(
    request: DateRangeRequest,
    db: Session = Depends(get_db)
):
    """按部门统计订单数据"""
    try:
        query = db.query(
            ProductOrder.department_code,
            ProductOrder.department_name,
            func.count(ProductOrder.id).label('order_count'),
            func.sum(ProductOrder.product_qty).label('total_product'),
            func.sum(ProductOrder.total_complete_qty).label('total_complete'),
            func.sum(ProductOrder.total_eligible_qty).label('total_eligible'),
            func.sum(ProductOrder.total_scrap_qty).label('total_scrap'),
        ).filter(
            and_(
                ProductOrder.query_date >= request.start_date,
                ProductOrder.query_date <= request.end_date,
                ProductOrder.department_code.isnot(None),
                ProductOrder.department_code != ''
            )
        )

        if request.part_number:
            query = query.filter(ProductOrder.part_number == request.part_number)

        query = query.group_by(
            ProductOrder.department_code,
            ProductOrder.department_name
        ).order_by(func.sum(ProductOrder.product_qty).desc())
        
        results = query.all()
        
        dept_stats = []
        for row in results:
            total_product = row.total_product or 0
            total_complete = row.total_complete or 0
            total_eligible = row.total_eligible or 0
            total_scrap = row.total_scrap or 0
            
            dept_stats.append(DepartmentStats(
                department_code=row.department_code or '',
                department_name=row.department_name or '',
                order_count=row.order_count,
                total_product_qty=total_product,
                total_complete_qty=total_complete,
                total_eligible_qty=total_eligible,
                total_scrap_qty=total_scrap,
                completion_rate=calculate_rate(total_complete, total_product),
                eligible_rate=calculate_rate(total_eligible, total_complete),
                scrap_rate=calculate_rate(total_scrap, total_product)
            ))
        
        return AnalysisResponse(
            success=True,
            message="获取部门统计成功",
            data={
                "departments": [d.model_dump() for d in dept_stats],
                "total_departments": len(dept_stats)
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取部门统计失败：{str(e)}")


@router.post("/by-project", response_model=AnalysisResponse)
async def get_project_stats(
    request: DateRangeRequest,
    db: Session = Depends(get_db)
):
    """按项目统计订单数据"""
    try:
        query = db.query(
            ProductOrder.project,
            func.count(ProductOrder.id).label('order_count'),
            func.sum(ProductOrder.product_qty).label('total_product'),
            func.sum(ProductOrder.total_complete_qty).label('total_complete'),
            func.sum(ProductOrder.total_eligible_qty).label('total_eligible'),
            func.sum(ProductOrder.total_scrap_qty).label('total_scrap'),
        ).filter(
            and_(
                ProductOrder.query_date >= request.start_date,
                ProductOrder.query_date <= request.end_date,
                ProductOrder.project.isnot(None),
                ProductOrder.project != ''
            )
        )

        if request.part_number:
            query = query.filter(ProductOrder.part_number == request.part_number)

        query = query.group_by(
            ProductOrder.project
        ).order_by(func.sum(ProductOrder.product_qty).desc())
        
        results = query.all()
        
        project_stats = []
        for row in results:
            total_product = row.total_product or 0
            total_complete = row.total_complete or 0
            total_eligible = row.total_eligible or 0
            total_scrap = row.total_scrap or 0
            
            project_stats.append(ProjectStats(
                project=row.project or '',
                order_count=row.order_count,
                total_product_qty=total_product,
                total_complete_qty=total_complete,
                total_eligible_qty=total_eligible,
                total_scrap_qty=total_scrap,
                completion_rate=calculate_rate(total_complete, total_product)
            ))
        
        return AnalysisResponse(
            success=True,
            message="获取项目统计成功",
            data={
                "projects": [p.model_dump() for p in project_stats],
                "total_projects": len(project_stats)
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取项目统计失败：{str(e)}")


@router.post("/daily-trend", response_model=AnalysisResponse)
async def get_daily_trend(
    request: DateRangeRequest,
    db: Session = Depends(get_db)
):
    """获取每日趋势数据"""
    try:
        query = db.query(
            ProductOrder.query_date,
            func.count(ProductOrder.id).label('order_count'),
            func.sum(ProductOrder.planned_output).label('total_planned'),
            func.sum(ProductOrder.product_qty).label('total_product'),
            func.sum(ProductOrder.total_complete_qty).label('total_complete'),
            func.sum(ProductOrder.total_eligible_qty).label('total_eligible'),
            func.sum(ProductOrder.total_scrap_qty).label('total_scrap'),
        ).filter(
            and_(
                ProductOrder.query_date >= request.start_date,
                ProductOrder.query_date <= request.end_date
            )
        )

        if request.part_number:
            query = query.filter(ProductOrder.part_number == request.part_number)

        query = query.group_by(ProductOrder.query_date).order_by(ProductOrder.query_date)
        
        results = query.all()
        
        daily_trends = []
        for row in results:
            daily_trends.append(DailyTrend(
                date=row.query_date,
                order_count=row.order_count or 0,
                planned_output=row.total_planned or 0,
                product_qty=row.total_product or 0,
                complete_qty=row.total_complete or 0,
                eligible_qty=row.total_eligible or 0,
                scrap_qty=row.total_scrap or 0
            ))
        
        return AnalysisResponse(
            success=True,
            message="获取每日趋势成功",
            data={
                "trends": [t.model_dump() for t in daily_trends],
                "total_days": len(daily_trends)
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取每日趋势失败：{str(e)}")


@router.post("/by-part", response_model=AnalysisResponse)
async def get_part_analysis(
    request: DateRangeRequest,
    db: Session = Depends(get_db)
):
    """按零件号分析订单数据"""
    try:
        query = db.query(
            ProductOrder.part_number,
            ProductOrder.specs,
            func.count(ProductOrder.id).label('order_count'),
            func.sum(ProductOrder.planned_output).label('total_planned'),
            func.sum(ProductOrder.product_qty).label('total_product'),
            func.sum(ProductOrder.total_complete_qty).label('total_complete'),
            func.sum(ProductOrder.total_eligible_qty).label('total_eligible'),
            func.sum(ProductOrder.total_scrap_qty).label('total_scrap'),
        ).filter(
            and_(
                ProductOrder.query_date >= request.start_date,
                ProductOrder.query_date <= request.end_date
            )
        )

        if request.part_number:
            query = query.filter(ProductOrder.part_number == request.part_number)

        query = query.group_by(
            ProductOrder.part_number,
            ProductOrder.specs
        ).order_by(func.sum(ProductOrder.product_qty).desc())
        
        results = query.all()
        
        part_analysis = []
        for row in results:
            total_product = row.total_product or 0
            total_complete = row.total_complete or 0
            total_eligible = row.total_eligible or 0
            total_scrap = row.total_scrap or 0
            
            part_analysis.append(PartAnalysis(
                part_number=row.part_number,
                specs=row.specs or '',
                order_count=row.order_count,
                total_planned_output=row.total_planned or 0,
                total_product_qty=total_product,
                total_complete_qty=total_complete,
                total_eligible_qty=total_eligible,
                total_scrap_qty=total_scrap,
                completion_rate=calculate_rate(total_complete, total_product),
                eligible_rate=calculate_rate(total_eligible, total_complete),
                scrap_rate=calculate_rate(total_scrap, total_product)
            ))
        
        return AnalysisResponse(
            success=True,
            message="获取零件分析成功",
            data={
                "parts": [p.model_dump() for p in part_analysis],
                "total_parts": len(part_analysis)
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取零件分析失败：{str(e)}")


@router.post("/by-doc-type", response_model=AnalysisResponse)
async def get_doc_type_stats(
    request: DateRangeRequest,
    db: Session = Depends(get_db)
):
    """按单据类型统计订单数据"""
    try:
        query = db.query(
            ProductOrder.doc_type,
            ProductOrder.doc_type_code,
            func.count(ProductOrder.id).label('order_count'),
            func.sum(ProductOrder.product_qty).label('total_product'),
            func.sum(ProductOrder.total_complete_qty).label('total_complete'),
        ).filter(
            and_(
                ProductOrder.query_date >= request.start_date,
                ProductOrder.query_date <= request.end_date,
                ProductOrder.doc_type.isnot(None),
                ProductOrder.doc_type != ''
            )
        )

        if request.part_number:
            query = query.filter(ProductOrder.part_number == request.part_number)

        query = query.group_by(
            ProductOrder.doc_type,
            ProductOrder.doc_type_code
        ).order_by(func.sum(ProductOrder.product_qty).desc())
        
        results = query.all()
        
        doc_type_stats = []
        for row in results:
            doc_type_stats.append(DocTypeStats(
                doc_type=row.doc_type or '',
                doc_type_code=row.doc_type_code or '',
                order_count=row.order_count,
                total_product_qty=row.total_product or 0,
                total_complete_qty=row.total_complete or 0
            ))
        
        return AnalysisResponse(
            success=True,
            message="获取单据类型统计成功",
            data={
                "doc_types": [d.model_dump() for d in doc_type_stats],
                "total_types": len(doc_type_stats)
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取单据类型统计失败：{str(e)}")


@router.post("/by-warehouse", response_model=AnalysisResponse)
async def get_warehouse_stats(
    request: DateRangeRequest,
    db: Session = Depends(get_db)
):
    """按仓库统计订单数据"""
    try:
        query = db.query(
            ProductOrder.complete_wh,
            ProductOrder.complete_wh_code,
            func.count(ProductOrder.id).label('order_count'),
            func.sum(ProductOrder.product_qty).label('total_product'),
            func.sum(ProductOrder.total_complete_qty).label('total_complete'),
        ).filter(
            and_(
                ProductOrder.query_date >= request.start_date,
                ProductOrder.query_date <= request.end_date,
                ProductOrder.complete_wh.isnot(None),
                ProductOrder.complete_wh != ''
            )
        )

        if request.part_number:
            query = query.filter(ProductOrder.part_number == request.part_number)

        query = query.group_by(
            ProductOrder.complete_wh,
            ProductOrder.complete_wh_code
        ).order_by(func.sum(ProductOrder.product_qty).desc())
        
        results = query.all()
        
        warehouse_stats = []
        for row in results:
            warehouse_stats.append(WarehouseStats(
                warehouse=row.complete_wh or '',
                warehouse_code=row.complete_wh_code or '',
                order_count=row.order_count,
                total_product_qty=row.total_product or 0,
                total_complete_qty=row.total_complete or 0
            ))
        
        return AnalysisResponse(
            success=True,
            message="获取仓库统计成功",
            data={
                "warehouses": [w.model_dump() for w in warehouse_stats],
                "total_warehouses": len(warehouse_stats)
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取仓库统计失败：{str(e)}")


@router.post("/comprehensive", response_model=AnalysisResponse)
async def get_comprehensive_analysis(
    request: DateRangeRequest,
    db: Session = Depends(get_db)
):
    """综合分析：一次性获取所有维度的统计分析数据"""
    try:
        # 直接调用同步函数，避免不必要的 async/await 开销
        summary_result = await get_order_summary(request, db)
        dept_result = await get_department_stats(request, db)
        project_result = await get_project_stats(request, db)
        trend_result = await get_daily_trend(request, db)
        part_result = await get_part_analysis(request, db)
        doc_type_result = await get_doc_type_stats(request, db)
        warehouse_result = await get_warehouse_stats(request, db)

        comprehensive_data = {
            "summary": summary_result.data,
            "departments": dept_result.data,
            "projects": project_result.data,
            "daily_trends": trend_result.data,
            "parts": part_result.data,
            "doc_types": doc_type_result.data,
            "warehouses": warehouse_result.data
        }

        return AnalysisResponse(
            success=True,
            message="获取综合分析成功",
            data=comprehensive_data
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取综合分析失败：{str(e)}")