import logging
import uuid
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr, validator
import re

from app.models.auth import User, LoginLog, RefreshToken
from app.database import get_db
from sqlalchemy.orm import Session
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/auth", tags=["认证"])

# HTTP Bearer 认证
security = HTTPBearer()


# ============ Pydantic 模型 ============

class LoginRequest(BaseModel):
    """登录请求"""
    username: str
    password: str
    remember_me: bool = False
    
    @validator('username')
    def validate_username(cls, v):
        """验证用户名格式（支持用户名或邮箱）"""
        v = v.strip()
        if not v:
            raise ValueError('用户名不能为空')
        
        # 检查是否为邮箱格式
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if re.match(email_pattern, v):
            # 验证邮箱格式
            if len(v) > 100:
                raise ValueError('邮箱地址过长')
        else:
            # 验证用户名格式（字母、数字、下划线，3-50 字符）
            username_pattern = r'^[a-zA-Z0-9_]{3,50}$'
            if not re.match(username_pattern, v):
                raise ValueError('用户名格式不正确（3-50 位字母、数字或下划线）')
        
        return v
    
    @validator('password')
    def validate_password(cls, v):
        """验证密码强度"""
        if not v:
            raise ValueError('密码不能为空')
        
        if len(v) < settings.PASSWORD_MIN_LENGTH:
            raise ValueError(f'密码长度至少为 {settings.PASSWORD_MIN_LENGTH} 位')
        
        # 检查密码强度
        has_upper = any(c.isupper() for c in v)
        has_lower = any(c.islower() for c in v)
        has_digit = any(c.isdigit() for c in v)
        has_special = any(not c.isalnum() for c in v)
        
        strength_checks = [has_upper, has_lower, has_digit, has_special]
        passed_checks = sum(strength_checks)
        
        if passed_checks < 3:
            raise ValueError('密码强度不足，需包含大小写字母、数字和特殊字符中的至少三种')
        
        return v


class LoginResponse(BaseModel):
    """登录响应"""
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: int
    user_info: dict


class TokenRefreshRequest(BaseModel):
    """刷新令牌请求"""
    refresh_token: str


class ChangePasswordRequest(BaseModel):
    """修改密码请求"""
    old_password: str
    new_password: str
    
    @validator('new_password')
    def validate_new_password(cls, v):
        """验证新密码"""
        if len(v) < settings.PASSWORD_MIN_LENGTH:
            raise ValueError(f'密码长度至少为 {settings.PASSWORD_MIN_LENGTH} 位')
        
        has_upper = any(c.isupper() for c in v)
        has_lower = any(c.islower() for c in v)
        has_digit = any(c.isdigit() for c in v)
        has_special = any(not c.isalnum() for c in v)
        
        if sum([has_upper, has_lower, has_digit, has_special]) < 3:
            raise ValueError('密码强度不足')
        
        return v


# ============ 辅助函数 ============

def get_client_ip(request: Request) -> str:
    """获取客户端 IP 地址"""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0]
    return request.client.host if request.client else "unknown"


def log_login_attempt(
    db: Session,
    username: str,
    ip_address: str,
    user_agent: str,
    success: bool,
    failure_reason: str = None,
    user_id: int = None
):
    """记录登录日志"""
    log = LoginLog(
        user_id=user_id,
        username_attempted=username,
        ip_address=ip_address,
        user_agent=user_agent,
        success=success,
        failure_reason=failure_reason
    )
    db.add(log)
    db.commit()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """获取当前登录用户"""
    token = credentials.credentials
    payload = User.decode_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="令牌无效或已过期",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="令牌无效",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在或已被禁用",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


# ============ 路由处理器 ============

@router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    req: Request,
    db: Session = Depends(get_db)
):
    """
    用户登录
    
    - **username**: 用户名或邮箱
    - **password**: 密码
    - **remember_me**: 是否记住我（延长令牌有效期）
    """
    ip_address = get_client_ip(req)
    user_agent = req.headers.get("user-agent", "")
    
    # 查找用户（支持用户名或邮箱）
    user = db.query(User).filter(
        (User.username == request.username) | (User.email == request.username)
    ).first()
    
    if not user:
        log_login_attempt(
            db=db,
            username=request.username,
            ip_address=ip_address,
            user_agent=user_agent,
            success=False,
            failure_reason="用户不存在"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    
    # 检查账户是否被锁定
    if user.is_locked():
        log_login_attempt(
            db=db,
            username=request.username,
            ip_address=ip_address,
            user_agent=user_agent,
            success=False,
            failure_reason="账户已锁定",
            user_id=user.id
        )
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail=f"账户已锁定，请于 {user.locked_until.strftime('%Y-%m-%d %H:%M')} 后重试"
        )
    
    # 验证密码
    if not User.verify_password(request.password, user.password_hash, user.salt):
        user.record_login_attempt(success=False)
        db.commit()
        
        log_login_attempt(
            db=db,
            username=request.username,
            ip_address=ip_address,
            user_agent=user_agent,
            success=False,
            failure_reason="密码错误",
            user_id=user.id
        )
        
        remaining_attempts = settings.MAX_LOGIN_ATTEMPTS - user.failed_login_attempts
        if remaining_attempts <= 0:
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail=f"账户已锁定，请于 {user.locked_until.strftime('%Y-%m-%d %H:%M')} 后重试"
            )
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"用户名或密码错误，还剩 {remaining_attempts} 次尝试机会"
        )
    
    # 登录成功
    user.record_login_attempt(success=True)
    db.commit()
    
    # 生成令牌
    expires_delta = timedelta(days=7) if request.remember_me else None
    access_token = user.generate_token(expires_delta)
    
    # 生成刷新令牌（仅当记住我时）
    refresh_token = None
    if request.remember_me:
        refresh_token_str = uuid.uuid4().hex
        refresh_token_obj = RefreshToken(
            user_id=user.id,
            token=refresh_token_str,
            expires_at=datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
            ip_address=ip_address,
            user_agent=user_agent
        )
        db.add(refresh_token_obj)
        db.commit()
        refresh_token = refresh_token_str
    
    # 记录登录日志
    log_login_attempt(
        db=db,
        username=request.username,
        ip_address=ip_address,
        user_agent=user_agent,
        success=True,
        user_id=user.id
    )
    
    logger.info(f"用户登录成功：{user.username}, IP: {ip_address}")
    
    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user_info={
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role
        }
    )


@router.post("/logout")
async def logout(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """用户登出"""
    # 这里可以添加令牌黑名单逻辑
    logger.info(f"用户登出：{current_user.username}")
    
    return {"message": "登出成功"}


@router.post("/refresh")
async def refresh_token(
    request: TokenRefreshRequest,
    req: Request,
    db: Session = Depends(get_db)
):
    """刷新访问令牌"""
    refresh_token_obj = db.query(RefreshToken).filter(
        RefreshToken.token == request.refresh_token
    ).first()
    
    if not refresh_token_obj or not RefreshToken.is_valid(request.refresh_token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="刷新令牌无效或已过期"
        )
    
    user = db.query(User).filter(User.id == refresh_token_obj.user_id).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在或已被禁用"
        )
    
    # 生成新的访问令牌
    access_token = user.generate_token()
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


@router.get("/me")
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """获取当前用户信息"""
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "role": current_user.role,
        "is_active": current_user.is_active,
        "last_login": current_user.last_login
    }


@router.post("/change-password")
async def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """修改密码"""
    # 验证旧密码
    if not User.verify_password(request.old_password, current_user.password_hash, current_user.salt):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="原密码错误"
        )
    
    # 更新密码
    new_hash, new_salt = User.hash_password(request.new_password)
    current_user.password_hash = new_hash
    current_user.salt = new_salt
    db.commit()
    
    logger.info(f"用户修改密码：{current_user.username}")
    
    return {"message": "密码修改成功"}
