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
PlantUML渲染工具

这个模块实现了PlantUML图表的渲染功能，支持：
- UML类图、时序图、活动图等多种UML图表
- 在线PlantUML服务器渲染
- 本地Java渲染（如果plantuml.jar可用）
- 多种输出格式（PNG、SVG、PDF）
- 自动UML语法验证
"""

import logging
import base64
import zlib
import string
import requests
import subprocess
import os
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional

from google.genai import types
from .base_render_tool import BaseRenderTool

logger = logging.getLogger(__name__)


class PlantUMLRenderTool(BaseRenderTool):
    """
    PlantUML图表渲染工具
    
    支持渲染各种UML图表：
    - 类图 (Class Diagram)
    - 时序图 (Sequence Diagram) 
    - 活动图 (Activity Diagram)
    - 用例图 (Use Case Diagram)
    - 状态图 (State Diagram)
    - 组件图 (Component Diagram)
    - 部署图 (Deployment Diagram)
    - 对象图 (Object Diagram)
    - 包图 (Package Diagram)
    """
    
    # PlantUML在线服务器列表
    PLANTUML_SERVERS = [
        "http://www.plantuml.com/plantuml",
        "https://plantuml-server.kkeisuke.dev",
        "http://plantuml.com:8080/plantuml"
    ]
    
    # PlantUML JAR 下载信息
    PLANTUML_JAR_URL = "https://github.com/plantuml/plantuml/releases/latest/download/plantuml.jar"
    
    def __init__(self):
        super().__init__(
            name="plantuml_render",
            description="PlantUML UML图表渲染工具，支持类图、时序图、活动图等各种UML图表",
            supported_formats=["png", "svg", "pdf", "txt"],
            default_format="png"
        )
        # 将依赖检查改为异步执行，避免阻塞初始化
        # asyncio.run(self._check_and_download_dependencies())
        self._java_available = None
        self._local_jar_path = None
        self._online_service_available = True  # 乐观假设
    
    async def _check_and_download_dependencies(self):
        """异步检查并下载PlantUML依赖"""
        if self._java_available is not None and self._local_jar_path is not None:
            return

        # 1. 检查Java环境
        self._java_available = self._check_java()

        # 2. 检查并获取JAR文件
        jar_path = self._find_plantuml_jar()
        if not jar_path:
            logger.info("本地未找到plantuml.jar，尝试自动下载...")
            jar_path = await self._download_plantuml_jar()

        if jar_path:
            logger.info(f"✅ PlantUML JAR文件可用: {jar_path}")
            self._local_jar_path = jar_path
        else:
            logger.warning("❌ 无法获取PlantUML JAR文件。本地渲染将不可用。")
            self._local_jar_path = None

        if not self._local_jar_path or not self._java_available:
            logger.warning("本地渲染条件不满足，将仅依赖在线服务。")

    def _check_java(self) -> bool:
        """检查Java环境是否可用"""
        try:
            result = subprocess.run(
                ["java", "-version"],
                capture_output=True,
                text=True,
                timeout=10,
                encoding='utf-8',
                errors='replace'
            )
            if result.returncode == 0 or result.returncode == 1:  # Some JREs output to stderr
                logger.info("✅ Java环境可用")
                return True
            else:
                logger.warning(f"❌ Java环境检查返回码: {result.returncode}")
                return False
        except (FileNotFoundError, subprocess.TimeoutExpired, OSError) as e:
            logger.warning(f"❌ Java环境检查失败: {e}")
            return False

    def _check_dependencies(self):
        """
        这个方法现在被异步版本_check_and_download_dependencies替代，
        保留为空以兼容基类，但实际逻辑已转移。
        """
        pass

    async def _download_plantuml_jar(self) -> Optional[str]:
        """从官方源下载plantuml.jar文件"""
        target_dir = Path(__file__).parent.parent # chart_coordinator_project/
        target_path = target_dir / "plantuml.jar"
        
        try:
            print("正在下载 plantuml.jar，请稍候...")
            with requests.get(self.PLANTUML_JAR_URL, stream=True) as r:
                r.raise_for_status()
                total_size = int(r.headers.get('content-length', 0))
                chunk_size = 8192
                downloaded_size = 0
                
                with open(target_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=chunk_size):
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        
                        # 简单的文本进度条
                        progress = int(50 * downloaded_size / total_size)
                        print(f"[{'=' * progress}{' ' * (50 - progress)}] {downloaded_size / (1024*1024):.2f}MB / {total_size / (1024*1024):.2f}MB", end='\r')

            print("\n✅ plantuml.jar 下载完成！")
            return str(target_path)
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ 下载plantuml.jar失败: {e}")
            if target_path.exists():
                target_path.unlink() # 删除不完整的文件
            return None
        except Exception as e:
            logger.error(f"❌ 保存plantuml.jar时发生未知错误: {e}")
            if target_path.exists():
                target_path.unlink()
            return None
    
    def _get_declaration(self) -> Optional[types.FunctionDeclaration]:
        """
        🔧 PlantUML工具的函数声明
        
        包含PlantUML特有的参数和详细的图表类型说明
        """
        return types.FunctionDeclaration(
            name=self.name,
            description="PlantUML UML图表渲染工具。支持渲染各种UML图表，包括类图、时序图、活动图、用例图、状态图、组件图等。",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    'code': types.Schema(
                        type=types.Type.STRING,
                        description='''PlantUML代码，支持以下图表类型：
- 类图：@startuml ... @enduml，使用class、interface、enum等关键字
- 时序图：participant、actor、->、-->等语法
- 活动图：start、stop、:activity;、if、else、endif等语法
- 用例图：actor、usecase、()等语法
- 状态图：state、[*]、-->等语法
- 组件图：component、interface、package等语法
- 部署图：node、artifact、cloud等语法

代码应该以@startuml开头，@enduml结尾'''
                    ),
                    'output_format': types.Schema(
                        type=types.Type.STRING,
                        description='输出格式：png(默认)、svg、pdf、txt(ASCII art)',
                        enum=['png', 'svg', 'pdf', 'txt'],
                        default='png'
                    ),
                    'title': types.Schema(
                        type=types.Type.STRING,
                        description='图表文件名称',
                        default='plantuml_diagram'
                    ),
                    'diagram_type': types.Schema(
                        type=types.Type.STRING,
                        description='UML图表类型提示（用于优化渲染）',
                        enum=['class', 'sequence', 'activity', 'usecase', 'state', 'component', 'deployment', 'object', 'package', 'other'],
                        default='class'
                    ),
                    'theme': types.Schema(
                        type=types.Type.STRING,
                        description='PlantUML主题',
                        enum=['default', 'plain', 'amiga', 'aws-orange', 'bluegray', 'blueprint', 'carbon', 'cerulean', 'cerulean-outline', 'crt-amber', 'crt-green', 'cyborg', 'cyborg-outline', 'hacker', 'lightgray', 'mars', 'materia', 'materia-outline', 'mimeograph', 'minty', 'reddress-darkblue', 'reddress-darkgreen', 'reddress-darkorange', 'reddress-darkred', 'reddress-lightblue', 'reddress-lightgreen', 'reddress-lightorange', 'reddress-lightred', 'sandstone', 'silver', 'sketchy', 'sketchy-outline', 'spacelab', 'spacelab-white', 'superhero', 'superhero-outline', 'toy', 'united', 'vibrant'],
                        default='default'
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
        同步渲染PlantUML图表
        
        渲染策略：
        1. 优先使用本地plantuml.jar（如果可用）
        2. 回退到在线PlantUML服务器
        3. 自动处理@startuml/@enduml标签
        4. 支持主题和样式设置
        """
        # 在实际渲染前，执行一次异步依赖检查
        import asyncio
        try:
            # 获取或创建事件循环
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            loop.run_until_complete(self._check_and_download_dependencies())
        except RuntimeError: # No event loop
             loop = asyncio.new_event_loop()
             asyncio.set_event_loop(loop)
             loop.run_until_complete(self._check_and_download_dependencies())

        try:
            # 预处理代码
            processed_code = self._preprocess_plantuml_code(code)
            
            # 验证PlantUML语法
            validation_result = self._validate_plantuml_syntax(processed_code)
            if not validation_result["valid"]:
                return {
                    "success": False,
                    "error": f"PlantUML语法错误: {validation_result['error']}"
                }
            
            # 尝试本地渲染
            if self._local_jar_path and self._java_available:
                logger.info("使用本地PlantUML jar渲染")
                result = self._render_with_local_jar(processed_code, output_format, self._local_jar_path)
                if result["success"]:
                    return result
                logger.warning(f"本地渲染失败，回退到在线服务: {result.get('error')}")
            
            # 在线渲染
            if self._online_service_available:
                logger.info("使用在线PlantUML服务渲染")
                return self._render_with_online_service(processed_code, output_format)
            
            return {
                "success": False,
                "error": "PlantUML不可用。请安装Java和PlantUML JAR文件，或确保网络连接正常"
            }
            
        except Exception as e:
            logger.error(f"PlantUML渲染失败: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"PlantUML渲染异常: {e}"
            }
    
    def _preprocess_plantuml_code(self, code: str) -> str:
        """
        预处理PlantUML代码
        
        - 自动添加@startuml/@enduml标签
        - 自动插入多字体skinparam，确保所有区域中文显示
        - 清理多余的空白
        - 标准化换行符
        """
        code = code.strip()
        
        # 如果没有@startuml开头，自动添加
        if not code.startswith('@startuml'):
            code = '@startuml\n' + code
        
        # 如果没有@enduml结尾，自动添加
        if not code.endswith('@enduml'):
            code = code + '\n@enduml'
        
        # 标准化换行符
        code = code.replace('\r\n', '\n').replace('\r', '\n')

        # 极简中文字体配置 - 使用兼容性最好的字体设置
        lines = code.split('\n')
        # 只在@startuml后面插入，且避免重复插入
        if len(lines) > 1 and not any('skinparam defaultFontName' in l for l in lines[:8]):
            lines.insert(1, 'skinparam defaultFontName "Microsoft YaHei,SimHei,Arial Unicode MS"')
        code = '\n'.join(lines)
        
        return code
    
    def _validate_plantuml_syntax(self, code: str) -> Dict[str, Any]:
        """
        验证PlantUML语法是否基本正确
        
        - 检查@startuml和@enduml是否配对
        - 简单的关键字检查
        """
        if not code.startswith('@startuml'):
            return {"valid": False, "error": "代码必须以@startuml开头"}
        if not code.endswith('@enduml'):
            return {"valid": False, "error": "代码必须以@enduml结尾"}
        
        # 可以在这里添加更多语法检查规则
        
        return {"valid": True}
    
    def _find_plantuml_jar(self) -> Optional[str]:
        """
        在项目目录中查找plantuml.jar
        """
        # 检查的路径列表
        check_paths = [
            Path(__file__).parent.parent / 'plantuml.jar', # chart_coordinator_project/plantuml.jar
            Path('.') / 'plantuml.jar', # 当前工作目录
        ]
        
        for path in check_paths:
            if path.exists() and path.is_file():
                logger.info(f"找到plantuml.jar: {path.resolve()}")
                return str(path.resolve())
        
        return None
    
    def _render_with_local_jar(self, 
                              code: str, 
                              output_format: str, 
                              jar_path: str) -> Dict[str, Any]:
        """
        使用本地的plantuml.jar文件进行渲染
        """
        if not jar_path:
            return {"success": False, "error": "JAR文件路径未提供"}

        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                input_file = temp_path / "input.puml"
                input_file.write_text(code, encoding='utf-8')
                
                # 构建命令 - 添加UTF-8字符编码支持解决中文乱码
                cmd = [
                    'java', '-jar', jar_path,
                    '-charset', 'UTF-8',
                    f'-t{output_format}',
                    str(input_file)
                ]

                logger.info(f"执行本地渲染命令: {' '.join(cmd)}")
                result = subprocess.run(
                    cmd, 
                    capture_output=True, 
                    text=True, 
                    timeout=60,
                    encoding='utf-8',
                    errors='replace'
                )
                
                if result.returncode != 0:
                    return {
                        "success": False,
                        "error": f"PlantUML本地渲染失败:\n{result.stderr}"
                    }
                
                # 根据格式确定输出文件路径
                if output_format == 'txt':
                    output_filename = "input.atxt"
                else:
                    output_filename = f"input.{output_format}"
                output_file = temp_path / output_filename

                if not output_file.exists():
                    return {
                        "success": False,
                        "error": "本地渲染执行完成但未生成输出文件"
                    }

                file_bytes = output_file.read_bytes()

                if not file_bytes:
                    return {
                        "success": False,
                        "error": "生成的输出文件为空"
                    }
                
                logger.info(f"✅ PlantUML本地渲染成功，大小: {len(file_bytes)} bytes")
                
                return {
                    "success": True,
                    "data": file_bytes
                }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "本地渲染超时（60秒）"
            }
        except Exception as e:
            logger.error(f"本地渲染异常: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"本地渲染异常: {e}"
            }
    
    def _render_with_online_service(self, 
                                  code: str, 
                                  output_format: str) -> Dict[str, Any]:
        """
        使用在线PlantUML服务渲染
        """
        for server in PlantUMLRenderTool.PLANTUML_SERVERS:
            try:
                # 编码PlantUML代码
                encoded_code = self._encode_plantuml_url(code)
                
                # 构建URL
                format_map = {
                    'png': 'png',
                    'svg': 'svg', 
                    'pdf': 'pdf',
                    'txt': 'txt'
                }
                
                url = f"{server}/{format_map[output_format]}/{encoded_code}"
                
                # 发送请求
                response = requests.get(url, timeout=30)
                
                if response.status_code == 200:
                    return {
                        "success": True,
                        "data": response.content
                    }
                else:
                    logger.warning(f"服务器 {server} 返回状态码: {response.status_code}")
                    continue
                    
            except requests.RequestException as e:
                logger.warning(f"请求服务器 {server} 失败: {e}")
                continue
            except Exception as e:
                logger.warning(f"使用服务器 {server} 时出错: {e}")
                continue
        
        return {
            "success": False,
            "error": "所有PlantUML在线服务都不可用"
        }
    
    def _encode_plantuml_url(self, plantuml_text: str) -> str:
        """
        将PlantUML代码编码为URL安全的字符串
        
        使用简化但可靠的编码方法
        """
        try:
            # UTF-8编码
            utf8_bytes = plantuml_text.encode('utf-8')
            
            # 使用zlib压缩（去掉zlib头尾，保留deflate数据）
            import zlib
            compressed = zlib.compress(utf8_bytes, 9)
            # 去掉zlib头（2字节）和校验和尾（4字节）
            deflate_data = compressed[2:-4]
            
            # 使用标准base64编码
            import base64
            base64_encoded = base64.b64encode(deflate_data).decode('ascii')
            
            # PlantUML的字符替换
            # 标准base64: ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/
            # PlantUML:   0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_
            
            translate_table = str.maketrans(
                'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/',
                '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_'
            )
            
            result = base64_encoded.translate(translate_table).rstrip('=')
            return result
            
        except Exception as e:
            logger.error(f"PlantUML URL编码失败: {e}")
            # 回退到简单的URL安全编码
            try:
                import urllib.parse
                return urllib.parse.quote(plantuml_text, safe='')
            except:
                return plantuml_text  # 最后的回退 