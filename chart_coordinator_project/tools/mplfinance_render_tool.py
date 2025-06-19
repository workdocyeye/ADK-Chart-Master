# Copyright 2025 Google LLC
# mplfinance渲染工具 - 金融图表专家

import logging
import tempfile
import subprocess
import sys
import platform
import re
from pathlib import Path
from typing import Dict, Any, Optional

from google.genai import types
from .base_render_tool import BaseRenderTool

logger = logging.getLogger(__name__)


class MplfinanceRenderTool(BaseRenderTool):
    """📈 Python mplfinance金融图表渲染工具"""
    
    def __init__(self):
        super().__init__(
            name="render_mplfinance",
            description="📈 Python mplfinance金融图表渲染工具：将Python mplfinance代码转换为金融图表图片。专门用于股票K线图、技术指标、量价分析等金融数据可视化。",
            supported_formats=["png", "svg", "pdf"],
            default_format="png"
        )
        self._check_dependencies()
    
    def _get_declaration(self) -> Optional[types.FunctionDeclaration]:
        """🔧 定义mplfinance渲染工具的精确函数声明"""
        return types.FunctionDeclaration(
            name=self.name,
            description=self.description,
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    'code': types.Schema(
                        type=types.Type.STRING,
                        description='要渲染的Python mplfinance代码。应该包含完整的金融图表创建逻辑，包括数据准备、K线图绘制、技术指标添加等'
                    ),
                    'output_format': types.Schema(
                        type=types.Type.STRING,
                        description='输出图片格式。png适合一般使用，svg适合矢量图，pdf适合报告',
                        enum=['png', 'svg', 'pdf'],
                        default='png'
                    ),
                    'title': types.Schema(
                        type=types.Type.STRING,
                        description='图表文件名称（不含扩展名）',
                        default='mplfinance_chart'
                    ),
                    'width': types.Schema(
                        type=types.Type.INTEGER,
                        description='图片宽度（像素）',
                        default=1200
                    ),
                    'height': types.Schema(
                        type=types.Type.INTEGER,
                        description='图片高度（像素）',
                        default=800
                    ),
                    'dpi': types.Schema(
                        type=types.Type.INTEGER,
                        description='图片分辨率（DPI）',
                        default=150
                    )
                },
                required=['code'],
            )
        )
    
    def _check_dependencies(self):
        """🔧 mplfinance依赖检查"""
        logger.info("🔍 检查mplfinance依赖...")
        
        self._mplfinance_available = False
        self._missing_deps = []
        
        # 检查核心依赖
        dependencies = [
            {
                'name': 'mplfinance',
                'import_name': 'mplfinance',
                'description': '金融图表库',
                'required': True,
                'install_cmd': 'pip install mplfinance'
            },
            {
                'name': 'pandas',
                'import_name': 'pandas',
                'description': '数据分析库',
                'required': True,
                'install_cmd': 'pip install pandas'
            },
            {
                'name': 'matplotlib',
                'import_name': 'matplotlib',
                'description': '绘图基础库',
                'required': True,
                'install_cmd': 'pip install matplotlib'
            },
            {
                'name': 'numpy',
                'import_name': 'numpy',
                'description': '数值计算库',
                'required': True,
                'install_cmd': 'pip install numpy'
            }
        ]
        
        for dep in dependencies:
            try:
                module = __import__(dep['import_name'])
                version = getattr(module, '__version__', '未知版本')
                logger.info(f"✅ {dep['name']} ({dep['description']}): {version}")
                
                if dep['name'] == 'mplfinance':
                    self._mplfinance_available = True
                    
            except ImportError:
                logger.warning(f"❌ {dep['name']} ({dep['description']}): 未安装")
                if dep['required']:
                    self._missing_deps.append(dep)
        
        if self._missing_deps:
            logger.warning(f"🔧 缺少必需依赖: {[dep['name'] for dep in self._missing_deps]}")
            logger.info(self._get_installation_guide())
        else:
            logger.info("✅ mplfinance渲染工具依赖检查通过")
            self._test_mplfinance_functionality()
    
    def _get_installation_guide(self) -> str:
        """获取安装指南"""
        if not self._missing_deps:
            return "所有依赖已安装"
        
        guide = "📦 mplfinance依赖安装指南:\n"
        guide += "=" * 40 + "\n"
        
        for dep in self._missing_deps:
            guide += f"• {dep['name']}: {dep['install_cmd']}\n"
        
        # 一键安装命令
        install_cmds = [dep['install_cmd'] for dep in self._missing_deps]
        if platform.system() == "Windows":
            guide += f"\n一键安装: {'; '.join(install_cmds)}\n"
        else:
            guide += f"\n一键安装: {' && '.join(install_cmds)}\n"
        
        guide += "\n🔗 更多信息:\n"
        guide += "• mplfinance文档: https://github.com/matplotlib/mplfinance\n"
        guide += "• mplfinance示例: https://github.com/matplotlib/mplfinance/tree/master/examples\n"
        
        return guide
    
    def _test_mplfinance_functionality(self):
        """测试mplfinance功能"""
        try:
            import mplfinance as mpf
            import pandas as pd
            import numpy as np
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
            
            # 创建测试数据
            dates = pd.date_range('2023-01-01', periods=20, freq='D')
            prices = 100 + np.cumsum(np.random.randn(20) * 0.5)
            
            data = pd.DataFrame({
                'Open': prices + np.random.randn(20) * 0.1,
                'High': prices + np.abs(np.random.randn(20)) * 0.2,
                'Low': prices - np.abs(np.random.randn(20)) * 0.2,
                'Close': prices,
                'Volume': np.random.randint(1000, 10000, 20)
            }, index=dates)
            
            # 确保OHLC数据逻辑正确
            data['High'] = np.maximum(data[['Open', 'Close']].max(axis=1), data['High'])
            data['Low'] = np.minimum(data[['Open', 'Close']].min(axis=1), data['Low'])
            
            # 测试基本绘图
            fig, ax = plt.subplots(figsize=(2, 2))
            
            # 使用mplfinance绘制简单K线图
            mpf.plot(data, type='candle', ax=ax, volume=False, show_nontrading=False)
            
            # 测试保存到内存
            import io
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png')
            buffer.seek(0)
            
            if len(buffer.getvalue()) > 0:
                logger.info("✅ mplfinance功能测试成功")
            else:
                logger.warning("⚠️ mplfinance功能测试失败 - 生成空文件")
                
            plt.close(fig)
            buffer.close()
            
        except Exception as e:
            logger.error(f"❌ mplfinance功能测试失败: {e}")
            self._mplfinance_available = False
    
    def _render_sync(self, code: str, output_format: str, width: int, height: int, **kwargs) -> Dict[str, Any]:
        """同步渲染mplfinance金融图表"""
        
        if not self._mplfinance_available:
            missing_deps = ["mplfinance", "pandas", "matplotlib", "numpy"]
            return {
                "success": False,
                "error": "mplfinance依赖不可用",
                "installation_guide": self._get_installation_guide(),
                "suggestion": "请先安装依赖: pip install mplfinance pandas matplotlib numpy"
            }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            try:
                code_file = temp_path / "finance_code.py"
                output_file = temp_path / f"output.{output_format}"
                
                # 获取额外参数
                dpi = kwargs.get('dpi', 150)
                
                # 预处理代码
                processed_code = self._preprocess_code(code, output_file, output_format, width, height, dpi)
                code_file.write_text(processed_code, encoding='utf-8')
                
                logger.info(f"🚀 执行mplfinance金融图表渲染...")
                
                # 执行Python代码
                result = subprocess.run(
                    [sys.executable, str(code_file)],
                    capture_output=True,
                    text=True,
                    timeout=90,
                    cwd=temp_dir,
                    encoding='utf-8',
                    errors='replace'
                )
                
                if result.returncode != 0:
                    return {
                        "success": False,
                        "error": f"Python代码执行失败:\n{result.stderr}"
                    }
                
                if not output_file.exists():
                    return {
                        "success": False,
                        "error": "代码执行完成但未生成图表文件"
                    }
                
                chart_bytes = output_file.read_bytes()
                
                if len(chart_bytes) == 0:
                    return {
                        "success": False,
                        "error": "生成的图表文件为空"
                    }
                
                logger.info(f"✅ mplfinance金融图表渲染成功，大小: {len(chart_bytes)} bytes")
                
                return {
                    "success": True,
                    "data": chart_bytes
                }
                
            except subprocess.TimeoutExpired:
                return {
                    "success": False,
                    "error": "金融图表渲染超时（90秒）"
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": f"渲染过程发生错误: {str(e)}"
                }
    
    def _preprocess_code(self, code: str, output_file: Path, output_format: str, width: int, height: int, dpi: int) -> str:
        """预处理mplfinance代码，自动修正ax+title用法，添加完整的中文支持"""
        # 移除代码块标记
        code = code.strip()
        if code.startswith("```python"):
            code = code[9:]
        elif code.startswith("```"):
            code = code[3:]
        if code.endswith("```"):
            code = code[:-3]

        # 自动修正mpf.plot(ax=..., title=...)用法，避免AttributeError
        def fix_ax_title(code):
            # 匹配mpf.plot( ... ax=..., title=... )
            pattern = re.compile(r"mpf\.plot\(([^\)]*?)ax\s*=\s*([\w\d_]+)[^\)]*?title\s*=\s*['\"]([^'\"]+)['\"][^\)]*?\)")
            def replacer(match):
                args = match.group(1)
                ax_var = match.group(2)
                title = match.group(3)
                # 移除title参数
                args_no_title = re.sub(r",?\s*title\s*=\s*['\"][^'\"]+['\"]", "", args)
                # 构造替换代码
                return f"mpf.plot({args_no_title}ax={ax_var})\n{ax_var}.set_title('{title}')  # 自动修正: title参数已移至set_title"
            return pattern.sub(replacer, code)
        code = fix_ax_title(code)
        
        # 确保必要的导入
        imports = [
            "import matplotlib",
            "matplotlib.use('Agg')  # 非交互式后端",
            "import matplotlib.pyplot as plt",
            "import mplfinance as mpf",
            "import pandas as pd",
            "import numpy as np",
            "import warnings",
            "warnings.filterwarnings('ignore')"
        ]
        
        # 强化的中文字体配置（解决mplfinance字体问题）
        font_config = [
            "# 强化中文字体配置 - 专门针对mplfinance",
            "import platform",
            "import matplotlib.font_manager as fm",
            "from matplotlib import rcParams",
            "",
            "# 根据操作系统选择最佳中文字体",
            "def setup_chinese_fonts_for_mplfinance():",
            "    import matplotlib.font_manager as fm  # 在函数内部重新导入",
            "    system = platform.system()",
            "    available_fonts = [f.name for f in fm.fontManager.ttflist]",
            "    ",
            "    # Windows系统字体优先级",
            "    if system == 'Windows':",
            "        font_priority = ['Microsoft YaHei', 'SimHei', 'SimSun', 'KaiTi']",
            "    elif system == 'Darwin':  # macOS",
            "        font_priority = ['Arial Unicode MS', 'Hiragino Sans GB', 'STHeiti', 'SimHei']",
            "    else:  # Linux",
            "        font_priority = ['WenQuanYi Micro Hei', 'DejaVu Sans', 'SimHei', 'Arial Unicode MS']",
            "    ",
            "    # 查找可用的中文字体",
            "    chinese_font = None",
            "    for font in font_priority:",
            "        if font in available_fonts:",
            "            chinese_font = font",
            "            break",
            "    ",
            "    # 强制设置字体（多种方法确保生效）",
            "    if chinese_font:",
            "        # 方法1: 设置rcParams",
            "        rcParams['font.sans-serif'] = [chinese_font, 'DejaVu Sans']",
            "        rcParams['axes.unicode_minus'] = False",
            "        rcParams['font.family'] = 'sans-serif'",
            "        ",
            "        # 方法2: 设置plt参数",
            "        plt.rcParams['font.sans-serif'] = [chinese_font, 'DejaVu Sans']",
            "        plt.rcParams['axes.unicode_minus'] = False",
            "        plt.rcParams['font.family'] = 'sans-serif'",
            "        ",
            "        # 方法3: 创建字体属性对象",
            "        global chinese_font_prop",
            "        chinese_font_prop = fm.FontProperties(family=chinese_font)",
            "        ",
            "        print(f'✅ 强制设置中文字体: {chinese_font}')",
            "        return chinese_font",
            "    else:",
            "        rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Liberation Sans']",
            "        plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Liberation Sans']",
            "        chinese_font_prop = None",
            "        print('⚠️ 未找到中文字体，使用默认字体')",
            "        return None",
            "",
            "# 应用字体配置",
            "selected_font = setup_chinese_fonts_for_mplfinance()",
            ""
        ]
        
        # 设置图片参数
        setup_code = [
            f"# 设置图片尺寸和DPI",
            f"plt.rcParams['figure.figsize'] = [{width/100:.1f}, {height/100:.1f}]",
            f"plt.rcParams['figure.dpi'] = {dpi}",
            f"plt.rcParams['savefig.dpi'] = {dpi}",
            f"",
        ]
        
        # 在用户代码后添加增强的字体修复代码
        font_fix_code = [
            "",
            "# 增强字体修复：全面修复图表中的中文字体显示",
            "def fix_chinese_font_comprehensive():",
            "    \"\"\"全面修复图表中的中文字体显示，包括所有文本元素\"\"\"",
            "    current_fig = plt.gcf()",
            "    if current_fig and selected_font:",
            "        print(f'🔧 开始全面修复中文字体: {selected_font}')",
            "        ",
            "        # 1. 修复图形级别的suptitle（最重要！）",
            "        if hasattr(current_fig, '_suptitle') and current_fig._suptitle:",
            "            suptitle_text = current_fig._suptitle.get_text()",
            "            if suptitle_text:",
            "                current_fig.suptitle(suptitle_text, fontfamily=selected_font, ",
            "                                   fontsize=current_fig._suptitle.get_fontsize())",
            "                print(f'  ✅ 修复suptitle: {suptitle_text[:20]}...')",
            "        ",
            "        # 2. 修复所有子图的字体",
            "        for i, ax in enumerate(current_fig.get_axes()):",
            "            print(f'  🔧 修复子图 {i+1}')",
            "            ",
            "            # 修复子图标题",
            "            if ax.get_title():",
            "                title_text = ax.get_title()",
            "                ax.set_title(title_text, fontfamily=selected_font, ",
            "                           fontsize=ax.title.get_fontsize())",
            "                print(f'    ✅ 修复title: {title_text[:20]}...')",
            "            ",
            "            # 修复x轴标签",
            "            if ax.get_xlabel():",
            "                xlabel_text = ax.get_xlabel()",
            "                ax.set_xlabel(xlabel_text, fontfamily=selected_font, ",
            "                            fontsize=ax.xaxis.label.get_fontsize())",
            "                print(f'    ✅ 修复xlabel: {xlabel_text}')",
            "            ",
            "            # 修复y轴标签", 
            "            if ax.get_ylabel():",
            "                ylabel_text = ax.get_ylabel()",
            "                ax.set_ylabel(ylabel_text, fontfamily=selected_font, ",
            "                            fontsize=ax.yaxis.label.get_fontsize())",
            "                print(f'    ✅ 修复ylabel: {ylabel_text}')",
            "            ",
            "            # 修复刻度标签",
            "            for label in ax.get_xticklabels():",
            "                if hasattr(label, 'set_fontfamily'):",
            "                    label.set_fontfamily(selected_font)",
            "            for label in ax.get_yticklabels():",
            "                if hasattr(label, 'set_fontfamily'):",
            "                    label.set_fontfamily(selected_font)",
            "        ",
            "        # 3. 查找和修复所有Text对象（兜底策略）",
            "        for text_obj in current_fig.findobj(lambda obj: hasattr(obj, 'set_fontfamily')):",
            "            try:",
            "                text_obj.set_fontfamily(selected_font)",
            "            except:",
            "                pass  # 忽略无法设置的对象",
            "        ",
            "        print(f'✅ 中文字体修复完成: {selected_font}')",
            "    else:",
            "        print('⚠️ 无法修复字体：图表或字体不可用')",
            "",
            "# 应用增强的字体修复",
            "fix_chinese_font_comprehensive()",
            ""
        ]
        
        # 构建完整代码
        full_code_lines = (
            imports + 
            [""] + 
            font_config +
            setup_code +
            ["# 用户代码开始"] + 
            self._indent_code(code).split('\n') + 
            font_fix_code +
            ["# 保存图片"] +
            [f"plt.tight_layout()"] +
            [f"plt.savefig(r'{output_file}', format='{output_format}', dpi={dpi}, bbox_inches='tight')"] +
            ["plt.close('all')"]
        )
        
        return '\n'.join(full_code_lines)
    
    def _indent_code(self, code: str) -> str:
        """为用户代码添加适当的缩进"""
        lines = code.split('\n')
        return '\n'.join(line for line in lines if line.strip()) 