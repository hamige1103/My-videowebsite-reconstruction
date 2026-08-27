"""
直播相关数据模式
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class LiveStreamBase(BaseModel):
    """直播流基础模式"""
    title: str
    description: Optional[str] = None
    category: str = "entertainment"
    quality: str = "720p"
    is_private: bool = False
    enable_chat: bool = True
    enable_recording: bool = True


class LiveStreamCreate(LiveStreamBase):
    """创建直播模式"""
    pass


class LiveStreamUpdate(BaseModel):
    """更新直播模式"""
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    is_private: Optional[bool] = None


class LiveStreamResponse(LiveStreamBase):
    """直播流响应模式"""
    id: int
    host_id: int
    host_name: str
    stream_url: Optional[str] = None
    play_url: Optional[str] = None
    status: str
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    created_at: datetime
    viewer_count: int = 0
    like_count: int = 0
    share_count: int = 0
    max_viewers: int = 0
    
    class Config:
        from_attributes = True


class LiveStreamListResponse(BaseModel):
    """直播列表响应模式"""
    total: int
    page: int
    page_size: int
    items: List[LiveStreamResponse]


class LiveChatMessage(BaseModel):
    """直播聊天消息模式"""
    live_id: int
    user_id: Optional[int] = None
    username: str
    message: str
    message_type: str = "text"
    gift_id: Optional[int] = None
    created_at: datetime


class LiveProduct(BaseModel):
    """直播商品模式"""
    name: str
    description: Optional[str] = None
    price: float
    original_price: Optional[float] = None
    image_url: Optional[str] = None
    product_url: Optional[str] = None
    stock: int = 0


class LiveProductResponse(LiveProduct):
    """直播商品响应模式"""
    id: int
    live_id: int
    sold_count: int = 0
    is_active: bool = True
    created_at: datetime
    
    class Config:
        from_attributes = True


class LiveGift(BaseModel):
    """直播礼物模式"""
    name: str
    emoji: Optional[str] = None
    image_url: Optional[str] = None
    price: float
    animation_url: Optional[str] = None


class LiveGiftResponse(LiveGift):
    """直播礼物响应模式"""
    id: int
    is_active: bool = True
    created_at: datetime
    
    class Config:
        from_attributes = True


class LiveStats(BaseModel):
    """直播统计数据模式"""
    viewer_count: int
    like_count: int
    share_count: int
    duration: float
    start_time: Optional[datetime] = None


class LiveViewerInfo(BaseModel):
    """直播观众信息模式"""
    user_id: Optional[int] = None
    username: str
    join_time: datetime
    watch_duration: int


class OBSConfig(BaseModel):
    """OBS推流配置模式"""
    server_url: str
    stream_key: str
    video_bitrate: int = 2500
    audio_bitrate: int = 128
    resolution: str = "1280x720"
    fps: int = 30


class OBSStatus(BaseModel):
    """OBS状态模式"""
    is_connected: bool
    is_streaming: bool
    is_recording: bool
    stream_time: Optional[int] = None
    total_frames: Optional[int] = None
    dropped_frames: Optional[int] = None


class LiveCommerceOrder(BaseModel):
    """直播带货订单模式"""
    product_id: int
    quantity: int = 1
    total_price: float
    buyer_name: str
    buyer_contact: str
    shipping_address: str