#!/usr/bin/env python3
"""
重新创建数据库表脚本
"""

import os
from app.core.database import engine, Base, create_tables

def recreate_database():
    """重新创建数据库表"""
    # 重新创建表
    Base.metadata.drop_all(bind=engine)
    print("已删除现有数据库表")
    
    Base.metadata.create_all(bind=engine)
    print("数据库表重新创建完成")

if __name__ == "__main__":
    recreate_database()