#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chart Coordinator - Google ADK Standard FastAPI Deployment
符合Google ADK官方标准的FastAPI部署文件

为Google ADK Hackathon设计的生产级部署配置
从项目根目录启动，模拟 'adk web' 行为
"""

import os
import sys
from pathlib import Path
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, HTMLResponse
import json
import asyncio

# 智能环境变量加载策略
def load_environment():
    """智能加载环境变量，支持多种部署场景"""
    env_loaded = False
    
    # 策略1: 优先在项目根目录查找.env
    root_env = Path(".env")
    if root_env.exists():
        print(f"✅ 加载根目录.env文件: {root_env.absolute()}")
        from dotenv import load_dotenv
        load_dotenv(root_env)
        env_loaded = True
    
    # 策略2: 备用在chart_coordinator_project子目录查找.env
    if not env_loaded:
        sub_env = Path("chart_coordinator_project/.env")
        if sub_env.exists():
            print(f"✅ 加载子目录.env文件: {sub_env.absolute()}")
            from dotenv import load_dotenv
            load_dotenv(sub_env)
            env_loaded = True
    
    # 策略3: 使用Render环境变量（生产环境）
    if not env_loaded:
        print("📡 使用Render平台环境变量")
    
    # 验证关键环境变量
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if api_key:
        print(f"✅ 检测到DEEPSEEK_API_KEY: {api_key[:10]}...")
    else:
        print("⚠️  警告: 未检测到DEEPSEEK_API_KEY，可能导致SSE连接失败")
    
    return env_loaded

# 加载环境变量
load_environment()

# 添加chart_coordinator_project到Python路径
chart_coordinator_path = os.path.join(os.getcwd(), 'chart_coordinator_project')
if os.path.exists(chart_coordinator_path):
    sys.path.insert(0, chart_coordinator_path)
    print(f"添加路径到sys.path: {chart_coordinator_path}")

print(f"当前sys.path前3项: {sys.path[:3]}")

print("🚀 启动Chart Coordinator服务...")
print(f"📁 当前工作目录: {os.getcwd()}")
print(f"🌍 环境变量PORT: {os.environ.get('PORT', '未设置')}")

# ADK应用发现：从当前目录扫描包含agent.py的子目录
# 这完全模拟了本地 'adk web' 的行为
AGENT_DIR = "."  # 当前目录，让ADK扫描子目录
print(f"📁 ADK agents_dir: {AGENT_DIR}")

# 验证chart_coordinator_project应用目录存在
app_dir = os.path.join(AGENT_DIR, 'chart_coordinator_project')
if os.path.exists(app_dir):
    print(f"✅ 找到应用目录: {app_dir}")
    agent_file = os.path.join(app_dir, 'agent.py')
    if os.path.exists(agent_file):
        print(f"✅ 找到agent.py: {agent_file}")
    else:
        print(f"❌ 未找到agent.py: {agent_file}")
else:
    print(f"❌ 未找到应用目录: {app_dir}")

# 初始化app变量
app = None

# 尝试使用Google ADK创建应用
try:
    print("🔄 尝试创建Google ADK FastAPI应用...")
    print(f"🎯 完全模拟本地 'adk web' 行为")
    from google.adk.cli.fast_api import get_fast_api_app
    
    app = get_fast_api_app(
        agents_dir=AGENT_DIR,  # 当前目录，ADK会发现chart_coordinator_project
        web=True,  # 启用Web UI界面
    )
    print("✅ Google ADK FastAPI应用创建成功")
    print("🎉 应该能在左上角看到 'chart_coordinator_project' 应用了！")
    
except Exception as e:
    print(f"❌ ADK FastAPI创建失败: {e}")
    print(f"🔍 尝试的agents_dir: {AGENT_DIR}")
    print("🔄 回退到基础FastAPI应用...")
    
    # 备用方案：创建基础FastAPI应用
    app = FastAPI(
        title="Chart Coordinator", 
        description="AI驱动的智能图表生成系统",
        version="1.0.0"
    )
    
    @app.get("/")
    async def root():
        return {
            "message": "Chart Coordinator正在运行", 
            "status": "ok",
            "mode": "fallback",
            "note": "Google ADK未能正常启动，运行在基础模式"
        }

# 确保app不为None
if app is None:
    print("❌ 创建FastAPI应用失败，使用最小配置")
    app = FastAPI()

# 添加健康检查端点（重要：Render需要这个）
@app.get("/health")
async def health_check():
    """Render健康检查端点 - 必须返回200状态码"""
    return {
        "status": "healthy",
        "service": "Chart Coordinator",
        "framework": "Google ADK",
        "message": "服务运行正常",
        "working_dir": os.getcwd(),
        "agents_dir": AGENT_DIR,
        "port": os.environ.get("PORT", "10000"),
        "deepseek_api_configured": bool(os.environ.get("DEEPSEEK_API_KEY"))
    }

@app.get("/debug/sse-test-page")
async def sse_test_page():
    """SSE测试页面"""
    from fastapi.responses import HTMLResponse
    
    # 读取HTML文件内容
    try:
        with open("sse_test.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    except FileNotFoundError:
        return HTMLResponse(content="""
        <!DOCTYPE html>
        <html>
        <head><title>SSE测试页面未找到</title></head>
        <body>
            <h1>❌ SSE测试页面未找到</h1>
            <p>请确保 sse_test.html 文件存在于项目根目录。</p>
            <p><a href="/debug/sse-test">直接测试SSE端点</a></p>
            <p><a href="/">返回主页</a></p>
        </body>
        </html>
        """)

@app.get("/debug/env")
async def debug_env():
    """环境变量调试接口"""
    return {
        "working_dir": os.getcwd(),
        "python_path": sys.path[:5],
        "environment_vars": {
            "PORT": os.environ.get("PORT"),
            "DEEPSEEK_API_KEY": "配置" if os.environ.get("DEEPSEEK_API_KEY") else "未配置",
            "GOOGLE_API_KEY": "配置" if os.environ.get("GOOGLE_API_KEY") else "未配置",
            "OPENAI_API_KEY": "配置" if os.environ.get("OPENAI_API_KEY") else "未配置",
        },
        "chart_coordinator_path": chart_coordinator_path,
        "chart_coordinator_exists": os.path.exists(chart_coordinator_path)
    }

# 根据Google ADK文档添加SSE修复
@app.get("/debug/sse-test")
async def sse_test():
    """SSE连接测试端点 - 用于诊断SSE问题"""
    
    async def event_generator():
        """SSE事件生成器"""
        try:
            # 发送连接建立消息
            yield f"data: {json.dumps({'type': 'connection', 'message': 'SSE连接已建立'})}\n\n"
            
            # 每秒发送一次心跳
            for i in range(10):
                await asyncio.sleep(1)
                yield f"data: {json.dumps({'type': 'heartbeat', 'count': i+1, 'timestamp': f'{i+1}秒'})}\n\n"
            
            # 发送完成消息
            yield f"data: {json.dumps({'type': 'complete', 'message': 'SSE测试完成'})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': f'SSE错误: {str(e)}'})}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-transform",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Cache-Control",
            "Content-Encoding": "identity",  # 关键：防止压缩缓冲
            "X-Accel-Buffering": "no",  # 禁用Nginx缓冲
        }
    )

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

def main():
    """主启动函数"""
    # 获取端口配置
    port = int(os.environ.get("PORT", 10000))
    
    print("=" * 50)
    print("🚀 Chart Coordinator - Google ADK Hackathon项目")
    print("=" * 50)
    print(f"🌐 服务端口: {port}")
    print(f"🎯 Web界面: http://0.0.0.0:{port}")
    print(f"📡 API文档: http://0.0.0.0:{port}/docs")
    print(f"❤️ 健康检查: http://0.0.0.0:{port}/health")
    print(f"🔧 调试接口: http://0.0.0.0:{port}/debug/env")
    print(f"🔍 SSE测试: http://0.0.0.0:{port}/debug/sse-test")
    print("🔗 Render要求绑定到0.0.0.0以接收HTTP请求")
    print("📱 应该能看到 chart_coordinator_project 应用选择器")
    print("=" * 50)
    
    # 启动服务器
    try:
        uvicorn.run(
            app, 
            host="0.0.0.0",  # Render要求
            port=port,
            log_level="info",
            access_log=True,
            # 优化SSE连接配置
            timeout_keep_alive=60,  # 保持连接60秒
            timeout_graceful_shutdown=15,  # 优雅关闭时间
            limit_concurrency=1000,  # 并发连接限制
            limit_max_requests=10000,  # 最大请求数
        )
    except Exception as e:
        print(f"❌ 服务器启动失败: {e}")
        raise

if __name__ == "__main__":
    main() 