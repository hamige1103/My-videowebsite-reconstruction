#!/usr/bin/env python3
"""
FastAPI Sakura Comic Backend
基于FastAPI框架重构的视频网站后端，采用异步策略
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.database import create_tables
from app.api.api_v1.router import api_router

# 创建FastAPI应用实例
app = FastAPI(
    title="Sakura Comic API",
    description="基于FastAPI重构的樱花动漫视频网站后端API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    # 确保正确处理中文编码
    openapi_tags=[
        {
            "name": "智能搜索",
            "description": "自然语言智能搜索功能"
        }
    ]
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory="static"), name="static")

# 包含API路由
app.include_router(api_router, prefix="/api")

@app.on_event("startup")
def startup_event():
    """应用启动时执行"""
    create_tables()
    print("FastAPI Sakura Comic Backend 启动成功!")

@app.get("/")
async def root():
    """根路径，用于健康检查"""
    return {
        "message": "欢迎使用Sakura Comic FastAPI后端服务",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )