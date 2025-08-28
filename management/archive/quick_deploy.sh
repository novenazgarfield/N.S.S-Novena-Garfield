#!/bin/bash
# RAG系统快速部署脚本

echo "🚀 开始部署RAG智能问答系统..."

# 进入项目目录
cd systems/rag-system

# 安装依赖
echo "📦 安装依赖..."
pip install streamlit pandas blinker

# 启动服务
echo "🌐 启动服务..."
streamlit run app_online.py --server.port 8501 --server.address 0.0.0.0 --server.enableCORS true --server.enableXsrfProtection false

echo "✅ 部署完成！"
echo "🌐 访问地址: https://your-codespace-url-8501.githubpreview.dev"