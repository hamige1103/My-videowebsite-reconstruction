#!/usr/bin/env python3
"""模拟前端调用智能搜索API"""

import requests
import json

# 模拟前端axios配置
base_url = 'http://localhost:8000/api'
headers = {
    'Content-Type': 'application/json',
    'X-Requested-With': 'XMLHttpRequest'
}

def test_smart_search():
    """测试智能搜索API"""
    try:
        print('=== 测试前端API调用 ===')
        
        # 测试智能搜索
        url = f"{base_url}/v1/smart-search"
        data = {
            "question": "动作电影"
        }
        
        response = requests.post(url, json=data, headers=headers)
        
        print(f'API响应状态: {response.status_code}')
        print(f'API响应数据: {json.dumps(response.json(), indent=2, ensure_ascii=False)}')
        
        if response.status_code == 200:
            result = response.json()
            if result.get('code') == 200:
                print('✅ 智能搜索API调用成功')
                print(f'生成的SQL: {result["data"]["generated_sql"]}')
                print(f'结果数量: {result["data"]["total"]}')
                
                # 显示前3个结果
                results = result['data']['results'][:3]
                for i, item in enumerate(results, 1):
                    print(f'结果{i}: ID={item.get("vod_id")}, 名称={item.get("vod_name")}')
            else:
                print(f'❌ 智能搜索API调用失败: {result.get("message")}')
        else:
            print(f'❌ HTTP错误: {response.status_code}')
            
    except Exception as e:
        print(f'❌ API调用异常: {e}')

if __name__ == '__main__':
    test_smart_search()