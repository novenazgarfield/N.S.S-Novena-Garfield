#!/bin/bash
"""
系统状态检查
NEXUS远程指挥中心 - 示例脚本
"""

echo "🖥️  检查系统状态..."
echo "💾 内存使用情况:"
free -h | head -2

echo ""
echo "💿 磁盘使用情况:"
df -h | head -5

echo ""
echo "🔥 CPU使用情况:"
top -bn1 | grep "Cpu(s)" | head -1

echo ""
echo "🌐 网络连接状态:"
ping -c 3 8.8.8.8 > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "   ✅ 网络连接正常"
else
    echo "   ❌ 网络连接异常"
fi

echo ""
echo "✅ 系统状态检查完成！"