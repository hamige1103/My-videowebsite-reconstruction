"""
视频相关的数据模型
"""

from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class VideoType(BaseModel):
    """视频类型模型"""
    id: int
    name: str
    
    class Config:
        from_attributes = True

class VideoInfo(BaseModel):
    """视频基本信息模型"""
    id: int
    name: str
    type_id: int
    type_name: Optional[str] = None
    
    class Config:
        from_attributes = True

class VideoDetail(BaseModel):
    """视频详情模型"""
    id: int
    vod_id: int
    vod_name: str
    type_id: int
    type_name: Optional[str] = None
    vod_pic: Optional[str] = None
    vod_remarks: Optional[str] = None
    vod_play_url: Optional[str] = None
    vod_content: Optional[str] = None
    vod_director: Optional[str] = None
    vod_actor: Optional[str] = None
    vod_area: Optional[str] = None
    vod_lang: Optional[str] = None
    vod_year: Optional[str] = None
    vod_time: Optional[datetime] = None
    vod_hits: Optional[int] = 0
    vod_hits_day: Optional[int] = 0
    vod_hits_week: Optional[int] = 0
    vod_hits_month: Optional[int] = 0
    vod_score: Optional[str] = None
    vod_up: Optional[int] = 0
    vod_down: Optional[int] = 0
    
    class Config:
        from_attributes = True

class VideoListResponse(BaseModel):
    """视频列表响应模型（兼容现有Flask接口）"""
    code: int
    message: str
    data: Optional[List[VideoDetail]] = None
    total: Optional[int] = 0
    page: Optional[int] = 1
    limit: Optional[int] = 20

class VideoDetailResponse(BaseModel):
    """视频详情响应模型（兼容现有Flask接口）"""
    code: int
    message: str
    data: Optional[VideoDetail] = None

class VideoTypeResponse(BaseModel):
    """视频类型响应模型（兼容现有Flask接口）"""
    code: int
    message: str
    data: Optional[List[VideoType]] = None

class SearchRequest(BaseModel):
    """搜索请求模型"""
    keyword: str
    page: int = 1
    limit: int = 20

class VideoPlayUrl(BaseModel):
    """视频播放地址模型"""
    name: str
    url: str

class VideoPlayInfo(BaseModel):
    """视频播放信息模型"""
    from_: str
    url: str
    name: str

class VideoPlayResponse(BaseModel):
    """视频播放响应模型（兼容现有Flask接口）"""
    code: int
    message: str
    data: Optional[Dict[str, Any]] = None