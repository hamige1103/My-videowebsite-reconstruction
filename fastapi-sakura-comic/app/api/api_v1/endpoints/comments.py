"""
评论API端点
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from typing import Optional, List

from app.core.database import get_db
from app.api.deps import flask_auth
from app.models.models import Comment, User, MovDetail
from app.schemas.comment import (
    CommentCreate, 
    CommentListResponse, 
    CommentCreateResponse,
    CommentDeleteResponse
)

router = APIRouter()

@router.get("/comment/list", response_model=CommentListResponse)
def get_comments(
    video_id: int = Query(..., description="视频ID"),
    page: int = Query(1, ge=1, description="页码"),
    limit: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db)
):
    """
    获取视频评论列表（兼容现有Flask接口）
    """
    # 验证视频是否存在
    video_result = db.execute(select(MovDetail).where(MovDetail.vod_id == video_id))
    video = video_result.scalar_one_or_none()
    
    # 如果视频不存在，返回空评论列表而不是错误
    if video is None:
        return CommentListResponse(
            code=200,
            message="获取评论列表成功",
            data=[],
            total=0
        )
    
    offset = (page - 1) * limit
    
    # 获取顶级评论（replied_id为None）
    # 使用转换后的movdetail_id（video.id）而不是vod_id
    query = select(Comment).where(
        Comment.movdetail_id == video.id,
        Comment.replied_id == None
    ).order_by(Comment.timestamp.desc())
    
    # 获取总数
    count_query = select(func.count()).select_from(query.subquery())
    total_result = db.execute(count_query)
    total = total_result.scalar()
    
    # 获取分页数据
    query = query.offset(offset).limit(limit)
    result = db.execute(query)
    comments = result.scalars().all()
    
    # 构建评论响应数据
    comment_responses = []
    for comment in comments:
        # 获取用户信息
        user_result = db.execute(select(User).where(User.id == comment.user_id))
        user = user_result.scalar_one_or_none()
        
        if user:
            # 获取回复数量
            reply_count_query = select(func.count()).where(Comment.replied_id == comment.id)
            reply_count_result = db.execute(reply_count_query)
            reply_count = reply_count_result.scalar()
            
            # 获取回复列表（最多5条）
            replies_query = select(Comment).where(
                Comment.replied_id == comment.id
            ).order_by(Comment.timestamp.asc()).limit(5)
            
            replies_result = db.execute(replies_query)
            replies = replies_result.scalars().all()
            
            reply_responses = []
            for reply in replies:
                reply_user_result = db.execute(select(User).where(User.id == reply.user_id))
                reply_user = reply_user_result.scalar_one_or_none()
                
                if reply_user:
                    reply_responses.append({
                        "id": reply.id,
                        "body": reply.body,
                        "video_id": reply.movdetail_id,
                        "user_id": reply.user_id,
                        "user_name": reply_user.name,
                        "parent_id": reply.replied_id,
                        "timestamp": reply.timestamp,
                        "reply_count": 0,
                        "replies": None
                    })
            
            comment_responses.append({
                    "id": comment.id,
                    "body": comment.body,
                    "video_id": comment.movdetail_id,
                    "user_id": comment.user_id,
                    "user_name": user.name,
                    "parent_id": comment.replied_id,
                    "timestamp": comment.timestamp,
                    "reply_count": reply_count,
                    "replies": reply_responses
                })
    
    return CommentListResponse(
        code=200,
        message="获取评论列表成功",
        data=comment_responses,
        total=total
    )

@router.post("/comment/create", response_model=CommentCreateResponse)
def create_comment(
    comment_data: CommentCreate,
    user_dict: dict = Depends(flask_auth),
    db: Session = Depends(get_db)
):
    """
    创建评论（兼容现有Flask接口）
    """
    # 验证视频是否存在
    video_result = db.execute(select(MovDetail).where(MovDetail.vod_id == comment_data.video_id))
    video = video_result.scalar_one_or_none()
    
    # 如果视频不存在，创建一个虚拟的视频记录
    if video is None:
        # 检查是否已经有对应的虚拟视频记录
        existing_virtual_result = db.execute(
            select(MovDetail).where(MovDetail.vod_id == comment_data.video_id)
        )
        existing_virtual = existing_virtual_result.scalar_one_or_none()
        
        if existing_virtual is None:
            # 创建虚拟视频记录 - 只使用MovDetail模型中实际存在的字段
            video = MovDetail(
                vod_id=comment_data.video_id,
                vod_name=f"虚拟视频-{comment_data.video_id}",
                vod_pic="",
                vod_remarks="",
                vod_play_url="",
                vod_content="",
                vod_director="",
                vod_actor="",
                vod_year="",
                vod_area="",
                vod_lang="",
                vod_sub="",
                vod_class="",
                vod_score="0.0",
                vod_duration=""
            )
            db.add(video)
            db.commit()
            db.refresh(video)
        else:
            video = existing_virtual
    
    # 验证父评论是否存在（如果是回复）
    if comment_data.parent_id:
        parent_result = db.execute(select(Comment).where(Comment.id == comment_data.parent_id))
        parent_comment = parent_result.scalar_one_or_none()
        
        if parent_comment is None:
            return CommentCreateResponse(
                code=404,
                message="父评论不存在"
            )
    
    # 创建评论
    # 如果parent_id为0或None，表示是顶级评论，应该设置为None
    replied_id = None if comment_data.parent_id == 0 or comment_data.parent_id is None else comment_data.parent_id
    
    # 将vod_id转换为movdetail_id（sakura_movdetail表的id字段）
    movdetail_id = video.id
    
    new_comment = Comment(
        body=comment_data.content,
        movdetail_id=movdetail_id,
        user_id=user_dict["id"],
        replied_id=replied_id
    )
    
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    
    # 获取用户信息
    user_result = db.execute(select(User).where(User.id == user_dict["id"]))
    user = user_result.scalar_one_or_none()
    
    if user:
        comment_response = {
            "id": new_comment.id,
            "body": new_comment.body,
            "video_id": new_comment.movdetail_id,
            "user_id": new_comment.user_id,
            "user_name": user.name,
            "parent_id": new_comment.replied_id,
            "timestamp": new_comment.timestamp,
            "reply_count": 0,
            "replies": None
        }
        
        return CommentCreateResponse(
            code=200,
            message="评论成功",
            data=comment_response
        )
    
    return CommentCreateResponse(
        code=500,
        message="评论失败"
    )

@router.delete("/comment/delete/{comment_id}", response_model=CommentDeleteResponse)
def delete_comment(
    comment_id: int,
    user_dict: dict = Depends(flask_auth),
    db: Session = Depends(get_db)
):
    """
    删除评论（兼容现有Flask接口）
    """
    # 获取评论
    result = db.execute(select(Comment).where(Comment.id == comment_id))
    comment = result.scalar_one_or_none()
    
    if comment is None:
        return CommentDeleteResponse(
            code=404,
            message="评论不存在"
        )
    
    # 验证评论所有权
    if comment.user_id != user_dict["id"]:
        return CommentDeleteResponse(
            code=403,
            message="无权删除此评论"
        )
    
    # 删除评论
    db.delete(comment)
    db.commit()
    
    return CommentDeleteResponse(
        code=200,
        message="删除评论成功"
    )

@router.get("/comment/replies/{comment_id}")
def get_comment_replies(
    comment_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """
    获取评论的回复列表（兼容现有Flask接口）
    """
    # 验证评论是否存在
    comment_result = db.execute(select(Comment).where(Comment.id == comment_id))
    comment = comment_result.scalar_one_or_none()
    
    if comment is None:
        return {
            "code": 404,
            "message": "评论不存在"
        }
    
    offset = (page - 1) * limit
    
    # 获取回复
    query = select(Comment).where(
        Comment.replied_id == comment_id
    ).order_by(Comment.timestamp.asc())
    
    # 获取总数
    count_query = select(func.count()).select_from(query.subquery())
    total_result = db.execute(count_query)
    total = total_result.scalar()
    
    # 获取分页数据
    query = query.offset(offset).limit(limit)
    result = db.execute(query)
    replies = result.scalars().all()
    
    # 构建回复响应数据
    reply_responses = []
    for reply in replies:
        user_result = db.execute(select(User).where(User.id == reply.user_id))
        user = user_result.scalar_one_or_none()
        
        if user:
            reply_responses.append({
                "id": reply.id,
                "body": reply.body,
                "video_id": reply.movdetail_id,
                "user_id": reply.user_id,
                "user_name": user.name,
                "parent_id": reply.replied_id,
                "timestamp": reply.timestamp,
                "reply_count": 0,
                "replies": None
            })
    
    return {
        "code": 200,
        "message": "获取回复列表成功",
        "data": reply_responses,
        "total": total,
        "page": page,
        "limit": limit
    }