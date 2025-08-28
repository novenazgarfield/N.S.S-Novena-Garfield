# 🐳 API管理器 Dockerfile
FROM python:3.11-slim

LABEL maintainer="N.S.S-Novena-Garfield Team"
LABEL description="API管理器服务"

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制requirements文件
COPY requirements.txt* ./
COPY ../requirements.txt ./global_requirements.txt

# 安装Python依赖
RUN pip install --no-cache-dir -r global_requirements.txt
RUN if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# 复制应用代码
COPY . .

# 创建必要目录
RUN mkdir -p logs data

# 设置环境变量
ENV PYTHONPATH=/app
ENV API_PORT=8000
ENV PYTHONUNBUFFERED=1

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 启动命令
CMD ["python", "api_manager.py"]