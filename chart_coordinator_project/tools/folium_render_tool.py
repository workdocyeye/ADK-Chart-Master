# Copyright 2025 Google LLC
# Folium渲染工具 - 地图可视化专家

import logging
import tempfile
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any, Optional

from google.genai import types
from .base_render_tool import BaseRenderTool

logger = logging.getLogger(__name__)


class FoliumRenderTool(BaseRenderTool):
    """🗺️ Python Folium地图可视化渲染工具"""
    
    def __init__(self):
        super().__init__(
            name="render_folium",
            description="🗺️ Python Folium地图可视化渲染工具：将Python Folium地图代码转换为HTML交互式地图或PNG静态图片。适合地理数据可视化、位置分析、空间统计。",
            supported_formats=["html", "png"],
            default_format="html"
        )
        self._check_dependencies()
    
    def _get_declaration(self) -> Optional[types.FunctionDeclaration]:
        """🔧 定义Folium渲染工具的精确函数声明"""
        return types.FunctionDeclaration(
            name=self.name,
            description=self.description,
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    'code': types.Schema(
                        type=types.Type.STRING,
                        description='要渲染的Python Folium地图代码。应该包含完整的地图创建逻辑，包括import语句、地图初始化、标记添加、图层配置等'
                    ),
                    'output_format': types.Schema(
                        type=types.Type.STRING,
                        description='输出格式。html生成交互式地图，png生成静态图片（需要selenium）',
                        enum=['html', 'png'],
                        default='html'
                    ),
                    'title': types.Schema(
                        type=types.Type.STRING,
                        description='地图文件名称（不含扩展名）',
                        default='folium_map'
                    ),
                    'width': types.Schema(
                        type=types.Type.INTEGER,
                        description='地图宽度（像素），仅PNG格式有效',
                        default=1024
                    ),
                    'height': types.Schema(
                        type=types.Type.INTEGER,
                        description='地图高度（像素），仅PNG格式有效',
                        default=768
                    ),
                    'center_lat': types.Schema(
                        type=types.Type.NUMBER,
                        description='地图中心纬度，如果代码中已指定则忽略',
                        default=39.9042
                    ),
                    'center_lon': types.Schema(
                        type=types.Type.NUMBER,
                        description='地图中心经度，如果代码中已指定则忽略',
                        default=116.4074
                    ),
                    'zoom_start': types.Schema(
                        type=types.Type.INTEGER,
                        description='初始缩放级别（1-18），如果代码中已指定则忽略',
                        default=10
                    )
                },
                required=['code'],
            )
        )
    
    def _check_dependencies(self):
        """🔧 Folium依赖检查"""
        self._folium_available = False
        missing_deps = []
        available_deps = []
        
        # 检查核心依赖
        core_deps = {
            'folium': '地图可视化库',
            'pandas': '数据分析库（可选）',
            'geopandas': '地理数据库（可选）'
        }
        
        for dep_name, desc in core_deps.items():
            try:
                module = __import__(dep_name)
                version = getattr(module, '__version__', '未知版本')
                logger.info(f"✅ {dep_name} ({desc}): {version}")
                available_deps.append(f"{dep_name}=={version}")
            except ImportError:
                logger.warning(f"❌ {dep_name} ({desc}): 未安装")
                if dep_name == 'folium':  # 只有folium是必需的
                    missing_deps.append(dep_name)
        
        # 检查PNG输出依赖（可选）
        try:
            import selenium
            import chromedriver_autoinstaller
            logger.info(f"✅ selenium (PNG输出支持): {selenium.__version__}")
            self._png_support = True
        except ImportError:
            logger.info("ℹ️ selenium未安装，仅支持HTML输出")
            self._png_support = False
        
        if missing_deps:
            logger.warning(f"🔧 缺少必需依赖: {', '.join(missing_deps)}")
            logger.info(self._get_installation_guide(missing_deps))
            self._folium_available = False
        else:
            logger.info("✅ Folium渲染工具核心依赖检查通过")
            self._folium_available = True
            self._test_folium_import()
    
    def _test_folium_import(self):
        """🔧 测试Folium导入"""
        try:
            import folium
            
            # 创建一个简单的测试地图
            test_map = folium.Map(location=[39.9042, 116.4074], zoom_start=10)
            html_str = test_map._repr_html_()
            
            if html_str and len(html_str) > 100:
                logger.info("✅ Folium导入测试成功")
            else:
                logger.warning("⚠️ Folium导入测试失败 - 生成空内容")
                
        except Exception as e:
            logger.error(f"❌ Folium导入测试失败: {e}")
            self._folium_available = False
    
    def _render_sync(self, code: str, output_format: str, width: int, height: int) -> Dict[str, Any]:
        """同步渲染Folium地图"""
        
        if not self._folium_available:
            missing_deps = ["folium"]
            return {
                "success": False,
                "error": "Folium依赖不可用",
                "installation_guide": self._get_installation_guide(missing_deps),
                "suggestion": "请先安装依赖: pip install folium pandas geopandas"
            }
        
        if output_format == "png" and not self._png_support:
            return {
                "success": False,
                "error": "PNG输出需要selenium和chromedriver",
                "installation_guide": self._get_installation_guide(["selenium", "chromedriver-autoinstaller"]),
                "suggestion": "请安装: pip install selenium chromedriver-autoinstaller 或使用HTML格式"
            }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            try:
                code_file = temp_path / "map_code.py"
                output_file = temp_path / f"output.{output_format}"
                
                # 预处理代码
                processed_code = self._preprocess_code(code, output_file, output_format, width, height)
                code_file.write_text(processed_code, encoding='utf-8')
                
                logger.info(f"🚀 执行Folium地图渲染...")
                
                # 执行Python代码
                result = subprocess.run(
                    [sys.executable, str(code_file)],
                    capture_output=True,
                    text=True,
                    timeout=120,  # 地图渲染可能需要更长时间
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
                        "error": "代码执行完成但未生成地图文件"
                    }
                
                if output_format == "html":
                    map_content = output_file.read_text(encoding='utf-8')
                    map_bytes = map_content.encode('utf-8')
                else:
                    map_bytes = output_file.read_bytes()
                
                if len(map_bytes) == 0:
                    return {
                        "success": False,
                        "error": "生成的地图文件为空"
                    }
                
                logger.info(f"✅ Folium地图渲染成功，大小: {len(map_bytes)} bytes")
                
                return {
                    "success": True,
                    "data": map_bytes
                }
                
            except subprocess.TimeoutExpired:
                return {
                    "success": False,
                    "error": "地图渲染超时（120秒）",
                    "suggestion": "请简化地图复杂度或优化数据量"
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": f"渲染过程发生错误: {str(e)}"
                }
    
    def _preprocess_code(self, code: str, output_file: Path, output_format: str, width: int, height: int) -> str:
        """预处理Folium代码"""
        
        # 确保有folium导入
        if 'import folium' not in code and 'from folium' not in code:
            imports = "import folium\nimport pandas as pd\n"
        else:
            imports = ""
        
        # 创建输出逻辑
        if output_format == "html":
            save_logic = f"""
# 保存地图为HTML
if 'map' in locals() or 'map' in globals():
    target_map = map if 'map' in locals() else globals()['map']
elif 'm' in locals() or 'm' in globals():
    target_map = m if 'm' in locals() else globals()['m']
else:
    # 尝试找到Folium地图对象
    import folium
    target_map = None
    for var_name, var_value in list(locals().items()):
        if isinstance(var_value, folium.Map):
            target_map = var_value
            break
    if target_map is None:
        for var_name, var_value in globals().items():
            if isinstance(var_value, folium.Map):
                target_map = var_value
                break
    
    if target_map is None:
        raise ValueError("未找到Folium Map对象，请确保代码中创建了地图变量（建议命名为'map'或'm'）")

target_map.save(r"{output_file}")
"""
        else:  # PNG format
            save_logic = f"""
# 保存地图为PNG (需要selenium)
if 'map' in locals() or 'map' in globals():
    target_map = map if 'map' in locals() else globals()['map']
elif 'm' in locals() or 'm' in globals():
    target_map = m if 'm' in locals() else globals()['m']
else:
    import folium
    target_map = None
    for var_name, var_value in list(locals().items()):
        if isinstance(var_value, folium.Map):
            target_map = var_value
            break
    if target_map is None:
        for var_name, var_value in globals().items():
            if isinstance(var_value, folium.Map):
                target_map = var_value
                break
    
    if target_map is None:
        raise ValueError("未找到Folium Map对象")

# 临时保存为HTML，然后转换为PNG
import tempfile
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import chromedriver_autoinstaller

# 自动安装chromedriver
chromedriver_autoinstaller.install()

# 保存为临时HTML
temp_html = os.path.join(os.path.dirname(r"{output_file}"), "temp_map.html")
target_map.save(temp_html)

# 配置Chrome选项
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument(f"--window-size={width},{height}")

# 截图保存为PNG
driver = webdriver.Chrome(options=chrome_options)
try:
    driver.get(f"file://{temp_html}")
    driver.set_window_size(width, height)
    import time
    time.sleep(3)  # 等待地图加载
    driver.save_screenshot(r"{output_file}")
finally:
    driver.quit()
    os.remove(temp_html)
"""
        
        processed_code = f"""
{imports}

# 用户代码
{self._indent_code(code)}

# 自动保存逻辑
{save_logic}
"""
        return processed_code
    
    def _indent_code(self, code: str) -> str:
        """为代码添加缩进"""
        lines = code.strip().split('\n')
        indented_lines = [line for line in lines if line.strip()]
        return '\n'.join(indented_lines)

    def _get_installation_guide(self, missing_deps):
        """获取安装指导"""
        if not missing_deps:
            return ""
            
        base_guide = super()._get_installation_guide(missing_deps)
        
        # 添加Folium特定说明
        if 'folium' in missing_deps:
            base_guide += "\n\n**🗺️ Folium地图可视化完整安装:**\n"
            base_guide += "```bash\n"
            base_guide += "# 基础地图功能\n"
            base_guide += "pip install folium pandas\n\n"
            base_guide += "# 地理数据支持（可选）\n"
            base_guide += "pip install geopandas\n\n"
            base_guide += "# PNG输出支持（可选）\n"
            base_guide += "pip install selenium chromedriver-autoinstaller\n"
            base_guide += "```\n"
        
        return base_guide 