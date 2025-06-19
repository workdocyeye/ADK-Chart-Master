# Copyright 2025 Google LLC
# Dygraphs渲染工具 - 时间序列专家

import logging
import tempfile
import subprocess
import sys
import platform
from pathlib import Path
from typing import Dict, Any, Optional

from google.genai import types
from .base_render_tool import BaseRenderTool

logger = logging.getLogger(__name__)


class DygraphsRenderTool(BaseRenderTool):
    """📊 Dygraphs时间序列图表渲染工具"""
    
    def __init__(self):
        super().__init__(
            name="render_dygraphs",
            description="📊 Dygraphs时间序列图表渲染工具：生成高性能的交互式时间序列图表HTML文件。专门用于大规模时间序列数据、股票数据、监控指标等。",
            supported_formats=["html", "png"],
            default_format="html"
        )
        self._check_dependencies()
        self._setup_chinese_fonts()
    
    def _setup_chinese_fonts(self):
        """🔧 设置智能中文字体支持"""
        logger.info("🎨 配置Dygraphs中文字体支持...")
        
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
        
        logger.info(f"✅ 中文字体配置完成: {self.font_family}")
    
    def _get_declaration(self) -> Optional[types.FunctionDeclaration]:
        """🔧 定义Dygraphs渲染工具的精确函数声明"""
        return types.FunctionDeclaration(
            name=self.name,
            description=self.description,
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    'code': types.Schema(
                        type=types.Type.STRING,
                        description='要渲染的Dygraphs代码。可以是Python代码（生成数据和HTML）或直接的HTML+JavaScript代码'
                    ),
                    'output_format': types.Schema(
                        type=types.Type.STRING,
                        description='输出格式。html生成交互式图表，png生成静态图片（需要selenium）',
                        enum=['html', 'png'],
                        default='html'
                    ),
                    'title': types.Schema(
                        type=types.Type.STRING,
                        description='图表文件名称（不含扩展名）',
                        default='dygraphs_chart'
                    ),
                    'width': types.Schema(
                        type=types.Type.INTEGER,
                        description='图表宽度（像素）',
                        default=800
                    ),
                    'height': types.Schema(
                        type=types.Type.INTEGER,
                        description='图表高度（像素）',
                        default=400
                    )
                },
                required=['code'],
            )
        )
    
    def _check_dependencies(self):
        """🔧 Dygraphs依赖检查"""
        self._dygraphs_available = True  # Dygraphs是JavaScript库，不需要Python依赖
        
        # 检查Python数据处理依赖（可选）
        try:
            import pandas
            logger.info(f"✅ pandas (数据处理支持): {pandas.__version__}")
            self._pandas_support = True
        except ImportError:
            logger.info("ℹ️ pandas未安装，仅支持JavaScript代码")
            self._pandas_support = False
        
        # 检查PNG输出依赖（可选）
        try:
            import selenium
            logger.info(f"✅ selenium (PNG输出支持): {selenium.__version__}")
            self._png_support = True
        except ImportError:
            logger.info("ℹ️ selenium未安装，仅支持HTML输出")
            self._png_support = False
        
        logger.info("✅ Dygraphs渲染工具检查完成")
    
    def _render_sync(self, code: str, output_format: str, width: int, height: int) -> Dict[str, Any]:
        """同步渲染Dygraphs时间序列图表"""
        
        if output_format == "png" and not self._png_support:
            return {
                "success": False,
                "error": "PNG输出需要selenium和chromedriver",
                "suggestion": "请安装: pip install selenium chromedriver-autoinstaller 或使用HTML格式"
            }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            try:
                # 判断是Python代码还是HTML代码
                if self._is_python_code(code):
                    # 处理Python代码
                    code_file = temp_path / "dygraphs_code.py"
                    output_file = temp_path / f"output.{output_format}"
                    
                    processed_code = self._preprocess_python_code(code, output_file, output_format, width, height)
                    code_file.write_text(processed_code, encoding='utf-8')
                    
                    logger.info(f"🚀 执行Python代码生成Dygraphs图表...")
                    
                    result = subprocess.run(
                        [sys.executable, str(code_file)],
                        capture_output=True,
                        text=True,
                        timeout=60,
                        cwd=temp_dir,
                        encoding='utf-8',
                        errors='replace'
                    )
                    
                    if result.returncode != 0:
                        return {
                            "success": False,
                            "error": f"Python代码执行失败:\n{result.stderr}"
                        }
                else:
                    # 处理HTML代码
                    output_file = temp_path / f"output.{output_format}"
                    html_content = self._process_html_code(code, width, height)
                    
                    # 检查是否是需要Python处理的模板
                    if html_content.startswith("PYTHON_TEMPLATE:"):
                        # 移除标记前缀
                        template_code = html_content[16:]
                        
                        # 创建Python代码来处理模板
                        python_code = f"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# 生成示例数据（如果用户代码中没有定义data）
dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
visits = np.random.randint(1000, 5000, size=len(dates))
data = pd.DataFrame({{'Date': dates, 'Visits': visits}})

# 转换为Dygraphs所需的格式
data['Date'] = data['Date'].astype(str)

# 处理模板
template = '''{template_code}'''

# 替换模板中的Python表达式
import re
def replace_data_expressions(match):
    expr = match.group(0)[1:-1]  # 移除花括号
    try:
        return str(eval(expr))
    except:
        return data.to_csv(index=False, header=False)

pattern = r'\\{{data\\.[^}}]*\\}}'
final_html = re.sub(pattern, replace_data_expressions, template)

# 保存HTML文件
with open(r"{output_file}", 'w', encoding='utf-8') as f:
    f.write(final_html)
"""
                        
                        # 执行Python代码
                        code_file = temp_path / "template_processor.py"
                        code_file.write_text(python_code, encoding='utf-8')
                        
                        result = subprocess.run(
                            [sys.executable, str(code_file)],
                            capture_output=True,
                            text=True,
                            timeout=60,
                            cwd=temp_dir,
                            encoding='utf-8',
                            errors='replace'
                        )
                        
                        if result.returncode != 0:
                            return {
                                "success": False,
                                "error": f"模板处理失败:\\n{result.stderr}"
                            }
                    else:
                        # 普通HTML处理
                        if output_format == "html":
                            output_file.write_text(html_content, encoding='utf-8')
                        else:  # PNG
                            temp_html = temp_path / "temp.html"
                            temp_html.write_text(html_content, encoding='utf-8')
                            self._html_to_png(temp_html, output_file, width, height)
                
                if not output_file.exists():
                    return {
                        "success": False,
                        "error": "未生成输出文件"
                    }
                
                if output_format == "html":
                    content = output_file.read_text(encoding='utf-8')
                    chart_bytes = content.encode('utf-8')
                else:
                    chart_bytes = output_file.read_bytes()
                
                if len(chart_bytes) == 0:
                    return {
                        "success": False,
                        "error": "生成的文件为空"
                    }
                
                logger.info(f"✅ Dygraphs图表渲染成功，大小: {len(chart_bytes)} bytes")
                
                return {
                    "success": True,
                    "data": chart_bytes
                }
                
            except subprocess.TimeoutExpired:
                return {
                    "success": False,
                    "error": "图表渲染超时（60秒）"
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": f"渲染过程发生错误: {str(e)}"
                }
    
    def _is_python_code(self, code: str) -> bool:
        """判断是否为Python代码"""
        python_indicators = ['import ', 'def ', 'pandas', 'numpy', 'print(', 'pd.']
        return any(indicator in code for indicator in python_indicators)
    
    def _preprocess_python_code(self, code: str, output_file: Path, output_format: str, width: int, height: int) -> str:
        """预处理Python代码"""
        
        # 添加必要的导入
        imports = []
        if 'import pandas' not in code and 'import pd' not in code:
            imports.append("import pandas as pd")
        if 'import numpy' not in code:
            imports.append("import numpy as np")
        
        imports_str = '\n'.join(imports) + '\n' if imports else ''
        
        # 创建带中文字体支持的HTML模板和保存逻辑
        save_logic = f"""
# 检查用户代码中是否已经定义了html_template变量
if 'html_template' in locals():
    # 用户已经定义了完整的HTML模板，直接使用
    final_html = html_template
else:
    # 用户没有定义HTML模板，使用默认模板
    # 假设用户定义了data变量（DataFrame或CSV字符串）
    if 'data' in locals():
        if hasattr(data, 'to_csv'):
            # DataFrame格式
            csv_data = data.to_csv(index=False)
        else:
            # 字符串格式
            csv_data = str(data)
    else:
        csv_data = "Date,Value\\n2023-01-01,100\\n2023-01-02,120"
    
    final_html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Dygraphs Time Series Chart</title>
    <script src="https://dygraphs.com/dygraph-combined.js"></script>
    <style>
        body {{ 
            font-family: {self.font_family}; 
            margin: 20px; 
            background-color: #fafafa;
        }}
        #graphdiv {{ 
            width: {width}px; 
            height: {height}px; 
            font-family: {self.font_family};
        }}
        h2 {{
            color: #333;
            font-family: {self.font_family};
        }}
        .dygraph-legend {{
            font-family: {self.font_family} !important;
        }}
        .dygraph-axis-label {{
            font-family: {self.font_family} !important;
        }}
        .dygraph-title {{
            font-family: {self.font_family} !important;
        }}
    </style>
</head>
<body>
    <h2>时间序列图表</h2>
    <div id="graphdiv"></div>
    <script>
        const csvData = `{{csv_data}}`;
        new Dygraph(
            document.getElementById("graphdiv"),
            csvData,
            {{
                xlabel: 'Time',
                ylabel: 'Value',
                title: 'Time Series Chart',
                legend: 'always',
                showRangeSelector: true,
                rangeSelectorHeight: 30,
                rangeSelectorPlotStrokeColor: '#808FAB',
                rangeSelectorPlotFillColor: '#A7B1C4',
                axisLabelFontSize: 12,
                titleHeight: 28
            }}
        );
    </script>
</body>
</html>'''

# 保存HTML文件
with open(r"{output_file}", 'w', encoding='utf-8') as f:
    f.write(final_html)
"""
        
        processed_code = f"""
{imports_str}

# 用户代码
{code}

# 自动保存逻辑
{save_logic}
"""
        return processed_code
    
    def _process_html_code(self, code: str, width: int, height: int) -> str:
        """处理HTML代码（支持中文字体）"""
        
        if '<html>' in code.lower():
            # 完整的HTML，注入中文字体支持
            if '<style>' in code:
                # 在现有样式中添加中文字体
                style_insert = f"""
        body, div, span, h1, h2, h3, h4, h5, h6 {{
            font-family: {self.font_family} !important;
        }}
        .dygraph-legend, .dygraph-axis-label, .dygraph-title {{
            font-family: {self.font_family} !important;
        }}
"""
                code = code.replace('<style>', f'<style>{style_insert}')
            else:
                # 添加新的样式块
                style_block = f"""
    <style>
        body, div, span, h1, h2, h3, h4, h5, h6 {{
            font-family: {self.font_family} !important;
        }}
        .dygraph-legend, .dygraph-axis-label, .dygraph-title {{
            font-family: {self.font_family} !important;
        }}
    </style>
"""
                code = code.replace('<head>', f'<head>{style_block}')
            
            # 确保有正确的字符编码
            if '<meta charset=' not in code.lower():
                code = code.replace('<head>', '<head>\n    <meta charset="UTF-8">')
            
            # 修复JavaScript中的Python格式化语法问题
            # 查找并替换 {data.to_csv(...)} 这样的Python表达式
            import re
            
            # 匹配 {data.to_csv(...)} 模式
            pattern = r'\{data\.to_csv\([^}]*\)\}'
            if re.search(pattern, code):
                # 如果发现这种模式，说明这是一个需要在Python中处理的模板
                # 我们需要提取数据并替换这些占位符
                # 这种情况下，我们返回一个标记，让Python代码处理器知道需要特殊处理
                return "PYTHON_TEMPLATE:" + code
            
            return code
        else:
            # 只是JavaScript片段，需要包装并添加中文字体支持
            return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Dygraphs Chart</title>
    <script src="https://dygraphs.com/dygraph-combined.js"></script>
    <style>
        body {{ 
            font-family: {self.font_family}; 
            margin: 20px; 
            background-color: #fafafa;
        }}
        #graphdiv {{ 
            width: {width}px; 
            height: {height}px; 
            font-family: {self.font_family};
        }}
        .dygraph-legend {{
            font-family: {self.font_family} !important;
        }}
        .dygraph-axis-label {{
            font-family: {self.font_family} !important;
        }}
        .dygraph-title {{
            font-family: {self.font_family} !important;
        }}
    </style>
</head>
<body>
    <div id="graphdiv"></div>
    <script>
        {code}
    </script>
</body>
</html>
"""
    
    def _html_to_png(self, html_file: Path, output_file: Path, width: int, height: int):
        """将HTML转换为PNG"""
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument(f"--window-size={width},{height}")
        
        driver = webdriver.Chrome(options=chrome_options)
        try:
            driver.get(f"file://{html_file}")
            driver.set_window_size(width, height)
            import time
            time.sleep(2)  # 等待图表加载
            driver.save_screenshot(str(output_file))
        finally:
            driver.quit() 