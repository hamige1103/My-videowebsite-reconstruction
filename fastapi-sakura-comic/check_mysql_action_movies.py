#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通过后端API检查MySQL数据库中的动作电影数据
"""

import requests
import json

def check_mysql_action_movies():
    """通过API检查动作电影数据"""
    
    base_url = "http://localhost:8000/api"
    
    print("🔍 通过后端API检查动作电影数据...")
    print("=" * 80)
    
    # 测试动作电影搜索
    test_cases = [
        {"question": "动作电影", "description": "基本动作电影搜索"},
        {"question": "动作片", "description": "动作片搜索"},
        {"question": "动作", "description": "动作关键词搜索"},
        {"question": "成龙电影", "description": "演员动作电影搜索"},
    ]
    
    for test_case in test_cases:
        question = test_case["question"]
        description = test_case["description"]
        
        print(f"\n📋 测试: {description} - '{question}'")
        
        try:
            # 发送搜索请求
            response = requests.post(
                f"{base_url}/v1/smart-search",
                headers={"Content-Type": "application/json"},
                json={"question": question}
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get("code") == 200:
                    data = result.get("data", {})
                    generated_sql = data.get("generated_sql", "")
                    results_count = len(data.get("results", []))
                    
                    print(f"   ✅ API调用成功")
                    print(f"   📊 生成SQL: {generated_sql}")
                    print(f"   📈 结果数量: {results_count}")
                    
                    # 显示前5个结果
                    if results_count > 0:
                        print(f"   📋 前5个结果:")
                        for j, item in enumerate(data.get("results", [])[:5], 1):
                            vod_name = item.get('vod_name', 'N/A')
                            type_name = item.get('type_name', 'N/A')
                            vod_year = item.get('vod_year', 'N/A')
                            print(f"      {j}. {vod_name} (分类: {type_name}, 年份: {vod_year})")
                    else:
                        print(f"   ⚠️  没有找到结果")
                        
                    # 检查SQL中的分类条件
                    if "type_name LIKE '%动作%'" in generated_sql:
                        print(f"   ✅ SQL正确使用了分类搜索")
                    else:
                        print(f"   ❌ SQL可能没有正确使用分类搜索")
                        
                else:
                    print(f"   ❌ API返回错误: {result.get('message', 'Unknown error')}")
            else:
                print(f"   ❌ HTTP错误: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ 请求异常: {str(e)}")
        
        print("-" * 60)
    
    # 检查数据库中的分类字段
    print("\n🔍 检查数据库中的分类字段...")
    
    # 通过直接查询API来获取分类信息
    try:
        # 使用一个通用搜索来获取分类示例
        response = requests.post(
            f"{base_url}/v1/smart-search",
            headers={"Content-Type": "application/json"},
            json={"question": "电影"}
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("code") == 200:
                data = result.get("data", {})
                results = data.get("results", [])
                
                if results:
                    print("\n📊 数据库中的分类示例:")
                    categories = set()
                    for item in results[:10]:  # 检查前10个结果的分类
                        type_name = item.get('type_name', '')
                        if type_name:
                            categories.add(type_name)
                    
                    for category in sorted(categories):
                        print(f"   - {category}")
                    
                    # 检查是否有动作相关的分类
                    action_categories = [cat for cat in categories if '动作' in cat]
                    if action_categories:
                        print(f"\n✅ 发现动作相关的分类: {action_categories}")
                    else:
                        print(f"\n⚠️  未发现包含'动作'的分类")
                
    except Exception as e:
        print(f"   ❌ 分类检查异常: {str(e)}")

if __name__ == "__main__":
    check_mysql_action_movies()