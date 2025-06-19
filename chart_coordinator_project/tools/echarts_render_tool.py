# Copyright 2025 Google LLC
# echarts渲染工具 - 完整实现

import logging
import os
import tempfile
import subprocess
import json
from pathlib import Path
from typing import Dict, Any, Optional

from google.genai import types
from .base_render_tool import BaseRenderTool

logger = logging.getLogger(__name__)

 
class EChartsRenderTool(BaseRenderTool):
    """📈 Apache ECharts企业级图表渲染工具"""
    
    def __init__(self):
        super().__init__(
            name="render_echarts",
            description="使用ECharts创建企业级图表。支持柱状图、折线图、饼图等多种图表类型",
            supported_formats=["html", "png"],
            default_format="html"
        )
        self._check_dependencies()
    
    def _get_declaration(self) -> Optional[types.FunctionDeclaration]:
        """🔧 定义ECharts渲染工具的函数声明"""
        return types.FunctionDeclaration(
            name=self.name,
            description="使用ECharts创建企业级图表。支持柱状图、折线图、饼图等多种图表类型",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    'config': types.Schema(
                        type=types.Type.STRING,
                        description='ECharts配置JavaScript代码。例如：{title: {text: "标题"}, xAxis: {data: ["A","B"]}, series: [{type: "bar", data: [1,2]}]}'
                    ),
                    'output_format': types.Schema(
                        type=types.Type.STRING,
                        description='输出格式：html(默认,交互式)、png',
                        enum=['html', 'png'],
                        default='html'
                    ),
                    'title': types.Schema(
                        type=types.Type.STRING,
                        description='图表文件名称',
                        default='echarts_chart'
                    ),
                    'width': types.Schema(
                        type=types.Type.INTEGER,
                        description='图表宽度（像素）',
                        default=800
                    ),
                    'height': types.Schema(
                        type=types.Type.INTEGER,
                        description='图表高度（像素）',
                        default=600
                    )
                },
                required=['config'],
            )
        )
    
    async def run_async(self, *, args: Dict[str, Any], tool_context) -> Dict[str, Any]:
        """
        运行ECharts渲染工具的主要方法
        
        ECharts工具使用config参数而不是code参数，但需要适配BaseRenderTool的标准流程
        以确保正确保存artifact并在ADK Web界面中显示链接
        
        Args:
            args: 工具参数
            tool_context: 工具上下文
            
        Returns:
            包含渲染结果的字典
        """
        # 提取ECharts专用的config参数
        config = args.get("config", "")
        
        if not config or not config.strip():
            return {
                "success": False,
                "error": "ECharts配置不能为空",
                "message": "❌ 请提供ECharts配置对象",
                "example": "例如：{title: {text: '标题'}, xAxis: {data: ['A','B']}, series: [{type: 'bar', data: [1,2]}]}"
            }
        
        # 将config映射为code，以适配BaseRenderTool的标准流程
        # 这样可以使用BaseRenderTool的artifact保存机制
        adapted_args = args.copy()
        adapted_args["code"] = config  # 将config映射为code参数
        
        # 调用父类的run_async方法，它会：
        # 1. 调用我们的_render_sync方法
        # 2. 保存结果为artifact
        # 3. 在ADK Web界面中显示可点击的链接
        return await super().run_async(args=adapted_args, tool_context=tool_context)
    

    
    def _check_dependencies(self):
        """🔧 增强的ECharts依赖检查"""
        self._echarts_available = False
        self._node_available = False
        self._html_mode_available = True  # HTML模式始终可用
        
        # 检查Node.js
        self._check_nodejs()
        
        # 检查ECharts模块
        if self._node_available:
            self._check_echarts_modules()
        else:
            # 即使Node.js不可用，HTML模式仍然可用
            logger.info("✅ ECharts HTML模式可用（无需Node.js，使用CDN加载）")
    
    def _check_nodejs(self):
        """检查Node.js环境"""
        try:
            result = subprocess.run(
                ["node", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                version = result.stdout.strip()
                logger.info(f"✅ Node.js: {version}")
                self._node_available = True
            else:
                logger.warning("❌ Node.js未安装或不可用")
                self._show_nodejs_installation_help()
                
        except (FileNotFoundError, subprocess.TimeoutExpired) as e:
            logger.warning(f"❌ Node.js检查失败: {e}")
            self._show_nodejs_installation_help()
    
    def _check_echarts_modules(self):
        """检查ECharts相关npm模块"""
        required_packages = {
            'echarts': 'ECharts核心库',
            'jsdom': 'DOM环境模拟'
        }
        
        optional_packages = {
            'canvas': 'Node.js Canvas支持（可选，Windows需要C++环境）'
        }
        
        missing_packages = []
        self._canvas_available = False
        
        # 检查必需包
        for package, desc in required_packages.items():
            if self._check_npm_package(package):
                logger.info(f"✅ {package} ({desc}): 已安装")
            else:
                logger.warning(f"❌ {package} ({desc}): 未安装")
                missing_packages.append(package)
        
        # 检查可选包
        for package, desc in optional_packages.items():
            if self._check_npm_package(package):
                logger.info(f"✅ {package} ({desc}): 已安装")
                if package == 'canvas':
                    self._canvas_available = True
            else:
                logger.info(f"ℹ️ {package} ({desc}): 未安装（可选）")
        
        if missing_packages:
            logger.warning(f"🔧 缺少必需npm包: {', '.join(missing_packages)}")
            self._show_npm_installation_help(missing_packages)
            self._echarts_available = False
        else:
            if self._canvas_available:
                logger.info("✅ ECharts渲染工具所有依赖检查通过")
            else:
                logger.info("✅ ECharts渲染工具基础依赖检查通过（canvas可选包未安装，仅支持SVG输出）")
            self._echarts_available = True
    
    def _check_npm_package(self, package_name: str) -> bool:
        """检查npm包是否已安装"""
        try:
            # 获取项目根目录
            project_root = Path(__file__).parent.parent
            
            # 使用Node.js直接检查模块是否可用（在项目目录下运行）
            result = subprocess.run(
                ["node", "-e", f"try {{ require('{package_name}'); process.exit(0); }} catch(e) {{ process.exit(1); }}"],
                capture_output=True,
                text=True,
                timeout=10,
                cwd=str(project_root)  # 在项目根目录下运行
            )
            return result.returncode == 0
        except Exception as e:
            logger.debug(f"检查npm包 {package_name} 时出错: {e}")
            return False
    
    def _show_nodejs_installation_help(self):
        """显示Node.js安装帮助"""
        help_text = """
🔧 Node.js安装指南：

Windows:
1. 访问 https://nodejs.org/
2. 下载LTS版本
3. 运行安装程序

macOS:
brew install node

Linux:
# Ubuntu/Debian
sudo apt update && sudo apt install nodejs npm

# CentOS/RHEL
sudo yum install nodejs npm

验证安装：
node --version
npm --version
        """
        logger.info(help_text)
    
    def _show_npm_installation_help(self, missing_packages: list):
        """显示npm包安装帮助"""
        packages_str = ' '.join(missing_packages)
        help_text = f"""
🔧 ECharts npm包安装指南：

全局安装（推荐）：
npm install -g {packages_str}

本地安装：
npm install {packages_str}

注意事项：
- canvas包可能需要系统依赖，Windows用户可能需要windows-build-tools
- 如果安装失败，可尝试：npm install --canvas_binary_host_mirror=https://npm.taobao.org/mirrors/node-canvas-prebuilt/
        """
        logger.info(help_text)
    
    def _render_sync(self, code: str, output_format: str, width: int, height: int) -> Dict[str, Any]:
        """同步渲染ECharts图表"""
        
        # code参数实际上是ECharts的config
        config = code
        
        # 如果输出格式是HTML，直接生成HTML文件（不需要Node.js）
        if output_format == 'html':
            return self._generate_html_output(config, width, height)
        
        # PNG输出需要Node.js环境
        if not self._node_available:
            return {
                "success": False,
                "error": "Node.js环境不可用（PNG输出需要）",
                "installation_guide": "请先安装Node.js: https://nodejs.org/",
                "suggestion": "建议使用HTML格式输出，或安装Node.js后使用PNG格式"
            }
            
        if not self._echarts_available:
            return {
                "success": False,
                "error": "ECharts依赖不可用（PNG输出需要）",
                "installation_guide": "npm install -g echarts canvas jsdom",
                "suggestion": "建议使用HTML格式输出，或安装依赖后使用PNG格式"
            }
        
        try:
            # 设置默认参数（简化后）
            theme = 'default'
            background_color = 'white'
            
            # 在项目根目录创建脚本和输出文件
            project_root = Path(__file__).parent.parent  # 项目根目录
            
            # 创建临时文件名（使用时间戳避免冲突）
            import time
            timestamp = str(int(time.time() * 1000))
            script_file = project_root / f"temp_render_echarts_{timestamp}.js"
            output_file = project_root / f"temp_output_{timestamp}.{output_format}"
            
            try:
                # 生成Node.js渲染脚本
                script_content = self._generate_render_script(config, output_file, output_format, width, height, theme, background_color)
                script_file.write_text(script_content, encoding='utf-8')
                
                logger.info(f"🚀 执行ECharts渲染...")
                
                # 执行Node.js脚本（在项目根目录下运行）
                result = subprocess.run(
                    ["node", str(script_file)],
                    capture_output=True,
                    text=True,
                    timeout=60,
                    cwd=str(project_root),  # 在项目根目录运行
                    encoding='utf-8',
                    errors='replace'
                )
                
                if result.returncode != 0:
                    return {
                        "success": False,
                        "error": f"Node.js脚本执行失败:\n{result.stderr}"
                    }
                
                if not output_file.exists():
                    return {
                        "success": False,
                        "error": "脚本执行完成但未生成图片文件"
                    }
                
                image_bytes = output_file.read_bytes()
                
                if len(image_bytes) == 0:
                    return {
                        "success": False,
                        "error": "生成的图片文件为空"
                    }
                
                logger.info(f"✅ ECharts图表渲染成功，大小: {len(image_bytes)} bytes")
                
                return {
                    "success": True,
                    "data": image_bytes
                }
                
            except subprocess.TimeoutExpired:
                return {
                    "success": False,
                    "error": "脚本执行超时（60秒），请检查配置复杂度"
                }
            except Exception as e:
                logger.error(f"❌ ECharts渲染过程中出现异常: {e}", exc_info=True)
                return {
                    "success": False,
                    "error": f"渲染过程异常: {e}"
                }
            finally:
                # 清理临时文件
                try:
                    if script_file.exists():
                        script_file.unlink()
                    if output_file.exists():
                        output_file.unlink()
                except:
                    pass  # 忽略清理错误
                    
        except Exception as e:
            logger.error(f"❌ ECharts渲染初始化失败: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"渲染初始化失败: {e}"
            }
    
    def _generate_render_script(self, config: str, output_file: Path, output_format: str, width: int, height: int, theme: str, background_color: str) -> str:
        """生成Node.js渲染脚本"""
        
        # 预处理配置
        processed_config = self._preprocess_config(config)
        
        # 简化模块加载：使用项目本地的node_modules
        module_setup = """
// 加载模块（从项目node_modules）
const echarts = require('echarts');
const fs = require('fs');

// 检查是否有canvas支持
let createCanvas;
try {
    createCanvas = require('canvas').createCanvas;
} catch (e) {
    console.log('Canvas模块未安装，将使用SVG输出');
    createCanvas = null;
}

// 加载JSDOM
const JSDOM = require('jsdom').JSDOM;"""
        
        script = f"""
{module_setup}

// 创建图表实例
let chart;
if (createCanvas && '{output_format}' === 'png') {{
    // 使用Canvas渲染PNG
    const canvas = createCanvas({width}, {height});
    echarts.setCanvasCreator(() => canvas);
    chart = echarts.init(canvas, '{theme}', {{
        renderer: 'canvas',
        width: {width},
        height: {height}
    }});
}} else {{
    // 使用SVG渲染（无需Canvas）
    const dom = new JSDOM('<!DOCTYPE html><html><body><div id="chart" style="width:{width}px;height:{height}px;"></div></body></html>');
    global.window = dom.window;
    global.document = dom.window.document;
    global.navigator = dom.window.navigator;
    
    const container = dom.window.document.getElementById('chart');
    chart = echarts.init(container, '{theme}', {{
        renderer: 'svg',
        width: {width},
        height: {height}
    }});
}}

// 配置选项
const option = {processed_config};

// 设置背景色
if (option.backgroundColor === undefined) {{
    option.backgroundColor = '{background_color}';
}}

try {{
    // 设置配置并渲染
    chart.setOption(option);
    
    // 等待渲染完成
    setTimeout(() => {{
        try {{
            let buffer;
            
            if ('{output_format}' === 'svg' || !createCanvas) {{
                // SVG输出
                const svgStr = chart.renderToSVGString();
                buffer = Buffer.from(svgStr, 'utf8');
            }} else {{
                // PNG输出（需要Canvas支持）
                // 在Canvas模式下，chart.getDom()返回canvas元素
                const canvas = chart.getDom();
                if (canvas && typeof canvas.toBuffer === 'function') {{
                    buffer = canvas.toBuffer('image/png');
                }} else {{
                    throw new Error('Canvas渲染失败，请尝试SVG格式');
                }}
            }}
            
            fs.writeFileSync('{output_file}', buffer);
            console.log('ECharts图表渲染完成');
            process.exit(0);
        }} catch (error) {{
            console.error('保存文件失败:', error);
            process.exit(1);
        }}
    }}, 100);
    
}} catch (error) {{
    console.error('ECharts渲染失败:', error);
    process.exit(1);
}}
"""
        
        return script
    
    def _preprocess_config(self, config: str) -> str:
        """预处理ECharts配置"""
        config = config.strip()
        
        # 移除代码块标记
        if config.startswith("```javascript") or config.startswith("```js"):
            config = config[config.index('\n')+1:]
        elif config.startswith("```json"):
            config = config[7:]
        elif config.startswith("```"):
            config = config[3:]
        
        if config.endswith("```"):
            config = config[:-3]
        
        config = config.strip()
        
        # 尝试解析为JSON
        try:
            # 如果是JSON字符串，验证格式
            json.loads(config)
            return config
        except:
            # 如果不是JSON，假设是JavaScript对象字面量
            # 简单处理：确保它看起来像一个对象
            if not config.startswith('{'):
                config = '{' + config + '}'
            return config
    
    def _generate_html_output(self, config: str, width: int, height: int) -> Dict[str, Any]:
        """生成HTML输出文件"""
        try:
            title = 'echarts_chart'  # 使用默认标题
            
            # 预处理配置
            processed_config = self._preprocess_config(config)
            
            # 生成HTML内容
            html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{title} - ECharts 图表</title>
    <!-- 引入 ECharts 文件 -->
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.6.0/dist/echarts.min.js"></script>
    <style>
        body {{
            margin: 0;
            padding: 20px;
            font-family: Arial, sans-serif;
            background-color: #f5f5f5;
        }}
        .chart-container {{
            width: {width}px;
            height: {height}px;
            margin: 20px auto;
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            border: 1px solid #e1e1e1;
        }}
        .chart-info {{
            text-align: center;
            margin-bottom: 20px;
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="chart-info">
        <h2>{title}</h2>
        <p>使用 ECharts 生成的交互式图表</p>
    </div>
    
    <!-- ECharts 图表容器 -->
    <div id="chart" class="chart-container"></div>

    <script type="text/javascript">
        // 基于准备好的dom，初始化echarts实例
        var myChart = echarts.init(document.getElementById('chart'));

        // 图表配置
        var option = {processed_config};

        // 使用刚指定的配置项和数据显示图表
        myChart.setOption(option);

        // 自适应屏幕
        window.addEventListener('resize', function() {{
            myChart.resize();
        }});
        
        // 添加加载完成提示
        console.log('ECharts图表已加载完成');
    </script>
</body>
</html>"""

            # 直接返回HTML内容作为字节数据，让BaseRenderTool处理保存为Artifact
            logger.info(f"✅ ECharts HTML图表生成成功")
            
            # 返回标准的ADK格式：data字节
            return {
                "success": True,
                "data": html_content.encode('utf-8')
            }
            
        except Exception as e:
            logger.error(f"❌ 生成HTML文件失败: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"生成HTML文件失败: {e}"
            } 