# Copyright 2025 Google LLC
# PyVis渲染工具 - 网络可视化专家

import logging
import tempfile
import subprocess
import sys
import platform
from pathlib import Path
from typing import Dict, Any, Optional
import re

from google.genai import types
from .base_render_tool import BaseRenderTool

logger = logging.getLogger(__name__)


class PyVisRenderTool(BaseRenderTool):
    """🕸️ PyVis网络图可视化渲染工具"""
    
    def __init__(self):
        super().__init__(
            name="render_pyvis",
            description="🕸️ PyVis网络图可视化渲染工具：生成交互式网络图HTML。专门用于社交网络、关系图谱、网络分析等。",
            supported_formats=["html"],
            default_format="html"
        )
        self._check_dependencies()
        self._setup_chinese_fonts()
    
    def _setup_chinese_fonts(self):
        """🔧 设置智能中文字体支持"""
        logger.info("🎨 配置PyVis中文字体支持...")
        
        system = platform.system().lower()
        
        if system == "windows":
            self.chinese_fonts = ["Microsoft YaHei", "SimHei", "SimSun", "KaiTi", "sans-serif"]
        elif system == "darwin":  # macOS
            self.chinese_fonts = ["Arial Unicode MS", "Hiragino Sans GB", "PingFang SC", "sans-serif"]
        else:  # Linux及其他
            self.chinese_fonts = ["WenQuanYi Micro Hei", "Noto Sans CJK SC", "DejaVu Sans", "sans-serif"]
        
        self.font_family = ", ".join([f'"{font}"' for font in self.chinese_fonts])
        
        logger.info(f"✅ PyVis中文字体配置完成: {self.font_family}")
    
    def _get_declaration(self) -> Optional[types.FunctionDeclaration]:
        return types.FunctionDeclaration(
            name=self.name,
            description=self.description,
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    'code': types.Schema(
                        type=types.Type.STRING,
                        description='要渲染的PyVis网络图代码'
                    ),
                    'title': types.Schema(
                        type=types.Type.STRING,
                        description='网络图文件名称',
                        default='pyvis_network'
                    ),
                    'width': types.Schema(
                        type=types.Type.INTEGER,
                        description='网络图宽度（像素）',
                        default=800
                    ),
                    'height': types.Schema(
                        type=types.Type.INTEGER,
                        description='网络图高度（像素）',
                        default=600
                    )
                },
                required=['code'],
            )
        )
    
    def _check_dependencies(self):
        """🔧 PyVis依赖检查和安装指导"""
        logger.info("🔍 检查PyVis依赖...")
        
        self._pyvis_available = False
        self._missing_deps = []
        
        dependencies = [
            {'name': 'pyvis', 'import_name': 'pyvis', 'description': '网络图可视化库', 'required': True, 'install_cmd': 'pip install pyvis'},
            {'name': 'networkx', 'import_name': 'networkx', 'description': '网络分析库', 'required': False, 'install_cmd': 'pip install networkx'},
            {'name': 'pandas', 'import_name': 'pandas', 'description': '数据处理库', 'required': False, 'install_cmd': 'pip install pandas'}
        ]
        
        for dep in dependencies:
            try:
                module = __import__(dep['import_name'])
                version = getattr(module, '__version__', '未知版本')
                logger.info(f"✅ {dep['name']} ({dep['description']}): {version}")
                if dep['name'] == 'pyvis':
                    self._pyvis_available = True
            except ImportError:
                logger.warning(f"❌ {dep['name']} ({dep['description']}): 未安装")
                if dep['required']:
                    self._missing_deps.append(dep)
        
        if self._missing_deps:
            logger.warning(f"🔧 缺少必需依赖: {[dep['name'] for dep in self._missing_deps]}")
            logger.info(self._get_installation_guide())
        else:
            logger.info("✅ PyVis渲染工具依赖检查通过")
    
    def _get_installation_guide(self) -> str:
        if not self._missing_deps: return "所有依赖已安装"
        guide = "📦 PyVis依赖安装指南:\n" + "=" * 40 + "\n"
        for dep in self._missing_deps:
            guide += f"• {dep['name']}: {dep['install_cmd']}\n"
        install_cmds = [dep['install_cmd'] for dep in self._missing_deps]
        guide += f"\n一键安装: {'; '.join(install_cmds) if platform.system() == 'Windows' else ' && '.join(install_cmds)}\n"
        guide += "\n🔗 更多信息:\n• PyVis文档: https://pyvis.readthedocs.io/\n"
        return guide

    def _render_sync(self, code: str, output_format: str = "html", width: int = 800, height: int = 600, title: str = "pyvis_network") -> Dict[str, Any]:
        """同步渲染PyVis网络图"""
        if not self._pyvis_available:
            return {"success": False, "error": "PyVis依赖不可用", "installation_guide": self._get_installation_guide()}
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            try:
                code_file = temp_path / "network_code.py"
                output_file = temp_path / "output.html"
                
                processed_code = self._preprocess_code(code, output_file, width, height, title)
                code_file.write_text(processed_code, encoding='utf-8')
                
                logger.info("🚀 执行PyVis网络图渲染...")
                result = subprocess.run(
                    [sys.executable, str(code_file)],
                    capture_output=True, text=True, timeout=60, cwd=temp_dir, encoding='utf-8', errors='replace'
                )
                
                if result.returncode != 0:
                    return {"success": False, "error": f"Python代码执行失败:\n{result.stderr}"}
                
                if not output_file.exists():
                    return {"success": False, "error": "代码执行完成但未生成网络图文件"}
                
                content = output_file.read_text(encoding='utf-8-sig')
                
                if not content:
                    return {"success": False, "error": "生成的网络图文件为空"}
                
                logger.info(f"✅ PyVis网络图渲染成功，大小: {len(content)} bytes")
                return {"success": True, "data": content.encode('utf-8')}
                
            except subprocess.TimeoutExpired:
                return {"success": False, "error": "网络图渲染超时（60秒）"}
            except Exception as e:
                return {"success": False, "error": f"渲染过程发生错误: {str(e)}"}
    
    def _preprocess_code(self, code: str, output_file: Path, width: int, height: int, title: str) -> str:
        """
        预处理PyVis代码，注入模板路径、保存逻辑并增强错误处理。
        """
        # 核心修复：处理从LLM传来的、包含"\\n"转义字符的单行代码字符串
        code = code.replace('\\n', '\n')

        template_path_str = None
        try:
            import pyvis
            import os
            from pathlib import Path
            template_path = Path(os.path.dirname(pyvis.__file__)) / "templates" / "index.html"
            if template_path.exists():
                template_path_str = str(template_path.resolve()).replace("\\", "\\\\")
            else:
                logger.warning("PyVis template 'index.html' not found. Will use default.")
        except (ImportError, FileNotFoundError) as e:
            logger.error(f"❌ 无法定位PyVis模板文件，将使用默认模板: {e}")

        imports = [
            "from pyvis.network import Network",
            "import pandas as pd",
            "import networkx as nx"
        ]
        
        code_lines = code.split('\n')
        filtered_code_lines = [line for line in code_lines if not re.search(r"=\s*Network\(", line)]
        processed_code_body = "\n".join(filtered_code_lines)
        
        if template_path_str:
            network_init = f"net = Network(notebook=True, width='{width}px', height='{height}px', heading='{title}', template=r'{template_path_str}')"
        else:
            network_init = f"net = Network(notebook=True, width='{width}px', height='{height}px', heading='{title}')"

        font_config_logic = f"""
try:
    net.set_options(r'''
    {{
        "nodes": {{ "font": {{ "face": "{self.font_family}" }} }},
        "edges": {{ "font": {{ "face": "{self.font_family}" }} }}
    }}
    ''')
except Exception as e:
    print(f"Failed to set fonts: {{e}}")
"""
        
        safe_output_path = str(output_file).replace('\\', '\\\\')
        save_logic = f"net.save_graph(r'{safe_output_path}')"
        
        full_code = "\n".join([
            *imports,
            network_init,
            processed_code_body,
            font_config_logic,
            save_logic
        ])

        return full_code
