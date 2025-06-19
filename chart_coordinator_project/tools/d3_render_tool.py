# Copyright 2025 Google LLC
# D3.js渲染工具 - 高级自定义可视化专家

import logging
import platform
from typing import Dict, Any, Optional

from google.genai import types
from .base_render_tool import BaseRenderTool

logger = logging.getLogger(__name__)


class D3RenderTool(BaseRenderTool):
    """📊 D3.js高级自定义可视化渲染工具"""
    
    def __init__(self):
        super().__init__(
            name="render_d3",
            description="📊 D3.js高级自定义可视化渲染工具：生成基于D3.js的高度自定义数据可视化HTML。专门用于复杂数据分析、交互式图表、定制化可视化。",
            supported_formats=["html"],
            default_format="html"
        )
        self._setup_chinese_fonts()
    
    def _setup_chinese_fonts(self):
        """🔧 设置智能中文字体支持"""
        logger.info("🎨 配置D3.js中文字体支持...")
        
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
        
        logger.info(f"✅ D3.js中文字体配置完成: {self.font_family}")
    
    def _get_declaration(self) -> Optional[types.FunctionDeclaration]:
        """🔧 定义D3.js渲染工具的精确函数声明"""
        return types.FunctionDeclaration(
            name=self.name,
            description=self.description,
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    'code': types.Schema(
                        type=types.Type.STRING,
                        description='要渲染的D3.js JavaScript代码或数据配置。支持完整的D3代码或JSON数据格式'
                    ),
                    'chart_type': types.Schema(
                        type=types.Type.STRING,
                        description='图表类型提示',
                        enum=['bar', 'line', 'scatter', 'pie', 'tree', 'network', 'map', 'heatmap', 'custom'],
                        default='custom'
                    ),
                    'title': types.Schema(
                        type=types.Type.STRING,
                        description='可视化标题',
                        default='D3.js 高级数据可视化'
                    ),
                    'width': types.Schema(
                        type=types.Type.INTEGER,
                        description='可视化宽度（像素）',
                        default=900
                    ),
                    'height': types.Schema(
                        type=types.Type.INTEGER,
                        description='可视化高度（像素）',
                        default=600
                    )
                },
                required=['code'],
            )
        )
    
    def _render_sync(self, code: str, output_format: str = "html", width: int = 900, height: int = 600, title: str = "D3.js 高级数据可视化", chart_type: str = "custom") -> Dict[str, Any]:
        """同步渲染D3.js高级可视化"""
        
        try:
            logger.info(f"🚀 开始渲染D3.js可视化 - 类型: {chart_type}, 尺寸: {width}x{height}")
            
            # 创建D3.js HTML页面
            html_content = self._create_d3_html(code, width, height, title)
            
            if not html_content:
                return {
                    "success": False,
                    "error": "生成D3.js HTML内容失败"
                }
            
            viz_bytes = html_content.encode('utf-8')
            
            logger.info(f"✅ D3.js高级可视化渲染成功，大小: {len(viz_bytes)} bytes")
            
            return {
                "success": True,
                "data": viz_bytes
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"D3.js渲染过程发生错误: {str(e)}"
            }
    
    def _create_d3_html(self, js_code: str, width: int, height: int, title: str) -> str:
        """创建D3.js HTML页面 - 简洁版本"""
        
        # 预处理用户代码：将body选择器替换为容器选择器
        import re
        processed_code = js_code
        # 确保代码在#d3-container内渲染，而不是整个body
        processed_code = re.sub(r'd3\.select\s*\(\s*["\']body["\']\s*\)', 'd3.select("#d3-container")', processed_code)
        processed_code = re.sub(r'd3\.select\s*\(\s*document\.body\s*\)', 'd3.select("#d3-container")', processed_code)
        
        # 🔧 调用代码质量预处理器
        processed_code = self._preprocess_user_code(processed_code)
        
        return f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{title}</title>
    
    <!-- D3.js 智能加载：本地优先，CDN备用 (保留了强大的插件加载能力) -->
    <script>
        // 🚀 增强型D3库智能加载系统 - 支持更多扩展库
        async function loadD3LibrariesWithFallback() {{
            const libraries = [
                {{
                    name: 'D3.js核心库',
                    sources: [
                        '/static/js/d3.v7.min.js',  // 本地资源（首选）
                        'https://d3js.org/d3.v7.min.js',
                        'https://cdn.jsdelivr.net/npm/d3@7/dist/d3.min.js',
                        'https://cdnjs.cloudflare.com/ajax/libs/d3/7.8.5/d3.min.js'
                    ],
                    check: () => typeof d3 !== 'undefined' && d3.version,
                    required: true
                }},
                {{
                    name: 'D3-Sankey桑基图库',
                    sources: [
                        '/static/js/d3-sankey.min.js',
                        'https://cdn.jsdelivr.net/npm/d3-sankey@0.12.3/dist/d3-sankey.min.js',
                    ],
                    check: () => d3 && d3.sankey,
                    optional: true
                }},
                {{
                    name: 'D3-Hierarchy层次结构库',
                    sources: [
                        '/static/js/d3-hierarchy.min.js',
                        'https://cdn.jsdelivr.net/npm/d3-hierarchy@3/dist/d3-hierarchy.min.js',
                    ],
                    check: () => d3 && d3.hierarchy,
                    optional: true
                }},
                {{
                    name: 'D3-Force力导向图库',
                    sources: [
                        '/static/js/d3-force.min.js',
                        'https://cdn.jsdelivr.net/npm/d3-force@3/dist/d3-force.min.js',
                    ],
                    check: () => d3 && d3.forceSimulation,
                    optional: true
                }},
                {{
                    name: 'D3-Geo地理库',
                    sources: [
                        '/static/js/d3-geo.min.js',
                        'https://cdn.jsdelivr.net/npm/d3-geo@3/dist/d3-geo.min.js',
                    ],
                    check: () => d3 && d3.geoPath,
                    optional: true
                }},
                {{
                    name: 'D3-Scale-Chromatic色彩库',
                    sources: [
                        '/static/js/d3-scale-chromatic.v1.min.js',
                        'https://d3js.org/d3-scale-chromatic.v1.min.js',
                    ],
                    check: () => d3 && d3.schemeCategory10,
                    optional: true
                }},
                {{
                    name: 'TopoJSON地理数据库',
                    sources: [
                        '/static/js/topojson.v3.min.js',
                        'https://d3js.org/topojson.v3.min.js',
                    ],
                    check: () => typeof topojson !== 'undefined',
                    optional: true
                }},
                {{
                    name: 'D3-Cloud词云库',
                    sources: [
                        '/static/js/d3-cloud.min.js',
                        'https://cdn.jsdelivr.net/gh/jasondavies/d3-cloud/build/d3.layout.cloud.js',
                    ],
                    check: () => d3 && d3.layout && d3.layout.cloud,
                    optional: true
                }},
                {{
                    name: 'D3-Hexbin六边形库',
                    sources: [
                        '/static/js/d3-hexbin.min.js',
                        'https://cdn.jsdelivr.net/npm/d3-hexbin@0.2.2/build/d3-hexbin.min.js',
                    ],
                    check: () => d3 && d3.hexbin,
                    optional: true
                }}
            ];
            
            let loadedCount = 0;
            let totalRequired = libraries.filter(lib => lib.required).length;
            let optionalLoaded = 0;
            
            for (const library of libraries) {{
                let loaded = false;
                
                for (const url of library.sources) {{
                    try {{
                        const isLocal = url.startsWith('/static/');
                        const timeout = isLocal ? 2000 : 8000;
                        
                        console.log(`🔄 尝试加载${{library.name}}: ${{url}} (${{isLocal ? '本地' : 'CDN'}})`);
                        
                        const script = document.createElement('script');
                        script.src = url;
                        script.crossOrigin = 'anonymous';
                        document.head.appendChild(script);
                        
                        await new Promise((resolve, reject) => {{
                            script.onload = resolve;
                            script.onerror = reject;
                            setTimeout(reject, timeout);
                        }});
                        
                        await new Promise(resolve => setTimeout(resolve, 100));
                        
                        if (library.check()) {{
                            console.log(`✅ ${{library.name}}加载成功: ${{url}} (${{isLocal ? '本地资源' : 'CDN资源'}})`);
                            loaded = true;
                            if (library.required) {{
                                loadedCount++;
                            }} else {{
                                optionalLoaded++;
                            }}
                            break;
                        }}
                    }} catch (e) {{
                        const isLocal = url.startsWith('/static/');
                        console.warn(`❌ ${{library.name}}加载失败: ${{url}} (${{isLocal ? '本地' : 'CDN'}})`);
                    }}
                }}
                
                if (!loaded && library.required) {{
                    console.error(`❌ 必需库${{library.name}}加载失败`);
                    return false;
                }}
                
                if (!loaded && library.optional) {{
                    console.warn(`⚠️ 可选库${{library.name}}加载失败，部分功能可能不可用`);
                }}
            }}
            
            console.log(`✅ D3.js库加载完成: ${{loadedCount}}/${{totalRequired}} 必需库, ${{optionalLoaded}} 个可选库已加载`);
            return loadedCount === totalRequired;
        }}
        
        document.addEventListener('DOMContentLoaded', async function() {{
            try {{
                const loadSuccess = await loadD3LibrariesWithFallback();
                if (loadSuccess) {{
                    console.log('🎉 D3.js环境准备就绪');
                    window.dispatchEvent(new Event('d3Ready'));
                }} else {{
                    console.error('❌ D3.js环境初始化失败');
                    document.getElementById('d3-container').innerHTML = 
                        '<div style="text-align:center;padding:50px;color:#666;">D3.js库加载失败，请检查网络连接</div>';
                }}
            }} catch (error) {{
                console.error('❌ D3.js库加载异常:', error);
                document.getElementById('d3-container').innerHTML = 
                    '<div style="text-align:center;padding:50px;color:#666;">D3.js初始化异常</div>';
            }}
        }});
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
        
        #d3-container {{
            width: {width}px;
            height: {height}px;
        }}
        
        .tooltip {{
            position: absolute;
            padding: 8px 12px;
            background: rgba(0, 0, 0, 0.8);
            color: white;
            border-radius: 4px;
            pointer-events: none;
            font-size: 12px;
            z-index: 1000;
            opacity: 0;
            transition: opacity 0.2s;
        }}
        
        /* D3.js 常用样式 - 支持中文 */
        .axis {{
            font-size: 12px;
            font-family: {self.font_family};
        }}
        
        .axis path,
        .axis line {{
            fill: none;
            stroke: #333;
            shape-rendering: crispEdges;
        }}
        
        .grid line {{
            stroke: lightgrey;
            stroke-opacity: 0.7;
            shape-rendering: crispEdges;
        }}
        
        text {{
            font-family: {self.font_family} !important;
        }}
    </style>
</head>
<body>
    <div id="d3-container">
        <!-- D3.js 可视化将在这里渲染 -->
    </div>
    
    <!-- 工具提示 -->
    <div class="tooltip" id="tooltip"></div>

    <script>
        // 🔧 增强型D3.js代码执行环境
        async function initializeD3Visualization() {{
            // 检查D3是否已加载
            if (typeof d3 === 'undefined') {{
                console.error('❌ D3.js库未加载，无法初始化可视化');
                document.getElementById('d3-container').innerHTML = 
                    '<div style="text-align:center;padding:50px;color:#666;">D3.js库加载失败</div>';
                return;
            }}
            
            console.log('🎨 开始初始化D3.js可视化');
            
            // 全局变量和辅助函数
            const container = d3.select("#d3-container");
            const width = {width};
            const height = {height};
            const margin = {{ top: 20, right: 20, bottom: 30, left: 50 }};
            const tooltip = d3.select("#tooltip");
        
            // 清除容器内容
            container.selectAll("*").remove();
        
            // 工具提示辅助函数
            function showTooltip(event, text) {{
                tooltip
                    .style("opacity", 1)
                    .html(text)
                    .style("left", (event.pageX + 10) + "px")
                    .style("top", (event.pageY - 10) + "px");
            }}
            
            function hideTooltip() {{
                tooltip.style("opacity", 0);
            }}
        
            // 颜色比例尺
            const colorScale = d3.scaleOrdinal(d3.schemeCategory10);
            
            // 🚀 增强：生成常用示例数据 (用于错误回退)
            const sampleData = {{
                nodes: d3.range(20).map(d => ({{ id: d, group: Math.floor(d / 5) }})),
                links: d3.range(15).map(() => ({{ source: Math.floor(Math.random() * 20), target: Math.floor(Math.random() * 20) }}))
            }};
        
            // 执行用户代码
            try {{
                const executeUserCode = async () => {{
                    {processed_code}
                }};
                
                await executeUserCode();
                console.log('✅ D3.js用户代码执行成功');
            }} catch (error) {{
                console.error('D3.js 用户代码执行错误:', error);
                
                // 创建SVG用于错误显示
                const svg = container.append("svg")
                    .attr("width", width)
                    .attr("height", height);
                
                // 显示错误信息
                svg.append("rect")
                    .attr("width", width)
                    .attr("height", height)
                    .attr("fill", "#f8f9fa");
                
                svg.append("text")
                    .attr("x", width / 2)
                    .attr("y", height / 2 - 20)
                    .attr("text-anchor", "middle")
                    .attr("font-size", "16px")
                    .attr("fill", "#dc3545")
                    .text("代码执行错误");
            
                svg.append("text")
                    .attr("x", width / 2)
                    .attr("y", height / 2)
                    .attr("text-anchor", "middle")
                    .attr("font-size", "12px")
                    .attr("fill", "#6c757d")
                    .text(`错误: ${{error.message}}`);
            }}
        }}
        
        // 监听D3库加载完成事件
        window.addEventListener('d3Ready', initializeD3Visualization);
        
        // 错误处理
        window.addEventListener('error', function(e) {{
            console.error('D3.js 页面错误:', e.error);
        }});
        
        console.log('📋 D3.js 可视化页面已准备完成');
    </script>
</body>
</html>
""" 
    
    def _preprocess_user_code(self, code: str) -> str:
        """🔧 预处理用户代码，解决大语言模型生成代码的常见质量问题"""
        import re
        
        processed = code
        
        # 1. 移除顶级async/await使用（因为我们在异步函数中执行）
        processed = re.sub(r'^(\s*)await\s+', r'\1', processed, flags=re.MULTILINE)
        
        # 2. 替换常见的错误选择器
        processed = re.sub(r'd3\.select\s*\(\s*["\']body["\']\s*\)', 'd3.select("#d3-container")', processed)
        processed = re.sub(r'd3\.select\s*\(\s*document\.body\s*\)', 'd3.select("#d3-container")', processed)
        
        # 3. 修复常见的SVG尺寸问题
        processed = re.sub(r'\.attr\s*\(\s*["\']width["\']\s*,\s*window\.innerWidth\s*\)', '.attr("width", width)', processed)
        processed = re.sub(r'\.attr\s*\(\s*["\']height["\']\s*,\s*window\.innerHeight\s*\)', '.attr("height", height)', processed)
        
        # 4. 确保SVG添加到正确的容器
        processed = re.sub(r'const\s+svg\s*=\s*d3\.select\s*\(\s*["\']svg["\']\s*\)', 'const svg = container.append("svg")', processed)
        
        # 5. 添加容器尺寸变量（如果用户代码中没有定义）
        if 'const width' not in processed and 'let width' not in processed and 'var width' not in processed:
            processed = f'const chartWidth = width;\nconst chartHeight = height;\n{processed}'
        
        # 6. 修复d3.json等异步函数调用
        processed = re.sub(r'd3\.json\s*\(\s*([^)]+)\s*\)\.then\s*\(\s*([^)]+)\s*\)', r'const data = await d3.json(\1); \2(data)', processed)
        processed = re.sub(r'd3\.csv\s*\(\s*([^)]+)\s*\)\.then\s*\(\s*([^)]+)\s*\)', r'const data = await d3.csv(\1); \2(data)', processed)
        
        # 7. 确保Sankey图使用正确的语法
        if 'd3.sankey' in processed:
            processed = re.sub(r'd3\.sankey\s*\(\s*\)', 'd3.sankey()', processed)
        
        # 8. 修复常见的数据访问问题
        processed = re.sub(r'data\.forEach\s*\(\s*function\s*\(\s*d\s*,\s*i\s*\)', 'sampleData.nodes.forEach(function(d, i)', processed)
        
        return processed