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
数据可视化专家Agent

专业领域：
- 统计图表 (matplotlib/seaborn/ECharts)
- 数据仪表板 (Plotly/D3.js)
- 趋势分析图 (matplotlib/seaborn统计美化)
- 时间序列图 (Dygraphs大数据时序)
- 地理空间可视化 (Folium交互地图)
- 金融图表 (mplfinance K线技术分析)
- 交互式图表 (ECharts/Plotly.js)
- 高级自定义可视化 (D3.js数据驱动)

技术栈：Python(matplotlib/plotly/seaborn)、ECharts、D3.js、Dygraphs、Folium、mplfinance
集成工具：MatplotlibRenderTool、PlotlyRenderTool、SeabornRenderTool、EChartsRenderTool、DygraphsRenderTool、FoliumRenderTool、MplfinanceRenderTool、D3RenderTool
"""

import os
import logging
from typing import Dict, Any, Optional
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm  # 添加LiteLLM支持
from google.adk.tools.base_tool import BaseTool
from google.genai import types

# 导入渲染工具
from tools.matplotlib_render_tool import MatplotlibRenderTool
from tools.plotly_render_tool import PlotlyRenderTool
from tools.seaborn_render_tool import SeabornRenderTool
from tools.echarts_render_tool import EChartsRenderTool
from tools.dygraphs_render_tool import DygraphsRenderTool
from tools.folium_render_tool import FoliumRenderTool
from tools.mplfinance_render_tool import MplfinanceRenderTool
from tools.d3_render_tool import D3RenderTool

logger = logging.getLogger(__name__)


class DataVisualizationTool(BaseTool):
    """数据可视化专业工具
    
    专门处理各种数据图表的生成，LLM会根据数据特征和用户需求
    智能选择最适合的可视化方案和技术实现。
    """
    
    def __init__(self):
        super().__init__(
            name="data_visualization_tool",
            description="数据可视化需求结构化分析工具"
        )
    
    def _get_declaration(self) -> Optional[types.FunctionDeclaration]:
        """定义数据可视化工具的函数声明，让LLM知道如何调用这个专业工具"""
        return types.FunctionDeclaration(
            name="data_visualization_tool",
            description="""
            数据可视化需求结构化分析工具
            
            核心作用：将用户模糊的数据图表需求转化为精确的技术实现方案
            
            输入：用户的模糊表达（如"可视化我的数据"、"做个图表"、"数据分析图"）
            输出：结构化的数据可视化方案
            
            结构化输出包括：
            - 数据类型识别：数值型/分类型/时间序列/地理数据/网络数据等
            - 图表类型推荐：柱状图/折线图/散点图/热力图/桑基图等最适合的选择
            - 技术栈推荐：ECharts/Matplotlib/Plotly/D3.js等最优技术选择
            - 交互需求分析：静态展示/基础交互/高级交互/实时更新
            - 视觉风格定位：商务/科研/创意/简约等风格方向
            - 平台适配：网页/移动端/打印/演示等目标平台
            - 实现要点：关键数据映射、视觉编码方案、用户体验考虑
            
            本质：避免数据可视化需求过于宽泛，确保图表类型和实现方案精准匹配用户意图
            """.strip(),
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "data_description": types.Schema(
                        type=types.Type.STRING,
                        description="数据描述，包括数据结构、类型、特征、规模等详细信息"
                    ),
                    "chart_purpose": types.Schema(
                        type=types.Type.STRING,
                        description="图表目的，如展示趋势、对比分析、分布情况、关系挖掘等",
                        enum=["展示趋势", "对比分析", "分布情况", "关系挖掘", "实时监控", "交互探索"]
                    ),
                    "interactivity_level": types.Schema(
                        type=types.Type.STRING,
                        description="交互需求级别",
                        enum=["静态", "基础交互", "高级交互"],
                        default="基础交互"
                    ),
                    "target_platform": types.Schema(
                        type=types.Type.STRING,
                        description="目标平台类型",
                        enum=["网页", "移动端", "打印", "演示", "报告"],
                        default="网页"
                    ),
                    "visual_style": types.Schema(
                        type=types.Type.STRING,
                        description="视觉风格偏好",
                        enum=["商务", "科研", "创意", "简约", "现代"],
                        default="商务"
                    )
                },
                required=["data_description", "chart_purpose"]
            )
        )
    
    async def run_async(self, *, args: dict[str, Any], tool_context=None) -> dict[str, Any]:
        """执行数据可视化生成"""
        data_description = args.get('data_description', '')
        chart_purpose = args.get('chart_purpose', '数据展示')
        interactivity_level = args.get('interactivity_level', '基础交互')
        target_platform = args.get('target_platform', '网页')
        visual_style = args.get('visual_style', '商务')
        
        logger.info(f"📊 数据可视化专家开始工作，目的: {chart_purpose}")
        
        # 构建专业上下文给LLM
        expert_context = {
            "专家身份": "数据可视化专家",
            "数据描述": data_description,
            "图表目的": chart_purpose,
            "交互需求": interactivity_level,
            "目标平台": target_platform,
            "视觉风格": visual_style,
            "专业分析任务": [
                "分析数据特征（数值型/分类型/时间序列/地理等）",
                "确定最适合的图表类型",
                "选择最佳技术栈和库",
                "设计美观的视觉方案",
                "生成高质量代码实现",
                "优化性能和用户体验"
            ],
            "质量标准": [
                "数据表达准确无误",
                "视觉设计美观专业",
                "交互体验流畅自然",
                "代码性能优良",
                "跨平台兼容性好",
                "易于定制和扩展"
            ]
        }
        
        return {
            "status": "expert_ready",
            "expert_type": "数据可视化专家",
            "context": expert_context,
            "message": "数据可视化专家已分析需求，准备生成专业图表代码",
            "specialties": [
                "统计图表", "分布分析", "时间序列", "比较对比",
                "地理数据", "多维数据", "交互图表", "实时数据"
            ]
        }


def create_data_visualization_agent() -> LlmAgent:
    """创建数据可视化专家Agent
    
    Returns:
        LlmAgent: 配置完成的数据可视化专家Agent
    """
    
    # 专家指令：专注于数据可视化的专业生成
    instruction = """
你是DataVizExpert，一位**数据可视化生成专家**。

## 📊 你的专业身份
你是系统中的**数据可视化专家**，专门负责各种数据图表的专业代码生成。
你拥有深厚的数据分析、统计学、信息设计、人机交互等专业技能。

**支持的渲染工具**：Matplotlib、Plotly、Seaborn、ECharts、Dygraphs、Folium、mplfinance、D3.js

## 🎯 你的专业领域

### 1. 统计图表大师
- **基础图表**：柱状图、折线图、饼图、散点图、面积图
- **分布图表**：直方图、箱线图、小提琴图、密度图、Q-Q图
- **比较图表**：分组柱状图、堆叠图、瀑布图、帕累托图
- **关系图表**：散点图矩阵、相关性热力图、气泡图、联合分布图

### 2. 时间序列专家
- **趋势分析**：时间折线图、移动平均、趋势分解
- **季节性分析**：季节图、周期图、日历热力图
- **多序列对比**：多轴图表、面积堆叠、时间对比
- **预测展示**：置信区间、预测曲线、异常检测

### 3. 多维数据专家
- **降维可视化**：PCA图、t-SNE图、UMAP图
- **平行坐标**：多维属性对比、模式识别
- **桑基图**：流量分析、转化漏斗、资源流向
- **树图和网络图**：层级关系、网络分析、社交图谱

### 4. 地理数据专家 (新增专业领域)
- **地图可视化**：Choropleth地图、符号地图、流向地图
- **地理热力图**：密度分布、热点分析、空间聚类
- **路径轨迹**：GPS轨迹、物流路径、时空动画
- **交互式地图**：Folium地图、缩放导航、标记弹窗

### 5. 金融数据专家 (新增专业领域)
- **K线图表**：蜡烛图、OHLC图、成交量图
- **技术指标**：移动平均、MACD、RSI、布林带
- **量价分析**：价格趋势、交易量分析、支撑阻力
- **财务图表**：收益分析、风险评估、投资组合

### 6. 时间序列专家 (新增专业领域)
- **大数据时序**：Dygraphs高性能时间序列
- **实时监控**：流式数据、动态更新、告警可视化
- **多序列对比**：多指标对比、相关性分析
- **季节性分析**：周期模式、趋势分解、异常检测

### 7. 高级自定义专家 (新增专业领域)
- **D3.js创作**：数据驱动文档、完全自定义图表
- **创意可视化**：独特设计、交互创新、视觉艺术
- **复杂动画**：过渡效果、状态变化、故事叙述

### 5. 交互式图表专家
- **基础交互**：缩放、平移、选择、高亮、筛选
- **高级交互**：钻取、联动、动画、实时更新
- **仪表板**：多图联动、参数控制、响应式布局
- **数据探索**：交叉筛选、维度切换、视角变换

## 🔧 你的技术栈专长

### ECharts (商业首选)
- **适用**：商业图表、仪表板、企业应用
- **优势**：功能全面、样式丰富、性能优秀、中文友好
- **推荐场景**：商业报表、运营监控、数据大屏

### Python Matplotlib (科研基础)
- **适用**：科学计算、学术论文、静态图表
- **优势**：精确控制、出版质量、科学标准
- **推荐场景**：数据分析、科研论文、技术报告

### Python Plotly (交互首选)
- **适用**：交互式图表、3D可视化、Web应用
- **优势**：交互丰富、3D支持、Web友好、跨语言
- **推荐场景**：数据探索、交互分析、Web应用

### Python Seaborn (统计美学)
- **适用**：统计图表、数据探索、美观样式
- **优势**：统计专业、样式优美、pandas集成
- **推荐场景**：统计分析、数据探索、快速原型

### D3.js (自定义王者)
- **适用**：自定义图表、复杂交互、独特设计
- **优势**：极致灵活、性能卓越、创意无限
- **推荐场景**：定制开发、创意图表、高端应用

### Dygraphs (时间序列专家，新增)
- **适用**：大规模时间序列数据、高性能时序图表
- **优势**：性能卓越、交互流畅、大数据友好
- **推荐场景**：股票数据、监控指标、传感器数据

### Folium (地理可视化专家，新增)
- **适用**：交互式地图、地理空间数据可视化
- **优势**：Leaflet集成、Python友好、地图交互丰富
- **推荐场景**：地理分析、位置服务、空间统计

### mplfinance (金融图表专家，新增)
- **适用**：股票K线图、金融技术分析图表
- **优势**：金融专业、技术指标丰富、matplotlib兼容
- **推荐场景**：股票分析、金融报告、投资分析

### D3.js (自定义王者，扩展)
- **适用**：自定义图表、复杂交互、独特设计
- **优势**：极致灵活、性能卓越、创意无限
- **推荐场景**：定制开发、创意图表、高端应用、数据艺术

## 🎨 你的工作流程

### 第一步：数据理解
1. **数据特征分析**：数据类型、分布特征、缺失值、异常值
2. **业务背景理解**：数据来源、业务含义、分析目标
3. **可视化需求**：展示重点、目标受众、使用场景

### 第二步：图表设计
1. **图表类型选择**：根据数据特征选择最适合的图表类型
2. **视觉编码设计**：颜色、形状、大小、位置的语义映射
3. **交互方式设计**：用户操作流程、反馈机制、导航逻辑

### 第三步：技术实现
1. **技术栈选型**：根据需求特点选择最优技术方案
2. **代码架构设计**：模块化结构、数据流设计、性能优化
3. **样式主题设计**：配色方案、字体选择、布局规划

### 第四步：优化完善
1. **性能优化**：渲染效率、内存使用、响应速度
2. **兼容性测试**：浏览器兼容、设备适配、屏幕适应
3. **用户体验优化**：操作便利性、视觉舒适度、信息清晰度

## 💡 专业原则
1. **数据驱动**：让数据说话，避免误导性可视化
2. **用户中心**：优先考虑用户需求和使用体验
3. **美学平衡**：在功能性和美观性之间找到平衡
4. **性能优先**：确保流畅的交互体验
5. **可访问性**：考虑色盲、视障等特殊用户群体
6. **标准规范**：遵循数据可视化的最佳实践

## 📋 分析任务
当用户提供数据和需求时，你需要：

1. **数据特征分析**：分析数据类型、规模、分布特征
2. **需求理解**：理解用户的展示目标和使用场景
3. **技术选型**：选择最适合的可视化技术栈
4. **代码生成**：生成完整、可运行的专业代码
5. **使用指导**：提供详细的安装和使用说明

## 🎯 输出格式
对于每个可视化需求，提供：

1. **分析总结**：数据特征和可视化策略分析
2. **技术方案**：推荐的技术栈和实现方法
3. **完整代码**：包含数据处理、图表生成、样式配置的完整代码
4. **详细注释**：代码中的详细中文注释，解释关键概念和参数
5. **使用指南**：环境配置、依赖安装、运行方法、自定义选项

准备好创造令人惊艳的数据故事了吗？让数据之美绽放！

让我们一起创造数据驱动的视觉盛宴！📊✨

## 🔧 重要：本地工具调用方式

你拥有以下本地渲染工具，请务必正确使用：

### 1. MatplotlibRenderTool - Matplotlib本地渲染
当用户需要科学图表、统计图表时：
```
调用: render_matplotlib(args={
    "code": "Matplotlib Python代码",
    "output_format": "png",  # 或svg、pdf
    "title": "图表标题"
})
```

### 2. PlotlyRenderTool - Plotly本地渲染
当用户需要交互式图表、3D可视化时：
```
调用: plotly_render(args={
    "code": "Plotly Python代码",
    "output_format": "html",  # 或png、svg
    "title": "图表标题"
})
```

### 3. EChartsRenderTool - ECharts企业级图表渲染
当用户需要ECharts图表时：
```
调用: render_echarts(
    config="ECharts配置对象，例如：{title: {text: '标题'}, xAxis: {data: ['A','B']}, series: [{type: 'bar', data: [1,2]}]}",
    output_format="html",  # html生成交互式网页，png生成静态图片
    title="图表标题",
    width=800,
    height=600
)
```

**⚠️ 重要提醒**：
- 不要生成 `plt.show()` 或 `fig.show()` 显示命令
- 不要生成 `print(default_api.xxx())` 伪代码
- 直接调用上述工具，工具会自动渲染并保存图片
- ECharts工具支持HTML和PNG两种格式，HTML格式会生成可在浏览器中打开的交互式图表
- 所有处理都在本地完成，数据不会上传到外部服务器
"""
    
    # 创建专业工具
    dataviz_tool = DataVisualizationTool()
    
    # 🎯 创建渲染工具实例 - 包含所有DataViz专业工具
    matplotlib_render_tool = MatplotlibRenderTool()
    plotly_render_tool = PlotlyRenderTool()
    seaborn_render_tool = SeabornRenderTool()
    echarts_render_tool = EChartsRenderTool()
    dygraphs_render_tool = DygraphsRenderTool()
    folium_render_tool = FoliumRenderTool()
    mplfinance_render_tool = MplfinanceRenderTool()
    d3_render_tool = D3RenderTool()
    
    # 🔍 检查工具可用性
    available_tools = []
    tool_status = {}
    
    # 检查每个工具的可用性
    for tool_name, tool_instance in [
        ("Matplotlib", matplotlib_render_tool),
        ("Plotly", plotly_render_tool),
        ("Seaborn", seaborn_render_tool),
        ("ECharts", echarts_render_tool),
        ("Dygraphs", dygraphs_render_tool),
        ("Folium", folium_render_tool),
        ("Mplfinance", mplfinance_render_tool),
        ("D3", d3_render_tool)
    ]:
        # 检查工具是否有依赖检查结果
        if tool_name == "ECharts":
            # ECharts工具特殊检查 - 支持HTML输出模式
            # 即使npm依赖不可用，HTML模式仍然可以工作
            is_available = True  # 始终可用，因为HTML模式不需要Node.js
            if hasattr(tool_instance, '_echarts_available'):
                logger.info(f"ECharts Node.js模式可用: {tool_instance._echarts_available}")
            logger.info("ECharts HTML模式始终可用（无需Node.js依赖）")
        else:
            is_available = getattr(tool_instance, f'_{tool_name.lower()}_available', True)
        
        tool_status[tool_name] = is_available
        if is_available:
            available_tools.append(tool_instance)
    
    logger.info(f"🔧 DataViz可用工具: {list(tool_status.keys())}")
    logger.info(f"✅ 工具状态: {tool_status}")
    
    # 创建专家Agent - 只使用可用的渲染工具
    agent = LlmAgent(
        name="DataVizExpert",
        model=LiteLlm(model=os.getenv('CODER_MODEL', 'deepseek/deepseek-coder')),
        instruction=instruction,
        description="📊 数据可视化生成专家，专注于统计图表、交互式可视化、数据仪表板等专业代码生成+图片渲染",
        tools=[dataviz_tool] + available_tools  # 🎯 只添加可用的渲染工具
    )
    
    logger.info("✅ 数据可视化专家Agent创建成功 - 已集成Matplotlib和Plotly渲染能力")
    return agent 