"""
用户认证模型 - 企业级安全认证系统
"""
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.orm import relationship
import bcrypt
import jwt
import uuid
from app.config import settings
from app.database import Base


class User(Base):
    """用户模型"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    salt = Column(String(100), nullable=False)
    full_name = Column(String(100))
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    role = Column(String(50), default="user")  # user, admin, super_admin
    
    # 安全字段
    last_login = Column(DateTime)
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @staticmethod
    def hash_password(password: str, salt: str = None) -> tuple:
        """
        密码加盐哈希
        
        Args:
            password: 原始密码
            salt: 盐值（可选，如果不提供则生成新的）
            
        Returns:
            (password_hash, salt) 元组
        """
        if salt is None:
            salt = uuid.uuid4().hex[:16]  # 缩短 salt 长度
            
        # 密码加盐后哈希（确保不超过 72 字节）
        salted_password = (password + salt).encode('utf-8')[:72]
        password_hash = bcrypt.hashpw(salted_password, bcrypt.gensalt()).decode('utf-8')
        return password_hash, salt

    @staticmethod
    def verify_password(password: str, password_hash: str, salt: str) -> bool:
        """
        验证密码
        
        Args:
            password: 尝试的密码
            password_hash: 存储的哈希值
            salt: 盐值
            
        Returns:
            bool: 验证结果
        """
        try:
            salted_password = (password + salt).encode('utf-8')[:72]
            return bcrypt.checkpw(salted_password, password_hash.encode('utf-8'))
        except Exception:
            return False

    def is_locked(self) -> bool:
        """检查账户是否被锁定"""
        if self.locked_until and self.locked_until > datetime.utcnow():
            return True
        return False

    def record_login_attempt(self, success: bool):
        """
        记录登录尝试
        
        Args:
            success: 是否成功
        """
        if success:
            self.failed_login_attempts = 0
            self.last_login = datetime.utcnow()
            self.locked_until = None
        else:
            self.failed_login_attempts += 1
            # 连续失败 5 次锁定账户 30 分钟
            if self.failed_login_attempts >= settings.MAX_LOGIN_ATTEMPTS:
                self.locked_until = datetime.utcnow() + timedelta(
                    minutes=settings.ACCOUNT_LOCKOUT_DURATION
                )

    def generate_token(self, expires_delta: Optional[timedelta] = None) -> str:
        """
        生成 JWT 令牌
        
        Args:
            expires_delta: 过期时间增量
            
        Returns:
            str: JWT 令牌
        """
        if expires_delta is None:
            expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            
        expire = datetime.utcnow() + expires_delta
        
        payload = {
            "sub": str(self.id),
            "username": self.username,
            "email": self.email,
            "role": self.role,
            "exp": expire,
            "iat": datetime.utcnow(),
            "jti": uuid.uuid4().hex  # 唯一标识符，防止重放攻击
        }
        
        token = jwt.encode(
            payload,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
        
        return token

    @staticmethod
    def decode_token(token: str) -> Optional[dict]:
        """
        解码 JWT 令牌
        
        Args:
            token: JWT 令牌
            
        Returns:
            dict: 令牌内容，验证失败返回 None
        """
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None


class LoginLog(Base):
    """登录日志模型 - 记录所有登录尝试"""
    __tablename__ = "login_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=True)  # 可为空，记录未登录用户的尝试
    username_attempted = Column(String(100), index=True)  # 尝试的用户名
    ip_address = Column(String(50))
    user_agent = Column(String(500))
    success = Column(Boolean)
    failure_reason = Column(String(200))  # 失败原因
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)


class RefreshToken(Base):
    """刷新令牌模型 - 实现令牌刷新机制"""
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    token = Column(String(500), unique=True, index=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    is_revoked = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    ip_address = Column(String(50))
    user_agent = Column(String(500))

    @staticmethod
    def is_valid(token: str) -> bool:
        """检查刷新令牌是否有效"""
        token_obj = RefreshToken.query.filter_by(token=token).first()
        if not token_obj:
            return False
        if token_obj.is_revoked:
            return False
        if token_obj.expires_at < datetime.utcnow():
            return False
        return True
