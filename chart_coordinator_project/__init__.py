"""
ChartCoordinatorProject - LLM驱动的智能图表生成系统

基于Google ADK框架的多Agent图表生成系统。
"""

__version__ = "1.0.0"
__author__ = "Your Name"
__description__ = "LLM驱动的智能图表生成系统，支持多Agent协作生成各类图表"

# ADK Web UI 支持文件
# 此文件让 adk web 命令能够识别和加载您的Agent
from . import agent

__all__ = [
    "agent",
    "__version__",
    "__author__", 
    "__description__"
] 