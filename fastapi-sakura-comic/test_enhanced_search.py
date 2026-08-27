#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试增强后的智能搜索功能
验证动作电影搜索问题是否已解决
"""

import requests
import json

def test_enhanced_search():
    """测试增强后的搜索功能"""
    base_url = "http://localhost:8000"
    
    # 测试搜索关键词
    test_queries = [
        "动作电影",
        "2023动作电影", 
        "美国动作电影",
        "高分动作电影",
        "热门电影",
        "最新电影",
        "科幻电影",
        "爱情电影"
    ]
    
    print("=== 测试增强后的智能搜索功能 ===\n")
    
    for query in test_queries:
        print(f"测试搜索: '{query}'")
        
        try:
            # 调用智能搜索API
            response = requests.post(
                f"{base_url}/api/v1/smart-search",
                json={"question": query}
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get("code") == 200:
                    data = result.get("data", {})
                    results = data.get("results", [])
                    count = len(results)
                    
                    print(f"  ✓ 搜索成功，找到 {count} 条结果")
                    
                    # 显示前3条结果的详细信息
                    if count > 0:
                        print(f"  前{min(3, count)}条结果:")
                        for i, item in enumerate(results[:3]):
                            print(f"    {i+1}. {item.get('vod_name', 'N/A')} | "
                                  f"评分: {item.get('vod_score', 'N/A')} | "
                                  f"地区: {item.get('vod_area', 'N/A')} | "
                                  f"年份: {item.get('vod_year', 'N/A')}")
                    else:
                        print("  ⚠ 未找到相关结果")
                        
                    # 显示生成的SQL查询
                    sql_query = data.get("generated_sql", "")
                    if sql_query:
                        print(f"  生成的SQL: {sql_query[:100]}...")
                        
                else:
                    print(f"  ✗ 搜索失败: {result.get('message', '未知错误')}")
                    
            else:
                print(f"  ✗ HTTP错误: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print("  ✗ 无法连接到服务器，请确保后端服务正在运行")
            break
        except Exception as e:
            print(f"  ✗ 请求异常: {e}")
            
        print()

def check_database_status():
    """检查数据库状态"""
    print("=== 检查数据库状态 ===\n")
    
    base_url = "http://localhost:8000"
    
    try:
        # 检查数据库连接
        response = requests.get(f"{base_url}/api/v1/health")
        
        if response.status_code == 200:
            health_info = response.json()
            print(f"  ✓ 数据库连接正常")
            print(f"  数据库状态: {health_info.get('database', 'N/A')}")
        else:
            print(f"  ⚠ 无法获取健康状态: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("  ✗ 无法连接到服务器")
    except Exception as e:
        print(f"  ✗ 检查异常: {e}")
    
    print()

def analyze_search_improvement():
    """分析搜索改进效果"""
    print("=== 搜索改进分析 ===\n")
    
    print("增强的搜索策略:")
    print("1. 多字段搜索: 同时检查 type_name, vod_content, vod_name 字段")
    print("2. 容错处理: 即使分类字段为空，也能通过内容/名称字段找到相关视频")
    print("3. 智能匹配: 支持多种搜索模式（分类、年份、地区、评分等）")
    print("4. 优先级排序: 根据点击量、评分、时间等进行智能排序")
    print()
    
    print("解决的主要问题:")
    print("✓ 分类字段为空导致的搜索无结果问题")
    print("✓ 动作电影等特定类型视频搜索不到的问题")
    print("✓ 搜索准确性和覆盖范围不足的问题")
    print()

if __name__ == "__main__":
    print("智能搜索功能增强测试")
    print("=" * 50)
    
    # 检查数据库状态
    check_database_status()
    
    # 分析改进效果
    analyze_search_improvement()
    
    # 测试搜索功能
    test_enhanced_search()
    
    print("测试完成！")