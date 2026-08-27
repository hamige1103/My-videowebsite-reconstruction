"""
认证API端点
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import (
    verify_password, 
    get_password_hash, 
    generate_auth_token,
    parse_user_from_token
)
from app.api.deps import security, flask_auth
from app.models.models import User
from app.schemas.auth import (
    UserLogin, 
    UserRegister, 
    AuthResponse, 
    UserInfoResponse
)

router = APIRouter()

@router.post("/auth/login", response_model=AuthResponse)
def login(
    user_login: UserLogin,
    db: Session = Depends(get_db)
):
    """
    用户登录（兼容现有Flask接口）
    """
    if not user_login.name or not user_login.password:
        return AuthResponse(
            code=400,
            message="请输入账户和密码"
        )
    
    # 查询用户
    result = db.execute(select(User).where(User.name == user_login.name))
    user = result.first()
    if user:
        user = user[0]
    
    if user is None:
        return AuthResponse(
            code=400,
            message="登录失败, 账户或密码不正确"
        )
    
    # 验证密码
    if not verify_password(user_login.password, user.password_hash):
        return AuthResponse(
            code=400,
            message="登录失败, 账户或密码不正确"
        )
    
    # 生成token
    token = generate_auth_token(user_id=user.id, name=user.name, effective_time=30)
    
    # 返回用户信息（包括角色）
    user_info = {
        "id": user.id,
        "name": user.name,
        "role": user.role
    }
    
    return AuthResponse(
        code=200,
        message="Login successfully",
        token=f"jwt {token}",
        data=user_info
    )

@router.post("/auth/register", response_model=AuthResponse)
def register(
    user_register: UserRegister,
    db: Session = Depends(get_db)
):
    """
    用户注册（兼容现有Flask接口）
    """
    if not user_register.name or not user_register.password:
        return AuthResponse(
            code=400,
            message="请输入账户和密码"
        )
    
    # 检查用户名是否已存在
    result = db.execute(select(User).where(User.name == user_register.name))
    existing_user = result.first()
    if existing_user:
        existing_user = existing_user[0]
    
    if existing_user:
        return AuthResponse(
            code=400,
            message="注册失败, 当前用户名已被注册, 请更换用户名"
        )
    
    # 创建新用户
    new_user = User(
        name=user_register.name,
        password_hash=get_password_hash(user_register.password)
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return AuthResponse(
        code=200,
        message="注册成功, 请重新登录"
    )

@router.get("/auth/user", response_model=UserInfoResponse)
async def get_current_user_info(
    user_dict: dict = Depends(flask_auth)
):
    """
    获取当前用户信息（兼容现有Flask接口）
    """
    return UserInfoResponse(
        code=200,
        message="获取用户信息成功",
        data=user_dict
    )

@router.get("/api/check")
async def check_token(
    user_dict: dict = Depends(flask_auth)
):
    """
    检查token有效性（兼容现有Flask接口）
    """
    return {
        "code": 200,
        "message": "success",
        "data": user_dict
    }

# FastAPI原生认证端点（可选）
@router.post("/token")
def login_for_access_token(
    user_login: UserLogin,
    db: Session = Depends(get_db)
):
    """
    FastAPI原生token获取端点
    """
    result = db.execute(select(User).where(User.name == user_login.name))
    user = result.first()
    if user:
        user = user[0]
    
    if user is None or not verify_password(user_login.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    from app.core.security import create_access_token
    access_token = create_access_token(subject=user.id)
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }