# Copyright 2025 Google LLC
# py3Dmol渲染工具 - 分子可视化专家（极简版）

import logging
import tempfile
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any, Optional

from google.genai import types
from .base_render_tool import BaseRenderTool

logger = logging.getLogger(__name__)


class Py3dmolRenderTool(BaseRenderTool):
    """🧬 py3Dmol分子3D可视化渲染工具（极简版）"""
    
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
                        description='要渲染的Python py3Dmol代码。代码必须纯净，包含分子结构加载、样式设置、3D视图配置等。请确保代码自包含且可直接执行。'
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
        """🔧 py3Dmol依赖检查"""
        logger.info("🔍 检查py3Dmol依赖...")
        
        self._py3dmol_available = False
        
        try:
            import py3Dmol
            version = getattr(py3Dmol, '__version__', '未知版本')
            logger.info(f"✅ py3Dmol: {version}")
            self._py3dmol_available = True
        except ImportError:
            logger.warning("❌ py3Dmol未安装，请运行: pip install py3Dmol")
            self._py3dmol_available = False
    
    def _render_sync(self, code: str, output_format: str, width: int, height: int) -> Dict[str, Any]:
        """同步渲染py3Dmol分子可视化（极简版）"""
        
        if not self._py3dmol_available:
            return {
                "success": False,
                "error": "py3Dmol依赖不可用，请安装: pip install py3Dmol"
            }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            try:
                code_file = temp_path / "molecule_code.py"
                output_file = temp_path / f"output.{output_format}"
                
                # 生成极简的可执行代码
                executable_code = self._create_executable_code(code, output_file, output_format, width, height)
                code_file.write_text(executable_code, encoding='utf-8')
                
                logger.info("🚀 执行py3Dmol分子可视化渲染...")
                
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
                        "error": "未生成输出文件"
                    }
                
                # 读取输出文件
                if output_format == "html":
                    content = output_file.read_text(encoding='utf-8')
                    molecule_bytes = content.encode('utf-8')
                else:
                    molecule_bytes = output_file.read_bytes()
                
                if len(molecule_bytes) == 0:
                    return {
                        "success": False,
                        "error": "生成的文件为空"
                    }
                
                logger.info(f"✅ py3Dmol渲染成功，大小: {len(molecule_bytes)} bytes")
                
                return {
                    "success": True,
                    "data": molecule_bytes
                }
                
            except subprocess.TimeoutExpired:
                return {
                    "success": False,
                    "error": "渲染超时（60秒）"
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": f"渲染错误: {str(e)}"
                }
    
    def _create_executable_code(self, user_code: str, output_file: Path, output_format: str, width: int, height: int) -> str:
        """创建可执行的代码（极简版）"""
        
        # 确保导入py3Dmol
        imports = "import py3Dmol\n"
        if 'import py3Dmol' in user_code:
            imports = ""
        
        # 极简的保存逻辑 - 修复Windows路径转义问题
        output_file_str = str(output_file).replace('\\', '\\\\')  # 转义反斜杠
        save_code = f"""
# 自动保存输出
try:
    # 查找viewer对象
    viewer_obj = None
    for var_name in ['view', 'viewer', 'v']:
        if var_name in locals():
            viewer_obj = locals()[var_name]
            break
    
    if viewer_obj is None:
        print("错误: 未找到viewer对象 (view, viewer, v)")
        exit(1)
    
    output_path = r'{output_file_str}'
    if '{output_format}' == 'html':
        html_content = viewer_obj._make_html()
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
    else:
        viewer_obj.png(output_path)
    
    print("保存成功:", output_path)
    
except Exception as e:
    print(f"保存失败: {{e}}")
    exit(1)
"""
        
        # 组合最终代码 - 修复缩进问题
        indented_user_code = '\n'.join('    ' + line for line in user_code.split('\n'))
        indented_save_code = '\n'.join('    ' + line for line in save_code.split('\n'))
        
        final_code = f"""{imports}
try:
{indented_user_code}
{indented_save_code}
except Exception as e:
    print(f"执行错误: {{e}}")
    import traceback
    traceback.print_exc()
    exit(1)
"""
        
        return final_code 