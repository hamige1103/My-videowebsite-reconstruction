"""
评论相关的数据模型
"""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class CommentBase(BaseModel):
    """评论基础模型"""
    content: str
    video_id: int
    parent_id: Optional[int] = None

class CommentCreate(CommentBase):
    """创建评论模型"""
    pass

class CommentResponse(BaseModel):
    """评论响应模型"""
    id: int
    body: str  # 使用body字段匹配数据库
    video_id: int
    user_id: int
    user_name: str
    parent_id: Optional[int] = None
    timestamp: datetime  # 使用timestamp字段匹配数据库
    reviewed: bool = True
    reply_count: int = 0
    replies: Optional[List['CommentResponse']] = None
    
    class Config:
        from_attributes = True

class CommentListResponse(BaseModel):
    """评论列表响应模型（兼容现有Flask接口）"""
    code: int
    message: str
    data: Optional[List[CommentResponse]] = None
    total: Optional[int] = 0

class CommentCreateResponse(BaseModel):
    """创建评论响应模型（兼容现有Flask接口）"""
    code: int
    message: str
    data: Optional[CommentResponse] = None

class CommentDeleteResponse(BaseModel):
    """删除评论响应模型（兼容现有Flask接口）"""
    code: int
    message: str

# 解决循环引用
CommentResponse.update_forward_refs()