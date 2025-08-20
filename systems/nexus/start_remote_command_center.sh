#!/bin/bash
# NEXUS远程指挥中心 - 一键启动脚本
# 启动WebSocket服务器和前端应用

echo "🚀 启动NEXUS远程指挥中心..."

# 检查依赖
if ! command -v python3 &> /dev/null; then
    echo "❌ 需要Python3"
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo "❌ 需要Node.js和npm"
    exit 1
fi

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "📁 工作目录: $SCRIPT_DIR"

# 创建日志目录
mkdir -p logs

# 启动WebSocket服务器
echo "📡 启动WebSocket服务器..."
cd backend
python3 websocket_server.py > ../logs/websocket.log 2>&1 &
WEBSOCKET_PID=$!
echo "   WebSocket服务器PID: $WEBSOCKET_PID"

# 等待WebSocket服务器启动
sleep 3

# 检查WebSocket服务器是否启动成功
if ps -p $WEBSOCKET_PID > /dev/null; then
    echo "   ✅ WebSocket服务器启动成功 (端口: 8765)"
else
    echo "   ❌ WebSocket服务器启动失败"
    exit 1
fi

# 返回项目根目录
cd "$SCRIPT_DIR"

# 启动前端开发服务器
echo "💻 启动前端服务器..."
npm run dev > logs/frontend.log 2>&1 &
FRONTEND_PID=$!
echo "   前端服务器PID: $FRONTEND_PID"

# 等待前端服务器启动
echo "⏳ 等待服务启动..."
sleep 10

# 检查前端服务器是否启动成功
if ps -p $FRONTEND_PID > /dev/null; then
    echo "   ✅ 前端服务器启动成功"
else
    echo "   ❌ 前端服务器启动失败"
    kill $WEBSOCKET_PID 2>/dev/null
    exit 1
fi

# 保存PID到文件
echo $WEBSOCKET_PID > logs/websocket.pid
echo $FRONTEND_PID > logs/frontend.pid

echo ""
echo "🎉 NEXUS远程指挥中心启动完成！"
echo ""
echo "📊 服务状态:"
echo "   📡 WebSocket服务器: ws://localhost:8765 (PID: $WEBSOCKET_PID)"
echo "   💻 前端服务器: http://localhost:52308 (PID: $FRONTEND_PID)"
echo ""
echo "🌐 访问地址:"
echo "   本地访问: http://localhost:52308/remote"
echo "   远程指挥中心: http://localhost:52308/remote"
echo ""
echo "📝 日志文件:"
echo "   WebSocket日志: logs/websocket.log"
echo "   前端日志: logs/frontend.log"
echo ""
echo "🛑 停止服务: ./stop_remote_command_center.sh"
echo ""
echo "✨ 现在您可以在任何设备上访问NEXUS远程指挥中心！"