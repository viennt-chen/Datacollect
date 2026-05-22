"""
Redis 客户端管理
提供 Redis 连接和缓存操作
"""
import json
import logging
from typing import Any, Optional
from redis import Redis, ConnectionError, RedisError
from app.config import settings

logger = logging.getLogger(__name__)

redis_client: Optional[Redis] = None


def get_redis() -> Optional[Redis]:
    """获取 Redis 客户端实例"""
    global redis_client
    
    if redis_client is None and settings.REDIS_ENABLED:
        try:
            if settings.REDIS_URL:
                redis_client = Redis.from_url(
                    settings.REDIS_URL,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5,
                    retry_on_timeout=True
                )
            else:
                redis_kwargs = {
                    'host': settings.REDIS_HOST,
                    'port': settings.REDIS_PORT,
                    'db': settings.REDIS_DB,
                    'decode_responses': True,
                    'socket_connect_timeout': 5,
                    'socket_timeout': 5,
                    'retry_on_timeout': True
                }
                
                if settings.REDIS_PASSWORD:
                    redis_kwargs['password'] = settings.REDIS_PASSWORD
                
                redis_client = Redis(**redis_kwargs)
            
            # 测试连接
            redis_client.ping()
            logger.info(f"Redis 连接成功: {settings.REDIS_HOST}:{settings.REDIS_PORT}")
            
        except ConnectionError as e:
            logger.warning(f"Redis 连接失败: {e}")
            redis_client = None
        except RedisError as e:
            logger.warning(f"Redis 初始化失败: {e}")
            redis_client = None
    
    return redis_client


def init_redis():
    """初始化 Redis 连接"""
    client = get_redis()
    if client:
        logger.info("Redis 中间件初始化完成")
    else:
        logger.warning("Redis 未启用或连接失败，缓存功能将不可用")


def close_redis():
    """关闭 Redis 连接"""
    global redis_client
    if redis_client:
        try:
            redis_client.close()
            logger.info("Redis 连接已关闭")
        except Exception as e:
            logger.error(f"关闭 Redis 连接失败: {e}")
        finally:
            redis_client = None


class CacheManager:
    """缓存管理器"""
    
    def __init__(self, client: Optional[Redis] = None):
        self.client = client or get_redis()
        self.prefix = settings.CACHE_PREFIX
    
    def _make_key(self, key: str) -> str:
        """生成带前缀的缓存键"""
        return f"{self.prefix}:{key}"
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        if not self.client:
            return None
        
        try:
            value = self.client.get(self._make_key(key))
            if value is not None:
                return json.loads(value)
            return None
        except (RedisError, json.JSONDecodeError) as e:
            logger.error(f"获取缓存失败: {key}, 错误: {e}")
            return None
    
    def set(self, key: str, value: Any, expire: Optional[int] = None) -> bool:
        """设置缓存值"""
        if not self.client:
            return False
        
        try:
            serialized = json.dumps(value, ensure_ascii=False, default=str)
            expire_time = expire if expire is not None else settings.CACHE_DEFAULT_EXPIRE
            self.client.setex(self._make_key(key), expire_time, serialized)
            return True
        except (RedisError, TypeError) as e:
            logger.error(f"设置缓存失败: {key}, 错误: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """删除缓存"""
        if not self.client:
            return False
        
        try:
            self.client.delete(self._make_key(key))
            return True
        except RedisError as e:
            logger.error(f"删除缓存失败: {key}, 错误: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """检查缓存是否存在"""
        if not self.client:
            return False
        
        try:
            return self.client.exists(self._make_key(key)) > 0
        except RedisError as e:
            logger.error(f"检查缓存失败: {key}, 错误: {e}")
            return False
    
    def clear_pattern(self, pattern: str) -> bool:
        """清除匹配模式的缓存"""
        if not self.client:
            return False
        
        try:
            full_pattern = self._make_key(pattern)
            keys = self.client.keys(full_pattern)
            if keys:
                self.client.delete(*keys)
            return True
        except RedisError as e:
            logger.error(f"清除缓存失败: {pattern}, 错误: {e}")
            return False


# 全局缓存管理器实例
cache_manager = CacheManager()
