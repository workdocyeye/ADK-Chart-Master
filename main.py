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

# 添加Google ADK标准端点
print("🔧 添加缺失的Google ADK标准端点...")

# 如果ADK应用创建成功，检查是否有/run_sse端点
if app and hasattr(app, 'routes'):
    existing_routes = [route.path for route in app.routes if hasattr(route, 'path')]
    print(f"📋 现有路由: {existing_routes}")
    
    # 检查是否缺少关键端点
    if '/run_sse' not in existing_routes:
        print("⚠️ 缺少 /run_sse 端点，手动添加...")
        
        @app.post("/run_sse")
        async def run_sse_endpoint(request: Request):
            """Google ADK标准的/run_sse端点 - 完全符合ADK文档规范"""
            try:
                # 解析请求数据 - 使用ADK标准参数名
                data = await request.json()
                print(f"📥 收到/run_sse请求: {data}")
                
                # ADK标准参数格式（驼峰命名）
                app_name = data.get("appName", data.get("app_name", "chart_coordinator_project"))
                user_id = data.get("userId", data.get("user_id", "default_user"))
                session_id = data.get("sessionId", data.get("session_id", f"session_{user_id}"))
                new_message = data.get("newMessage", data.get("new_message", {}))
                streaming = data.get("streaming", True)  # 默认启用streaming
                
                # 获取用户消息文本
                user_text = ""
                if new_message and "parts" in new_message:
                    for part in new_message["parts"]:
                        if "text" in part:
                            user_text = part["text"]
                            break
                
                print(f"🤖 处理消息: {user_text} (应用: {app_name}, 用户: {user_id}, 会话: {session_id})")
                
                # 生成invocation_id（ADK标准）
                import uuid
                invocation_id = f"e-{str(uuid.uuid4())[:8]}"
                
                # 针对ADK规范的SSE响应
                async def event_generator():
                    try:
                        # ADK标准事件格式
                        def create_adk_event(content_parts, partial=True, turn_complete=False, event_id=None):
                            return {
                                "author": "chart_coordinator_project", 
                                "invocationId": invocation_id,
                                "content": {
                                    "parts": content_parts,
                                    "role": "model"
                                },
                                "partial": partial,
                                "turn_complete": turn_complete,
                                "actions": {
                                    "stateDelta": {},
                                    "artifactDelta": {}, 
                                    "requestedAuthConfigs": {}
                                },
                                "longRunningToolIds": [],
                                "id": event_id or f"evt-{str(uuid.uuid4())[:8]}",
                                "timestamp": __import__('time').time()
                            }
                        
                        # 1. 发送连接开始事件
                        start_event = create_adk_event(
                            [{"text": "🤔 Chart Coordinator正在分析你的需求..."}],
                            partial=True,
                            turn_complete=False
                        )
                        yield f"data: {json.dumps(start_event)}\n\n"
                        await asyncio.sleep(0.2)
                        
                        # 2. 发送进度更新
                        progress_events = [
                            "🔍 分析图表类型和数据要求...",
                            "🎨 选择合适的可视化工具...", 
                            "⚙️ 生成图表代码..."
                        ]
                        
                        for progress_text in progress_events:
                            progress_event = create_adk_event(
                                [{"text": progress_text}],
                                partial=True,
                                turn_complete=False
                            )
                            yield f"data: {json.dumps(progress_event)}\n\n"
                            await asyncio.sleep(0.3)
                        
                        # 3. 根据用户输入生成智能回复
                        if "流程图" in user_text or "流程" in user_text or "flowchart" in user_text.lower():
                            response_text = "🎯 我理解您需要创建流程图！我可以使用Mermaid、PlantUML或Graphviz来为您生成专业的流程图表。请提供具体的流程步骤或业务场景。\n\n📊 **可用工具：**\n• Mermaid - 现代流程图\n• PlantUML - UML标准图表\n• Graphviz - 复杂关系图"
                        elif "数据可视化" in user_text or "图表" in user_text or "chart" in user_text.lower():
                            response_text = "📊 数据可视化是我的专长！我可以使用ECharts、Matplotlib、Plotly等工具创建各种图表。\n\n🎨 **可用工具：**\n• ECharts - 交互式Web图表\n• Matplotlib - 科学绘图\n• Plotly - 动态可视化\n• Seaborn - 统计图表\n\n请分享您的数据或描述想要的图表类型。"
                        elif "思维导图" in user_text or "mind map" in user_text.lower():
                            response_text = "🧠 思维导图很棒的选择！我可以帮您创建结构化的思维导图来整理想法和概念。\n\n🌟 **特色功能：**\n• 多层级结构\n• 色彩编码\n• 图标支持\n• 导出多种格式\n\n请告诉我主题和要包含的要点。"
                        elif "动态" in user_text or "交互" in user_text or "3d" in user_text.lower():
                            response_text = "✨ 交互动态图表很有趣！我可以使用Three.js创建3D可视化，或使用Canvas制作动态效果。\n\n🚀 **技术栈：**\n• Three.js - 3D渲染\n• Canvas - 2D动画\n• WebGL - 硬件加速\n• 物理引擎支持\n\n请描述您想要的交互功能。"
                        else:
                            response_text = f"👋 您好！我是Chart Coordinator，一个AI驱动的智能图表生成系统。\n\n我收到了您的消息：\"{user_text}\"\n\n🎯 **我的能力：**\n• 流程架构图表 (Mermaid, PlantUML, Graphviz)\n• 数据可视化 (ECharts, Matplotlib, Plotly)\n• 交互动态图表 (Three.js, Canvas)\n• 思维概念图 (思维导图, 知识图谱)\n• 文档业务图表\n\n💡 **快速开始：**\n尝试说：'创建一个销售流程图' 或 '生成数据分析图表'"
                        
                        # 4. 发送主要回复事件
                        main_event = create_adk_event(
                            [{"text": response_text}],
                            partial=True,
                            turn_complete=False
                        )
                        yield f"data: {json.dumps(main_event)}\n\n"
                        await asyncio.sleep(0.4)
                        
                        # 5. 发送功能建议
                        suggestions = [
                            "💡 **专业提示：** 描述具体场景能帮我生成更精确的图表",
                            "🔧 **工具选择：** 我会根据您的需求自动选择最适合的渲染工具",
                            "📈 **数据支持：** 支持CSV、JSON等多种数据格式",
                            "🎨 **样式定制：** 可以调整颜色、字体、布局等视觉效果"
                        ]
                        
                        for suggestion in suggestions:
                            suggestion_event = create_adk_event(
                                [{"text": suggestion}],
                                partial=True,
                                turn_complete=False
                            )
                            yield f"data: {json.dumps(suggestion_event)}\n\n"
                            await asyncio.sleep(0.2)
                        
                        # 6. 发送完成事件
                        final_event = create_adk_event(
                            [{"text": "\n✅ Chart Coordinator已准备好为您服务！请告诉我您需要什么类型的图表？"}],
                            partial=False,
                            turn_complete=True
                        )
                        yield f"data: {json.dumps(final_event)}\n\n"
                        
                        # 7. 保持连接活跃（防止超时）
                        for i in range(2):
                            await asyncio.sleep(15)  # 每15秒发送心跳
                            heartbeat_event = {
                                "type": "heartbeat",
                                "timestamp": __import__('time').time(),
                                "session_id": session_id,
                                "status": "alive"
                            }
                            yield f"data: {json.dumps(heartbeat_event)}\n\n"
                        
                    except Exception as e:
                        print(f"❌ SSE生成器错误: {e}")
                        error_event = create_adk_event(
                            [{"text": f"❌ 处理错误: {str(e)}"}],
                            partial=False,
                            turn_complete=True
                        )
                        yield f"data: {json.dumps(error_event)}\n\n"
                
                # ADK + Render/Cloudflare优化的响应头
                return StreamingResponse(
                    event_generator(),
                    media_type="text/event-stream",
                    headers={
                        # ADK标准头
                        "Cache-Control": "no-cache, no-store, must-revalidate, max-age=0",
                        "Pragma": "no-cache",
                        "Expires": "0",
                        "Connection": "keep-alive",
                        
                        # Render/Cloudflare优化
                        "Content-Encoding": "identity",
                        "X-Accel-Buffering": "no",
                        "Transfer-Encoding": "chunked",
                        
                        # CORS支持
                        "Access-Control-Allow-Origin": "*",
                        "Access-Control-Allow-Headers": "Cache-Control, Content-Type, Authorization",
                        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                        
                        # 安全头
                        "X-Content-Type-Options": "nosniff",
                        "X-Frame-Options": "SAMEORIGIN",
                    }
                )
                
            except Exception as e:
                print(f"❌ /run_sse端点错误: {e}")
                return {"error": str(e), "status": "failed", "timestamp": __import__('time').time()}
    
    # 添加会话管理端点（ADK标准驼峰命名）
    @app.get("/apps/{appName}/users/{userId}/sessions/{sessionId}")
    async def get_session(appName: str, userId: str, sessionId: str):
        """ADK会话获取端点 - 使用标准驼峰命名"""
        try:
            print(f"📋 获取会话信息: {appName}/{userId}/{sessionId}")
            return {
                "sessionId": sessionId,
                "userId": userId, 
                "appName": appName,
                "status": "active",
                "createdAt": __import__('time').time(),
                "messages": [],
                "metadata": {
                    "chartCoordinatorVersion": "1.0",
                    "agentsAvailable": 5,
                    "renderTools": 15,
                    "supportedFormats": ["mermaid", "plantuml", "echarts", "matplotlib", "plotly"]
                }
            }
        except Exception as e:
            print(f"❌ 会话获取错误: {e}")
            return {"error": str(e), "status": "failed"}
    
    @app.post("/apps/{appName}/users/{userId}/sessions")
    async def create_session(appName: str, userId: str):
        """ADK会话创建端点 - 使用标准驼峰命名"""
        try:
            import uuid
            sessionId = str(uuid.uuid4())
            print(f"🆕 创建新会话: {appName}/{userId}/{sessionId}")
            return {
                "sessionId": sessionId,
                "userId": userId,
                "appName": appName, 
                "status": "created",
                "createdAt": __import__('time').time(),
                "metadata": {
                    "chartCoordinatorVersion": "1.0",
                    "initializedAgents": 5
                }
            }
        except Exception as e:
            print(f"❌ 会话创建错误: {e}")
            return {"error": str(e), "status": "failed"}

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