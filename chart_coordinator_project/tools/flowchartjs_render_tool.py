# Copyright 2025 Google LLC
# FlowchartJS渲染工具 - JavaScript流程图专家

import logging
import platform
from typing import Dict, Any, Optional

from google.genai import types
from .base_render_tool import BaseRenderTool

logger = logging.getLogger(__name__)


class FlowchartJSRenderTool(BaseRenderTool):
    """📋 FlowchartJS前端流程图渲染工具"""
    
    def __init__(self):
        super().__init__(
            name="render_flowchartjs",
            description="📋 FlowchartJS前端流程图渲染工具：生成基于flowchart.js的流程图HTML",
            supported_formats=["html"],
            default_format="html"
        )
        self._setup_chinese_fonts()
    
    def _setup_chinese_fonts(self):
        """🔧 设置智能中文字体支持"""
        logger.info("🎨 配置FlowchartJS中文字体支持...")
        
        # 获取系统类型
        system = platform.system().lower()
        
        # 定义跨平台字体优先级
        if system == "windows":
            self.chinese_fonts = ["Microsoft YaHei", "SimHei", "SimSun", "KaiTi", "sans-serif"]
        elif system == "darwin":  # macOS
            self.chinese_fonts = ["Arial Unicode MS", "Hiragino Sans GB", "PingFang SC", "sans-serif"]
        else:  # Linux及其他
            self.chinese_fonts = ["WenQuanYi Micro Hei", "Noto Sans CJK SC", "DejaVu Sans", "sans-serif"]
        
        # 构建字体族字符串
        self.font_family = ", ".join([f'"{font}"' for font in self.chinese_fonts])
        
        logger.info(f"✅ FlowchartJS中文字体配置完成: {self.font_family}")
    
    def _get_declaration(self) -> Optional[types.FunctionDeclaration]:
        return types.FunctionDeclaration(
            name=self.name,
            description=self.description,
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    'code': types.Schema(
                        type=types.Type.STRING,
                        description='Flowchart.js语法的流程图代码'
                    ),
                    'width': types.Schema(
                        type=types.Type.INTEGER,
                        description='流程图宽度（像素）',
                        default=800
                    ),
                    'height': types.Schema(
                        type=types.Type.INTEGER,
                        description='流程图高度（像素）',
                        default=600
                    ),
                    'title': types.Schema(
                        type=types.Type.STRING,
                        description='流程图标题',
                        default='FlowchartJS 流程图'
                    )
                },
                required=['code'],
            )
        )
    
    def _render_sync(self, code: str, output_format: str = "html", width: int = 800, height: int = 600, title: str = "FlowchartJS 流程图") -> Dict[str, Any]:
        try:
            html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <!-- 多CDN备用方案 -->
    <script>
        // 资源加载优先级：本地优先，CDN备用
        const raphaelSources = [
            '/static/js/raphael.min.js',  // 本地资源（首选）
            'https://cdn.jsdelivr.net/npm/raphael@2.3.0/raphael.min.js',
            'https://cdnjs.cloudflare.com/ajax/libs/raphael/2.3.0/raphael.min.js'
        ];
        
        const flowchartSources = [
            '/static/js/flowchart.min.js',  // 本地资源（首选）
            'https://cdnjs.cloudflare.com/ajax/libs/flowchart/1.17.1/flowchart.min.js',
            'https://cdn.jsdelivr.net/npm/flowchart.js@1.17.1/release/flowchart.min.js'
        ];
        
        // 智能资源加载：本地优先，CDN备用
        async function loadLibrariesWithFallback() {{
            let raphaelLoaded = false;
            let flowchartLoaded = false;
            
            // 尝试加载Raphael（本地优先）
            for (const url of raphaelSources) {{
                try {{
                    const isLocal = url.startsWith('/static/');
                    const timeout = isLocal ? 2000 : 5000;
                    
                    console.log(`尝试加载Raphael: ${{url}} (${{isLocal ? '本地' : 'CDN'}})`);
                    
                    const script = document.createElement('script');
                    script.src = url;
                    document.head.appendChild(script);
                    
                    await new Promise((resolve, reject) => {{
                        script.onload = resolve;
                        script.onerror = reject;
                        setTimeout(reject, timeout);
                    }});
                    
                    if (typeof Raphael !== 'undefined') {{
                        raphaelLoaded = true;
                        console.log(`✅ Raphael加载成功: ${{url}} (${{isLocal ? '本地资源' : 'CDN资源'}})`);
                        break;
                    }}
                }} catch (e) {{
                    const isLocal = url.startsWith('/static/');
                    console.warn(`❌ Raphael加载失败: ${{url}} (${{isLocal ? '本地' : 'CDN'}})`);
                }}
            }}
            
            // 尝试加载Flowchart.js（本地优先）
            for (const url of flowchartSources) {{
                try {{
                    const isLocal = url.startsWith('/static/');
                    const timeout = isLocal ? 2000 : 5000;
                    
                    console.log(`尝试加载Flowchart.js: ${{url}} (${{isLocal ? '本地' : 'CDN'}})`);
                    
                    const script = document.createElement('script');
                    script.src = url;
                    document.head.appendChild(script);
                    
                    await new Promise((resolve, reject) => {{
                        script.onload = resolve;
                        script.onerror = reject;
                        setTimeout(reject, timeout);
                    }});
                    
                    if (typeof flowchart !== 'undefined') {{
                        flowchartLoaded = true;
                        console.log(`✅ Flowchart.js加载成功: ${{url}} (${{isLocal ? '本地资源' : 'CDN资源'}})`);
                        break;
                    }}
                }} catch (e) {{
                    const isLocal = url.startsWith('/static/');
                    console.warn(`❌ Flowchart.js加载失败: ${{url}} (${{isLocal ? '本地' : 'CDN'}})`);
                }}
            }}
            
            return {{ raphaelLoaded, flowchartLoaded }};
        }}
        
        // 如果所有CDN都失败，提供简化的本地实现
        function createFallbackDiagram() {{
            const diagramDiv = document.getElementById('diagram');
            diagramDiv.innerHTML = `
                <div style="text-align: center; padding: 40px; border: 2px dashed #ccc; background: #f9f9f9; width: 100%; height: 100%; box-sizing: border-box;">
                    <h3 style="color: #666; margin-bottom: 20px;">FlowchartJS库加载失败</h3>
                    <p style="color: #888; margin-bottom: 15px;">正在使用简化版本显示流程图结构：</p>
                    <div style="background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                        <pre style="text-align: left; font-family: {self.font_family}; color: #333; line-height: 1.6;">{code}</pre>
                    </div>
                </div>
            `;
        }}
    </script>
    <style>
        body {{ 
            margin: 0; 
            padding: 0;
            font-family: {self.font_family}; 
            background-color: #ffffff;
            display: flex;
            justify-content: center;
            align-items: center;
            width: 100vw;
            height: 100vh;
            overflow: hidden;
        }}
        #diagram {{ 
            width: {width}px; 
            height: {height}px; 
            overflow: auto;
        }}
        /* SVG文本元素中文字体支持 */
        text {{
            font-family: {self.font_family} !important;
        }}
        /* 流程图节点样式优化 */
        rect, path, ellipse {{
            stroke: #2c3e50;
            stroke-width: 2px;
        }}
    </style>
</head>
<body>
    <div id="diagram"></div>
    <script>
        // 等待DOM加载完成后开始加载库
        document.addEventListener('DOMContentLoaded', async function() {{
            console.log('开始加载FlowchartJS库...');
            
        try {{
                // 尝试加载库
                const {{ raphaelLoaded, flowchartLoaded }} = await loadLibrariesWithFallback();
                
                if (!raphaelLoaded || !flowchartLoaded) {{
                    console.warn('部分库加载失败，使用备用方案');
                    createFallbackDiagram();
                    return;
                }}
                
                // 等待一下确保库完全初始化
                await new Promise(resolve => setTimeout(resolve, 100));
                
                // 再次检查库是否可用
                if (typeof Raphael === 'undefined' || typeof flowchart === 'undefined') {{
                    console.error('库加载后仍不可用');
                    createFallbackDiagram();
                    return;
                }}
                
                console.log('FlowchartJS库加载成功，开始渲染...');
                
            // 创建流程图配置，支持中文
            var diagramOptions = {{
                'x': 0,
                'y': 0,
                'line-width': 2,
                'line-length': 50,
                'text-margin': 10,
                'font-size': 14,
                'font-family': '{self.font_family}',
                'font-color': '#2c3e50',
                'line-color': '#34495e',
                'element-color': '#3498db',
                'fill': '#ecf0f1',
                'yes-text': '是',
                'no-text': '否',
                'arrow-end': 'block',
                'flowstate': {{
                    'past' : {{'fill': '#CCCCCC', 'font-size': 12, 'font-family': '{self.font_family}'}},
                    'current' : {{'fill': '#3498db', 'color': 'white', 'font-weight': 'bold', 'font-family': '{self.font_family}'}},
                    'future' : {{'fill': '#FFFF99', 'font-family': '{self.font_family}'}},
                    'invalid': {{'fill': '#e74c3c', 'color': 'white', 'font-family': '{self.font_family}'}},
                    'approved' : {{'fill': '#27ae60', 'color': 'white', 'font-family': '{self.font_family}'}},
                    'rejected' : {{'fill': '#e74c3c', 'color': 'white', 'font-family': '{self.font_family}'}},
                }}
            }};
            
                console.log('开始解析流程图代码:', `{code}`);
                
                // 解析并绘制流程图
            var diagram = flowchart.parse(`{code}`);
            diagram.drawSVG('diagram', diagramOptions);
                
                console.log('流程图绘制完成');
            
        }} catch(e) {{
                console.error('FlowchartJS渲染错误:', e);
                createFallbackDiagram();
            }}
        }});
        
        // 全局错误处理
        window.addEventListener('error', function(e) {{
            console.error('页面错误:', e.error);
        }});
    </script>
</body>
</html>
"""
            return {"success": True, "data": html_content.encode('utf-8')}
        except Exception as e:
            return {"success": False, "error": f"FlowchartJS渲染错误: {str(e)}"}