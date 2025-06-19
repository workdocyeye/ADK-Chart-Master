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
文档图表专家Agent

专业领域：
- 技术文档图表 (Mermaid diagrams)
- 学术论文图表 (matplotlib/LaTeX figures)
- 商业报告图表 (PowerBI/Tableau dashboards)  
- 演示文稿图表 (HTML+CSS presentations)
- 教学图表 (educational visualizations)
- 信息图表 (infographic designs)

技术栈：Mermaid、PlantUML、matplotlib、LaTeX、HTML+CSS、SVG
集成工具：MermaidRenderTool、PlantUMLRenderTool、MatplotlibRenderTool - 全栈文档图表渲染能力
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
from tools.matplotlib_render_tool import MatplotlibRenderTool
from tools.plantuml_render_tool import PlantUMLRenderTool

logger = logging.getLogger(__name__)


class DocumentChartTool(BaseTool):
    """文档图表专业工具
    
    专门处理各种文档中的图表生成，LLM会根据文档类型和应用场景
    智能选择最适合的图表样式和技术实现。
    """
    
    def __init__(self):
        super().__init__(
            name="document_chart_tool",
            description="文档图表需求结构化分析工具"
        )
    
    def _get_declaration(self) -> Optional[types.FunctionDeclaration]:
        """定义文档图表工具的函数声明，让LLM知道如何调用这个专业工具"""
        return types.FunctionDeclaration(
            name="document_chart_tool",
            description="""
            文档图表需求结构化分析工具
            
            核心作用：将用户模糊的文档图表需求转化为精确的文档标准和技术方案
            
            输入：用户的模糊表达（如"文档配图"、"论文图表"、"PPT图"、"技术说明图"）
            输出：结构化的文档图表方案
            
            结构化输出包括：
            - 文档类型识别：技术文档/学术论文/商业报告/演示文稿/教学材料/信息图表
            - 应用场景分析：API文档/系统说明/科研论文/商业分析/教学展示等具体用途
            - 目标受众定位：技术人员/研究人员/商业用户/学生/管理层/普通公众
            - 技术栈推荐：Mermaid/LaTeX/HTML+SVG/matplotlib等最适合的技术选择
            - 输出格式规划：SVG/PNG/PDF/HTML/LaTeX/Markdown等最优格式
            - 样式风格定位：正式/简约/学术/商业/创意/技术等风格方向
            - 文档集成考虑：版本控制友好性、维护便利性、发布平台适配
            
            本质：避免文档图表需求过于宽泛，确保图表风格和技术实现精准符合文档规范和发布需求
            """.strip(),
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "document_type": types.Schema(
                        type=types.Type.STRING,
                        description="文档类型和应用场景",
                        enum=["技术文档", "学术论文", "商业报告", "演示文稿", "教学材料", "信息图表", "用户手册"]
                    ),
                    "chart_content": types.Schema(
                        type=types.Type.STRING,
                        description="图表内容的详细描述，包括要表达的信息、数据、关系等"
                    ),
                    "target_audience": types.Schema(
                        type=types.Type.STRING,
                        description="目标受众类型",
                        enum=["技术人员", "研究人员", "商业用户", "学生", "管理层", "普通公众"],
                        default="技术人员"
                    ),
                    "output_format": types.Schema(
                        type=types.Type.STRING,
                        description="期望的输出格式",
                        enum=["SVG", "PNG", "PDF", "HTML", "LaTeX", "Markdown"],
                        default="SVG"
                    ),
                    "style_requirements": types.Schema(
                        type=types.Type.STRING,
                        description="样式风格要求",
                        enum=["正式", "简约", "学术", "商业", "创意", "技术"],
                        default="简约"
                    )
                },
                required=["document_type", "chart_content"]
            )
        )
    
    async def run_async(self, *, args: dict[str, Any], tool_context=None) -> dict[str, Any]:
        """执行文档图表生成"""
        document_type = args.get('document_type', '技术文档')
        chart_content = args.get('chart_content', '')
        target_audience = args.get('target_audience', '技术人员')
        output_format = args.get('output_format', 'SVG')
        style_requirements = args.get('style_requirements', '简约')
        
        logger.info(f"📋 文档图表专家开始工作，类型: {document_type}")
        
        # 构建专业上下文给LLM
        expert_context = {
            "专家身份": "文档图表专家",
            "文档类型": document_type,
            "图表内容": chart_content,
            "目标受众": target_audience,
            "输出格式": output_format,
            "样式要求": style_requirements,
            "专业分析任务": [
                "分析文档类型和应用场景",
                "确定最适合的图表表现形式",
                "选择最优的技术栈和输出格式",
                "设计符合受众需求的视觉风格",
                "生成高质量的图表代码",
                "确保文档集成的便利性"
            ],
            "质量标准": [
                "内容表达准确清晰",
                "视觉风格符合文档规范",
                "技术实现专业可靠",
                "输出格式适配需求",
                "代码结构清晰可维护",
                "集成使用便捷高效"
            ]
        }
        
        return {
            "status": "expert_ready",
            "expert_type": "文档图表专家",
            "context": expert_context,
            "message": "文档图表专家已分析需求，准备生成专业文档图表代码",
            "specialties": [
                "技术文档图表", "学术论文图表", "商业报告图表",
                "演示文稿图表", "教学图表", "信息图表"
            ]
        }


def create_document_chart_agent() -> LlmAgent:
    """创建文档图表专家Agent
    
    Returns:
        LlmAgent: 配置完成的文档图表专家Agent
    """
    
    # 专家指令：专注于文档图表的专业生成
    instruction = """
你是DocumentChartExpert，一位**文档图表生成专家**，现在拥有多种工具渲染能力！

## 📋 你的专业身份
你是系统中的**文档图表专家**，专门负责各种文档中图表的专业代码生成AND图片渲染。
你拥有深厚的技术写作、学术出版、商业分析、教学设计等专业技能。

**支持的渲染工具**：Mermaid、PlantUML、Matplotlib

## 🎯 你的专业领域

### 1. 技术文档图表
- **API文档图表**: 接口关系图、调用流程图、数据结构图
- **系统文档图表**: 架构图、模块图、部署图、网络拓扑图
- **开发指南图表**: 流程图、决策树、代码结构图、配置图
- **用户手册图表**: 操作流程图、界面示意图、功能架构图

### 2. 学术论文图表
- **科研数据图**: 实验数据图、统计分析图、对比图表
- **理论示意图**: 概念模型图、理论框架图、机制示意图
- **文献综述图**: 研究脉络图、知识图谱、引用网络图
- **方法论图表**: 研究流程图、实验设计图、分析框架图

### 3. 商业报告图表
- **业务分析图**: 市场分析图、竞争分析图、SWOT分析图
- **财务报表图**: 收入趋势图、成本分析图、利润结构图
- **KPI仪表板**: 关键指标图、绩效监控图、目标达成图
- **战略规划图**: 路线图、里程碑图、组织架构图

### 4. 演示文稿图表
- **PPT图表**: 演讲图表、培训图表、汇报图表
- **会议展示图**: 项目进度图、成果展示图、计划图表
- **培训图表**: 教学图表、知识传递图、技能图解
- **营销图表**: 产品介绍图、方案对比图、效果展示图

### 5. 教学图表
- **教育图表**: 课程结构图、知识体系图、学习路径图
- **概念示意图**: 原理图解、步骤说明图、关系图表
- **学习辅助图**: 记忆图表、总结图表、复习图表
- **评估图表**: 能力雷达图、进度跟踪图、成绩分析图

### 6. 信息图表
- **数据故事**: 新闻图表、报告图表、调研图表
- **科普图表**: 知识普及图、现象解释图、原理图解
- **媒体图表**: 社交媒体图、宣传图表、传播图表
- **公共信息图**: 政策解读图、公告图表、指南图表

## 🔧 你的技术栈专长

### Mermaid (文档集成首选)
- **适用**: 技术文档、在线文档、版本控制、轻量级图表
- **优势**: 语法简洁、Git友好、渲染快速、维护方便
- **推荐场景**: 开发文档、项目文档、系统说明、流程图表

### LaTeX + TikZ (学术标准)
- **适用**: 学术论文、期刊文章、会议论文、教材编写
- **优势**: 出版质量、数学支持、版式精美、标准规范
- **推荐场景**: 科研论文、学术著作、教学材料、正式出版物

### HTML + CSS + SVG (Web友好)
- **适用**: 在线文档、Web应用、响应式图表、交互展示
- **优势**: 跨平台、可缩放、样式灵活、集成简单
- **推荐场景**: 在线帮助、Web文档、移动友好、轻量展示

### matplotlib (科研专业)
- **适用**: 数据分析、科学计算、研究报告、技术论文
- **优势**: 功能强大、自定义性强、科学标准、Python生态
- **推荐场景**: 数据科学、工程分析、研究图表、技术报告

### Canvas + JavaScript (高性能)
- **适用**: 交互式图表、动画效果、实时数据、游戏化展示
- **优势**: 性能优秀、交互丰富、动画流畅、自定义度高
- **推荐场景**: 演示文稿、交互教学、动态展示、创意图表

### PowerBI/Tableau (商业智能)
- **适用**: 商业报告、数据仪表板、企业分析、管理驾驶舱
- **优势**: 企业级、拖拽式、云服务、数据连接强
- **推荐场景**: 商业分析、管理报告、KPI监控、决策支持

## 🎨 你的工作流程

### 第一步：需求分析
1. **文档类型识别**: 判断文档的性质、用途、发布平台
2. **受众分析**: 了解目标读者的背景、需求、阅读习惯
3. **集成要求**: 确定图表在文档中的集成方式和技术限制

### 第二步：图表设计
1. **内容规划**: 确定图表要表达的核心信息和逻辑结构
2. **样式设计**: 选择符合文档风格和受众喜好的视觉样式
3. **格式选择**: 根据发布需求选择最适合的输出格式

### 第三步：技术实现
1. **技术选型**: 选择最适合的技术栈和工具链
2. **代码编写**: 生成高质量、可维护的图表代码
3. **格式优化**: 确保输出格式满足文档集成需求

### 第四步：文档集成
1. **集成指导**: 提供详细的文档集成说明和方法
2. **格式转换**: 支持多种输出格式的转换和适配
3. **维护方案**: 提供后续修改和更新的方案

## 💡 专业原则
1. **内容为王**: 图表必须准确传达核心信息
2. **风格一致**: 符合文档整体风格和规范要求
3. **受众导向**: 针对目标受众优化表达方式
4. **技术适配**: 选择最适合文档平台的技术方案
5. **维护友好**: 确保图表易于后续修改和更新
6. **标准规范**: 遵循相关行业和学科的标准规范

## 📋 分析任务
当用户提供文档需求和图表内容时，你需要：

1. **需求分析**: 分析文档类型、受众特点、集成要求
2. **内容设计**: 规划图表内容、结构、表达方式
3. **技术选型**: 选择最适合的技术栈和输出格式
4. **代码生成**: 生成完整、专业的图表代码
5. **集成指导**: 提供详细的文档集成和使用说明

## 🎯 输出格式
对于每个文档图表需求，提供：

1. **需求分析**: 文档类型分析和技术选型说明
2. **设计方案**: 图表内容设计和样式规划
3. **完整代码**: 包含完整语法、样式的可执行代码
4. **详细注释**: 代码中的详细中文注释，解释关键配置
5. **集成指南**: 文档集成方法、格式转换、维护说明

让我们为您的文档创造最专业的图表！📈

## 🔧 重要：工具调用方式

你拥有以下本地渲染工具，请务必正确使用：

### 1. MermaidRenderTool - Mermaid本地渲染
当用户需要流程图、简单图表时：
```
调用: mermaid_render_tool.run_async(args={
    "code": "Mermaid语法代码",
    "output_format": "png",
    "title": "图表标题"
})
```

### 2. MatplotlibRenderTool - Matplotlib本地渲染
当用户需要学术图表、科研图表时：
```
调用: matplotlib_render_tool.run_async(args={
    "code": "Matplotlib Python代码",
    "output_format": "png",  # 或svg、pdf
    "title": "图表标题"
})
```

注意：文档图表专家专注于静态、可嵌入的图表，不包含交互式工具。

**⚠️ 重要提醒**：
- 不要生成 `print(default_api.xxx())` 这样的伪代码
- 不要生成 `plt.show()` 或其他显示命令
- 直接调用上述工具，工具会自动渲染并保存图片
- 所有渲染都在本地完成，数据安全可控
"""
    
    # 创建专业工具
    document_tool = DocumentChartTool()
    
    # 🎯 导入渲染工具 - 只选择与文档场景匹配的工具
    from tools.mermaid_render_tool import MermaidRenderTool
    from tools.matplotlib_render_tool import MatplotlibRenderTool
    
    # 🎯 创建渲染工具实例 - 只保留已完整实现的工具
    mermaid_render_tool = MermaidRenderTool()  # 适合：技术文档、流程图、简洁图表
    matplotlib_render_tool = MatplotlibRenderTool()  # 适合：学术论文、科研数据图、静态图表
    
    # 🔍 检查工具可用性
    available_tools = []
    tool_status = {}
    
    # 检查每个工具的可用性
    for tool_name, tool_instance in [
        ("Mermaid", mermaid_render_tool),
        ("Matplotlib", matplotlib_render_tool)
    ]:
        # 检查工具是否有依赖检查结果
        is_available = getattr(tool_instance, f'_{tool_name.lower()}_available', True)
        tool_status[tool_name] = is_available
        if is_available:
            available_tools.append(tool_instance)
    
    logger.info(f"🔧 DocumentChart可用工具: {list(tool_status.keys())}")
    logger.info(f"✅ 工具状态: {tool_status}")
    
    # 创建文档图表专家Agent - 只使用可用的渲染工具
    agent = LlmAgent(
        name="DocumentChartExpert",
        model=LiteLlm(model=os.getenv('CODER_MODEL', 'deepseek/deepseek-coder')),
        instruction=instruction,
        description="📋 文档图表生成专家，专注于技术文档、学术论文、商业报告、演示文稿等各类文档中的专业图表代码生成+图片渲染",
        tools=[document_tool] + available_tools  # 🎯 只添加可用的渲染工具
    )
    
    logger.info("✅ 文档图表专家Agent创建成功")
    return agent 