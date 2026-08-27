"""
数据库模型 - 适配现有数据表结构
基于现有Flask项目的数据库表结构进行异步适配
"""

import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy import Text as LONGTEXT
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base

class MovType(Base):
    """视频分类表"""
    __tablename__ = 'sakura_movtype'
    
    type_id = Column(Integer, primary_key=True)
    type_name = Column(String(20), nullable=False)
    
    # 关系
    this_type_movies = relationship(
        "MovInfo", back_populates="this_mov_type"
    )
    this_type_movie_details = relationship(
        "MovDetail", back_populates="this_mov_type"
    )

class MovInfo(Base):
    """视频基本信息表"""
    __tablename__ = 'sakura_movinfo'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    type_id = Column(Integer, ForeignKey('sakura_movtype.type_id'))
    type_name = Column(String(20), nullable=False)
    vod_en = Column(Text, nullable=False)
    vod_id = Column(Integer, unique=True, nullable=False)
    vod_name = Column(Text, nullable=False)
    vod_play_from = Column(Text)
    vod_remarks = Column(Text)
    vod_time = Column(DateTime)
    
    # 关系
    this_mov_type = relationship(
        "MovType", back_populates="this_type_movies"
    )

class MovDetail(Base):
    """视频详情表 - 核心数据表"""
    __tablename__ = 'sakura_movdetail'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    group_id = Column(Integer)
    type_id = Column(Integer, ForeignKey('sakura_movtype.type_id'))
    type_id_1 = Column(Integer)
    type_name = Column(String(20))
    
    # 基本信息
    vod_actor = Column(Text)
    vod_area = Column(Text)
    vod_author = Column(Text)
    vod_behind = Column(Text)
    vod_blurb = Column(Text)
    vod_class = Column(Text)
    vod_color = Column(Text)
    vod_content = Column(Text)
    vod_copyright = Column(Integer)
    vod_director = Column(Text)
    vod_douban_id = Column(Integer)
    vod_douban_score = Column(String(20))
    
    # 播放信息
    vod_down = Column(Integer)
    vod_down_from = Column(Text)
    vod_down_note = Column(Text)
    vod_down_server = Column(Text)
    vod_down_url = Column(Text)
    vod_duration = Column(Text)
    vod_en = Column(Text)
    
    # 统计信息
    vod_hits = Column(Integer)
    vod_hits_day = Column(Integer)
    vod_hits_month = Column(Integer)
    vod_hits_week = Column(Integer)
    vod_id = Column(Integer, unique=True, nullable=False)
    vod_isend = Column(Integer)
    
    # 技术信息
    vod_jumpurl = Column(Text)
    vod_lang = Column(Text)
    vod_letter = Column(Text)
    vod_level = Column(Integer)
    vod_lock = Column(Integer)
    vod_name = Column(Text)
    vod_pic = Column(Text)
    vod_pic_screenshot = Column(Text)
    vod_pic_slide = Column(Text)
    vod_pic_thumb = Column(Text)
    vod_play_from = Column(Text)
    vod_play_note = Column(Text)
    vod_play_server = Column(Text)
    vod_play_url = Column(LONGTEXT)
    
    # 其他信息
    vod_plot = Column(Integer)
    vod_plot_detail = Column(Text)
    vod_plot_name = Column(Text)
    vod_points = Column(Integer)
    vod_points_down = Column(Integer)
    vod_points_play = Column(Integer)
    vod_pubdate = Column(Text)
    vod_pwd = Column(Text)
    vod_pwd_down = Column(Text)
    vod_pwd_down_url = Column(Text)
    vod_pwd_play = Column(Text)
    vod_pwd_play_url = Column(Text)
    vod_pwd_url = Column(Text)
    vod_rel_art = Column(Text)
    vod_rel_vod = Column(Text)
    vod_remarks = Column(Text)
    vod_reurl = Column(Text)
    vod_score = Column(Text)
    vod_score_all = Column(Integer)
    vod_score_num = Column(Integer)
    vod_serial = Column(Text)
    vod_state = Column(Text)
    vod_status = Column(Integer)
    vod_sub = Column(Text)
    vod_tag = Column(Text)
    vod_time = Column(DateTime)
    vod_time_add = Column(Integer)
    vod_time_hits = Column(Integer)
    vod_time_make = Column(Integer)
    vod_total = Column(Integer)
    vod_tpl = Column(Text)
    vod_tpl_down = Column(Text)
    vod_tpl_play = Column(Text)
    vod_trysee = Column(Integer)
    vod_tv = Column(Text)
    vod_up = Column(Integer)
    vod_version = Column(Text)
    vod_weekday = Column(Text)
    vod_writer = Column(Text)
    vod_year = Column(Text)
    
    # 关系
    this_mov_type = relationship(
        "MovType", back_populates="this_type_movie_details"
    )
    comments = relationship(
        "Comment", back_populates="mov_detail", cascade="all, delete-orphan"
    )

class User(Base):
    """用户表"""
    __tablename__ = 'sakura_user'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(30))
    password_hash = Column(String(128))
    role = Column(String(20), default='user')  # 用户角色：user, admin
    
    # 关系
    comments = relationship(
        "Comment", back_populates="user", cascade="all, delete-orphan"
    )
    collections = relationship(
        "UserCollection", back_populates="user", cascade="all, delete-orphan"
    )

class Comment(Base):
    """评论表 - 支持多级评论"""
    __tablename__ = 'sakura_comment'
    
    id = Column(Integer, primary_key=True)
    body = Column(Text)
    reviewed = Column(Boolean, default=True)
    timestamp = Column(
        DateTime, default=func.now(), index=True
    )
    
    # 外键
    user_id = Column(Integer, ForeignKey('sakura_user.id'))
    replied_id = Column(Integer, ForeignKey('sakura_comment.id'))
    movdetail_id = Column(Integer, ForeignKey('sakura_movdetail.id'))
    
    # 关系
    user = relationship("User", back_populates="comments")
    mov_detail = relationship("MovDetail", back_populates="comments")
    replies = relationship(
        "Comment", back_populates="replied", cascade="all, delete-orphan"
    )
    replied = relationship(
        "Comment", back_populates="replies", remote_side=[id]
    )

class UserCollection(Base):
    """用户收藏表"""
    __tablename__ = 'sakura_user_collection'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('sakura_user.id'))
    movdetail_id_list = Column(LONGTEXT)
    
    # 关系
    user = relationship("User", back_populates="collections")