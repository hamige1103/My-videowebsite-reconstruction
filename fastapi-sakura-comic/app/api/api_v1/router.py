"""
API v1 路由聚合
"""

from fastapi import APIRouter

from app.api.api_v1.endpoints import auth, videos, comments, collections, admin, smart_search, live, live_commerce

api_router = APIRouter()

# 认证相关路由
api_router.include_router(auth.router, prefix="/v1", tags=["认证"])

# 视频相关路由
api_router.include_router(videos.router, prefix="/v1", tags=["视频"])

# 评论相关路由
api_router.include_router(comments.router, prefix="/v1", tags=["评论"])

# 收藏相关路由
api_router.include_router(collections.router, prefix="/v1", tags=["收藏"])

# 管理后台路由
api_router.include_router(admin.router, prefix="/v1/admin", tags=["管理后台"])

# 智能搜索路由
api_router.include_router(smart_search.router, prefix="/v1", tags=["智能搜索"])

# 直播相关路由
api_router.include_router(live.router, prefix="/v1", tags=["直播"])

# 直播带货相关路由
api_router.include_router(live_commerce.router, prefix="/v1", tags=["直播带货"])

# 其他路由可以在这里添加
# api_router.include_router(other.router, prefix="/v1", tags=["其他"])