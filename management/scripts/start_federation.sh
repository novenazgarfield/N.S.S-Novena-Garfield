#!/bin/bash

# 🏥 Chronicle联邦启动脚本
# ================================
# 
# 启动Chronicle联邦系统 (Docker版本)
# - Chronicle中央医院
# - RAG智能系统
# - 性能监控
#
# Author: N.S.S-Novena-Garfield Project
# Version: 2.0.0 - "Chronicle Federation Docker"

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
DOCKER_COMPOSE_FILE="$PROJECT_ROOT/management/config/docker-compose.yml"

echo -e "${CYAN}🏥 Chronicle联邦启动脚本${NC}"
echo -e "${CYAN}================================${NC}"
echo ""

# 检查Docker是否安装
check_docker() {
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker未安装，请先安装Docker${NC}"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        echo -e "${RED}❌ Docker Compose未安装，请先安装Docker Compose${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Docker环境检查通过${NC}"
}

# 检查端口是否被占用
check_ports() {
    local ports=(3000 8501)
    local occupied_ports=()
    
    for port in "${ports[@]}"; do
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
            occupied_ports+=($port)
        fi
    done
    
    if [ ${#occupied_ports[@]} -gt 0 ]; then
        echo -e "${YELLOW}⚠️ 以下端口被占用: ${occupied_ports[*]}${NC}"
        echo -e "${YELLOW}   请停止相关服务或使用不同端口${NC}"
        read -p "是否继续启动? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    else
        echo -e "${GREEN}✅ 端口检查通过${NC}"
    fi
}

# 构建Docker镜像
build_images() {
    echo -e "${BLUE}🔨 构建Docker镜像...${NC}"
    
    cd "$PROJECT_ROOT"
    
    # 构建Chronicle镜像
    echo -e "${BLUE}   构建Chronicle中央医院镜像...${NC}"
    docker build -t chronicle-hospital:latest systems/chronicle/
    
    # 构建RAG系统镜像
    echo -e "${BLUE}   构建RAG智能系统镜像...${NC}"
    docker build -t rag-intelligence:latest systems/rag-system/
    
    echo -e "${GREEN}✅ Docker镜像构建完成${NC}"
}

# 启动服务
start_services() {
    echo -e "${BLUE}🚀 启动Chronicle联邦服务...${NC}"
    
    cd "$PROJECT_ROOT"
    docker-compose -f "$DOCKER_COMPOSE_FILE" up -d
    
    echo -e "${GREEN}✅ 服务启动完成${NC}"
}

# 等待服务就绪
wait_for_services() {
    echo -e "${YELLOW}⏳ 等待服务就绪...${NC}"
    
    # 等待Chronicle服务
    echo -e "${YELLOW}   等待Chronicle中央医院...${NC}"
    timeout=60
    while [ $timeout -gt 0 ]; do
        if curl -f http://localhost:3000/health >/dev/null 2>&1; then
            echo -e "${GREEN}   ✅ Chronicle中央医院已就绪${NC}"
            break
        fi
        sleep 2
        ((timeout-=2))
    done
    
    if [ $timeout -le 0 ]; then
        echo -e "${RED}   ❌ Chronicle中央医院启动超时${NC}"
        return 1
    fi
    
    # 等待RAG系统
    echo -e "${YELLOW}   等待RAG智能系统...${NC}"
    timeout=90
    while [ $timeout -gt 0 ]; do
        if curl -f http://localhost:8501/_stcore/health >/dev/null 2>&1; then
            echo -e "${GREEN}   ✅ RAG智能系统已就绪${NC}"
            break
        fi
        sleep 3
        ((timeout-=3))
    done
    
    if [ $timeout -le 0 ]; then
        echo -e "${RED}   ❌ RAG智能系统启动超时${NC}"
        return 1
    fi
    
    echo -e "${GREEN}✅ 所有服务已就绪${NC}"
}

# 显示服务状态
show_status() {
    echo ""
    echo -e "${CYAN}📊 Chronicle联邦服务状态${NC}"
    echo -e "${CYAN}========================${NC}"
    
    docker-compose -f "$DOCKER_COMPOSE_FILE" ps
    
    echo ""
    echo -e "${GREEN}🌐 服务访问地址:${NC}"
    echo -e "${GREEN}   Chronicle中央医院: http://localhost:3000${NC}"
    echo -e "${GREEN}   RAG智能系统:      http://localhost:8501${NC}"
    echo ""
    echo -e "${PURPLE}🔗 联邦连接测试:${NC}"
    echo -e "${PURPLE}   python management/tests/test_chronicle_federation.py${NC}"
}

# 运行联邦测试
run_tests() {
    echo -e "${BLUE}🧪 运行Chronicle联邦测试...${NC}"
    
    cd "$PROJECT_ROOT"
    if [ -f "management/tests/test_chronicle_federation.py" ]; then
        python management/tests/test_chronicle_federation.py
    else
        echo -e "${YELLOW}⚠️ 测试文件未找到${NC}"
    fi
}

# 主函数
main() {
    case "${1:-start}" in
        "start")
            check_docker
            check_ports
            build_images
            start_services
            wait_for_services
            show_status
            ;;
        "stop")
            echo -e "${YELLOW}⏹️ 停止Chronicle联邦服务...${NC}"
            docker-compose -f "$DOCKER_COMPOSE_FILE" down
            echo -e "${GREEN}✅ 服务已停止${NC}"
            ;;
        "restart")
            echo -e "${YELLOW}🔄 重启Chronicle联邦服务...${NC}"
            docker-compose -f "$DOCKER_COMPOSE_FILE" down
            sleep 2
            main start
            ;;
        "status")
            show_status
            ;;
        "logs")
            docker-compose -f "$DOCKER_COMPOSE_FILE" logs -f
            ;;
        "test")
            run_tests
            ;;
        "build")
            check_docker
            build_images
            ;;
        "help"|*)
            echo -e "${CYAN}Chronicle联邦启动脚本使用说明:${NC}"
            echo ""
            echo -e "${GREEN}命令:${NC}"
            echo -e "  start    启动Chronicle联邦服务 (默认)"
            echo -e "  stop     停止Chronicle联邦服务"
            echo -e "  restart  重启Chronicle联邦服务"
            echo -e "  status   查看服务状态"
            echo -e "  logs     查看服务日志"
            echo -e "  test     运行联邦测试"
            echo -e "  build    构建Docker镜像"
            echo -e "  help     显示此帮助信息"
            echo ""
            echo -e "${YELLOW}示例:${NC}"
            echo -e "  ./start_federation.sh start"
            echo -e "  ./start_federation.sh stop"
            echo -e "  ./start_federation.sh logs"
            ;;
    esac
}

# 执行主函数
main "$@"