#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试智能搜索准确性优化效果
"""

import requests
import json

def test_search_accuracy():
    """测试搜索准确性"""
    
    # API配置
    base_url = "http://localhost:8000/api"
    endpoint = "/v1/smart-search"
    
    # 测试用例：各种搜索场景
    test_cases = [
        # 精确搜索（演员、导演）
        {"question": "成龙电影", "expected_type": "演员搜索", "expected_keyword": "成龙"},
        {"question": "周星驰作品", "expected_type": "演员搜索", "expected_keyword": "周星驰"},
        {"question": "张艺谋导演的电影", "expected_type": "导演搜索", "expected_keyword": "张艺谋"},
        
        # 分类搜索
        {"question": "动作电影", "expected_type": "分类搜索", "expected_keyword": "动作"},
        {"question": "喜剧片", "expected_type": "分类搜索", "expected_keyword": "喜剧"},
        {"question": "爱情电影", "expected_type": "分类搜索", "expected_keyword": "爱情"},
        
        # 年份搜索
        {"question": "2023年电影", "expected_type": "年份搜索", "expected_keyword": "2023"},
        {"question": "2022年上映的电影", "expected_type": "年份搜索", "expected_keyword": "2022"},
        
        # 评分搜索
        {"question": "高分电影", "expected_type": "评分搜索", "expected_keyword": "高分"},
        {"question": "9分以上的电影", "expected_type": "评分搜索", "expected_keyword": "9分"},
        
        # 地区搜索
        {"question": "中国电影", "expected_type": "地区搜索", "expected_keyword": "中国"},
        {"question": "美国电影", "expected_type": "地区搜索", "expected_keyword": "美国"},
        
        # 综合搜索
        {"question": "2023年动作电影", "expected_type": "综合搜索", "expected_keyword": "2023动作"},
        {"question": "中国爱情电影", "expected_type": "综合搜索", "expected_keyword": "中国爱情"},
        
        # 通用搜索
        {"question": "搜索复仇者联盟", "expected_type": "通用搜索", "expected_keyword": "复仇者联盟"},
        {"question": "找流浪地球", "expected_type": "通用搜索", "expected_keyword": "流浪地球"},
    ]
    
    print("🔍 开始测试智能搜索准确性...")
    print("=" * 80)
    
    success_count = 0
    total_count = len(test_cases)
    
    for i, test_case in enumerate(test_cases, 1):
        question = test_case["question"]
        expected_type = test_case["expected_type"]
        expected_keyword = test_case["expected_keyword"]
        
        print(f"\n📋 测试用例 {i}/{total_count}: {question}")
        print(f"   期望类型: {expected_type}")
        print(f"   期望关键词: {expected_keyword}")
        
        try:
            # 发送搜索请求
            response = requests.post(
                f"{base_url}{endpoint}",
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
                    
                    # 检查SQL是否包含期望的关键词
                    if expected_keyword in generated_sql:
                        print(f"   ✅ SQL包含期望关键词: {expected_keyword}")
                        success_count += 1
                    else:
                        print(f"   ❌ SQL未包含期望关键词: {expected_keyword}")
                    
                    # 显示前3个结果
                    if results_count > 0:
                        print(f"   📋 前3个结果:")
                        for j, item in enumerate(data.get("results", [])[:3], 1):
                            print(f"      {j}. {item.get('vod_name', 'N/A')} (ID: {item.get('id', 'N/A')})")
                else:
                    print(f"   ❌ API返回错误: {result.get('message', 'Unknown error')}")
            else:
                print(f"   ❌ HTTP错误: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ 请求异常: {str(e)}")
        
        print("-" * 60)
    
    # 统计结果
    accuracy = (success_count / total_count) * 100
    
    print("\n" + "=" * 80)
    print("📊 测试结果统计:")
    print(f"   总测试用例: {total_count}")
    print(f"   成功用例: {success_count}")
    print(f"   失败用例: {total_count - success_count}")
    print(f"   准确率: {accuracy:.2f}%")
    
    if accuracy >= 80:
        print("   🎉 搜索准确性良好！")
    elif accuracy >= 60:
        print("   ⚠️  搜索准确性一般，需要进一步优化")
    else:
        print("   ❌ 搜索准确性较差，需要大幅优化")
    
    return accuracy

if __name__ == "__main__":
    test_search_accuracy()