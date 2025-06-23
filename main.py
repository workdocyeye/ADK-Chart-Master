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
import json
import asyncio
import uvicorn
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from google.adk.core import Agent
from google.adk.core.runners import InMemoryRunner
from google.adk.core.session_service import SessionService
from google.adk.core.config import RunConfig
from google.adk.core.content import Content, Part
from google.adk.core.live_request_queue import LiveRequestQueue
import base64

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
        print("⚠️ 未找到.env文件，使用Render环境变量")

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

# 如果root_agent存在，包装为ADK兼容的代理
if root_agent:
    try:
        # 使用ADK标准方式启动代理会话
        async def start_agent_session(user_id: str, is_audio: bool = False):
            """启动代理会话 - 完全按照ADK官方文档实现"""
            
            # 创建Runner
            runner = InMemoryRunner(
                app_name=APP_NAME,
                agent=root_agent,
            )
            
            # 创建Session
            session = await runner.session_service.create_session(
                app_name=APP_NAME,
                user_id=user_id,
            )
            
            # 设置响应模态
            modality = "AUDIO" if is_audio else "TEXT"
            run_config = RunConfig(response_modalities=[modality])
            
            # 创建LiveRequestQueue
            live_request_queue = LiveRequestQueue()
            
            # 启动代理会话
            live_events = runner.run_live(
                session=session,
                live_request_queue=live_request_queue,
                run_config=run_config,
            )
            
            return live_events, live_request_queue

        async def agent_to_client_sse(live_events):
            """代理到客户端的SSE通信 - 完全按照ADK官方文档实现"""
            async for event in live_events:
                # 如果对话完成或被中断，发送它
                if event.turn_complete or event.interrupted:
                    message = {
                        "turn_complete": event.turn_complete,
                        "interrupted": event.interrupted,
                    }
                    yield f"data: {json.dumps(message)}\n\n"
                    print(f"[AGENT TO CLIENT]: {message}")
                    continue

                # 读取Content和它的第一个Part
                part: Part = (
                    event.content and event.content.parts and event.content.parts[0]
                )
                if not part:
                    continue

                # 如果是音频，发送Base64编码的音频数据
                is_audio = part.inline_data and part.inline_data.mime_type.startswith("audio/pcm")
                if is_audio:
                    audio_data = part.inline_data and part.inline_data.data
                    if audio_data:
                        message = {
                            "mime_type": "audio/pcm",
                            "data": base64.b64encode(audio_data).decode("ascii")
                        }
                        yield f"data: {json.dumps(message)}\n\n"
                        print(f"[AGENT TO CLIENT]: audio/pcm: {len(audio_data)} bytes.")
                        continue

                # 如果是文本且是部分文本，发送它
                if part.text and event.partial:
                    message = {
                        "mime_type": "text/plain",
                        "data": part.text
                    }
                    yield f"data: {json.dumps(message)}\n\n"
                    print(f"[AGENT TO CLIENT]: text/plain: {message}")

        # ADK标准SSE端点
        @app.get("/events/{user_id}")
        async def sse_endpoint(user_id: int, is_audio: str = "false"):
            """ADK标准SSE端点 - 按照官方文档实现"""
            
            # 启动代理会话
            user_id_str = str(user_id)
            live_events, live_request_queue = await start_agent_session(user_id_str, is_audio == "true")
            
            # 存储此用户的请求队列
            active_sessions[user_id_str] = live_request_queue
            
            print(f"客户端 #{user_id} 通过SSE连接，音频模式: {is_audio}")
            
            def cleanup():
                live_request_queue.close()
                if user_id_str in active_sessions:
                    del active_sessions[user_id_str]
                print(f"客户端 #{user_id} 从SSE断开连接")
            
            async def event_generator():
                try:
                    async for data in agent_to_client_sse(live_events):
                        yield data
                except Exception as e:
                    print(f"SSE流错误: {e}")
                finally:
                    cleanup()
            
            return StreamingResponse(
                event_generator(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "Cache-Control"
                }
            )

        # ADK标准消息发送端点
        @app.post("/send/{user_id}")
        async def send_message_endpoint(user_id: int, request: Request):
            """ADK标准消息发送端点 - 按照官方文档实现"""
            try:
                user_id_str = str(user_id)
                
                # 查找会话
                if user_id_str not in active_sessions:
                    return {"error": "会话不存在", "status": "failed"}
                
                live_request_queue = active_sessions[user_id_str]
                
                # 解析消息
                data = await request.json()
                mime_type = data.get("mime_type", "text/plain")
                message_data = data.get("data", "")
                
                print(f"[CLIENT TO AGENT] 用户 {user_id}: {mime_type} - {message_data[:100]}...")
                
                # 处理文本消息
                if mime_type == "text/plain":
                    content = Content(parts=[Part.from_text(message_data)])
                    await live_request_queue.send_content(content)
                    return {"status": "已发送文本消息"}
                
                # 处理音频消息
                elif mime_type == "audio/pcm":
                    try:
                        audio_data = base64.b64decode(message_data)
                        blob = Part.from_bytes(audio_data, mime_type="audio/pcm")
                        await live_request_queue.send_realtime(blob)
                        return {"status": "已发送音频消息"}
                    except Exception as e:
                        return {"error": f"音频处理错误: {str(e)}", "status": "failed"}
                
                else:
                    return {"error": f"不支持的MIME类型: {mime_type}", "status": "failed"}
                    
            except Exception as e:
                print(f"❌ 发送消息错误: {e}")
                return {"error": str(e), "status": "failed"}

        print("✅ Chart Coordinator代理已启用ADK标准SSE功能")
        
    except Exception as e:
        print(f"❌ ADK代理集成失败: {e}")

# 静态文件服务
app.mount("/static", StaticFiles(directory="chart_coordinator_project/static"), name="static")

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
    """Render健康检查端点"""
    return {
        "status": "healthy",
        "service": "Chart Coordinator",
        "framework": "Google ADK",
        "message": "服务运行正常",
        "working_dir": os.getcwd(),
        "agents_dir": AGENT_DIR,
        "port": os.environ.get("PORT", "10000"),
        "deepseek_api_configured": bool(os.environ.get("DEEPSEEK_API_KEY")),
        "adk_standard": "✅ 使用ADK标准SSE实现"
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