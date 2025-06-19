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
交互动态图表专家Agent

专业领域：
- 动画效果图 (CSS3+JS animations, Canvas动画)
- 实时数据图 (WebSocket+Chart.js, D3.js streaming)
- 游戏化图表 (Canvas games, 交互式体验)
- 3D可视化 (Three.js, WebGL)
- 移动端交互图表 (F2 AntV, 触屏优化)
- 动态仪表板 (实时更新、参数联动)
- 响应式交互 (触摸手势、多设备适配)

技术栈：Canvas、WebGL、Three.js、D3.js、CSS3、HTML5、WebSocket、F2 AntV
集成工具：PlotlyRenderTool、EChartsRenderTool、ThreeJSRenderTool、DygraphsRenderTool
"""

import os
import logging
from typing import Dict, Any, Optional
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm  # 添加LiteLLM支持
from google.adk.tools.base_tool import BaseTool
from google.genai import types

logger = logging.getLogger(__name__)


class InteractiveDynamicTool(BaseTool):
    """交互动态图表专业工具
    
    专门处理各种交互式和动态图表的生成，LLM会根据交互需求和性能要求
    智能选择最适合的动画技术和实现方案。
    """
    
    def __init__(self):
        super().__init__(
            name="interactive_dynamic_tool",
            description="交互动态图表需求结构化分析工具"
        )
    
    def _get_declaration(self) -> Optional[types.FunctionDeclaration]:
        """定义交互动态图表工具的函数声明，让LLM知道如何调用这个专业工具"""
        return types.FunctionDeclaration(
            name="interactive_dynamic_tool",
            description="""
            交互动态需求结构化分析工具
            
            核心作用：将用户模糊的交互动态需求转化为精确的技术实现规格
            
            输入：用户的模糊表达（如"要动态的"、"实时更新"、"3D效果"、"游戏化"）
            输出：结构化的交互动态方案
            
            结构化输出包括：
            - 交互类型识别：动画效果/实时数据/3D可视化/游戏化图表等
            - 性能要求评估：流畅/高性能/移动端友好/极致优化级别判断
            - 技术栈推荐：Canvas/WebGL/Three.js/D3.js等最优选择
            - 更新机制设计：静态/定期/实时/流式数据更新方案
            - 设备适配方案：桌面/移动端/平板/VR等目标设备考虑
            - 动画复杂度定位：简单/中等/复杂/电影级效果规划
            - 实现要点：关键技术点、性能优化策略、用户体验设计
            
            本质：避免交互动态需求表达不清，确保技术方案与用户期望的交互体验精准匹配
            """.strip(),
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "interaction_type": types.Schema(
                        type=types.Type.STRING,
                        description="交互类型和特效需求",
                        enum=["动画效果", "实时数据", "3D可视化", "游戏化图表", "高性能渲染", "多设备适配", "协作交互"]
                    ),
                    "performance_requirement": types.Schema(
                        type=types.Type.STRING,
                        description="性能要求级别",
                        enum=["流畅", "高性能", "移动端友好", "极致优化"],
                        default="流畅"
                    ),
                    "data_update_frequency": types.Schema(
                        type=types.Type.STRING,
                        description="数据更新频率",
                        enum=["静态", "定期", "实时", "流式"],
                        default="静态"
                    ),
                    "target_devices": types.Schema(
                        type=types.Type.STRING,
                        description="目标设备类型",
                        enum=["桌面", "移动端", "平板", "VR", "多设备"],
                        default="桌面"
                    ),
                    "animation_complexity": types.Schema(
                        type=types.Type.STRING,
                        description="动画复杂度要求",
                        enum=["简单", "中等", "复杂", "电影级"],
                        default="中等"
                    )
                },
                required=["interaction_type"]
            )
        )
    
    async def run_async(self, *, args: dict[str, Any], tool_context=None) -> dict[str, Any]:
        """执行交互动态图表生成"""
        interaction_type = args.get('interaction_type', '基础交互')
        performance_requirement = args.get('performance_requirement', '流畅')
        data_update_frequency = args.get('data_update_frequency', '静态')
        target_devices = args.get('target_devices', '桌面')
        animation_complexity = args.get('animation_complexity', '中等')
        
        logger.info(f"⚡ 交互动态专家开始工作，类型: {interaction_type}")
        
        # 构建专业上下文给LLM
        expert_context = {
            "专家身份": "交互动态图表专家",
            "交互类型": interaction_type,
            "性能要求": performance_requirement,
            "更新频率": data_update_frequency,
            "目标设备": target_devices,
            "动画复杂度": animation_complexity,
            "专业分析任务": [
                "分析交互需求和用户体验目标",
                "评估性能要求和技术约束",
                "选择最适合的渲染技术",
                "设计流畅的动画效果",
                "优化性能和兼容性",
                "实现高质量交互体验"
            ],
            "质量标准": [
                "交互响应迅速流畅",
                "动画效果自然美观",
                "性能优化到位",
                "跨设备兼容性好",
                "用户体验直观友好",
                "代码架构清晰可维护"
            ]
        }
        
        return {
            "status": "expert_ready",
            "expert_type": "交互动态专家",
            "context": expert_context,
            "message": "交互动态专家已分析需求，准备生成高性能交互代码",
            "specialties": [
                "动画效果", "实时数据", "交互体验", "3D可视化",
                "游戏化图表", "高性能渲染", "多设备适配", "协作交互"
            ]
        }


def create_interactive_dynamic_agent() -> LlmAgent:
    """创建交互动态图表专家Agent
    
    Returns:
        LlmAgent: 配置完成的交互动态图表专家Agent
    """
    
    # 专家指令：专注于交互动态图表的专业生成
    instruction = """
你是InteractiveDynamicExpert，一位**交互动态图表生成专家**。

## ⚡ 你的专业身份
你是系统中的**交互动态图表专家**，专门负责各种交互式和动态图表的专业代码生成。
你拥有深厚的前端技术、动画设计、性能优化、用户体验等专业技能。

**支持的渲染工具**：Plotly、ECharts、Three.js、Dygraphs

## 🎯 你的专业领域

### 1. 动画效果大师
- **进入动画**：图表出现效果、数据加载动画、元素渐现
- **过渡动画**：状态切换、数据变化、视图转换
- **交互动画**：悬停效果、点击反馈、拖拽响应
- **循环动画**：呼吸效果、脉冲动画、旋转指示器
- **粒子效果**：数据粒子、流动效果、爆炸特效

### 2. 实时数据专家
- **流式数据**：实时股票、传感器数据、日志监控
- **数据推送**：WebSocket连接、Server-Sent Events、长轮询
- **动态更新**：图表实时刷新、平滑过渡、增量更新
- **数据缓存**：历史数据管理、滑动窗口、内存优化
- **性能监控**：帧率优化、内存管理、CPU使用率

### 3. 3D可视化专家
- **3D图表**：立体柱状图、3D散点图、曲面图、体积渲染
- **场景管理**：相机控制、光照设置、材质效果、阴影处理
- **交互控制**：轨道控制、缩放漫游、选择拾取、手势操作
- **数据映射**：3D空间坐标、颜色编码、大小映射、透明度
- **性能优化**：LOD细节层次、遮挡剔除、批处理渲染

### 4. 游戏化图表专家
- **游戏机制**：积分系统、成就解锁、进度条、排行榜
- **互动元素**：可操作组件、拖拽游戏、点击挑战
- **视觉反馈**：音效配合、震动反馈、视觉奖励
- **故事化数据**：数据叙事、情节推进、角色设定
- **社交功能**：分享机制、协作竞争、用户生成内容

### 5. 高性能渲染专家
- **Canvas优化**：离屏渲染、局部重绘、对象池、批处理
- **WebGL编程**：着色器优化、纹理管理、几何体优化
- **内存管理**：垃圾回收优化、对象复用、内存泄漏防护
- **多线程**：Web Workers、共享内存、并行计算
- **GPU加速**：硬件加速、计算着色器、并行处理

## 🔧 你的技术栈专长

### Canvas 2D (性能之王)
- **适用**：高性能2D图形、自定义绘制、动画效果
- **优势**：性能最优、控制精确、兼容性好
- **推荐场景**：实时监控、大数据图表、游戏化应用

### WebGL/Three.js (3D王者)
- **适用**：3D可视化、复杂图形、GPU加速
- **优势**：硬件加速、效果震撼、扩展性强
- **推荐场景**：3D数据、科学可视化、虚拟现实

### D3.js (交互之神)
- **适用**：数据驱动动画、复杂交互、SVG动画
- **优势**：灵活性极高、动画丰富、数据绑定
- **推荐场景**：复杂交互、自定义动画、数据故事

### CSS3 (轻量优雅)
- **适用**：轻量动画、响应式、移动端
- **优势**：性能友好、开发简单、移动优化
- **推荐场景**：简单动效、响应式图表、移动应用

### WebSocket (实时通信)
- **适用**：实时数据、多用户协作、数据推送
- **优势**：低延迟、双向通信、实时性强
- **推荐场景**：实时监控、协作应用、直播数据

## 🎨 你的工作流程

### 第一步：需求分析
1. **交互需求分析**：用户操作流程、反馈机制、体验目标
2. **性能需求评估**：数据量大小、更新频率、设备性能
3. **技术约束识别**：浏览器兼容、移动端支持、网络条件

### 第二步：技术设计
1. **架构选型**：渲染引擎选择、数据流设计、模块划分
2. **动画设计**：时间轴规划、缓动函数、关键帧设计
3. **交互设计**：事件处理、状态管理、反馈机制

### 第三步：性能优化
1. **渲染优化**：批处理、避免重排重绘、GPU加速
2. **内存优化**：对象池、垃圾回收、内存监控
3. **网络优化**：数据压缩、增量更新、缓存策略

### 第四步：用户体验
1. **响应性**：加载反馈、操作确认、错误处理
2. **可访问性**：键盘导航、屏幕阅读器、色彩对比
3. **设备适配**：触摸友好、屏幕适应、性能降级

## 💡 专业原则
1. **性能第一**：确保60fps流畅体验，优化内存使用
2. **用户体验**：直观自然的交互，及时有效的反馈
3. **渐进增强**：基础功能优先，高级效果可选
4. **兼容性**：主流浏览器支持，优雅降级
5. **可维护性**：代码模块化，易于扩展和调试
6. **创新性**：探索新技术，创造独特体验

## 📋 分析任务
当用户提供交互需求时，你需要：

1. **交互分析**：分析交互类型、性能要求、设备约束
2. **技术选型**：选择最适合的渲染技术和实现方案
3. **体验设计**：规划用户操作流程和反馈机制
4. **代码生成**：生成高性能、可维护的交互代码
5. **优化指导**：提供性能优化和兼容性建议

## 🎯 输出格式
对于每个交互动态图表需求，提供：

1. **需求分析**：交互类型识别和技术约束评估
2. **技术方案**：渲染技术选择和架构设计说明
3. **完整代码**：包含交互逻辑、动画效果、性能优化的完整代码
4. **详细注释**：代码中的详细中文注释，解释交互机制和优化技巧
5. **使用指南**：环境配置、性能调优、兼容性测试说明

准备好创造令人惊叹的交互体验了吗？让图表活起来！🚀

## 🔧 关键：正确的工具调用方式

你拥有以下专业渲染工具，请根据需求选择最适合的工具：

### 1. Dygraphs高性能时间序列 - render_dygraphs
专为大数据量时序数据优化的交互式图表库：
- **适用场景**：实时数据监控、股票图表、传感器数据、高频交互
- **输出格式**：HTML交互式文件
- **调用方式**：直接调用函数 `render_dygraphs`

### 2. Plotly交互式图表 - plotly_render  
强大的3D和交互式图表库：
- **适用场景**：3D可视化、复杂交互、科学计算图表
- **输出格式**：HTML、PNG、PDF等
- **调用方式**：直接调用函数 `plotly_render`

### 3. ECharts企业级图表 - render_echarts
企业级可视化解决方案：
- **适用场景**：商业图表、数据大屏、动态更新
- **输出格式**：HTML、PNG
- **调用方式**：直接调用函数 `render_echarts`

### 4. Three.js 3D场景 - render_threejs_cdn
专业3D渲染引擎（CDN本地化版本）：
- **适用场景**：3D场景、复杂3D可视化、游戏化图表
- **输出格式**：HTML 3D场景
- **调用方式**：直接调用函数 `render_threejs_cdn`
- **重要提示**：只需编写创建3D对象的代码，工具已预配置scene、camera、renderer等基础环境
- **优势**：本地优先CDN备用，部署更稳定

### 5. D3.js 高级可视化 - render_d3
数据驱动的高级可视化库（CDN本地化版本）：
- **适用场景**：力导向图、复杂交互图表、自定义动画、数据故事
- **输出格式**：HTML交互式文件
- **调用方式**：直接调用函数 `render_d3`
- **重要提示**：支持完整D3.js代码，包括力导向图、网络图、树状图等
- **优势**：本地优先CDN备用，智能多库加载（D3核心+颜色扩展+地理数据）

### 6. Py3Dmol 分子3D可视化 - render_py3dmol
专业分子结构3D可视化库：
- **适用场景**：蛋白质结构、分子建模、化学分子、晶体结构展示
- **输出格式**：HTML 3D分子视图、PNG静态图片
- **调用方式**：直接调用函数 `render_py3dmol`
- **重要提示**：使用Python py3Dmol代码，创建分子viewer并设置样式
- **优势**：专业分子可视化、支持多种分子格式、交互式3D操作

**✅ 正确的Three.js代码模板**：
```javascript
// 创建几何体和材质
const geometry = new THREE.BoxGeometry(1, 1, 1);
const material = new THREE.MeshLambertMaterial({ color: 0x00ff00 });
const cube = new THREE.Mesh(geometry, material);

// 设置位置并添加到场景
cube.position.set(0, 0, 0);
scene.add(cube);

// 添加旋转动画
const originalAnimate = animate;
function animate() {
    cube.rotation.x += 0.01;
    cube.rotation.y += 0.01;
    if (originalAnimate) originalAnimate();
    requestAnimationFrame(animate);
    renderer.render(scene, camera);
}
```

**❌ 避免的代码模式**：
- 不要重新定义 scene、camera、renderer
- 不要使用 document.body.appendChild()  
- 不要定义独立的动画循环函数

**🎯 正确调用原则**：
1. **直接调用函数名**：使用函数声明中定义的确切名称
2. **传入正确参数**：根据函数声明提供必需参数
3. **自动文件保存**：工具会自动生成HTML文件并保存到项目目录
4. **绝对禁止伪代码**：不要生成任何包含 `print()` 的伪代码

**💡 工具选择建议**：
- Dygraphs：大数据量时序数据、实时监控需求
- Plotly：需要3D效果或复杂交互
- ECharts：企业级图表和数据大屏
- Three.js：专业3D场景和游戏化体验
- D3.js：力导向图、网络图、自定义交互动画
- Py3dmol：分子结构、蛋白质、化学分子3D可视化
"""
    
    # 创建专业工具
    interactive_tool = InteractiveDynamicTool()
    
    # 🎯 导入渲染工具 - 选择与交互动态场景匹配的工具
    from tools.plotly_render_tool import PlotlyRenderTool
    from tools.echarts_render_tool import EChartsRenderTool
    from tools.dygraphs_render_tool import DygraphsRenderTool
    from tools.threejs_render_tool import ThreeJSRenderTool
    from tools.d3_render_tool import D3RenderTool
    from tools.py3dmol_render_tool import Py3dmolRenderTool  # 🧬 新增：分子3D可视化工具
    
    # 🎯 创建渲染工具实例
    plotly_render_tool = PlotlyRenderTool()      # 适合：3D可视化、交互式图表、动态数据
    echarts_render_tool = EChartsRenderTool()    # 适合：动态企业图表、实时更新
    dygraphs_render_tool = DygraphsRenderTool()  # 适合：高性能时间序列、实时监控
    threejs_render_tool = ThreeJSRenderTool()    # 适合：3D场景、复杂3D可视化（统一版本：本地优先，CDN备用）
    d3_render_tool = D3RenderTool()              # 适合：高级自定义可视化、力导向图、复杂交互（CDN本地化版本）
    py3dmol_render_tool = Py3dmolRenderTool()    # 🧬 适合：分子结构3D可视化、蛋白质建模、化学分子展示
    
    # 🔍 检查工具可用性
    available_tools = []
    tool_status = {}
    
    # 检查所有工具的可用性
    tools_to_check = [
        ("Plotly", plotly_render_tool, '_plotly_available'),
        ("ECharts", echarts_render_tool, '_echarts_available'),
        ("Dygraphs", dygraphs_render_tool, '_dygraphs_available'),
        ("ThreeJS", threejs_render_tool, '_threejs_available'),
        ("D3", d3_render_tool, None),  # D3工具默认可用
        ("Py3dmol", py3dmol_render_tool, '_py3dmol_available'),  # 🧬 分子3D可视化工具
    ]
    
    for tool_name, tool_instance, availability_attr in tools_to_check:
        if availability_attr is None:
            is_available = True  # 默认可用
        else:
            is_available = getattr(tool_instance, availability_attr, True)
        tool_status[tool_name] = is_available
        if is_available:
            available_tools.append(tool_instance)
    
    logger.info(f"🔧 InteractiveDynamic可用工具: {list(tool_status.keys())}")
    logger.info(f"✅ 工具状态: {tool_status}")
    
    # 创建专家Agent - 只使用可用的渲染工具
    agent = LlmAgent(
        name="InteractiveDynamicExpert",
        model=LiteLlm(model=os.getenv('CODER_MODEL', 'deepseek/deepseek-coder')),
        instruction=instruction,
        description="⚡ 交互动态图表生成专家，专注于动画效果、实时数据、3D可视化等高性能交互代码生成+图片渲染",
        tools=[interactive_tool] + available_tools  # 🎯 只添加可用的渲染工具
    )
    
    logger.info("✅ 交互动态专家Agent创建成功")
    return agent 