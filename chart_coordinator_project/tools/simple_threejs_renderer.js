#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

console.log('🎲 简化版Three.js本地渲染器 (浏览器兼容版)');

// 检查参数
if (process.argv.length < 4) {
    console.error('用法: node simple_threejs_renderer.js <用户代码文件> <输出HTML文件>');
    process.exit(1);
}

const userCodeFile = process.argv[2];
const outputFile = process.argv[3];
const width = 800;
const height = 600;
const title = 'Three.js 本地测试';

try {
    console.log('📄 读取用户代码...');
    const userCode = fs.readFileSync(userCodeFile, 'utf8');
    console.log('✅ 用户代码读取成功');
    
    console.log('📦 定位Three.js库...');
    
    // 尝试不同的Three.js文件路径（优先使用core.js）
    let threejsCode = null;
    const possiblePaths = [
        path.join(__dirname, '..', 'node_modules', 'three', 'build', 'three.core.js'),
        path.join(__dirname, '..', 'node_modules', 'three', 'build', 'three.module.js'),
        path.join(process.cwd(), 'node_modules', 'three', 'build', 'three.core.js'),
        path.join(process.cwd(), 'node_modules', 'three', 'build', 'three.module.js'),
    ];
    
    for (const libPath of possiblePaths) {
        console.log(`🔍 尝试路径: ${libPath}`);
        if (fs.existsSync(libPath)) {
            threejsCode = fs.readFileSync(libPath, 'utf8');
            console.log(`✅ 找到Three.js库: ${libPath}`);
            break;
        }
    }
    
    if (!threejsCode) {
        throw new Error('无法找到Three.js库文件');
    }
    
    console.log('🔧 转换Three.js为浏览器兼容格式...');
    
    // 转换ES6模块为浏览器兼容格式
    // 创建一个立即执行函数，将所有导出作为全局THREE对象的属性
    const browserCompatibleCode = `
(function() {
    // Three.js library code
    ${threejsCode}
    
    // 创建全局THREE对象，包含所有导出的内容
    window.THREE = {
        ACESFilmicToneMapping, AddEquation, AddOperation, AdditiveAnimationBlendMode, AdditiveBlending, 
        AgXToneMapping, AlphaFormat, AlwaysCompare, AlwaysDepth, AlwaysStencilFunc, AmbientLight, 
        AnimationAction, AnimationClip, AnimationLoader, AnimationMixer, AnimationObjectGroup, AnimationUtils, 
        ArcCurve, ArrayCamera, ArrowHelper, AttachedBindMode, Audio, AudioAnalyser, AudioContext, 
        AudioListener, AudioLoader, AxesHelper, BackSide, BasicDepthPacking, BasicShadowMap, BatchedMesh, 
        Bone, BooleanKeyframeTrack, Box2, Box3, Box3Helper, BoxGeometry, BoxHelper, BufferAttribute, 
        BufferGeometry, BufferGeometryLoader, ByteType, Cache, Camera, CameraHelper, CanvasTexture, 
        CapsuleGeometry, CatmullRomCurve3, CineonToneMapping, CircleGeometry, ClampToEdgeWrapping, Clock, 
        Color, ColorKeyframeTrack, ColorManagement, CompressedArrayTexture, CompressedCubeTexture, 
        CompressedTexture, CompressedTextureLoader, ConeGeometry, ConstantAlphaFactor, ConstantColorFactor, 
        Controls, CubeCamera, CubeReflectionMapping, CubeRefractionMapping, CubeTexture, CubeTextureLoader, 
        CubeUVReflectionMapping, CubicBezierCurve, CubicBezierCurve3, CubicInterpolant, CullFaceBack, 
        CullFaceFront, CullFaceFrontBack, CullFaceNone, Curve, CurvePath, CustomBlending, CustomToneMapping, 
        CylinderGeometry, Cylindrical, Data3DTexture, DataArrayTexture, DataTexture, DataTextureLoader, 
        DataUtils, DecrementStencilOp, DecrementWrapStencilOp, DefaultLoadingManager, DepthFormat, 
        DepthStencilFormat, DepthTexture, DetachedBindMode, DirectionalLight, DirectionalLightHelper, 
        DiscreteInterpolant, DodecahedronGeometry, DoubleSide, DstAlphaFactor, DstColorFactor, 
        DynamicCopyUsage, DynamicDrawUsage, DynamicReadUsage, EdgesGeometry, EllipseCurve, EqualCompare, 
        EqualDepth, EqualStencilFunc, EquirectangularReflectionMapping, EquirectangularRefractionMapping, 
        Euler, EventDispatcher, ExtrudeGeometry, FileLoader, Float16BufferAttribute, Float32BufferAttribute, 
        FloatType, Fog, FogExp2, FramebufferTexture, FrontSide, Frustum, GLBufferAttribute, GLSL1, GLSL3, 
        GreaterCompare, GreaterDepth, GreaterEqualCompare, GreaterEqualDepth, GreaterEqualStencilFunc, 
        GreaterStencilFunc, GridHelper, Group, HalfFloatType, HemisphereLight, HemisphereLightHelper, 
        IcosahedronGeometry, ImageBitmapLoader, ImageLoader, ImageUtils, IncrementStencilOp, 
        IncrementWrapStencilOp, InstancedBufferAttribute, InstancedBufferGeometry, InstancedInterleavedBuffer, 
        InstancedMesh, Int16BufferAttribute, Int32BufferAttribute, Int8BufferAttribute, IntType, 
        InterleavedBuffer, InterleavedBufferAttribute, Interpolant, InterpolateDiscrete, InterpolateLinear, 
        InterpolateSmooth, InvertStencilOp, KeepStencilOp, KeyframeTrack, LOD, LatheGeometry, Layers, 
        LessCompare, LessDepth, LessEqualCompare, LessEqualDepth, LessEqualStencilFunc, LessStencilFunc, 
        Light, LightProbe, Line, Line3, LineBasicMaterial, LineCurve, LineCurve3, LineDashedMaterial, 
        LineLoop, LineSegments, LinearFilter, LinearInterpolant, LinearMipMapLinearFilter, 
        LinearMipMapNearestFilter, LinearMipmapLinearFilter, LinearMipmapNearestFilter, LinearSRGBColorSpace, 
        LinearToneMapping, LinearTransfer, Loader, LoaderUtils, LoadingManager, LoopOnce, LoopPingPong, 
        LoopRepeat, MOUSE, Material, MaterialLoader, MathUtils, Matrix2, Matrix3, Matrix4, MaxEquation, 
        Mesh, MeshBasicMaterial, MeshDepthMaterial, MeshDistanceMaterial, MeshLambertMaterial, 
        MeshMatcapMaterial, MeshNormalMaterial, MeshPhongMaterial, MeshPhysicalMaterial, MeshStandardMaterial, 
        MeshToonMaterial, MinEquation, MirroredRepeatWrapping, MixOperation, MultiplyBlending, 
        MultiplyOperation, NearestFilter, NearestMipMapLinearFilter, NearestMipMapNearestFilter, 
        NearestMipmapLinearFilter, NearestMipmapNearestFilter, NeutralToneMapping, NeverCompare, NeverDepth, 
        NeverStencilFunc, NoBlending, NoColorSpace, NoToneMapping, NormalAnimationBlendMode, NormalBlending, 
        NotEqualCompare, NotEqualDepth, NotEqualStencilFunc, NumberKeyframeTrack, Object3D, ObjectLoader, 
        ObjectSpaceNormalMap, OctahedronGeometry, OneFactor, OneMinusConstantAlphaFactor, 
        OneMinusConstantColorFactor, OneMinusDstAlphaFactor, OneMinusDstColorFactor, OneMinusSrcAlphaFactor, 
        OneMinusSrcColorFactor, OrthographicCamera, PCFShadowMap, PCFSoftShadowMap, Path, PerspectiveCamera, 
        Plane, PlaneGeometry, PlaneHelper, PointLight, PointLightHelper, Points, PointsMaterial, 
        PolarGridHelper, PolyhedronGeometry, PositionalAudio, PropertyBinding, PropertyMixer, 
        QuadraticBezierCurve, QuadraticBezierCurve3, Quaternion, QuaternionKeyframeTrack, 
        QuaternionLinearInterpolant, RAD2DEG, REVISION, RGBADepthPacking, RGBAFormat, RGBAIntegerFormat, 
        RawShaderMaterial, Ray, Raycaster, RectAreaLight, RedFormat, RedIntegerFormat, ReinhardToneMapping, 
        RenderTarget, RepeatWrapping, ReplaceStencilOp, ReverseSubtractEquation, RingGeometry, 
        SRGBColorSpace, SRGBTransfer, Scene, ShaderMaterial, ShadowMaterial, Shape, ShapeGeometry, 
        ShapePath, ShapeUtils, ShortType, Skeleton, SkeletonHelper, SkinnedMesh, Source, Sphere, 
        SphereGeometry, Spherical, SphericalHarmonics3, SplineCurve, SpotLight, SpotLightHelper, Sprite, 
        SpriteMaterial, SrcAlphaFactor, SrcAlphaSaturateFactor, SrcColorFactor, StaticCopyUsage, 
        StaticDrawUsage, StaticReadUsage, StereoCamera, StreamCopyUsage, StreamDrawUsage, StreamReadUsage, 
        StringKeyframeTrack, SubtractEquation, SubtractiveBlending, TOUCH, TangentSpaceNormalMap, 
        TetrahedronGeometry, Texture, TextureLoader, TextureUtils, TorusGeometry, TorusKnotGeometry, 
        Triangle, TriangleFanDrawMode, TriangleStripDrawMode, TrianglesDrawMode, TubeGeometry, UVMapping, 
        Uint16BufferAttribute, Uint32BufferAttribute, Uint8BufferAttribute, Uint8ClampedBufferAttribute, 
        Uniform, UniformsGroup, UniformsUtils, UnsignedByteType, UnsignedInt248Type, UnsignedInt5999Type, 
        UnsignedIntType, UnsignedShort4444Type, UnsignedShort5551Type, UnsignedShortType, VSMShadowMap, 
        Vector2, Vector3, Vector4, VectorKeyframeTrack, VideoFrameTexture, VideoTexture, 
        WebGL3DRenderTarget, WebGLArrayRenderTarget, WebGLCoordinateSystem, WebGLCubeRenderTarget, 
        WebGLRenderTarget, WebGPUCoordinateSystem, WebXRController, WireframeGeometry, WrapAroundEnding, 
        ZeroCurvatureEnding, ZeroFactor, ZeroSlopeEnding, ZeroStencilOp, arrayNeedsUint32, cloneUniforms, 
        createCanvasElement, createElementNS, getByteLength, getUnlitUniformColorSpace, mergeUniforms, 
        probeAsync, toNormalizedProjectionMatrix, toReversedProjectionMatrix, warnOnce
    };
    
    console.log('✅ Three.js 已加载为全局对象');
})();`;
    
    console.log('🔧 生成HTML文件...');
    
    // 生成优化的HTML文件
    const html = `<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>${title}</title>
    <style>
        body {
            margin: 0;
            background: #1a1a2e;
            font-family: Arial, sans-serif;
            color: white;
            overflow: hidden;
        }
        #container {
            width: ${width}px;
            height: ${height}px;
            margin: 20px auto;
            border: 2px solid #4facfe;
            border-radius: 8px;
        }
        #info {
            text-align: center;
            margin: 10px;
            color: #4facfe;
        }
    </style>
</head>
<body>
    <div id="info">${title} - 浏览器兼容版</div>
    <div id="container"></div>

    <script>
        ${browserCompatibleCode}
    </script>
    
    <script>
        // 初始化Three.js
        console.log('初始化Three.js...');
        
        // 检查THREE是否可用
        if (typeof THREE === 'undefined') {
            document.getElementById('info').innerHTML = '❌ Three.js加载失败';
            throw new Error('Three.js未正确加载');
        }
        
        console.log('THREE对象:', THREE);
        
        // 创建场景
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(75, ${width} / ${height}, 0.1, 1000);
        const renderer = new THREE.WebGLRenderer({ antialias: true });
        
        renderer.setSize(${width}, ${height});
        renderer.setClearColor(0x1a1a2e, 1);
        
        document.getElementById('container').appendChild(renderer.domElement);
        
        // 添加光照
        const ambientLight = new THREE.AmbientLight(0x404040, 0.6);
        scene.add(ambientLight);
        
        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
        directionalLight.position.set(10, 10, 5);
        scene.add(directionalLight);
        
        // 设置相机位置
        camera.position.set(5, 5, 5);
        camera.lookAt(0, 0, 0);
        
        // 定义基础动画函数
        function animate() {
            requestAnimationFrame(animate);
            renderer.render(scene, camera);
        }
        
        // 执行用户代码
        try {
            ${userCode}
        } catch (e) {
            console.error('用户代码执行错误:', e);
            document.getElementById('info').innerHTML = '❌ 用户代码执行失败: ' + e.message;
        }
        
        // 启动渲染循环
        animate();
        
        console.log('✅ Three.js初始化完成');
        document.getElementById('info').innerHTML = '✅ ${title} - 运行中';
    </script>
</body>
</html>`;
    
    fs.writeFileSync(outputFile, html, 'utf8');
    console.log(`✅ HTML文件已生成: ${outputFile}`);
    
} catch (error) {
    console.error(`❌ 错误: ${error.message}`);
    process.exit(1);
} 