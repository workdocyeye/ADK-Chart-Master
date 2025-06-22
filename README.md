# Chart Coordinator Project: Enterprise-Grade Intelligent Chart Generation System

**🏆 Google ADK Hackathon Submission - Enterprise AI Multi-Agent System**

> **Language Options**: [🇺🇸 English](README.md) | [🇨🇳 中文](README_CN.md)

Welcome to Chart Coordinator Project! This is an enterprise-grade, intelligent chart rendering system built on Google's Agent Development Kit (ADK) framework. It understands your needs through natural language and automatically selects the most suitable visualization tool to generate a wide range of charts, from simple flowcharts to complex 3D models and interactive maps.

**This project is a submission for the Google ADK Hackathon.**

<!-- GitHub refresh trigger -->

> **2024 Structure Update**: This project has been streamlined to include only production-essential files. All operations are performed in the project root directory (same level as this README). Test files and redundant configurations have been removed for cleaner structure and simpler deployment.

## 💻 Local Installation & Deployment (🌟 Highly Recommended - Full Feature Stability)

### System Requirements

- **Python 3.10+** (Recommended: 3.11)
- **Node.js 18+ LTS** 
- **Java JRE 8+** (for PlantUML)
- **Graphviz** (for graph rendering)

**Quick System Dependencies Installation:**
```powershell
# Windows (using winget - recommended)
winget install OpenJS.NodeJS.LTS
winget install Oracle.JavaRuntimeEnvironment  
winget install Graphviz.Graphviz

# Verify installation
node --version
java --version
dot -V
```

> For detailed dependency lists and version requirements, please check `chart_coordinator_project/requirements.txt` and `package.json`

### 🚀 Installation Steps

#### Step 1: Clone Project and Enter Directory

```bash
git clone https://github.com/workdocyeye/ADK-Chart-Master.git
cd ADK-Chart-Master
```

#### Step 2: Python Environment Setup (Virtual Environment Recommended)

```powershell
# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# Windows CMD:
# venv\Scripts\activate.bat  
# macOS/Linux:
# source venv/bin/activate

# Enter project core directory and install Python dependencies
cd chart_coordinator_project
pip install -r requirements.txt

# Important: Install latest Google ADK framework
pip install git+https://github.com/google/adk-python.git@main
```

#### Step 3: Node.js Dependencies Installation

```powershell
# In chart_coordinator_project directory
npm install

# Install global tools (Important! Ensures Mermaid tools work properly)
# Note: May require administrator privileges
npm install -g @mermaid-js/mermaid-cli

# Verify installation (if failed, restart terminal and try again)
mmdc --version
```

#### Step 4: Environment Variables Configuration

```powershell
# Navigate to chart_coordinator_project directory
cd chart_coordinator_project

# Create .env file by removing .example suffix from template
ren .env.example .env

# Edit .env file and configure your Deepseek API key
# Replace the placeholder: DEEPSEEK_API_KEY=your-actual-deepseek-api-key-here
# With your actual API key: DEEPSEEK_API_KEY=sk-your-real-api-key-here
notepad .env
```

> **Get Deepseek API Key**: Visit [https://platform.deepseek.com/](https://platform.deepseek.com/) to register and obtain API key.

#### Step 5: Launch Project

```powershell
# Return to project root directory (same level as README.md)
cd ..

# Start ADK Web service
adk web

# If adk command is not available, install latest version:
pip install git+https://github.com/google/adk-python.git@main
```

#### Step 6: Access Application

Open browser and visit: [http://localhost:8000](http://localhost:8000)

You will see the ADK Web UI, select `chart_coordinator_project` to start using.

### 🔍 Environment Check (Optional)

If you encounter issues after installation, check the following:

1. **Python Version**: Ensure ≥3.10
2. **Dependencies Installation**: Check if required packages are in `pip list`
3. **API Key**: Confirm `DEEPSEEK_API_KEY` in `.env` file is correctly set
4. **System Dependencies**: Confirm Java, Graphviz, Node.js are installed

### ✅ Functional Verification Tests

After successful startup, try these tests:

1. **Simple Chart**: `Create a sine function plot using matplotlib`
2. **Flowchart**: `Draw a user login flowchart`
3. **Data Visualization**: `Create a box plot using seaborn`
4. **3D Molecule**: `Show 3D structure of caffeine molecule with py3Dmol`
5. **Interactive Chart**: `Create an interactive pie chart with ECharts`

---

## 🐳 Docker Deployment (⚠️ Experimental - Some Features Under Development)

> **Important Notice**: Docker deployment is currently experimental, with some rendering tools having compatibility issues in container environments.
> For best experience and full functionality, **strongly recommend using the local installation method above**.

### Known Limitations

- ⚠️ **Mermaid Tools**: May not render properly in Docker environment (Puppeteer/Chrome sandbox issues)
- ⚠️ **Some JavaScript Tools**: Working normally (Matplotlib, Plotly, Seaborn, etc.)
- ✅ **Most Python Tools**: May have module loading or Chinese font rendering issues

### Quick Docker Trial

If you still want to try Docker deployment:

```bash
# Clone project
git clone https://github.com/workdocyeye/ADK-Chart-Master.git
cd ADK-Chart-Master

# Build image
docker build -t chart-coordinator .

# Run container
docker run -it --rm -p 8000:8000 -e DEEPSEEK_API_KEY="your_api_key_here" --name chart-coordinator-app chart-coordinator
```

Browser access: [http://localhost:8000](http://localhost:8000)

**Docker optimization work** is in progress, future versions will resolve container compatibility issues.

---

## 🔧 Common Issue Solutions

### Issue 1: `adk` command not found
```powershell
# Solution 1: Check if properly installed
pip show google-adk

# Solution 2: If PyPI version has issues, install GitHub development version
pip uninstall google-adk
pip install git+https://github.com/google/adk-python.git@main
```

### Issue 2: plantuml related errors
```powershell
# Ensure Java is installed
java -version

# plantuml.jar will auto-download, if issues occur, can manually download
```

### Issue 3: Module import errors
```powershell
# Ensure in correct directory and check Python path
cd chart_coordinator_project
python -c "import llm_driven_chart_system; print('Import successful')"
```

### Issue 4: Port occupied
```powershell
# Check port 8000 usage
netstat -ano | findstr :8000

# Kill occupying process or use different port
adk web --port 8001
```

### Issue 5: Mermaid tools not working
```powershell
# Ensure global installation of mermaid-cli
npm install -g @mermaid-js/mermaid-cli

# Verify installation
mmdc --version

# If still issues, can use npx for temporary calls
npx @mermaid-js/mermaid-cli --version
```

## 🚀 Core Features & Advantages

- **🤖 AI Intelligent Decision-Making**: Fully intelligent system based on Large Language Models (LLM), automatically analyzing user needs and selecting the most suitable expert agents and rendering tools
- **👥 Expert Team Collaboration**: 5 professional AI agents (Data Visualization Expert, Flow Architect Expert, etc.) working together to ensure optimal solutions
- **🛠️ 15+ Rendering Tool Ecosystem**: Seamlessly integrated with industry-leading chart libraries like Matplotlib, Plotly, ECharts, D3.js, Graphviz
- **🌐 Multi-format Output**: Supports static images (PNG, SVG, PDF) and interactive HTML file generation
- **🔧 Fully Extensible**: Modular architecture based on Google ADK framework, easily add new tools or agents
- **🏢 Enterprise-grade Localization**: 100% using Deepseek models, ensuring data privacy security and stable performance
- **✅ Production Environment Ready**: Local deployment solution thoroughly tested, 14 out of 15 tools completely stable and available

### 🎯 Tool Stability Status

**Fully Stable** (14/15):
- ✅ **Python Tools** (7/7): Matplotlib, Plotly, Seaborn, Folium, PyVis, Py3dmol, Mplfinance
- ✅ **JavaScript Tools** (4/5): ECharts, D3.js, Dygraphs, FlowchartJS  
- ✅ **Universal Tools** (3/3): PlantUML, Graphviz, Mermaid(local environment)

**Needs Optimization** (1/15):
- ⚠️ **ThreeJS**: Container environment ES6 module compatibility pending improvement

> **Local Deployment**: 15/15 tools fully available  
> **Docker Deployment**: 14/15 tools available (ThreeJS excluded)

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

## 📊 Project Status & Version Information

### V1.0-STABLE (Current Version) - Production Ready
- ✅ **Architecture Completion**: 100% (5 AI agents + 15 rendering tools)
- ✅ **Local Deployment Stability**: 15/15 tools fully available
- ✅ **Docker Deployment Stability**: 14/15 tools available (93.3% availability rate)
- ✅ **Enterprise Features**: Full localization, Deepseek model driven
- ✅ **Code Quality**: Detailed comments, comprehensive error handling, unified coding standards

### 🚧 Development Roadmap
- **V1.1 Plan**: Docker container compatibility optimization (Mermaid/ThreeJS issue fixes)
- **V1.2 Plan**: More rendering tool integrations (Bokeh, Altair, etc.)
- **V2.0 Vision**: Real-time collaboration, cloud deployment, API service

### 📈 Test Coverage & Validation
This project has undergone comprehensive functional testing, detailed test cases available in [`COMPREHENSIVE_TESTING_GUIDE.md`](COMPREHENSIVE_TESTING_GUIDE.md):
- **Tool-specific Testing**: 15 tools × 3 difficulty levels = 45 test cases
- **AI Routing Testing**: 7 semantically ambiguous prompt intelligent routing verifications
- **Production Environment Validation**: Complete testing in Windows 11 + PowerShell environment

---

## 🙏 Acknowledgments & Statement

### Google ADK Hackathon Submission
This project is an enterprise-grade intelligent chart generation system specially developed for the **Google ADK Hackathon**, showcasing the powerful capabilities of the ADK framework in complex multi-agent collaboration scenarios.

### Technical Acknowledgments
- **Google ADK Team**: Provided excellent Agent development framework
- **Deepseek Team**: High-quality AI model support
- **Open Source Community**: Excellent visualization libraries like Matplotlib, D3.js, ECharts

### Special Notes
- 🔒 **Data Privacy**: 100% localized deployment, all data processing completed in user environment
- 🌟 **Production Ready**: Enterprise-grade code quality, directly usable in production environments
- 📚 **Education Friendly**: Detailed documentation and comments, suitable for learning ADK framework and multi-agent system development

---

## 📄 License

This project is released under the **Apache License 2.0** open source license.

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

## 🎯 Quick Start

**Recommended to use local deployment for the best experience!**

1. Clone project: `git clone https://github.com/workdocyeye/ADK-Chart-Master.git`
2. Install dependencies: Enter directory, install Python and Node.js dependencies
3. Configure API: Set Deepseek API key
4. Start service: `adk web`
5. Begin using: Browser visit http://localhost:8000

**Experience the powerful functionality of intelligent chart generation immediately!** 🚀