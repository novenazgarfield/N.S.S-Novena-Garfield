#!/bin/bash

# NEXUS Research Workstation 一键部署脚本 (Linux/macOS)
# 支持用户交互和自动化部署

set -e  # 遇到错误立即退出

# 默认参数
INSTALL_PATH=""
GITHUB_TOKEN=""
SILENT=false
HELP=false

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# 输出函数
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${CYAN}ℹ️  $1${NC}"
}

print_header() {
    echo -e "${MAGENTA}$1${NC}"
}

# 显示帮助信息
show_help() {
    cat << EOF
NEXUS Research Workstation 一键部署脚本

用法:
    ./deploy_nexus.sh [选项]

选项:
    -p, --path <路径>      指定安装路径 (默认: ~/nexus)
    -t, --token <令牌>     GitHub个人访问令牌
    -s, --silent          静默模式，不显示交互提示
    -h, --help            显示此帮助信息

示例:
    ./deploy_nexus.sh
    ./deploy_nexus.sh -p "/opt/nexus" -t "ghp_xxxx"
    ./deploy_nexus.sh --silent

EOF
}

# 解析命令行参数
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -p|--path)
                INSTALL_PATH="$2"
                shift 2
                ;;
            -t|--token)
                GITHUB_TOKEN="$2"
                shift 2
                ;;
            -s|--silent)
                SILENT=true
                shift
                ;;
            -h|--help)
                HELP=true
                shift
                ;;
            *)
                print_error "未知参数: $1"
                show_help
                exit 1
                ;;
        esac
    done
}

# 检查操作系统
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
        if command -v apt-get &> /dev/null; then
            PACKAGE_MANAGER="apt"
        elif command -v yum &> /dev/null; then
            PACKAGE_MANAGER="yum"
        elif command -v pacman &> /dev/null; then
            PACKAGE_MANAGER="pacman"
        else
            print_error "不支持的Linux发行版"
            exit 1
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        PACKAGE_MANAGER="brew"
    else
        print_error "不支持的操作系统: $OSTYPE"
        exit 1
    fi
    
    print_info "检测到操作系统: $OS"
    print_info "包管理器: $PACKAGE_MANAGER"
}

# 检查依赖项
check_dependency() {
    local cmd=$1
    local name=$2
    
    if command -v "$cmd" &> /dev/null; then
        print_success "$name 已安装"
        return 0
    else
        print_warning "$name 未安装"
        return 1
    fi
}

# 安装依赖项
install_dependency() {
    local name=$1
    local package=$2
    
    print_info "正在安装 $name..."
    
    case $PACKAGE_MANAGER in
        apt)
            sudo apt-get update -qq
            sudo apt-get install -y "$package"
            ;;
        yum)
            sudo yum install -y "$package"
            ;;
        pacman)
            sudo pacman -S --noconfirm "$package"
            ;;
        brew)
            if ! command -v brew &> /dev/null; then
                print_info "正在安装 Homebrew..."
                /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
            fi
            brew install "$package"
            ;;
        *)
            print_error "不支持的包管理器: $PACKAGE_MANAGER"
            return 1
            ;;
    esac
    
    if [[ $? -eq 0 ]]; then
        print_success "$name 安装成功"
        return 0
    else
        print_error "$name 安装失败"
        return 1
    fi
}

# 安装Node.js (使用NodeSource)
install_nodejs() {
    print_info "正在安装 Node.js..."
    
    if [[ "$OS" == "linux" ]]; then
        curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
        sudo apt-get install -y nodejs
    elif [[ "$OS" == "macos" ]]; then
        brew install node
    fi
    
    if command -v node &> /dev/null; then
        print_success "Node.js 安装成功 ($(node --version))"
        return 0
    else
        print_error "Node.js 安装失败"
        return 1
    fi
}

# 安装Python
install_python() {
    print_info "正在安装 Python..."
    
    case $PACKAGE_MANAGER in
        apt)
            sudo apt-get install -y python3 python3-pip python3-venv
            ;;
        yum)
            sudo yum install -y python3 python3-pip
            ;;
        pacman)
            sudo pacman -S --noconfirm python python-pip
            ;;
        brew)
            brew install python@3.11
            ;;
    esac
    
    if command -v python3 &> /dev/null; then
        print_success "Python 安装成功 ($(python3 --version))"
        return 0
    else
        print_error "Python 安装失败"
        return 1
    fi
}

# 克隆代码库
clone_repository() {
    local repo_url=$1
    local target_path=$2
    local token=$3
    
    print_info "正在克隆代码库到 $target_path..."
    
    # 如果提供了令牌，修改URL
    if [[ -n "$token" ]]; then
        repo_url=$(echo "$repo_url" | sed "s|https://github.com/|https://$token@github.com/|")
    fi
    
    if [[ -d "$target_path" ]]; then
        print_warning "目标目录已存在，正在更新..."
        cd "$target_path"
        git pull
    else
        git clone "$repo_url" "$target_path"
    fi
    
    if [[ $? -eq 0 ]]; then
        print_success "代码库克隆/更新成功"
        return 0
    else
        print_error "代码库克隆/更新失败"
        return 1
    fi
}

# 安装Node.js依赖
install_node_dependencies() {
    local path=$1
    
    print_info "正在安装Node.js依赖..."
    
    cd "$path"
    npm install
    
    if [[ $? -eq 0 ]]; then
        print_success "Node.js依赖安装成功"
        return 0
    else
        print_error "Node.js依赖安装失败"
        return 1
    fi
}

# 安装Python依赖
install_python_dependencies() {
    local path=$1
    
    print_info "正在安装Python依赖..."
    
    cd "$path"
    
    # 检查是否有requirements.txt
    if [[ -f "requirements.txt" ]]; then
        pip3 install -r requirements.txt
    fi
    
    # 检查是否有backend的requirements.txt
    if [[ -f "backend/requirements.txt" ]]; then
        pip3 install -r backend/requirements.txt
    fi
    
    if [[ $? -eq 0 ]]; then
        print_success "Python依赖安装成功"
        return 0
    else
        print_error "Python依赖安装失败"
        return 1
    fi
}

# 创建启动脚本
create_launch_script() {
    local install_path=$1
    local script_path="$install_path/launch_nexus.sh"
    
    cat > "$script_path" << EOF
#!/bin/bash

# NEXUS 启动脚本
cd "$install_path/systems/nexus"

echo "🚀 启动 NEXUS Research Workstation..."

# 启动后端WebSocket服务器
cd backend
python3 websocket_server.py &
BACKEND_PID=\$!

# 等待后端启动
sleep 3

# 启动前端开发服务器
cd ..
npm run dev &
FRONTEND_PID=\$!

echo "✅ NEXUS 启动完成!"
echo "📱 前端界面: http://localhost:5173"
echo "🔌 WebSocket服务: ws://localhost:8765"
echo "🌐 测试页面: http://localhost:52333/test_remote_center.html"

# 等待用户输入
echo "按 Ctrl+C 停止服务"
trap 'kill \$BACKEND_PID \$FRONTEND_PID; exit' INT
wait
EOF

    chmod +x "$script_path"
    
    if [[ $? -eq 0 ]]; then
        print_success "启动脚本创建成功: $script_path"
        return 0
    else
        print_error "启动脚本创建失败"
        return 1
    fi
}

# 创建桌面快捷方式 (Linux)
create_desktop_shortcut_linux() {
    local install_path=$1
    local script_path="$install_path/launch_nexus.sh"
    local desktop_file="$HOME/Desktop/nexus-research-workstation.desktop"
    
    cat > "$desktop_file" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=NEXUS Research Workstation
Comment=远程指挥与控制系统
Exec=gnome-terminal -- bash -c "$script_path; exec bash"
Icon=$install_path/systems/nexus/public/vite.svg
Terminal=false
Categories=Development;Science;
EOF

    chmod +x "$desktop_file"
    
    if [[ $? -eq 0 ]]; then
        print_success "桌面快捷方式创建成功"
        return 0
    else
        print_error "桌面快捷方式创建失败"
        return 1
    fi
}

# 创建macOS应用程序快捷方式
create_app_shortcut_macos() {
    local install_path=$1
    local script_path="$install_path/launch_nexus.sh"
    local app_path="$HOME/Applications/NEXUS Research Workstation.app"
    
    mkdir -p "$app_path/Contents/MacOS"
    mkdir -p "$app_path/Contents/Resources"
    
    # 创建Info.plist
    cat > "$app_path/Contents/Info.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>launch</string>
    <key>CFBundleIdentifier</key>
    <string>com.nexus.research-workstation</string>
    <key>CFBundleName</key>
    <string>NEXUS Research Workstation</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
</dict>
</plist>
EOF

    # 创建启动脚本
    cat > "$app_path/Contents/MacOS/launch" << EOF
#!/bin/bash
open -a Terminal "$script_path"
EOF

    chmod +x "$app_path/Contents/MacOS/launch"
    
    if [[ $? -eq 0 ]]; then
        print_success "应用程序快捷方式创建成功"
        return 0
    else
        print_error "应用程序快捷方式创建失败"
        return 1
    fi
}

# 主函数
main() {
    print_header "🚀 NEXUS Research Workstation 一键部署脚本"
    print_header "================================================"
    print_header "版本: 1.0.0"
    print_header "平台: Linux/macOS Bash"
    print_header "================================================"
    
    # 检查操作系统
    detect_os
    
    # 获取用户输入
    if [[ "$SILENT" != true ]]; then
        if [[ -z "$INSTALL_PATH" ]]; then
            read -p "请输入安装路径 (默认: ~/nexus): " INSTALL_PATH
            if [[ -z "$INSTALL_PATH" ]]; then
                INSTALL_PATH="$HOME/nexus"
            fi
        fi
        
        if [[ -z "$GITHUB_TOKEN" ]]; then
            print_info "GitHub个人访问令牌用于访问私有仓库"
            print_info "如果仓库是公开的，可以直接按回车跳过"
            read -p "请输入GitHub个人访问令牌 (可选): " GITHUB_TOKEN
        fi
    else
        if [[ -z "$INSTALL_PATH" ]]; then
            INSTALL_PATH="$HOME/nexus"
        fi
    fi
    
    print_info "安装路径: $INSTALL_PATH"
    print_info "GitHub令牌: $(if [[ -n "$GITHUB_TOKEN" ]]; then echo '已提供'; else echo '未提供'; fi)"
    
    # 创建安装目录
    mkdir -p "$INSTALL_PATH"
    print_success "创建安装目录: $INSTALL_PATH"
    
    # 检查和安装依赖项
    print_info "检查系统依赖项..."
    
    missing_deps=()
    
    if ! check_dependency "git" "Git"; then
        missing_deps+=("git")
    fi
    
    if ! check_dependency "node" "Node.js"; then
        missing_deps+=("nodejs")
    fi
    
    if ! check_dependency "python3" "Python"; then
        missing_deps+=("python")
    fi
    
    # 安装缺失的依赖项
    if [[ ${#missing_deps[@]} -gt 0 ]]; then
        print_info "需要安装以下依赖项:"
        for dep in "${missing_deps[@]}"; do
            echo "  - $dep"
        done
        
        if [[ "$SILENT" != true ]]; then
            read -p "是否继续安装? (y/N): " confirm
            if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
                print_warning "用户取消安装"
                exit 0
            fi
        fi
        
        for dep in "${missing_deps[@]}"; do
            case $dep in
                git)
                    install_dependency "Git" "git" || exit 1
                    ;;
                nodejs)
                    install_nodejs || exit 1
                    ;;
                python)
                    install_python || exit 1
                    ;;
            esac
        done
    fi
    
    # 克隆代码库
    repo_url="https://github.com/novenazgarfield/research-workstation.git"
    clone_repository "$repo_url" "$INSTALL_PATH" "$GITHUB_TOKEN" || exit 1
    
    # 切换到NEXUS目录
    nexus_path="$INSTALL_PATH/systems/nexus"
    if [[ ! -d "$nexus_path" ]]; then
        print_error "NEXUS目录不存在: $nexus_path"
        exit 1
    fi
    
    # 安装Node.js依赖
    install_node_dependencies "$nexus_path" || exit 1
    
    # 安装Python依赖
    install_python_dependencies "$nexus_path" || print_warning "Python依赖安装失败，但继续执行"
    
    # 创建启动脚本
    create_launch_script "$INSTALL_PATH" || print_warning "启动脚本创建失败"
    
    # 创建快捷方式
    if [[ "$OS" == "linux" ]]; then
        create_desktop_shortcut_linux "$INSTALL_PATH" || print_warning "桌面快捷方式创建失败"
    elif [[ "$OS" == "macos" ]]; then
        create_app_shortcut_macos "$INSTALL_PATH" || print_warning "应用程序快捷方式创建失败"
    fi
    
    # 完成安装
    print_header ""
    print_header "🎉 NEXUS Research Workstation 安装完成!"
    print_header "========================================"
    print_header ""
    print_success "📁 安装路径: $INSTALL_PATH"
    print_success "🚀 启动脚本: $INSTALL_PATH/launch_nexus.sh"
    print_success "🖥️  快捷方式: 已创建"
    print_header ""
    print_info "📱 访问地址:"
    print_info "   - 主界面: http://localhost:5173"
    print_info "   - 测试页面: http://localhost:52333/test_remote_center.html"
    print_info "   - WebSocket: ws://localhost:8765"
    print_header ""
    print_info "🔧 手动启动:"
    print_info "   bash $INSTALL_PATH/launch_nexus.sh"
    print_header ""
    print_info "📚 文档: $INSTALL_PATH/README.md"
    print_header ""
    
    if [[ "$SILENT" != true ]]; then
        read -p "是否立即启动NEXUS? (Y/n): " launch
        if [[ "$launch" != "n" && "$launch" != "N" ]]; then
            print_info "正在启动NEXUS..."
            bash "$INSTALL_PATH/launch_nexus.sh"
        fi
    fi
}

# 错误处理
trap 'print_error "脚本执行出错，行号: $LINENO"; exit 1' ERR

# 解析参数
parse_args "$@"

# 显示帮助
if [[ "$HELP" == true ]]; then
    show_help
    exit 0
fi

# 执行主函数
main