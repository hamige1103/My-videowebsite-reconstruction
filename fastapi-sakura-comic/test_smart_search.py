#!/usr/bin/env python3
"""测试智能搜索功能 - 使用Python确保中文编码正确"""

import requests
import json

# 测试数据
test_questions = [
    "动作电影",
    "喜剧片", 
    "爱情电影",
    "科幻片"
]

url = "http://localhost:8000/api/v1/smart-search"
headers = {
    "Content-Type": "application/json; charset=utf-8"
}

for question in test_questions:
    print(f"\n=== 测试问题: {question} ===")
    
    # 准备请求数据
    data = {
        "question": question
    }
    
    # 发送请求
    try:
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            print(f"生成的SQL: {result['data']['generated_sql']}")
            print(f"搜索结果数量: {result['data']['total']}")
            
            # 显示前3个结果
            results = result['data']['results'][:3]
            for i, item in enumerate(results, 1):
                print(f"结果{i}: ID={item.get('vod_id')}, 名称={item.get('vod_name')}, 类型={item.get('type_name')}")
        else:
            print(f"请求失败: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"请求异常: {e}")

print("\n=== 测试完成 ===")