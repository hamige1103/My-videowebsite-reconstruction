"""
依赖注入模块 - 认证和数据库依赖
"""

from typing import Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import verify_token
from app.models.models import User

# HTTP Bearer认证方案
security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    获取当前认证用户
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # 支持两种token格式：Bearer token 和 jwt token
    token = credentials.credentials
    if token.startswith("jwt "):
        token = token[4:]  # 移除"jwt "前缀
    
    # 验证token
    user_id = verify_token(token)
    if user_id is None:
        raise credentials_exception
    
    # 从数据库获取用户（包含角色信息）
    from sqlalchemy import select
    result = db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()
    
    if user is None:
        raise credentials_exception
    
    return user

def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    获取当前活跃用户（可扩展用于用户状态检查）
    """
    # 这里可以添加用户状态检查逻辑
    # 例如：if not current_user.is_active:
    #     raise HTTPException(status_code=400, detail="用户已被禁用")
    return current_user

def get_flask_compatible_auth():
    """
    获取Flask兼容的认证依赖（用于保持API兼容性）
    """
    def flask_auth_dependency(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db: Session = Depends(get_db)
    ) -> dict:
        """
        Flask兼容的认证，返回用户字典
        """
        token = credentials.credentials
        
        # 支持jwt和Bearer两种前缀
        if token.startswith("jwt "):
            token = token[4:]
        elif token.startswith("Bearer "):
            token = token[7:]
        # 如果没有前缀，直接使用整个字符串作为token
        
        from app.core.security import parse_user_from_token
        user_dict = parse_user_from_token(token)
        
        if user_dict is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="认证失败"
            )
        
        # 验证用户是否存在于数据库中
        from sqlalchemy import select
        from app.models.models import User
        result = db.execute(select(User).where(User.id == user_dict["id"]))
        user = result.scalar_one_or_none()
        
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户不存在"
            )
        
        # 添加角色信息到用户字典
        user_dict["role"] = user.role
        
        return user_dict
    
    return flask_auth_dependency

# Flask兼容的认证依赖
flask_auth = get_flask_compatible_auth()