#!/bin/bash
# 🚀 N.S.S-Novena-Garfield 快速启动脚本

set -e

echo "🚀 N.S.S-Novena-Garfield 启动器"
echo "=================================="

# 检查Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker未安装，请先安装Docker"
    exit 1
fi

if ! command -v docker compose &> /dev/null; then
    echo "❌ Docker Compose未安装，请先安装Docker Compose"
    exit 1
fi

# 创建必要目录
echo "📁 创建必要目录..."
mkdir -p ../data ../logs ../temp

# 复制环境变量模板
if [ ! -f ../../.env ]; then
    echo "📋 创建环境配置文件..."
    cp .env.template ../../.env
    echo "✅ 已创建 .env 文件，请根据需要修改配置"
fi

# 选择启动模式
echo ""
echo "请选择启动模式:"
echo "1) Docker Compose (推荐)"
echo "2) 本地模式"
echo "3) 仅启动核心服务"
echo "4) 配置验证"
echo ""
read -p "请输入选择 (1-4): " choice

case $choice in
    1)
        echo "🐳 使用Docker Compose启动所有服务..."
        cd ../../ && docker compose -f management/deployment/docker-compose.yml up -d
        echo "✅ 服务启动完成！"
        echo ""
        echo "🌐 访问地址:"
        echo "  - RAG智能系统: http://localhost:8501"
        echo "  - Changlee音乐: http://localhost:8082"
        echo "  - Chronicle时间: http://localhost:3000"
        echo "  - Nexus集成: http://localhost:8080"
        echo "  - API管理: http://localhost:8000"
        echo ""
        echo "📊 查看状态: docker compose -f management/deployment/docker-compose.yml ps"
        echo "🛑 停止服务: docker compose -f management/deployment/docker-compose.yml down"
        ;;
    2)
        echo "💻 使用本地模式启动..."
        cd ../../ && chmod +x management/scripts/unified_launcher.py
        python management/scripts/unified_launcher.py --interactive
        ;;
    3)
        echo "🎯 启动核心服务..."
        cd ../../ && docker compose -f management/deployment/docker-compose.yml up -d api-manager rag-system changlee-web
        echo "✅ 核心服务启动完成！"
        ;;
    4)
        echo "🔧 运行配置验证..."
        cd ../../ && python management/scripts/config_validator.py
        ;;
    *)
        echo "❌ 无效选择"
        exit 1
        ;;
esac