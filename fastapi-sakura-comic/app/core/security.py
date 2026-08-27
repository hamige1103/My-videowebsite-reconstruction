"""
安全模块 - JWT token管理和密码加密
"""

from datetime import datetime, timedelta
from typing import Any, Optional, Union
from jose import JWTError, jwt
from passlib.context import CryptContext
import hashlib

from app.core.config import settings

# 密码加密上下文 - 使用更简单的方案避免bcrypt问题
pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")

# 备用密码哈希函数
def simple_password_hash(password: str) -> str:
    """简单的密码哈希函数"""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def create_access_token(
    subject: Union[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """
    创建JWT访问令牌
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码 - 兼容Flask项目的密码哈希格式
    """
    try:
        # 首先尝试使用passlib验证（FastAPI项目的哈希格式）
        result = pwd_context.verify(plain_password, hashed_password)
        if result:
            return True
    except Exception:
        pass
    
    try:
        # 如果passlib失败，尝试使用werkzeug的check_password_hash（兼容Flask项目）
        from werkzeug.security import check_password_hash
        # 注意：check_password_hash的第一个参数是哈希值，第二个参数是明文密码
        result = check_password_hash(hashed_password, plain_password)
        if result:
            return True
    except Exception:
        pass
    
    # 如果以上都失败，使用备用方案
    return simple_password_hash(plain_password) == hashed_password

def get_password_hash(password: str) -> str:
    """
    生成密码哈希
    """
    try:
        # 首先尝试使用passlib
        return pwd_context.hash(password)
    except Exception:
        # 如果passlib失败，使用备用方案
        return simple_password_hash(password)

def verify_token(token: str) -> Optional[str]:
    """
    验证JWT令牌并返回用户标识
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        subject: str = payload.get("sub")
        if subject is None:
            return None
        return subject
    except JWTError:
        return None

def generate_auth_token(user_id: int, name: str, effective_time: int = 30) -> str:
    """
    生成认证令牌（兼容现有Flask接口）
    """
    expire = datetime.utcnow() + timedelta(days=effective_time)
    to_encode = {
        "exp": expire,
        "user_id": user_id,
        "name": name
    }
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def parse_user_from_token(token: str) -> Optional[dict]:
    """
    从令牌中解析用户信息（兼容现有Flask接口）
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return {
            "id": payload.get("user_id"),  # 使用"id"字段以兼容现有Flask接口
            "user_id": payload.get("user_id"),
            "name": payload.get("name")
        }
    except JWTError:
        return None