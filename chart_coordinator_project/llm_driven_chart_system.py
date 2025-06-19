"""
LLM驱动的智能图表代码生成系统
基于Google ADK框架的完全AI驱动系统 - 标准ADK多Agent架构

核心理念：使用ADK标准的sub_agents模式
- 用户提供数据和模糊需求
- ChartCoordinatorAI主Agent智能分析并选择专家
- 三个专业Sub-Agent负责各领域的代码生成
- 完全由LLM决策，无硬编码路由逻辑

支持图表类型：
- 科研: 流程图、架构图、思维导图
- 产品: 原型图、用户流程、功能图  
- 程序: 系统架构、类图、序列图
- 统计: 各类数据可视化图表
- 生活: 规划图、组织图等

支持代码格式：
mermaid、PlantUML、Flowchart、Graphviz、HTML、ECharts、
XML、Canvas、Xmind、Markdown、Draw.io等
"""

import os
import asyncio
import logging
import json
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

# Google ADK框架导入
from google.adk import Runner
from google.adk.agents import LlmAgent
from google.adk.tools.base_tool import BaseTool
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.adk.models.lite_llm import LiteLlm  # 添加LiteLLM支持

# 添加工具声明所需的类型导入
from google.genai import types

# 导入专业Agent
from agents.flow_architect_agent import create_flow_architect_agent
from agents.data_visualization_agent import create_data_visualization_agent
from agents.interactive_dynamic_agent import create_interactive_dynamic_agent
from agents.conceptual_mind_agent import create_conceptual_mind_agent
from agents.document_chart_agent import create_document_chart_agent

# 加载环境变量
load_dotenv(encoding='utf-8')

# 配置日志
logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class LLMAnalysisOrchestrator(BaseTool):
    """LLM分析协调器
    
    这是系统的核心工具，负责：
    1. 接收用户的数据和模糊需求
    2. 调用LLM进行深度分析
    3. 让LLM推荐最适合的图表类型
    4. 协调整个分析流程
    
    注意：这个工具不做实际分析，只是为LLM提供结构化的输入输出接口
    """
    
    def __init__(self):
        super().__init__(
            name="llm_analysis_orchestrator",
            description="LLM分析协调器 - 系统核心工具"
        )
    
    def _get_declaration(self) -> Optional[types.FunctionDeclaration]:
        """定义工具的函数声明，让LLM知道如何调用这个工具
        
        这是ADK框架要求的标准方法，用于：
        1. 告诉LLM这个工具的名称和功能描述
        2. 定义工具接受的参数及其类型
        3. 指定哪些参数是必需的
        4. 为LLM提供调用工具所需的完整接口信息
        """
        return types.FunctionDeclaration(
            name="llm_analysis_orchestrator",
            description="""
            LLM分析协调器 - 系统核心工具
            
            功能：
            - 接收用户提供的原始数据（任何格式）
            - 接收用户的模糊需求描述
            - 为LLM分析提供结构化接口
            - 返回LLM的分析结果和推荐方案
            
            这个工具帮助LLM理解用户需求并准备分析上下文，
            为后续的专家Agent选择提供基础信息。
            """.strip(),
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "user_data": types.Schema(
                        type=types.Type.STRING,
                        description="用户提供的数据，可以是文本、CSV格式、表格描述、数据说明等任何形式的数据信息"
                    ),
                    "user_requirements": types.Schema(
                        type=types.Type.STRING,
                        description="用户的需求描述，可以很模糊，如'想要个流程图'、'做个数据分析'、'画个架构图'等"
                    ),
                    "domain": types.Schema(
                        type=types.Type.STRING,
                        description="应用领域，可选值：科研、产品、程序、统计、生活、通用等，用于优化分析方向",
                        enum=["科研", "产品", "程序", "统计", "生活", "通用"]
                    ),
                    "urgency": types.Schema(
                        type=types.Type.STRING,
                        description="紧急程度，影响处理优先级和复杂度",
                        enum=["低", "中", "高"]
                    )
                },
                required=["user_data", "user_requirements"]
            )
        )
    
    async def run_async(self, *, args: dict[str, Any], tool_context=None) -> dict[str, Any]:
        """执行LLM分析协调"""
        user_data = args.get('user_data', '')
        user_requirements = args.get('user_requirements', '')
        domain = args.get('domain', '通用')
        urgency = args.get('urgency', '中')
        
        logger.info(f"🚀 启动LLM分析协调，领域: {domain}")
        
        # 构建给LLM的结构化提示
        analysis_context = {
            "用户数据": user_data,
            "用户需求": user_requirements,
            "应用领域": domain,
            "紧急程度": urgency,
            "分析任务": "请作为专业的数据分析师和可视化专家，完成以下任务"
        }
        
        return {
            "status": "ready_for_llm_analysis",
            "context": analysis_context,
            "message": "数据已准备好，等待LLM进行深度分析",
            "next_step": "LLM将分析数据特征并推荐最适合的图表类型"
        }


def create_llm_driven_chart_coordinator() -> LlmAgent:
    """创建LLM驱动的图表协调系统 - 使用ADK标准sub_agents模式"""
    
    # 创建五个专业Sub-Agent
    flow_architect_agent = create_flow_architect_agent()
    data_viz_agent = create_data_visualization_agent()  
    interactive_agent = create_interactive_dynamic_agent()
    conceptual_mind_agent = create_conceptual_mind_agent()
    document_chart_agent = create_document_chart_agent()
    
    # 协调Agent的指令：让LLM智能选择并调用专业Agent
    instruction = """
你是ChartCoordinatorAI，一位拥有顶级能力的**智能图表协调专家**。

## 🧠 你的核心身份
你是系统中的**智能协调中心**，负责分析用户需求并智能选择最合适的专业子Agent来完成工作。
你有五位专业助手，每位都是各自领域的专家。

## 👥 你的专业团队（Sub-Agents）

### 🏗️ FlowArchitectExpert - 流程架构专家
**专业领域**：业务流程图、系统架构图、UML图表、网络拓扑图、算法流程图
**技术栈**：Mermaid、PlantUML、Graphviz、Draw.io XML、Flowchart.js
**支持的渲染工具**：Mermaid、PlantUML、Graphviz、Flowchart.js、PyVis
**适用场景**：流程设计、系统建模、架构图、UML图表

### 📊 DataVizExpert - 数据可视化专家  
**专业领域**：统计图表、数据仪表板、趋势分析、交互式图表、科学数据图
**技术栈**：ECharts、Python(matplotlib/plotly/seaborn)、D3.js、Canvas、HTML+JS
**支持的渲染工具**：Matplotlib、Plotly、Seaborn、ECharts、Dygraphs、Folium、mplfinance、D3.js
**适用场景**：数据分析、统计图表、可视化报表

### ⚡ InteractiveDynamicExpert - 交互动态专家
**专业领域**：动画效果、实时数据、3D可视化、游戏化图表、高性能渲染
**技术栈**：Canvas、WebGL、Three.js、CSS3、WebSocket、动画库
**支持的渲染工具**：Plotly、ECharts、Three.js、Dygraphs
**适用场景**：动态效果、交互体验、实时更新、3D图表

### 🧠 ConceptualMindExpert - 思维概念专家
**专业领域**：思维导图、概念图、知识图谱、组织架构图、分类树图、关系网络图
**技术栈**：NetworkX、Graphviz、Matplotlib、Plotly、PyVis、思维导图库
**支持的渲染工具**：Mermaid、Plotly、Graphviz、Py3dmol、PyVis
**适用场景**：知识整理、概念展示、关系分析、层次结构

### 📑 DocumentChartExpert - 文档图表专家
**专业领域**：报告图表、仪表板图表、信息图表、对比图表、趋势分析图、业务报表
**技术栈**：Matplotlib、Seaborn、Plotly、Bokeh、专业报表库
**支持的渲染工具**：Mermaid、PlantUML、Matplotlib
**适用场景**：商业报告、学术论文、演示文稿、业务分析

> 当用户明确指定渲染工具（如"请用ECharts画图"），请优先选择具备该工具能力的专家Agent。
> 若需求模糊，请根据图表类型和工具能力综合判断最优分配。

## 🎯 你的智能协调流程

### 第一步：深度需求分析
仔细分析用户的需求：

1. **理解核心意图**
   - 用户想要什么类型的图表？
   - 解决什么问题或展示什么信息？
   - 目标受众是谁？

2. **数据特征分析**（如果用户提供数据）
   - 数据类型和结构
   - 数据量和复杂度
   - 时间特征和更新频率

3. **技术需求判断**
   - 静态图表还是交互式？
   - 简单展示还是复杂分析？
   - 需要什么技术栈？

### 第二步：智能专家选择
基于分析结果，使用ADK的transfer_to_agent功能智能选择专家：

**选择FlowArchitectExpert，当用户需要：**
- 流程图、架构图、系统设计图
- UML图表（类图、时序图、用例图等）
- 业务流程、工作流程、算法流程
- 网络拓扑、组件关系、模块依赖
- 关键词：流程、架构、系统、UML、设计、逻辑、步骤

**选择DataVizExpert，当用户需要：**
- 统计图表、数据分析图表
- 趋势图、对比图、分布图
- 数据仪表板、报表图表
- 科学数据可视化
- 关键词：数据、图表、统计、分析、趋势、可视化

**选择InteractiveDynamicExpert，当用户需要：**
- 动画效果、交互式图表
- 实时数据展示、动态更新
- 3D可视化、游戏化图表
- 高性能渲染、特效展示
- 关键词：动画、交互、实时、动态、3D、游戏化

**选择ConceptualMindExpert，当用户需要：**
- 思维导图、概念图、知识图谱
- 组织架构图、分类树图
- 关系网络图、层次结构图
- 概念关系展示、知识整理
- 关键词：思维、概念、知识、关系、层次、网络

**选择DocumentChartExpert，当用户需要：**
- 报告图表、商业演示图表
- 仪表板、信息图表
- 对比分析图、趋势报告
- 专业文档图表、学术论文图表
- 关键词：报告、文档、商业、演示、对比、专业

### 第三步：专业展示分析过程
在选择专家之前，向用户展示你的分析：

```
🧠 **智能需求分析**

📊 **需求理解**：
[详细说明你对用户需求的理解]

🎯 **技术判断**：
需求类型：[流程架构/数据可视化/交互动态/思维概念/文档图表]
选择理由：[为什么选择这个专家]
技术栈：[预期使用的技术方案]

🔧 **处理方案**：
我将调用[专家名称]为您生成专业的代码解决方案。

💡 **预期效果**：
[说明将生成什么样的代码和最终效果]
```

### 第四步：调用专业Sub-Agent
分析完成后，ADK会自动处理sub_agents之间的转发，你只需要在分析后**直接进行相应的function call**：

**重要**：使用正确的ADK syntax！

Function call语法：
- 函数名：`transferToAgent` 
- 参数名：`agentName`
- 可选的sub_agents：
  - "FlowArchitectExpert" - 流程架构需求
  - "DataVizExpert" - 数据可视化需求  
  - "InteractiveDynamicExpert" - 交互动态需求
  - "ConceptualMindExpert" - 思维概念需求
  - "DocumentChartExpert" - 文档图表需求

## 💡 智能决策原则
1. **需求优先**：始终以用户真实需求为中心
2. **专业匹配**：选择最匹配的专业领域专家
3. **技术适配**：考虑技术复杂度和实现可行性
4. **用户体验**：确保提供清晰的分析和说明
5. **质量保证**：每个专家都会提供高质量的专业代码

## 🔧 工作示例

**用户输入**："我需要一个用户注册流程图"
**你的分析**：这是业务流程设计需求
**选择专家**：FlowArchitectExpert
**ADK转发**：transferToAgent(agentName="FlowArchitectExpert")

**用户输入**："用我的销售数据做个趋势分析图"
**你的分析**：这是数据可视化需求
**选择专家**：DataVizExpert  
**ADK转发**：transferToAgent(agentName="DataVizExpert")

**用户输入**："我要一个会动的3D数据展示"
**你的分析**：这是交互动态需求
**选择专家**：InteractiveDynamicExpert
**ADK转发**：transferToAgent(agentName="InteractiveDynamicExpert")

**用户输入**："我想画个知识管理系统的思维导图"
**你的分析**：这是思维概念需求
**选择专家**：ConceptualMindExpert
**ADK转发**：transferToAgent(agentName="ConceptualMindExpert")

**用户输入**："我需要为业务报告制作专业图表"
**你的分析**：这是文档图表需求
**选择专家**：DocumentChartExpert
**ADK转发**：transferToAgent(agentName="DocumentChartExpert")

准备好开始智能协调工作了吗？我会仔细分析每个需求，选择最合适的专家为您服务！🚀
"""
    
    # 创建分析工具
    analysis_tool = LLMAnalysisOrchestrator()
    
    # 创建智能协调Agent - 使用ADK标准sub_agents模式 + Deepseek模型
    coordinator = LlmAgent(
        name="ChartCoordinatorAI",
        model=LiteLlm(model=os.getenv('DEFAULT_MODEL', 'deepseek/deepseek-chat')),
        instruction=instruction,
        description="🧠 智能图表协调系统，自动分析需求并调用专业Sub-Agent生成高质量代码",
        tools=[analysis_tool],
        # 关键：使用ADK标准的sub_agents模式
        sub_agents=[flow_architect_agent, data_viz_agent, interactive_agent, conceptual_mind_agent, document_chart_agent]
    )
    
    logger.info("✅ ChartCoordinatorAI 智能协调系统创建成功")
    logger.info(f"📋 已配置{len(coordinator.sub_agents)}个专业Sub-Agent")
    
    return coordinator


async def main():
    """主函数 - LLM驱动图表系统入口"""
    
    print("🧠 启动LLM驱动智能图表生成系统...")
    print("=" * 60)
    
    # 检查API key配置 - 现在使用Deepseek
    api_key = os.getenv('DEEPSEEK_API_KEY')
    if not api_key or api_key == 'your_deepseek_api_key_here':
        print("⚠️  请在.env文件中配置正确的DEEPSEEK_API_KEY")
        print("💡 获取API密钥：https://platform.deepseek.com/")
        return
    
    try:
        # 创建LLM驱动的协调Agent
        chart_coordinator = create_llm_driven_chart_coordinator()
        
        # 创建Runner
        runner = Runner(
            app_name="LLMDrivenChartSystem",
            agent=chart_coordinator,
            session_service=InMemorySessionService(),
            memory_service=InMemoryMemoryService()
        )
        
        print("✅ LLM驱动系统启动成功!")
        print(f"🧠 主协调Agent: {chart_coordinator.name}")
        print(f"🔧 AI模型: {chart_coordinator.model}")
        print(f"👥 专业Sub-Agents: {len(chart_coordinator.sub_agents)}个")
        
        # 显示Sub-Agent信息
        for i, sub_agent in enumerate(chart_coordinator.sub_agents, 1):
            print(f"   {i}. {sub_agent.name} - {sub_agent.description}")
        
        print("\n🌟 系统特色：")
        print("🤖 **完全LLM驱动** - 智能分析需求并自动选择专家")
        print("🏗️ **ADK标准架构** - 使用sub_agents模式，无硬编码路由")
        print("🧠 **智能决策** - LLM自主判断并调用最合适的专家")
        print("📊 **全领域覆盖** - 流程架构、数据可视化、交互动态")
        print("🛠️ **多格式支持** - 11种主流制图技术栈")
        
        print("\n📝 使用方式：")
        print("1. 直接描述你的需求（可以很模糊）")
        print("2. 协调中心会智能分析并选择最合适的专家")
        print("3. 专业Sub-Agent生成完整可执行的代码")
        print("4. 获得专业级的图表代码和使用指导")
        
        return runner
        
    except Exception as e:
        logger.error(f"系统运行错误: {e}")
        print(f"❌ 系统错误: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())

# 导出核心组件
__all__ = [
    'create_llm_driven_chart_coordinator',
    'LLMAnalysisOrchestrator'
] 