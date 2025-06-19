# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Plotly渲染工具

这个模块实现了Plotly交互式图表的渲染功能，支持：
- 多种图表类型（散点图、线图、柱状图、热力图、3D图等）
- 交互式功能（缩放、平移、悬停、选择）
- 多种输出格式（HTML、PNG、PDF、SVG、JSON）
- Python代码执行环境
- 数据处理和分析功能
"""

import logging
import io
import json
import tempfile
import os
import sys
from typing import Dict, Any, Optional

try:
    import plotly.graph_objects as go
    import plotly.express as px
    import plotly.io as pio
    import plotly.offline as offline
    import pandas as pd
    import numpy as np
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

from google.genai import types
from .base_render_tool import BaseRenderTool

logger = logging.getLogger(__name__)

 
class PlotlyRenderTool(BaseRenderTool):
    """
    Plotly交互式图表渲染工具
    
    支持渲染各种类型的图表：
    - 基础图表：散点图、线图、柱状图、饼图
    - 统计图表：直方图、箱线图、小提琴图、热力图
    - 科学图表：3D散点图、3D曲面图、等高线图
    - 金融图表：蜡烛图、OHLC图、瀑布图
    - 地理图表：地图、散点地图、热力地图
    - 专业图表：雷达图、漏斗图、气泡图、树状图
    """
    
    def __init__(self):
        super().__init__(
            name="plotly_render",
            description="Plotly交互式数据可视化工具，支持各种图表类型和交互功能",
            supported_formats=["html", "png", "pdf", "svg", "json"],
            default_format="html"
        )
        
        # 设置Plotly渲染器
        if PLOTLY_AVAILABLE:
            # 检查kaleido是否可用于静态图像渲染
            try:
                import kaleido
                logger.info("kaleido已安装，支持静态图像格式")
            except ImportError:
                logger.warning("kaleido未安装，静态图像格式可能不可用")
        self._check_dependencies()
    
    def _check_dependencies(self):
        """🔧 增强的Plotly依赖检查"""
        self._plotly_available = False
        missing_deps = []
        available_deps = []
        
        # 检查核心依赖
        core_deps = {
            'plotly': '交互式可视化库',
            'pandas': '数据分析库',
            'numpy': '数值计算库',
            'statsmodels': '统计建模库（趋势线功能）',
            'kaleido': '静态图像渲染引擎（可选）'
        }
        
        for dep_name, desc in core_deps.items():
            try:
                module = __import__(dep_name)
                version = getattr(module, '__version__', '未知版本')
                logger.info(f"✅ {dep_name} ({desc}): {version}")
                available_deps.append(f"{dep_name}=={version}")
            except ImportError:
                logger.warning(f"❌ {dep_name} ({desc}): 未安装")
                if dep_name not in ['kaleido', 'statsmodels']:  # kaleido和statsmodels是可选的
                    missing_deps.append(dep_name)
                elif dep_name == 'statsmodels':
                    logger.info(f"ℹ️ {dep_name} 未安装，趋势线功能将不可用")
        
        if missing_deps:
            logger.warning(f"🔧 缺少必需依赖: {', '.join(missing_deps)}")
            logger.info(self._get_installation_guide(missing_deps))
            self._plotly_available = False
        else:
            logger.info("✅ Plotly渲染工具核心依赖检查通过")
            self._plotly_available = True
            
        # 测试Plotly功能
        if self._plotly_available:
            self._test_plotly_functionality()
    
    def _test_plotly_functionality(self):
        """🔧 新增方法：测试Plotly功能"""
        try:
            import plotly.graph_objects as go
            import plotly.express as px
            import pandas as pd
            import numpy as np
            
            # 创建测试数据
            test_df = pd.DataFrame({
                'x': [1, 2, 3],
                'y': [1, 4, 2]
            })
            
            # 测试基础图表创建
            fig = px.line(test_df, x='x', y='y', title='测试图表')
            
            # 测试HTML渲染
            html_output = fig.to_html()
            if len(html_output) > 0:
                logger.info("✅ Plotly HTML渲染测试成功")
            else:
                logger.warning("⚠️ Plotly HTML渲染测试失败")
                
            # 测试静态图像渲染（如果kaleido可用）
            try:
                import kaleido
                png_bytes = fig.to_image(format='png', width=100, height=100)
                if len(png_bytes) > 0:
                    logger.info("✅ Plotly静态图像渲染测试成功")
                else:
                    logger.warning("⚠️ Plotly静态图像渲染测试失败")
            except ImportError:
                logger.info("ℹ️ kaleido未安装，HTML格式仍可用，静态图像格式不可用")
            except Exception as e:
                logger.warning(f"⚠️ 静态图像渲染测试失败: {e}")
                
        except Exception as e:
            logger.error(f"❌ Plotly功能测试失败: {e}")
            self._plotly_available = False
    
    def _get_declaration(self) -> Optional[types.FunctionDeclaration]:
        """
        🔧 Plotly工具的函数声明
        
        包含Plotly特有的参数和详细的图表类型说明
        """
        return types.FunctionDeclaration(
            name=self.name,
            description="Plotly交互式数据可视化工具。支持生成各种类型的交互式图表，包括基础图表、统计图表、3D图表、地理图表等。",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    'code': types.Schema(
                        type=types.Type.STRING,
                        description='''Python代码，用于生成Plotly图表。代码应该创建一个名为'fig'的图表对象。

支持的图表类型和示例：

1. 基础图表：
   - 散点图：fig = px.scatter(df, x='x', y='y')
   - 线图：fig = px.line(df, x='x', y='y')
   - 柱状图：fig = px.bar(df, x='x', y='y')
   - 饼图：fig = px.pie(df, values='values', names='names')

2. 统计图表：
   - 直方图：fig = px.histogram(df, x='x')
   - 箱线图：fig = px.box(df, x='x', y='y')
   - 热力图：fig = px.imshow(data)

3. 3D图表：
   - 3D散点图：fig = px.scatter_3d(df, x='x', y='y', z='z')
   - 3D曲面：fig = go.Figure(data=[go.Surface(z=data)])

代码中可以使用pandas、numpy、plotly.express、plotly.graph_objects等库。
最后必须创建一个名为'fig'的图表对象。'''
                    ),
                    'output_format': types.Schema(
                        type=types.Type.STRING,
                        description='输出格式：html(默认,交互式)、png、pdf、svg、json',
                        enum=['html', 'png', 'pdf', 'svg', 'json'],
                        default='html'
                    ),
                    'title': types.Schema(
                        type=types.Type.STRING,
                        description='图表文件名称',
                        default='plotly_chart'
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
                    ),
                    'theme': types.Schema(
                        type=types.Type.STRING,
                        description='Plotly主题',
                        enum=['plotly', 'plotly_white', 'plotly_dark', 'ggplot2', 'seaborn', 'simple_white', 'none'],
                        default='plotly'
                    ),
                    'config': types.Schema(
                        type=types.Type.STRING,
                        description='额外的配置选项（JSON格式），如{"displayModeBar": true, "toImageButtonOptions": {"format": "png"}}',
                        default='{}'
                    )
                },
                required=['code'],
            )
        )
    
    def _render_sync(self, 
                    code: str, 
                    output_format: str, 
                    width: int, 
                    height: int) -> Dict[str, Any]:
        """
        同步渲染Plotly图表
        
        执行步骤：
        1. 检查Plotly依赖
        2. 准备执行环境
        3. 执行Python代码
        4. 提取图表对象
        5. 渲染为指定格式
        """
        if not self._plotly_available:
            missing_deps = ["plotly", "pandas", "numpy", "kaleido"]
            return {
                "success": False,
                "error": "Plotly依赖不可用",
                "installation_guide": self._get_installation_guide(missing_deps),
                "suggestion": "请先安装依赖: pip install plotly pandas numpy kaleido"
            }
        
        try:
            # 准备执行环境
            exec_globals = self._prepare_execution_environment()
            
            # 执行用户代码
            execution_result = self._execute_plotly_code(code, exec_globals)
            if not execution_result["success"]:
                return execution_result
            
            # 提取图表对象
            fig = execution_result["figure"]
            
            # 应用尺寸和主题
            self._apply_figure_settings(fig, width, height)
            
            # 渲染为指定格式
            return self._render_figure(fig, output_format, width, height)
            
        except Exception as e:
            logger.error(f"Plotly渲染失败: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"Plotly渲染异常: {e}"
            }
    
    def _prepare_execution_environment(self) -> Dict[str, Any]:
        """
        准备Python代码执行环境
        
        提供常用的库和工具函数
        """
        # 创建示例数据
        sample_data = self._create_sample_data()
        
        # 准备执行环境
        exec_globals = {
            # Plotly库
            'plotly': __import__('plotly'),
            'go': go,
            'px': px,
            'pio': pio,
            
            # 数据处理库
            'pd': pd,
            'np': np,
            
            # 示例数据
            'sample_data': sample_data,
            'df': sample_data['simple_df'],
            
            # 工具函数
            'range': range,
            'len': len,
            'list': list,
            'dict': dict,
            'zip': zip,
            'enumerate': enumerate,
            
            # 数学函数
            'abs': abs,
            'min': min,
            'max': max,
            'sum': sum,
            'round': round,
            
            # 其他常用模块
            'json': json,
            'math': __import__('math'),
            'random': __import__('random'),
            'datetime': __import__('datetime'),
        }
        
        return exec_globals
    
    def _create_sample_data(self) -> Dict[str, Any]:
        """
        创建示例数据集，方便用户快速测试
        """
        np.random.seed(42)  # 确保可重现性
        
        # 简单DataFrame
        simple_df = pd.DataFrame({
            'x': range(10),
            'y': np.random.randn(10).cumsum(),
            'category': ['A', 'B'] * 5,
            'size': np.random.randint(10, 100, 10)
        })
        
        # 时间序列数据
        dates = pd.date_range('2023-01-01', periods=30, freq='D')
        time_series_df = pd.DataFrame({
            'date': dates,
            'value': np.random.randn(30).cumsum(),
            'category': np.random.choice(['Type1', 'Type2', 'Type3'], 30)
        })
        
        # 3D数据
        x_3d = np.linspace(-3, 3, 50)
        y_3d = np.linspace(-3, 3, 50)
        X_3d, Y_3d = np.meshgrid(x_3d, y_3d)
        Z_3d = np.sin(np.sqrt(X_3d**2 + Y_3d**2))
        
        # 热力图数据
        heatmap_data = np.random.randn(10, 10)
        
        return {
            'simple_df': simple_df,
            'time_series_df': time_series_df,
            'x_3d': X_3d,
            'y_3d': Y_3d,
            'z_3d': Z_3d,
            'heatmap_data': heatmap_data
        }
    
    def _execute_plotly_code(self, code: str, exec_globals: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行Plotly代码并提取图表对象
        """
        try:
            # 重定向stdout和stderr以捕获输出
            old_stdout = sys.stdout
            old_stderr = sys.stderr
            
            stdout_buffer = io.StringIO()
            stderr_buffer = io.StringIO()
            
            sys.stdout = stdout_buffer
            sys.stderr = stderr_buffer
            
            try:
                # 执行用户代码
                exec_locals = {}
                exec(code, exec_globals, exec_locals)
                
                # 检查是否创建了图表对象
                fig = None
                if 'fig' in exec_locals:
                    fig = exec_locals['fig']
                elif 'figure' in exec_locals:
                    fig = exec_locals['figure']
                else:
                    # 在globals中查找
                    for name, obj in exec_globals.items():
                        if hasattr(obj, 'show') and hasattr(obj, 'to_html'):
                            fig = obj
                            break
                
                if fig is None:
                    return {
                        "success": False,
                        "error": "代码中未找到图表对象。请确保创建一个名为'fig'的Plotly图表对象。"
                    }
                
                # 验证图表对象
                if not hasattr(fig, 'to_html'):
                    return {
                        "success": False,
                        "error": f"对象类型错误：期望Plotly图表对象，实际得到 {type(fig)}"
                    }
                
                return {
                    "success": True,
                    "figure": fig,
                    "stdout": stdout_buffer.getvalue(),
                    "stderr": stderr_buffer.getvalue()
                }
                
            finally:
                # 恢复stdout和stderr
                sys.stdout = old_stdout
                sys.stderr = old_stderr
        
        except SyntaxError as e:
            return {
                "success": False,
                "error": f"Python语法错误: {e}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"代码执行失败: {e}"
            }
    
    def _apply_figure_settings(self, fig, width: int, height: int):
        """
        应用图表设置（尺寸、主题等）
        """
        try:
            # 更新布局
            fig.update_layout(
                width=width,
                height=height,
                autosize=True,
                margin=dict(l=50, r=50, t=50, b=50)
            )
        except Exception as e:
            logger.warning(f"应用图表设置失败: {e}")
    
    def _render_figure(self, 
                      fig, 
                      output_format: str, 
                      width: int, 
                      height: int) -> Dict[str, Any]:
        """
        将图表渲染为指定格式
        """
        try:
            if output_format == 'html':
                # 生成HTML
                html_content = fig.to_html(
                    include_plotlyjs=True,
                    div_id="plotly-chart",
                    config={'displayModeBar': True, 'responsive': True}
                )
                return {
                    "success": True,
                    "data": html_content.encode('utf-8')
                }
            
            elif output_format == 'json':
                # 生成JSON
                json_content = fig.to_json()
                return {
                    "success": True,
                    "data": json_content.encode('utf-8')
                }
            
            elif output_format in ['png', 'pdf', 'svg']:
                # 生成静态图像
                try:
                    image_bytes = fig.to_image(
                        format=output_format,
                        width=width,
                        height=height,
                        scale=2  # 高分辨率
                    )
                    return {
                        "success": True,
                        "data": image_bytes
                    }
                except Exception as e:
                    return {
                        "success": False,
                        "error": f"静态图像生成失败: {e}。请确保已安装kaleido: pip install kaleido"
                    }
            
            else:
                return {
                    "success": False,
                    "error": f"不支持的输出格式: {output_format}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"图表渲染失败: {e}"
            }
    
    def _get_mime_type(self, format: str) -> str:
        """
        重写父类方法，添加Plotly特有的MIME类型
        """
        plotly_mime_types = {
            'html': 'text/html',
            'json': 'application/json',
            'png': 'image/png',
            'pdf': 'application/pdf',
            'svg': 'image/svg+xml'
        }
        return plotly_mime_types.get(format.lower(), 'application/octet-stream') 