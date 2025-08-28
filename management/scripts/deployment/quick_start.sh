#!/bin/bash

# NEXUS AI 快速启动脚本
# 简化版本，用于快速重启服务

echo "🚀 快速启动 NEXUS AI 系统..."

# 进入脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 运行完整启动脚本
./start_tunnels.sh

echo ""
echo "✅ 快速启动完成！"
echo "📱 请查看上方显示的访问地址"