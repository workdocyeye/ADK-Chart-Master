# Copyright 2025 Google LLC
# seaborn渲染工具 - 完整实现

import logging
import tempfile
import sys
from pathlib import Path
from typing import Dict, Any, Optional
import io
import os
from urllib.error import URLError

# 核心绘图和数据处理库
import pandas as pd
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt
import matplotlib

from google.genai import types
from .base_render_tool import BaseRenderTool

# ==============================================================================
# Seaborn 数据集加载 "本地缓存优先" 补丁
# 核心作用：动态替换seaborn.load_dataset函数，优先从本地加载数据，避免因网络
# 问题（尤其是SSL错误）导致程序中断，并能自动缓存已下载的数据。
# ==============================================================================
# 获取seaborn原始的load_dataset函数
_original_load_dataset = sns.load_dataset

# 定义本地缓存目录
_CACHE_DIR = Path.cwd() / "static" / "seaborn-data"
os.makedirs(_CACHE_DIR, exist_ok=True)

def _robust_load_dataset(name, cache=True, data_home=None, **kws):
    """
    一个健壮的seaborn数据集加载函数，实现了本地缓存优先策略。
    """
    local_path = _CACHE_DIR / f"{name}.csv"
    
    # 1. 优先从本地缓存加载
    if local_path.exists():
        logging.info(f"✅ 从本地缓存加载seaborn数据集: {local_path}")
        try:
            return pd.read_csv(local_path)
        except Exception as e:
            logging.error(f"❌ 读取本地缓存文件 {local_path} 失败: {e}", exc_info=True)
            # 如果本地文件损坏，尝试删除后重新下载
            try:
                os.remove(local_path)
            except OSError:
                pass

    logging.info(f"ℹ️ 本地缓存未找到，尝试从网络下载seaborn数据集: '{name}'")
    
    # 2. 尝试从网络下载
    try:
        dataset = _original_load_dataset(name, cache=cache, data_home=data_home, **kws)
        # 3. 成功下载后，存入本地缓存
        try:
            dataset.to_csv(local_path, index=False)
            logging.info(f"✅ 数据集 '{name}' 已成功下载并缓存至: {local_path}")
        except Exception as e:
            logging.warning(f"⚠️ 缓存数据集 '{name}' 到 {local_path} 失败: {e}", exc_info=True)
        return dataset
    except (URLError, ConnectionError, TimeoutError) as e:
        # 4. 下载失败时的优雅处理
        error_msg = (
            f"❌ 网络错误：无法下载seaborn数据集 '{name}'。错误详情: {e}\n"
            f"解决方案: 请手动从 https://github.com/mwaskom/seaborn-data/blob/master/{name}.csv 下载数据文件, "
            f"并将其放置在以下路径: {local_path.resolve()}"
        )
        logging.error(error_msg)
        raise ConnectionError(error_msg) from e
    except Exception as e:
        error_msg = (
            f"❌ 加载seaborn数据集 '{name}' 时发生未知错误: {e}\n"
            f"请检查数据集名称是否正确，或尝试手动下载。"
        )
        logging.error(error_msg, exc_info=True)
        raise e

# 应用补丁：用我们的健壮版本替换原始的load_dataset函数
sns.load_dataset = _robust_load_dataset
logging.info("✅ Seaborn 'load_dataset' 函数已应用本地缓存补丁。")
# ==============================================================================
# 补丁结束
# ==============================================================================


logger = logging.getLogger(__name__)


class SeabornRenderTool(BaseRenderTool):
    """📊 Python Seaborn统计图表渲染工具"""
    
    def __init__(self):
        super().__init__(
            name="render_seaborn",
            description="📊 Python Seaborn统计图表渲染工具：基于matplotlib的统计数据可视化库。专门用于美观的统计图表、分布图、相关性分析图。",
            supported_formats=["png", "svg", "pdf"],
            default_format="png"
        )
        # 使用非交互式后端，避免在服务器上弹出GUI窗口
        matplotlib.use('Agg')
        self._check_dependencies()
    
    def _get_declaration(self) -> Optional[types.FunctionDeclaration]:
        """🔧 定义Seaborn渲染工具的精确函数声明"""
        return types.FunctionDeclaration(
            name=self.name,
            description=self.description,
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    'code': types.Schema(
                        type=types.Type.STRING,
                        description='要渲染的Python seaborn代码。应该包含完整的统计图表逻辑，包括import语句、数据准备、seaborn绘图函数。支持散点图、分布图、热力图、箱线图、小提琴图等。使用`sns.load_dataset("dataset_name")`来加载内置数据集。',
                    ),
                    'output_format': types.Schema(
                        type=types.Type.STRING,
                        description='输出图片格式。png适合数据报告，svg适合矢量编辑，pdf适合文档嵌入',
                        enum=['png', 'svg', 'pdf'],
                        default='png'
                    ),
                    'title': types.Schema(
                        type=types.Type.STRING,
                        description='图表文件名称（不含扩展名）',
                        default='seaborn_chart'
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
                    ),
                    'style': types.Schema(
                        type=types.Type.STRING,
                        description='Seaborn样式主题',
                        enum=['darkgrid', 'whitegrid', 'dark', 'white', 'ticks'],
                        default='darkgrid'
                    ),
                    'palette': types.Schema(
                        type=types.Type.STRING,
                        description='颜色调色板',
                        enum=['deep', 'muted', 'bright', 'pastel', 'dark', 'colorblind', 'husl', 'Set1', 'Set2', 'tab10'],
                        default='deep'
                    )
                },
                required=['code'],
            )
        )
    
    def _check_dependencies(self):
        """🔧 增强的seaborn依赖检查"""
        self._seaborn_available = False
        missing_deps = []
        
        core_deps = ['seaborn', 'matplotlib', 'numpy', 'pandas']
        
        for dep_name in core_deps:
            try:
                module = __import__(dep_name)
                version = getattr(module, '__version__', '未知版本')
                logger.info(f"✅ {dep_name}: {version}")
            except ImportError:
                logger.warning(f"❌ {dep_name}: 未安装")
                missing_deps.append(dep_name)
        
        if missing_deps:
            logger.warning(f"🔧 缺少必需依赖: {', '.join(missing_deps)}")
            logger.info(self._get_installation_guide(missing_deps))
            self._seaborn_available = False
        else:
            logger.info("✅ seaborn渲染工具所有依赖检查通过")
            self._seaborn_available = True
            
    def _render_sync(self, code: str, output_format: str, width: int, height: int, dpi: int = 150, style: str = 'darkgrid', palette: str = 'deep', title: str = 'seaborn_chart') -> Dict[str, Any]:
        """使用 exec() 同步渲染Seaborn图表，集成缓存和样式设置"""
        if not self._seaborn_available:
            return {
                "success": False,
                "error": "seaborn或其依赖不可用。",
                "suggestion": "请检查启动日志中的依赖检查信息并安装所有必需的库。"
            }
        # 预处理代码
        code = self._preprocess_code(code)
        # 定义执行上下文，提供常用库
        global_vars = {
            "sns": sns,
            "plt": plt,
            "pd": pd,
            "np": np,
            "__file__": "SeabornRenderTool"
        }
        try:
            # 应用样式和调色板
            plt.style.use('default') 
            sns.set_style(style)
            sns.set_palette(palette)
            # 计算图表尺寸（英寸）
            fig_width_inches = width / dpi
            fig_height_inches = height / dpi
            # 动态注入plt.figure()以控制尺寸
            code_to_exec = f"plt.figure(figsize=({fig_width_inches}, {fig_height_inches}), dpi={dpi})\n" + code
            # 执行用户代码
            exec(code_to_exec, global_vars)
            if not plt.get_fignums():
                 raise ValueError("代码未生成任何活动的Matplotlib图表。请确保您的代码调用了绘图函数（如 sns.histplot）。")
            # 保存图表到内存缓冲区
            buffer = io.BytesIO()
            plt.savefig(buffer, format=output_format, dpi=dpi, bbox_inches='tight')
            buffer.seek(0)
            image_bytes = buffer.getvalue()
            if not image_bytes:
                raise ValueError("生成的图表文件为空。请检查代码逻辑。")
            return {"success": True, "data": image_bytes, "format": output_format}
        except Exception as e:
            logger.error(f"❌ Seaborn渲染失败: {e}", exc_info=True)
            return {"success": False, "error": f"Seaborn渲染失败: {str(e)}", "suggestion": "请检查您的Seaborn代码是否有语法或逻辑错误。"}
        finally:
            # 确保关闭所有由exec创建的图表，防止内存泄漏
            plt.close('all')

    def _preprocess_code(self, code: str) -> str:
        """从字符串中移除Markdown代码块标记"""
        if code.strip().startswith("```python"):
            code = code.strip()[9:]
        elif code.strip().startswith("```"):
            code = code.strip()[3:]
        
        if code.strip().endswith("```"):
            code = code.strip()[:-3]
            
        return code.strip()

    def _get_installation_guide(self, missing_deps: list) -> str:
        """生成依赖安装指南"""
        return (
            f"🔧 请在您的项目终端中运行以下命令来安装缺失的依赖: \n"
            f"   pip install {' '.join(missing_deps)}"
        )
