"""
认证相关的数据模型
"""

from pydantic import BaseModel, EmailStr
from typing import Optional

class Token(BaseModel):
    """令牌响应模型"""
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    """令牌数据模型"""
    username: Optional[str] = None

class UserLogin(BaseModel):
    """用户登录模型"""
    name: str
    password: str

class UserRegister(BaseModel):
    """用户注册模型"""
    name: str
    password: str

class UserResponse(BaseModel):
    """用户响应模型"""
    id: int
    name: str
    role: str = 'user'
    
    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    """用户更新模型"""
    name: Optional[str] = None
    role: Optional[str] = None
    
    class Config:
        from_attributes = True

class AuthResponse(BaseModel):
    """认证响应模型（兼容现有Flask接口）"""
    code: int
    message: str
    token: Optional[str] = None
    data: Optional[dict] = None

class UserInfoResponse(BaseModel):
    """用户信息响应模型（兼容现有Flask接口）"""
    code: int
    message: str
    data: Optional[dict] = None