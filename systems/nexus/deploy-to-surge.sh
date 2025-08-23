#!/bin/bash

# NEXUS 一键部署到 Surge.sh
# 自定义域名: nss-novena-garfield.surge.sh

echo "🚀 NEXUS 一键部署脚本"
echo "目标地址: https://nss-novena-garfield.surge.sh"
echo "=================================="

# 检查是否安装了 surge
if ! command -v surge &> /dev/null; then
    echo "📦 正在安装 Surge.sh..."
    npm install -g surge
fi

# 创建部署目录
echo "📁 准备部署文件..."
mkdir -p deploy-temp
cp nexus-mini.html deploy-temp/index.html

# 创建 CNAME 文件指定自定义域名
echo "nss-novena-garfield.surge.sh" > deploy-temp/CNAME

# 部署到 Surge
echo "🌐 正在部署到 Surge.sh..."
cd deploy-temp

# 自动部署（需要用户首次登录）
surge . nss-novena-garfield.surge.sh

echo ""
echo "🎉 部署完成！"
echo "🌐 访问地址: https://nss-novena-garfield.surge.sh"
echo "📱 移动端友好，支持PWA"
echo ""
echo "💡 提示: 首次使用需要注册 Surge 账号（免费）"
echo "📧 只需要邮箱即可，无需信用卡"

# 清理临时文件
cd ..
rm -rf deploy-temp