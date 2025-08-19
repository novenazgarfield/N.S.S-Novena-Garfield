#!/bin/bash

# 长离的学习胶囊 - 快速安装脚本
# 适用于 Linux 和 macOS

set -e

echo "🐱 欢迎使用长离的学习胶囊安装程序"
echo "========================================"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 检查系统要求
check_requirements() {
    log_info "检查系统要求..."
    
    # 检查操作系统
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
        log_info "检测到 Linux 系统"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        log_info "检测到 macOS 系统"
    else
        log_error "不支持的操作系统: $OSTYPE"
        exit 1
    fi
    
    # 检查 Node.js
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version)
        log_success "Node.js 已安装: $NODE_VERSION"
        
        # 检查版本
        NODE_MAJOR=$(echo $NODE_VERSION | cut -d'.' -f1 | sed 's/v//')
        if [ "$NODE_MAJOR" -lt 16 ]; then
            log_error "需要 Node.js 16 或更高版本，当前版本: $NODE_VERSION"
            exit 1
        fi
    else
        log_error "未找到 Node.js，请先安装 Node.js 16+"
        log_info "访问 https://nodejs.org 下载安装"
        exit 1
    fi
    
    # 检查 npm
    if command -v npm &> /dev/null; then
        NPM_VERSION=$(npm --version)
        log_success "npm 已安装: $NPM_VERSION"
    else
        log_error "未找到 npm"
        exit 1
    fi
    
    # 检查 Python (某些 native 模块需要)
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version)
        log_success "Python3 已安装: $PYTHON_VERSION"
    else
        log_warning "未找到 Python3，某些功能可能无法正常工作"
    fi
}

# 安装系统依赖
install_system_deps() {
    log_info "安装系统依赖..."
    
    if [[ "$OS" == "linux" ]]; then
        # 检查包管理器
        if command -v apt-get &> /dev/null; then
            log_info "使用 apt-get 安装依赖..."
            sudo apt-get update
            sudo apt-get install -y build-essential libnss3-dev libatk-bridge2.0-dev libdrm2 libxkbcommon-dev libxss1 libasound2-dev
        elif command -v yum &> /dev/null; then
            log_info "使用 yum 安装依赖..."
            sudo yum groupinstall -y "Development Tools"
            sudo yum install -y nss atk at-spi2-atk libdrm libxkbcommon libXScrnSaver alsa-lib
        else
            log_warning "未识别的包管理器，请手动安装构建工具"
        fi
    elif [[ "$OS" == "macos" ]]; then
        # 检查 Xcode Command Line Tools
        if ! xcode-select -p &> /dev/null; then
            log_info "安装 Xcode Command Line Tools..."
            xcode-select --install
        else
            log_success "Xcode Command Line Tools 已安装"
        fi
    fi
}

# 安装项目依赖
install_project_deps() {
    log_info "安装项目依赖..."
    
    # 安装主项目依赖
    log_info "安装主项目依赖..."
    npm install
    
    # 安装渲染进程依赖
    if [ -f "src/renderer/package.json" ]; then
        log_info "安装渲染进程依赖..."
        cd src/renderer
        npm install
        cd ../..
    fi
    
    log_success "项目依赖安装完成"
}

# 配置环境
setup_environment() {
    log_info "配置环境..."
    
    # 创建必要的目录
    mkdir -p database logs assets/sounds assets/images
    
    # 检查 Gemini API 密钥
    if [ -z "$GEMINI_API_KEY" ]; then
        log_warning "未设置 GEMINI_API_KEY 环境变量"
        echo -n "请输入你的 Gemini API 密钥 (可选，回车跳过): "
        read -r API_KEY
        
        if [ -n "$API_KEY" ]; then
            echo "GEMINI_API_KEY=$API_KEY" > .env
            log_success "API 密钥已保存到 .env 文件"
        else
            log_info "跳过 API 密钥配置，稍后可在设置中配置"
        fi
    else
        echo "GEMINI_API_KEY=$GEMINI_API_KEY" > .env
        log_success "使用环境变量中的 API 密钥"
    fi
    
    # 设置权限
    chmod +x start.js
    chmod +x test_system.js
    
    log_success "环境配置完成"
}

# 运行测试
run_tests() {
    log_info "运行系统测试..."
    
    if node test_system.js; then
        log_success "系统测试通过"
    else
        log_warning "系统测试失败，但安装可以继续"
    fi
}

# 创建桌面快捷方式
create_shortcuts() {
    log_info "创建快捷方式..."
    
    APP_DIR=$(pwd)
    
    if [[ "$OS" == "linux" ]]; then
        # 创建 .desktop 文件
        DESKTOP_FILE="$HOME/.local/share/applications/changlee-learning-capsule.desktop"
        cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Name=长离的学习胶囊
Comment=情感陪伴式桌面宠物英语学习应用
Exec=node $APP_DIR/start.js
Icon=$APP_DIR/assets/images/icon.png
Terminal=false
Type=Application
Categories=Education;
EOF
        chmod +x "$DESKTOP_FILE"
        log_success "已创建桌面快捷方式"
        
    elif [[ "$OS" == "macos" ]]; then
        # 创建 Automator 应用或 shell 脚本
        SCRIPT_FILE="$HOME/Desktop/长离的学习胶囊.command"
        cat > "$SCRIPT_FILE" << EOF
#!/bin/bash
cd "$APP_DIR"
node start.js
EOF
        chmod +x "$SCRIPT_FILE"
        log_success "已创建桌面快捷方式"
    fi
}

# 主安装流程
main() {
    log_info "开始安装长离的学习胶囊..."
    
    check_requirements
    install_system_deps
    install_project_deps
    setup_environment
    run_tests
    create_shortcuts
    
    echo ""
    log_success "🎉 安装完成！"
    echo ""
    echo "📚 使用方法:"
    echo "  • 启动应用: node start.js"
    echo "  • 运行测试: node test_system.js"
    echo "  • 查看文档: docs/DEVELOPMENT.md"
    echo ""
    echo "🐱 长离正在等待与你一起学习英语！"
    echo ""
    
    # 询问是否立即启动
    echo -n "是否现在启动应用？(y/N): "
    read -r START_NOW
    
    if [[ "$START_NOW" =~ ^[Yy]$ ]]; then
        log_info "启动长离的学习胶囊..."
        node start.js
    else
        log_info "稍后可以运行 'node start.js' 启动应用"
    fi
}

# 错误处理
trap 'log_error "安装过程中出现错误，请检查上面的错误信息"; exit 1' ERR

# 运行主函数
main "$@"