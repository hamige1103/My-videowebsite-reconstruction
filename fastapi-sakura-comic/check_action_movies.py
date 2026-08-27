#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查动作电影数据，分析搜索问题
"""

import sqlite3

def check_action_movies():
    """检查动作电影数据"""
    
    try:
        conn = sqlite3.connect('sakura_comic.db')
        cursor = conn.cursor()
        
        print("🔍 检查动作电影数据...")
        print("=" * 60)
        
        # 1. 检查动作类别的不同分类名称
        cursor.execute('SELECT DISTINCT type_name FROM sakura_movdetail WHERE type_name LIKE "%动作%" LIMIT 10')
        print('\n动作类别的不同分类名称:')
        action_categories = cursor.fetchall()
        for row in action_categories:
            print(f'  {row[0]}')
        
        # 2. 检查动作电影的数量
        cursor.execute('SELECT COUNT(*) FROM sakura_movdetail WHERE type_name LIKE "%动作%"')
        action_count = cursor.fetchone()[0]
        print(f'\n动作电影总数: {action_count}')
        
        # 3. 检查一些具体的动作电影示例
        cursor.execute('SELECT vod_name, type_name, vod_year FROM sakura_movdetail WHERE type_name LIKE "%动作%" LIMIT 10')
        print('\n动作电影示例:')
        action_movies = cursor.fetchall()
        for i, row in enumerate(action_movies, 1):
            print(f'  {i}. 名称: {row[0]}, 分类: {row[1]}, 年份: {row[2]}')
        
        # 4. 检查分类字段的格式
        cursor.execute('SELECT DISTINCT type_name FROM sakura_movdetail LIMIT 15')
        print('\n所有分类字段示例:')
        all_categories = cursor.fetchall()
        for row in all_categories:
            print(f'  {row[0]}')
        
        # 5. 检查是否有电影分类不包含"动作"但可能是动作电影
        cursor.execute('''
            SELECT vod_name, type_name, vod_content 
            FROM sakura_movdetail 
            WHERE (vod_name LIKE "%动作%" OR vod_content LIKE "%动作%")
            AND type_name NOT LIKE "%动作%"
            LIMIT 5
        ''')
        print('\n可能被遗漏的动作电影（分类不包含"动作"但内容包含）:')
        missed_movies = cursor.fetchall()
        for i, row in enumerate(missed_movies, 1):
            print(f'  {i}. 名称: {row[0]}, 分类: {row[1]}, 内容片段: {row[2][:50]}...')
        
        conn.close()
        
        print("\n" + "=" * 60)
        print("📊 分析结果:")
        print(f"   动作电影总数: {action_count}")
        print(f"   动作分类种类: {len(action_categories)}")
        print(f"   可能遗漏的动作电影: {len(missed_movies)}")
        
        if len(missed_movies) > 0:
            print("\n⚠️  发现可能被遗漏的动作电影！")
            print("   这些电影在名称或内容中包含'动作'，但分类字段不包含'动作'")
        
    except Exception as e:
        print(f"❌ 数据库查询错误: {str(e)}")

if __name__ == "__main__":
    check_action_movies()