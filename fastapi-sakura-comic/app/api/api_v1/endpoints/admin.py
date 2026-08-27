"""
管理后台API端点
提供用户管理、视频管理、评论管理等功能
仅管理员可访问
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.models import User, MovDetail, Comment
from app.schemas.auth import UserResponse, UserUpdate
from app.schemas.video import VideoDetail
from app.schemas.comment import CommentResponse
from app.api.deps import flask_auth

router = APIRouter()

# 权限检查函数
def require_admin(user_dict: dict = Depends(flask_auth)):
    """检查当前用户是否为管理员"""
    if user_dict.get("role") != 'admin':
        raise HTTPException(
            status_code=403, 
            detail="权限不足，需要管理员权限"
        )
    return user_dict

# 用户管理接口
@router.get("/users", response_model=List[UserResponse], summary="获取用户列表")
def get_users(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    search: Optional[str] = Query(None, description="搜索用户名"),
    role: Optional[str] = Query(None, description="按角色筛选"),
    db: Session = Depends(get_db),
    user_dict: dict = Depends(require_admin)
):
    """获取用户列表（仅管理员）"""
    offset = (page - 1) * page_size
    
    # 构建查询
    query = select(User)
    
    if search:
        query = query.where(User.name.contains(search))
    
    if role:
        query = query.where(User.role == role)
    
    # 执行查询
    result = db.execute(query.offset(offset).limit(page_size))
    users = result.scalars().all()
    
    return users

@router.get("/users/{user_id}", response_model=UserResponse, summary="获取用户信息")
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    user_dict: dict = Depends(require_admin)
):
    """获取用户详情（仅管理员）"""
    result = db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    return user

@router.put("/users/{user_id}", response_model=UserResponse, summary="更新用户信息")
def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    user_dict: dict = Depends(require_admin)
):
    """更新用户信息（仅管理员）"""# 查询用户是否存在
    result = db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 更新用户信息
    update_data = user_update.dict(exclude_unset=True)
    db.execute(
        update(User)
        .where(User.id == user_id)
        .values(**update_data)
    )
    db.commit()
    
    # 重新获取更新后的用户
    result = db.execute(select(User).where(User.id == user_id))
    updated_user = result.scalar_one()
    
    return updated_user

@router.delete("/users/{user_id}", summary="删除用户")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    user_dict: dict = Depends(require_admin)
):
    """删除用户（仅管理员）"""
    result = db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 不能删除自己
    if user_id == user_dict.get("id"):
        raise HTTPException(status_code=400, detail="不能删除自己的账户")
    
    db.execute(delete(User).where(User.id == user_id))
    db.commit()
    
    return {"message": "用户删除成功"}

# 视频管理接口
@router.get("/videos", response_model=List[VideoDetail], summary="获取视频列表")
def get_videos(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    search: Optional[str] = Query(None, description="搜索视频名称"),
    type_id: Optional[int] = Query(None, description="按分类筛选"),
    db: Session = Depends(get_db),
    user_dict: dict = Depends(require_admin)
):
    """获取视频列表（仅管理员）"""
    offset = (page - 1) * page_size
    
    # 构建查询
    query = select(MovDetail)
    
    if search:
        query = query.where(MovDetail.vod_name.contains(search))
    
    if type_id:
        query = query.where(MovDetail.type_id == type_id)
    
    # 执行查询
    result = db.execute(query.offset(offset).limit(page_size))
    videos = result.scalars().all()
    
    return videos

@router.delete("/videos/{video_id}", summary="删除视频")
def delete_video(
    video_id: int,
    db: Session = Depends(get_db),
    user_dict: dict = Depends(require_admin)
):
    """删除视频（仅管理员）"""
    result = db.execute(select(MovDetail).where(MovDetail.vod_id == video_id))
    video = result.scalar_one_or_none()
    
    if not video:
        raise HTTPException(status_code=404, detail="视频不存在")
    
    db.execute(delete(MovDetail).where(MovDetail.vod_id == video_id))
    db.commit()
    
    return {"message": "视频删除成功"}

# 评论管理接口
@router.get("/comments", response_model=List[CommentResponse], summary="获取评论列表")
def get_comments(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    reviewed: Optional[bool] = Query(None, description="按审核状态筛选"),
    user_id: Optional[int] = Query(None, description="按用户筛选"),
    db: Session = Depends(get_db),
    user_dict: dict = Depends(require_admin)
):
    """获取评论列表（仅管理员）"""
    offset = (page - 1) * page_size
    
    # 构建查询
    query = select(Comment).options(selectinload(Comment.user), selectinload(Comment.mov_detail))
    
    if reviewed is not None:
        query = query.where(Comment.reviewed == reviewed)
    
    if user_id:
        query = query.where(Comment.user_id == user_id)
    
    # 执行查询
    result = db.execute(query.offset(offset).limit(page_size))
    comments = result.scalars().all()
    
    # 转换为CommentResponse模型
    comment_responses = []
    for comment in comments:
        comment_response = CommentResponse(
            id=comment.id,
            body=comment.body,
            video_id=comment.movdetail_id if comment.movdetail_id else 0,  # 处理None值
            user_id=comment.user_id,
            user_name=comment.user.name if comment.user else "未知用户",
            parent_id=comment.replied_id,
            timestamp=comment.timestamp,
            reviewed=comment.reviewed,
            reply_count=0,  # 需要计算回复数量
            replies=None
        )
        comment_responses.append(comment_response)
    
    return comment_responses

# 管理后台仪表盘接口
@router.get("/dashboard", summary="获取仪表盘数据")
def get_dashboard_data(
    db: Session = Depends(get_db),
    user_dict: dict = Depends(require_admin)
):
    """获取管理后台仪表盘统计数据（仅管理员）"""
    
    # 获取用户总数
    user_count_result = db.execute(select(func.count(User.id)))
    total_users = user_count_result.scalar()
    
    # 获取视频总数
    video_count_result = db.execute(select(func.count(MovDetail.vod_id)))
    total_videos = video_count_result.scalar()
    
    # 获取评论总数
    comment_count_result = db.execute(select(func.count(Comment.id)))
    total_comments = comment_count_result.scalar()
    
    # 获取今日新增用户数（简化处理，实际应该按日期筛选）
    today_users = 0
    
    return {
        "code": 200,
        "message": "success",
        "data": {
            "total_users": total_users,
            "total_videos": total_videos,
            "total_comments": total_comments,
            "today_users": today_users,
            "system_info": {
                "database": "MySQL",
                "backend": "FastAPI",
                "status": "running"
            }
        }
    }

# 管理后台健康检查接口
@router.get("/health", summary="管理后台健康检查")
def admin_health_check():
    """管理后台健康检查接口"""
    return {
        "code": 200,
        "message": "管理后台服务运行正常",
        "data": {
            "status": "healthy",
            "service": "admin_backend",
            "timestamp": "2024-01-01T00:00:00Z"
        }
    }

@router.put("/comments/{comment_id}/review", summary="审核评论")
def review_comment(
    comment_id: int,
    reviewed: bool = Query(..., description="审核状态"),
    db: Session = Depends(get_db),
    user_dict: dict = Depends(require_admin)
):
    """审核评论（仅管理员）"""
    result = db.execute(select(Comment).where(Comment.id == comment_id))
    comment = result.scalar_one_or_none()
    
    if not comment:
        raise HTTPException(status_code=404, detail="评论不存在")
    
    db.execute(
        update(Comment)
        .where(Comment.id == comment_id)
        .values(reviewed=reviewed)
    )
    db.commit()
    
    return {"message": "评论审核状态更新成功"}

@router.delete("/comments/{comment_id}", summary="删除评论")
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    user_dict: dict = Depends(require_admin)
):
    """删除评论（仅管理员）"""
    result = db.execute(select(Comment).where(Comment.id == comment_id))
    comment = result.scalar_one_or_none()
    
    if not comment:
        raise HTTPException(status_code=404, detail="评论不存在")
    
    db.execute(delete(Comment).where(Comment.id == comment_id))
    db.commit()
    
    return {"message": "评论删除成功"}