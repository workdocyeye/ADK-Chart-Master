# Chart Coordinator Project: 企业级智能图表生成系统

**🏆 Google ADK Hackathon 提交作品 - 企业级AI多智能体系统**

> **语言选择**: [🇺🇸 English](README.md) | [🇨🇳 中文](README_CN.md)

欢迎使用Chart Coordinator Project！这是一个基于Google ADK（Agent Development Kit）框架构建的企业级智能图表渲染系统。它通过自然语言理解您的需求，自动选择最适合的可视化工具，生成从简单流程图到复杂3D模型和交互地图的各种图表。

**本项目是Google ADK Hackathon的参赛作品。**



## 💻 本地安装部署（🌟 强烈推荐 - 功能完整稳定）

### 系统要求

- **Python 3.10+** （推荐 3.11）
- **Node.js 18+ LTS** 
- **Java JRE 8+** （用于 PlantUML）
- **Graphviz** （图形渲染）

**快速安装系统依赖：**
```powershell
# Windows (推荐使用 winget)
winget install OpenJS.NodeJS.LTS
winget install Oracle.JavaRuntimeEnvironment  
winget install Graphviz.Graphviz

# 验证安装
node --version
java --version
dot -V
```

> 详细的依赖列表和版本要求请查看 `chart_coordinator_project/requirements.txt` 和 `package.json`

### 🚀 安装步骤

#### 第一步：克隆项目并进入目录

```bash
git clone https://github.com/workdocyeye/ADK-Chart-Master.git
cd ADK-Chart-Master
```

#### 第二步：Python环境准备（推荐使用虚拟环境）

```powershell
# 创建虚拟环境（推荐）
python -m venv venv

# 激活虚拟环境
# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# Windows CMD:
# venv\Scripts\activate.bat  
# macOS/Linux:
# source venv/bin/activate

# 进入项目核心目录安装Python依赖
cd chart_coordinator_project
pip install -r requirements.txt

# 重要：安装最新版本的Google ADK框架
pip install git+https://github.com/google/adk-python.git@main
```

#### 第三步：Node.js依赖安装

```powershell
# 在 chart_coordinator_project 目录下
npm install

# 安装全局工具（重要！确保Mermaid工具正常工作）
# 注意：可能需要管理员权限
npm install -g @mermaid-js/mermaid-cli

# 验证安装（如果失败，重启终端后再试）
mmdc --version
```

#### 第四步：环境变量配置

```powershell
# 在 chart_coordinator_project 目录下，复制环境变量模板
copy .env.example .env

# 编辑 .env 文件，设置你的 Deepseek API 密钥
# 将 DEEPSEEK_API_KEY=your-actual-deepseek-api-key-here 
# 替换为 DEEPSEEK_API_KEY=sk-你的真实密钥
```

> **获取 Deepseek API Key**：访问 [https://platform.deepseek.com/](https://platform.deepseek.com/) 注册并获取 API 密钥。

#### 第五步：启动项目

```powershell
# 返回到 project 根目录（README.md 同级目录）
cd ..

# 启动 ADK Web 服务
adk web

# 如果 adk 命令不可用，安装最新版本：
pip install git+https://github.com/google/adk-python.git@main
```

#### 第六步：访问应用

打开浏览器访问：[http://localhost:8000](http://localhost:8000)

你将看到 ADK Web UI，选择 `chart_coordinator_project` 开始使用。

### 🔍 环境检查（可选）

如果安装后遇到问题，可以检查以下几个方面：

1. **Python版本**：确保 ≥3.10
2. **依赖安装**：检查 `pip list` 中是否包含所需包
3. **API密钥**：确认 `.env` 文件中的 `DEEPSEEK_API_KEY` 已正确设置
4. **系统依赖**：确认 Java、Graphviz、Node.js 已安装

### ✅ 功能验证测试

启动成功后，可以尝试以下测试：

1. **简单图表**：`使用 matplotlib 画一个正弦函数图`
2. **流程图**：`画一个用户登录的流程图`
3. **数据可视化**：`用 seaborn 画一个箱线图`
4. **3D分子**：`用py3Dmol显示咖啡因分子的3D结构`
5. **交互图表**：`用ECharts做一个可交互的饼图`

---

## 🐳 Docker 部署（⚠️ 实验性质 - 部分功能待完善）

> **重要提醒**：Docker部署目前处于实验阶段，某些渲染工具在容器环境中存在兼容性问题。
> 为获得最佳体验和完整功能，**强烈建议使用上述本地安装方式**。

### 已知限制

- ⚠️ **Mermaid工具**：在Docker环境中可能无法正常渲染（Puppeteer/Chrome沙箱问题）
- ⚠️ **部分JavaScript工具**：工作正常（Matplotlib、Plotly、Seaborn等）
- ✅ **大部分Python工具**：可能存在模块加载或中文字体渲染问题

### Docker快速试用

如果您仍想尝试Docker部署：

```bash
# 克隆项目
git clone https://github.com/workdocyeye/ADK-Chart-Master.git
cd ADK-Chart-Master

# 构建镜像
docker build -t chart-coordinator .

# 运行容器
docker run -it --rm -p 8000:8000 -e DEEPSEEK_API_KEY="your_api_key_here" --name chart-coordinator-app chart-coordinator
```

浏览器访问：[http://localhost:8000](http://localhost:8000)

**Docker优化工作**正在进行中，未来版本将解决容器兼容性问题。

---

## 🔧 常见问题解决

### 问题1：`adk` 命令找不到
```powershell
# 方案1：检查是否正确安装
pip show google-adk

# 方案2：如果 PyPI 版本有问题，安装 GitHub 开发版
pip uninstall google-adk
pip install git+https://github.com/google/adk-python.git@main
```

### 问题2：plantuml 相关错误
```powershell
# 确保安装了 Java
java -version

# plantuml.jar 会自动下载，如有问题可手动下载
```

### 问题3：模块导入错误
```powershell
# 确保在正确目录，并检查 Python 路径
cd chart_coordinator_project
python -c "import llm_driven_chart_system; print('导入成功')"
```

### 问题4：端口被占用
```powershell
# 检查 8000 端口使用情况
netstat -ano | findstr :8000

# 结束占用进程或使用其他端口
adk web --port 8001
```

### 问题5：Mermaid工具无法使用
```powershell
# 确保全局安装了 mermaid-cli
npm install -g @mermaid-js/mermaid-cli

# 验证安装
mmdc --version

# 如果仍有问题，可以使用 npx 临时调用
npx @mermaid-js/mermaid-cli --version
```

## 🚀 核心特性与优势

- **🤖 AI智能决策**: 基于大型语言模型(LLM)的完全智能系统，自动分析用户需求并选择最适合的专家代理和渲染工具
- **👥 专家团队协作**: 5个专业AI代理(数据可视化专家、流程架构专家等)协同工作，确保最佳解决方案
- **🛠️ 15+渲染工具生态**: 无缝集成Matplotlib、Plotly、ECharts、D3.js、Graphviz等行业领先图表库
- **🌐 多格式输出**: 支持静态图片(PNG、SVG、PDF)和交互式HTML文件生成
- **🔧 完全可扩展**: 基于Google ADK框架的模块化架构，轻松添加新工具或代理
- **🏢 企业级本地化**: 100%使用Deepseek模型，确保数据隐私安全和稳定性能
- **✅ 生产环境就绪**: 本地部署方案经过充分测试，15个工具中14个完全稳定可用

### 🎯 工具稳定性状态

**完全稳定** (14/15):
- ✅ **Python工具** (7/7): Matplotlib、Plotly、Seaborn、Folium、PyVis、Py3dmol、Mplfinance
- ✅ **JavaScript工具** (4/5): ECharts、D3.js、Dygraphs、FlowchartJS  
- ✅ **通用工具** (3/3): PlantUML、Graphviz、Mermaid(本地环境)

**需优化** (1/15):
- ⚠️ **ThreeJS**: 容器环境ES6模块兼容性待完善

> **本地部署**: 15/15工具完全可用  
> **Docker部署**: 14/15工具可用(ThreeJS除外)



## 🏛️ Architecture and Design

<details>
<summary><strong>Click to expand: System Architecture Diagram</strong></summary>

The project follows a multi-agent, hierarchical design pattern. A central coordinator agent analyzes requests and delegates them to a team of specialists, who in turn use a shared pool of rendering tools.

```
┌─────────────────────────────────────────────────────────────┐
│                Chart Coordinator Project                    │
│                 (Intelligent Chart System)                  │
└─────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │   5 Specialist AI Agents    │
                    └─────────┬─────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
    ┌───▼───┐           ┌─────▼─────┐         ┌─────▼─────┐
    │Flow   │           │Conceptual │         │Interactive│
    │Architect Expert   │Mind Expert│         │Dynamic Expert│
    └───┬───┘           └─────┬─────┘         └─────┬─────┘
        │                     │                     │
   ┌────▼────┐          ┌─────▼─────┐         ┌─────▼─────┐
   │DataViz  │          │Document   │         │  (etc.)   │
   │Expert   │          │Chart Expert│         │           │
   └─────────┘          └───────────┘         └───────────┘
                              │
                    ┌─────────▼─────────┐
                    │  15+ Rendering Tools  │
                    └─────────┬─────────┘
                              │
    ┌─────────────────────────┼─────────────────────────┐
    │                         │                         │
┌───▼───┐               ┌─────▼─────┐           ┌───────▼───────┐
│Python Tools           │JavaScript Tools       │ Universal Tools │
│(Matplotlib, Plotly..) │(ECharts, D3.js..)     │ (Mermaid, PlantUML..)│
└───────┘               └───────────┘           └───────────────┘
```

</details>

<details>
<summary><strong>Click to expand: Agent and Tool Details</strong></summary>

### The Agent Team

| Agent | Expertise | Primary Tools |
| :--- | :--- | :--- |
| **FlowArchitectExpert** | Business Processes, System Architecture | `Mermaid`, `PlantUML`, `Graphviz`, `FlowchartJS` |
| **ConceptualMindExpert**| Mind Maps, Knowledge Graphs | `Mermaid`, `Graphviz`, `PyVis`, `Plotly` |
| **DataVizExpert** | Data Analysis, Statistical Charts | `Matplotlib`, `Plotly`, `Seaborn`, `ECharts`, `Folium` |
| **InteractiveDynamicExpert**| Real-time Data, 3D, Interactive Dashboards| `Plotly`, `ECharts`, `ThreeJS`, `Dygraphs` |
| **DocumentChartExpert** | Technical Docs, Report Graphics | `Mermaid`, `Matplotlib`, `PlantUML`|

### The Render Tool Matrix

A suite of 15+ fully integrated visualization tools is available.

#### Python Stack (7 Tools)
| Tool | Domain | Output | Status |
|:---|:---|:---|:---|
| **Matplotlib** | Scientific Plotting | PNG/SVG/PDF | ✅ Available |
| **Plotly** | Interactive Viz | HTML/PNG | ✅ Available |
| **Seaborn** | Statistical Viz | PNG/PDF | ✅ Available |
| **PyVis** | Network Graphs | HTML | ✅ Available |
| **Mplfinance** | Financial Charts | PNG/PDF | ✅ Available |
| **Py3dmol** | Molecular Viz | HTML/PNG | ✅ Available |
| **Folium** | Geospatial Maps | HTML | ✅ Available |

#### JavaScript Stack (5 Tools)
| Tool | Domain | Output | Status |
|:---|:---|:---|:---|
| **ECharts** | Enterprise Viz | HTML/PNG | ✅ Available |
| **D3.js** | Custom Viz | HTML/SVG | ✅ Available |
| **Dygraphs** | Time-Series Data | HTML/PNG | ✅ Available |
| **ThreeJS** | 3D Rendering | HTML | ✅ Available |
| **Flowchart.js**| Simple Flowcharts | HTML/PNG | ✅ Available |

#### Universal Stack (3 Tools)
| Tool | Domain | Output | Status |
|:---|:---|:---|:---|
| **Mermaid** | Diagram as Code | PNG/SVG | ✅ Available |
| **PlantUML** | UML Diagrams | PNG/SVG | ✅ Available |
| **Graphviz** | Graph Theory Viz | PNG/SVG | ✅ Available |

</details>

<details>
<summary><strong>Click to expand: Developer Guide & Best Practices</strong></summary>

### Core Technical Experience

**ADK Tool Registration**: A key pattern in the ADK framework is the `_get_declaration()` method, which every tool must implement to describe its interface to the LLM.
```python
# Every tool must provide this method
def _get_declaration(self) -> Optional[types.FunctionDeclaration]:
    return types.FunctionDeclaration(
        name=self.name,
        description=self.description,
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                # Precise parameter definitions go here
            },
            required=['list_of_required_parameters']
        )
    )
```

**Cross-Platform Compatibility**:
- **PowerShell Commands**: Use semicolons (`;`) instead of `&&` to chain commands.
- **File Encoding**: Explicitly use `encoding='utf-8'` and `errors='replace'` when running `subprocess` calls to handle character encoding issues, especially on Windows.

**Dependency Management**: Each tool performs a self-check for its dependencies (Python libraries, system commands) upon initialization. The agent only loads tools that are fully operational, making the system resilient to incomplete environments.

### How to Add a New Rendering Tool
1.  Create a new tool class that inherits from `tools.base_render_tool.BaseRenderTool`.
2.  Implement the required `_get_declaration()` and `_render_sync()` methods.
3.  Add a dependency self-check method (`_check_dependencies()`).
4.  Instantiate your new tool in the appropriate agent file (e.g., `agents/data_visualization_agent.py`).
5.  Add the new tool instance to the `tools` list of that agent.

</details>

## 📊 项目状态与版本信息

### V1.0-STABLE (当前版本) - 生产就绪
- ✅ **架构完成度**: 100% (5个AI代理 + 15个渲染工具)
- ✅ **本地部署稳定性**: 15/15工具完全可用
- ✅ **Docker部署稳定性**: 14/15工具可用(93.3%可用率)
- ✅ **企业级特性**: 完全本地化，Deepseek模型驱动
- ✅ **代码质量**: 详细注释，完善错误处理，统一编码规范

### 🚧 开发路线图
- **V1.1计划**: Docker容器兼容性优化(Mermaid/ThreeJS问题修复)
- **V1.2计划**: 更多渲染工具集成(Bokeh、Altair等)
- **V2.0愿景**: 实时协作、云端部署、API服务化



---

## 🙏 致谢与声明

### Google ADK Hackathon 提交作品
本项目是为**Google ADK Hackathon**专门开发的企业级智能图表生成系统，展示了ADK框架在复杂多Agent协作场景中的强大能力。

### 技术致谢
- **Google ADK团队**: 提供了出色的Agent开发框架
- **Deepseek团队**: 高质量的AI模型支持
- **开源社区**: Matplotlib、D3.js、ECharts等优秀可视化库

### 特别说明
- 🔒 **数据隐私**: 100%本地化部署，所有数据处理在用户环境中完成
- 🌟 **生产就绪**: 企业级代码质量，可直接用于生产环境
- 📚 **教育友好**: 详细文档和注释，适合学习ADK框架和多Agent系统开发

---

## 📄 许可证

本项目基于 **Apache License 2.0** 开源许可证发布。

```
Copyright 2025 Chart Coordinator Project Contributors

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```

---

## 🎯 快速开始

**推荐使用本地部署获得最佳体验！**

1. 克隆项目：`git clone https://github.com/workdocyeye/ADK-Chart-Master.git`
2. 安装依赖：进入目录，安装Python和Node.js依赖
3. 配置API：设置Deepseek API密钥
4. 启动服务：`adk web`
5. 开始使用：浏览器访问 http://localhost:8000

**立即体验智能图表生成的强大功能！** 🚀 

 