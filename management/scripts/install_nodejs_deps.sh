#!/bin/bash

# 🧠 N.S.S-Novena-Garfield Node.js依赖安装脚本
# 多模态AI融合研究工作站 - Node.js依赖一键安装
# 使用方法: chmod +x install_nodejs_deps.sh && ./install_nodejs_deps.sh

echo "🧠 N.S.S-Novena-Garfield Node.js依赖安装"
echo "========================================"
echo ""

# 检查Node.js环境
echo "🔍 检查Node.js环境..."
if ! command -v node &> /dev/null; then
    echo "❌ Node.js未安装，请先安装Node.js 16+"
    echo "📥 下载地址: https://nodejs.org/"
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo "❌ npm未安装，请先安装npm"
    exit 1
fi

NODE_VERSION=$(node --version)
NPM_VERSION=$(npm --version)
echo "✅ Node.js版本: $NODE_VERSION"
echo "✅ npm版本: $NPM_VERSION"
echo ""

# 检查磁盘空间
echo "💾 检查磁盘空间..."
AVAILABLE_SPACE=$(df . | tail -1 | awk '{print $4}')
if [ $AVAILABLE_SPACE -lt 2097152 ]; then  # 2GB in KB
    echo "⚠️  警告: 可用磁盘空间不足2GB，可能导致安装失败"
    echo "📊 当前可用空间: $(df -h . | tail -1 | awk '{print $4}')"
    read -p "是否继续安装? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi
echo ""

# 设置npm镜像源（可选）
echo "🌐 配置npm镜像源..."
read -p "是否使用国内镜像源加速下载? (Y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
    npm config set registry https://registry.npmmirror.com
    echo "✅ 已设置为国内镜像源"
else
    echo "📡 使用默认npm源"
fi
echo ""

# 开始安装
echo "🚀 开始安装Node.js依赖..."
echo "📊 预计安装大小: ~1.6GB"
echo "⏱️  预计安装时间: 5-20分钟"
echo ""

INSTALL_SUCCESS=true

# 安装Chronicle系统依赖
echo "1️⃣ 安装Chronicle系统依赖..."
if [ -d "systems/chronicle" ]; then
    cd systems/chronicle
    if npm install; then
        echo "✅ Chronicle依赖安装成功 (~116MB)"
    else
        echo "❌ Chronicle依赖安装失败"
        INSTALL_SUCCESS=false
    fi
    cd ../..
else
    echo "⚠️  Chronicle系统目录不存在，跳过"
fi
echo ""

# 安装Changlee系统依赖
echo "2️⃣ 安装Changlee系统依赖..."
if [ -d "systems/Changlee" ]; then
    cd systems/Changlee
    if npm install; then
        echo "✅ Changlee依赖安装成功 (~558MB)"
    else
        echo "❌ Changlee依赖安装失败"
        INSTALL_SUCCESS=false
    fi
    cd ../..
else
    echo "⚠️  Changlee系统目录不存在，跳过"
fi
echo ""

# 安装NEXUS系统依赖
echo "3️⃣ 安装NEXUS系统依赖..."
if [ -d "systems/nexus" ]; then
    cd systems/nexus
    if npm install; then
        echo "✅ NEXUS依赖安装成功 (~918MB)"
    else
        echo "❌ NEXUS依赖安装失败"
        INSTALL_SUCCESS=false
    fi
    cd ../..
else
    echo "⚠️  NEXUS系统目录不存在，跳过"
fi
echo ""

# 验证安装
echo "🔍 验证安装结果..."
echo ""

if [ -d "systems/chronicle/node_modules" ]; then
    echo "✅ Chronicle: $(du -sh systems/chronicle/node_modules | cut -f1)"
    cd systems/chronicle
    if node chronicle.js --help > /dev/null 2>&1; then
        echo "   📋 功能测试: 通过"
    else
        echo "   📋 功能测试: 失败"
    fi
    cd ../..
fi

if [ -d "systems/Changlee/node_modules" ]; then
    echo "✅ Changlee: $(du -sh systems/Changlee/node_modules | cut -f1)"
    cd systems/Changlee
    if node changlee.js --help > /dev/null 2>&1; then
        echo "   📋 功能测试: 通过"
    else
        echo "   📋 功能测试: 失败"
    fi
    cd ../..
fi

if [ -d "systems/nexus/node_modules" ]; then
    echo "✅ NEXUS: $(du -sh systems/nexus/node_modules | cut -f1)"
    cd systems/nexus
    if [ -f "package.json" ]; then
        echo "   📋 配置文件: 存在"
    else
        echo "   📋 配置文件: 缺失"
    fi
    cd ../..
fi

echo ""

# 安装总结
if [ "$INSTALL_SUCCESS" = true ]; then
    echo "🎉 Node.js依赖安装完成！"
    echo ""
    echo "📊 安装统计:"
    echo "  💾 总大小: $(du -sh systems/*/node_modules 2>/dev/null | awk '{sum+=$1} END {print sum "B"}' || echo '~1.6GB')"
    echo "  📦 系统数: $(ls -d systems/*/node_modules 2>/dev/null | wc -l)/3"
    echo ""
    echo "🚀 快速启动:"
    echo "  📚 Chronicle: cd systems/chronicle && node chronicle.js server"
    echo "  🎵 Changlee: cd systems/Changlee && node changlee.js server"
    echo "  🌐 NEXUS: cd systems/nexus && npm run dev"
    echo ""
    echo "📖 更多信息请查看README.md"
else
    echo "❌ 部分依赖安装失败"
    echo ""
    echo "🛠️ 故障排除:"
    echo "  1. 检查网络连接"
    echo "  2. 清理npm缓存: npm cache clean --force"
    echo "  3. 检查磁盘空间"
    echo "  4. 查看详细错误信息重新运行"
    echo ""
    echo "📞 如需帮助，请查看requirements.txt中的常见问题解决方案"
fi