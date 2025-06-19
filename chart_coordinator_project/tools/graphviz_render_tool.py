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
Graphviz渲染工具

这个模块实现了Graphviz图形的渲染功能，支持：
- DOT语言图形描述
- 多种布局算法（dot、neato、fdp、sfdp、twopi、circo）
- 有向图、无向图、子图
- 丰富的节点和边样式
- 多种输出格式（PNG、SVG、PDF、DOT）
"""

import logging
import subprocess
import tempfile
import os
import shutil
from typing import Dict, Any, Optional
import re
import platform

try:
    import graphviz
    GRAPHVIZ_AVAILABLE = True
except ImportError:
    GRAPHVIZ_AVAILABLE = False

from google.genai import types
from .base_render_tool import BaseRenderTool

logger = logging.getLogger(__name__)

 
class GraphvizRenderTool(BaseRenderTool):
    """
    Graphviz图形渲染工具
    
    支持渲染各种类型的图形：
    - 有向图 (Directed Graph)：层次结构、流程图、依赖关系
    - 无向图 (Undirected Graph)：网络图、关系图
    - 混合图 (Mixed Graph)：部分有向、部分无向
    - 集群图 (Cluster Graph)：包含子图的复杂图形
    """
    
    # 支持的布局引擎
    LAYOUT_ENGINES = {
        'dot': '分层布局，适合有向无环图、流程图',
        'neato': '弹簧模型布局，适合无向图',
        'fdp': '弹簧模型布局（大图优化），适合大型无向图',
        'sfdp': '多尺度弹簧模型，适合超大图',
        'twopi': '径向布局，适合树状结构',
        'circo': '圆形布局，适合循环结构'
    }
    
    def __init__(self):
        super().__init__(
            name="graphviz_render",
            description="Graphviz图形可视化工具，支持DOT语言和多种布局算法",
            supported_formats=["png", "svg", "pdf", "dot", "ps"],
            default_format="png"
        )
        self._check_dependencies()
    
    def _check_dependencies(self):
        """检查Graphviz依赖是否已安装"""
        try:
            # 检查Python库
            if GRAPHVIZ_AVAILABLE:
                import graphviz
                logger.info(f"✅ graphviz Python库版本: {graphviz.__version__}")
                self._python_lib_available = True
            else:
                logger.warning("❌ graphviz Python库未安装")
                self._python_lib_available = False
            
            # 检查命令行工具
            self.graphviz_executable = self._find_graphviz_executable()
            if self.graphviz_executable:
                logger.info(f"✅ Graphviz可执行文件: {self.graphviz_executable}")
                self._cli_available = True
            else:
                logger.warning("❌ Graphviz命令行工具未找到")
                self._cli_available = False
                
            # 至少需要其中一种方式可用
            self._graphviz_available = self._python_lib_available or self._cli_available
            if not self._graphviz_available:
                logger.error("❌ Graphviz不可用，请安装：pip install graphviz 或安装Graphviz软件包")
                
        except Exception as e:
            logger.warning(f"❌ Graphviz依赖检查失败: {e}")
            self._python_lib_available = False
            self._cli_available = False
            self._graphviz_available = False
    
    def _get_declaration(self) -> Optional[types.FunctionDeclaration]:
        """
        🔧 Graphviz工具的函数声明
        
        包含Graphviz特有的参数和详细的DOT语言说明
        """
        return types.FunctionDeclaration(
            name=self.name,
            description="Graphviz图形可视化工具。使用DOT语言创建各种类型的图形，包括有向图、无向图、网络图、流程图等。",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    'code': types.Schema(
                        type=types.Type.STRING,
                        description='''DOT语言代码，用于描述图形结构。

基本语法：
1. 有向图：
   digraph G {
       A -> B -> C;
       A -> C;
   }

2. 无向图：
   graph G {
       A -- B -- C;
       A -- C;
   }

3. 节点样式：
   A [label="节点A", color=red, shape=box];

4. 边样式：
   A -> B [label="边标签", color=blue, style=dashed];

5. 子图/集群：
   subgraph cluster_0 {
       label="子图";
       A; B;
   }

支持的节点形状：box, circle, ellipse, diamond, triangle, plaintext等
支持的样式：solid, dashed, dotted, bold等
支持的颜色：red, blue, green, black或十六进制#RRGGBB'''
                    ),
                    'output_format': types.Schema(
                        type=types.Type.STRING,
                        description='输出格式：png(默认)、svg、pdf、dot、ps',
                        enum=['png', 'svg', 'pdf', 'dot', 'ps'],
                        default='png'
                    ),
                    'title': types.Schema(
                        type=types.Type.STRING,
                        description='图形文件名称',
                        default='graphviz_graph'
                    ),
                    'layout_engine': types.Schema(
                        type=types.Type.STRING,
                        description=f'''布局引擎：
- dot: 分层布局，适合有向无环图、流程图
- neato: 弹簧模型布局，适合无向图
- fdp: 弹簧模型布局（大图优化）
- sfdp: 多尺度弹簧模型，适合超大图
- twopi: 径向布局，适合树状结构
- circo: 圆形布局，适合循环结构''',
                        enum=list(self.LAYOUT_ENGINES.keys()),
                        default='dot'
                    ),
                    'dpi': types.Schema(
                        type=types.Type.INTEGER,
                        description='图像分辨率（DPI）',
                        default=96
                    ),
                    'rankdir': types.Schema(
                        type=types.Type.STRING,
                        description='图形方向（仅dot布局）：TB(上到下)、BT(下到上)、LR(左到右)、RL(右到左)',
                        enum=['TB', 'BT', 'LR', 'RL'],
                        default='TB'
                    ),
                    'width': types.Schema(
                        type=types.Type.INTEGER,
                        description='图片宽度（像素）',
                        default=800
                    ),
                    'height': types.Schema(
                        type=types.Type.INTEGER,
                        description='图片高度（像素）',
                        default=600
                    )
                },
                required=['code'],
            )
        )
    
    def _render_sync(self, 
                    code: str, 
                    output_format: str, 
                    width: int, 
                    height: int) -> Dict[str, Any]:
        """
        同步渲染Graphviz图形
        
        渲染策略：
        1. 优先使用graphviz Python库
        2. 回退到命令行工具
        3. 自动处理DOT语法
        4. 支持多种布局引擎
        """
        try:
            # 预处理DOT代码
            processed_code = self._preprocess_dot_code(code)
            
            # 验证DOT语法
            validation_result = self._validate_dot_syntax(processed_code)
            if not validation_result["valid"]:
                return {
                    "success": False,
                    "error": f"DOT语法错误: {validation_result['error']}"
                }
            
            # 尝试使用Python库渲染
            if self._python_lib_available:
                logger.info("使用graphviz Python库渲染")
                result = self._render_with_python_lib(processed_code, output_format, width, height)
                if result["success"]:
                    return result
                logger.warning(f"Python库渲染失败，回退到命令行: {result.get('error')}")
            
            # 使用命令行工具渲染
            if self._cli_available:
                logger.info("使用Graphviz命令行工具渲染")
                return self._render_with_command_line(processed_code, output_format, width, height)
            
            return {
                "success": False,
                "error": "Graphviz不可用。请安装：pip install graphviz 或安装Graphviz软件包"
            }
            
        except Exception as e:
            logger.error(f"Graphviz渲染失败: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"Graphviz渲染异常: {e}"
            }
    
    def _preprocess_dot_code(self, code: str) -> str:
        """
        预处理DOT代码
        - 自动添加图形声明（如果缺少）
        - 清理多余的空白
        - 强制注入全局中文字体设置以解决中文乱码问题
        """
        code = code.strip()

        # 1. 自动添加图形声明（如果缺少）
        if not re.match(r'^\s*(strict\s+)?(graph|digraph)', code, re.IGNORECASE):
            if '->' in code:
                code = f'digraph G {{\n{code}\n}}'
            else:
                code = f'graph G {{\n{code}\n}}'
        
        # 2. 移除所有已存在的fontname属性，避免AI模型指定不支持的字体
        code = re.sub(r'fontname\s*=\s*".*?"', '', code, flags=re.IGNORECASE)
        code = re.sub(r"fontname\s*=\s*'.*?'", '', code, flags=re.IGNORECASE)
        # 清理可能留下的多余逗号或空格
        code = re.sub(r'\[\s*,', '[', code)
        code = re.sub(r',\s*,', ',', code)
        code = re.sub(r',\s*\]', ']', code)

        # 3. 选择适合当前操作系统的中文字体
        system = platform.system()
        if system == "Windows":
            # 在Windows上，微软雅黑是最常见且效果好的中文字体
            font_name = "Microsoft YaHei"
        elif system == "Darwin":  # macOS
            # 在macOS上，苹方是标准选择
            font_name = "PingFang SC"
        else:  # Linux
            # 在Linux上，文泉驿微米黑是常见的开源中文字体
            font_name = "WenQuanYi Micro Hei"
        
        logger.info(f"为Graphviz选择的中文字体: {font_name} (OS: {system})")

        # 4. 准备要注入的全局字体设置
        font_attributes = f'''
    // Injected by ADK to support Chinese characters
    graph [fontname="{font_name}"];
    node [fontname="{font_name}"];
    edge [fontname="{font_name}"];
'''

        # 5. 使用正则表达式找到第一个开括号'{'并注入属性
        # 这种方法比基于行的查找更可靠，能适应不同的代码格式
        match = re.search(r'{', code)
        if match:
            insertion_point = match.end()
            processed_code = code[:insertion_point] + font_attributes + code[insertion_point:]
            logger.info(f"✅ 成功为Graphviz注入全局中文字体设置。")
            return processed_code
        else:
            # 如果没有找到'{'，说明DOT代码格式可能不规范，但还是返回清理过的代码
            logger.warning("在DOT代码中未找到开括号'{'，无法注入全局字体设置。")
            return code
    
    def _validate_dot_syntax(self, code: str) -> Dict[str, Any]:
        """
        验证DOT语法
        
        基本的语法检查
        """
        if not code.strip():
            return {"valid": False, "error": "代码为空"}
        
        # 检查基本结构
        if not (code.startswith('digraph') or code.startswith('graph') or code.startswith('strict')):
            return {"valid": False, "error": "代码必须以digraph、graph或strict开头"}
        
        # 检查大括号配对
        open_braces = code.count('{')
        close_braces = code.count('}')
        
        if open_braces != close_braces:
            return {"valid": False, "error": "大括号不匹配"}
        
        if open_braces == 0:
            return {"valid": False, "error": "缺少大括号"}
        
        return {"valid": True}
    
    def _find_graphviz_executable(self) -> Optional[str]:
        """
        查找Graphviz可执行文件
        优先检查Windows标准安装路径，然后检查PATH
        """
        # Windows标准安装路径
        windows_paths = [
            r"C:\Program Files\Graphviz\bin\dot.exe",
            r"C:\Program Files (x86)\Graphviz\bin\dot.exe",
        ]
        
        # 首先检查Windows标准路径
        for path in windows_paths:
            if os.path.exists(path):
                logger.info(f"找到Graphviz: {path}")
                return path
        
        # 然后检查PATH中的可执行文件
        executables = ['dot', 'neato', 'fdp', 'sfdp', 'twopi', 'circo']
        for executable in executables:
            found_path = shutil.which(executable)
            if found_path:
                logger.info(f"在PATH中找到Graphviz: {found_path}")
                return found_path
        
        logger.warning("未找到Graphviz可执行文件")
        return None
    
    def _render_with_python_lib(self, 
                               code: str, 
                               output_format: str, 
                               width: int, 
                               height: int) -> Dict[str, Any]:
        """
        使用graphviz Python库渲染
        """
        try:
            # 检测图形类型
            if code.strip().startswith('digraph'):
                source = graphviz.Source(code, format=output_format, engine='dot')
            else:
                source = graphviz.Source(code, format=output_format, engine='neato')
            
            # 渲染
            with tempfile.TemporaryDirectory() as temp_dir:
                output_path = source.render(
                    filename='graph',
                    directory=temp_dir,
                    cleanup=True
                )
                
                # 读取输出文件
                with open(output_path, 'rb') as f:
                    data = f.read()
                
                return {
                    "success": True,
                    "data": data
                }
                
        except graphviz.CalledProcessError as e:
            return {
                "success": False,
                "error": f"Graphviz渲染错误: {e}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Python库渲染失败: {e}"
            }
    
    def _render_with_command_line(self, 
                                code: str, 
                                output_format: str, 
                                width: int, 
                                height: int) -> Dict[str, Any]:
        """
        使用Graphviz命令行工具渲染
        """
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                # 写入DOT文件
                input_file = os.path.join(temp_dir, "graph.dot")
                with open(input_file, 'w', encoding='utf-8') as f:
                    f.write(code)
                
                # 确定输出文件
                output_file = os.path.join(temp_dir, f"graph.{output_format}")
                
                # 决定使用哪个可执行文件
                executable = self.graphviz_executable or 'dot'
                
                # 如果是完整路径，直接使用
                if os.path.isabs(executable) or executable.endswith('.exe'):
                    dot_cmd = executable
                else:
                    # 尝试在PATH中查找
                    dot_cmd = shutil.which(executable)
                    if not dot_cmd:
                        # 尝试Windows完整路径
                        windows_path = r"C:\Program Files\Graphviz\bin\dot.exe"
                        if os.path.exists(windows_path):
                            dot_cmd = windows_path
                        else:
                            return {
                                "success": False,
                                "error": f"找不到Graphviz可执行文件: {executable}"
                            }
                
                # 构建命令
                cmd = [
                    dot_cmd,
                    f'-T{output_format}',
                    f'-o{output_file}',
                    input_file
                ]
                
                # 添加DPI设置（对位图格式）
                if output_format in ['png', 'jpg', 'jpeg']:
                    cmd.insert(1, f'-Gdpi=96')
                
                logger.info(f"执行命令: {' '.join(cmd)}")
                
                # 执行渲染
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=30,
                    encoding='utf-8',
                    errors='replace'
                )
                
                if result.returncode != 0:
                    return {
                        "success": False,
                        "error": f"Graphviz渲染失败: {result.stderr}"
                    }
                
                # 检查输出文件
                if not os.path.exists(output_file):
                    return {
                        "success": False,
                        "error": f"输出文件未生成: {output_file}"
                    }
                
                # 读取输出文件
                with open(output_file, 'rb') as f:
                    data = f.read()
                
                return {
                    "success": True,
                    "data": data
                }
                
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Graphviz渲染超时（30秒）"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"命令行渲染失败: {e}"
            }
    
    def _get_mime_type(self, format: str) -> str:
        """
        重写父类方法，添加Graphviz特有的MIME类型
        """
        graphviz_mime_types = {
            'dot': 'text/vnd.graphviz',
            'ps': 'application/postscript',
            'png': 'image/png',
            'svg': 'image/svg+xml',
            'pdf': 'application/pdf'
        }
        return graphviz_mime_types.get(format.lower(), 'application/octet-stream') 