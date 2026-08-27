"""
用户收藏API端点
"""

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from typing import Optional, List
import json

from app.core.database import get_db
from app.api.deps import flask_auth
from app.models.models import UserCollection, MovDetail, MovType, User
from app.schemas.collection import (
    CollectionCreate, 
    CollectionDelete,
    CollectionListResponse, 
    CollectionCreateResponse,
    CollectionDeleteResponse,
    CollectionCheckResponse
)

router = APIRouter()

@router.get("/collection/list", response_model=CollectionListResponse)
def get_user_collections(
    user_dict: dict = Depends(flask_auth),
    page: int = Query(1, ge=1, description="页码"),
    limit: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db)
):
    """
    获取用户收藏列表（兼容现有Flask接口）
    """
    # 获取用户收藏记录
    result = db.execute(
        select(UserCollection).where(UserCollection.user_id == user_dict["id"])
    )
    collection = result.scalar_one_or_none()
    
    if collection is None or not collection.movdetail_id_list:
        return CollectionListResponse(
            code=200,
            message="获取收藏列表成功",
            data=[],
            total=0
        )
    
    # 解析收藏的视频ID列表（分号分隔格式）
    try:
        video_ids = [int(vid) for vid in collection.movdetail_id_list.split(';') if vid.strip()]
    except:
        video_ids = []
    
    if not video_ids:
        return CollectionListResponse(
            code=200,
            message="获取收藏列表成功",
            data=[],
            total=0
        )
    
    # 分页处理
    offset = (page - 1) * limit
    total = len(video_ids)
    
    # 获取当前页的视频ID
    page_video_ids = video_ids[offset:offset + limit]
    
    if not page_video_ids:
        return CollectionListResponse(
            code=200,
            message="获取收藏列表成功",
            data=[],
            total=total
        )
    
    # 获取视频详情
    result = db.execute(
        select(MovDetail).where(MovDetail.vod_id.in_(page_video_ids))
    )
    videos = result.scalars().all()
    
    # 获取类型信息
    type_ids = list(set([video.type_id for video in videos]))
    type_result = db.execute(select(MovType).where(MovType.type_id.in_(type_ids)))
    type_map = {t.type_id: t.type_name for t in type_result.scalars().all()}
    
    # 构建响应数据
    collection_responses = []
    for video in videos:
        collection_responses.append({
            "id": video.vod_id,  # 使用视频vod_id作为临时ID
            "user_id": user_dict["id"],
            "video_id": video.vod_id,
            "video_name": video.vod_name or "",
            "video_pic": video.vod_pic or "",
            "video_type": type_map.get(video.type_id, ""),
            "create_time": video.vod_time or datetime.now()  # 使用视频的创建时间，如果为空则使用当前时间
        })
    
    return CollectionListResponse(
        code=200,
        message="获取收藏列表成功",
        data=collection_responses,
        total=total
    )

@router.post("/collection/add", response_model=CollectionCreateResponse)
def add_collection(
    collection_data: CollectionCreate,
    user_dict: dict = Depends(flask_auth),
    db: Session = Depends(get_db)
):
    """
    添加收藏（兼容现有Flask接口）
    """
    # 验证用户是否存在
    user_result = db.execute(
        select(User).where(User.id == user_dict["id"])
    )
    user = user_result.scalar_one_or_none()
    
    if user is None:
        return CollectionCreateResponse(
            code=404,
            message="用户不存在"
        )
    
    # 验证视频是否存在
    video_result = db.execute(
        select(MovDetail).where(MovDetail.vod_id == collection_data.video_id)
    )
    video = video_result.scalar_one_or_none()
    
    if video is None:
        return CollectionCreateResponse(
            code=404,
            message="视频不存在"
        )
    
    # 获取或创建用户收藏记录
    result = db.execute(
        select(UserCollection).where(UserCollection.user_id == user_dict["id"])
    )
    collection = result.scalar_one_or_none()
    
    if collection is None:
        # 创建新的收藏记录（使用分号分隔格式）
        collection = UserCollection(
            user_id=user_dict["id"],
            movdetail_id_list=f"{collection_data.video_id};"
        )
        db.add(collection)
    else:
        # 更新现有收藏记录
        if not collection.movdetail_id_list:
            collection.movdetail_id_list = ""
        
        # 检查是否已收藏
        if f"{collection_data.video_id};" in collection.movdetail_id_list:
            return CollectionCreateResponse(
                code=400,
                message="已收藏该视频"
            )
        
        # 添加到收藏列表（分号分隔格式）
        collection.movdetail_id_list += f"{collection_data.video_id};"
    
    db.commit()
    db.refresh(collection)
    
    # 构建响应数据
    collection_response = {
        "id": video.vod_id,  # 使用视频vod_id作为临时ID
        "user_id": user_dict["id"],
        "video_id": video.vod_id,
        "video_name": video.vod_name or "",
        "video_pic": video.vod_pic or "",
        "video_type": "",  # 需要额外查询类型信息
        "create_time": video.vod_time or datetime.now()  # 使用视频的创建时间，如果为空则使用当前时间
    }
    
    # 获取类型信息
    type_result = db.execute(select(MovType).where(MovType.type_id == video.type_id))
    type_obj = type_result.scalar_one_or_none()
    if type_obj:
        collection_response["video_type"] = type_obj.type_name
    
    return CollectionCreateResponse(
        code=200,
        message="收藏成功",
        data=collection_response
    )

@router.delete("/collection/remove", response_model=CollectionDeleteResponse)
def remove_collection(
    collection_data: CollectionDelete,
    user_dict: dict = Depends(flask_auth),
    db: Session = Depends(get_db)
):
    """
    移除收藏（兼容现有Flask接口）
    """
    # 获取用户收藏记录
    result = db.execute(
        select(UserCollection).where(UserCollection.user_id == user_dict["id"])
    )
    collection = result.scalar_one_or_none()
    
    if collection is None or not collection.movdetail_id_list:
        return CollectionDeleteResponse(
            code=404,
            message="收藏记录不存在"
        )
    
    # 检查是否已收藏（分号分隔格式）
    if f"{collection_data.video_id};" not in collection.movdetail_id_list:
        return CollectionDeleteResponse(
            code=404,
            message="未收藏该视频"
        )
    
    # 从收藏列表中移除（分号分隔格式）
    collection.movdetail_id_list = collection.movdetail_id_list.replace(f"{collection_data.video_id};", "")
    
    db.commit()
    
    return CollectionDeleteResponse(
        code=200,
        message="取消收藏成功"
    )

@router.get("/collection/check/{video_id}", response_model=CollectionCheckResponse)
def check_collection(
    video_id: int,
    user_dict: dict = Depends(flask_auth),
    db: Session = Depends(get_db)
):
    """
    检查是否已收藏（兼容现有Flask接口）
    """
    # 获取用户收藏记录
    result = db.execute(
        select(UserCollection).where(UserCollection.user_id == user_dict["id"])
    )
    collection = result.scalar_one_or_none()
    
    if collection is None or not collection.movdetail_id_list:
        return CollectionCheckResponse(
            code=200,
            message="检查收藏状态成功",
            data=False
        )
    
    # 检查是否已收藏（分号分隔格式）
    is_collected = f"{video_id};" in collection.movdetail_id_list
    
    return CollectionCheckResponse(
        code=200,
        message="检查收藏状态成功",
        data=is_collected
    )

@router.get("/collection/count")
def get_collection_count(
    user_dict: dict = Depends(flask_auth),
    db: Session = Depends(get_db)
):
    """
    获取用户收藏数量（兼容现有Flask接口）
    """
    # 获取用户收藏记录
    result = db.execute(
        select(UserCollection).where(UserCollection.user_id == user_dict["id"])
    )
    collection = result.scalar_one_or_none()
    
    if collection is None or not collection.movdetail_id_list:
        return {
            "code": 200,
            "message": "获取收藏数量成功",
            "data": 0
        }
    
    # 解析收藏列表（分号分隔格式）
    try:
        video_ids = [int(vid) for vid in collection.movdetail_id_list.split(';') if vid.strip()]
    except:
        video_ids = []
    
    count = len(video_ids)
    
    return {
        "code": 200,
        "message": "获取收藏数量成功",
        "data": count
    }