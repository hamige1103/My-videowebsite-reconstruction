"""
视频API端点
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, func, and_
from typing import Optional, List

from app.core.database import get_db
from app.api.deps import flask_auth
from app.models.models import MovType, MovInfo, MovDetail
from app.schemas.video import (
    VideoTypeResponse, 
    VideoListResponse, 
    VideoDetailResponse,
    VideoPlayResponse,
    SearchRequest
)

router = APIRouter()

@router.get("/video/types", response_model=VideoTypeResponse)
def get_video_types(
    db: Session = Depends(get_db)
):
    """
    获取视频类型列表（兼容现有Flask接口）
    """
    result = db.execute(select(MovType))
    types = result.scalars().all()
    
    # 转换为VideoType模型格式，并修复编码问题
    video_types = []
    for mov_type in types:
        # 修复编码问题，将可能的乱码转换为正确的中文
        type_name = mov_type.type_name
        if type_name:
            # 尝试修复常见的编码问题
            try:
                # 如果是gbk编码的字节串，转换为utf-8
                if isinstance(type_name, bytes):
                    type_name = type_name.decode('gbk').encode('utf-8').decode('utf-8')
                else:
                    # 尝试从可能的错误编码恢复
                    type_name = type_name.encode('latin1').decode('gbk')
            except:
                # 如果转换失败，保持原样
                pass
        
        video_types.append({
            "id": mov_type.type_id,
            "name": type_name
        })
    
    return VideoTypeResponse(
        code=200,
        message="获取视频类型成功",
        data=video_types
    )

@router.get("/video/list", response_model=VideoListResponse)
def get_video_list(
    type_id: Optional[int] = Query(None, description="视频类型ID"),
    movtype: Optional[int] = Query(None, description="视频类型ID（兼容前端参数名）"),
    vod_area: Optional[str] = Query(None, description="地区筛选"),
    vod_year: Optional[str] = Query(None, description="年份筛选"),
    vod_class: Optional[str] = Query(None, description="分类筛选"),
    page: int = Query(1, ge=1, description="页码"),
    limit: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db)
):
    """
    获取视频列表（兼容现有Flask接口）
    支持多维度筛选：类型、地区、年份、分类
    """
    offset = (page - 1) * limit
    
    # 构建查询条件 - 优先使用movtype参数（前端传递的），如果不存在则使用type_id
    # 修改：使用JOIN查询关联MovInfo和MovDetail表，为重复字段指定别名
    query = select(
        MovInfo.id.label("info_id"),
        MovInfo.vod_id,
        MovInfo.vod_name,
        MovInfo.type_id.label("info_type_id"),
        MovInfo.type_name,
        MovInfo.vod_remarks,
        MovInfo.vod_time,
        MovDetail.id.label("detail_id"),
        MovDetail.vod_pic,
        MovDetail.vod_content,
        MovDetail.vod_director,
        MovDetail.vod_actor,
        MovDetail.vod_area,
        MovDetail.vod_lang,
        MovDetail.vod_year,
        MovDetail.vod_hits,
        MovDetail.vod_score,
        MovDetail.vod_play_url
    ).join(MovDetail, MovInfo.vod_id == MovDetail.vod_id)
    actual_type_id = movtype if movtype is not None else type_id
    
    # 分类映射优化：将子分类映射到主要分类
    type_mapping = {
        # 电影分类映射
        22: [22, 6, 7, 8, 9, 10, 11, 12, 20, 21, 34],  # 电影 + 动作片、喜剧片、爱情片、科幻片、恐怖片、剧情片、战争片、犯罪片、纪录片、伦理片
        # 电视剧分类映射  
        13: [13, 14, 15, 16, 23, 24, 25],  # 国产剧 + 香港剧、台湾剧、韩国剧、日本剧、欧美剧、海外剧
        # 综艺分类映射
        26: [26, 27, 28, 29],  # 大陆综艺 + 日韩综艺、港台综艺、欧美综艺
        # 动漫分类映射
        30: [30, 31, 32, 33]   # 国产动漫 + 日本动漫、欧美动漫、海外动漫
    }
    
    # 构建筛选条件
    conditions = []
    
    if actual_type_id:
        # 如果请求的是主要分类，查询对应的所有子分类
        if actual_type_id in type_mapping:
            conditions.append(MovInfo.type_id.in_(type_mapping[actual_type_id]))
        else:
            # 如果不是主要分类，直接查询
            conditions.append(MovInfo.type_id == actual_type_id)
    
    # 地区筛选 - 使用MovDetail表的vod_area字段
    if vod_area and vod_area != '':
        conditions.append(MovDetail.vod_area.like(f"%{vod_area}%"))
    
    # 年份筛选 - 使用MovDetail表的vod_year字段
    if vod_year and vod_year != '':
        conditions.append(MovDetail.vod_year.like(f"%{vod_year}%"))
    
    # 分类筛选 - 使用MovDetail表的vod_class字段
    if vod_class and vod_class != '':
        conditions.append(MovDetail.vod_class.like(f"%{vod_class}%"))
    
    # 应用所有筛选条件
    if conditions:
        query = query.where(and_(*conditions))
    
    # 获取总数
    count_query = select(func.count()).select_from(query.subquery())
    total_result = db.execute(count_query)
    total = total_result.scalar()
    
    # 获取分页数据
    query = query.offset(offset).limit(limit).order_by(MovInfo.id.desc())
    result = db.execute(query)
    video_rows = result.all()
    
    # 合并数据：将MovInfo和MovDetail的数据合并
    videos = []
    for row in video_rows:
        video_data = {
            # 基本信息（来自MovInfo）
            "id": row.info_id,
            "vod_id": row.vod_id,
            "vod_name": row.vod_name,
            "type_id": row.info_type_id,
            "type_name": row.type_name,
            "vod_remarks": row.vod_remarks,
            "vod_time": row.vod_time,
            
            # 详细信息（来自MovDetail）
            "vod_pic": row.vod_pic,
            "vod_content": row.vod_content,
            "vod_director": row.vod_director,
            "vod_actor": row.vod_actor,
            "vod_area": row.vod_area,
            "vod_lang": row.vod_lang,
            "vod_year": row.vod_year,
            "vod_hits": row.vod_hits,
            "vod_score": row.vod_score,
            "vod_play_url": row.vod_play_url
        }
        videos.append(video_data)
    
    # 获取类型名称
    if videos:
        type_ids = list(set([video["type_id"] for video in videos]))
        type_result = db.execute(select(MovType).where(MovType.type_id.in_(type_ids)))
        type_map = {t.type_id: t.type_name for t in type_result.scalars().all()}
        
        for video in videos:
            video["type_name"] = type_map.get(video["type_id"], "")
    
    return VideoListResponse(
        code=200,
        message="获取视频列表成功",
        data=videos,
        total=total,
        page=page,
        limit=limit
    )

@router.get("/video/detail/{video_id}", response_model=VideoDetailResponse)
def get_video_detail(
    video_id: int,
    db: Session = Depends(get_db)
):
    """
    获取视频详情（兼容现有Flask接口）
    同时查询MovInfo和MovDetail表，合并返回完整数据
    """
    # 首先尝试通过vod_id查询（这是两个表共有的字段）
    # 查询MovInfo表获取基本信息
    result = db.execute(select(MovInfo).where(MovInfo.vod_id == video_id))
    video_info = result.scalar_one_or_none()
    
    # 如果通过vod_id没找到，尝试通过MovInfo.id查询
    if video_info is None:
        result = db.execute(select(MovInfo).where(MovInfo.id == video_id))
        video_info = result.scalar_one_or_none()
        
        if video_info is None:
            return VideoDetailResponse(
                code=404,
                message="视频不存在"
            )
    
    # 查询MovDetail表获取详细信息（使用vod_id关联）
    detail_result = db.execute(select(MovDetail).where(MovDetail.vod_id == video_info.vod_id))
    video_detail = detail_result.scalar_one_or_none()
    
    # 获取类型名称
    type_result = db.execute(select(MovType).where(MovType.type_id == video_info.type_id))
    type_obj = type_result.scalar_one_or_none()
    if type_obj:
        video_info.type_name = type_obj.type_name
    
    # 合并数据：优先使用MovDetail表的详细信息，如果没有则使用MovInfo表的基本信息
    video_data = {
        # 基本信息（来自MovInfo）
        "id": video_info.id,
        "vod_id": video_info.vod_id,
        "vod_name": video_info.vod_name,
        "type_id": video_info.type_id,
        "type_name": video_info.type_name,
        "vod_remarks": video_info.vod_remarks,
        "vod_time": video_info.vod_time,
        
        # 详细信息（来自MovDetail，如果存在）
        "vod_pic": video_detail.vod_pic if video_detail else None,
        "vod_content": video_detail.vod_content if video_detail else None,
        "vod_director": video_detail.vod_director if video_detail else None,
        "vod_actor": video_detail.vod_actor if video_detail else None,
        "vod_area": video_detail.vod_area if video_detail else None,
        "vod_lang": video_detail.vod_lang if video_detail else None,
        "vod_year": video_detail.vod_year if video_detail else None,
        "vod_hits": video_detail.vod_hits if video_detail else 0,
        "vod_score": video_detail.vod_score if video_detail else None,
        "vod_play_url": video_detail.vod_play_url if video_detail else None
    }
    
    return VideoDetailResponse(
        code=200,
        message="获取视频详情成功",
        data=video_data
    )

@router.post("/video/search", response_model=VideoListResponse)
def search_videos(
    search_request: SearchRequest,
    db: Session = Depends(get_db)
):
    """
    搜索视频（兼容现有Flask接口）
    """
    keyword = search_request.keyword.strip()
    if not keyword:
        return VideoListResponse(
            code=400,
            message="请输入搜索关键词"
        )
    
    offset = (search_request.page - 1) * search_request.limit
    
    # 构建查询
    # 修改：使用JOIN查询关联MovInfo和MovDetail表，为重复字段指定别名
    query = select(
        MovInfo.id.label("info_id"),
        MovInfo.vod_id,
        MovInfo.vod_name,
        MovInfo.type_id.label("info_type_id"),
        MovInfo.type_name,
        MovInfo.vod_remarks,
        MovInfo.vod_time,
        MovDetail.id.label("detail_id"),
        MovDetail.vod_pic,
        MovDetail.vod_content,
        MovDetail.vod_director,
        MovDetail.vod_actor,
        MovDetail.vod_area,
        MovDetail.vod_lang,
        MovDetail.vod_year,
        MovDetail.vod_hits,
        MovDetail.vod_score,
        MovDetail.vod_play_url
    ).join(MovDetail, MovInfo.vod_id == MovDetail.vod_id).where(
        MovInfo.vod_name.like(f"%{keyword}%")
    )
    
    # 获取总数
    count_query = select(func.count()).select_from(query.subquery())
    total_result = db.execute(count_query)
    total = total_result.scalar()
    
    # 获取分页数据
    query = query.offset(offset).limit(search_request.limit).order_by(MovInfo.id.desc())
    result = db.execute(query)
    video_rows = result.all()
    
    # 合并数据：将MovInfo和MovDetail的数据合并
    videos = []
    for row in video_rows:
        video_data = {
            # 基本信息（来自MovInfo）
            "id": row.info_id,
            "vod_id": row.vod_id,
            "vod_name": row.vod_name,
            "type_id": row.info_type_id,
            "type_name": row.type_name,
            "vod_remarks": row.vod_remarks,
            "vod_time": row.vod_time,
            
            # 详细信息（来自MovDetail）
            "vod_pic": row.vod_pic,
            "vod_content": row.vod_content,
            "vod_director": row.vod_director,
            "vod_actor": row.vod_actor,
            "vod_area": row.vod_area,
            "vod_lang": row.vod_lang,
            "vod_year": row.vod_year,
            "vod_hits": row.vod_hits,
            "vod_score": row.vod_score,
            "vod_play_url": row.vod_play_url
        }
        videos.append(video_data)
    
    # 获取类型名称
    if videos:
        type_ids = list(set([video["type_id"] for video in videos]))
        type_result = db.execute(select(MovType).where(MovType.type_id.in_(type_ids)))
        type_map = {t.type_id: t.type_name for t in type_result.scalars().all()}
        
        for video in videos:
            video["type_name"] = type_map.get(video["type_id"], "")
    
    return VideoListResponse(
        code=200,
        message="搜索成功",
        data=videos,
        total=total,
        page=search_request.page,
        limit=search_request.limit
    )

@router.get("/video/play/{video_id}", response_model=VideoPlayResponse)
def get_video_play(
    video_id: int,
    db: Session = Depends(get_db)
):
    """
    获取视频播放地址（兼容现有Flask接口）
    查询MovDetail表获取播放地址
    """
    # 首先尝试通过vod_id查询MovDetail表
    result = db.execute(select(MovDetail).where(MovDetail.vod_id == video_id))
    video_detail = result.scalar_one_or_none()
    
    # 如果通过vod_id没找到，尝试通过MovInfo.id查找对应的vod_id
    if video_detail is None:
        # 先查询MovInfo表获取vod_id
        info_result = db.execute(select(MovInfo).where(MovInfo.id == video_id))
        video_info = info_result.scalar_one_or_none()
        
        if video_info is None:
            return VideoPlayResponse(
                code=404,
                message="视频播放地址不存在"
            )
        
        # 使用从MovInfo获取的vod_id查询MovDetail表
        result = db.execute(select(MovDetail).where(MovDetail.vod_id == video_info.vod_id))
        video_detail = result.scalar_one_or_none()
        
        if video_detail is None:
            return VideoPlayResponse(
                code=404,
                message="视频播放地址不存在"
            )
    
    # 解析播放地址
    play_urls = []
    if video_detail.vod_play_url:
        # 解析播放地址格式：第01集$https://example.com/1.mp4#第02集$https://example.com/2.mp4
        url_parts = video_detail.vod_play_url.split('#')
        for part in url_parts:
            if '$' in part:
                episode_name, episode_url = part.split('$', 1)
                
                # 强制使用测试视频源，让所有影片都播放同一个视频
                # 使用Mux提供的公开测试流，兼容所有现代浏览器
                fixed_test_url = "https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8"
                
                play_urls.append({
                    "episode": episode_name.strip(),
                    "url": fixed_test_url  # 替换为固定测试URL
                })
    
    return VideoPlayResponse(
        code=200,
        message="获取播放地址成功",
        data={
            "vod_id": video_detail.vod_id,
            "vod_name": video_detail.vod_name,
            "play_urls": play_urls
        }
    )

@router.get("/video/recommend")
def get_recommend_videos(
    limit: int = Query(10, ge=1, le=50, description="推荐数量"),
    db: Session = Depends(get_db)
):
    """
    获取推荐视频（兼容现有Flask接口）
    """
    # 按点击量排序获取热门视频
    # 修改：查询MovInfo表而不是MovDetail表
    # MovInfo表没有vod_hits字段，暂时按id排序
    query = select(MovInfo).order_by(
        MovInfo.id.desc()
    ).limit(limit)
    
    result = db.execute(query)
    videos = result.scalars().all()
    
    # 获取类型名称
    if videos:
        type_ids = list(set([video.type_id for video in videos]))
        type_result = db.execute(select(MovType).where(MovType.type_id.in_(type_ids)))
        type_map = {t.type_id: t.type_name for t in type_result.scalars().all()}
        
        for video in videos:
            video.type_name = type_map.get(video.type_id, "")
    
    return {
        "code": 200,
        "message": "获取推荐视频成功",
        "data": videos
    }