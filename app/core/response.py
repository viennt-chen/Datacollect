"""
统一 API 响应和状态码规范
功能：
1. 定义统一的 API 响应格式
2. 标准化状态码体系
3. 统一错误处理机制
4. 提供响应辅助函数
"""
from typing import Optional, Any, Dict, List
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime
import json


# ==================== 状态码定义 ====================
class StatusCode(Enum):
    """统一状态码定义"""
    # 成功 (200-299)
    SUCCESS = 200, "成功"
    CREATED = 201, "已创建"
    ACCEPTED = 202, "已接受"
    NO_CONTENT = 204, "无内容"
    
    # 客户端错误 (400-499)
    BAD_REQUEST = 400, "请求参数错误"
    UNAUTHORIZED = 401, "未授权"
    FORBIDDEN = 403, "禁止访问"
    NOT_FOUND = 404, "资源不存在"
    METHOD_NOT_ALLOWED = 405, "方法不允许"
    CONFLICT = 409, "资源冲突"
    VALIDATION_ERROR = 422, "数据验证失败"
    TOO_MANY_REQUESTS = 429, "请求过多"
    
    # 服务端错误 (500-599)
    INTERNAL_ERROR = 500, "服务器内部错误"
    NOT_IMPLEMENTED = 501, "未实现"
    SERVICE_UNAVAILABLE = 503, "服务不可用"
    GATEWAY_TIMEOUT = 504, "网关超时"
    
    # 业务错误 (1000-1999)
    MQTT_CONNECTION_ERROR = 1001, "MQTT 连接失败"
    MQTT_SUBSCRIBE_ERROR = 1002, "MQTT 订阅失败"
    DATABASE_ERROR = 1003, "数据库操作失败"
    U9_API_ERROR = 1004, "U9 接口调用失败"
    CACHE_ERROR = 1005, "缓存操作失败"
    FILE_ERROR = 1006, "文件操作失败"
    DATA_NOT_FOUND = 1007, "数据不存在"
    DATA_DUPLICATE = 1008, "数据重复"
    OPERATION_FAILED = 1009, "操作失败"
    TIMEOUT_ERROR = 1010, "操作超时"
    
    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message


# ==================== 响应模型 ====================
class APIResponse(BaseModel):
    """统一 API 响应模型"""
    code: int = Field(200, description="状态码")
    message: str = Field("success", description="响应消息")
    data: Optional[Any] = Field(None, description="响应数据")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="时间戳")
    success: bool = Field(True, description="是否成功")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ErrorResponse(BaseModel):
    """错误响应模型"""
    code: int = Field(description="错误码")
    message: str = Field(description="错误消息")
    detail: Optional[str] = Field(None, description="详细错误信息")
    error_type: Optional[str] = Field(None, description="错误类型")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="时间戳")
    path: Optional[str] = Field(None, description="请求路径")


class PaginatedResponse(BaseModel):
    """分页响应模型"""
    code: int = Field(200, description="状态码")
    message: str = Field("success", description="响应消息")
    data: List[Any] = Field(default_factory=list, description="数据列表")
    total: int = Field(0, description="总数")
    page: int = Field(1, description="当前页码")
    page_size: int = Field(20, description="每页数量")
    total_pages: int = Field(0, description="总页数")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="时间戳")
    success: bool = Field(True, description="是否成功")


# ==================== WebSocket 消息模型 ====================
class WebSocketMessage(BaseModel):
    """WebSocket 消息模型"""
    type: str = Field(description="消息类型")
    action: Optional[str] = Field(None, description="动作")
    data: Optional[Dict[str, Any]] = Field(None, description="消息数据")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="时间戳")


# ==================== 响应辅助函数 ====================
def success_response(
    data: Any = None,
    message: str = "success",
    code: StatusCode = StatusCode.SUCCESS
) -> APIResponse:
    """成功响应"""
    return APIResponse(
        code=code.code,
        message=message,
        data=data,
        success=True
    )


def error_response(
    message: str,
    code: StatusCode = StatusCode.INTERNAL_ERROR,
    detail: Optional[str] = None,
    error_type: Optional[str] = None
) -> ErrorResponse:
    """错误响应"""
    return ErrorResponse(
        code=code.code,
        message=message,
        detail=detail,
        error_type=error_type
    )


def paginated_response(
    data: List[Any],
    total: int,
    page: int = 1,
    page_size: int = 20,
    message: str = "success"
) -> PaginatedResponse:
    """分页响应"""
    total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0
    
    return PaginatedResponse(
        data=data,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        message=message
    )


# ==================== 异常处理 ====================
class APIException(Exception):
    """API 异常基类"""
    def __init__(
        self,
        message: str,
        code: StatusCode = StatusCode.INTERNAL_ERROR,
        detail: Optional[str] = None
    ):
        self.message = message
        self.code = code
        self.detail = detail
        super().__init__(self.message)


class MQTTConnectionException(APIException):
    """MQTT 连接异常"""
    def __init__(self, message: str = "MQTT 连接失败", detail: Optional[str] = None):
        super().__init__(message, StatusCode.MQTT_CONNECTION_ERROR, detail)


class DatabaseException(APIException):
    """数据库异常"""
    def __init__(self, message: str = "数据库操作失败", detail: Optional[str] = None):
        super().__init__(message, StatusCode.DATABASE_ERROR, detail)


class U9APIException(APIException):
    """U9 接口异常"""
    def __init__(self, message: str = "U9 接口调用失败", detail: Optional[str] = None):
        super().__init__(message, StatusCode.U9_API_ERROR, detail)


class DataNotFoundException(APIException):
    """数据不存在异常"""
    def __init__(self, message: str = "数据不存在", detail: Optional[str] = None):
        super().__init__(message, StatusCode.DATA_NOT_FOUND, detail)


class ValidationException(APIException):
    """数据验证异常"""
    def __init__(self, message: str = "数据验证失败", detail: Optional[str] = None):
        super().__init__(message, StatusCode.VALIDATION_ERROR, detail)


# ==================== 异常处理器 ====================
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
import logging

logger = logging.getLogger(__name__)


async def api_exception_handler(request: Request, exc: APIException):
    """API 异常处理器"""
    error_msg = getattr(exc, 'message', str(exc))
    logger.error(f"API 异常：{error_msg}, 路径：{request.url.path}")
    
    return JSONResponse(
        status_code=exc.code.code if exc.code.code < 1000 else status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response(
            message=error_msg,
            code=exc.code,
            detail=exc.detail,
            error_type=exc.__class__.__name__
        ).model_dump(),
        headers={"X-Error-Code": str(exc.code.code)}
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """验证异常处理器"""
    logger.warning(f"验证失败：{exc.errors()}, 路径：{request.url.path}")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_response(
            message="请求参数验证失败",
            code=StatusCode.VALIDATION_ERROR,
            detail=str(exc.errors()),
            error_type="RequestValidationError"
        ).dict(),
        headers={"X-Error-Code": str(StatusCode.VALIDATION_ERROR.code)}
    )


async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """数据库异常处理器"""
    logger.error(f"数据库异常：{str(exc)}, 路径：{request.url.path}")
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response(
            message="数据库操作失败",
            code=StatusCode.DATABASE_ERROR,
            detail=str(exc),
            error_type="SQLAlchemyError"
        ).dict(),
        headers={"X-Error-Code": str(StatusCode.DATABASE_ERROR.code)}
    )


async def generic_exception_handler(request: Request, exc: Exception):
    """通用异常处理器"""
    logger.error(f"未处理异常：{str(exc)}, 路径：{request.url.path}", exc_info=True)
    
    # 处理 HTTPException
    if hasattr(exc, 'detail'):
        error_msg = exc.detail if isinstance(exc.detail, str) else str(exc.detail)
    elif hasattr(exc, 'message'):
        error_msg = exc.message
    else:
        error_msg = str(exc)
    
    return JSONResponse(
        status_code=getattr(exc, 'status_code', status.HTTP_500_INTERNAL_SERVER_ERROR),
        content=error_response(
            message=error_msg if len(error_msg) < 100 else "服务器内部错误",
            code=StatusCode.INTERNAL_ERROR,
            detail=str(exc),
            error_type=type(exc).__name__
        ).dict(),
        headers={"X-Error-Code": str(StatusCode.INTERNAL_ERROR.code)}
    )


# ==================== 中间件 ====================
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp, Receive, Scope, Send
import time


class TimingMiddleware(BaseHTTPMiddleware):
    """请求耗时统计中间件"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        response = await call_next(request)
        
        duration = time.time() - start_time
        response.headers["X-Process-Time"] = f"{duration:.3f}s"
        
        logger.info(
            f"{request.method} {request.url.path} - "
            f"{response.status_code} - "
            f"{duration:.3f}s"
        )
        
        return response


class RequestIDMiddleware(BaseHTTPMiddleware):
    """请求 ID 中间件"""
    
    async def dispatch(self, request: Request, call_next):
        import uuid
        
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id
        
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        
        return response
