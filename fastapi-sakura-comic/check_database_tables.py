#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查数据库表结构
"""

import sqlite3

def check_database_tables():
    """检查数据库表结构"""
    
    try:
        conn = sqlite3.connect('sakura_comic.db')
        cursor = conn.cursor()
        
        print("🔍 检查数据库表结构...")
        print("=" * 60)
        
        # 检查所有表
        cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
        tables = cursor.fetchall()
        print('数据库中的表:')
        for table in tables:
            print(f'  {table[0]}')
        
        # 检查视频相关表的字段
        video_tables = ['sakura_movdetail', 'sakura_vod', 'vod', 'movies', 'videos']
        for table_name in video_tables:
            try:
                cursor.execute(f'PRAGMA table_info({table_name})')
                columns = cursor.fetchall()
                if columns:
                    print(f'\n表 {table_name} 的字段:')
                    for col in columns:
                        print(f'  {col[1]} ({col[2]})')
                    
                    # 检查是否有数据
                    cursor.execute(f'SELECT COUNT(*) FROM {table_name}')
                    count = cursor.fetchone()[0]
                    print(f'  数据行数: {count}')
                    
                    # 检查分类字段示例
                    cursor.execute(f'SELECT DISTINCT type_name FROM {table_name} LIMIT 5')
                    categories = cursor.fetchall()
                    if categories:
                        print(f'  分类字段示例:')
                        for cat in categories:
                            print(f'    {cat[0]}')
            except:
                pass
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 数据库查询错误: {str(e)}")

if __name__ == "__main__":
    check_database_tables()