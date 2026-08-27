#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查MySQL数据库中的分类字段实际值
"""

import requests
import json

def check_mysql_categories():
    """检查数据库中的分类字段"""
    
    base_url = "http://localhost:8000/api"
    
    print("🔍 检查MySQL数据库中的分类字段...")
    print("=" * 80)
    
    # 测试不同的搜索来获取分类信息
    test_cases = [
        {"question": "电影", "description": "通用电影搜索"},
        {"question": "电视剧", "description": "电视剧搜索"},
        {"question": "动漫", "description": "动漫搜索"},
        {"question": "动作", "description": "动作内容搜索"},
        {"question": "爱情", "description": "爱情内容搜索"},
        {"question": "喜剧", "description": "喜剧内容搜索"},
    ]
    
    all_categories = set()
    
    for test_case in test_cases:
        question = test_case["question"]
        description = test_case["description"]
        
        print(f"\n📋 测试: {description} - '{question}'")
        
        try:
            response = requests.post(
                f"{base_url}/v1/smart-search",
                headers={"Content-Type": "application/json"},
                json={"question": question}
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("code") == 200:
                    data = result.get("data", {})
                    results = data.get("results", [])
                    
                    print(f"   ✅ 找到 {len(results)} 个结果")
                    
                    # 收集分类信息
                    for item in results:
                        type_name = item.get('type_name', '')
                        if type_name and type_name != 'N/A':
                            all_categories.add(type_name)
                    
                    # 显示前3个结果的详细信息
                    for j, item in enumerate(results[:3], 1):
                        vod_name = item.get('vod_name', 'N/A')
                        type_name = item.get('type_name', 'N/A')
                        vod_year = item.get('vod_year', 'N/A')
                        vod_actor = item.get('vod_actor', 'N/A')[:50] + "..." if item.get('vod_actor') else 'N/A'
                        vod_content = item.get('vod_content', 'N/A')[:100] + "..." if item.get('vod_content') else 'N/A'
                        
                        print(f"   {j}. 名称: {vod_name}")
                        print(f"      分类: {type_name}")
                        print(f"      年份: {vod_year}")
                        print(f"      演员: {vod_actor}")
                        print(f"      简介: {vod_content}")
                        
                else:
                    print(f"   ❌ API错误: {result.get('message', 'Unknown error')}")
            else:
                print(f"   ❌ HTTP错误: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ 请求异常: {str(e)}")
    
    # 显示所有收集到的分类
    print("\n📊 数据库中实际存在的分类:")
    if all_categories:
        for category in sorted(all_categories):
            print(f"   - {category}")
    else:
        print("   ⚠️  未找到有效的分类信息")
    
    # 检查分类字段是否为空或默认值
    print("\n🔍 检查分类字段问题...")
    
    # 通过直接查询数据库结构来检查
    try:
        # 使用一个能返回结果的搜索
        response = requests.post(
            f"{base_url}/v1/smart-search",
            headers={"Content-Type": "application/json"},
            json={"question": "最新电影"}
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("code") == 200:
                data = result.get("data", {})
                results = data.get("results", [])
                
                if results:
                    print("\n📋 检查分类字段值:")
                    type_name_values = {}
                    
                    for item in results:
                        type_name = item.get('type_name', '')
                        if type_name not in type_name_values:
                            type_name_values[type_name] = 0
                        type_name_values[type_name] += 1
                    
                    for type_name, count in type_name_values.items():
                        print(f"   - '{type_name}': {count} 个记录")
                        
                    # 检查是否有空值或默认值
                    empty_or_default = [k for k in type_name_values.keys() if not k or k == 'N/A' or k == 'null']
                    if empty_or_default:
                        print(f"\n⚠️  发现空值或默认值分类: {empty_or_default}")
                        print("   这可能是动作电影搜索不到的原因！")
                    
    except Exception as e:
        print(f"   ❌ 检查异常: {str(e)}")

if __name__ == "__main__":
    check_mysql_categories()