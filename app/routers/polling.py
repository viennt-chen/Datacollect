"""
产品订单日志轮询 API 路由
功能：提供产品订单日志的轮询功能，包括配置、状态监控和数据获取
"""
from fastapi import APIRouter, HTTPException
from typing import Optional
from datetime import datetime

from app.services.ProductOrderinQuiry import (
    polling_config,
    polling_logs,
    polling_lock,
    is_polling_active,
    last_poll_time,
    last_error,
    total_logs_fetched,
    start_polling,
    stop_polling,
    fetch_product_order_logs,
    PollingConfig,
    PollingStatusResponse,
    PollingLogsResponse,
    ServiceControlResponse,
    PollingStatus
)

router = APIRouter(prefix="/api/polling", tags=["产品订单日志轮询"])


@router.get("/config", response_model=PollingConfig)
async def get_polling_config_endpoint():
    """获取轮询配置"""
    return polling_config


@router.put("/config", response_model=PollingConfig)
async def update_polling_config_endpoint(config: PollingConfig):
    """更新轮询配置"""
    global polling_config
    polling_config = config
    polling_config.last_updated = datetime.now().isoformat()
    
    # 根据配置决定是否启动或停止轮询
    if config.enabled:
        start_polling()
    else:
        stop_polling()
    
    return polling_config


@router.get("/status", response_model=PollingStatusResponse)
async def get_polling_status_endpoint():
    """获取轮询状态"""
    with polling_lock:
        status = PollingStatus.RUNNING if is_polling_active and polling_config.enabled else (
            PollingStatus.STOPPED if not polling_config.enabled else PollingStatus.ERROR
        )
        
        return PollingStatusResponse(
            status=status,
            is_active=is_polling_active and polling_config.enabled,
            last_poll_time=last_poll_time,
            last_error=last_error,
            total_logs_fetched=total_logs_fetched,
            config=polling_config
        )


@router.get("/logs", response_model=PollingLogsResponse)
async def get_polling_logs_endpoint():
    """获取轮询获取的日志数据"""
    with polling_lock:
        return PollingLogsResponse(
            success=True,
            message="获取产品订单日志成功",
            data=polling_logs,
            total_count=len(polling_logs),
            last_updated=datetime.now().isoformat()
        )


@router.post("/start", response_model=ServiceControlResponse)
async def start_polling_endpoint_wrapper():
    """启动轮询"""
    global polling_config
    polling_config.enabled = True
    start_polling()
    return ServiceControlResponse(
        success=True,
        message="轮询已启动",
        timestamp=datetime.now().isoformat()
    )


@router.post("/stop", response_model=ServiceControlResponse)
async def stop_polling_endpoint_wrapper():
    """停止轮询"""
    global polling_config
    polling_config.enabled = False
    stop_polling()
    return ServiceControlResponse(
        success=True,
        message="轮询已停止",
        timestamp=datetime.now().isoformat()
    )