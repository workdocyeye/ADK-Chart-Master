# Copyright 2025 Google LLC
# py3Dmol渲染工具 - 分子可视化专家

import logging
import tempfile
import subprocess
import sys
import platform
from pathlib import Path
from typing import Dict, Any, Optional

from google.genai import types
from .base_render_tool import BaseRenderTool

logger = logging.getLogger(__name__)


class Py3dmolRenderTool(BaseRenderTool):
    """🧬 py3Dmol分子3D可视化渲染工具"""
    
    def __init__(self):
        super().__init__(
            name="render_py3dmol",
            description="🧬 py3Dmol分子3D可视化渲染工具：将Python py3Dmol代码转换为分子结构3D可视化。专门用于蛋白质结构、分子建模、化学结构展示等科学可视化。",
            supported_formats=["html", "png"],
            default_format="html"
        )
        self._check_dependencies()
    
    def _get_declaration(self) -> Optional[types.FunctionDeclaration]:
        """🔧 定义py3Dmol渲染工具的精确函数声明"""
        return types.FunctionDeclaration(
            name=self.name,
            description=self.description,
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    'code': types.Schema(
                        type=types.Type.STRING,
                        description='要渲染的Python py3Dmol代码。应该包含分子结构加载、样式设置、3D视图配置等'
                    ),
                    'output_format': types.Schema(
                        type=types.Type.STRING,
                        description='输出格式。html生成交互式3D分子视图，png生成静态图片',
                        enum=['html', 'png'],
                        default='html'
                    ),
                    'title': types.Schema(
                        type=types.Type.STRING,
                        description='分子视图文件名称（不含扩展名）',
                        default='py3dmol_molecule'
                    ),
                    'width': types.Schema(
                        type=types.Type.INTEGER,
                        description='视图宽度（像素）',
                        default=800
                    ),
                    'height': types.Schema(
                        type=types.Type.INTEGER,
                        description='视图高度（像素）',
                        default=600
                    )
                },
                required=['code'],
            )
        )
    
    def _check_dependencies(self):
        """🔧 py3Dmol依赖检查和安装指导"""
        logger.info("🔍 检查py3Dmol依赖...")
        
        self._py3dmol_available = False
        self._missing_deps = []
        
        # 检查核心依赖
        dependencies = [
            {
                'name': 'py3Dmol',
                'import_name': 'py3Dmol',
                'description': '分子3D可视化库',
                'required': True,
                'install_cmd': 'pip install py3Dmol'
            },
            {
                'name': 'IPython',
                'import_name': 'IPython',
                'description': 'Jupyter支持',
                'required': False,
                'install_cmd': 'pip install IPython'
            }
        ]
        
        for dep in dependencies:
            try:
                module = __import__(dep['import_name'])
                version = getattr(module, '__version__', '未知版本')
                logger.info(f"✅ {dep['name']} ({dep['description']}): {version}")
                
                if dep['name'] == 'py3Dmol':
                    self._py3dmol_available = True
                    
            except ImportError:
                logger.warning(f"❌ {dep['name']} ({dep['description']}): 未安装")
                if dep['required']:
                    self._missing_deps.append(dep)
        
        if self._missing_deps:
            logger.warning(f"🔧 缺少必需依赖: {[dep['name'] for dep in self._missing_deps]}")
            logger.info(self._get_installation_guide())
        else:
            logger.info("✅ py3Dmol渲染工具依赖检查通过")
    
    def _get_installation_guide(self) -> str:
        """获取安装指南"""
        if not self._missing_deps:
            return "所有依赖已安装"
        
        guide = "📦 py3Dmol依赖安装指南:\n"
        guide += "=" * 40 + "\n"
        
        for dep in self._missing_deps:
            guide += f"• {dep['name']}: {dep['install_cmd']}\n"
        
        # 一键安装命令
        install_cmds = [dep['install_cmd'] for dep in self._missing_deps]
        if platform.system() == "Windows":
            guide += f"\n一键安装: {'; '.join(install_cmds)}\n"
        else:
            guide += f"\n一键安装: {' && '.join(install_cmds)}\n"
        
        guide += "\n🔗 更多信息:\n"
        guide += "• py3Dmol文档: https://3dmol.csb.pitt.edu/\n"
        guide += "• py3Dmol GitHub: https://github.com/3dmol/3Dmol.js\n"
        
        return guide
    
    def _render_sync(self, code: str, output_format: str, width: int, height: int) -> Dict[str, Any]:
        """同步渲染py3Dmol分子可视化"""
        
        if not self._py3dmol_available:
            missing_deps = ["py3Dmol"]
            return {
                "success": False,
                "error": "py3Dmol依赖不可用",
                "installation_guide": self._get_installation_guide(),
                "suggestion": "请先安装依赖: pip install py3Dmol"
            }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            try:
                code_file = temp_path / "molecule_code.py"
                output_file = temp_path / f"output.{output_format}"
                
                # 预处理代码
                processed_code = self._preprocess_code(code, output_file, output_format, width, height)
                code_file.write_text(processed_code, encoding='utf-8')
                
                logger.info(f"🚀 执行py3Dmol分子可视化渲染...")
                
                # 执行Python代码
                result = subprocess.run(
                    [sys.executable, str(code_file)],
                    capture_output=True,
                    text=True,
                    timeout=60,
                    cwd=temp_dir,
                    encoding='utf-8',
                    errors='replace'
                )
                
                if result.returncode != 0:
                    return {
                        "success": False,
                        "error": f"Python代码执行失败:\n{result.stderr}"
                    }
                
                if not output_file.exists():
                    return {
                        "success": False,
                        "error": "代码执行完成但未生成分子可视化文件"
                    }
                
                if output_format == "html":
                    content = output_file.read_text(encoding='utf-8')
                    molecule_bytes = content.encode('utf-8')
                else:
                    molecule_bytes = output_file.read_bytes()
                
                if len(molecule_bytes) == 0:
                    return {
                        "success": False,
                        "error": "生成的分子可视化文件为空"
                    }
                
                logger.info(f"✅ py3Dmol分子可视化渲染成功，大小: {len(molecule_bytes)} bytes")
                
                return {
                    "success": True,
                    "data": molecule_bytes
                }
                
            except subprocess.TimeoutExpired:
                return {
                    "success": False,
                    "error": "分子可视化渲染超时（60秒）"
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": f"渲染过程发生错误: {str(e)}"
                }
    
    def _preprocess_code(self, code: str, output_file: Path, output_format: str, width: int, height: int) -> str:
        """预处理py3Dmol代码，增强错误处理和中文支持"""
        
        # 确保有必要的导入
        imports = []
        if 'import py3Dmol' not in code:
            imports.append("import py3Dmol")
        
        # 添加异常处理导入
        imports.append("import traceback")
        imports.append("import os")
        
        imports_str = '\n'.join(imports) + '\n' if imports else ''
        
        # 检查用户代码中是否已经创建了viewer
        has_viewer_creation = any(pattern in code for pattern in [
            'py3Dmol.view(', 'view = py3Dmol.view', 'viewer = py3Dmol.view'
        ])
        
        # 如果用户代码中没有创建viewer，我们需要添加
        viewer_creation = ""
        if not has_viewer_creation:
            viewer_creation = f"""
    # 创建py3Dmol viewer（如果用户代码中没有创建）
    view = py3Dmol.view(width={width}, height={height})
"""
        
        # 创建增强的保存逻辑
        save_logic = f"""
    # 增强的自动保存逻辑
    # 查找viewer对象
    viewer_obj = None
    if 'viewer' in locals():
        viewer_obj = viewer
    elif 'view' in locals():
        viewer_obj = view
    elif 'v' in locals():
        viewer_obj = v
    
    if viewer_obj is None:
        print("错误: 未找到py3Dmol viewer对象")
        print("提示: 请确保代码中创建了viewer变量，例如:")
        print("view = py3Dmol.view(width={width}, height={height})")
        exit(1)
    
    if '{output_format}' == 'html':
        # 生成增强的HTML（支持中文）
        html_content = viewer_obj._make_html()
        
        # 注入中文字体支持
        font_css = '<style>body, div, span {font-family: "Microsoft YaHei", "SimHei", "SimSun", "Arial Unicode MS", "WenQuanYi Micro Hei", sans-serif !important;}</style>'
        if '<head>' in html_content:
            html_content = html_content.replace('<head>', '<head>\n' + font_css)
        
        # 确保UTF-8编码
        if '<meta charset=' not in html_content.lower():
            html_content = html_content.replace('<head>', '<head>\n    <meta charset="UTF-8">')
        
        # 自动插入<!DOCTYPE html>，避免Quirks Mode
        if not html_content.lstrip().lower().startswith('<!doctype html>'):
            html_content = '<!DOCTYPE html>\n' + html_content
        
        with open(r"{output_file}", 'w', encoding='utf-8') as f:
            f.write(html_content)
    else:
        # PNG输出
        try:
            viewer_obj.png(r"{output_file}")
        except Exception as png_error:
            print(f"PNG生成失败: {{png_error}}")
            print("提示: PNG功能需要额外的依赖，建议使用HTML格式")
            exit(1)
    
    print("✅ 分子可视化已保存: " + str(r"{output_file}"))"""
        
        # 对用户代码进行缩进处理
        indented_code = '\n'.join('    ' + line for line in code.split('\n'))
        
        processed_code = f"""
{imports_str}

try:
{viewer_creation}
    # 用户代码
{indented_code}

{save_logic}

except ImportError as e:
    print(f"❌ 导入错误: {{e}}")
    print("请确保已安装py3Dmol: pip install py3Dmol")
    exit(1)
except Exception as e:
    print(f"❌ 代码执行错误: {{e}}")
    traceback.print_exc()
    exit(1)
"""
        return processed_code 