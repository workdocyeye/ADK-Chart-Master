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
Chart Coordinator Project - 渲染工具集合

专注于纯粹的"代码→图表"渲染工具集合。
每个工具负责将特定类型的代码转换为图片文件，并通过ADK Artifacts系统保存。

工具分类：
🥇 已实现工具 - 6个 (Mermaid, Matplotlib, Graphviz, Plotly, PlantUML, Seaborn, ECharts)
🥈 新增核心工具 - 5个 (Folium, mplfinance, Dygraphs, Py3Dmol, F2/AntV)
🥉 JavaScript交互工具 - 5个 (D3.js, Three.js, PyVis, Flowchart.js, ECharts)

总计: 16个纯渲染工具 (移除了8个不合适的工具)
"""

# 基础工具类
from .base_render_tool import BaseRenderTool

# 🥇 已实现的渲染工具
from .mermaid_render_tool import MermaidRenderTool
from .matplotlib_render_tool import MatplotlibRenderTool
from .graphviz_render_tool import GraphvizRenderTool
from .plotly_render_tool import PlotlyRenderTool
from .plantuml_render_tool import PlantUMLRenderTool
from .seaborn_render_tool import SeabornRenderTool
from .echarts_render_tool import EChartsRenderTool

# 🥈 新增核心渲染工具 (占位符 - 待实现)
from .folium_render_tool import FoliumRenderTool
from .mplfinance_render_tool import MplfinanceRenderTool
from .dygraphs_render_tool import DygraphsRenderTool
from .py3dmol_render_tool import Py3dmolRenderTool


# 🥉 JavaScript交互工具 (已实现)
from .d3_render_tool import D3RenderTool
from .threejs_render_tool import ThreeJSRenderTool
from .pyvis_render_tool import PyVisRenderTool
from .flowchartjs_render_tool import FlowchartJSRenderTool

# 工具集合分类 (纯渲染工具集合)
IMPLEMENTED_TOOLS = [
    MermaidRenderTool,
    MatplotlibRenderTool,
    GraphvizRenderTool,
    PlotlyRenderTool,
    PlantUMLRenderTool,
    SeabornRenderTool,
    EChartsRenderTool,
]

NEW_CORE_TOOLS = [
    FoliumRenderTool,
    MplfinanceRenderTool,
    DygraphsRenderTool,
    Py3dmolRenderTool,
]

# JavaScript交互工具 (已实现)
JAVASCRIPT_TOOLS = [
    D3RenderTool,
    ThreeJSRenderTool,     # 统一版本（本地优先，CDN备用）
    PyVisRenderTool,
    FlowchartJSRenderTool,
]

# 所有工具
ALL_TOOLS = IMPLEMENTED_TOOLS + NEW_CORE_TOOLS + JAVASCRIPT_TOOLS

# 按Agent分类的工具映射 (已完成所有工具)
AGENT_TOOL_MAPPING = {
    "FlowArchitectExpert": [
        MermaidRenderTool,      # 流程图、时序图
        PlantUMLRenderTool,     # UML图表、系统设计
        GraphvizRenderTool,     # DOT图形、架构图
        FlowchartJSRenderTool,  # JavaScript前端流程图
        PyVisRenderTool,        # 网络关系图
    ],
    "DataVizExpert": [
        MatplotlibRenderTool,   # 科学计算图表
        PlotlyRenderTool,       # 交互式数据可视化
        SeabornRenderTool,      # 统计图表美化
        EChartsRenderTool,      # 企业级数据图表
        MplfinanceRenderTool,   # 金融图表
        DygraphsRenderTool,     # 时间序列
        FoliumRenderTool,       # 地理可视化
        D3RenderTool,           # 高级自定义可视化
    ],
    "ConceptualMindExpert": [
        GraphvizRenderTool,     # 思维导图结构
        MermaidRenderTool,      # 概念流程图
        PlotlyRenderTool,       # 交互式概念图
        Py3dmolRenderTool,      # 分子结构图
    ],
    "InteractiveDynamicExpert": [
        PlotlyRenderTool,       # 交互式可视化
        EChartsRenderTool,      # 动态企业图表
        ThreeJSRenderTool,      # 3D可视化（统一版本）
        DygraphsRenderTool,     # 高性能时间序列交互
    ],
    "DocumentChartExpert": [
        MermaidRenderTool,      # 文档流程图
        MatplotlibRenderTool,   # 技术文档图表
        PlantUMLRenderTool,     # 技术设计图
    ],
}

# 便捷函数
def get_tools_for_agent(agent_name: str) -> list:
    """获取指定Agent的工具列表"""
    return AGENT_TOOL_MAPPING.get(agent_name, [])

def get_implemented_tools() -> list:
    """获取已实现工具列表"""
    return IMPLEMENTED_TOOLS

def get_new_core_tools() -> list:
    """获取新增核心工具列表"""
    return NEW_CORE_TOOLS

def get_all_tools() -> list:
    """获取所有工具列表"""
    return ALL_TOOLS

def get_tool_count_by_status() -> dict:
    """获取工具状态统计"""
    total_tools = 15  # 移除F2工具后的纯渲染工具总数
    implemented = len(IMPLEMENTED_TOOLS) + len(NEW_CORE_TOOLS) + len(JAVASCRIPT_TOOLS)
    return {
        "implemented": implemented,
        "pending": total_tools - implemented,
        "total": total_tools,
        "completion_rate": f"{implemented/total_tools*100:.1f}%",
        "removed_inappropriate": 9,  # 移除的不合适工具数（包括F2）
        "purification_note": "已移除9个不合适的工具，专注纯渲染功能（移除F2移动端工具）"
    }

__all__ = [
    # 基础类
    "BaseRenderTool",
    
    # 已实现的工具 (7个)
    "MermaidRenderTool",
    "MatplotlibRenderTool", 
    "GraphvizRenderTool",
    "PlotlyRenderTool",
    "PlantUMLRenderTool",
    "SeabornRenderTool",
    "EChartsRenderTool",
    
    # 新增工具 (9个已实现)
    "FoliumRenderTool",
    "MplfinanceRenderTool",
    "DygraphsRenderTool",
    "Py3dmolRenderTool",

    "D3RenderTool",
    "ThreeJSRenderTool",
    "PyVisRenderTool",
    "FlowchartJSRenderTool",
    
    # 工具集合
    "IMPLEMENTED_TOOLS",
    "NEW_CORE_TOOLS", 
    "JAVASCRIPT_TOOLS",
    "ALL_TOOLS",
    "AGENT_TOOL_MAPPING",
    
    # 便捷函数
    "get_tools_for_agent",
    "get_implemented_tools",
    "get_new_core_tools",
    "get_all_tools",
    "get_tool_count_by_status",
] 