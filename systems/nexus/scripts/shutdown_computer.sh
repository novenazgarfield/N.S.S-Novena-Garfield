#!/bin/bash

# NEXUS远程关机系统
# 支持Windows/Linux/macOS远程关机
# 作者: NEXUS Team
# 版本: 1.0.0

echo "🔴 NEXUS远程关机系统启动..."
echo "⚠️  准备关闭目标电脑"

# 获取参数
SHUTDOWN_TYPE=${1:-"normal"}  # normal, force, reboot
DELAY_SECONDS=${2:-"60"}      # 延迟秒数，默认60秒
MESSAGE=${3:-"NEXUS远程关机：系统将在${DELAY_SECONDS}秒后关闭"}

echo "🎯 关机信息:"
echo "   类型: $SHUTDOWN_TYPE"
echo "   延迟: ${DELAY_SECONDS}秒"
echo "   消息: $MESSAGE"

# 检测操作系统
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    elif [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
        echo "windows"
    else
        echo "unknown"
    fi
}

OS=$(detect_os)
echo "🖥️  检测到操作系统: $OS"

# 执行关机命令
execute_shutdown() {
    case $OS in
        "linux")
            echo "🐧 执行Linux关机命令..."
            case $SHUTDOWN_TYPE in
                "force")
                    echo "⚡ 强制关机模式"
                    sudo shutdown -h +$(($DELAY_SECONDS/60)) "$MESSAGE"
                    ;;
                "reboot")
                    echo "🔄 重启模式"
                    sudo shutdown -r +$(($DELAY_SECONDS/60)) "$MESSAGE"
                    ;;
                *)
                    echo "🔴 正常关机模式"
                    sudo shutdown -h +$(($DELAY_SECONDS/60)) "$MESSAGE"
                    ;;
            esac
            ;;
            
        "macos")
            echo "🍎 执行macOS关机命令..."
            case $SHUTDOWN_TYPE in
                "force")
                    echo "⚡ 强制关机模式"
                    sudo shutdown -h +$(($DELAY_SECONDS/60))
                    ;;
                "reboot")
                    echo "🔄 重启模式"
                    sudo shutdown -r +$(($DELAY_SECONDS/60))
                    ;;
                *)
                    echo "🔴 正常关机模式"
                    sudo shutdown -h +$(($DELAY_SECONDS/60))
                    ;;
            esac
            ;;
            
        "windows")
            echo "🪟 执行Windows关机命令..."
            case $SHUTDOWN_TYPE in
                "force")
                    echo "⚡ 强制关机模式"
                    shutdown /s /f /t $DELAY_SECONDS /c "$MESSAGE"
                    ;;
                "reboot")
                    echo "🔄 重启模式"
                    shutdown /r /t $DELAY_SECONDS /c "$MESSAGE"
                    ;;
                *)
                    echo "🔴 正常关机模式"
                    shutdown /s /t $DELAY_SECONDS /c "$MESSAGE"
                    ;;
            esac
            ;;
            
        *)
            echo "❌ 不支持的操作系统: $OS"
            exit 1
            ;;
    esac
}

# 显示警告信息
echo ""
echo "⚠️  警告: 系统将在 ${DELAY_SECONDS} 秒后关闭！"
echo "📋 关机详情:"
echo "   - 操作系统: $OS"
echo "   - 关机类型: $SHUTDOWN_TYPE"
echo "   - 延迟时间: ${DELAY_SECONDS}秒"
echo "   - 提示消息: $MESSAGE"
echo ""

# 询问确认（如果是交互模式）
if [ -t 0 ]; then
    echo "❓ 确认要执行关机操作吗? (y/N)"
    read -r confirmation
    if [[ ! $confirmation =~ ^[Yy]$ ]]; then
        echo "❌ 关机操作已取消"
        exit 0
    fi
fi

echo "🚀 正在执行关机命令..."

# 执行关机
if execute_shutdown; then
    echo "✅ 关机命令执行成功！"
    echo "⏳ 系统将在 ${DELAY_SECONDS} 秒后关闭"
    
    # 显示倒计时（仅在交互模式下）
    if [ -t 0 ] && [ $DELAY_SECONDS -le 300 ]; then
        echo "⏰ 倒计时开始..."
        for ((i=$DELAY_SECONDS; i>0; i--)); do
            echo -ne "\r🔴 系统将在 $i 秒后关闭...   "
            sleep 1
        done
        echo -e "\n💤 系统正在关闭..."
    fi
else
    echo "❌ 关机命令执行失败！"
    exit 1
fi

echo ""
echo "🎉 远程关机命令执行完成！"
echo ""
echo "📋 操作摘要:"
echo "   ✓ 关机命令已发送"
echo "   ✓ 延迟时间: ${DELAY_SECONDS}秒"
echo "   ✓ 关机类型: $SHUTDOWN_TYPE"
echo ""
echo "💡 提示:"
echo "   - 如需取消关机，请执行: shutdown -c (Windows) 或 sudo shutdown -c (Linux/macOS)"
echo "   - 关机后可使用远程唤醒功能重新启动"
echo "   - 建议在关机前保存所有工作"
echo ""
echo "🔧 故障排除:"
echo "   - 如果权限不足，请使用管理员权限运行"
echo "   - Windows用户可能需要启用远程关机权限"
echo "   - Linux/macOS用户需要sudo权限"