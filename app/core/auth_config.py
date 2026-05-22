"""
认证相关配置
"""
from datetime import timedelta
from typing import List
from pydantic_settings import BaseSettings
import secrets


class AuthSettings(BaseSettings):
    """认证配置"""
    
    # JWT 配置
    SECRET_KEY: str = secrets.token_urlsafe(32)  # 生产环境应使用固定密钥
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30  # 访问令牌过期时间（分钟）
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7  # 刷新令牌过期时间（天）
    
    # 安全配置
    MAX_LOGIN_ATTEMPTS: int = 5  # 最大登录尝试次数
    ACCOUNT_LOCKOUT_DURATION: int = 30  # 账户锁定时间（分钟）
    PASSWORD_MIN_LENGTH: int = 8  # 密码最小长度
    PASSWORD_REQUIRE_SPECIAL: bool = True  # 要求特殊字符
    PASSWORD_REQUIRE_NUMBER: bool = True  # 要求数字
    PASSWORD_REQUIRE_UPPERCASE: bool = True  # 要求大写字母
    
    # Session 配置
    SESSION_COOKIE_NAME: str = "auth_token"
    SESSION_COOKIE_SECURE: bool = True  # 仅 HTTPS
    SESSION_COOKIE_HTTPONLY: bool = True  # 禁止 JavaScript 访问
    SESSION_COOKIE_SAMESITE: str = "lax"  # CSRF 保护
    
    # 限流配置
    RATE_LIMIT_PER_MINUTE: int = 60  # 每分钟请求限制
    
    # CORS 配置（生产环境应指定具体域名）
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:8000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8000",
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# 创建配置实例
auth_settings = AuthSettings()
