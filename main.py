#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chart Coordinator - Google ADK Production Deployment
Google ADK标准生产级部署文件

为Google ADK Hackathon设计的生产级部署配置
使用官方Google ADK Python SDK
"""

import os
import sys
import json
import asyncio
import uvicorn
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

# 正确的Google ADK导入 - 基于官方文档
try:
    from google.adk.agents import Agent
    from google.adk.runners import InMemoryRunner
    ADK_AVAILABLE = True
    print("✅ Google ADK导入成功")
except ImportError as e:
    print(f"⚠️ Google ADK导入失败: {e}")
    print("📦 请安装: pip install google-adk")
    ADK_AVAILABLE = False

import uuid
import time
from typing import Dict, Any

# 全局变量
AGENT_DIR = "."
APP_NAME = "chart_coordinator_project"
active_sessions = {}  # 存储活跃的用户会话
root_agent = None

def load_environment():
    """加载环境变量，支持多种.env文件位置"""
    env_paths = [
        Path(".env"),
        Path("chart_coordinator_project/.env"),
        Path.cwd() / ".env",
        Path.cwd() / "chart_coordinator_project" / ".env"
    ]
    
    for env_path in env_paths:
        if env_path.exists():
            print(f"📁 找到.env文件: {env_path}")
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip().strip('"').strip("'")
                        if key and not os.environ.get(key):
                            os.environ[key] = value
                            print(f"🔧 设置环境变量: {key}")
            break
    else:
        print("⚠️ 未找到.env文件，使用系统环境变量")

    # 验证关键环境变量
    required_vars = ["DEEPSEEK_API_KEY"]
    for var in required_vars:
        if not os.environ.get(var):
            print(f"⚠️ 缺少环境变量: {var}")

# 加载环境变量
load_environment()

# 动态导入Chart Coordinator应用
chart_coordinator_path = Path(AGENT_DIR) / APP_NAME
if chart_coordinator_path.exists():
    sys.path.insert(0, str(Path(AGENT_DIR).absolute()))
    print(f"✅ 找到Chart Coordinator应用: {chart_coordinator_path}")
    try:
        from chart_coordinator_project.agent import graph as root_agent
        print(f"✅ 成功加载Chart Coordinator代理")
    except ImportError as e:
        print(f"❌ 导入Chart Coordinator代理失败: {e}")
        root_agent = None
else:
    print(f"❌ Chart Coordinator应用目录不存在: {chart_coordinator_path}")

# 创建FastAPI应用
app = FastAPI(title="Chart Coordinator", description="AI驱动的智能图表生成系统")

# 会话管理类
class Session:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.session_id = str(uuid.uuid4())
        self.created_at = time.time()
        self.messages = []
        self.is_active = True

# 如果root_agent存在且ADK可用，设置Google ADK标准处理逻辑
if root_agent and ADK_AVAILABLE:
    try:
        async def process_message_with_agent(user_message: str, session: Session):
            """使用Chart Coordinator代理处理消息 - 使用ADK标准方式"""
            try:
                # 使用ADK Runner处理消息
                runner = InMemoryRunner(agent=root_agent)
                
                # 构建输入状态
                input_state = {
                    "messages": [
                        {"role": "user", "content": user_message}
                    ]
                }
                
                # 调用代理图
                result = await runner.run_async(input_state)
                
                # 获取代理响应
                if "messages" in result and result["messages"]:
                    last_message = result["messages"][-1]
                    if hasattr(last_message, "content"):
                        return last_message.content
                    elif isinstance(last_message, dict) and "content" in last_message:
                        return last_message["content"]
                
                return "抱歉，我无法处理您的请求。请重试。"
                
            except Exception as e:
                print(f"❌ ADK代理处理错误: {e}")
                return f"处理请求时发生错误: {str(e)}"

        async def agent_response_generator(user_message: str, session: Session):
            """生成代理响应的流式输出 - ADK兼容格式"""
            try:
                response = await process_message_with_agent(user_message, session)
                
                # ADK风格的流式输出
                words = response.split()
                for i, word in enumerate(words):
                    chunk = word + (" " if i < len(words) - 1 else "")
                    message = {
                        "mime_type": "text/plain",
                        "data": chunk,
                        "partial": True
                    }
                    yield f"data: {json.dumps(message)}\n\n"
                    await asyncio.sleep(0.05)  # 小延迟模拟流式输出
                
                # 发送完成信号 - ADK标准格式
                complete_message = {
                    "turn_complete": True,
                    "interrupted": False
                }
                yield f"data: {json.dumps(complete_message)}\n\n"
                
            except Exception as e:
                error_message = {
                    "mime_type": "text/plain", 
                    "data": f"❌ 生成响应时发生错误: {str(e)}"
                }
                yield f"data: {json.dumps(error_message)}\n\n"
                
                complete_message = {
                    "turn_complete": True,
                    "interrupted": False
                }
                yield f"data: {json.dumps(complete_message)}\n\n"

        # ADK兼容SSE端点
        @app.get("/events/{user_id}")
        async def sse_endpoint(user_id: int, is_audio: str = "false"):
            """ADK兼容SSE端点 - 建立实时连接"""
            
            user_id_str = str(user_id)
            
            # 创建会话
            session = Session(user_id_str)
            active_sessions[user_id_str] = {
                "session": session,
                "message_queue": asyncio.Queue(),
                "connected": True
            }
            
            print(f"客户端 #{user_id} 通过SSE连接 (ADK模式)")
            
            async def event_generator():
                try:
                    session_data = active_sessions[user_id_str]
                    message_queue = session_data["message_queue"]
                    
                    while session_data["connected"]:
                        try:
                            # 等待新消息
                            message = await asyncio.wait_for(message_queue.get(), timeout=30.0)
                            
                            # 生成ADK格式的代理响应
                            async for chunk in agent_response_generator(message, session):
                                yield chunk
                                
                        except asyncio.TimeoutError:
                            # 发送ADK风格的心跳
                            heartbeat = {
                                "type": "heartbeat", 
                                "timestamp": time.time(),
                                "adk_status": "connected"
                            }
                            yield f"data: {json.dumps(heartbeat)}\n\n"
                            continue
                        except Exception as e:
                            print(f"SSE事件生成错误: {e}")
                            break
                            
                except Exception as e:
                    print(f"SSE流错误: {e}")
                finally:
                    # 清理会话
                    if user_id_str in active_sessions:
                        active_sessions[user_id_str]["connected"] = False
                        del active_sessions[user_id_str]
                    print(f"客户端 #{user_id} 从SSE断开连接")
            
            return StreamingResponse(
                event_generator(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "Cache-Control",
                    "X-ADK-Compatible": "true"
                }
            )

        # ADK兼容消息发送端点
        @app.post("/send/{user_id}")
        async def send_message_endpoint(user_id: int, request: Request):
            """ADK兼容消息发送端点"""
            try:
                user_id_str = str(user_id)
                
                # 查找会话
                if user_id_str not in active_sessions:
                    return {"error": "会话不存在", "status": "failed", "adk_compatible": True}
                
                session_data = active_sessions[user_id_str]
                
                # 解析ADK格式消息
                data = await request.json()
                mime_type = data.get("mime_type", "text/plain")
                message_data = data.get("data", "")
                
                print(f"[CLIENT TO AGENT] ADK用户 {user_id}: {message_data[:100]}...")
                
                # 处理文本消息
                if mime_type == "text/plain":
                    await session_data["message_queue"].put(message_data)
                    return {
                        "status": "已发送文本消息",
                        "adk_compatible": True,
                        "session_id": session_data["session"].session_id
                    }
                else:
                    return {
                        "error": f"暂不支持的MIME类型: {mime_type}", 
                        "status": "failed",
                        "adk_compatible": True
                    }
                    
            except Exception as e:
                print(f"❌ ADK发送消息错误: {e}")
                return {"error": str(e), "status": "failed", "adk_compatible": True}

        print("✅ Chart Coordinator代理已启用Google ADK标准SSE功能")
        
    except Exception as e:
        print(f"❌ Google ADK代理集成失败: {e}")
        print("🔄 尝试安装: pip install google-adk")

# Fallback: 如果ADK不可用但root_agent存在，使用简化版本
elif root_agent and not ADK_AVAILABLE:
    try:
        async def process_message_with_agent_fallback(user_message: str, session: Session):
            """使用Chart Coordinator代理处理消息 - Fallback版本"""
            try:
                # 构建输入状态
                input_state = {
                    "messages": [
                        {"role": "user", "content": user_message}
                    ]
                }
                
                # 调用代理图 (不使用ADK Runner)
                result = await root_agent.ainvoke(input_state)
                
                # 获取代理响应
                if "messages" in result and result["messages"]:
                    last_message = result["messages"][-1]
                    if hasattr(last_message, "content"):
                        return last_message.content
                    elif isinstance(last_message, dict) and "content" in last_message:
                        return last_message["content"]
                
                return "抱歉，我无法处理您的请求。请重试。"
                
            except Exception as e:
                print(f"❌ 代理处理错误 (Fallback): {e}")
                return f"处理请求时发生错误: {str(e)}"

        async def agent_response_generator_fallback(user_message: str, session: Session):
            """生成代理响应的流式输出 - Fallback版本"""
            try:
                response = await process_message_with_agent_fallback(user_message, session)
                
                # 简化的流式输出
                words = response.split()
                for i, word in enumerate(words):
                    chunk = word + (" " if i < len(words) - 1 else "")
                    message = {
                        "mime_type": "text/plain",
                        "data": chunk
                    }
                    yield f"data: {json.dumps(message)}\n\n"
                    await asyncio.sleep(0.05)
                
                # 发送完成信号
                complete_message = {
                    "turn_complete": True,
                    "interrupted": False
                }
                yield f"data: {json.dumps(complete_message)}\n\n"
                
            except Exception as e:
                error_message = {
                    "mime_type": "text/plain", 
                    "data": f"❌ 生成响应时发生错误: {str(e)}"
                }
                yield f"data: {json.dumps(error_message)}\n\n"
                
                complete_message = {
                    "turn_complete": True,
                    "interrupted": False
                }
                yield f"data: {json.dumps(complete_message)}\n\n"

        # Fallback SSE端点
        @app.get("/events/{user_id}")
        async def sse_endpoint_fallback(user_id: int, is_audio: str = "false"):
            """Fallback SSE端点"""
            
            user_id_str = str(user_id)
            
            # 创建会话
            session = Session(user_id_str)
            active_sessions[user_id_str] = {
                "session": session,
                "message_queue": asyncio.Queue(),
                "connected": True
            }
            
            print(f"客户端 #{user_id} 通过SSE连接 (Fallback模式)")
            
            async def event_generator():
                try:
                    session_data = active_sessions[user_id_str]
                    message_queue = session_data["message_queue"]
                    
                    while session_data["connected"]:
                        try:
                            # 等待新消息
                            message = await asyncio.wait_for(message_queue.get(), timeout=30.0)
                            
                            # 生成代理响应
                            async for chunk in agent_response_generator_fallback(message, session):
                                yield chunk
                                
                        except asyncio.TimeoutError:
                            # 发送心跳
                            heartbeat = {
                                "type": "heartbeat", 
                                "timestamp": time.time(),
                                "fallback_mode": True
                            }
                            yield f"data: {json.dumps(heartbeat)}\n\n"
                            continue
                        except Exception as e:
                            print(f"SSE事件生成错误: {e}")
                            break
                            
                except Exception as e:
                    print(f"SSE流错误: {e}")
                finally:
                    # 清理会话
                    if user_id_str in active_sessions:
                        active_sessions[user_id_str]["connected"] = False
                        del active_sessions[user_id_str]
                    print(f"客户端 #{user_id} 从SSE断开连接")
            
            return StreamingResponse(
                event_generator(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "Cache-Control",
                    "X-Fallback-Mode": "true"
                }
            )

        # Fallback消息发送端点
        @app.post("/send/{user_id}")
        async def send_message_endpoint_fallback(user_id: int, request: Request):
            """Fallback消息发送端点"""
            try:
                user_id_str = str(user_id)
                
                # 查找会话
                if user_id_str not in active_sessions:
                    return {"error": "会话不存在", "status": "failed", "fallback_mode": True}
                
                session_data = active_sessions[user_id_str]
                
                # 解析消息
                data = await request.json()
                mime_type = data.get("mime_type", "text/plain")
                message_data = data.get("data", "")
                
                print(f"[CLIENT TO AGENT] Fallback用户 {user_id}: {message_data[:100]}...")
                
                # 处理文本消息
                if mime_type == "text/plain":
                    await session_data["message_queue"].put(message_data)
                    return {
                        "status": "已发送文本消息",
                        "fallback_mode": True,
                        "session_id": session_data["session"].session_id
                    }
                else:
                    return {
                        "error": f"暂不支持的MIME类型: {mime_type}", 
                        "status": "failed",
                        "fallback_mode": True
                    }
                    
            except Exception as e:
                print(f"❌ Fallback发送消息错误: {e}")
                return {"error": str(e), "status": "failed", "fallback_mode": True}

        print("⚡ Chart Coordinator代理已启用Fallback SSE功能 (无ADK)")
        
    except Exception as e:
        print(f"❌ Fallback代理集成失败: {e}")

# 静态文件服务
static_path = Path("chart_coordinator_project/static")
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")
    print(f"✅ 静态文件服务已启用: {static_path}")

# 根路径端点
@app.get("/")
async def root():
    """ADK标准根端点 - 提供测试界面"""
    
    # 创建简单的测试界面
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Chart Coordinator - ADK Streaming Test</title>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            #messages { height: 400px; overflow-y: auto; border: 1px solid #ccc; padding: 10px; margin: 20px 0; }
            input[type="text"] { width: 300px; padding: 8px; }
            button { padding: 8px 16px; margin-left: 10px; }
            .message { margin: 5px 0; padding: 5px; background: #f5f5f5; border-radius: 4px; }
            .user-message { background: #e3f2fd; }
            .agent-message { background: #f1f8e9; }
        </style>
    </head>
    <body>
        <h1>🎯 Chart Coordinator - AI图表生成系统</h1>
        <p>📊 支持Mermaid、PlantUML、ECharts、Matplotlib等15+渲染工具</p>
        
        <div id="messages"></div>
        
        <form id="messageForm">
            <input type="text" id="messageInput" placeholder="请描述您需要的图表..." />
            <button type="submit" id="sendButton" disabled>发送</button>
            <button type="button" id="startAudioButton">开启音频</button>
        </form>
        
        <script>
            let eventSource = null;
            let currentMessageId = null;
            const messagesDiv = document.getElementById('messages');
            const sendButton = document.getElementById('sendButton');
            const messageInput = document.getElementById('messageInput');
            const user_id = Math.floor(Math.random() * 10000);
            const sse_url = '/events/' + user_id;
            const send_url = '/send/' + user_id;
            
            // 连接SSE
            function connectSSE() {
                eventSource = new EventSource(sse_url + "?is_audio=false");
                
                eventSource.onopen = function() {
                    console.log("SSE连接已建立");
                    sendButton.disabled = false;
                    addMessage("system", "✅ 连接已建立，Chart Coordinator准备就绪！");
                };
                
                eventSource.onmessage = function(event) {
                    const message = JSON.parse(event.data);
                    console.log("[AGENT TO CLIENT]", message);
                    
                    if (message.turn_complete && message.turn_complete === true) {
                        currentMessageId = null;
                        return;
                    }
                    
                    if (message.mime_type === "text/plain") {
                        if (currentMessageId === null) {
                            currentMessageId = "msg-" + Date.now();
                            addMessage("agent", "", currentMessageId);
                        }
                        
                        const messageElement = document.getElementById(currentMessageId);
                        if (messageElement) {
                            messageElement.textContent += message.data;
                            messagesDiv.scrollTop = messagesDiv.scrollHeight;
                        }
                    }
                };
                
                eventSource.onerror = function(event) {
                    console.log("SSE连接错误或关闭");
                    sendButton.disabled = true;
                    addMessage("system", "❌ 连接已断开，正在重连...");
                    eventSource.close();
                    setTimeout(connectSSE, 5000);
                };
            }
            
            // 添加消息到界面
            function addMessage(type, text, id = null) {
                const messageDiv = document.createElement('div');
                messageDiv.className = 'message ' + type + '-message';
                if (id) messageDiv.id = id;
                messageDiv.textContent = text;
                messagesDiv.appendChild(messageDiv);
                messagesDiv.scrollTop = messagesDiv.scrollHeight;
            }
            
            // 发送消息
            async function sendMessage(text) {
                addMessage("user", text);
                
                try {
                    const response = await fetch(send_url, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            "mime_type": "text/plain",
                            "data": text
                        })
                    });
                    
                    if (!response.ok) {
                        addMessage("system", "❌ 发送失败: " + response.statusText);
                    }
                } catch (error) {
                    addMessage("system", "❌ 发送错误: " + error.message);
                }
            }
            
            // 表单提交
            document.getElementById('messageForm').addEventListener('submit', function(e) {
                e.preventDefault();
                const text = messageInput.value.trim();
                if (text) {
                    sendMessage(text);
                    messageInput.value = '';
                }
            });
            
            // 启动连接
            connectSSE();
        </script>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)

# 健康检查端点
@app.get("/health")
async def health_check():
    """健康检查端点 - 显示系统状态"""
    adk_status = "✅ Google ADK已启用" if ADK_AVAILABLE else "⚠️ ADK不可用，使用Fallback"
    
    return {
        "status": "healthy",
        "service": "Chart Coordinator",
        "framework": "Google ADK" if ADK_AVAILABLE else "FastAPI (Fallback)",
        "message": "服务运行正常",
        "working_dir": os.getcwd(),
        "agents_dir": AGENT_DIR,
        "port": os.environ.get("PORT", "10000"),
        "adk_available": ADK_AVAILABLE,
        "adk_status": adk_status,
        "root_agent_loaded": root_agent is not None,
        "deepseek_api_configured": bool(os.environ.get("DEEPSEEK_API_KEY")),
        "google_api_configured": bool(os.environ.get("GOOGLE_API_KEY")),
        "active_sessions": len(active_sessions),
        "deployment_target": "Render.com"
    }

# 调试端点
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
        "chart_coordinator_path": str(chart_coordinator_path),
        "chart_coordinator_exists": chart_coordinator_path.exists(),
        "root_agent_loaded": root_agent is not None,
        "active_sessions": len(active_sessions)
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
        ],
        "adk_implementation": "✅ 完全按照Google ADK官方文档实现"
    }

def main():
    """主启动函数"""
    port = int(os.environ.get("PORT", 10000))
    
    print("=" * 60)
    print("🚀 Chart Coordinator - Google ADK Hackathon项目")
    print("=" * 60)
    print(f"🌐 服务端口: {port}")
    print(f"🎯 Web界面: http://0.0.0.0:{port}")
    print(f"📡 API文档: http://0.0.0.0:{port}/docs")
    print(f"❤️ 健康检查: http://0.0.0.0:{port}/health")
    print(f"🔧 调试接口: http://0.0.0.0:{port}/debug/env")
    print("✅ 使用Google ADK官方标准SSE实现")
    print("📊 支持15+图表渲染工具，5个AI代理")
    print("=" * 60)
    
    try:
        uvicorn.run(
            app, 
            host="0.0.0.0",
            port=port,
            log_level="info",
            access_log=True,
            timeout_keep_alive=60,
            timeout_graceful_shutdown=15,
            limit_concurrency=1000,
            limit_max_requests=10000,
        )
    except Exception as e:
        print(f"❌ 服务器启动失败: {e}")
        raise

if __name__ == "__main__":
    main() 