"""
用户收藏相关的数据模型
"""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class CollectionBase(BaseModel):
    """收藏基础模型"""
    video_id: int

class CollectionCreate(CollectionBase):
    """创建收藏模型"""
    pass

class CollectionDelete(CollectionBase):
    """删除收藏模型"""
    pass

class CollectionResponse(BaseModel):
    """收藏响应模型"""
    id: int
    user_id: int
    video_id: int
    video_name: Optional[str] = None
    video_pic: Optional[str] = None
    video_type: Optional[str] = None
    create_time: datetime
    
    class Config:
        from_attributes = True

class CollectionListResponse(BaseModel):
    """收藏列表响应模型（兼容现有Flask接口）"""
    code: int
    message: str
    data: Optional[List[CollectionResponse]] = None
    total: Optional[int] = 0

class CollectionCreateResponse(BaseModel):
    """创建收藏响应模型（兼容现有Flask接口）"""
    code: int
    message: str
    data: Optional[CollectionResponse] = None

class CollectionDeleteResponse(BaseModel):
    """删除收藏响应模型（兼容现有Flask接口）"""
    code: int
    message: str

class CollectionCheckResponse(BaseModel):
    """检查收藏状态响应模型（兼容现有Flask接口）"""
    code: int
    message: str
    data: Optional[bool] = None