"""
Web 管理后台 - 主应用
功能：工艺参数追溯 + 产品加工信息追溯 + 生产看板 + WebSocket 实时通信
"""
import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBearer
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.exc import SQLAlchemyError
import uuid
import time

# 加载 .env 文件中的环境变量
load_dotenv()

from app.routers import dashboard, auth, process_params, processing_events, data_collector, mqtt_topic_configs, materials, product_orders, erp_orders, polling, collector_logs, compressed_params, product_order_logs, product_order_analysis, devices, alarms, data_sources, event_relations, device_status_monitor_configs, db_param_curve, current_product_configs, order_processing_records, workshops, projects, bom, material_categories, order_processing_comparison, production_flows, production_flow_instances, process_definitions, process_param_history, quality_records, event_associations
from app.config import settings
from app.core.response import (
    api_exception_handler,
    validation_exception_handler,
    sqlalchemy_exception_handler,
    generic_exception_handler,
    TimingMiddleware,
    RequestIDMiddleware
)
from app.core.redis_client import init_redis, close_redis, cache_manager
from app.core.cache_middleware import CacheMiddleware, CacheControlMiddleware
from app.services.websocket_service import websocket_endpoint
import threading

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="数据管理后台",
    description="工艺查询系统",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GZip 压缩中间件（压缩超过 500 字节的响应）
app.add_middleware(GZipMiddleware, minimum_size=500)

# 添加自定义中间件
app.add_middleware(TimingMiddleware)
app.add_middleware(RequestIDMiddleware)

# 添加 Redis 缓存中间件
if settings.REDIS_ENABLED:
    app.add_middleware(
        CacheMiddleware,
        default_ttl=settings.CACHE_DEFAULT_EXPIRE
    )
    app.add_middleware(
        CacheControlMiddleware,
        default_max_age=settings.CACHE_DEFAULT_EXPIRE
    )

# 认证路由（无需登录）
app.include_router(auth.router)
app.include_router(process_params.router, prefix="/api/process-params", tags=["工艺参数追溯"])
app.include_router(processing_events.router, prefix="/api/processing-events", tags=["物料加工信息追溯"])
app.include_router(materials.router, prefix="/api/materials", tags=["物料管理"])
app.include_router(materials.router, prefix="/api/products", tags=["物料管理(兼容)"])
app.include_router(product_orders.router, prefix="/api/product-orders", tags=["本地订单查询"])
app.include_router(erp_orders.router, prefix="/api/erp-orders", tags=["ERP订单定时任务管理"])
app.include_router(product_order_logs.router, prefix="/api", tags=["物料订单查询日志"])
app.include_router(product_order_analysis.router, tags=["物料订单分析"])
app.include_router(data_collector.router, prefix="/api/data-collector", tags=["数据采集管理"])
app.include_router(mqtt_topic_configs.router, prefix="/api/mqtt-topic-configs", tags=["MQTT Topic 配置"])
app.include_router(collector_logs.router, prefix="/api", tags=["采集日志管理"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["生产看板"])
app.include_router(compressed_params.router, prefix="/api/compressed-params", tags=["压缩工艺参数追溯"])
app.include_router(device_status_monitor_configs.router, prefix="/api", tags=["设备状态规则配置"])
app.include_router(devices.router, prefix="/api", tags=["设备管理"])
app.include_router(alarms.router, prefix="/api", tags=["报警管理"])
app.include_router(polling.router)
app.include_router(data_sources.router, prefix="/api", tags=["数据源配置管理"])
app.include_router(event_relations.router, prefix="/api", tags=["事件数据关联管理"])
app.include_router(db_param_curve.router, prefix="/api", tags=["DB参数曲线管理"])
app.include_router(current_product_configs.router, prefix="/api", tags=["当前加工物料配置"])
app.include_router(order_processing_records.router, prefix="/api", tags=["订单加工记录"])
app.include_router(workshops.router, prefix="/api/workshops", tags=["车间管理"])
app.include_router(projects.router, prefix="/api/projects", tags=["项目管理"])
app.include_router(bom.router, prefix="/api/bom", tags=["BOM 物料清单管理"])
app.include_router(material_categories.router, prefix="/api/material-categories", tags=["物料分类管理"])
app.include_router(order_processing_comparison.router, prefix="/api", tags=["订单完工比对"])
app.include_router(production_flows.router, prefix="/api", tags=["工艺路线模板"])
app.include_router(production_flow_instances.router, prefix="/api", tags=["流程执行跟踪"])
app.include_router(process_definitions.router, prefix="/api", tags=["工艺管理"])
app.include_router(process_param_history.router, prefix="/api/process-param-histories", tags=["工艺参数历史"])
app.include_router(quality_records.router, prefix="/api", tags=["质量管理"])
app.include_router(event_associations.router, prefix="/api", tags=["事件关联查询"])

# WebSocket 路由
app.add_api_websocket_route("/ws", websocket_endpoint)

# 挂载 Vue 前端静态文件
frontend_dist = Path(__file__).parent.parent / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_dist / "static")), name="static")
    logger.info(f"Vue 前端静态文件目录：{frontend_dist}")
else:
    logger.warning(f"Vue 前端构建目录不存在：{frontend_dist}")


@app.on_event("startup")
async def startup_event():
    """应用启动时自动启动 MQTT 数据采集服务和产品订单定时任务"""
    from app.services.mqtt_collector import collector
    from app.database import get_db
    from app.services.product_order_scheduler import init_scheduler
    from app.services.event_relation_trigger import init_event_relation_trigger
    from app.services.event_relation_scheduler import init_event_relation_scheduler
    import os
    
    # 初始化 Redis
    init_redis()
    
    logger.info("正在启动 MQTT 数据采集服务...")
    
    # 在后台线程启动采集服务，避免阻塞主应用
    thread = threading.Thread(target=collector.start, daemon=True)
    thread.start()
    
    logger.info("MQTT 数据采集服务已在后台启动")

    # 启动工艺参数自动同步服务
    try:
        from app.services.process_param_sync import init_param_sync_service
        sync_interval = float(os.getenv("PARAM_SYNC_INTERVAL", "1"))
        logger.info(f"正在启动工艺参数自动同步服务，间隔：{sync_interval}秒")
        init_param_sync_service(interval=sync_interval)
        logger.info("工艺参数自动同步服务已启动")
    except Exception as e:
        logger.error(f"启动工艺参数自动同步服务失败：{e}")

    # 启动产品订单定时任务
    try:
        # 从环境变量读取 Cron 表达式，默认每30分钟执行一次
        cron_expression = os.getenv("PRODUCT_ORDER_CRON", "*/30 * * * *")
        
        logger.info(f"正在启动产品订单定时任务，Cron 表达式：{cron_expression}")
        init_scheduler(get_db, cron_expression)
        logger.info("产品订单定时任务已启动")
    except Exception as e:
        logger.error(f"启动产品订单定时任务失败：{e}")
    
    # 初始化事件数据关联触发器
    try:
        logger.info("正在初始化事件数据关联触发器...")
        init_event_relation_trigger()
        logger.info("事件数据关联触发器已初始化")
    except Exception as e:
        logger.error(f"初始化事件数据关联触发器失败：{e}")
    
    # 启动事件数据关联定时任务
    try:
        interval = int(os.getenv("EVENT_RELATION_INTERVAL", "300"))
        batch_size = int(os.getenv("EVENT_RELATION_BATCH_SIZE", "100"))

        logger.info(f"正在启动事件数据关联定时任务，间隔={interval}秒，批次大小={batch_size}")
        init_event_relation_scheduler(interval=interval, batch_size=batch_size)
        logger.info("事件数据关联定时任务已启动")
    except Exception as e:
        logger.error(f"启动事件数据关联定时任务失败：{e}")

    # 初始化订单加工关联触发器
    try:
        from app.services.order_processing_trigger import init_order_processing_trigger
        logger.info("正在初始化订单加工关联触发器...")
        init_order_processing_trigger()
        logger.info("订单加工关联触发器已初始化")
    except Exception as e:
        logger.error(f"初始化订单加工关联触发器失败：{e}")

    # 启动订单加工定时调度
    try:
        from app.services.order_processing_scheduler import init_order_processing_scheduler
        op_interval = int(os.getenv("ORDER_PROCESSING_RECONCILE_INTERVAL", "600"))
        op_batch_size = int(os.getenv("ORDER_PROCESSING_BATCH_SIZE", "100"))

        logger.info(f"正在启动订单加工定时任务，间隔={op_interval}秒，批次大小={op_batch_size}")
        init_order_processing_scheduler(interval=op_interval, batch_size=op_batch_size)
        logger.info("订单加工定时任务已启动")
    except Exception as e:
        logger.error(f"启动订单加工定时任务失败：{e}")


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时清理资源"""
    close_redis()
    logger.info("应用已关闭")


@app.get("/", response_class=HTMLResponse)
async def root():
    """首页 - Vue 前端"""
    index_path = Path(__file__).parent.parent / "frontend" / "dist" / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    return {
        "message": "数据管理后台运行正常",
        "version": "1.0.0",
        "docs": "/docs",
        "admin": "/admin",
        "dashboard": "/dashboard"
    }


@app.get("/health")
async def health_check():
    health_data = {"status": "healthy"}
    
    # 检查 Redis 状态
    if settings.REDIS_ENABLED:
        try:
            client = cache_manager.client
            if client and client.ping():
                health_data["redis"] = "connected"
            else:
                health_data["redis"] = "disconnected"
        except Exception:
            health_data["redis"] = "error"
    
    return health_data


# 注册异常处理器
app.add_exception_handler(Exception, generic_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(HTTPException, generic_exception_handler)

# 添加 FastAPI 内置的验证异常处理器
from fastapi.exceptions import RequestValidationError
app.add_exception_handler(RequestValidationError, validation_exception_handler)


@app.get("/admin", response_class=HTMLResponse)
async def admin_page():
    """管理后台页面 - Vue 前端"""
    index_path = Path(__file__).parent.parent / "frontend" / "dist" / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    return FileResponse("templates/index.html")


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page():
    """生产看板页面 - Vue 前端"""
    index_path = Path(__file__).parent.parent / "frontend" / "dist" / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    return FileResponse("templates/dashboard.html")


@app.get("/{full_path:path}", response_class=HTMLResponse)
async def catch_all(full_path: str):
    """Vue Router catch-all 路由 - 支持前端路由"""
    index_path = Path(__file__).parent.parent / "frontend" / "dist" / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    return {"error": "Frontend not built"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
