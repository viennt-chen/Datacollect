from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import requests
import json
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
import signal
import sys
import os
import subprocess
from pathlib import Path
import asyncio
import threading
from dataclasses import dataclass
from enum import Enum

app = FastAPI(
    title="U9 接口服务 API",
    description="为数据大屏提供 U9 ERP 系统的计划总产量数据",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

def signal_handler(signum, frame):
    print(f"\n收到信号 {signum}，正在关闭服务...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# Only run startup logic when running as standalone service
if __name__ == '__main__':
    @app.on_event("startup")
    async def startup_event():
        print("=" * 50)
        print("U9 接口服务已启动")
        print(f"服务地址: http://localhost:5001")
        print(f"Swagger 文档: http://localhost:5001/docs")
        print("=" * 50)
        
        # 启动轮询机制（如果配置为启用）
        if polling_config.enabled:
            start_polling()
            print("产品订单日志轮询已启动")
        else:
            print("产品订单日志轮询未启用")
else:
    # When imported as a module, initialize polling if needed
    # But don't start it automatically to avoid conflicts with main app
    pass

# Only run shutdown logic when running as standalone service
if __name__ == '__main__':
    @app.on_event("shutdown")
    async def shutdown_event():
        print("=" * 50)
        print("U9 接口服务正在关闭...")
        # 停止轮询机制
        stop_polling()
        print("产品订单日志轮询已停止")
        print("服务已关闭")
        print("=" * 50)
else:
    # When imported as a module, provide a shutdown function if needed
    pass

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

U9_API_URL = "https://erp.jsxq.group/U9/RestServices/COM.XQ.WMS.IQryWMSMO.svc/Do"


class HealthResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "message": "U9 后端服务运行正常",
                "timestamp": "2026-03-18T09:39:30.185727"
            }
        }
    )
    
    success: bool
    message: str
    timestamp: str

class PlannedOutputResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "planned_output": 1000,
                "specs": "2025630-30-B",
                "date": "2026-03-18",
                "details": [
                    {
                        "cavityNumber": "",
                        "completeWh": "半成品库-二车间（SH）",
                        "completeWhCode": "WH02",
                        "docNo": "DMO202603180001",
                        "itemCode": "2025630-30-B",
                        "itemDescription": "产品描述",
                        "productQty": 1000,
                        "specs": "2025630-30-B"
                    }
                ]
            }
        }
    )
    
    planned_output: int = Field(..., description="计划总产量")
    specs: str = Field(..., description="规格型号")
    date: str = Field(..., description="查询日期")
    details: List[Dict[str, Any]] = Field(..., description="详细信息")

class SuccessResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "data": {
                    "planned_output": 1000,
                    "specs": "2025630-30-B",
                    "date": "2026-03-18",
                    "details": []
                },
                "message": "获取计划总产量成功"
            }
        }
    )
    
    success: bool
    data: PlannedOutputResponse
    message: str

@app.get("/", response_model=HealthResponse, tags=["系统"])
async def root():
    return HealthResponse(
        success=True,
        message="U9 后端服务运行正常",
        timestamp=datetime.now().isoformat()
    )

@app.get("/api/u9/health", response_model=HealthResponse, tags=["系统"])
async def health_check():
    return HealthResponse(
        success=True,
        message="U9 后端服务运行正常",
        timestamp=datetime.now().isoformat()
    )

class ServiceControlResponse(BaseModel):
    success: bool
    message: str
    timestamp: str


class PollingConfig(BaseModel):
    """轮询配置"""
    interval_seconds: int = Field(default=60, ge=10, le=3600, description="轮询间隔（秒），范围10-3600")
    enabled: bool = Field(default=True, description="是否启用轮询")
    last_updated: Optional[str] = Field(default=None, description="最后更新时间")


class ProductOrderLog(BaseModel):
    """产品订单日志模型"""
    docNo: str = Field(..., description="单据编号")
    itemCode: str = Field(..., description="物料编码")
    itemDescription: str = Field(..., description="物料描述")
    productQty: int = Field(..., description="生产数量")
    specs: str = Field(..., description="规格型号")
    completeWh: str = Field(..., description="完成仓库")
    completeWhCode: str = Field(..., description="完成仓库编码")
    cavityNumber: Optional[str] = Field(default="", description="腔体号")
    timestamp: str = Field(..., description="记录时间戳")


class PollingStatus(str, Enum):
    """轮询状态枚举"""
    STOPPED = "stopped"
    RUNNING = "running"
    ERROR = "error"


class PollingStatusResponse(BaseModel):
    """轮询状态响应"""
    status: PollingStatus
    is_active: bool
    last_poll_time: Optional[str] = None
    last_error: Optional[str] = None
    total_logs_fetched: int
    config: PollingConfig


class PollingLogsResponse(BaseModel):
    """轮询日志响应"""
    success: bool
    message: str
    data: List[ProductOrderLog]
    total_count: int
    last_updated: str

def get_python_exe():
    return r"C:\Users\Chen\miniconda3\envs\fastapi\python.exe"


def fetch_product_order_logs(specs: str = "") -> List[Dict[str, Any]]:
    """
    获取产品订单日志数据
    """
    global last_error
    
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        params = {
            "context": {
                "CultureName": "zh-CN",
                "EntCode": "001",
                "OrgCode": "28",
                "UserCode": "shsbhyz"
            }, 
            "startDate": today,
            "endDate": today,
            "docType": "DMO",
            "itemCode": "",
            "dept": "",
            "specs": specs if specs else "2161521-10-B"
        }
        
        headers = {"Content-Type": "application/json"}
        response = requests.post(U9_API_URL, json=params, headers=headers, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        if not data.get('d'):
            return []
        
        if 'd' in data:
            outer_data = data['d']
            if not outer_data:
                return []
                
            cleaned_data = outer_data.replace('\r\n', '\n').replace('\\r\\n', '\\n').replace('\\\\', '\\')
            parsed_data = json.loads(cleaned_data)
            
            if 'msg' in parsed_data:
                msg_data = parsed_data['msg']
                
                if not msg_data:
                    return []
                
                try:
                    if isinstance(msg_data, str):
                        msg_data = json.loads(msg_data)
                except:
                    pass
                
                if isinstance(msg_data, list) and len(msg_data) > 0:
                    return msg_data
                else:
                    return []
            else:
                last_error = "U9 接口返回数据格式错误: 缺少 msg 字段"
                return []
        else:
            last_error = "U9 接口返回数据格式错误: 缺少 d 字段"
            return []
            
    except requests.exceptions.RequestException as e:
        last_error = f"网络请求失败: {str(e)}"
        return []
    except json.JSONDecodeError as e:
        last_error = f"JSON 解析失败: {str(e)}"
        return []
    except Exception as e:
        last_error = f"获取产品订单日志时发生错误: {str(e)}"
        return []


async def polling_worker():
    """
    轮询工作函数，在后台定期获取产品订单日志
    """
    global polling_logs, last_poll_time, last_error, total_logs_fetched, is_polling_active
    
    is_polling_active = True
    while polling_config.enabled:
        try:
            # 获取当前时间作为本次轮询的时间
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # 获取产品订单日志
            raw_logs = fetch_product_order_logs()
            
            if raw_logs:
                # 转换原始数据为 ProductOrderLog 对象
                new_logs = []
                for log in raw_logs:
                    product_log = ProductOrderLog(
                        docNo=log.get('docNo', ''),
                        itemCode=log.get('itemCode', ''),
                        itemDescription=log.get('itemDescription', ''),
                        productQty=log.get('productQty', 0),
                        specs=log.get('specs', ''),
                        completeWh=log.get('completeWh', ''),
                        completeWhCode=log.get('completeWhCode', ''),
                        cavityNumber=log.get('cavityNumber', ''),
                        timestamp=current_time
                    )
                    new_logs.append(product_log)
                
                # 更新全局日志列表
                with polling_lock:
                    # 保留最近的100条日志以防止内存无限增长
                    polling_logs.extend(new_logs)
                    polling_logs = polling_logs[-100:]
                    total_logs_fetched += len(new_logs)
                
                last_poll_time = current_time
                last_error = None
            
            # 等待指定的轮询间隔
            await asyncio.sleep(polling_config.interval_seconds)
            
        except Exception as e:
            last_error = f"轮询过程中发生错误: {str(e)}"
            # 发生错误后等待一段时间再继续
            await asyncio.sleep(polling_config.interval_seconds)


def start_polling():
    """
    启动轮询任务
    """
    global polling_task, is_polling_active
    if polling_task is None or polling_task.done():
        is_polling_active = True
        polling_task = asyncio.create_task(polling_worker())


def stop_polling():
    """
    停止轮询任务
    """
    global polling_task, is_polling_active
    if polling_task and not polling_task.done():
        polling_task.cancel()
        is_polling_active = False

def get_app_path():
    return r"c:\Users\Chen\Desktop\chufengkou\backend\app.py"

def kill_existing_service():
    try:
        result = subprocess.run(
            ['powershell', '-Command', 
             f"Get-NetTCPConnection -LocalPort 5001 -ErrorAction SilentlyContinue | "
             f"Select-Object -ExpandProperty OwningProcess | "
             f"ForEach-Object {{ Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue }}"],
            capture_output=True, text=True
        )
    except:
        pass

def start_service_background():
    python_exe = get_python_exe()
    app_path = get_app_path()
    subprocess.Popen(
        [python_exe, app_path],
        cwd=str(Path(app_path).parent),
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == 'win32' else 0
    )

@app.post("/api/u9/service/restart", response_model=ServiceControlResponse, tags=["服务控制"])
async def restart_service():
    kill_existing_service()
    await asyncio.sleep(2)
    start_service_background()
    return ServiceControlResponse(
        success=True,
        message="服务重启成功",
        timestamp=datetime.now().isoformat()
    )

@app.post("/api/u9/service/stop", response_model=ServiceControlResponse, tags=["服务控制"])
async def stop_service():
    kill_existing_service()
    return ServiceControlResponse(
        success=True,
        message="服务已停止",
        timestamp=datetime.now().isoformat()
    )

@app.post("/api/u9/service/start", response_model=ServiceControlResponse, tags=["服务控制"])
async def start_service():
    start_service_background()
    return ServiceControlResponse(
        success=True,
        message="服务启动成功",
        timestamp=datetime.now().isoformat()
    )

@app.get("/api/u9/service/status", response_model=ServiceControlResponse, tags=["服务控制"])
async def service_status():
    try:
        result = subprocess.run(
            ['powershell', '-Command', 
             "Get-NetTCPConnection -LocalPort 5001 -State Listen -ErrorAction SilentlyContinue | "
             "Measure-Object | Select-Object -ExpandProperty Count"],
            capture_output=True, text=True
        )
        is_running = result.stdout.strip() == "1"
        if is_running:
            return ServiceControlResponse(
                success=True,
                message="服务正在运行",
                timestamp=datetime.now().isoformat()
            )
        else:
            return ServiceControlResponse(
                success=False,
                message="服务未运行",
                timestamp=datetime.now().isoformat()
            )
    except:
        return ServiceControlResponse(
            success=False,
            message="无法检查服务状态",
            timestamp=datetime.now().isoformat()
        )

@app.get("/api/u9/get-planned-output", response_model=SuccessResponse, tags=["U9接口"])
async def get_planned_output(
    specs: Optional[str] = Query(default="2161521-10-B", description="规格型号"),
    startDate: Optional[str] = Query(default=None, description="开始日期 YYYY-MM-DD"),
    endDate: Optional[str] = Query(default=None, description="结束日期 YYYY-MM-DD")
):
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        query_start_date = startDate if startDate else today
        query_end_date = endDate if endDate else today
        params = {
            "context": {
                "CultureName": "zh-CN",
                "EntCode": "001",
                "OrgCode": "28",
                "UserCode": "shsbhyz"
            }, 
            "startDate": query_start_date,
            "endDate": query_end_date,
            "docType": "DMO",
            "itemCode": "",
            "dept": "",
            "specs": specs
        }
        
        headers = {"Content-Type": "application/json"}
        response = requests.post(U9_API_URL, json=params, headers=headers, timeout=30)
        
        response.raise_for_status()
        
        data = response.json()
        
        if not data.get('d'):
            return SuccessResponse(
                success=True,
                data=PlannedOutputResponse(
                    planned_output=0,
                    specs=specs,
                    date=today,
                    details=[]
                ),
                message="U9 接口返回空数据"
            )
        
        if 'd' in data:
            outer_data = data['d']
            if not outer_data:
                return SuccessResponse(
                    success=True,
                    data=PlannedOutputResponse(
                        planned_output=0,
                        specs=specs,
                        date=today,
                        details=[]
                    ),
                    message="U9 接口返回空数据"
                )
            cleaned_data = outer_data.replace('\r\n', '\n').replace('\\r\\n', '\\n').replace('\\\\', '\\')
            parsed_data = json.loads(cleaned_data)
            
            if 'msg' in parsed_data:
                msg_data = parsed_data['msg']
                
                if not msg_data:
                    return SuccessResponse(
                        success=True,
                        data=PlannedOutputResponse(
                            planned_output=0,
                            specs=specs,
                            date=today,
                            details=[]
                        ),
                        message="U9 接口返回空数据"
                    )
                
                try:
                    if isinstance(msg_data, str):
                        msg_data = json.loads(msg_data)
                except:
                    pass
                
                if isinstance(msg_data, list) and len(msg_data) > 0:
                    planned_output = msg_data[0].get('productQty', 0) if msg_data else 0
                    
                    return SuccessResponse(
                        success=True,
                        data=PlannedOutputResponse(
                            planned_output=planned_output,
                            specs=specs,
                            date=today,
                            details=msg_data
                        ),
                        message="获取计划总产量成功"
                    )
                else:
                    return SuccessResponse(
                        success=True,
                        data=PlannedOutputResponse(
                            planned_output=0,
                            specs=specs,
                            date=today,
                            details=[]
                        ),
                        message="U9 接口返回空数据"
                    )
            else:
                raise HTTPException(
                    status_code=500,
                    detail="U9 接口返回数据格式错误: 缺少 msg 字段"
                )
        else:
            raise HTTPException(
                status_code=500,
                detail="U9 接口返回数据格式错误: 缺少 d 字段"
            )
            
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=500,
            detail=f"网络请求失败: {str(e)}"
        )
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=500,
            detail=f"JSON 解析失败: {str(e)}, 原始数据: {data.get('d', '')[:200] if data.get('d') else 'None'}"
        )
    except Exception as e:
        import traceback
        raise HTTPException(
            status_code=500,
            detail=f"服务器内部错误: {str(e)}\n{traceback.format_exc()}"
        )


# 新增产品订单日志轮询相关端点
async def get_polling_config():
    """获取轮询配置"""
    return polling_config


async def update_polling_config(config: PollingConfig):
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


async def get_polling_status():
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


async def get_polling_logs():
    """获取轮询获取的日志数据"""
    with polling_lock:
        return PollingLogsResponse(
            success=True,
            message="获取产品订单日志成功",
            data=polling_logs,
            total_count=len(polling_logs),
            last_updated=datetime.now().isoformat()
        )


async def start_polling_endpoint():
    """启动轮询"""
    global polling_config
    polling_config.enabled = True
    start_polling()
    return ServiceControlResponse(
        success=True,
        message="轮询已启动",
        timestamp=datetime.now().isoformat()
    )


async def stop_polling_endpoint():
    """停止轮询"""
    global polling_config
    polling_config.enabled = False
    stop_polling()
    return ServiceControlResponse(
        success=True,
        message="轮询已停止",
        timestamp=datetime.now().isoformat()
    )

# 全局变量用于存储轮询状态和数据
polling_config = PollingConfig(interval_seconds=60, enabled=True)
polling_logs: List[ProductOrderLog] = []
polling_lock = threading.Lock()
polling_task = None
last_poll_time: Optional[str] = None
last_error: Optional[str] = None
total_logs_fetched = 0
is_polling_active = False


def initialize_polling():
    """Initialize polling when module is imported"""
    global polling_task
    # Initialize polling task variable but don't start it automatically
    if 'polling_task' not in globals():
        globals()['polling_task'] = None


# Initialize when module is loaded
initialize_polling()


# API routes for standalone service
@app.get("/api/u9/polling/config", response_model=PollingConfig, tags=["产品订单日志轮询"])
async def get_polling_config_endpoint():
    """获取轮询配置"""
    return await get_polling_config()


@app.put("/api/u9/polling/config", response_model=PollingConfig, tags=["产品订单日志轮询"])
async def update_polling_config_endpoint(config: PollingConfig):
    """更新轮询配置"""
    return await update_polling_config(config)


@app.get("/api/u9/polling/status", response_model=PollingStatusResponse, tags=["产品订单日志轮询"])
async def get_polling_status_endpoint():
    """获取轮询状态"""
    return await get_polling_status()


@app.get("/api/u9/polling/logs", response_model=PollingLogsResponse, tags=["产品订单日志轮询"])
async def get_polling_logs_endpoint():
    """获取轮询获取的日志数据"""
    return await get_polling_logs()


@app.post("/api/u9/polling/start", response_model=ServiceControlResponse, tags=["产品订单日志轮询"])
async def start_polling_endpoint_wrapper():
    """启动轮询"""
    return await start_polling_endpoint()


@app.post("/api/u9/polling/stop", response_model=ServiceControlResponse, tags=["产品订单日志轮询"])
async def stop_polling_endpoint_wrapper():
    """停止轮询"""
    return await stop_polling_endpoint()


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5001)