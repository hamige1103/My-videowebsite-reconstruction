#!/usr/bin/env python3
"""测试前端智能搜索功能"""

import requests
import json

# 前端API配置
base_url = 'http://localhost:8000/api'
headers = {
    'Content-Type': 'application/json',
    'X-Requested-With': 'XMLHttpRequest'
}

def test_frontend_smart_search():
    """测试前端智能搜索功能"""
    print('=== 测试前端智能搜索功能 ===\n')
    
    # 测试多个搜索问题
    test_cases = [
        "动作电影",
        "喜剧片",
        "爱情电影", 
        "科幻片",
        "2023年电影",
        "高分电影"
    ]
    
    for question in test_cases:
        print(f'🔍 测试问题: "{question}"')
        
        try:
            # 发送智能搜索请求
            url = f"{base_url}/v1/smart-search"
            data = {"question": question}
            
            response = requests.post(url, json=data, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                
                # 检查响应格式
                if 'code' in result and 'message' in result and 'data' in result:
                    if result['code'] == 200:
                        print(f'✅ API调用成功 - {result["message"]}')
                        print(f'   生成的SQL: {result["data"]["generated_sql"]}')
                        print(f'   结果数量: {result["data"]["total"]}')
                        
                        # 检查结果格式
                        if 'results' in result['data'] and isinstance(result['data']['results'], list):
                            print(f'   结果格式: ✅ 正确 (列表格式)')
                        else:
                            print(f'   结果格式: ❌ 错误')
                    else:
                        print(f'❌ API调用失败 - 错误码: {result["code"]}, 消息: {result["message"]}')
                else:
                    print(f'❌ 响应格式错误 - 缺少必要字段')
                    print(f'   响应内容: {json.dumps(result, indent=2, ensure_ascii=False)}')
            else:
                print(f'❌ HTTP错误: {response.status_code}')
                print(f'   响应内容: {response.text}')
                
        except Exception as e:
            print(f'❌ 请求异常: {e}')
        
        print()
    
    print('=== 测试完成 ===')

if __name__ == '__main__':
    test_frontend_smart_search()