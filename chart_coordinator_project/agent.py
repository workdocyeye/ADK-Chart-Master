# Copyright 2025 Google LLC
"""
ADK Web UI 标准Agent文件 - Deepseek版本
定义root_agent供adk web命令加载
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv(encoding='utf-8')

# 处理导入路径问题
current_dir = Path(__file__).parent.absolute()
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))
    
# 确保能够找到agents和tools模块
print(f"添加路径到sys.path: {current_dir}")
print(f"当前sys.path前3项: {sys.path[:3]}")

def create_root_agent():
    """创建root_agent的函数，处理可能的配置错误"""
    try:
        # 检查Deepseek API密钥
        api_key = os.getenv('DEEPSEEK_API_KEY')
        if not api_key or api_key == 'your_deepseek_api_key_here':
            print("⚠️  警告：未检测到有效的DEEPSEEK_API_KEY")
            print("💡 请在.env文件中配置：DEEPSEEK_API_KEY=你的密钥")
            print("📝 获取地址：https://platform.deepseek.com/")
            return None

        # 导入我们的LLM驱动图表系统
        from llm_driven_chart_system import create_llm_driven_chart_coordinator
        
        # 创建agent
        agent = create_llm_driven_chart_coordinator()
        
        print(f"✅ Deepseek Agent创建成功: {agent.name}")
        print(f"🔧 工具数量: {len(agent.tools)}")
        print(f"👥 Sub-Agents数量: {len(agent.sub_agents)}")
        print(f"🏷️ Agent类型: {type(agent)}")
        
        return agent
        
    except Exception as e:
        print(f"❌ Agent创建失败: {e}")
        print("💡 请检查：")
        print("   1. .env文件中的DEEPSEEK_API_KEY配置")
        print("   2. litellm库是否正确安装")
        print("   3. 所有依赖是否完整")
        return None

# ADK Web UI 要求的标准变量名
# adk web 命令会自动查找这个变量
root_agent = create_root_agent() 