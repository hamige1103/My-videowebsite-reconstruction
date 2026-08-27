"""
智能搜索API端点 - 模仿M2_UGL_2中的SQL Agent模式
实现：用户问题 -> 生成SQL -> 执行SQL -> 返回结果
"""

from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Dict, Any, List
import json

from app.core.database import get_db
from app.models.models import MovType, MovInfo, MovDetail
from app.services.qianwen_service import get_qianwen_service

router = APIRouter()

class SQLGenerator:
    """SQL生成器 - 模仿M2_UGL_2中的实现"""
    
    def __init__(self):
        self.schema = self._get_database_schema()
    
    def _get_database_schema(self) -> str:
        """获取数据库表结构描述"""
        return """
        数据库表结构：
        
        主要搜索表：sakura_movdetail (视频详情表)
           - vod_id: Integer (唯一，视频ID)
           - vod_name: Text (视频名称)
           - type_name: String(20) (视频类型，如：动作片、喜剧片、爱情片、科幻片、剧情片、恐怖片、动画电影、纪录片等)
           - vod_actor: Text (演员)
           - vod_area: Text (地区)
           - vod_director: Text (导演)
           - vod_content: Text (内容简介)
           - vod_year: Text (年份)
           - vod_lang: Text (语言)
           - vod_score: Text (评分)
           - vod_hits: Integer (点击量)
           - vod_pic: Text (封面图片)
           - vod_play_url: Text (播放地址)
           
        重要说明：
        1. type_name字段存储具体的视频类型，如：动作片、喜剧片、爱情片等
        2. 使用LIKE进行模糊匹配时，应该搜索type_name LIKE '%动作%'来查找动作片
        3. 按vod_hits降序排序可以显示热门视频
        4. 按vod_time降序排序可以显示最新视频
        5. 按vod_score降序排序可以显示高分视频
        """
    
    def generate_sql(self, question: str) -> str:
        """根据用户问题生成SQL查询语句"""
        
        # 问题分类和SQL模板映射 - 按优先级从高到低排列
        question_patterns = {
            # 高优先级：精确匹配（演员、导演、具体名称）
            "成龙.*": "SELECT * FROM sakura_movdetail WHERE vod_actor LIKE '%成龙%' ORDER BY vod_hits DESC",
            "周星驰.*": "SELECT * FROM sakura_movdetail WHERE vod_actor LIKE '%周星驰%' ORDER BY vod_hits DESC",
            "张艺谋.*": "SELECT * FROM sakura_movdetail WHERE vod_director LIKE '%张艺谋%' ORDER BY vod_hits DESC",
            "冯小刚.*": "SELECT * FROM sakura_movdetail WHERE vod_director LIKE '%冯小刚%' ORDER BY vod_hits DESC",
            
            # 高优先级：综合搜索（精确匹配，增强版）
            "2023.*动作.*电影": "SELECT * FROM sakura_movdetail WHERE (type_name LIKE '%动作%' OR vod_content LIKE '%动作%' OR vod_name LIKE '%动作%') AND vod_year LIKE '%2023%' AND (type_name LIKE '%电影%' OR vod_content LIKE '%电影%' OR vod_name LIKE '%电影%') ORDER BY vod_hits DESC",
            "2022.*动作.*电影": "SELECT * FROM sakura_movdetail WHERE (type_name LIKE '%动作%' OR vod_content LIKE '%动作%' OR vod_name LIKE '%动作%') AND vod_year LIKE '%2022%' AND (type_name LIKE '%电影%' OR vod_content LIKE '%电影%' OR vod_name LIKE '%电影%') ORDER BY vod_hits DESC",
            "2021.*动作.*电影": "SELECT * FROM sakura_movdetail WHERE (type_name LIKE '%动作%' OR vod_content LIKE '%动作%' OR vod_name LIKE '%动作%') AND vod_year LIKE '%2021%' AND (type_name LIKE '%电影%' OR vod_content LIKE '%电影%' OR vod_name LIKE '%电影%') ORDER BY vod_hits DESC",
            "中国.*爱情.*电影": "SELECT * FROM sakura_movdetail WHERE (type_name LIKE '%爱情%' OR vod_content LIKE '%爱情%' OR vod_name LIKE '%爱情%') AND vod_area LIKE '%中国%' AND (type_name LIKE '%电影%' OR vod_content LIKE '%电影%' OR vod_name LIKE '%电影%') ORDER BY vod_hits DESC",
            "美国.*科幻.*电影": "SELECT * FROM sakura_movdetail WHERE (type_name LIKE '%科幻%' OR vod_content LIKE '%科幻%' OR vod_name LIKE '%科幻%') AND vod_area LIKE '%美国%' AND (type_name LIKE '%电影%' OR vod_content LIKE '%电影%' OR vod_name LIKE '%电影%') ORDER BY vod_hits DESC",
            "韩国.*爱情.*电视剧": "SELECT * FROM sakura_movdetail WHERE (type_name LIKE '%爱情%' OR vod_content LIKE '%爱情%' OR vod_name LIKE '%爱情%') AND vod_area LIKE '%韩国%' AND (type_name LIKE '%剧%' OR vod_content LIKE '%剧%' OR vod_name LIKE '%剧%') ORDER BY vod_hits DESC",
            
            # 中优先级：分类搜索（带年份、地区等限定条件，增强版）
            "2023.*动作.*": "SELECT * FROM sakura_movdetail WHERE (type_name LIKE '%动作%' OR vod_content LIKE '%动作%' OR vod_name LIKE '%动作%') AND vod_year LIKE '%2023%' ORDER BY vod_hits DESC",
            "2022.*动作.*": "SELECT * FROM sakura_movdetail WHERE (type_name LIKE '%动作%' OR vod_content LIKE '%动作%' OR vod_name LIKE '%动作%') AND vod_year LIKE '%2022%' ORDER BY vod_hits DESC",
            "2021.*动作.*": "SELECT * FROM sakura_movdetail WHERE (type_name LIKE '%动作%' OR vod_content LIKE '%动作%' OR vod_name LIKE '%动作%') AND vod_year LIKE '%2021%' ORDER BY vod_hits DESC",
            "2023.*喜剧.*": "SELECT * FROM sakura_movdetail WHERE (type_name LIKE '%喜剧%' OR vod_content LIKE '%喜剧%' OR vod_name LIKE '%喜剧%') AND vod_year LIKE '%2023%' ORDER BY vod_hits DESC",
            "2022.*喜剧.*": "SELECT * FROM sakura_movdetail WHERE (type_name LIKE '%喜剧%' OR vod_content LIKE '%喜剧%' OR vod_name LIKE '%喜剧%') AND vod_year LIKE '%2022%' ORDER BY vod_hits DESC",
            "中国.*爱情.*": "SELECT * FROM sakura_movdetail WHERE (type_name LIKE '%爱情%' OR vod_content LIKE '%爱情%' OR vod_name LIKE '%爱情%') AND vod_area LIKE '%中国%' ORDER BY vod_hits DESC",
            "美国.*科幻.*": "SELECT * FROM sakura_movdetail WHERE (type_name LIKE '%科幻%' OR vod_content LIKE '%科幻%' OR vod_name LIKE '%科幻%') AND vod_area LIKE '%美国%' ORDER BY vod_hits DESC",
            "韩国.*爱情.*": "SELECT * FROM sakura_movdetail WHERE (type_name LIKE '%爱情%' OR vod_content LIKE '%爱情%' OR vod_name LIKE '%爱情%') AND vod_area LIKE '%韩国%' ORDER BY vod_hits DESC",
            "日本.*动画.*": "SELECT * FROM sakura_movdetail WHERE (type_name LIKE '%动画%' OR vod_content LIKE '%动画%' OR vod_name LIKE '%动画%') AND vod_area LIKE '%日本%' ORDER BY vod_hits DESC",
            
            # 评分搜索（增强版）
            "9.*分.*电影": "SELECT * FROM sakura_movdetail WHERE CAST(vod_score AS FLOAT) >= 9.0 AND (type_name LIKE '%电影%' OR vod_content LIKE '%电影%' OR vod_name LIKE '%电影%') ORDER BY CAST(vod_score AS FLOAT) DESC",
            "8.*分.*电影": "SELECT * FROM sakura_movdetail WHERE CAST(vod_score AS FLOAT) >= 8.0 AND (type_name LIKE '%电影%' OR vod_content LIKE '%电影%' OR vod_name LIKE '%电影%') ORDER BY CAST(vod_score AS FLOAT) DESC",
            "高分.*电影": "SELECT * FROM sakura_movdetail WHERE CAST(vod_score AS FLOAT) > 8.0 AND (type_name LIKE '%电影%' OR vod_content LIKE '%电影%' OR vod_name LIKE '%电影%') ORDER BY CAST(vod_score AS FLOAT) DESC",
            "评分.*高": "SELECT * FROM sakura_movdetail WHERE CAST(vod_score AS FLOAT) > 7.5 ORDER BY CAST(vod_score AS FLOAT) DESC",
            
            # 年份搜索（增强版）
            "2023.*电影": "SELECT * FROM sakura_movdetail WHERE vod_year LIKE '%2023%' AND (type_name LIKE '%电影%' OR vod_content LIKE '%电影%' OR vod_name LIKE '%电影%') ORDER BY vod_time DESC",
            "2022.*电影": "SELECT * FROM sakura_movdetail WHERE vod_year LIKE '%2022%' AND (type_name LIKE '%电影%' OR vod_content LIKE '%电影%' OR vod_name LIKE '%电影%') ORDER BY vod_time DESC",
            "2021.*电影": "SELECT * FROM sakura_movdetail WHERE vod_year LIKE '%2021%' AND (type_name LIKE '%电影%' OR vod_content LIKE '%电影%' OR vod_name LIKE '%电影%') ORDER BY vod_time DESC",
            
            # 地区搜索（增强版）
            "中国.*电影": "SELECT * FROM sakura_movdetail WHERE vod_area LIKE '%中国%' AND (type_name LIKE '%电影%' OR vod_content LIKE '%电影%' OR vod_name LIKE '%电影%') ORDER BY vod_hits DESC",
            "美国.*电影": "SELECT * FROM sakura_movdetail WHERE vod_area LIKE '%美国%' AND (type_name LIKE '%电影%' OR vod_content LIKE '%电影%' OR vod_name LIKE '%电影%') ORDER BY vod_hits DESC",
            "韩国.*电视剧": "SELECT * FROM sakura_movdetail WHERE vod_area LIKE '%韩国%' AND (type_name LIKE '%剧%' OR vod_content LIKE '%剧%' OR vod_name LIKE '%剧%') ORDER BY vod_hits DESC",
            
            # 分类搜索（增强版：同时检查分类字段和内容/名称）
            "动作.*电影": "SELECT * FROM sakura_movdetail WHERE (type_name LIKE '%动作%' OR vod_content LIKE '%动作%' OR vod_name LIKE '%动作%') AND (type_name LIKE '%电影%' OR vod_content LIKE '%电影%' OR vod_name LIKE '%电影%') ORDER BY vod_hits DESC",
            "喜剧.*电影": "SELECT * FROM sakura_movdetail WHERE (type_name LIKE '%喜剧%' OR vod_content LIKE '%喜剧%' OR vod_name LIKE '%喜剧%') AND (type_name LIKE '%电影%' OR vod_content LIKE '%电影%' OR vod_name LIKE '%电影%') ORDER BY vod_hits DESC",
            "爱情.*电影": "SELECT * FROM sakura_movdetail WHERE (type_name LIKE '%爱情%' OR vod_content LIKE '%爱情%' OR vod_name LIKE '%爱情%') AND (type_name LIKE '%电影%' OR vod_content LIKE '%电影%' OR vod_name LIKE '%电影%') ORDER BY vod_hits DESC",
            "科幻.*电影": "SELECT * FROM sakura_movdetail WHERE (type_name LIKE '%科幻%' OR vod_content LIKE '%科幻%' OR vod_name LIKE '%科幻%') AND (type_name LIKE '%电影%' OR vod_content LIKE '%电影%' OR vod_name LIKE '%电影%') ORDER BY vod_hits DESC",
            "动作.*": "SELECT * FROM sakura_movdetail WHERE type_name LIKE '%动作%' OR vod_content LIKE '%动作%' OR vod_name LIKE '%动作%' ORDER BY vod_hits DESC",
            "喜剧.*": "SELECT * FROM sakura_movdetail WHERE type_name LIKE '%喜剧%' OR vod_content LIKE '%喜剧%' OR vod_name LIKE '%喜剧%' ORDER BY vod_hits DESC",
            "爱情.*": "SELECT * FROM sakura_movdetail WHERE type_name LIKE '%爱情%' OR vod_content LIKE '%爱情%' OR vod_name LIKE '%爱情%' ORDER BY vod_hits DESC",
            "科幻.*": "SELECT * FROM sakura_movdetail WHERE type_name LIKE '%科幻%' OR vod_content LIKE '%科幻%' OR vod_name LIKE '%科幻%' ORDER BY vod_hits DESC",
            
            # 热门搜索（增强版）
            "热门.*电影": "SELECT * FROM sakura_movdetail WHERE type_name LIKE '%电影%' OR vod_content LIKE '%电影%' OR vod_name LIKE '%电影%' ORDER BY vod_hits DESC LIMIT 20",
            "热门.*电视剧": "SELECT * FROM sakura_movdetail WHERE type_name LIKE '%剧%' OR vod_content LIKE '%剧%' OR vod_name LIKE '%剧%' ORDER BY vod_hits DESC LIMIT 20",
            "热门.*动漫": "SELECT * FROM sakura_movdetail WHERE type_name LIKE '%动漫%' OR type_name LIKE '%动画%' OR vod_content LIKE '%动漫%' OR vod_content LIKE '%动画%' OR vod_name LIKE '%动漫%' OR vod_name LIKE '%动画%' ORDER BY vod_hits DESC LIMIT 20",
            
            # 最新搜索（增强版）
            "最新.*电影": "SELECT * FROM sakura_movdetail WHERE type_name LIKE '%电影%' OR vod_content LIKE '%电影%' OR vod_name LIKE '%电影%' ORDER BY vod_time DESC LIMIT 20",
            "最新.*电视剧": "SELECT * FROM sakura_movdetail WHERE type_name LIKE '%剧%' OR vod_content LIKE '%剧%' OR vod_name LIKE '%剧%' ORDER BY vod_time DESC LIMIT 20",
            
            # 演员搜索（增强版）
            "成龙.*电影": "SELECT * FROM sakura_movdetail WHERE vod_actor LIKE '%成龙%' AND (type_name LIKE '%电影%' OR vod_content LIKE '%电影%' OR vod_name LIKE '%电影%') ORDER BY vod_hits DESC",
            "周星驰.*电影": "SELECT * FROM sakura_movdetail WHERE vod_actor LIKE '%周星驰%' AND (type_name LIKE '%电影%' OR vod_content LIKE '%电影%' OR vod_name LIKE '%电影%') ORDER BY vod_hits DESC",
            
            # 推荐搜索
            "推荐.*视频": "SELECT * FROM sakura_movdetail ORDER BY vod_hits DESC, CAST(vod_score AS FLOAT) DESC LIMIT 15",
            
            # 通用搜索模式
            "搜索.*视频": "SELECT * FROM sakura_movdetail WHERE vod_name LIKE '%{keyword}%' ORDER BY vod_hits DESC",
            "查找.*电影": "SELECT * FROM sakura_movdetail WHERE vod_name LIKE '%{keyword}%' AND type_name LIKE '%电影%' ORDER BY vod_hits DESC",
            "找.*电视剧": "SELECT * FROM sakura_movdetail WHERE vod_name LIKE '%{keyword}%' AND type_name LIKE '%剧%' ORDER BY vod_hits DESC"
        }
        
        # 提取关键词
        keyword = self._extract_keyword(question)
        
        # 按优先级顺序匹配模式
        for pattern, sql_template in question_patterns.items():
            if self._match_pattern(question, pattern):
                print(f"✅ 匹配模式: {pattern}")
                sql = sql_template.format(keyword=keyword) if '{keyword}' in sql_template else sql_template
                return sql
        
        # 默认搜索：在视频名称中搜索，按点击量排序
        return f"SELECT * FROM sakura_movdetail WHERE vod_name LIKE '%{keyword}%' ORDER BY vod_hits DESC"
    
    def _extract_keyword(self, question: str) -> str:
        """从问题中提取关键词"""
        # 更精确的关键词提取逻辑
        
        # 定义需要移除的常见搜索词
        stop_words = ["搜索", "查找", "找", "的", "电影", "视频", "电视剧", "片", "作品", "推荐", "热门", "高分", "最新", "什么", "哪些", "有没有"]
        
        # 定义需要保留的关键词（如演员、导演名称）
        preserve_words = ["成龙", "周星驰", "张艺谋", "冯小刚", "吴京", "沈腾", "徐峥", "刘德华", "周润发"]
        
        # 如果问题包含保留关键词，直接返回
        for preserve_word in preserve_words:
            if preserve_word in question:
                return preserve_word
        
        # 移除常见搜索词
        keyword = question
        for word in stop_words:
            keyword = keyword.replace(word, "")
        
        # 清理多余空格和标点
        keyword = keyword.strip().replace("，", "").replace("。", "").replace("？", "")
        
        # 如果关键词为空，返回原问题
        return keyword if keyword else question
    
    def _match_pattern(self, question: str, pattern: str) -> bool:
        """检查问题是否匹配模式"""
        try:
            # 使用正则表达式进行模式匹配
            import re
            
            # 增强匹配逻辑：对于包含特定关键词的模式，要求关键词必须存在
            if "成龙" in pattern and "成龙" not in question:
                return False
            if "周星驰" in pattern and "周星驰" not in question:
                return False
            if "张艺谋" in pattern and "张艺谋" not in question:
                return False
            if "冯小刚" in pattern and "冯小刚" not in question:
                return False
            
            # 对于年份模式，检查是否包含年份数字
            if "2023" in pattern and "2023" not in question:
                return False
            if "2022" in pattern and "2022" not in question:
                return False
            if "2021" in pattern and "2021" not in question:
                return False
            
            # 对于评分模式，检查是否包含评分相关词汇
            if "分" in pattern and "分" not in question and "评分" not in question:
                return False
            
            return bool(re.search(pattern, question))
        except:
            return False


class SQLExecutor:
    """SQL执行器"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def execute_sql(self, sql: str) -> List[Dict[str, Any]]:
        """执行SQL查询并返回结果"""
        try:
            # 执行SQL查询
            result = self.db.execute(text(sql))
            rows = result.fetchall()
            
            # 转换为字典列表
            columns = result.keys()
            results = []
            for row in rows:
                row_dict = {column: value for column, value in zip(columns, row)}
                results.append(row_dict)
            
            return results
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"SQL执行错误: {str(e)}")
    
    def validate_sql(self, sql: str) -> bool:
        """验证SQL语句的安全性"""
        # 禁止的危险操作
        dangerous_keywords = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE', 'TRUNCATE']
        
        sql_upper = sql.upper()
        for keyword in dangerous_keywords:
            if keyword in sql_upper:
                return False
        
        return True


@router.post("/smart-search", response_model=Dict[str, Any])
async def smart_search(
    request_data: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db)
):
    """智能搜索API端点"""
    question = request_data.get("question", "").strip()
    
    # 调试：打印接收到的原始数据
    print(f"调试: 接收到的原始请求数据: {request_data}")
    print(f"调试: 接收到的question字段: {repr(question)}")
    
    if not question:
        raise HTTPException(status_code=400, detail="问题不能为空")
    
    # 检查中文编码问题
    if '?' in question and len(question) == 4:
        # 如果是乱码，尝试从请求体中重新获取
        import json
        from fastapi.encoders import jsonable_encoder
        print(f"调试: 检测到可能的乱码，尝试重新编码")
        
        # 尝试使用UTF-8编码
        try:
            question_bytes = question.encode('latin1').decode('utf-8')
            print(f"调试: 重新编码后的question: {repr(question_bytes)}")
            question = question_bytes
        except:
            pass
    
    print(f"调试: 最终处理的question: {repr(question)}")
    
    # 初始化SQL生成器和执行器
    sql_generator = SQLGenerator()
    sql_executor = SQLExecutor(db)
    
    # 生成SQL
    generated_sql = sql_generator.generate_sql(question)
    
    # 验证SQL安全性
    if not sql_executor.validate_sql(generated_sql):
        raise HTTPException(status_code=400, detail="SQL语句不安全")
    
    # 执行SQL
    results = sql_executor.execute_sql(generated_sql)
    
    # 格式化结果
    formatted_results = []
    for result in results:
        # 确保结果包含必要字段
        video_data = {
            "vod_id": result.get("vod_id"),
            "vod_name": result.get("vod_name", "未知名称"),
            "vod_pic": result.get("vod_pic"),
            "vod_score": result.get("vod_score", "0.0"),
            "vod_hits": result.get("vod_hits", 0),
            "vod_area": result.get("vod_area", ""),
            "vod_year": result.get("vod_year", ""),
            "vod_actor": result.get("vod_actor", ""),
            "vod_director": result.get("vod_director", ""),
            "vod_content": result.get("vod_content", "")
        }
        formatted_results.append(video_data)
    
    return {
        "code": 200,
        "message": "智能搜索成功",
        "data": {
            "question": question,
            "generated_sql": generated_sql,
            "total": len(formatted_results),
            "results": formatted_results
        }
    }


@router.get("/smart-search/examples")
def get_search_examples():
    """
    获取智能搜索示例
    """
    examples = [
        {
            "question": "搜索动作电影",
            "description": "搜索所有动作类型的电影"
        },
        {
            "question": "查找2023年上映的高分电影",
            "description": "查找2023年上映且评分较高的电影"
        },
        {
            "question": "找周星驰的喜剧片",
            "description": "搜索周星驰主演的喜剧电影"
        },
        {
            "question": "热门美国电视剧",
            "description": "查找热门的美国电视剧"
        },
        {
            "question": "张艺谋导演的最新作品",
            "description": "搜索张艺谋导演的最新电影"
        },
        {
            "question": "评分9分以上的科幻电影",
            "description": "查找评分9分以上的科幻电影"
        }
    ]
    
    return {
        "code": 200,
        "message": "获取搜索示例成功",
        "data": examples
    }


@router.post("/qianwen-search", response_model=Dict[str, Any])
async def qianwen_search(
    request_data: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db)
):
    """
    使用阿里云千问API的智能搜索
    """
    question = request_data.get("question", "").strip()
    
    if not question:
        raise HTTPException(status_code=400, detail="问题不能为空")
    
    print(f"千问搜索: 接收到的问题: {repr(question)}")
    
    try:
        # 获取千问服务实例
        qianwen_service = get_qianwen_service()
        
        # 获取数据库表结构
        sql_generator = SQLGenerator()
        table_schema = sql_generator._get_database_schema()
        
        # 使用千问API生成SQL
        generated_sql = await qianwen_service.generate_sql_from_question(question, table_schema)
        
        # 如果千问API调用失败，回退到本地智能搜索
        if not generated_sql:
            print("千问API调用失败，回退到本地智能搜索")
            generated_sql = sql_generator.generate_sql(question)
        
        print(f"生成的SQL: {generated_sql}")
        
        # 验证SQL安全性
        sql_executor = SQLExecutor(db)
        if not sql_executor.validate_sql(generated_sql):
            raise HTTPException(status_code=400, detail="SQL语句不安全")
        
        # 执行SQL
        results = sql_executor.execute_sql(generated_sql)
        
        # 格式化结果
        formatted_results = []
        for result in results:
            video_data = {
                "vod_id": result.get("vod_id"),
                "vod_name": result.get("vod_name", "未知名称"),
                "vod_pic": result.get("vod_pic"),
                "vod_score": result.get("vod_score", "0.0"),
                "vod_hits": result.get("vod_hits", 0),
                "vod_area": result.get("vod_area", ""),
                "vod_year": result.get("vod_year", ""),
                "vod_actor": result.get("vod_actor", ""),
                "vod_director": result.get("vod_director", ""),
                "vod_content": result.get("vod_content", "")
            }
            formatted_results.append(video_data)
        
        return {
            "code": 200,
            "message": "千问智能搜索成功",
            "data": {
                "question": question,
                "generated_sql": generated_sql,
                "total": len(formatted_results),
                "results": formatted_results,
                "ai_engine": "阿里云千问"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"千问搜索异常: {str(e)}")
        # 异常时回退到本地智能搜索
        sql_generator = SQLGenerator()
        sql_executor = SQLExecutor(db)
        
        generated_sql = sql_generator.generate_sql(question)
        results = sql_executor.execute_sql(generated_sql)
        
        formatted_results = []
        for result in results:
            video_data = {
                "vod_id": result.get("vod_id"),
                "vod_name": result.get("vod_name", "未知名称"),
                "vod_pic": result.get("vod_pic"),
                "vod_score": result.get("vod_score", "0.0"),
                "vod_hits": result.get("vod_hits", 0),
                "vod_area": result.get("vod_area", ""),
                "vod_year": result.get("vod_year", ""),
                "vod_actor": result.get("vod_actor", ""),
                "vod_director": result.get("vod_director", ""),
                "vod_content": result.get("vod_content", "")
            }
            formatted_results.append(video_data)
        
        return {
            "code": 200,
            "message": "本地智能搜索成功（千问API异常）",
            "data": {
                "question": question,
                "generated_sql": generated_sql,
                "total": len(formatted_results),
                "results": formatted_results,
                "ai_engine": "本地智能搜索"
            }
        }


@router.get("/qianwen-search/health")
async def check_qianwen_health():
    """
    检查千问API健康状态
    """
    try:
        qianwen_service = get_qianwen_service()
        
        # 简单的健康检查 - 尝试分析一个简单问题
        intent_result = await qianwen_service.analyze_search_intent("测试健康检查")
        
        return {
            "code": 200,
            "message": "千问API健康检查通过",
            "data": {
                "status": "healthy",
                "intent_analysis": intent_result
            }
        }
    except Exception as e:
        return {
            "code": 500,
            "message": "千问API健康检查失败",
            "data": {
                "status": "unhealthy",
                "error": str(e)
            }
        }