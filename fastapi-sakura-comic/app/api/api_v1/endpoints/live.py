"""
直播相关API端点
"""

from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import User
from app.models.live import LiveStream, LiveProduct as LiveProductModel
from app.api.deps import get_current_active_user
from app.schemas.live import LiveStreamResponse, LiveStreamCreate, LiveStreamUpdate, LiveStreamListResponse, LiveProduct
from app.services.obs_service import get_obs_service

router = APIRouter()


@router.get("/live/list", response_model=LiveStreamListResponse)
def get_live_list(
    page: int = 1,
    page_size: int = 20,
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取直播列表"""
    query = db.query(LiveStream).filter(LiveStream.status == "live")
    
    if category:
        query = query.filter(LiveStream.category == category)
    
    total = query.count()
    live_streams = query.offset((page - 1) * page_size).limit(page_size).all()
    
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": live_streams
    }


@router.post("/live/create", response_model=LiveStreamResponse)
def create_live_stream(
    live_data: LiveStreamCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """创建直播"""
    # 检查用户是否已有正在进行的直播
    existing_live = db.query(LiveStream).filter(
        LiveStream.host_id == current_user.id,
        LiveStream.status == "live"
    ).first()
    
    if existing_live:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="您已有正在进行的直播"
        )
    
    # 创建直播记录
    live_stream = LiveStream(
        title=live_data.title,
        description=live_data.description,
        category=live_data.category,
        host_id=current_user.id,
        host_name=current_user.username,
        quality=live_data.quality,
        is_private=live_data.is_private,
        enable_chat=live_data.enable_chat,
        enable_recording=live_data.enable_recording,
        status="preparing",
        created_at=datetime.now()
    )
    
    db.add(live_stream)
    db.commit()
    db.refresh(live_stream)
    
    # 生成推流地址和播放地址
    stream_key = f"live_{current_user.id}_{live_stream.id}"
    live_stream.stream_url = f"rtmp://localhost:1935/live/{stream_key}"
    live_stream.play_url = f"http://localhost:8000/live/{stream_key}.m3u8"
    
    db.commit()
    
    return live_stream


@router.get("/live/detail/{live_id}", response_model=LiveStreamResponse)
def get_live_detail(live_id: int, db: Session = Depends(get_db)):
    """获取直播详情"""
    live_stream = db.query(LiveStream).filter(LiveStream.id == live_id).first()
    
    if not live_stream:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="直播不存在"
        )
    
    return live_stream


@router.post("/live/start/{live_id}")
def start_live_stream(
    live_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """开始直播"""
    live_stream = db.query(LiveStream).filter(
        LiveStream.id == live_id,
        LiveStream.host_id == current_user.id
    ).first()
    
    if not live_stream:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="直播不存在或无权操作"
        )
    
    if live_stream.status == "live":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="直播已在进行中"
        )
    
    # 更新直播状态
    live_stream.status = "live"
    live_stream.start_time = datetime.now()
    live_stream.viewer_count = 0
    
    db.commit()
    
    return {"message": "直播已开始", "live_id": live_id}


@router.post("/live/stop/{live_id}")
def stop_live_stream(
    live_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """停止直播"""
    live_stream = db.query(LiveStream).filter(
        LiveStream.id == live_id,
        LiveStream.host_id == current_user.id
    ).first()
    
    if not live_stream:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="直播不存在或无权操作"
        )
    
    if live_stream.status != "live":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="直播未在进行中"
        )
    
    # 更新直播状态
    live_stream.status = "ended"
    live_stream.end_time = datetime.now()
    
    db.commit()
    
    return {"message": "直播已结束", "live_id": live_id}


@router.get("/live/stream/{live_id}")
def get_stream_url(live_id: int, db: Session = Depends(get_db)):
    """获取直播推流地址"""
    live_stream = db.query(LiveStream).filter(LiveStream.id == live_id).first()
    
    if not live_stream:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="直播不存在"
        )
    
    return {"stream_url": live_stream.stream_url}


@router.get("/live/play/{live_id}")
def get_play_url(live_id: int, db: Session = Depends(get_db)):
    """获取直播播放地址"""
    live_stream = db.query(LiveStream).filter(LiveStream.id == live_id).first()
    
    if not live_stream:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="直播不存在"
        )
    
    if live_stream.status != "live":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="直播未在进行中"
        )
    
    return {"play_url": live_stream.play_url}


@router.get("/live/hot")
def get_hot_lives(db: Session = Depends(get_db)):
    """获取热门直播"""
    hot_lives = db.query(LiveStream).filter(
        LiveStream.status == "live"
    ).order_by(LiveStream.viewer_count.desc()).limit(10).all()
    
    return {"items": hot_lives}


@router.get("/live/my-lives")
def get_my_lives(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取我的直播记录"""
    my_lives = db.query(LiveStream).filter(
        LiveStream.host_id == current_user.id
    ).order_by(LiveStream.created_at.desc()).all()
    
    return {"items": my_lives}


@router.get("/live/stats/{live_id}")
def get_live_stats(live_id: int, db: Session = Depends(get_db)):
    """获取直播统计数据"""
    live_stream = db.query(LiveStream).filter(LiveStream.id == live_id).first()
    
    if not live_stream:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="直播不存在"
        )
    
    stats = LiveStats(
        viewer_count=live_stream.viewer_count,
        like_count=live_stream.like_count,
        share_count=live_stream.share_count,
        duration=live_stream.duration,
        start_time=live_stream.start_time
    )
    
    return stats


@router.post("/live/{live_id}/products")
def add_live_product(
    live_id: int,
    product: LiveProduct,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """添加直播商品"""
    live_stream = db.query(LiveStream).filter(
        LiveStream.id == live_id,
        LiveStream.host_id == current_user.id
    ).first()
    
    if not live_stream:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="直播不存在或无权操作"
        )
    
    live_product = LiveProductModel(
        live_id=live_id,
        name=product.name,
        description=product.description,
        price=product.price,
        image_url=product.image_url,
        product_url=product.product_url,
        created_at=datetime.now()
    )
    
    db.add(live_product)
    db.commit()
    db.refresh(live_product)
    
    return {"message": "商品添加成功", "product_id": live_product.id}


@router.get("/live/{live_id}/products")
def get_live_products(live_id: int, db: Session = Depends(get_db)):
    """获取直播商品列表"""
    products = db.query(LiveProductModel).filter(
        LiveProductModel.live_id == live_id
    ).all()
    
    return {"items": products}


@router.delete("/live/{live_id}/products/{product_id}")
def remove_live_product(
    live_id: int,
    product_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """移除直播商品"""
    live_stream = db.query(LiveStream).filter(
        LiveStream.id == live_id,
        LiveStream.host_id == current_user.id
    ).first()
    
    if not live_stream:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="直播不存在或无权操作"
        )
    
    product = db.query(LiveProductModel).filter(
        LiveProductModel.id == product_id,
        LiveProductModel.live_id == live_id
    ).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="商品不存在"
        )
    
    db.delete(product)
    db.commit()
    
    return {"message": "商品移除成功"}