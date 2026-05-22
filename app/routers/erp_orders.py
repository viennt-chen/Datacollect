"""
ERP U9 订单定时任务管理 API 路由
功能：管理物料订单定时查询任务的启动、停止、状态查询和手动触发
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from datetime import datetime
import asyncio
import logging

logger = logging.getLogger(__name__)

from app.database import get_db
from app.models.product_order import ProductOrder
from app.models.material import Material
from app.services.u9_service import U9Service, U9ServiceError

router = APIRouter()


async def query_u9_order(specs: str, start_date: str, end_date: str, item_code: str = "") -> List[Dict[str, Any]]:
    """查询 U9 ERP 系统的订单数据"""
    return await U9Service.query_mo_orders(specs, start_date, end_date, item_code)


async def query_u9_order_with_details(specs: str, start_date: str, end_date: str, item_code: str = "") -> Dict[str, Any]:
    """查询 U9 ERP 系统的订单数据（包含详细信息）"""
    try:
        orders = await query_u9_order(specs, start_date, end_date, item_code)
        planned_output = sum(order.get('productQty', 0) for order in orders)
        return {
            "planned_output": planned_output,
            "specs": specs,
            "date": start_date,
            "details": orders
        }
    except Exception as e:
        logger.error(f"查询订单详情失败 [specs={specs}, item_code={item_code}]: {e}", exc_info=True)
        return {
            "planned_output": 0,
            "specs": specs,
            "date": start_date,
            "details": []
        }


async def save_order_to_db_with_upsert(
    db: Session,
    part_number: str,
    u9_material_code: str,
    specs: str,
    order_data: Dict[str, Any],
    query_date: str
) -> int:
    """保存订单数据到数据库（按 doc_no upsert，单表结构）"""
    try:
        query_time = datetime.now()
        details = order_data.get('details', [])
        saved_count = 0
        seen_doc_nos = set()

        for detail_data in details:
            doc_no = detail_data.get('docNo', '')
            item_code = detail_data.get('itemCode', '')

            if not doc_no or not item_code:
                continue

            if doc_no in seen_doc_nos:
                logger.warning(f"跳过重复订单号（批次内）：{doc_no}")
                continue
            seen_doc_nos.add(doc_no)

            start_date_str = detail_data.get('startDate', '')
            start_date = None
            if start_date_str:
                try:
                    if ' ' in start_date_str:
                        start_date = datetime.strptime(start_date_str, '%Y-%m-%d %H:%M:%S')
                    else:
                        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
                except:
                    pass

            existing = db.query(ProductOrder).filter(ProductOrder.doc_no == doc_no).first()

            if existing:
                existing.part_number = part_number
                existing.u9_material_code = u9_material_code
                existing.specs = detail_data.get('specs', '') or specs
                existing.item_code = item_code
                existing.item_name = detail_data.get('itemName', '')
                existing.planned_output = order_data.get('planned_output', 0)
                existing.query_date = query_date
                existing.product_qty = detail_data.get('productQty', 0)
                existing.total_complete_qty = detail_data.get('totalCompleteQty', 0)
                existing.total_eligible_qty = detail_data.get('totalEligibleQty', 0)
                existing.total_scrap_qty = detail_data.get('totalScrapQty', 0)
                existing.complete_wh = detail_data.get('completeWh', '')
                existing.complete_wh_code = detail_data.get('completeWhCode', '')
                existing.line_number = detail_data.get('lineNumber', '')
                existing.line_code = detail_data.get('lineCode', '')
                existing.line_description = detail_data.get('lineDescription', '')
                existing.department_code = detail_data.get('departmentCode', '')
                existing.department_name = detail_data.get('departmentName', '')
                existing.doc_type_code = detail_data.get('docTypeCode', '')
                existing.doc_type = detail_data.get('docType', '')
                existing.doc_state = detail_data.get('docState', '')
                existing.project = detail_data.get('project', '')
                existing.mold_no = detail_data.get('moldNo', '')
                existing.cavity_number = detail_data.get('cavityNumber', '')
                existing.short_code = detail_data.get('shortCode', '')
                existing.packet_qty = detail_data.get('packetQty', 0)
                existing.cycle_time = detail_data.get('cycleTime', '')
                existing.machine = detail_data.get('machine', '')
                existing.over_rate = detail_data.get('overRate', 0)
                existing.start_date = start_date
                existing.description = detail_data.get('description', '')
                existing.query_time = query_time
            else:
                order = ProductOrder(
                    doc_no=doc_no,
                    part_number=part_number,
                    u9_material_code=u9_material_code,
                    specs=detail_data.get('specs', '') or specs,
                    item_code=item_code,
                    item_name=detail_data.get('itemName', ''),
                    planned_output=order_data.get('planned_output', 0),
                    query_date=query_date,
                    product_qty=detail_data.get('productQty', 0),
                    total_complete_qty=detail_data.get('totalCompleteQty', 0),
                    total_eligible_qty=detail_data.get('totalEligibleQty', 0),
                    total_scrap_qty=detail_data.get('totalScrapQty', 0),
                    complete_wh=detail_data.get('completeWh', ''),
                    complete_wh_code=detail_data.get('completeWhCode', ''),
                    line_number=detail_data.get('lineNumber', ''),
                    line_code=detail_data.get('lineCode', ''),
                    line_description=detail_data.get('lineDescription', ''),
                    department_code=detail_data.get('departmentCode', ''),
                    department_name=detail_data.get('departmentName', ''),
                    doc_type_code=detail_data.get('docTypeCode', ''),
                    doc_type=detail_data.get('docType', ''),
                    doc_state=detail_data.get('docState', ''),
                    project=detail_data.get('project', ''),
                    mold_no=detail_data.get('moldNo', ''),
                    cavity_number=detail_data.get('cavityNumber', ''),
                    short_code=detail_data.get('shortCode', ''),
                    packet_qty=detail_data.get('packetQty', 0),
                    cycle_time=detail_data.get('cycleTime', ''),
                    machine=detail_data.get('machine', ''),
                    over_rate=detail_data.get('overRate', 0),
                    start_date=start_date,
                    description=detail_data.get('description', ''),
                    query_time=query_time
                )
                db.add(order)

            saved_count += 1

        db.commit()
        return saved_count

    except Exception as e:
        db.rollback()
        logger.error(f"保存订单失败（upsert）：{str(e)}", exc_info=True)
        return 0


@router.get("/query-single-part")
async def query_single_part(
    start_date: str = Query(..., description="开始日期 YYYY-MM-DD"),
    end_date: str = Query(..., description="结束日期 YYYY-MM-DD"),
    part_number: Optional[str] = Query(default=None, description="零件号"),
    u9_material_code: Optional[str] = Query(default=None, description="U9 物料号"),
    db: Session = Depends(get_db)
):
    """查询单个零件的 ERP 订单数据"""
    try:
        # 从物料表获取规格型号和单件工时
        product = None
        specs = ""
        if u9_material_code:
            product = db.query(Material).filter(Material.u9_material_code == u9_material_code).first()
        elif part_number:
            product = db.query(Material).filter(Material.part_number == part_number).first()

        if product:
            specs = product.specification or ""
            unit_work_time = float(product.unit_work_time) if product.unit_work_time else None
        else:
            # 没有产品记录时，用零件号作为 specs 查询
            specs = part_number or u9_material_code or ""
            unit_work_time = None

        # 调用 U9 ERP 查询
        item_code = u9_material_code or ""
        orders = await U9Service.query_mo_orders(specs, start_date, end_date, item_code)

        planned_output = sum(order.get('productQty', 0) for order in orders)

        return {
            "success": True,
            "data": {
                "planned_output": planned_output,
                "specs": specs,
                "unit_work_time": unit_work_time,
                "date": start_date,
                "details": orders
            }
        }
    except U9ServiceError as e:
        logger.error(f"查询单个零件订单失败：{e}", exc_info=True)
        raise HTTPException(status_code=502, detail=f"U9 ERP 查询失败：{str(e)}")
    except Exception as e:
        logger.error(f"查询单个零件订单失败：{e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"查询失败：{str(e)}")


@router.post("/query-orders-by-time")
async def query_orders_by_time(
    data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """按时间范围批量查询订单并保存到数据库"""
    try:
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        filter_part_number = data.get('part_number')

        if not start_date or not end_date:
            raise HTTPException(status_code=400, detail="请提供 start_date 和 end_date")

        # 获取所有启用的物料
        query = db.query(Material).filter(Material.status == 'active')
        if filter_part_number:
            query = query.filter(Material.part_number.contains(filter_part_number))
        products = query.all()

        if not products:
            return {
                "success": True,
                "total_queried": 0,
                "total_saved": 0,
                "message": "没有找到匹配的产品",
                "results": []
            }

        total_saved = 0
        results = []
        query_time = datetime.now()
        query_date = query_time.strftime('%Y-%m-%d')

        for product in products:
            specs = product.specification or ""
            item_code = product.u9_material_code or ""
            part_number = product.part_number or ""

            try:
                orders = await U9Service.query_mo_orders(specs, start_date, end_date, item_code)
                planned_output = sum(order.get('productQty', 0) for order in orders)

                order_data = {
                    "planned_output": planned_output,
                    "specs": specs,
                    "date": start_date,
                    "details": orders
                }

                saved = await save_order_to_db_with_upsert(
                    db, part_number, item_code, specs, order_data, query_date
                )
                total_saved += saved

                results.append({
                    "part_number": part_number,
                    "material_code": item_code,
                    "specs": specs,
                    "planned_output": planned_output,
                    "order_count": len(orders),
                    "saved_count": saved,
                    "status": "success",
                    "error": None
                })
            except Exception as e:
                logger.error(f"查询产品 {part_number} ({item_code}) 失败：{e}")
                results.append({
                    "part_number": part_number,
                    "material_code": item_code,
                    "specs": specs,
                    "planned_output": 0,
                    "order_count": 0,
                    "saved_count": 0,
                    "status": "failed",
                    "error": str(e)
                })

        return {
            "success": True,
            "total_queried": len(products),
            "total_saved": total_saved,
            "message": f"批量查询完成，共查询 {len(products)} 个产品，保存 {total_saved} 条订单",
            "results": results
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"批量查询订单失败：{e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"批量查询失败：{str(e)}")


@router.post("/query-today-by-part")
async def query_today_by_part(
    data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """按零件号查询今日 ERP 订单并保存"""
    try:
        part_number = data.get('part_number')
        u9_material_code = data.get('u9_material_code')

        if not part_number and not u9_material_code:
            raise HTTPException(status_code=400, detail="请提供 part_number 或 u9_material_code")

        today = datetime.now().strftime('%Y-%m-%d')

        # 从物料表获取信息
        product = None
        if u9_material_code:
            product = db.query(Material).filter(Material.u9_material_code == u9_material_code).first()
        elif part_number:
            product = db.query(Material).filter(Material.part_number == part_number).first()

        specs = product.specification if product and product.specification else (part_number or u9_material_code or "")
        item_code = product.u9_material_code if product else (u9_material_code or "")
        pn = product.part_number if product else (part_number or "")
        unit_work_time = float(product.unit_work_time) if product and product.unit_work_time else None

        # 查询 U9
        orders = await U9Service.query_mo_orders(specs, today, today, item_code)
        planned_output = sum(order.get('productQty', 0) for order in orders)

        # 保存到数据库
        order_data = {
            "planned_output": planned_output,
            "specs": specs,
            "date": today,
            "details": orders
        }
        saved = await save_order_to_db_with_upsert(db, pn, item_code, specs, order_data, today)

        return {
            "success": True,
            "data": {
                "planned_output": planned_output,
                "specs": specs,
                "unit_work_time": unit_work_time,
                "date": today,
                "details": orders
            },
            "saved_count": saved,
            "message": f"查询成功，共 {len(orders)} 条订单"
        }
    except U9ServiceError as e:
        logger.error(f"查询今日订单失败：{e}", exc_info=True)
        raise HTTPException(status_code=502, detail=f"U9 ERP 查询失败：{str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"查询今日订单失败：{e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"查询失败：{str(e)}")


@router.post("/query-today-orders")
async def query_today_orders(
    part_number: Optional[str] = Query(default=None, description="零件号（可选）"),
    db: Session = Depends(get_db)
):
    """查询今日所有订单（从本地数据库）"""
    today = datetime.now().strftime('%Y-%m-%d')

    query = db.query(ProductOrder).filter(ProductOrder.query_date == today)
    if part_number:
        query = query.filter(
            (ProductOrder.part_number.contains(part_number)) |
            (ProductOrder.u9_material_code.contains(part_number))
        )

    orders = query.order_by(ProductOrder.query_time.desc()).all()

    return {
        "success": True,
        "total": len(orders),
        "data": orders,
        "date": today
    }


@router.get("/scheduler/status")
async def get_scheduler_status():
    """获取定时任务状态"""
    from app.services.product_order_scheduler import get_scheduler
    scheduler = get_scheduler()
    if not scheduler:
        raise HTTPException(status_code=400, detail="定时任务未初始化")
    return scheduler.get_status()


@router.post("/scheduler/start")
async def start_scheduler(cron_expression: Optional[str] = Query(None, description="Cron 表达式，例如：0 2 * * *")):
    """启动定时任务"""
    from app.services.product_order_scheduler import get_scheduler, start_scheduler as scheduler_start
    scheduler = get_scheduler()
    if not scheduler:
        raise HTTPException(status_code=400, detail="定时任务未初始化")
    scheduler_start(cron_expression)
    return {
        'success': True,
        'message': f'定时任务已启动，Cron 表达式：{cron_expression or "0 2 * * *"}'
    }


@router.post("/scheduler/stop")
async def stop_scheduler():
    """停止定时任务"""
    from app.services.product_order_scheduler import get_scheduler, stop_scheduler as scheduler_stop
    scheduler = get_scheduler()
    if not scheduler:
        raise HTTPException(status_code=400, detail="定时任务未初始化")
    scheduler_stop()
    return {
        'success': True,
        'message': '定时任务已停止'
    }


@router.post("/scheduler/trigger")
async def trigger_scheduler():
    """立即触发一次查询"""
    from app.services.product_order_scheduler import get_scheduler

    scheduler = get_scheduler()
    if not scheduler:
        raise HTTPException(status_code=400, detail="定时任务未初始化")

    asyncio.create_task(scheduler.run_auto_query())

    return {
        'success': True,
        'message': '已触发立即查询'
    }
