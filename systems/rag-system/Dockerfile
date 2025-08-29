# 🐳 RAG智能系统 Dockerfile
FROM python:3.11-slim

LABEL maintainer="N.S.S-Novena-Garfield Team"
LABEL description="RAG智能系统 - Streamlit应用"

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# 复制requirements文件
COPY requirements.txt* ./
COPY ../../requirements.txt ./global_requirements.txt

# 安装Python依赖
RUN pip install --no-cache-dir -r global_requirements.txt
RUN if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# 安装Streamlit
RUN pip install --no-cache-dir streamlit

# 复制应用代码
COPY . .

# 创建必要目录
RUN mkdir -p models data sessions

# 设置环境变量
ENV PYTHONPATH=/app
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
ENV STREAMLIT_SERVER_ENABLE_CORS=true
ENV STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=false

# 暴露端口
EXPOSE 8501

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# 启动命令
CMD ["streamlit", "run", "intelligence_app.py", "--server.port=8501", "--server.address=0.0.0.0"]