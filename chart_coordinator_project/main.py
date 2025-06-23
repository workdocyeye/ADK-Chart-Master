#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chart Coordinator - Google ADK Standard FastAPI Deployment
符合Google ADK官方标准的FastAPI部署文件

为Google ADK Hackathon设计的生产级部署配置
使用Google ADK官方推荐的get_fast_api_app方法
"""

import os
import uvicorn
from fastapi import FastAPI
from google.adk.cli.fast_api import get_fast_api_app

# 获取当前目录作为Agent目录
AGENT_DIR = os.path.dirname(os.path.abspath(__file__))

# ADK FastAPI配置
SESSION_DB_URL = "sqlite:///./adk_sessions.db"  # 会话数据库
ALLOWED_ORIGINS = ["*"]  # CORS设置，生产环境建议限制具体域名
SERVE_WEB_INTERFACE = True  # 启用Web UI界面

# 使用Google ADK官方方法创建FastAPI应用
app: FastAPI = get_fast_api_app(
    agents_dir=AGENT_DIR,
    session_db_url=SESSION_DB_URL,
    allow_origins=ALLOWED_ORIGINS,
    web=SERVE_WEB_INTERFACE,
)

# 可以添加自定义路由
@app.get("/hackathon-info")
async def hackathon_info():
    """Hackathon项目信息接口"""
    return {
        "project": "Chart Coordinator",
        "hackathon": "Google ADK Hackathon",
        "description": "AI驱动的智能图表生成系统",
        "framework": "Google ADK",
        "agents": 5,
        "tools": 17,
        "features": [
            "流程架构图表 (Mermaid, PlantUML, Graphviz)",
            "数据可视化 (ECharts, Matplotlib, Plotly)",
            "交互动态图表 (Three.js, Canvas)",
            "思维概念图 (思维导图, 知识图谱)",
            "文档业务图表"
        ]
    }

if __name__ == "__main__":
    # 使用Render的PORT环境变量，默认8080
    port = int(os.environ.get("PORT", 8080))
    
    print("🚀 启动Chart Coordinator - Google ADK Hackathon项目")
    print(f"🌐 服务端口: {port}")
    print(f"🎯 Web界面: http://localhost:{port}")
    print(f"📡 API文档: http://localhost:{port}/docs")
    
    # 启动uvicorn服务器
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=port,
        log_level="info"
    ) 