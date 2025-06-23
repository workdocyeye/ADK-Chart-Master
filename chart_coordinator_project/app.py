#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chart Coordinator Web Application
基于Flask的Web服务接口，用于部署到Render等云平台

主要功能：
1. 提供RESTful API接口
2. 处理图表生成请求
3. 返回生成的图表代码和预览
4. 健康检查和监控接口
"""

import os
import sys
import asyncio
import logging
import json
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import traceback
from datetime import datetime
import threading
from concurrent.futures import ThreadPoolExecutor

# 添加项目路径到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入Chart Coordinator核心系统
from llm_driven_chart_system import create_llm_driven_chart_coordinator
from google.adk import Runner

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建Flask应用
app = Flask(__name__)
CORS(app)  # 启用跨域支持

# 全局变量
chart_coordinator = None
runner = None
executor = ThreadPoolExecutor(max_workers=2)  # 异步执行器

def init_chart_coordinator():
    """初始化Chart Coordinator系统"""
    global chart_coordinator, runner
    try:
        logger.info("🚀 初始化Chart Coordinator系统...")
        chart_coordinator = create_llm_driven_chart_coordinator()
        runner = Runner()
        logger.info("✅ Chart Coordinator系统初始化成功")
        return True
    except Exception as e:
        logger.error(f"❌ Chart Coordinator系统初始化失败: {e}")
        logger.error(traceback.format_exc())
        return False

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'Chart Coordinator',
        'version': '1.0',
        'coordinator_ready': chart_coordinator is not None
    }), 200

@app.route('/', methods=['GET'])
def index():
    """主页"""
    html_template = """
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Chart Coordinator - AI智能图表生成系统</title>
        <style>
            body { font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
            .container { max-width: 800px; margin: 0 auto; background: rgba(255,255,255,0.1); padding: 30px; border-radius: 15px; backdrop-filter: blur(10px); }
            h1 { text-align: center; margin-bottom: 30px; font-size: 2.5em; }
            .feature { background: rgba(255,255,255,0.2); padding: 20px; margin: 15px 0; border-radius: 10px; }
            .api-info { background: rgba(0,0,0,0.3); padding: 20px; border-radius: 10px; margin-top: 20px; }
            code { background: rgba(0,0,0,0.5); padding: 5px 10px; border-radius: 5px; font-family: monospace; }
            .status { text-align: center; padding: 20px; }
            .ready { color: #4CAF50; }
            .not-ready { color: #f44336; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎨 Chart Coordinator</h1>
            <div class="status">
                <h2>系统状态: <span class="{{ 'ready' if coordinator_ready else 'not-ready' }}">
                    {{ '🟢 运行中' if coordinator_ready else '🔴 未就绪' }}
                </span></h2>
            </div>
            
            <div class="feature">
                <h3>🚀 AI驱动的智能图表生成</h3>
                <p>基于Google ADK框架，支持多种图表类型：流程图、数据可视化、思维导图、架构图等</p>
            </div>
            
            <div class="feature">
                <h3>📊 支持的图表类型</h3>
                <ul>
                    <li><strong>流程架构:</strong> Mermaid、PlantUML、Graphviz</li>
                    <li><strong>数据可视化:</strong> ECharts、Matplotlib、Plotly</li>
                    <li><strong>交互动态:</strong> Three.js、Canvas、WebGL</li>
                    <li><strong>思维概念:</strong> 思维导图、知识图谱</li>
                    <li><strong>文档图表:</strong> 报告图表、业务图表</li>
                </ul>
            </div>
            
            <div class="api-info">
                <h3>📡 API接口</h3>
                <p><strong>生成图表:</strong> <code>POST /generate</code></p>
                <p><strong>健康检查:</strong> <code>GET /health</code></p>
                <p><strong>系统信息:</strong> <code>GET /info</code></p>
            </div>
            
            <div style="text-align: center; margin-top: 30px;">
                <p>🏆 为Google ADK Hackathon开发 | Powered by AI</p>
            </div>
        </div>
    </body>
    </html>
    """
    return render_template_string(html_template, coordinator_ready=chart_coordinator is not None)

@app.route('/generate', methods=['POST'])
def generate_chart():
    """生成图表接口"""
    try:
        if not chart_coordinator:
            return jsonify({
                'error': 'Chart Coordinator系统未初始化',
                'status': 'error'
            }), 503
        
        # 获取请求数据
        data = request.get_json()
        if not data:
            return jsonify({
                'error': '请提供JSON格式的请求数据',
                'status': 'error'
            }), 400
        
        user_data = data.get('data', '')
        requirements = data.get('requirements', '')
        domain = data.get('domain', '通用')
        
        if not user_data or not requirements:
            return jsonify({
                'error': '请提供data和requirements字段',
                'status': 'error'
            }), 400
        
        logger.info(f"📊 收到图表生成请求，领域: {domain}")
        
        # 构建会话和运行Chart Coordinator
        session_id = f"chart_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 在线程池中运行异步Chart Coordinator
        def run_chart_coordinator():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(
                    runner.run_async(
                        agent=chart_coordinator,
                        session_id=session_id,
                        user_input=f"""
                        请根据以下信息生成图表：
                        
                        数据: {user_data}
                        需求: {requirements}
                        领域: {domain}
                        
                        请分析这些信息并生成最合适的图表代码。
                        """,
                        memory_service=None,  # 可以后续添加内存服务
                        session_service=None  # 可以后续添加会话服务
                    )
                )
            finally:
                loop.close()
        
        # 提交到线程池执行
        future = executor.submit(run_chart_coordinator)
        result = future.result(timeout=120)  # 2分钟超时
        
        return jsonify({
            'status': 'success',
            'session_id': session_id,
            'result': result,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ 图表生成失败: {e}")
        logger.error(traceback.format_exc())
        return jsonify({
            'error': f'图表生成失败: {str(e)}',
            'status': 'error',
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/info', methods=['GET'])
def system_info():
    """系统信息接口"""
    return jsonify({
        'service': 'Chart Coordinator',
        'version': '1.0',
        'framework': 'Google ADK',
        'description': 'AI驱动的智能图表生成系统',
        'supported_charts': [
            'Mermaid流程图',
            'PlantUML架构图', 
            'ECharts数据图表',
            'Three.js 3D图表',
            'Matplotlib统计图',
            'Plotly交互图表',
            '思维导图',
            '知识图谱'
        ],
        'coordinator_ready': chart_coordinator is not None,
        'timestamp': datetime.now().isoformat()
    })

@app.errorhandler(404)
def not_found(error):
    """404错误处理"""
    return jsonify({
        'error': '接口不存在',
        'status': 'error',
        'available_endpoints': ['/health', '/', '/generate', '/info']
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """500错误处理"""
    return jsonify({
        'error': '服务器内部错误',
        'status': 'error'
    }), 500

def main():
    """主函数"""
    logger.info("🚀 启动Chart Coordinator Web服务...")
    
    # 初始化Chart Coordinator系统
    if not init_chart_coordinator():
        logger.error("❌ Chart Coordinator系统初始化失败，服务将以受限模式运行")
    
    # 获取端口（Render会设置PORT环境变量）
    port = int(os.environ.get('PORT', 5000))
    
    logger.info(f"🌐 服务启动在端口 {port}")
    
    # 启动Flask应用
    app.run(
        host='0.0.0.0',  # 监听所有IP
        port=port,
        debug=False,  # 生产环境不启用debug
        threaded=True   # 启用多线程支持
    )

if __name__ == '__main__':
    main() 