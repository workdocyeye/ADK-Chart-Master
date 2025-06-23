# --- Base Image ---
# Start with a slim, official Python image
FROM python:3.11-slim

# 环境变量
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# 安装系统依赖
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    # Node.js/JavaScript工具
    nodejs npm \
    # PlantUML/Java
    default-jre \
    # Graphviz流程图
    graphviz \
    # Matplotlib等需要的Tk
    python3-tk \
    # 构建C/C++扩展
    build-essential \
    # Puppeteer/Chromium/mermaid-cli/Selenium依赖
    ca-certificates \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    xdg-utils \
    wget \
    # 中文字体（全平台常用，覆盖SimHei、YaHei、KaiTi、思源、文泉驿、Noto、DejaVu等）
    fonts-wqy-zenhei \
    fonts-wqy-microhei \
    fonts-noto-cjk \
    fonts-noto-cjk-extra \
    fonts-noto-color-emoji \
    fonts-arphic-ukai \
    fonts-arphic-uming \
    fonts-dejavu \
    fonts-dejavu-core \
    fonts-dejavu-extra \
    fonts-droid-fallback \
    fonts-liberation \
    fonts-freefont-ttf \
    fonts-noto \
    fonts-noto-mono \
    fonts-noto-unhinted \
    fonts-noto-ui-core \
    fonts-noto-ui-extra \
    # fonts-noto-ui-symbols \
    # fonts-noto-ui-symbols-extra \
    # ttf-mscorefonts-installer \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 复制 Python 依赖
COPY chart_coordinator_project/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# 复制 Node 依赖
COPY chart_coordinator_project/package.json ./package.json
COPY chart_coordinator_project/package-lock.json ./package-lock.json
RUN npm install
RUN npm install -g @mermaid-js/mermaid-cli

# 复制全部项目代码
COPY . .

# 暴露端口
EXPOSE 8000

# 设置环境变量
ENV PORT=8000

# 启动命令：在总文件夹下启动 ADK 服务
CMD ["adk", "web", ".", "--host", "0.0.0.0", "--port", "8000"]

# Prevents Python from writing .pyc files 