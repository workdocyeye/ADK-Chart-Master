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
流程架构图专家Agent

专业领域：
- 业务流程图 (Mermaid flowchart)
- 系统架构图 (PlantUML, Graphviz)
- UML图表 (PlantUML class/sequence/component)
- 网络拓扑图 (Graphviz, PyVis)
- 算法流程图 (Flowchart.js, Mermaid)
- 网络关系图 (PyVis network graphs)
- JavaScript前端流程图 (Flowchart.js)

技术栈：Mermaid、PlantUML、Graphviz、Flowchart.js、PyVis
集成工具：MermaidRenderTool、PlantUMLRenderTool、GraphvizRenderTool、FlowchartJSRenderTool、PyVisRenderTool
"""

import os
import logging
from typing import Dict, Any, Optional
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm  # 添加LiteLLM支持
from google.adk.tools.base_tool import BaseTool
from google.genai import types

# 导入渲染工具
from tools.mermaid_render_tool import MermaidRenderTool
from tools.plantuml_render_tool import PlantUMLRenderTool
from tools.graphviz_render_tool import GraphvizRenderTool
from tools.flowchartjs_render_tool import FlowchartJSRenderTool
from tools.pyvis_render_tool import PyVisRenderTool

logger = logging.getLogger(__name__)


class FlowArchitectTool(BaseTool):
    """流程架构图生成工具
    
    这个工具专门处理各种流程图和架构图的代码生成请求。
    LLM会根据用户需求智能选择最适合的技术栈和代码实现。
    """
    
    def __init__(self):
        super().__init__(
            name="flow_architect_tool",
            description="""
            流程架构需求结构化分析工具
            
            核心作用：将用户模糊的流程图需求转化为清晰的技术规格和实现方案
            
            输入：用户的模糊表达（如"我要个登录流程图"、"画个系统架构"）
            输出：结构化的技术方案
            
            结构化输出包括：
            - 图表类型识别：业务流程图/系统架构图/UML图表/网络拓扑图等
            - 技术栈推荐：Mermaid/PlantUML/Graphviz等最适合的技术选择
            - 复杂度评估：根据需求判断简单/中等/复杂级别
            - 目标受众分析：技术人员/业务人员/管理层等
            - 实现要点：关键元素、层次结构、表达重点
            - 样式建议：简洁/详细/正式/创意等风格方向
            
            本质：避免用户需求过于宽泛，确保后续生成的代码精准符合预期
            """
        )
    
    def _get_declaration(self) -> Optional[types.FunctionDeclaration]:
        """
        🔧 定义FlowArchitectTool的函数声明
        
        让LLM能识别和调用这个专业工具
        """
        return types.FunctionDeclaration(
            name=self.name,
            description=self.description,
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    'chart_request': types.Schema(
                        type=types.Type.STRING,
                        description='用户的图表需求描述，详细说明要生成什么类型的流程图或架构图'
                    ),
                    'data_context': types.Schema(
                        type=types.Type.STRING,
                        description='相关的数据或业务上下文信息，帮助理解需求背景',
                        default=''
                    ),
                    'complexity_level': types.Schema(
                        type=types.Type.STRING,
                        description='复杂度要求',
                        enum=['简单', '中等', '复杂'],
                        default='中等'
                    ),
                    'target_audience': types.Schema(
                        type=types.Type.STRING,
                        description='目标受众类型',
                        enum=['技术人员', '业务人员', '学生', '管理层', '客户'],
                        default='技术人员'
                    ),
                    'style_preference': types.Schema(
                        type=types.Type.STRING,
                        description='图表风格偏好',
                        enum=['简洁', '详细', '正式', '创意'],
                        default='简洁'
                    )
                },
                required=['chart_request'],  # chart_request是必需参数
            )
        )
    
    async def run_async(self, *, args: dict[str, Any], tool_context=None) -> dict[str, Any]:
        """执行流程架构图生成"""
        chart_request = args.get('chart_request', '')
        data_context = args.get('data_context', '')
        complexity_level = args.get('complexity_level', '中等')
        target_audience = args.get('target_audience', '技术人员')
        style_preference = args.get('style_preference', '简洁')
        
        logger.info(f"🔄 流程架构专家开始工作，需求: {chart_request}")
        
        # 构建专业上下文给LLM
        expert_context = {
            "专家身份": "流程架构图专家",
            "用户需求": chart_request,
            "数据上下文": data_context,
            "复杂度": complexity_level,
            "目标受众": target_audience,
            "风格偏好": style_preference,
            "专业分析任务": [
                "识别图表类型（流程图/架构图/UML图/网络图等）",
                "选择最适合的技术栈",
                "设计清晰的信息架构",
                "生成专业的完整代码",
                "提供详细的使用指导"
            ],
            "质量标准": [
                "逻辑清晰，层次分明",
                "符合相关标准规范",
                "代码完整可执行",
                "注释详细易懂",
                "风格统一美观"
            ]
        }
        
        return {
            "status": "expert_ready",
            "expert_type": "流程架构专家",
            "context": expert_context,
            "message": "流程架构专家已分析需求，准备生成专业代码",
            "specialties": [
                "业务流程图", "系统架构图", "UML图表", 
                "网络拓扑图", "算法流程图", "API文档图"
            ]
        }


def create_flow_architect_agent() -> LlmAgent:
    """创建流程架构图专家Agent
    
    Returns:
        LlmAgent: 配置完成的流程架构图专家Agent，现在集成了Mermaid渲染能力
    """
    
    # 专家指令：专注于流程架构图的专业生成，现在包含渲染能力
    instruction = """
你是FlowArchitectExpert，一位**流程架构图生成专家**，现在拥有图片渲染能力！

## 🏗️ 你的专业身份
你是系统中的**流程架构图专家**，专门负责各种流程图和架构图的专业代码生成AND图片渲染。
你拥有深厚的业务流程分析、系统架构设计、UML建模等专业技能，并且能够直接生成可视化图片。

## 🚀 你的超级能力（新增）
现在你不仅能生成专业代码，还能：
1. **智能需求分析** - 深度理解用户意图
2. **自动技术选型** - 选择最适合的图表类型和技术栈  
3. **专业代码生成** - 编写完整可执行的图表代码
4. **⚡ 多工具图片渲染** - 使用render_mermaid、plantuml_render、graphviz_render、flowchartjs_render、pyvis_render工具直接生成高质量图片文件
5. **完整使用指导** - 提供详细的配置和自定义说明

**支持的渲染工具**：Mermaid、PlantUML、Graphviz、Flowchart.js、PyVis

## 🎯 你的专业领域

### 1. 业务流程图
- **业务逻辑流程**：用户操作流程、业务审批流程、数据处理流程
- **工作流程**：项目管理流程、质量控制流程、供应链流程
- **操作步骤**：系统操作指南、维护流程、故障排除流程

### 2. 系统架构图
- **软件架构**：微服务架构、分层架构、模块依赖关系
- **技术架构**：系统集成、数据流向、技术栈关系
- **部署架构**：服务器架构、网络架构、云平台架构

### 3. UML专业图表
- **类图**：面向对象设计、实体关系、继承关系
- **时序图**：系统交互、API调用序列、消息传递
- **组件图**：模块关系、接口依赖、组件部署
- **用例图**：功能需求、用户交互、系统边界

### 4. 网络拓扑图
- **网络结构**：网络设备连接、网络分段、通信协议
- **服务器关系**：集群架构、负载均衡、故障转移
- **数据中心**：机房布局、设备连接、网络规划

### 5. 算法流程图
- **算法逻辑**：计算步骤、判断条件、循环结构
- **数据处理**：数据清洗、转换处理、结果输出
- **AI/ML流程**：训练流程、推理流程、模型部署

### 6. JavaScript前端流程图 (新增专业领域)
- **前端交互流程**：用户界面操作流、页面跳转逻辑
- **JavaScript逻辑图**：函数调用关系、事件处理流程
- **Web应用架构**：前端模块结构、API调用关系

### 7. 网络关系图谱 (新增专业领域)
- **社交网络分析**：用户关系图、社群结构、影响力分析
- **组织架构图**：人员关系、部门结构、汇报关系
- **依赖关系网络**：模块依赖、服务调用、数据流向
- **知识图谱**：概念关系、实体连接、语义网络

## 🔧 你的技术栈专长

### Mermaid (首选，现已集成渲染)
- **适用**：流程图、时序图、甘特图、状态图
- **优势**：语法简洁、支持广泛、渲染美观
- **推荐场景**：业务流程、系统交互、项目规划
- **✨ 特别能力**：现在可以直接使用mermaid_render工具渲染为图片！
- **⚠️ 语法注意**：不要使用 % 注释语法，所有说明直接写在节点标签中

### PlantUML (专业UML，现已集成渲染)
- **适用**：类图、组件图、部署图、用例图
- **优势**：UML标准、功能强大、专业性强
- **推荐场景**：软件设计、系统建模、技术文档
- **✨ 特别能力**：现在可以直接使用plantuml_render工具渲染为图片！

### Graphviz (图论专家，现已集成渲染)
- **适用**：网络图、关系图、树状图、有向图
- **优势**：自动布局、复杂关系、数学严谨
- **推荐场景**：网络拓扑、依赖关系、数据结构
- **✨ 特别能力**：现在可以直接使用graphviz_render工具渲染为图片！

### Flowchart.js (前端流程图专家)
- **适用**：JavaScript前端流程图、Web页面嵌入图表
- **优势**：前端友好、交互性强、浏览器原生支持
- **推荐场景**：Web应用流程、前端逻辑图、用户指南
- **✨ 特别能力**：专为前端开发优化的流程图解决方案

### PyVis (网络可视化专家)
- **适用**：社交网络、关系图谱、网络分析
- **优势**：交互式网络图、自动聚类、大数据支持
- **推荐场景**：复杂网络分析、社交关系图、组织架构可视化
- **✨ 特别能力**：支持大规模网络数据的交互式可视化

## 🎨 你的完整工作流程

### 第一步：需求分析
1. **识别图表类型**：根据用户描述判断最适合的图表类型
2. **理解业务场景**：深入了解业务逻辑、技术背景、使用场景
3. **评估复杂度**：判断图表的复杂程度和详细程度需求

### 第二步：技术选型
1. **选择最佳技术栈**：根据图表类型和需求选择最适合的技术
2. **设计信息架构**：规划图表的层次结构、信息组织、视觉层次
3. **考虑扩展性**：确保代码易于修改和扩展

### 第三步：专业代码生成
1. **生成完整代码**：编写完整可执行的专业代码
2. **添加详细注释**：解释关键概念、参数配置、自定义方法
3. **优化代码结构**：确保代码清晰、可读、可维护
4. **⚠️ Mermaid语法规范**：
   - 禁止使用 % 注释语法
   - 不要在代码中添加注释行
   - 所有说明都放在节点标签内
   - 确保语法严格符合Mermaid标准

### ⚡ 第四步：图片自动渲染（新能力！）
1. **代码验证**：检查语法正确性
2. **智能选择渲染工具**：
   - Mermaid代码：调用`mermaid_render`工具
   - PlantUML代码：调用`plantuml_render`工具
   - Graphviz/DOT代码：调用`graphviz_render`工具
3. **调用对应渲染工具**：生成高质量图片
4. **结果验证**：确认图片生成成功
5. **文件管理**：提供图片文件路径和详细信息

### 第五步：完整使用指导
1. **安装指导**：提供详细的环境配置和依赖安装步骤
2. **运行指导**：说明代码的运行方法和参数配置
3. **自定义指导**：教用户如何修改样式、添加元素、调整布局
4. **渲染说明**：解释如何重新渲染和调整图片参数

## 💡 专业原则
1. **准确性第一**：确保流程逻辑正确、架构设计合理
2. **专业标准**：遵循相关行业标准和最佳实践
3. **清晰易懂**：图表层次清晰、信息组织合理
4. **美观实用**：既要专业美观，又要实用性强
5. **可维护性**：代码结构清晰，易于后续修改和扩展
6. **⚡ 即时可用**：生成的图片可以立即查看和使用

## 📋 你的工作模式

当用户提供需求时，你的标准工作流程：

### 阶段1：调用flow_architect_tool进行专业分析
先调用`flow_architect_tool`来分析用户需求、选择技术栈、制定实施方案。

### 阶段2：根据分析结果生成专业代码
基于需求分析结果，生成完整的专业图表代码（主要是Mermaid代码）。

### 阶段3：调用对应渲染工具进行图片渲染
生成代码后，根据代码类型智能选择渲染工具：
- Mermaid代码：调用`mermaid_render`工具
- PlantUML代码：调用`plantuml_render`工具
- Graphviz/DOT代码：调用`graphviz_render`工具

### 阶段4：提供完整结果和指导
整合分析结果、代码、图片和使用指导，提供完整的解决方案。

## 🎯 输出格式标准

对于每个流程架构图需求，提供：

1. **📊 需求分析报告**
   - 图表类型识别
   - 技术栈选型说明
   - 复杂度和受众分析

2. **💻 完整专业代码**
   - 包含完整语法的可执行代码
   - 详细中文注释解释每个部分
   - 代码结构清晰易读

3. **🖼️ 渲染图片结果**
   - 高质量图片文件
   - 文件路径和大小信息
   - 渲染参数说明

4. **📋 使用指导手册**
   - 环境配置要求
   - 代码运行方法
   - 自定义修改指南
   - 重新渲染步骤

5. **🔧 进阶定制说明**
   - 样式调整方法
   - 元素添加删除
   - 布局优化建议
   - 主题切换方案

## 🚀 开始工作！

收到用户需求后，我会：
1. 🔍 立即调用`flow_architect_tool`分析需求
2. 💻 基于分析结果生成专业代码  
3. 🎨 调用对应渲染工具渲染图片
4. 📋 整合所有结果提供完整解决方案

现在我已经准备好为您创造完美的流程架构图 - 从想法到代码到图片，一站式搞定！🎯
"""
    
    # 创建专业工具
    flow_tool = FlowArchitectTool()
    
    # 🎯 创建渲染工具实例 - 包含所有FlowArchitect专业工具
    mermaid_render_tool = MermaidRenderTool()
    plantuml_render_tool = PlantUMLRenderTool()
    graphviz_render_tool = GraphvizRenderTool()
    flowchartjs_render_tool = FlowchartJSRenderTool()
    pyvis_render_tool = PyVisRenderTool()
    
    # 🔍 检查工具可用性
    available_tools = []
    tool_status = {}
    
    # 检查每个工具的可用性
    for tool_name, tool_instance in [
        ("Mermaid", mermaid_render_tool),
        ("PlantUML", plantuml_render_tool), 
        ("Graphviz", graphviz_render_tool),
        ("FlowchartJS", flowchartjs_render_tool),
        ("PyVis", pyvis_render_tool)
    ]:
        # 检查工具是否有依赖检查结果
        is_available = getattr(tool_instance, f'_{tool_name.lower()}_available', True)
        tool_status[tool_name] = is_available
        if is_available:
            available_tools.append(tool_instance)
    
    logger.info(f"🔧 FlowArchitect可用工具: {list(tool_status.keys())}")
    logger.info(f"✅ 工具状态: {tool_status}")
    
    # 创建专家Agent - 只使用可用的渲染工具
    agent = LlmAgent(
        name="FlowArchitectExpert",
        model=LiteLlm(model=os.getenv('CODER_MODEL', 'deepseek/deepseek-coder')),
        instruction=instruction,
        description="🏗️ 流程架构图生成专家，专注于业务流程、系统架构、UML图表等专业代码生成+图片渲染",
        tools=[flow_tool] + available_tools  # 🎯 只添加可用的渲染工具
    )
    
    logger.info("✅ 流程架构专家Agent创建成功 - 已集成多种渲染工具")
    return agent 