# Copyright 2025 Google LLC
# matplotlib渲染工具 - 完整实现

import logging
import tempfile
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any, Optional

from google.genai import types
from .base_render_tool import BaseRenderTool

logger = logging.getLogger(__name__)


class MatplotlibRenderTool(BaseRenderTool):
    """🐍 Python Matplotlib图表渲染工具"""
    
    def __init__(self):
        super().__init__(
            name="render_matplotlib",
            description="🐍 Python Matplotlib图表渲染工具：将Python matplotlib代码转换为图片。适合科学计算、数据分析、统计图表。",
            supported_formats=["png", "svg", "pdf"],
            default_format="png"
        )
        self._check_dependencies()
    
    def _get_declaration(self) -> Optional[types.FunctionDeclaration]:
        """🔧 定义Matplotlib渲染工具的精确函数声明"""
        return types.FunctionDeclaration(
            name=self.name,
            description=self.description,
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    'code': types.Schema(
                        type=types.Type.STRING,
                        description='要渲染的Python matplotlib代码。应该包含完整的绘图逻辑，包括import语句、数据准备、绘图命令'
                    ),
                    'output_format': types.Schema(
                        type=types.Type.STRING,
                        description='输出图片格式。png适合数据分析，svg适合矢量图，pdf适合学术论文',
                        enum=['png', 'svg', 'pdf'],
                        default='png'
                    ),
                    'title': types.Schema(
                        type=types.Type.STRING,
                        description='图表文件名称（不含扩展名）',
                        default='matplotlib_chart'
                    ),
                    'width': types.Schema(
                        type=types.Type.INTEGER,
                        description='图片宽度（像素）',
                        default=800
                    ),
                    'height': types.Schema(
                        type=types.Type.INTEGER,
                        description='图片高度（像素）',
                        default=600
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
        """🔧 增强的matplotlib依赖检查"""
        self._matplotlib_available = False
        missing_deps = []
        available_deps = []
        
        # 检查核心依赖
        core_deps = {
            'matplotlib': '绘图库',
            'numpy': '数值计算库',
            'pandas': '数据分析库（可选）'
        }
        
        for dep_name, desc in core_deps.items():
            try:
                module = __import__(dep_name)
                version = getattr(module, '__version__', '未知版本')
                logger.info(f"✅ {dep_name} ({desc}): {version}")
                available_deps.append(f"{dep_name}=={version}")
            except ImportError:
                logger.warning(f"❌ {dep_name} ({desc}): 未安装")
                if dep_name != 'pandas':  # pandas是可选的
                    missing_deps.append(dep_name)
        
        if missing_deps:
            logger.warning(f"🔧 缺少必需依赖: {', '.join(missing_deps)}")
            logger.info(self._get_installation_guide(missing_deps))
            self._matplotlib_available = False
        else:
            logger.info("✅ matplotlib渲染工具所有依赖检查通过")
            self._matplotlib_available = True
            
        # 测试matplotlib后端
        if self._matplotlib_available:
            self._test_matplotlib_backend()
    
    def _test_matplotlib_backend(self):
        """🔧 新增方法：测试matplotlib后端"""
        try:
            import matplotlib
            matplotlib.use('Agg')  # 使用非交互式后端
            import matplotlib.pyplot as plt
            
            # 创建一个简单的测试图
            fig, ax = plt.subplots(figsize=(1, 1))
            ax.plot([1, 2], [1, 2])
            
            # 测试保存到内存
            import io
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png')
            buffer.seek(0)
            
            if len(buffer.getvalue()) > 0:
                logger.info("✅ matplotlib后端测试成功")
            else:
                logger.warning("⚠️ matplotlib后端测试失败 - 生成空文件")
                
            plt.close(fig)
            buffer.close()
            
        except Exception as e:
            logger.error(f"❌ matplotlib后端测试失败: {e}")
            self._matplotlib_available = False
    
    def _render_sync(self, code: str, output_format: str, width: int, height: int) -> Dict[str, Any]:
        """同步渲染Matplotlib图表"""
        
        if not self._matplotlib_available:
            missing_deps = ["matplotlib", "numpy"]
            return {
                "success": False,
                "error": "matplotlib依赖不可用",
                "installation_guide": self._get_installation_guide(missing_deps),
                "suggestion": "请先安装依赖: pip install matplotlib numpy pandas"
            }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            try:
                code_file = temp_path / "chart_code.py"
                output_file = temp_path / f"output.{output_format}"
                
                # 预处理代码
                processed_code = self._preprocess_code(code, output_file, output_format, width, height)
                code_file.write_text(processed_code, encoding='utf-8')
                
                logger.info(f"🚀 执行matplotlib代码渲染...")
                
                # 执行Python代码
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
                
                if not output_file.exists():
                    return {
                        "success": False,
                        "error": "代码执行完成但未生成图片文件"
                    }
                
                image_bytes = output_file.read_bytes()
                
                if len(image_bytes) == 0:
                    return {
                        "success": False,
                        "error": "生成的图片文件为空"
                    }
                
                logger.info(f"✅ Matplotlib图表渲染成功，大小: {len(image_bytes)} bytes")
                
                return {
                    "success": True,
                    "data": image_bytes
                }
                
            except subprocess.TimeoutExpired:
                return {
                    "success": False,
                    "error": "代码执行超时（60秒）"
                }
            except Exception as e:
                logger.error(f"Matplotlib渲染异常: {e}", exc_info=True)
                return {
                    "success": False,
                    "error": f"渲染过程异常: {e}"
                }
    
    def _preprocess_code(self, code: str, output_file: Path, output_format: str, width: int, height: int) -> str:
        """预处理matplotlib代码"""
        # 移除代码块标记
        code = code.strip()
        if code.startswith("```python"):
            code = code[9:]
        elif code.startswith("```"):
            code = code[3:]
        if code.endswith("```"):
            code = code[:-3]
        
        code = code.strip()
        
        if not code:
            raise ValueError("matplotlib代码不能为空")
        
        # 计算figsize
        figwidth = width / 100
        figheight = height / 100
        
        # 检查代码中是否已有savefig调用
        has_savefig = 'savefig' in code
        
        # 构建完整的Python代码
        full_code = f"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体支持
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 设置图表大小
plt.figure(figsize=({figwidth:.2f}, {figheight:.2f}))

try:
{self._indent_code(code)}
    
    # 自动保存图片
    if not {has_savefig}:
        plt.savefig(r"{output_file}", format="{output_format}", dpi=150, bbox_inches='tight')
    
    plt.close('all')
    print("✅ matplotlib图表渲染完成")
    
except Exception as e:
    print(f"❌ matplotlib渲染失败: {{e}}")
    raise e
"""
        return full_code
    
    def _indent_code(self, code: str) -> str:
        """为代码添加缩进"""
        lines = code.split('\n')
        return '\n'.join(['    ' + line for line in lines]) 