"""
直播带货相关API端点
"""

from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import User
from app.models.live import LiveStream, LiveProduct, LiveCommerceOrder
from app.api.deps import get_current_active_user
from app.schemas.live import LiveProduct, LiveCommerceOrder as LiveCommerceOrderSchema

router = APIRouter()


@router.post("/live/{live_id}/products", response_model=dict)
def add_live_product(
    live_id: int,
    product: LiveProduct,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """添加直播商品"""
    # 检查直播是否存在且用户是主播
    live_stream = db.query(LiveStream).filter(
        LiveStream.id == live_id,
        LiveStream.host_id == current_user.id
    ).first()
    
    if not live_stream:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="直播不存在或无权操作"
        )
    
    # 创建商品记录
    live_product = LiveProduct(
        live_id=live_id,
        name=product.name,
        description=product.description,
        price=product.price,
        original_price=product.original_price,
        image_url=product.image_url,
        product_url=product.product_url,
        stock=product.stock,
        created_at=datetime.now()
    )
    
    db.add(live_product)
    db.commit()
    db.refresh(live_product)
    
    return {
        "message": "商品添加成功",
        "product_id": live_product.id,
        "product": {
            "id": live_product.id,
            "name": live_product.name,
            "price": live_product.price,
            "image_url": live_product.image_url
        }
    }


@router.get("/live/{live_id}/products", response_model=dict)
def get_live_products(live_id: int, db: Session = Depends(get_db)):
    """获取直播商品列表"""
    live_stream = db.query(LiveStream).filter(LiveStream.id == live_id).first()
    
    if not live_stream:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="直播不存在"
        )
    
    products = db.query(LiveProduct).filter(
        LiveProduct.live_id == live_id,
        LiveProduct.is_active == True
    ).all()
    
    product_list = []
    for product in products:
        product_list.append({
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "price": product.price,
            "original_price": product.original_price,
            "image_url": product.image_url,
            "product_url": product.product_url,
            "stock": product.stock,
            "sold_count": product.sold_count,
            "is_active": product.is_active
        })
    
    return {
        "live_id": live_id,
        "live_title": live_stream.title,
        "products": product_list
    }


@router.put("/live/{live_id}/products/{product_id}", response_model=dict)
def update_live_product(
    live_id: int,
    product_id: int,
    product: LiveProduct,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """更新直播商品"""
    # 检查直播和商品是否存在
    live_stream = db.query(LiveStream).filter(
        LiveStream.id == live_id,
        LiveStream.host_id == current_user.id
    ).first()
    
    if not live_stream:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="直播不存在或无权操作"
        )
    
    live_product = db.query(LiveProduct).filter(
        LiveProduct.id == product_id,
        LiveProduct.live_id == live_id
    ).first()
    
    if not live_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="商品不存在"
        )
    
    # 更新商品信息
    live_product.name = product.name
    live_product.description = product.description
    live_product.price = product.price
    live_product.original_price = product.original_price
    live_product.image_url = product.image_url
    live_product.product_url = product.product_url
    live_product.stock = product.stock
    
    db.commit()
    
    return {"message": "商品更新成功", "product_id": product_id}


@router.delete("/live/{live_id}/products/{product_id}", response_model=dict)
def remove_live_product(
    live_id: int,
    product_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """移除直播商品"""
    # 检查直播和商品是否存在
    live_stream = db.query(LiveStream).filter(
        LiveStream.id == live_id,
        LiveStream.host_id == current_user.id
    ).first()
    
    if not live_stream:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="直播不存在或无权操作"
        )
    
    live_product = db.query(LiveProduct).filter(
        LiveProduct.id == product_id,
        LiveProduct.live_id == live_id
    ).first()
    
    if not live_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="商品不存在"
        )
    
    # 软删除商品（设置为非激活状态）
    live_product.is_active = False
    db.commit()
    
    return {"message": "商品移除成功"}


@router.post("/live/{live_id}/orders", response_model=dict)
def create_live_order(
    live_id: int,
    order_data: LiveCommerceOrderSchema,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """创建直播带货订单"""
    # 检查直播是否存在
    live_stream = db.query(LiveStream).filter(LiveStream.id == live_id).first()
    
    if not live_stream:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="直播不存在"
        )
    
    # 检查商品是否存在且有库存
    product = db.query(LiveProduct).filter(
        LiveProduct.id == order_data.product_id,
        LiveProduct.live_id == live_id,
        LiveProduct.is_active == True
    ).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="商品不存在"
        )
    
    if product.stock < order_data.quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="商品库存不足"
        )
    
    # 计算总价
    total_price = product.price * order_data.quantity
    
    # 创建订单
    live_order = LiveCommerceOrder(
        live_id=live_id,
        product_id=order_data.product_id,
        user_id=current_user.id,
        username=current_user.username,
        quantity=order_data.quantity,
        total_price=total_price,
        buyer_name=order_data.buyer_name,
        buyer_contact=order_data.buyer_contact,
        shipping_address=order_data.shipping_address,
        status="pending",
        created_at=datetime.now()
    )
    
    # 更新商品库存和销量
    product.stock -= order_data.quantity
    product.sold_count += order_data.quantity
    
    db.add(live_order)
    db.commit()
    db.refresh(live_order)
    
    return {
        "message": "订单创建成功",
        "order_id": live_order.id,
        "total_price": total_price
    }


@router.get("/live/{live_id}/orders", response_model=dict)
def get_live_orders(
    live_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取直播订单列表（仅主播可查看）"""
    # 检查直播是否存在且用户是主播
    live_stream = db.query(LiveStream).filter(
        LiveStream.id == live_id,
        LiveStream.host_id == current_user.id
    ).first()
    
    if not live_stream:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="直播不存在或无权查看"
        )
    
    orders = db.query(LiveCommerceOrder).filter(
        LiveCommerceOrder.live_id == live_id
    ).order_by(LiveCommerceOrder.created_at.desc()).all()
    
    order_list = []
    for order in orders:
        order_list.append({
            "id": order.id,
            "product_id": order.product_id,
            "username": order.username,
            "quantity": order.quantity,
            "total_price": order.total_price,
            "status": order.status,
            "created_at": order.created_at
        })
    
    return {
        "live_id": live_id,
        "total_orders": len(orders),
        "total_revenue": sum(order.total_price for order in orders),
        "orders": order_list
    }


@router.get("/live/{live_id}/stats/commerce", response_model=dict)
def get_live_commerce_stats(
    live_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取直播带货统计数据"""
    # 检查直播是否存在且用户是主播
    live_stream = db.query(LiveStream).filter(
        LiveStream.id == live_id,
        LiveStream.host_id == current_user.id
    ).first()
    
    if not live_stream:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="直播不存在或无权查看"
        )
    
    # 获取商品统计
    products = db.query(LiveProduct).filter(
        LiveProduct.live_id == live_id
    ).all()
    
    # 获取订单统计
    orders = db.query(LiveCommerceOrder).filter(
        LiveCommerceOrder.live_id == live_id
    ).all()
    
    total_products = len(products)
    total_orders = len(orders)
    total_revenue = sum(order.total_price for order in orders)
    total_sold = sum(product.sold_count for product in products)
    
    # 热销商品排行
    top_products = sorted(products, key=lambda x: x.sold_count, reverse=True)[:5]
    
    top_products_list = []
    for product in top_products:
        top_products_list.append({
            "id": product.id,
            "name": product.name,
            "sold_count": product.sold_count,
            "revenue": product.price * product.sold_count
        })
    
    return {
        "live_id": live_id,
        "total_products": total_products,
        "total_orders": total_orders,
        "total_revenue": total_revenue,
        "total_sold": total_sold,
        "top_products": top_products_list
    }


@router.post("/live/{live_id}/promote/{product_id}", response_model=dict)
def promote_live_product(
    live_id: int,
    product_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """推广直播商品（在聊天室中展示）"""
    # 检查直播和商品是否存在
    live_stream = db.query(LiveStream).filter(
        LiveStream.id == live_id,
        LiveStream.host_id == current_user.id
    ).first()
    
    if not live_stream:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="直播不存在或无权操作"
        )
    
    product = db.query(LiveProduct).filter(
        LiveProduct.id == product_id,
        LiveProduct.live_id == live_id
    ).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="商品不存在"
        )
    
    # 在实际项目中，这里会发送WebSocket消息到聊天室
    # 暂时返回成功信息
    return {
        "message": "商品推广成功",
        "product": {
            "id": product.id,
            "name": product.name,
            "price": product.price,
            "image_url": product.image_url
        }
    }