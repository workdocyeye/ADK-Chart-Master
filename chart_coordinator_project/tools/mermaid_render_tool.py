# Copyright 2025 Google LLC
# Mermaid渲染工具 - 流程图与图表专家

import logging
import platform
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional

from google.genai import types
from .base_render_tool import BaseRenderTool

logger = logging.getLogger(__name__)


class MermaidRenderTool(BaseRenderTool):
    """🌊 Mermaid图表渲染工具"""
    
    def __init__(self):
        super().__init__(
            name="render_mermaid",
            description="🌊 Mermaid图表渲染工具：将Mermaid代码转换为流程图、时序图、甘特图等。支持多种图表类型和输出格式。",
            supported_formats=["png", "svg", "pdf"],
            default_format="png"
        )
        self._check_dependencies()
    
    def _get_declaration(self) -> Optional[types.FunctionDeclaration]:
        """🔧 定义Mermaid渲染工具的精确函数声明"""
        return types.FunctionDeclaration(
            name=self.name,
            description=self.description,
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    'code': types.Schema(
                        type=types.Type.STRING,
                        description='要渲染的Mermaid图表代码。支持flowchart、sequence、class、state、journey、gantt等图表类型'
                    ),
                    'output_format': types.Schema(
                        type=types.Type.STRING,
                        description='输出格式。png适合一般使用，svg适合矢量图，pdf适合文档',
                        enum=['png', 'svg', 'pdf'],
                        default='png'
                    ),
                    'title': types.Schema(
                        type=types.Type.STRING,
                        description='图表文件名称（不含扩展名）',
                        default='mermaid_diagram'
                    ),
                    'width': types.Schema(
                        type=types.Type.INTEGER,
                        description='图片宽度（像素，仅适用于png/pdf）',
                        default=1200
                    ),
                    'height': types.Schema(
                        type=types.Type.INTEGER,
                        description='图片高度（像素，仅适用于png/pdf）',
                        default=800
                    )
                },
                required=['code'],
            )
        )
    
    def _get_platform_command(self, base_cmd: str):
        """获取平台特定的命令"""
        if platform.system() == "Windows":
            return [f"{base_cmd}.cmd"]
        return [base_cmd]
    
    def _check_dependencies(self):
        """🔧 增强的依赖检查 - 多种方式尝试，友好错误提示"""
        self._mmdc_available = False
        self._mmdc_cmd = None
        
        # Windows下的明确路径优先尝试
        if platform.system() == "Windows":
            mmdc_explicit_path = r"C:\Users\Lenovo\AppData\Roaming\npm\mmdc.cmd"
            if Path(mmdc_explicit_path).exists():
                try:
                    result = subprocess.run(
                        [mmdc_explicit_path, "--version"],
                        capture_output=True, 
                        text=True,
                        timeout=10,
                        encoding='utf-8',
                        errors='replace'
                    )
                    if result.returncode == 0:
                        version_info = result.stdout.strip()
                        logger.info(f"✅ mermaid-cli 检测成功 (明确路径)! 版本: {version_info}")
                        self._mmdc_available = True
                        self._mmdc_cmd = [mmdc_explicit_path]
                        return
                except Exception as e:
                    logger.debug(f"❌ 明确路径测试失败: {e}")
        
        # 获取平台特定的命令候选列表 (回退方案)
        candidates = self._get_platform_command("mmdc")
        
        # 尝试多种方式
        for cmd_variant in [
            candidates + ["--version"],
            ["mmdc", "--version"],
            ["npx", "@mermaid-js/mermaid-cli", "--version"]
        ]:
            try:
                logger.info(f"🔍 测试命令: {' '.join(cmd_variant)}")
                
                result = subprocess.run(
                    cmd_variant,
                    capture_output=True, 
                    text=True,
                    timeout=15,
                    encoding='utf-8',
                    errors='replace'
                )
            
                if result.returncode == 0:
                    version_info = result.stdout.strip()
                    logger.info(f"✅ mermaid-cli 检测成功! 版本: {version_info}")
                    self._mmdc_available = True
                    self._mmdc_cmd = cmd_variant[:-1]  # 去掉--version
                    return
                else:
                    logger.debug(f"❌ 命令失败 ({result.returncode}): {result.stderr}")
                
            except subprocess.TimeoutExpired:
                logger.debug(f"⏰ 命令超时: {' '.join(cmd_variant)}")
            except FileNotFoundError:
                logger.debug(f"📂 命令不存在: {cmd_variant[0]}")
            except Exception as e:
                logger.debug(f"❌ 执行异常: {e}")
        
        # 所有方式都失败，生成友好提示
        self._show_installation_help()
    
    def _show_installation_help(self):
        """🔧 显示安装帮助"""
        logger.warning("❌ mermaid-cli 未安装或不可用")
        
        help_text = """
🔧 Mermaid渲染工具安装指南：

方式1：使用npm（推荐）
  npm install -g @mermaid-js/mermaid-cli

方式2：使用yarn
  yarn global add @mermaid-js/mermaid-cli

方式3：使用pnpm
  pnpm add -g @mermaid-js/mermaid-cli

安装后验证：
  mmdc --version

Windows特殊说明：
- 可能需要以管理员身份运行PowerShell
- 如果PATH未正确设置，可以使用：npx @mermaid-js/mermaid-cli

故障排除：
1. 确保已安装Node.js (https://nodejs.org/)
2. 重启终端/PowerShell
3. 检查PATH环境变量是否包含npm全局目录
        """
        
        logger.info(help_text)
    
    def _get_installation_guide(self, missing_deps):
        """获取安装指南"""
        guide = "📦 Mermaid依赖安装指南:\n"
        guide += "=" * 40 + "\n"
        guide += "• @mermaid-js/mermaid-cli: npm install -g @mermaid-js/mermaid-cli\n"
        
        if platform.system() == "Windows":
            guide += "\n一键安装: npm install -g @mermaid-js/mermaid-cli\n"
        else:
            guide += "\n一键安装: npm install -g @mermaid-js/mermaid-cli\n"
        
        guide += "\n🔗 更多信息:\n"
        guide += "• Mermaid文档: https://mermaid.js.org/\n"
        guide += "• CLI工具: https://github.com/mermaid-js/mermaid-cli\n"
        
        return guide
    
    def _render_sync(self, code: str, output_format: str, width: int, height: int, **kwargs) -> Dict[str, Any]:
        """同步渲染Mermaid图表"""
        
        if not self._mmdc_available:
            return {
                "success": False,
                "error": "mermaid-cli未安装或不可用",
                "installation_guide": self._get_installation_guide(["@mermaid-js/mermaid-cli"]),
                "suggestion": "请先安装mermaid-cli: npm install -g @mermaid-js/mermaid-cli"
            }
        
        # 创建临时目录
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            try:
                # 准备输入和输出文件
                input_file = temp_path / "diagram.mmd"
                output_file = temp_path / f"output.{output_format}"
                
                # 预处理Mermaid代码
                processed_code = self._preprocess_mermaid_code(code)
                
                # 写入Mermaid代码到文件
                input_file.write_text(processed_code, encoding='utf-8')
                
                # 构建渲染命令
                cmd = self._mmdc_cmd + [
                    "-i", str(input_file),
                    "-o", str(output_file),
                    "-t", "default",
                    "-b", "white",
                ]
                
                # 添加尺寸参数
                if output_format in ["png", "pdf"]:
                    cmd.extend(["-w", str(width)])
                    cmd.extend(["-H", str(height)])
                
                logger.info(f"🚀 执行渲染命令: {' '.join(cmd)}")
                
                # 执行渲染命令
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=30,
                    cwd=temp_dir,
                    encoding='utf-8',
                    errors='replace'
                )
                
                logger.info(f"🔍 命令执行结果 - 返回码: {result.returncode}")
                
                if result.stdout:
                    logger.info(f"📤 标准输出: {result.stdout}")
                if result.stderr:
                    logger.warning(f"⚠️ 标准错误: {result.stderr}")
                
                if result.returncode != 0:
                    error_msg = f"mermaid-cli渲染失败:\n{result.stderr}"
                    logger.error(error_msg)
                    return {
                        "success": False,
                        "error": error_msg
                    }
                
                # 检查输出文件是否存在
                if not output_file.exists():
                    return {
                        "success": False,
                        "error": "渲染完成但未生成输出文件"
                    }
                
                # 读取渲染结果
                image_bytes = output_file.read_bytes()
                
                if len(image_bytes) == 0:
                    return {
                        "success": False,
                        "error": "生成的图片文件为空"
                    }
                
                logger.info(f"✅ Mermaid图表渲染成功，大小: {len(image_bytes)} bytes")
                
                return {
                    "success": True,
                    "data": image_bytes
                }
                
            except subprocess.TimeoutExpired:
                return {
                    "success": False,
                    "error": "渲染超时（30秒），请检查图表代码复杂度"
                }
            except Exception as e:
                logger.error(f"❌ Mermaid渲染过程中出现异常: {e}", exc_info=True)
                return {
                    "success": False,
                    "error": f"渲染过程异常: {e}"
                }
    
    def _preprocess_mermaid_code(self, code: str) -> str:
        """预处理Mermaid代码"""
        # 移除代码块标记
        code = code.strip()
        if code.startswith("```mermaid"):
            code = code[10:]
        elif code.startswith("```"):
            code = code[3:]
        if code.endswith("```"):
            code = code[:-3]
        
        # 清理和格式化
        lines = []
        for line in code.split('\n'):
            line = line.strip()
            if line and not line.startswith('<!--'):
                lines.append(line)
        
        return '\n'.join(lines) 