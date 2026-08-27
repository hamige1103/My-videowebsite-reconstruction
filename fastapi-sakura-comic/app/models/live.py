"""
直播相关数据模型
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship

from app.core.database import Base


class LiveStream(Base):
    """直播流模型"""
    __tablename__ = "sakura_livestream"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    category = Column(String(50), default="entertainment")  # entertainment, gaming, music, education, sports, other
    host_id = Column(Integer, ForeignKey("sakura_user.id"), nullable=False)
    host_name = Column(String(100), nullable=False)
    
    # 推流配置
    stream_url = Column(String(500))  # RTMP推流地址
    play_url = Column(String(500))    # HLS播放地址
    quality = Column(String(20), default="720p")  # 480p, 720p, 1080p
    
    # 直播状态
    status = Column(String(20), default="preparing")  # preparing, live, ended, error
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    created_at = Column(DateTime, default=datetime.now)
    
    # 直播设置
    is_private = Column(Boolean, default=False)
    enable_chat = Column(Boolean, default=True)
    enable_recording = Column(Boolean, default=True)
    
    # 统计数据
    viewer_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    share_count = Column(Integer, default=0)
    max_viewers = Column(Integer, default=0)
    
    # 关联关系
    host = relationship("User", backref="live_streams")
    chat_messages = relationship("LiveChat", back_populates="live_stream", cascade="all, delete-orphan")
    products = relationship("LiveProduct", back_populates="live_stream", cascade="all, delete-orphan")
    orders = relationship("LiveCommerceOrder", back_populates="live_stream", cascade="all, delete-orphan")
    
    @property
    def duration(self):
        """计算直播时长"""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        elif self.start_time and self.status == "live":
            return (datetime.now() - self.start_time).total_seconds()
        return 0


class LiveChat(Base):
    """直播聊天消息模型"""
    __tablename__ = "sakura_livechat"
    
    id = Column(Integer, primary_key=True, index=True)
    live_id = Column(Integer, ForeignKey("sakura_livestream.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("sakura_user.id"))
    username = Column(String(100), nullable=False)
    message = Column(Text, nullable=False)
    message_type = Column(String(20), default="text")  # text, gift, system, admin
    gift_id = Column(Integer)  # 礼物ID
    created_at = Column(DateTime, default=datetime.now)
    
    # 关联关系
    live_stream = relationship("LiveStream", back_populates="chat_messages")
    user = relationship("User", backref="live_chat_messages")


class LiveProduct(Base):
    """直播带货商品模型"""
    __tablename__ = "sakura_liveproduct"
    
    id = Column(Integer, primary_key=True, index=True)
    live_id = Column(Integer, ForeignKey("sakura_livestream.id"), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)
    original_price = Column(Float)
    image_url = Column(String(500))
    product_url = Column(String(500))  # 商品购买链接
    stock = Column(Integer, default=0)  # 库存
    sold_count = Column(Integer, default=0)  # 已售数量
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    
    # 关联关系
    live_stream = relationship("LiveStream", back_populates="products")
    orders = relationship("LiveCommerceOrder", back_populates="product")


class LiveGift(Base):
    """直播礼物模型"""
    __tablename__ = "sakura_livegift"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    emoji = Column(String(10))  # 表情符号
    image_url = Column(String(500))  # 礼物图片
    price = Column(Float, nullable=False)  # 礼物价格
    animation_url = Column(String(500))  # 动画效果URL
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)


class LiveViewer(Base):
    """直播观众模型（用于记录观众信息）"""
    __tablename__ = "sakura_liveviewer"
    
    id = Column(Integer, primary_key=True, index=True)
    live_id = Column(Integer, ForeignKey("sakura_livestream.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("sakura_user.id"))
    username = Column(String(100))
    join_time = Column(DateTime, default=datetime.now)
    leave_time = Column(DateTime)
    watch_duration = Column(Integer, default=0)  # 观看时长（秒）
    
    # 关联关系
    live_stream = relationship("LiveStream")
    user = relationship("User")


class LiveCommerceOrder(Base):
    """直播带货订单模型"""
    __tablename__ = "sakura_liveorder"
    
    id = Column(Integer, primary_key=True, index=True)
    live_id = Column(Integer, ForeignKey("sakura_livestream.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("sakura_liveproduct.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("sakura_user.id"), nullable=False)
    username = Column(String(100), nullable=False)
    quantity = Column(Integer, default=1)
    total_price = Column(Float, nullable=False)
    buyer_name = Column(String(100), nullable=False)
    buyer_contact = Column(String(100), nullable=False)
    shipping_address = Column(Text, nullable=False)
    status = Column(String(20), default="pending")  # pending, paid, shipped, completed, cancelled
    created_at = Column(DateTime, default=datetime.now)
    
    # 关联关系
    live_stream = relationship("LiveStream", back_populates="orders")
    product = relationship("LiveProduct", back_populates="orders")
    user = relationship("User", backref="live_orders")