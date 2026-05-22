"""
Redis 缓存中间件
为 API 请求提供自动缓存功能
"""
import json
import hashlib
import logging
import time
from typing import Optional
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.redis_client import cache_manager
from app.config import settings

logger = logging.getLogger(__name__)


class CacheMiddleware(BaseHTTPMiddleware):
    """
    缓存中间件
    
    功能：
    - 自动缓存 GET 请求的响应
    - 支持自定义缓存时间
    - 支持跳过缓存（通过请求头或路径）
    """
    
    def __init__(self, app, default_ttl: int = 300, exclude_paths: Optional[list] = None):
        super().__init__(app)
        self.default_ttl = default_ttl
        self.exclude_paths = exclude_paths or [
            "/docs",
            "/openapi.json",
            "/redoc",
            "/health",
            "/static",
            "/admin",
            "/dashboard",
            "/ws"
        ]
    
    def _generate_cache_key(self, request: Request) -> str:
        """生成缓存键"""
        url = str(request.url)
        query_params = dict(request.query_params)
        key_data = f"{url}:{json.dumps(query_params, sort_keys=True)}"
        key_hash = hashlib.md5(key_data.encode()).hexdigest()
        return f"cache:{request.method}:{key_hash}"
    
    def _should_skip_cache(self, request: Request) -> bool:
        """检查是否应该跳过缓存"""
        # 只缓存 GET 请求
        if request.method != "GET":
            return True
        
        # 检查请求头
        if request.headers.get("Cache-Control") == "no-cache":
            return True
        
        # 检查路径
        path = request.url.path
        for exclude_path in self.exclude_paths:
            if path.startswith(exclude_path):
                return True
        
        return False
    
    async def dispatch(self, request: Request, call_next):
        """处理请求"""
        # 检查是否跳过缓存
        if not settings.REDIS_ENABLED or self._should_skip_cache(request):
            return await call_next(request)
        
        # 生成缓存键
        cache_key = self._generate_cache_key(request)
        
        # 尝试从缓存获取
        cached_response = cache_manager.get(cache_key)
        if cached_response:
            logger.debug(f"缓存命中: {cache_key[:20]}...")
            return Response(
                content=cached_response["body"],
                status_code=cached_response["status_code"],
                headers=cached_response["headers"],
                media_type=cached_response["media_type"]
            )
        
        # 执行请求
        start_time = time.time()
        response = await call_next(request)
        duration = time.time() - start_time
        
        # 缓存成功的响应
        if response.status_code == 200:
            try:
                body = b""
                async for chunk in response.body_iterator:
                    body += chunk
                
                # 获取响应头
                headers = dict(response.headers)
                headers["X-Cache"] = "MISS"
                headers["X-Response-Time"] = f"{duration:.3f}s"
                
                # 存储到缓存
                cache_data = {
                    "body": body.decode("utf-8", errors="ignore"),
                    "status_code": response.status_code,
                    "headers": headers,
                    "media_type": response.media_type
                }
                
                # 获取自定义 TTL
                ttl = self.default_ttl
                cache_control = request.headers.get("Cache-Control", "")
                if "max-age=" in cache_control:
                    try:
                        ttl = int(cache_control.split("max-age=")[1].split(",")[0])
                    except (ValueError, IndexError):
                        pass
                
                cache_manager.set(cache_key, cache_data, expire=ttl)
                logger.debug(f"缓存已设置: {cache_key[:20]}..., TTL: {ttl}s")
                
                return Response(
                    content=body,
                    status_code=response.status_code,
                    headers=headers,
                    media_type=response.media_type
                )
            except Exception as e:
                logger.error(f"缓存响应失败: {e}")
        
        return response


class CacheControlMiddleware(BaseHTTPMiddleware):
    """
    缓存控制中间件

    添加缓存控制头到响应中
    """

    def __init__(self, app, default_max_age: int = 300):
        super().__init__(app)
        self.default_max_age = default_max_age
        # 静态资源缓存时间（1年）
        self.static_max_age = 31536000
        # 需要长期缓存的静态资源扩展名
        self.static_extensions = {
            '.woff2', '.woff', '.ttf', '.eot',  # 字体
            '.js', '.css',                         # 脚本和样式
            '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico',  # 图片
        }

    def _get_cache_max_age(self, path: str) -> int:
        """根据路径返回合适的缓存时间"""
        from pathlib import Path
        ext = Path(path).suffix.lower()
        if ext in self.static_extensions:
            return self.static_max_age
        return self.default_max_age

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # 只处理成功的 GET 请求
        if request.method == "GET" and response.status_code == 200:
            if "Cache-Control" not in response.headers:
                max_age = self._get_cache_max_age(request.url.path)
                response.headers["Cache-Control"] = f"public, max-age={max_age}, immutable"

        return response
