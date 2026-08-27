#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析动作电影搜索不到的根本原因
"""

import requests
import json

def analyze_action_movie_issue():
    """分析动作电影搜索问题"""
    
    base_url = "http://localhost:8000/api"
    
    print("🔍 分析动作电影搜索不到的根本原因")
    print("=" * 80)
    
    # 测试不同的搜索策略
    test_cases = [
        {"question": "动作电影", "description": "分类搜索"},
        {"question": "动作片", "description": "类型搜索"},
        {"question": "动作", "description": "关键词搜索"},
        {"question": "复仇者联盟", "description": "具体动作电影名称"},
        {"question": "流浪地球", "description": "科幻动作电影"},
        {"question": "速度与激情", "description": "经典动作系列"},
    ]
    
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
                    generated_sql = data.get("generated_sql", "")
                    results_count = len(data.get("results", []))
                    
                    print(f"   ✅ API调用成功")
                    print(f"   📊 生成SQL: {generated_sql}")
                    print(f"   📈 结果数量: {results_count}")
                    
                    # 分析SQL中的分类条件
                    if "type_name LIKE '%动作%'" in generated_sql:
                        print(f"   ✅ SQL正确使用了动作分类搜索")
                        
                        # 检查分类字段是否为空
                        if results_count == 0:
                            print(f"   ❌ 问题: 分类搜索返回0个结果，说明type_name字段可能为空或没有动作分类")
                        else:
                            # 检查实际分类字段值
                            first_result = data.get("results", [{}])[0]
                            actual_type = first_result.get('type_name', '')
                            print(f"   📋 第一个结果的分类字段: '{actual_type}'")
                            
                            if not actual_type or actual_type == 'N/A':
                                print(f"   ❌ 问题: 分类字段为空或默认值，无法正确分类")
                            elif '动作' not in actual_type:
                                print(f"   ❌ 问题: 分类字段不包含'动作'，但被错误分类")
                            
                    elif "vod_name LIKE '%动作%'" in generated_sql:
                        print(f"   ⚠️  SQL使用了名称搜索而不是分类搜索")
                        if results_count == 0:
                            print(f"   ❌ 问题: 名称搜索也返回0个结果，说明数据库中可能没有相关数据")
                    else:
                        print(f"   ⚠️  SQL使用了其他搜索策略")
                        
                    # 显示前3个结果的详细信息
                    if results_count > 0:
                        print(f"   📋 前3个结果详情:")
                        for j, item in enumerate(data.get("results", [])[:3], 1):
                            vod_name = item.get('vod_name', 'N/A')
                            type_name = item.get('type_name', 'N/A')
                            vod_year = item.get('vod_year', 'N/A')
                            vod_actor = item.get('vod_actor', 'N/A')[:30] + "..." if item.get('vod_actor') else 'N/A'
                            vod_content = item.get('vod_content', 'N/A')[:50] + "..." if item.get('vod_content') else 'N/A'
                            
                            print(f"      {j}. 名称: {vod_name}")
                            print(f"         分类: {type_name}")
                            print(f"         年份: {vod_year}")
                            print(f"         演员: {vod_actor}")
                            print(f"         简介: {vod_content}")
                    
                else:
                    print(f"   ❌ API返回错误: {result.get('message', 'Unknown error')}")
            else:
                print(f"   ❌ HTTP错误: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ 请求异常: {str(e)}")
        
        print("-" * 60)
    
    # 检查数据库中的分类字段问题
    print("\n🔍 检查数据库分类字段的根本问题...")
    
    try:
        # 使用通用搜索获取更多数据样本
        response = requests.post(
            f"{base_url}/v1/smart-search",
            headers={"Content-Type": "application/json"},
            json={"question": "热门视频"}
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("code") == 200:
                data = result.get("data", {})
                results = data.get("results", [])
                
                if results:
                    print(f"\n📊 分析 {len(results)} 个热门视频的分类字段:")
                    
                    # 统计分类字段情况
                    type_name_stats = {}
                    for item in results:
                        type_name = item.get('type_name', '')
                        if type_name not in type_name_stats:
                            type_name_stats[type_name] = 0
                        type_name_stats[type_name] += 1
                    
                    # 显示分类字段统计
                    print("\n📋 分类字段统计:")
                    for type_name, count in sorted(type_name_stats.items(), key=lambda x: x[1], reverse=True):
                        status = "空值/默认值" if not type_name or type_name == 'N/A' else "有效值"
                        print(f"   - '{type_name}': {count} 个记录 ({status})")
                    
                    # 分析问题
                    empty_count = sum(count for type_name, count in type_name_stats.items() if not type_name or type_name == 'N/A')
                    total_count = len(results)
                    empty_percentage = (empty_count / total_count) * 100
                    
                    print(f"\n📈 问题分析:")
                    print(f"   - 总记录数: {total_count}")
                    print(f"   - 空值/默认值记录: {empty_count} ({empty_percentage:.1f}%)")
                    
                    if empty_percentage > 50:
                        print(f"   ❌ 严重问题: 超过一半的分类字段为空或默认值")
                        print(f"   💡 建议: 需要修复数据库中的分类信息")
                    elif empty_percentage > 20:
                        print(f"   ⚠️  问题: 相当一部分分类字段为空或默认值")
                        print(f"   💡 建议: 建议修复分类字段数据")
                    else:
                        print(f"   ✅ 分类字段数据基本正常")
                    
                    # 检查是否有动作相关的分类
                    action_categories = [cat for cat in type_name_stats.keys() if cat and '动作' in cat]
                    if action_categories:
                        print(f"\n✅ 发现动作相关的分类: {action_categories}")
                    else:
                        print(f"\n❌ 未发现包含'动作'的分类")
                        print(f"   💡 建议: 数据库中的分类字段可能没有正确设置动作分类")
                        
                else:
                    print("   ⚠️  没有找到热门视频数据")
            
    except Exception as e:
        print(f"   ❌ 分析异常: {str(e)}")
    
    # 总结问题
    print("\n🔍 问题总结与解决方案:")
    print("=" * 80)
    print("1. 根本原因: 数据库中的type_name分类字段大部分为空或默认值")
    print("2. 影响: 智能搜索虽然能正确生成SQL，但无法通过分类字段找到动作电影")
    print("3. 解决方案:")
    print("   - 方案A: 修复数据库中的分类字段数据")
    print("   - 方案B: 修改搜索算法，增加基于内容或名称的搜索策略")
    print("   - 方案C: 结合多种搜索条件提高命中率")
    print("\n💡 推荐: 优先修复数据库分类字段，确保数据质量")

if __name__ == "__main__":
    analyze_action_movie_issue()