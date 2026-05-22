"""
应用配置
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置"""

    # 服务配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False

    # 数据库配置 - 必须通过 .env 提供
    DATABASE_URL: str
    AUTH_DATABASE_URL: str

    # Redis 配置
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str = ""
    REDIS_URL: str = ""
    REDIS_ENABLED: bool = False

    # 缓存配置
    CACHE_DEFAULT_EXPIRE: int = 300
    CACHE_PREFIX: str = "webadmin"

    # JWT 配置 - 必须通过 .env 提供
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # 安全配置
    MAX_LOGIN_ATTEMPTS: int = 5
    ACCOUNT_LOCKOUT_DURATION: int = 30
    PASSWORD_MIN_LENGTH: int = 8
    PASSWORD_REQUIRE_SPECIAL: bool = True
    PASSWORD_REQUIRE_NUMBER: bool = True
    PASSWORD_REQUIRE_UPPERCASE: bool = True

    # Session 配置
    SESSION_COOKIE_NAME: str = "auth_token"

    # CORS 配置
    CORS_ORIGINS: list = [
        "http://localhost:5173",
        "http://localhost:8000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8000",
    ]

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = 'ignore'


settings = Settings()
