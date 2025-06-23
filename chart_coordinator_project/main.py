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

# Google ADK应用目录 - 指向chart_coordinator_project
# 从项目根目录运行时，agents_dir应该是chart_coordinator_project
AGENT_DIR = "chart_coordinator_project"

print(f"📁 当前工作目录: {os.getcwd()}")
print(f"📁 ADK应用目录: {AGENT_DIR}")

# 验证应用目录存在
if os.path.exists(AGENT_DIR):
    print(f"✅ 找到应用目录: {AGENT_DIR}")
    agent_file = os.path.join(AGENT_DIR, 'agent.py')
    if os.path.exists(agent_file):
        print(f"✅ 找到agent.py: {agent_file}")
    else:
        print(f"❌ 未找到agent.py: {agent_file}")
else:
    print(f"❌ 未找到应用目录: {AGENT_DIR}")

# 使用Google ADK官方方法创建FastAPI应用
try:
    app: FastAPI = get_fast_api_app(
        agents_dir=AGENT_DIR,
        web=True,  # 启用Web UI界面
    )
    print("✅ Google ADK FastAPI应用创建成功")
except Exception as e:
    print(f"❌ ADK FastAPI创建失败: {e}")
    print(f"🔍 尝试的agents_dir: {AGENT_DIR}")
    # 备用方案：直接创建FastAPI应用
    from fastapi import FastAPI
    app = FastAPI(title="Chart Coordinator", description="AI驱动的智能图表生成系统")
    
    @app.get("/")
    async def root():
        return {"message": "Chart Coordinator正在运行", "status": "ok"}

# 添加自定义路由
@app.get("/health")
async def health_check():
    """Render健康检查端点"""
    return {
        "status": "healthy",
        "service": "Chart Coordinator",
        "framework": "Google ADK",
        "message": "服务运行正常",
        "working_dir": os.getcwd(),
        "agents_dir": AGENT_DIR
    }

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
    # 根据Render文档，默认PORT是10000
    port = int(os.environ.get("PORT", 10000))
    
    print("🚀 启动Chart Coordinator - Google ADK Hackathon项目")
    print(f"🌐 服务端口: {port}")
    print(f"🎯 Web界面: http://0.0.0.0:{port}")
    print(f"📡 API文档: http://0.0.0.0:{port}/docs")
    print("🔗 Render要求绑定到0.0.0.0以接收HTTP请求")
    
    # 根据Render文档，必须绑定到0.0.0.0
    uvicorn.run(
        app, 
        host="0.0.0.0",  # Render要求
        port=port,
        log_level="info"
    ) 