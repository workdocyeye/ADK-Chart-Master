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
思维概念图专家Agent

专业领域：
- 思维导图 (NetworkX mind maps, Mermaid mind maps)
- 概念图 (Graphviz concept maps)  
- 知识图谱 (PyVis knowledge graphs)
- 组织架构图 (Plotly org charts)
- 分类树图 (matplotlib tree diagrams)
- 关系网络图 (NetworkX relationship networks)
- 分子可视化 (Py3Dmol 蛋白质3D结构)
- 科学概念图 (生物化学、材料科学)

技术栈：NetworkX、Graphviz、PyVis、Plotly、matplotlib、D3.js、Mermaid、Py3Dmol
集成工具：MermaidRenderTool、PlotlyRenderTool、GraphvizRenderTool、Py3dmolRenderTool
"""

import os
import logging
from typing import Dict, Any, Optional
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm  # 添加LiteLLM支持
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext
from google.genai import types

# 导入渲染工具
from tools.mermaid_render_tool import MermaidRenderTool
from tools.plotly_render_tool import PlotlyRenderTool
from tools.graphviz_render_tool import GraphvizRenderTool
from tools.py3dmol_render_tool import Py3dmolRenderTool
from tools.pyvis_render_tool import PyVisRenderTool

logger = logging.getLogger(__name__)


class ConceptualMindTool(BaseTool):
    """思维概念图专业工具
    
    专门处理各种概念性图表的生成，LLM会根据数据结构和概念关系
    智能选择最适合的思维图表类型和技术实现。
    """
    
    def __init__(self):
        super().__init__(
            name="conceptual_mind_tool",
            description="思维概念图需求结构化分析工具"
        )
    
    def _get_declaration(self) -> Optional[types.FunctionDeclaration]:
        """定义思维概念图工具的函数声明，让LLM知道如何调用这个专业工具"""
        return types.FunctionDeclaration(
            name="conceptual_mind_tool",
            description="""
            思维概念需求结构化分析工具
            
            核心作用：将用户模糊的概念图表需求转化为清晰的认知结构和技术方案
            
            输入：用户的模糊表达（如"思维导图"、"概念图"、"知识图谱"、"组织架构"）
            输出：结构化的概念可视化方案
            
            结构化输出包括：
            - 图表类型识别：思维导图/概念图/知识图谱/组织架构图/分类树图/关系网络图
            - 数据结构分析：层次性/网络性/分类性特征判断
            - 布局策略推荐：层次型/放射型/网络型/树状型/圆形/力导向等最佳布局
            - 技术栈推荐：NetworkX/Plotly/Graphviz/PyVis/D3.js等最优选择
            - 交互需求评估：静态展示/基础交互/高级交互功能规划
            - 视觉主题定位：学术/商务/创意/简约/科技风格方向
            - 实现要点：关键节点设计、关系表达方式、认知友好性考虑
            
            本质：避免概念图表需求表达不清，确保认知结构与可视化方案精准匹配用户的思维模式
            """.strip(),
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "concept_data": types.Schema(
                        type=types.Type.STRING,
                        description="概念数据描述，包括节点、关系、属性、层次结构等信息"
                    ),
                    "graph_type": types.Schema(
                        type=types.Type.STRING,
                        description="图表类型选择",
                        enum=["思维导图", "概念图", "知识图谱", "组织架构图", "分类树图", "关系网络图"]
                    ),
                    "layout_style": types.Schema(
                        type=types.Type.STRING,
                        description="布局风格偏好",
                        enum=["层次型", "放射型", "网络型", "树状型", "圆形布局", "力导向布局"],
                        default="层次型"
                    ),
                    "interaction_level": types.Schema(
                        type=types.Type.STRING,
                        description="交互需求级别",
                        enum=["静态", "基础交互", "高级交互"],
                        default="基础交互"
                    ),
                    "visual_theme": types.Schema(
                        type=types.Type.STRING,
                        description="视觉主题样式",
                        enum=["学术", "商务", "创意", "简约", "科技"],
                        default="学术"
                    )
                },
                required=["concept_data", "graph_type"]
            )
        )
    
    async def run_async(self, *, args: dict[str, Any], tool_context=None) -> dict[str, Any]:
        """执行思维概念图生成"""
        concept_data = args.get('concept_data', '')
        graph_type = args.get('graph_type', '概念图')
        layout_style = args.get('layout_style', '层次型')
        interaction_level = args.get('interaction_level', '基础交互')
        visual_theme = args.get('visual_theme', '学术')
        
        logger.info(f"🧠 思维概念图专家开始工作，类型: {graph_type}")
        
        # 构建专业上下文给LLM
        expert_context = {
            "专家身份": "思维概念图专家",
            "概念数据": concept_data,
            "图表类型": graph_type,
            "布局风格": layout_style,
            "交互需求": interaction_level,
            "视觉主题": visual_theme,
            "专业分析任务": [
                "分析概念数据的结构特征（层次性/网络性/分类性）",
                "选择最适合的图表类型和布局算法",
                "设计清晰的视觉层次和信息架构",
                "选择最优的技术栈和实现方案",
                "生成专业的完整代码实现",
                "优化用户体验和交互功能"
            ],
            "质量标准": [
                "概念关系表达准确",
                "视觉层次清晰合理",
                "布局算法选择恰当",
                "交互体验流畅自然",
                "代码质量优良可维护",
                "文档说明详细完整"
            ]
        }
        
        return {
            "status": "expert_ready",
            "expert_type": "思维概念图专家",
            "context": expert_context,
            "message": "思维概念图专家已分析概念数据，准备生成专业图表代码",
            "specialties": [
                "思维导图", "概念图", "知识图谱", 
                "组织架构图", "分类树图", "关系网络图"
            ]
        }


def create_conceptual_mind_agent() -> LlmAgent:
    """创建思维概念图专家Agent
    
    Returns:
        LlmAgent: 配置完成的思维概念图专家Agent
    """
    
    # 专家指令：专注于思维概念图的专业生成
    instruction = """
你是ConceptualMindExpert，一位**思维概念图生成专家**。

## 🧠 你的专业身份
你是系统中的**思维概念图专家**，专门负责概念性、结构性图表的专业代码生成。
你拥有深厚的知识管理、信息架构、认知科学、图论等专业技能。

**支持的渲染工具**：Mermaid、Plotly、Graphviz、Py3dmol、PyVis

## 🎯 你的专业领域

### 1. 思维导图 (Mind Maps)
- **适用场景**: 头脑风暴、知识整理、学习笔记、创意发散
- **数据特点**: 中心主题+多层次分支结构
- **核心优势**: 模仿大脑思维模式，层次清晰，记忆友好

### 2. 概念图 (Concept Maps)  
- **适用场景**: 知识体系展示、学科结构图、概念关系梳理
- **数据特点**: 概念节点+有标签的关系连线
- **核心优势**: 显示概念间的逻辑关系，支持复杂知识结构

### 3. 知识图谱 (Knowledge Graphs)
- **适用场景**: 复杂知识网络、实体关系图、语义网络
- **数据特点**: 实体+属性+关系三元组，多维度关联
- **核心优势**: 可表达复杂语义关系，支持推理查询

### 4. 组织架构图 (Organizational Charts)
- **适用场景**: 公司结构、项目团队、系统层级、管理关系
- **数据特点**: 层级结构+职责信息+汇报关系
- **核心优势**: 清晰展示权力结构和责任分工

### 5. 分类树图 (Classification Trees)
- **适用场景**: 分类体系、决策树、产品分类、知识分类
- **数据特点**: 分层分类+属性标签+包含关系
- **核心优势**: 系统化分类，支持递归查找和筛选

### 6. 关系网络图 (Relationship Networks)
- **适用场景**: 社交网络、依赖关系、影响网络、协作图
- **数据特点**: 节点+边+网络指标+社群结构
- **核心优势**: 发现网络模式，识别关键节点和社群

## 🔧 你的技术栈专长

### NetworkX + Matplotlib (科学严谨)
- **适用**: 复杂网络分析、算法可视化、科研论文
- **优势**: 算法丰富、数学严谨、自定义性强
- **推荐场景**: 网络分析、图论研究、学术展示

### Plotly (交互体验)
- **适用**: 交互式网络图、3D可视化、Web应用
- **优势**: 交互丰富、3D支持、Web友好
- **推荐场景**: 数据探索、在线展示、用户交互

### Graphviz (专业布局)
- **适用**: 有向图、层次图、复杂关系图
- **优势**: 自动布局算法优秀、专业级质量
- **推荐场景**: 流程图、依赖图、组织架构

### PyVis (轻量交互)
- **适用**: 快速网络可视化、社交网络图、关系网络
- **优势**: 轻量级、易用性强、快速原型、中文支持完善
- **推荐场景**: 快速展示、演示原型、教学用途、社交网络分析

## 🎨 你的工作流程

### 第一步：数据理解
1. **结构分析**: 识别数据的层次性、网络性、分类性特征
2. **关系挖掘**: 发现实体间的关联、依赖、包含关系
3. **语义理解**: 理解概念的含义、重要性、上下文

### 第二步：图表设计
1. **类型选择**: 根据数据特征选择最适合的概念图类型
2. **布局设计**: 选择合适的布局算法和视觉层次
3. **样式规划**: 设计颜色编码、节点样式、连线风格

### 第三步：技术实现
1. **算法选择**: 选择最优的布局算法和计算方法
2. **代码生成**: 编写高质量、可维护的可视化代码
3. **性能优化**: 处理大规模数据和复杂关系网络

### 第四步：交互优化
1. **用户体验**: 设计直观的交互方式和导航功能
2. **信息展示**: 平衡信息密度和视觉清晰度
3. **扩展性**: 支持动态更新和数据变化

## 💡 专业原则
1. **认知友好**: 符合人类认知模式，易于理解和记忆
2. **层次清晰**: 信息组织有序，视觉层次分明
3. **关系准确**: 准确表达实体间的语义关系
4. **美观实用**: 兼顾视觉美感和实用功能
5. **可扩展性**: 支持数据增长和结构变化
6. **交互友好**: 提供必要的交互功能增强用户体验

## 📋 分析任务
当用户提供概念数据和需求时，你需要：

1. **数据分析**: 分析数据的结构特征、关系类型、复杂程度
2. **需求理解**: 理解用户的展示目标、使用场景、受众特点
3. **图表选择**: 选择最适合的概念图类型和可视化方案
4. **技术实现**: 生成完整、专业的可视化代码
5. **使用指导**: 提供详细的配置、自定义、扩展说明

## 🎯 输出格式
对于每个概念图需求，提供：

1. **数据分析**: 数据结构特征和关系类型分析
2. **方案推荐**: 最适合的概念图类型和技术选择
3. **完整代码**: 包含数据处理、图表生成、样式配置的完整代码
4. **详细注释**: 代码中的详细中文注释，解释算法和配置
5. **使用指南**: 环境配置、参数调整、功能扩展说明

让我们一起构建清晰的知识结构，让思维可视化！🌟

## 🔧 重要：工具调用方式

你拥有以下本地渲染工具，请务必正确使用：

### 1. GraphvizRenderTool - Graphviz本地渲染
当用户需要组织架构图、层次图、关系图时：
```
调用: graphviz_render_tool.run_async(args={
    "code": "DOT语言代码",
    "output_format": "png",  # 或svg、pdf
    "title": "图表标题"
})
```

### 2. PlotlyRenderTool - Plotly本地渲染  
当用户需要交互式图表、网络图时：
```
调用: plotly_render_tool.run_async(args={
    "code": "Plotly Python代码", 
    "output_format": "html",  # 或png、svg
    "title": "图表标题"
})
```

### 3. MermaidRenderTool - Mermaid本地渲染
当用户需要流程图、简单图表时：
```
调用: mermaid_render_tool.run_async(args={
    "code": "Mermaid语法代码",
    "output_format": "png",
    "title": "图表标题"  
})
```

### 4. PyVisRenderTool - PyVis本地渲染
当用户需要交互式网络图、社交网络图时：
```
调用: pyvis_render_tool.run_async(args={
    "code": "PyVis Python代码",
    "output_format": "html",  # 或png
    "title": "图表标题"
})
```

**⚠️ 重要提醒**：
- 不要生成 `print(default_api.xxx())` 这样的伪代码
- 不要生成 `plt.show()` 或其他显示命令
- 直接调用上述工具，工具会自动渲染并保存图片
- 所有渲染都在本地完成，无需网络连接
"""
    
    # 创建专业工具
    conceptual_tool = ConceptualMindTool()
    
    # 🎯 创建渲染工具实例 - 只保留已完整实现的工具
    mermaid_render_tool = MermaidRenderTool()
    plotly_render_tool = PlotlyRenderTool()
    graphviz_render_tool = GraphvizRenderTool()
    py3dmol_render_tool = Py3dmolRenderTool()
    pyvis_render_tool = PyVisRenderTool()  # 添加PyVis工具
    
    # 🔍 检查工具可用性
    available_tools = []
    tool_status = {}
    
    # 检查每个工具的可用性
    for tool_name, tool_instance in [
        ("Mermaid", mermaid_render_tool),
        ("Plotly", plotly_render_tool),
        ("Graphviz", graphviz_render_tool),
        ("Py3dmol", py3dmol_render_tool),
        ("PyVis", pyvis_render_tool)  # 添加PyVis工具检查
    ]:
        # 检查工具是否有依赖检查结果
        is_available = getattr(tool_instance, f'_{tool_name.lower()}_available', True)
        tool_status[tool_name] = is_available
        if is_available:
            available_tools.append(tool_instance)
    
    logger.info(f"🔧 ConceptualMind可用工具: {list(tool_status.keys())}")
    logger.info(f"✅ 工具状态: {tool_status}")
    
    # 创建思维概念图专家Agent - 只使用可用的渲染工具
    agent = LlmAgent(
        name="ConceptualMindExpert",
        model=LiteLlm(model=os.getenv('CODER_MODEL', 'deepseek/deepseek-coder')),
        instruction=instruction,
        description="🧠 思维概念图生成专家，专注于思维导图、概念图、知识图谱、组织架构图等概念性图表的代码生成+图片渲染",
        tools=[conceptual_tool] + available_tools  # 🎯 只添加可用的渲染工具
    )
    
    logger.info("✅ 思维概念图专家Agent创建成功 - 已集成多种渲染能力")
    return agent 