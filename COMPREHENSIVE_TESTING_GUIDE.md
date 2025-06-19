# Chart Coordinator Project 全面测试指南 (V1.0)

本文档旨在提供一套完整的测试用例，用于全面评估`Chart Coordinator Project`的稳定性、鲁棒性以及AI智能路由的准确性。

---

## Part 1: 工具专项能力测试

本部分针对项目中的15个渲染工具，每个工具提供三个从易到难的测试提示词。

### Python 渲染工具 (7个)

#### 1. MatplotlibRenderTool(通过了)
*   **LV1 (简单)**: `用Matplotlib画一个简单的正弦函数曲线。`
*   **LV2 (详细)**: `使用Matplotlib绘制一个包含两条线的折线图，X轴是月份（1到12），Y轴是销售额。第一条线代表A产品，数据为[50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150, 160]，第二条线代表B产品，数据为[85, 80, 95, 110, 100, 120, 125, 130, 145, 140, 160, 170]。请为图表添加标题“A产品 vs B产品月度销售额”，并加上图例。`
*   **LV3 (复杂)**: `请用Matplotlib创建一个2x1的子图布局。在上面的子图中，绘制一个带有误差线的散点图，数据点为(1, 2), (2, 3), (3, 5), (4, 4)，Y轴误差均为0.5。在下面的子图中，绘制一个苹果公司股价（AAPL）从2023年1月到2023年6月的K线图。`

#### 2. PlotlyRenderTool（完美通过）
*   **LV1 (简单)**: `用Plotly生成一个可以交互的散点图。`
*   **LV2 (详细)**: `使用Plotly创建一个交互式条形图，展示四个季度（Q1, Q2, Q3, Q4）的收入，数据分别为[100, 150, 120, 200]。要求鼠标悬停时需要显示具体数值。`
*   **LV3 (复杂)**: `请用Plotly构建一个3D曲面图，函数为 z = sin(sqrt(x^2 + y^2))，其中x和y的范围都是-5到5。图表应该是可交互的，允许用户旋转和缩放。`

#### 3. SeabornRenderTool
*   **LV1 (简单)**: `用Seaborn画一个简单的直方图。`
*   **LV2 (详细)**: `加载Seaborn内置的“tips”数据集，然后创建一个小提琴图（violin plot），X轴是“day”，Y轴是“total_bill”，并按“sex”进行颜色区分。`看起来在加载Seaborn内置的“tips”数据集时遇到了SSL连接问题。这可能是由于网络环境或SSL配置导致的。以下是修正后的代码，您可以手动运行它来生成小提琴图：
*   **LV3 (复杂)**: `使用Seaborn的“iris”数据集，创建一个pair plot（散点图矩阵），用不同颜色表示不同的鸢尾花物种（species），并在对角线上显示每个特征的核密度估计图。`

#### 4. FoliumRenderTool（重点修复）
*   **LV1 (简单)**: `用Folium创建一张显示世界地图的HTML文件。`
*   **LV2 (详细)**: `用Folium创建一张以中国北京（39.9042° N, 116.4074° E）为中心的地图，并添加一个标记，标记的弹出内容为“首都北京”。`
*   **LV3 (复杂)**: `请用Folium绘制一张包含多个国家首都位置的热力图。你需要自己查找至少10个国家首都的经纬度数据，并根据这些点生成热力图层。`

#### 5. MplfinanceRenderTool
*   **LV1 (简单)**: `用Mplfinance绘制一个简单的股票K线图。`
*   **LV2 (详细)**: `获取2024年第一季度特斯拉（TSLA）的股票数据，使用Mplfinance绘制一个包含5日和20日移动平均线的K线图，并附带成交量。`由于当前环境中缺少 yfinance 库，无法直接获取特斯拉的股票数据。
*   **LV3 (复杂)**: `请使用Mplfinance的“renko”样式，绘制微软（MSFT）2023年全年的砖形图，并与传统的K线图并排显示以便比较。`由于技术限制，我无法直接渲染并排显示的图表。以下是完整的Python代码，您可以手动运行来生成微软(MSFT)2023年的砖形图与传统K线图对比：

#### 6. PyVisRenderTool（较为完美通过）
*   **LV1 (简单)**: `用PyVis创建一个包含3个节点和2条边的简单网络图。`NetworkVisualizationExpert提到一个不存在的专家。！！
*   **LV2 (详细)**: `创建一个网络图，表示一个小型社交网络。节点包括：Alice, Bob, Charlie, David。边包括：(Alice, Bob), (Alice, Charlie), (Bob, Charlie), (Bob, David)。请将Alice节点设为中心，并用不同颜色标记。`
*   **LV3 (复杂)**: `生成一个描述《权力的游戏》中史塔克家族人物关系的网络图。节点至少应包括奈德、凯特琳、罗柏、珊莎、艾莉亚、布兰、瑞肯和琼恩·雪诺。边的粗细可以用来表示关系的亲密程度（例如，夫妻关系最粗，兄弟姐妹次之）。`

#### 7. Py3dmolRenderTool（完美通过）
*   **LV1 (简单)**: `用py3Dmol显示水分子的3D结构。`
*   **LV2 (详细)**: `从PDB数据库获取咖啡因的结构（CID 2519），并使用py3Dmol进行3D可视化，将其显示为“棍状”（stick）模型。`
*   **LV3 (复杂)**: `从PDB数据库加载PDB ID为“1CRN”的蛋白质结构，使用py3Dmol进行可视化。要求将其显示为“卡通”（cartoon）模型，并根据二级结构（α螺旋和β折叠）进行着色。`

### JavaScript 渲染工具 (5个)

#### 8. EChartsRenderTool（完美通过）
*   **LV1 (简单)**: `用ECharts画一个饼图。`
*   **LV2 (详细)**: `使用ECharts创建一个仪表盘图，显示当前CPU使用率，设定值为75%。`
*   **LV3 (复杂)**: `请用ECharts制作一个动态排序的条形图，模拟2020年至2024年全球手机品牌市场份额变化。你需要虚构一些数据，让图表在5秒内动态展示排名变化。`

#### 9. DygraphsRenderTool（要重点修复）
*   **LV1 (简单)**: `用Dygraphs绘制一个基本的时间序列图。`
*   **LV2 (详细)**: `使用Dygraphs绘制从2024年1月1日到2024年1月31日的每日气温变化，数据需要包含最高温和最低温两条线。X轴为日期，Y轴为温度。`
*   **LV3 (复杂)**: `请创建一个Dygraphs图表，显示某只股票的价格和对应的布林带（上轨、中轨、下轨）。当用户拖动选择一个时间范围时，图表需要能动态缩放。`

#### 10. ThreeJSRenderTool（要修复）（边框界面看看能不能去掉）
*   **LV1 (简单)**: `用ThreeJS创建一个旋转的立方体。`
*   **LV2 (详细)**: `使用ThreeJS创建一个包含一个球体和一个立方体的3D场景。添加光源，使物体产生阴影。`（使用到了之前遗留的cdn版本，渲染出图出错了）
*   **LV3 (复杂)**: `请用ThreeJS构建一个简单的太阳系模型，中心是一个代表太阳的光源，有至少三个行星（如地球、火星）围绕太阳旋转，其中地球还有一个卫星（月球）围绕它旋转。`能出图，但是效果不好

#### 11. D3RenderTool（边框界面看看能不能去掉）
*   **LV1 (简单)**: `用D3画几个SVG圆形。`
*   **LV2 (详细)**: `使用D3创建一个力导向图，节点为A, B, C, D，边为(A,B), (B,C), (C,D), (D,A)。`
*   **LV3 (复杂)**: `请用D3制作一个可交互的中国地图，当鼠标悬停在不同省份上时，高亮该省份并显示省份名称。你需要使用GeoJSON或TopoJSON格式的中国地图数据。`（能出图，但是效果非常不好，有报错）

#### 12. FlowchartJSRenderTool（能完美运行，但是看看能不能去掉这个边框）
*   **LV1 (简单)**: `用Flowchart.js画一个简单的“开始 -> 结束”流程图。`
*   **LV2 (详细)**: `使用Flowchart.js绘制一个用户登录流程图，包括：开始 -> 输入用户名和密码 -> 条件判断：信息是否正确？ -> (是) -> 进入主页 -> (否) -> 显示错误提示 -> 结束。`
*   **LV3 (复杂)**: `请用Flowchart.js描述一个递归函数的执行流程，以计算阶乘为例。流程图需要能体现出函数调用自身以及基线条件（base case）的判断。`

### 通用 渲染工具 (3个)

#### 13. MermaidRenderTool（完美通过！）
*   **LV1 (简单)**: `用Mermaid生成一个A到B的流程图。`
*   **LV2 (详细)**: `使用Mermaid创建一个甘特图，规划一个为期一周的软件开发冲刺（Sprint）。任务包括：需求分析（2天）、UI设计（3天）、后端开发（4天）、测试（2天）。`
*   **LV3 (复杂)**: `请用Mermaid的类图（class diagram）功能，描述一个简化的网上商城系统。需要包含 User, Product, Order 等核心类，以及它们之间的关系（如继承、关联、聚合）。`

#### 14. PlantUMLRenderTool（完美通过！）
*   **LV1 (简单)**: `用PlantUML画一个简单的时序图。`
*   **LV2 (详细)**: `使用PlantUML创建一个活动图，描述一个在线购物的完整流程，从用户浏览商品到最终支付成功。`
*   **LV3 (复杂)**: `请用PlantUML的对象图（object diagram）展示一个具体的订单场景。例如，用户“张三”创建了一个订单“Order123”，该订单包含两个商品：“笔记本电脑”和“鼠标”。`

#### 15. GraphvizRenderTool（有中文问题！）
*   **LV1 (简单)**: `用Graphviz画一个A指向B的有向图。`
*   **LV2 (详细)**: `使用Graphviz的DOT语言创建一个家族树，至少包含三代人，并使用不同的形状来区分男性和女性。`（中文有问题可能）
*   **LV3 (复杂)**: `请用Graphviz绘制一个有限状态自动机（FSM）的图形，该自动机用于识别以“ab”结尾的字符串。需要清晰地标示出状态、转换条件以及最终状态。`

---

## Part 2: AI 智能路由测试

本部分提供一组语义模糊的提示词，旨在测试 `ChartCoordinatorAI` 是否能准确理解用户意图，并将任务路由给正确的专家代理。

1.  **模糊提示1**: `我想看看公司最近的销售趋势，数据波动有点大，帮我理理清楚。`
    *   **预期行为**: `ChartCoordinatorAI` 应该判断出这是一个时间序列分析任务，将请求路由给 `DataVisualizationExpert` 或 `InteractiveDynamicExpert`。最终可能使用 `DygraphsRenderTool` 或 `PlotlyRenderTool`。

2.  **模糊提示2**: `我们团队下个版本的开发流程是怎样的？能不能画出来给我看？`
    *   **预期行为**: `ChartCoordinatorAI` 应该识别出这是一个流程/架构描述任务，路由给 `FlowArchitectExpert`。最终可能使用 `FlowchartJSRenderTool`, `MermaidRenderTool`, 或 `PlantUMLRenderTool`。

3.  **模糊提示3**: `帮我把这个分子结构展示出来，我想从不同角度看看。`
    *   **预期行为**: `ChartCoordinatorAI` 应该识别出这是3D科学可视化需求，路由给 `InteractiveDynamicExpert`。最终使用 `Py3dmolRenderTool` 或 `ThreeJSRenderTool`。

4.  **模糊提示4**: `给我解释一下“决策树”这个概念。`
    *   **预期行为**: `ChartCoordinatorAI` 应该理解这是一个概念解释任务，路由给 `ConceptualMindExpert`。最终可能使用 `GraphvizRenderTool` 或 `MermaidRenderTool` 来绘制一个决策树示例。

5.  **模糊提示5**: `我想在项目报告里插一张图，说明各个地区的用户分布情况。`
    *   **预期行为**: `ChartCoordinatorAI` 识别出这是文档/报告制图和地理数据可视化，路由给 `DocumentChartExpert` 或 `DataVisualizationExpert`。最终可能使用 `FoliumRenderTool` (地图) 或 `EChartsRenderTool` (饼图/条形图)。

6.  **模糊提示6**: `展示一下不同产品类别之间的关系。`
    *   **预期行为**: `ChartCoordinatorAI` 识别出这是一个关系/网络图需求，路由给 `DataVisualizationExpert`。最终可能使用 `PyVisRenderTool` 或 `GraphvizRenderTool`。

7.  **模糊提示7**: `把这份数据做成好看一点的图表，要能交互。`
    *   **预期行为**: `ChartCoordinatorAI` 识别出“好看”、“交互”是关键，路由给 `InteractiveDynamicExpert`。最终可能使用 `PlotlyRenderTool` 或 `EChartsRenderTool`。
