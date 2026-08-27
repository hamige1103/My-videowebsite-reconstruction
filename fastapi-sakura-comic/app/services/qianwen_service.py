"""
阿里云千问API服务
"""
import json
import time
import hashlib
import hmac
import base64
from typing import Dict, Any, Optional
import httpx
from fastapi import HTTPException


class QianWenService:
    """阿里云千问API服务类"""
    
    def __init__(self, access_key_id: str, access_key_secret: str):
        self.access_key_id = access_key_id
        self.access_key_secret = access_key_secret
        self.base_url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
        
    def _generate_signature(self, timestamp: str) -> str:
        """生成签名"""
        # 构建签名字符串
        string_to_sign = f"{timestamp}\n{self.access_key_id}\n"
        
        # 使用HMAC-SHA256算法生成签名
        signature = hmac.new(
            self.access_key_secret.encode('utf-8'),
            string_to_sign.encode('utf-8'),
            hashlib.sha256
        ).digest()
        
        # Base64编码
        signature_base64 = base64.b64encode(signature).decode('utf-8')
        return signature_base64
    
    def _build_headers(self) -> Dict[str, str]:
        """构建请求头"""
        timestamp = str(int(time.time() * 1000))
        signature = self._generate_signature(timestamp)
        
        return {
            "Authorization": f"Bearer {self.access_key_id}:{signature}",
            "X-DashScope-Timestamp": timestamp,
            "Content-Type": "application/json"
        }
    
    async def generate_sql_from_question(self, question: str, table_schema: str) -> Optional[str]:
        """
        使用千问API根据问题生成SQL查询语句
        
        Args:
            question: 用户的问题
            table_schema: 数据库表结构描述
            
        Returns:
            SQL查询语句或None
        """
        # 构建提示词
        prompt = f"""
你是一个专业的SQL生成助手。请根据用户的问题和数据库表结构，生成合适的SQL查询语句。

数据库表结构：
{table_schema}

用户问题：{question}

要求：
1. 只生成SELECT查询语句
2. 不要包含DROP、DELETE、UPDATE、INSERT等危险操作
3. 使用LIKE进行模糊匹配
4. 按相关度排序
5. 返回格式：只返回SQL语句，不要有其他内容

请生成SQL查询语句：
"""
        
        # 构建请求体
        request_data = {
            "model": "qwen-turbo",
            "input": {
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            },
            "parameters": {
                "result_format": "message",
                "max_tokens": 1000,
                "temperature": 0.1
            }
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                headers = self._build_headers()
                response = await client.post(self.base_url, json=request_data, headers=headers)
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # 解析响应
                    if "output" in result and "choices" in result["output"]:
                        choice = result["output"]["choices"][0]
                        if "message" in choice and "content" in choice["message"]:
                            sql_content = choice["message"]["content"].strip()
                            
                            # 清理SQL语句，只保留SELECT语句
                            if sql_content.startswith("SELECT") or sql_content.startswith("select"):
                                # 移除可能的代码块标记
                                sql_content = sql_content.replace("```sql", "").replace("```", "").strip()
                                return sql_content
                            
                            # 如果返回内容包含SQL，尝试提取
                            if "SELECT" in sql_content.upper():
                                # 提取SQL语句
                                import re
                                sql_match = re.search(r'(SELECT.*?)(?:$|;|`|\n\n)', sql_content, re.IGNORECASE | re.DOTALL)
                                if sql_match:
                                    return sql_match.group(1).strip()
                
                # 如果API调用失败，返回None
                print(f"千问API调用失败: {response.status_code}, {response.text}")
                return None
                
        except Exception as e:
            print(f"千问API调用异常: {str(e)}")
            return None
    
    async def analyze_search_intent(self, question: str) -> Dict[str, Any]:
        """
        分析用户搜索意图
        
        Args:
            question: 用户的问题
            
        Returns:
            意图分析结果
        """
        prompt = f"""
请分析用户的搜索意图，并返回JSON格式的分析结果。

用户问题：{question}

分析要求：
1. 识别搜索类型：电影、电视剧、演员、导演、类型、年份、评分等
2. 提取关键词
3. 判断搜索的精确度（精确搜索/模糊搜索）
4. 分析可能的排序需求

返回格式：
{{
    "search_type": "电影/电视剧/演员/导演/类型/年份/评分/综合",
    "keywords": ["关键词1", "关键词2", ...],
    "precision": "exact/fuzzy",
    "sort_by": "score/hits/year/none",
    "year_filter": "2023/2022/.../none",
    "score_filter": "9.0/8.0/.../none"
}}

请返回JSON格式的分析结果：
"""
        
        request_data = {
            "model": "qwen-turbo",
            "input": {
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            },
            "parameters": {
                "result_format": "message",
                "max_tokens": 500,
                "temperature": 0.1
            }
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                headers = self._build_headers()
                response = await client.post(self.base_url, json=request_data, headers=headers)
                
                if response.status_code == 200:
                    result = response.json()
                    
                    if "output" in result and "choices" in result["output"]:
                        choice = result["output"]["choices"][0]
                        if "message" in choice and "content" in choice["message"]:
                            content = choice["message"]["content"].strip()
                            
                            # 尝试解析JSON
                            try:
                                import re
                                # 提取JSON部分
                                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                                if json_match:
                                    intent_data = json.loads(json_match.group())
                                    return intent_data
                            except:
                                pass
                
                # 如果解析失败，返回默认分析
                return {
                    "search_type": "综合",
                    "keywords": [question],
                    "precision": "fuzzy",
                    "sort_by": "none",
                    "year_filter": "none",
                    "score_filter": "none"
                }
                
        except Exception as e:
            print(f"千问意图分析异常: {str(e)}")
            return {
                "search_type": "综合",
                "keywords": [question],
                "precision": "fuzzy",
                "sort_by": "none",
                "year_filter": "none",
                "score_filter": "none"
            }


# 全局服务实例
_qianwen_service = None


def get_qianwen_service() -> QianWenService:
    """获取千问服务实例"""
    global _qianwen_service
    
    if _qianwen_service is None:
        # 从环境变量获取配置
        import os
        access_key_id = os.getenv("ALIYUN_ACCESS_KEY_ID")
        access_key_secret = os.getenv("ALIYUN_ACCESS_KEY_SECRET")
        
        if not access_key_id or not access_key_secret:
            raise HTTPException(
                status_code=500, 
                detail="阿里云API密钥未配置，请设置ALIYUN_ACCESS_KEY_ID和ALIYUN_ACCESS_KEY_SECRET环境变量"
            )
        
        _qianwen_service = QianWenService(access_key_id, access_key_secret)
    
    return _qianwen_service