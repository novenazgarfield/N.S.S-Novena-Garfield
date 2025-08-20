#!/bin/bash

# NEXUS远程关机测试脚本
# 用于演示关机功能，不会真正关机

echo "🔴 NEXUS远程关机测试模式"
echo "⚠️  这是测试模式，不会真正关机"

# 获取参数
SHUTDOWN_TYPE=${1:-"normal"}
DELAY_SECONDS=${2:-"60"}
MESSAGE=${3:-"NEXUS远程关机测试"}

echo ""
echo "🎯 关机参数:"
echo "   类型: $SHUTDOWN_TYPE"
echo "   延迟: ${DELAY_SECONDS}秒"
echo "   消息: $MESSAGE"
echo ""

# 模拟关机过程
echo "🚀 模拟执行关机命令..."

case $SHUTDOWN_TYPE in
    "force")
        echo "⚡ 强制关机模式 - 立即关闭系统"
        echo "💾 警告: 可能丢失未保存的数据"
        ;;
    "reboot")
        echo "🔄 重启模式 - 关机后自动重新启动"
        echo "⏳ 系统将在${DELAY_SECONDS}秒后重启"
        ;;
    *)
        echo "🔴 正常关机模式 - 安全关闭所有程序"
        echo "💾 正在保存所有工作..."
        ;;
esac

echo ""
echo "✅ 关机命令模拟执行成功！"
echo "⏳ 在真实环境中，系统将在 ${DELAY_SECONDS} 秒后执行操作"

# 模拟倒计时（仅显示前5秒）
echo ""
echo "⏰ 模拟倒计时（仅显示前5秒）:"
for ((i=5; i>0; i--)); do
    echo -ne "\r🔴 系统将在 $i 秒后${SHUTDOWN_TYPE}...   "
    sleep 1
done

echo -e "\n"
echo "🎉 测试完成！"
echo ""
echo "📋 测试摘要:"
echo "   ✓ 参数解析正确"
echo "   ✓ 关机类型: $SHUTDOWN_TYPE"
echo "   ✓ 延迟时间: ${DELAY_SECONDS}秒"
echo "   ✓ 提示消息: $MESSAGE"
echo ""
echo "💡 在真实环境中:"
echo "   - Linux: sudo shutdown -h +$((DELAY_SECONDS/60))"
echo "   - Windows: shutdown /s /t $DELAY_SECONDS"
echo "   - macOS: sudo shutdown -h +$((DELAY_SECONDS/60))"
echo ""
echo "🔧 如需取消关机，请执行:"
echo "   - Linux/macOS: sudo shutdown -c"
echo "   - Windows: shutdown /a"