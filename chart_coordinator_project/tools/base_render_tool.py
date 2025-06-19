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
基础渲染工具类

这个模块定义了所有图表渲染工具的基础类，提供统一的接口和通用功能。
所有具体的渲染工具都应该继承自BaseRenderTool类。
"""

import logging
import time
import asyncio
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Union, List
from concurrent.futures import ThreadPoolExecutor

from google.adk.tools import BaseTool, ToolContext
from google.genai import types

logger = logging.getLogger(__name__)


class BaseRenderTool(BaseTool, ABC):
    """
    所有渲染工具的基础类
    
    这个类提供了渲染工具的通用功能：
    - 统一的错误处理
    - 进度提示
    - 文件保存
    - 异步处理
    - 日志记录
    - 🔧 强制子类实现关键方法 (使用 @abstractmethod)
    
    子类必须实现：
    - _get_declaration(): 函数声明定义 (修复ADK工具注册问题)
    - _render_sync(): 同步渲染方法
    - _get_supported_formats(): 支持的输出格式 (可选，但建议重写)
    - _get_default_format(): 默认输出格式 (可选，但建议重写)
    - _check_dependencies(): 依赖检查 (可选，但建议实现)
    """
    
    def __init__(self, 
                 name: str,
                 description: str,
                 supported_formats: list = None,
                 default_format: str = "png"):
        """
        初始化基础渲染工具
        
        Args:
            name: 工具名称
            description: 工具描述
            supported_formats: 支持的输出格式列表
            default_format: 默认输出格式
        """
        super().__init__(
            name=name,
            description=description
        )
        self.supported_formats = supported_formats or self._get_supported_formats()
        self.default_format = default_format or self._get_default_format()
        self.executor = ThreadPoolExecutor(max_workers=2)  # 用于CPU密集型任务
        
        # 运行依赖检查
        self._check_dependencies()
    
    @abstractmethod
    def _get_declaration(self) -> Optional[types.FunctionDeclaration]:
        """
        🔧 函数声明定义 - 子类必须重写 (abstractmethod)
        
        这是最关键的方法！每个具体的渲染工具都必须重写此方法，
        提供符合自己特点的精确函数声明。
        
        为什么要强制子类重写：
        1. 每个工具的参数可能不同（如PlantUML可能需要图表类型参数）
        2. 每个工具的描述应该更具体（Mermaid vs Matplotlib vs D3.js）
        3. 让LLM能更准确地理解每个工具的具体用途
        4. 这是ADK工具能被LLM调用的唯一方式
        
        Returns:
            types.FunctionDeclaration - 工具的函数声明，不能为None
        """
        pass
    
    @abstractmethod
    def _render_sync(self, 
                    code: str, 
                    output_format: str, 
                    width: int, 
                    height: int) -> Dict[str, Any]:
        """
        同步渲染方法 - 子类必须实现 (abstractmethod)
        
        这是渲染的核心逻辑，每个工具都必须实现自己的渲染算法。
        
        Args:
            code: 图表代码
            output_format: 输出格式
            width: 宽度
            height: 高度
            
        Returns:
            包含success和data字段的字典
            success: bool - 是否成功
            data: bytes - 渲染后的图片数据（成功时）
            error: str - 错误信息（失败时）
        """
        pass
    
    def _get_supported_formats(self) -> List[str]:
        """
        获取支持的输出格式 - 建议子类重写
        
        虽然不是强制的，但强烈建议子类重写此方法，
        提供该工具实际支持的格式列表。
        
        Returns:
            支持的格式列表，默认只支持PNG
        """
        return ["png"]
    
    def _get_default_format(self) -> str:
        """
        获取默认输出格式 - 建议子类重写
        
        虽然不是强制的，但建议子类根据工具特性设置合适的默认格式。
        
        Returns:
            默认格式字符串，默认为PNG
        """
        return "png"
    
    def _check_dependencies(self) -> None:
        """
        检查工具依赖 - 建议子类实现
        
        虽然不是强制的，但强烈建议子类实现此方法，
        在工具初始化时检查必要的依赖是否已安装。
        
        实现示例：
        ```python
        def _check_dependencies(self):
            try:
                import matplotlib
                self._matplotlib_available = True
            except ImportError:
                logger.warning("matplotlib未安装")
                self._matplotlib_available = False
        ```
        """
        logger.info(f"{self.name} 使用默认依赖检查（建议子类重写此方法）")
        
    def _get_installation_guide(self, missing_deps: List[str]) -> str:
        """
        🔧 新增辅助方法：获取依赖安装指导
        
        Args:
            missing_deps: 缺失的依赖列表
            
        Returns:
            安装指导字符串
        """
        if not missing_deps:
            return ""
            
        guide = f"🔧 {self.name} 缺少依赖，请安装：\n\n"
        guide += "**Windows PowerShell:**\n"
        guide += f"```powershell\npip install {' '.join(missing_deps)}\n```\n\n"
        guide += "**Linux/macOS:**\n"
        guide += f"```bash\npip install {' '.join(missing_deps)}\n```\n\n"
        guide += "安装完成后，请重新运行工具。"
        
        return guide
    
    def _test_command(self, cmd: List[str]) -> bool:
        """
        🔧 新增辅助方法：测试命令是否可用
        
        Args:
            cmd: 要测试的命令列表
            
        Returns:
            命令是否可用
        """
        import subprocess
        import platform
        
        try:
            # Windows使用不同的空设备
            devnull = "NUL" if platform.system() == "Windows" else "/dev/null"
            
            result = subprocess.run(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=10,
                check=False
            )
            return result.returncode == 0 or result.returncode is None
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            return False
    
    def _get_platform_command(self, base_cmd: str) -> List[str]:
        """
        🔧 新增辅助方法：获取平台特定命令
        
        Args:
            base_cmd: 基础命令
            
        Returns:
            平台特定的命令列表
        """
        import platform
        
        if platform.system() == "Windows":
            # 在Windows上尝试多种方式
            candidates = [
                ["powershell", "-Command", base_cmd, "--version"],
                [base_cmd + ".cmd", "--version"],
                [base_cmd + ".exe", "--version"],
                [base_cmd, "--version"]
            ]
            
            for cmd in candidates:
                if self._test_command(cmd[:-1]):  # 测试时不带--version
                    return cmd[:-1]  # 返回时也不带--version
                    
            return [base_cmd]  # 回退到基础命令
        else:
            return [base_cmd]
    
    async def run_async(self, *, args: Dict[str, Any], tool_context: ToolContext) -> Dict[str, Any]:
        """
        运行渲染工具的主要方法
        
        Args:
            args: 工具参数
            tool_context: 工具上下文
            
        Returns:
            包含渲染结果的字典
        """
        # 提取参数
        code = args.get("code", "")
        output_format = args.get("output_format", self.default_format)
        title = args.get("title", "chart")
        width = args.get("width", 800)
        height = args.get("height", 600)
        
        if not code.strip():
            return {
                "success": False,
                "error": "图表代码不能为空",
                "message": "❌ 请提供要渲染的图表代码"
            }
        
        # 验证格式
        if output_format not in self.supported_formats:
            return {
                "success": False,
                "error": f"不支持的输出格式: {output_format}",
                "supported_formats": self.supported_formats,
                "message": f"❌ 支持的格式: {', '.join(self.supported_formats)}"
            }
        
        try:
            # 记录渲染进度
            logger.info(f"🎨 正在渲染{self.name}图表...")
            
            # 异步渲染
            render_result = await self._render_async(
                code=code,
                output_format=output_format,
                width=width,
                height=height
            )
            
            if not render_result["success"]:
                return self._handle_render_error(
                    render_result.get("error", "渲染失败"),
                    code
                )
            
            # 保存为Artifact
            logger.info("💾 正在保存图表文件...")
            
            artifact_result = await self._save_rendered_artifact(
                image_bytes=render_result["data"],
                filename=f"{title}_{int(time.time())}.{output_format}",
                mime_type=self._get_mime_type(output_format),
                tool_context=tool_context
            )
            
            if not artifact_result["success"]:
                return self._handle_render_error(
                    artifact_result.get("error", "保存失败"),
                    code
                )
            
            # 返回成功结果
            return {
                "success": True,
                "filename": artifact_result["filename"],
                "version": artifact_result["version"],
                "size": len(render_result["data"]),
                "format": output_format,
                "dimensions": f"{width}x{height}",
                "tool_name": self.name,
                "message": f"✅ {self.name}图表已生成！文件: {artifact_result['filename']}"
            }
            
        except Exception as e:
            logger.error(f"渲染工具 {self.name} 执行失败: {e}", exc_info=True)
            return self._handle_render_error(str(e), code)
    
    async def _render_async(self, 
                           code: str, 
                           output_format: str, 
                           width: int, 
                           height: int) -> Dict[str, Any]:
        """
        异步渲染方法，将CPU密集型任务转移到线程池
        
        🔧 增强功能：
        - 添加超时处理（2分钟）
        - 改进错误恢复机制
        - 增强进度反馈
        
        Args:
            code: 图表代码
            output_format: 输出格式
            width: 宽度
            height: 高度
            
        Returns:
            渲染结果字典
        """
        loop = asyncio.get_event_loop()
        
        try:
            logger.info(f"🎨 开始渲染 {self.name} 图表，预计耗时10-30秒...")
            
            # 🔧 增加超时处理 - 2分钟超时
            result = await asyncio.wait_for(
                loop.run_in_executor(
                self.executor,
                self._render_sync,
                code,
                output_format,
                width,
                height
                ),
                timeout=120.0  # 2分钟超时
            )
            
            if result.get("success"):
                logger.info(f"✅ {self.name} 渲染完成！")
            else:
                logger.warning(f"⚠️ {self.name} 渲染失败: {result.get('error', '未知错误')}")
            
            return result
            
        except asyncio.TimeoutError:
            error_msg = f"渲染超时（超过2分钟），可能原因：代码过于复杂、依赖未正确安装、或系统资源不足"
            logger.error(f"⏰ {self.name} {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "suggestion": "请尝试简化代码或检查依赖安装"
            }
        except Exception as e:
            error_msg = f"异步渲染失败: {e}"
            logger.error(f"❌ {self.name} {error_msg}", exc_info=True)
            return {
                "success": False,
                "error": error_msg,
                "suggestion": "请检查代码语法和依赖环境"
            }
    
    async def _save_rendered_artifact(self, 
                                    image_bytes: bytes,
                                    filename: str,
                                    mime_type: str,
                                    tool_context: ToolContext) -> Dict[str, Any]:
        """
        保存渲染后的图片为Artifact或本地文件
        
        Args:
            image_bytes: 图片字节数据
            filename: 文件名
            mime_type: MIME类型
            tool_context: 工具上下文（可为None）
            
        Returns:
            保存结果字典
        """
        try:
            # 如果有tool_context，使用Artifact保存
            if tool_context is not None:
                # 创建types.Part对象
                image_part = types.Part.from_bytes(
                    data=image_bytes,
                    mime_type=mime_type
                )
                
                # 保存为Artifact
                version = await tool_context.save_artifact(filename, image_part)
                
                return {
                    "success": True,
                    "filename": filename,
                    "version": version,
                    "mime_type": mime_type
                }
            else:
                # 保存到本地文件
                import os
                from pathlib import Path
                
                # 确保文件名是安全的
                safe_filename = filename.replace(' ', '_').replace(':', '-')
                file_path = Path(safe_filename)
                
                # 写入文件
                with open(file_path, 'wb') as f:
                    f.write(image_bytes)
                
                logger.info(f"✅ 文件已保存到本地: {file_path.absolute()}")
                
                return {
                    "success": True,
                    "filename": str(file_path),
                    "version": "local",
                    "file_path": str(file_path.absolute()),
                    "mime_type": mime_type
                }
            
        except Exception as e:
            logger.error(f"保存文件失败: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"保存文件失败: {e}"
            }
    
    
    def _handle_render_error(self, error: Exception, fallback_code: str) -> Dict[str, Any]:
        """
        统一的错误处理
        
        Args:
            error: 错误信息
            fallback_code: 回退代码
            
        Returns:
            错误结果字典
        """
        error_message = str(error)
        logger.error(f"{self.name} 渲染失败: {error_message}")
        
        return {
            "success": False,
            "error": error_message,
            "fallback_code": fallback_code,
            "tool_name": self.name,
            "message": f"❌ {self.name}图表渲染失败: {error_message}\n\n已返回原始代码，您可以手动渲染。"
        }
    
    def _get_mime_type(self, format: str) -> str:
        """
        根据格式获取MIME类型
        
        Args:
            format: 文件格式
            
        Returns:
            MIME类型字符串
        """
        mime_types = {
            'png': 'image/png',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'svg': 'image/svg+xml',
            'pdf': 'application/pdf',
            'gif': 'image/gif',
            'webp': 'image/webp',
            'html': 'text/html',
            'json': 'application/json'
        }
        return mime_types.get(format.lower(), 'application/octet-stream')
    
    def __del__(self):
        """析构函数，清理线程池"""
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=False) 