#!/bin/bash

# NEXUS远程唤醒脚本
# 使用Wake-on-LAN技术远程唤醒目标电脑

echo "🌅 NEXUS远程唤醒系统启动..."
echo "⚡ 准备发送魔术包唤醒目标电脑"

# 默认配置（用户可以修改）
DEFAULT_MAC="00:11:22:33:44:55"  # 示例MAC地址
DEFAULT_IP="192.168.1.255"       # 广播地址
DEFAULT_PORT="9"                 # WOL标准端口

# 从参数获取MAC地址，如果没有则使用默认值
TARGET_MAC=${1:-$DEFAULT_MAC}
TARGET_IP=${2:-$DEFAULT_IP}
TARGET_PORT=${3:-$DEFAULT_PORT}

echo "📡 目标信息:"
echo "   MAC地址: $TARGET_MAC"
echo "   IP地址: $TARGET_IP"
echo "   端口: $TARGET_PORT"

# 验证MAC地址格式
if [[ ! $TARGET_MAC =~ ^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$ ]]; then
    echo "❌ 错误: MAC地址格式无效"
    echo "   正确格式: XX:XX:XX:XX:XX:XX 或 XX-XX-XX-XX-XX-XX"
    exit 1
fi

echo "🚀 正在发送魔术包..."

# 使用Python wakeonlan库发送魔术包
python3 -c "
from wakeonlan import send_magic_packet
import sys

try:
    # 发送魔术包
    send_magic_packet('$TARGET_MAC', ip_address='$TARGET_IP', port=$TARGET_PORT)
    print('✅ 魔术包发送成功！')
    print('⏳ 目标电脑应该在30-60秒内启动')
    print('💡 提示: 确保目标电脑已启用Wake-on-LAN功能')
except Exception as e:
    print(f'❌ 发送失败: {e}')
    sys.exit(1)
"

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 远程唤醒命令执行完成！"
    echo ""
    echo "📋 检查清单:"
    echo "   ✓ 魔术包已发送"
    echo "   ⏳ 等待目标电脑响应"
    echo ""
    echo "💡 如果电脑没有启动，请检查:"
    echo "   1. 目标电脑是否支持Wake-on-LAN"
    echo "   2. BIOS中是否启用了WOL功能"
    echo "   3. 网卡驱动是否启用了WOL"
    echo "   4. MAC地址是否正确"
    echo "   5. 网络连接是否正常"
    echo ""
    echo "🔧 常见设置位置:"
    echo "   - BIOS: Power Management → Wake on LAN"
    echo "   - Windows: 设备管理器 → 网络适配器 → 属性 → 电源管理"
    echo "   - Linux: ethtool -s eth0 wol g"
else
    echo "❌ 远程唤醒失败，请检查网络连接和配置"
    exit 1
fi