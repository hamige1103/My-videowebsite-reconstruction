#!/usr/bin/env python3
"""
创建管理员用户脚本
"""

from sqlalchemy import select

from app.core.database import SessionLocal
from app.models.models import User
from app.core.security import get_password_hash

def create_admin_user():
    """创建管理员用户"""
    session = SessionLocal()
    try:
        # 检查是否已存在管理员用户
        existing_admin = session.query(User).filter(User.name == "admin").first()
        
        if existing_admin:
            print("管理员用户已存在")
            return
        
        # 创建管理员用户
        admin_user = User(
            name="admin",
            password_hash=get_password_hash("admin123"),
            role="admin"
        )
        
        session.add(admin_user)
        session.commit()
        print("管理员用户创建成功")
        
        # 检查用户表数据
        users = session.query(User).all()
        print(f"当前用户表中共有 {len(users)} 个用户:")
        for user in users:
            print(f"  - ID: {user.id}, 用户名: {user.name}, 角色: {user.role}")
    finally:
        session.close()

if __name__ == "__main__":
    create_admin_user()