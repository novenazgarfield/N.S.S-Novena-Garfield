#!/bin/bash
# NEXUS远程指挥中心 - 停止脚本

echo "🛑 停止NEXUS远程指挥中心..."

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 读取PID文件并停止服务
if [ -f "logs/websocket.pid" ]; then
    WEBSOCKET_PID=$(cat logs/websocket.pid)
    if ps -p $WEBSOCKET_PID > /dev/null; then
        echo "📡 停止WebSocket服务器 (PID: $WEBSOCKET_PID)..."
        kill $WEBSOCKET_PID
        echo "   ✅ WebSocket服务器已停止"
    else
        echo "   ⚠️  WebSocket服务器已经停止"
    fi
    rm -f logs/websocket.pid
fi

if [ -f "logs/frontend.pid" ]; then
    FRONTEND_PID=$(cat logs/frontend.pid)
    if ps -p $FRONTEND_PID > /dev/null; then
        echo "💻 停止前端服务器 (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID
        echo "   ✅ 前端服务器已停止"
    else
        echo "   ⚠️  前端服务器已经停止"
    fi
    rm -f logs/frontend.pid
fi

# 清理可能残留的进程
echo "🧹 清理残留进程..."
pkill -f "websocket_server.py" 2>/dev/null
pkill -f "vite.*52308" 2>/dev/null

echo ""
echo "✅ NEXUS远程指挥中心已完全停止"