"""
数据库连接模块
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from app.core.config import settings

# 创建数据库引擎
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,  # 调试模式下显示SQL语句
    pool_pre_ping=True,   # 连接池预检查
    pool_recycle=3600,    # 连接回收时间
)

# 创建会话工厂
SessionLocal = sessionmaker(
    bind=engine,
    expire_on_commit=False,
)

Base = declarative_base()

def get_db():
    """
    获取数据库会话的依赖注入函数
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """
    创建数据库表（仅在开发环境使用）
    """
    if settings.DEBUG:
        Base.metadata.create_all(bind=engine)
        print("数据库表创建完成")

def close_db():
    """
    关闭数据库连接
    """
    engine.dispose()