# Copyright 2025 Google LLC
# Three.js渲染工具 - CDN-Only
import logging
import re
from typing import Dict, Any, Optional

from google.genai import types
from .base_render_tool import BaseRenderTool

logger = logging.getLogger(__name__)

class ThreeJSRenderTool(BaseRenderTool):
    """🎲 Three.js 3D可视化渲染工具 (纯CDN方案)"""

    def __init__(self):
        super().__init__(
            name="render_threejs",
            description="🎲 使用CDN加载最新版Three.js库，创建交互式3D场景。代码将在一个预设环境中执行，该环境已包含 scene, camera, renderer, 和 OrbitControls。",
            supported_formats=["html"],
            default_format="html"
        )
        self._check_dependencies()

    def _check_dependencies(self):
        """🔧 依赖检查：此工具现在使用纯CDN方案，无本地依赖。"""
        logger.info("✅ ThreeJSRenderTool 使用纯CDN方案，无需检查本地依赖。")

    def _get_declaration(self) -> Optional[types.FunctionDeclaration]:
        """🔧 定义Three.js渲染工具的精确函数声明"""
        return types.FunctionDeclaration(
            name=self.name,
            description="🎲 使用CDN加载最新版Three.js库，创建交互式3D场景。\n代码将在一个预设环境中执行，该环境已包含 `scene`, `camera`, `renderer`, `OrbitControls` 和默认的 `ambientLight` 与 `directionalLight`。\n你的代码应该只关注创建和添加几何体到场景中。",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    'code': types.Schema(
                        type=types.Type.STRING,
                        description='纯Three.js JavaScript代码。重要: **不要**创建`scene`, `camera`, `renderer`或任何与模板中默认光源同名的光源 (`ambientLight`, `directionalLight`)，这些都由环境提供。如果需要动画，定义一个名为`animate`的函数。'
                    ),
                    'title': types.Schema(
                        type=types.Type.STRING,
                        description='HTML页面的标题',
                        default='Three.js 3D Scene'
                    )
                },
                required=['code'],
            )
        )

    def _render_sync(self, code: str, output_format: str = "html", width: int = 800, height: int = 600, title: str = "Three.js 3D Scene") -> Dict[str, Any]:
        """同步渲染Three.js 3D场景 - 纯CDN方案"""
        logger.info(f"🚀 开始渲染Three.js 3D场景 (窗口自适应)")
        result = self._render_with_cdn(code, title)
        
        if result["success"]:
            logger.info("✅ CDN渲染成功")
            return result
        else:
            logger.error(f"❌ CDN渲染失败: {result['error']}")
            return result

    def _render_with_cdn(self, code: str, title: str) -> Dict[str, Any]:
        """CDN渲染方案"""
        try:
            processed_code = self._preprocess_user_code(code)
            html_content = self._create_clean_html_template(processed_code, title)
            viz_bytes = html_content.encode('utf-8')
            return {
                "success": True,
                "data": viz_bytes,
                "method": "cdn"
            }
        except Exception as e:
            logger.exception("CDN渲染过程中发生未知错误")
            return {"success": False, "error": f"CDN渲染过程发生错误: {str(e)}"}

    def _preprocess_user_code(self, js_code: str) -> str:
        """🔧 预处理用户代码，移除与模板冲突的冗余代码。"""
        processed = js_code
        
        # 定义需要移除的冗余代码模式
        patterns_to_remove = [
            # 移除场景、相机、渲染器的创建和配置
            re.compile(r'^\s*(?:const|let|var)\s+\w+\s*=\s*new\s+THREE\.(?:Scene|PerspectiveCamera|WebGLRenderer)\(.*\);?.*$', re.MULTILINE),
            re.compile(r'^\s*\w+\.setSize\(.*\);?.*$', re.MULTILINE),
            re.compile(r'^\s*document\.\w+\.appendChild\(.*\);?.*$', re.MULTILINE),

            # 移除OrbitControls的创建
            re.compile(r'^\s*(?:const|let|var)\s+controls\s*=\s*new\s+OrbitControls\(.*\);?.*$', re.MULTILINE),

            # 移除渲染循环的启动调用
            re.compile(r'^\s*requestAnimationFrame\(.*\);?.*$', re.MULTILINE),
            re.compile(r'^\s*animate\(\);?.*$', re.MULTILINE),

            # **核心修复**：移除与模板中默认光源冲突的声明和使用
            # 1. 移除 ambientLight 的声明和添加
            re.compile(r'^\s*(?:const|let|var)\s+ambientLight\s*=\s*new\s+THREE\.AmbientLight\(.*\);?.*$', re.MULTILINE),
            re.compile(r'^\s*scene\.add\(\s*ambientLight\s*\);?.*$', re.MULTILINE),
            
            # 2. 移除 directionalLight 的声明、配置和添加
            re.compile(r'^\s*(?:const|let|var)\s+directionalLight\s*=\s*new\s+THREE\.DirectionalLight\(.*\);?.*$', re.MULTILINE),
            re.compile(r'^\s*directionalLight\.(?:position|castShadow|shadow)\s*.*?(?:;)?.*$', re.MULTILINE),
            re.compile(r'^\s*scene\.add\(\s*directionalLight\s*\);?.*$', re.MULTILINE),
        ]
        
        for pattern in patterns_to_remove:
            processed = pattern.sub('', processed)
            
        return processed.strip()

    def _create_clean_html_template(self, processed_code: str, title: str) -> str:
        """创建一个简洁、现代、功能强大的Three.js HTML模板"""
        return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{ margin: 0; overflow: hidden; }}
        canvas {{ display: block; }}
    </style>
</head>
<body>
    <script type="importmap">
    {{
        "imports": {{
            "three": "https://unpkg.com/three@0.165.0/build/three.module.js",
            "three/addons/": "https://unpkg.com/three@0.165.0/examples/jsm/"
        }}
    }}
    </script>
    <script type="module">
        import * as THREE from 'three';
        import {{ OrbitControls }} from 'three/addons/controls/OrbitControls.js';

        let scene, camera, renderer, controls;
        
        // --- 初始化场景 ---
        function init() {{
            // 场景
            scene = new THREE.Scene();
            scene.background = new THREE.Color(0xffffff);

            // 相机
            camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
            camera.position.set(5, 5, 10);

            // 渲染器
            renderer = new THREE.WebGLRenderer({{ antialias: true }});
            renderer.setSize(window.innerWidth, window.innerHeight);
            renderer.shadowMap.enabled = true;
            document.body.appendChild(renderer.domElement);

            // 控制器
            controls = new OrbitControls(camera, renderer.domElement);
            controls.enableDamping = true;
            controls.target.set(0, 0, 0);

            // 光源
            const ambientLight = new THREE.AmbientLight(0x666666, 2);
            scene.add(ambientLight);
            const directionalLight = new THREE.DirectionalLight(0xffffff, 1.5);
            directionalLight.position.set(5, 10, 7.5).normalize();
            directionalLight.castShadow = true;
            scene.add(directionalLight);
            
            // --- 用户代码注入 ---
            // 用户代码中可以直接使用 scene, camera, renderer, THREE
            // 并可以定义一个 'animate' 函数
            {processed_code}
            
            // --- 监听与启动 ---
            window.addEventListener('resize', onWindowResize);
            coreAnimate();
        }}

        // --- 核心循环 ---
        function coreAnimate() {{
            requestAnimationFrame(coreAnimate);
            
            // 如果用户定义了 animate, 执行它
            if (typeof animate === 'function') {{
                animate();
            }}

            controls.update();
            renderer.render(scene, camera);
        }}

        // --- 窗口适配 ---
        function onWindowResize() {{
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        }}

        init();
    </script>
</body>
</html>'''

    def get_dependencies_status(self) -> Dict[str, Any]:
        """获取依赖状态"""
        return {{
            "rendering_strategy": {{
                "primary": "纯CDN渲染",
                "fallback": "无",
                "description": "该工具使用现代Web标准，通过CDN直接加载Three.js库，无需本地Node.js环境。"
            }}
        }} 