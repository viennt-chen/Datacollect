"""
本地订单查询 API 路由
功能：从本地数据库查询产品订单数据，支持统计和分析
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, case
from typing import Optional, List
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

from app.database import get_db
from app.models.product_order import ProductOrder
from app.schemas.product_order import (
    ProductOrderList, OrderQueryParams, OrderStatsResponse
)


router = APIRouter()


@router.get("/", response_model=ProductOrderList)
async def list_orders(
    query: OrderQueryParams = Depends(),
    db: Session = Depends(get_db)
):
    """
    查询本地产品订单列表

    查询条件包括：
    - 零件号：part_number（支持模糊查询）
    - 开始日期：start_date
    - 结束日期：end_date
    """
    db_query = db.query(ProductOrder)

    if query.part_number:
        db_query = db_query.filter(
            (ProductOrder.part_number.contains(query.part_number)) |
            (ProductOrder.u9_material_code.contains(query.part_number))
        )

    if query.doc_no:
        db_query = db_query.filter(ProductOrder.doc_no.contains(query.doc_no))

    if query.doc_state:
        db_query = db_query.filter(ProductOrder.doc_state == query.doc_state)

    if query.doc_type:
        db_query = db_query.filter(ProductOrder.doc_type == query.doc_type)

    if query.start_date:
        db_query = db_query.filter(ProductOrder.query_date >= query.start_date)

    if query.end_date:
        db_query = db_query.filter(ProductOrder.query_date <= query.end_date)

    total = db_query.count()
    offset = (query.page - 1) * query.page_size
    items = db_query.order_by(ProductOrder.query_time.desc()).offset(offset).limit(query.page_size).all()

    return ProductOrderList(total=total, items=items)


@router.get("/stats", response_model=OrderStatsResponse)
async def get_order_stats(
    date: Optional[str] = Query(default=None, description="查询日期 YYYY-MM-DD"),
    db: Session = Depends(get_db)
):
    """获取订单统计信息：总统计 + 指定日期(默认今天)统计"""
    query_date = date if date else datetime.now().strftime('%Y-%m-%d')

    # 一次性查询：总订单数、总计划产量、今日订单数、今日计划产量
    stats = db.query(
        func.count(ProductOrder.id).label('total_orders'),
        func.sum(ProductOrder.planned_output).label('total_planned_output'),
        func.sum(case(
            (ProductOrder.query_date == query_date, 1),
            else_=0
        )).label('today_orders'),
        func.sum(case(
            (ProductOrder.query_date == query_date, ProductOrder.planned_output),
            else_=0
        )).label('today_planned_output')
    ).first()

    return OrderStatsResponse(
        total_orders=stats.total_orders or 0,
        total_planned_output=stats.total_planned_output or 0,
        total_detail_count=stats.total_orders or 0,
        today_orders=stats.today_orders or 0,
        today_planned_output=stats.today_planned_output or 0,
        date=query_date
    )


@router.get("/today")
async def get_today_orders(
    part_number: Optional[str] = Query(default=None, description="零件号"),
    db: Session = Depends(get_db)
):
    """获取今天已查询的订单数据"""
    today = datetime.now().strftime('%Y-%m-%d')

    db_query = db.query(ProductOrder).filter(ProductOrder.query_date == today)

    if part_number:
        db_query = db_query.filter(
            (ProductOrder.part_number.contains(part_number)) |
            (ProductOrder.u9_material_code.contains(part_number))
        )

    total = db_query.count()
    orders = db_query.order_by(ProductOrder.query_time.desc()).all()

    return {
        'total': total,
        'items': orders
    }


@router.delete("/clear-today")
async def clear_today_orders(
    db: Session = Depends(get_db)
):
    """清除今天的订单数据"""
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        count = db.query(ProductOrder).filter(ProductOrder.query_date == today).delete()
        db.commit()
        return {
            'success': True,
            'message': f'已清除{count}条今天的订单数据'
        }
    except Exception as e:
        db.rollback()
        logger.error(f"清除今日订单数据失败：{e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"清除数据失败：{str(e)}")


@router.get("/analysis/comprehensive")
async def get_comprehensive_order_analysis(
    start_date: str = Query(..., description="开始日期 YYYY-MM-DD"),
    end_date: str = Query(..., description="结束日期 YYYY-MM-DD"),
    db: Session = Depends(get_db)
):
    """
    获取订单综合分析数据

    分析维度包括：
    1. 按日期分析：每日订单数量和产量趋势
    2. 按物料分析：各产品的订单分布
    3. 按仓库分析：各仓库的订单分布
    4. 按订单状态分析：开工、完工等状态分布
    5. 按部门分析：各部门的订单分布
    6. 按项目分析：各项目的订单分布
    7. 按订单类型分析：白班、夜班等类型分布
    8. 订单趋势：时间序列趋势数据
    """
    try:
        date_filter = and_(
            ProductOrder.query_date >= start_date,
            ProductOrder.query_date <= end_date
        )

        # 1. 按日期分析 + 汇总统计（合并为一次查询）
        by_date_query = db.query(
            ProductOrder.query_date,
            func.count(ProductOrder.id).label('order_count'),
            func.sum(ProductOrder.planned_output).label('total_planned_output'),
            func.sum(ProductOrder.product_qty).label('total_product_qty')
        ).filter(date_filter).group_by(
            ProductOrder.query_date
        ).order_by(ProductOrder.query_date).all()

        by_date = []
        total_orders = 0
        total_planned_output = 0
        total_product_qty = 0

        for row in by_date_query:
            qty = row.total_product_qty or 0
            planned = row.total_planned_output or 0
            total_orders += row.order_count
            total_planned_output += planned
            total_product_qty += qty
            by_date.append({
                "query_date": row.query_date,
                "order_count": row.order_count,
                "total_planned_output": planned,
                "total_product_qty": qty
            })

        avg_daily_orders = total_orders / len(by_date_query) if by_date_query else 0
        avg_daily_output = total_planned_output / len(by_date_query) if by_date_query else 0

        # 2. 按物料分析（同时提取 TOP5）
        by_material_query = db.query(
            ProductOrder.u9_material_code,
            ProductOrder.part_number,
            ProductOrder.specs,
            func.count(ProductOrder.id).label('order_count'),
            func.sum(ProductOrder.planned_output).label('total_planned_output'),
            func.sum(ProductOrder.product_qty).label('total_product_qty')
        ).filter(date_filter).group_by(
            ProductOrder.u9_material_code, ProductOrder.part_number, ProductOrder.specs
        ).order_by(func.sum(ProductOrder.planned_output).desc()).all()

        by_material = []
        top_materials_list = []
        for i, r in enumerate(by_material_query):
            qty = r.total_product_qty or 0
            material = {
                "u9_material_code": r.u9_material_code,
                "part_number": r.part_number,
                "specs": r.specs,
                "order_count": r.order_count,
                "total_planned_output": r.total_planned_output,
                "total_product_qty": qty,
                "avg_product_qty": qty / r.order_count if r.order_count > 0 else 0
            }
            by_material.append(material)
            if i < 5:
                top_materials_list.append({
                    "u9_material_code": r.u9_material_code,
                    "part_number": r.part_number,
                    "order_count": r.order_count,
                    "total_output": r.total_planned_output
                })

        # 3. 按仓库分析（同时提取 TOP5）
        by_warehouse_query = db.query(
            ProductOrder.complete_wh_code,
            ProductOrder.complete_wh,
            func.count(ProductOrder.id).label('order_count'),
            func.sum(ProductOrder.product_qty).label('total_product_qty'),
            func.sum(ProductOrder.total_complete_qty).label('total_complete_qty'),
            func.sum(ProductOrder.total_eligible_qty).label('total_eligible_qty')
        ).filter(
            and_(date_filter, ProductOrder.complete_wh_code.isnot(None), ProductOrder.complete_wh_code != '')
        ).group_by(
            ProductOrder.complete_wh_code, ProductOrder.complete_wh
        ).order_by(func.sum(ProductOrder.product_qty).desc()).all()

        by_warehouse = []
        top_warehouses_list = []
        for i, r in enumerate(by_warehouse_query):
            warehouse = {
                "complete_wh_code": r.complete_wh_code or 'N/A',
                "complete_wh": r.complete_wh or '未知仓库',
                "order_count": r.order_count,
                "total_product_qty": r.total_product_qty or 0,
                "total_complete_qty": r.total_complete_qty or 0,
                "total_eligible_qty": r.total_eligible_qty or 0
            }
            by_warehouse.append(warehouse)
            if i < 5:
                top_warehouses_list.append({
                    "complete_wh_code": r.complete_wh_code,
                    "complete_wh": r.complete_wh,
                    "order_count": r.order_count,
                    "total_qty": r.total_product_qty or 0
                })

        # 4. 按订单状态分析
        by_doc_state_query = db.query(
            ProductOrder.doc_state,
            func.count(ProductOrder.id).label('order_count'),
            func.sum(ProductOrder.product_qty).label('total_product_qty')
        ).filter(
            and_(date_filter, ProductOrder.doc_state.isnot(None), ProductOrder.doc_state != '')
        ).group_by(ProductOrder.doc_state).order_by(func.count(ProductOrder.id).desc()).all()

        by_doc_state = []
        doc_state_distribution = []
        for r in by_doc_state_query:
            by_doc_state.append({
                "doc_state": r.doc_state or '未知状态',
                "order_count": r.order_count,
                "total_product_qty": r.total_product_qty or 0
            })
            doc_state_distribution.append({
                "doc_state": r.doc_state,
                "count": r.order_count,
                "percentage": round((r.order_count / total_orders * 100), 1) if total_orders > 0 else 0
            })

        # 5. 按部门分析（同时提取 TOP5）
        by_department_query = db.query(
            ProductOrder.department_code,
            ProductOrder.department_name,
            func.count(ProductOrder.id).label('order_count'),
            func.sum(ProductOrder.product_qty).label('total_product_qty')
        ).filter(
            and_(date_filter, ProductOrder.department_code.isnot(None), ProductOrder.department_code != '')
        ).group_by(
            ProductOrder.department_code, ProductOrder.department_name
        ).order_by(func.sum(ProductOrder.product_qty).desc()).all()

        by_department = []
        dept_distribution = []
        for i, r in enumerate(by_department_query):
            by_department.append({
                "department_code": r.department_code or 'N/A',
                "department_name": r.department_name or '未知部门',
                "order_count": r.order_count,
                "total_product_qty": r.total_product_qty or 0
            })
            if i < 5:
                dept_distribution.append({
                    "department_code": r.department_code,
                    "department_name": r.department_name,
                    "count": r.order_count,
                    "total_qty": r.total_product_qty or 0
                })

        # 6. 按项目分析
        by_project_query = db.query(
            ProductOrder.project,
            func.count(ProductOrder.id).label('order_count'),
            func.sum(ProductOrder.product_qty).label('total_product_qty')
        ).filter(
            and_(date_filter, ProductOrder.project.isnot(None), ProductOrder.project != '')
        ).group_by(ProductOrder.project).order_by(func.sum(ProductOrder.product_qty).desc()).all()

        by_project = [{
            "project": r.project or '未知项目',
            "order_count": r.order_count,
            "total_product_qty": r.total_product_qty or 0
        } for r in by_project_query]

        # 7. 按订单类型分析
        by_doc_type_query = db.query(
            ProductOrder.doc_type_code,
            ProductOrder.doc_type,
            func.count(ProductOrder.id).label('order_count'),
            func.sum(ProductOrder.product_qty).label('total_product_qty')
        ).filter(
            and_(date_filter, ProductOrder.doc_type_code.isnot(None), ProductOrder.doc_type_code != '')
        ).group_by(
            ProductOrder.doc_type_code, ProductOrder.doc_type
        ).order_by(func.count(ProductOrder.id).desc()).all()

        by_doc_type = [{
            "doc_type_code": r.doc_type_code or 'N/A',
            "doc_type": r.doc_type or '未知类型',
            "order_count": r.order_count,
            "total_product_qty": r.total_product_qty or 0
        } for r in by_doc_type_query]

        # 8. 趋势对比（前一周期数据）
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        days_diff = (end_dt - start_dt).days + 1
        prev_start = (start_dt - timedelta(days=days_diff)).strftime('%Y-%m-%d')
        prev_end = (start_dt - timedelta(days=1)).strftime('%Y-%m-%d')

        prev_stats = db.query(
            func.count(ProductOrder.id).label('prev_orders'),
            func.sum(ProductOrder.planned_output).label('prev_output')
        ).filter(
            and_(ProductOrder.query_date >= prev_start, ProductOrder.query_date <= prev_end)
        ).first()

        prev_total_orders = prev_stats.prev_orders or 0
        prev_total_output = prev_stats.prev_output or 0

        orders_trend = round(((total_orders - prev_total_orders) / prev_total_orders) * 100, 1) if prev_total_orders > 0 else 0
        output_trend = round(((total_planned_output - prev_total_output) / prev_total_output) * 100, 1) if prev_total_output > 0 else 0

        summary = {
            "total_orders": total_orders,
            "total_planned_output": total_planned_output,
            "total_details": total_orders,
            "total_product_qty": total_product_qty,
            "date_range": f"{start_date} ~ {end_date}",
            "avg_daily_orders": round(avg_daily_orders, 1),
            "avg_daily_output": round(avg_daily_output, 0),
            "top_materials": top_materials_list,
            "top_warehouses": top_warehouses_list,
            "doc_state_distribution": doc_state_distribution,
            "dept_distribution": dept_distribution,
            "orders_trend": orders_trend,
            "output_trend": output_trend,
            "prev_total_orders": prev_total_orders,
            "prev_total_output": prev_total_output
        }

        # 订单趋势（复用 by_date 数据）
        trend = [{
            "date": item["query_date"],
            "order_count": item["order_count"],
            "total_planned_output": item["total_planned_output"],
            "total_product_qty": item["total_product_qty"]
        } for item in by_date]

        return {
            "success": True,
            "data": {
                "date_range": {"start_date": start_date, "end_date": end_date},
                "summary": summary,
                "by_date": by_date,
                "by_material": by_material,
                "by_warehouse": by_warehouse,
                "by_doc_state": by_doc_state,
                "by_department": by_department,
                "by_project": by_project,
                "by_doc_type": by_doc_type,
                "trend": trend
            },
            "message": "获取综合分析数据成功"
        }

    except Exception as e:
        logger.error(f"获取综合分析数据失败：{e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取分析数据失败：{str(e)}")
