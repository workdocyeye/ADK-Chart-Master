# Chart Coordinator Project: An Intelligent Chart Generation System

Welcome to the Chart Coordinator Project! This is an enterprise-grade, intelligent chart rendering system built on Google's Agent Development Kit (ADK) framework. It understands your needs through natural language and automatically selects the most suitable visualization tool to generate a wide range of charts, from simple flowcharts to complex 3D models and interactive maps.

**This project is a submission for the Google ADK Hackathon.**

> **2024年结构更新说明**：本项目已极致精简，仅保留生产环境所需文件，所有操作均在项目根目录（即本README同级目录）完成。测试文件和多余配置已移除，目录结构更清晰，部署更简单。

## 🚀 一键使用 Docker 部署（推荐）

### 第一步：克隆项目到本地（必做！）

请在终端中运行以下命令，将本项目从GitHub克隆到您的电脑上，并进入项目目录：

```bash
git clone https://github.com/workdocyeye/ADK-Chart-Master.git
cd ADK-Chart-Master
```

> **注意**：后续所有命令都需要在 `ADK-Chart-Master` 目录下执行！

### 第二步：构建 Docker 镜像

在终端中运行以下命令，这将基于 `Dockerfile` 创建一个名为 `chart-coordinator` 的 Docker 镜像。第一次运行可能需要几分钟：

```bash
docker build -t chart-coordinator .
```

### 第三步：运行应用容器

镜像构建完成后，使用以下命令运行应用。请将 `your_api_key_here` 替换为您的 Deepseek API 密钥：

```bash
docker run -it --rm -p 8000:8000 -e DEEPSEEK_API_KEY="your_api_key_here" --name chart-coordinator-app chart-coordinator
```

- `-it`：以交互模式运行容器。
- `--rm`：容器退出时自动移除。
- `-p 8000:8000`：将主机的8000端口映射到容器的8000端口。
- `-e DEEPSEEK_API_KEY=...`：将API密钥作为环境变量安全传递。
- `--name ...`：为运行的容器分配一个方便的名称。

现在，您可以在浏览器中访问 [http://localhost:8000](http://localhost:8000) 与图表协调器交互。

---

## 💻 手动安装指南（推荐用于本地开发）

<details>
<summary><strong>点击展开手动安装详细步骤</strong></summary>

### 系统要求

- **Python 3.10+** （推荐 3.11）
- **Node.js** 18+ (LTS)
- **Java** JRE 8+ （用于 PlantUML）
- **Graphviz** （图形渲染）
- **Windows 11** / macOS / Linux（推荐 Windows 11 + PowerShell）

### Step 1: 克隆项目并进入目录

```bash
git clone https://github.com/workdocyeye/ADK-Chart-Master.git
cd ADK-Chart-Master
```

### Step 2: Python 环境准备（推荐使用虚拟环境）

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

# 进入项目核心目录安装 Python 依赖
cd chart_coordinator_project
pip install -r requirements.txt
```

### Step 3: Node.js 依赖安装

```powershell
# 在 chart_coordinator_project 目录下
npm install

# 安装全局工具（可选，用于 Mermaid 图表）
npm install -g @mermaid-js/mermaid-cli
```

### Step 4: 环境变量配置

在 `chart_coordinator_project` 目录下创建 `.env` 文件：

```bash
# 必需配置
DEEPSEEK_API_KEY=sk-your-actual-deepseek-api-key-here

# 系统配置（通常无需修改）
PYTHONPATH=.
MPLBACKEND=Agg
```

> **获取 Deepseek API Key**：访问 [https://platform.deepseek.com/](https://platform.deepseek.com/) 注册并获取 API 密钥。

### Step 5: 启动项目

```powershell
# 返回到 project 根目录（README.md 同级目录）
cd ..

# 启动 ADK Web 服务
adk web

# 如果 adk 命令不可用，可能需要从 GitHub 安装最新版本：
# pip install git+https://github.com/google/adk-python.git@main
```

### Step 6: 访问应用

打开浏览器访问：[http://localhost:8000](http://localhost:8000)

你将看到 ADK Web UI，选择 `chart_coordinator_project` 开始使用。

### 常见问题解决

#### 问题1：`adk` 命令找不到
```powershell
# 方案1：检查是否正确安装
pip show google-adk

# 方案2：如果 PyPI 版本有问题，安装 GitHub 开发版
pip uninstall google-adk
pip install git+https://github.com/google/adk-python.git@main
```

#### 问题2：plantuml 相关错误
```powershell
# 确保安装了 Java
java -version

# plantuml.jar 会自动下载，如有问题可手动下载
```

#### 问题3：模块导入错误
```powershell
# 确保在正确目录，并检查 Python 路径
cd chart_coordinator_project
python -c "import llm_driven_chart_system; print('导入成功')"
```

#### 问题4：端口被占用
```powershell
# 检查 8000 端口使用情况
netstat -ano | findstr :8000

# 结束占用进程或使用其他端口
adk web --port 8001
```

### 功能验证

启动成功后，可以尝试以下测试：

1. **简单图表**：`使用 matplotlib 画一个正弦函数图`
2. **流程图**：`画一个用户登录的流程图`
3. **数据可视化**：`用 seaborn 画一个箱线图`

</details>

## 🚀 Core Features

- **🤖 AI-Driven Decisions**: The system is fully driven by Large Language Models (LLMs) that analyze user requests and intelligently delegate tasks to the most suitable expert agent and tool.
- **- 専門家チーム**: A team of 5 specialist agents (e.g., Data Viz Expert, Flow Architect) collaborate to find the best solution.
- **- 15+ Rendering Tools**: Seamlessly integrates industry-leading libraries like Matplotlib, Plotly, ECharts, D3.js, Graphviz, and more.
- **- 🌐 Multi-Format Output**: Generates not just static images (PNG, SVG, PDF) but also interactive HTML files.
- **- 🔧 Fully Extensible**: The underlying ADK framework makes it easy to add new tools or agents.
- **- 🏢 100% Localized & Enterprise-Ready**: The entire system now runs on the Deepseek model, ensuring data privacy and stable performance.

## ✨ Showcase: From Prompt to Picture

Here are some examples of what you can create with a single line of instruction:

| Category | Prompt | Generated Chart |
| :--- | :--- | :--- |
| **3D Scientific Viz** | `From PDB get caffeine (CID 2519), and use py3Dmol to visualize it as a 'stick' model.` | *(Imagine a 3D model of a caffeine molecule here)* |
| **Financial Analysis**| `Get TSLA stock data for Q1 2024, and use Mplfinance to draw a candlestick chart with 5-day and 20-day moving averages.` | *(Imagine a professional candlestick stock chart here)* |
| **Process Flow** | `Use Flowchart.js to map out the user login process: start -> input credentials -> check if valid? -> if yes, go to homepage -> if no, show error -> end.` | *(Imagine a clean flowchart diagram here)* |
| **Interactive 3D** | `Please use Plotly to build a 3D surface plot for the function z = sin(sqrt(x^2 + y^2)).` | *(Imagine an interactive 3D surface plot here)* |
| **Complex Network** | `Create a network graph showing the relationships in the Stark family from Game of Thrones, including Ned, Catelyn, Robb, Sansa, Arya, and Jon Snow.` | *(Imagine a node-link diagram of the Stark family here)* |

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

## 🤝 Contributing & License

This project was created for the Google ADK Hackathon. Contributions, forks, and feedback are highly encouraged.

The project is licensed under the **Apache License 2.0**. 