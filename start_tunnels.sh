#!/bin/bash

# NEXUS AI 系统自动隧道启动脚本
# 作者: Kepilot AI Assistant
# 功能: 自动启动隧道、更新配置、启动服务

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 项目路径
PROJECT_DIR="/workspace/N.S.S-Novena-Garfield"
FRONTEND_DIR="$PROJECT_DIR/systems/nexus"
CLOUDFLARED_PATH="$FRONTEND_DIR/cloudflared"

# 日志文件
API_TUNNEL_LOG="/tmp/api_tunnel.log"
FRONTEND_TUNNEL_LOG="/tmp/frontend_tunnel.log"
RAG_API_LOG="$PROJECT_DIR/rag_api.log"

echo -e "${CYAN}🚀 === NEXUS AI 隧道启动脚本 === 🚀${NC}"
echo ""

# 函数：打印带时间戳的日志
log() {
    echo -e "${BLUE}[$(date '+%H:%M:%S')]${NC} $1"
}

# 函数：打印成功信息
success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# 函数：打印警告信息
warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# 函数：打印错误信息
error() {
    echo -e "${RED}❌ $1${NC}"
}

# 函数：停止现有服务
stop_services() {
    log "停止现有服务..."
    
    # 停止cloudflared隧道
    pkill -f "cloudflared.*tunnel" 2>/dev/null || true
    
    # 停止RAG API服务
    pkill -f "online_rag_api.py" 2>/dev/null || true
    
    # 停止前端服务
    pkill -f "python.*-m.*http.server.*52943" 2>/dev/null || true
    
    sleep 2
    success "现有服务已停止"
}

# 函数：启动API隧道
start_api_tunnel() {
    log "启动RAG API隧道..."
    
    # 清理旧日志
    > "$API_TUNNEL_LOG"
    
    # 启动隧道
    cd "$FRONTEND_DIR"
    ./cloudflared tunnel --url http://localhost:5000 > "$API_TUNNEL_LOG" 2>&1 &
    
    # 等待隧道启动
    local max_wait=30
    local count=0
    
    while [ $count -lt $max_wait ]; do
        if grep -q "https://.*\.trycloudflare\.com" "$API_TUNNEL_LOG" 2>/dev/null; then
            break
        fi
        sleep 1
        count=$((count + 1))
        echo -n "."
    done
    echo ""
    
    if [ $count -eq $max_wait ]; then
        error "API隧道启动超时"
        return 1
    fi
    
    # 提取隧道URL
    API_TUNNEL_URL=$(grep -o "https://[^[:space:]]*\.trycloudflare\.com" "$API_TUNNEL_LOG" | head -1)
    
    if [ -z "$API_TUNNEL_URL" ]; then
        error "无法获取API隧道URL"
        return 1
    fi
    
    success "API隧道已启动: $API_TUNNEL_URL"
    echo "$API_TUNNEL_URL" > /tmp/current_api_url.txt
}

# 函数：启动前端隧道
start_frontend_tunnel() {
    log "启动前端隧道..."
    
    # 清理旧日志
    > "$FRONTEND_TUNNEL_LOG"
    
    # 启动隧道
    cd "$FRONTEND_DIR"
    ./cloudflared tunnel --url http://localhost:52943 > "$FRONTEND_TUNNEL_LOG" 2>&1 &
    
    # 等待隧道启动
    local max_wait=30
    local count=0
    
    while [ $count -lt $max_wait ]; do
        if grep -q "https://.*\.trycloudflare\.com" "$FRONTEND_TUNNEL_LOG" 2>/dev/null; then
            break
        fi
        sleep 1
        count=$((count + 1))
        echo -n "."
    done
    echo ""
    
    if [ $count -eq $max_wait ]; then
        error "前端隧道启动超时"
        return 1
    fi
    
    # 提取隧道URL
    FRONTEND_TUNNEL_URL=$(grep -o "https://[^[:space:]]*\.trycloudflare\.com" "$FRONTEND_TUNNEL_LOG" | head -1)
    
    if [ -z "$FRONTEND_TUNNEL_URL" ]; then
        error "无法获取前端隧道URL"
        return 1
    fi
    
    success "前端隧道已启动: $FRONTEND_TUNNEL_URL"
    echo "$FRONTEND_TUNNEL_URL" > /tmp/current_frontend_url.txt
}

# 函数：更新前端配置
update_frontend_config() {
    log "更新前端配置..."
    
    local api_url="$1"
    local config_file="$FRONTEND_DIR/index.html"
    
    # 备份原配置
    cp "$config_file" "$config_file.backup.$(date +%s)"
    
    # 查找并替换API URL
    # 使用sed替换主要API URL
    sed -i "s|return 'https://[^']*\.trycloudflare\.com';|return '$api_url';|g" "$config_file"
    
    # 替换fallbackURLs中的第一个URL
    sed -i "0,/https:\/\/[^']*\.trycloudflare\.com/{s|https://[^']*\.trycloudflare\.com|$api_url|}" "$config_file"
    
    # 更新meta标签中的API URL
    sed -i "s|<meta name=\"api-url\" content=\"https://[^\"]*\.trycloudflare\.com\">|<meta name=\"api-url\" content=\"$api_url\">|g" "$config_file"
    
    success "前端配置已更新"
}

# 函数：启动RAG API服务
start_rag_api() {
    log "启动RAG API服务..."
    
    cd "$PROJECT_DIR"
    python online_rag_api.py > "$RAG_API_LOG" 2>&1 &
    
    # 等待服务启动
    local max_wait=15
    local count=0
    
    while [ $count -lt $max_wait ]; do
        if curl -s http://localhost:5000/api/health >/dev/null 2>&1; then
            break
        fi
        sleep 1
        count=$((count + 1))
        echo -n "."
    done
    echo ""
    
    if [ $count -eq $max_wait ]; then
        error "RAG API服务启动失败"
        return 1
    fi
    
    success "RAG API服务已启动"
}

# 函数：启动前端服务
start_frontend_service() {
    log "启动前端服务..."
    
    cd "$FRONTEND_DIR"
    python -m http.server 52943 > /dev/null 2>&1 &
    
    sleep 3
    success "前端服务已启动"
}

# 函数：健康检查
health_check() {
    log "执行健康检查..."
    
    local api_url="$1"
    local frontend_url="$2"
    
    # 检查API服务
    if curl -s "$api_url/api/health" | grep -q '"status":"ok"'; then
        success "API服务健康检查通过"
    else
        error "API服务健康检查失败"
        return 1
    fi
    
    # 检查前端服务
    if curl -s "$frontend_url" | grep -q "NEXUS AI" >/dev/null 2>&1; then
        success "前端服务健康检查通过"
    else
        warning "前端服务可能需要几秒钟才能完全启动"
    fi
    
    return 0
}

# 函数：显示最终状态
show_final_status() {
    local api_url="$1"
    local frontend_url="$2"
    
    echo ""
    echo -e "${PURPLE}🎉 === 启动完成！=== 🎉${NC}"
    echo ""
    echo -e "${CYAN}📱 前端界面:${NC} $frontend_url"
    echo -e "${CYAN}🤖 RAG API:${NC} $api_url"
    echo ""
    echo -e "${GREEN}✅ 所有服务已启动并运行正常${NC}"
    echo ""
    echo -e "${YELLOW}💡 使用提示:${NC}"
    echo "   1. 访问前端界面开始使用"
    echo "   2. 上传文档文件进行RAG问答"
    echo "   3. 享受智能对话体验"
    echo ""
    echo -e "${BLUE}📋 服务状态:${NC}"
    echo "   • API隧道: 运行中"
    echo "   • 前端隧道: 运行中"
    echo "   • RAG服务: 运行中"
    echo "   • 前端服务: 运行中"
    echo ""
    echo -e "${CYAN}🔧 如需重启服务，请重新运行此脚本${NC}"
}

# 主执行流程
main() {
    # 检查必要文件
    if [ ! -f "$CLOUDFLARED_PATH" ]; then
        error "cloudflared 未找到: $CLOUDFLARED_PATH"
        exit 1
    fi
    
    if [ ! -f "$PROJECT_DIR/online_rag_api.py" ]; then
        error "RAG API 文件未找到: $PROJECT_DIR/online_rag_api.py"
        exit 1
    fi
    
    # 执行启动流程
    stop_services
    
    start_api_tunnel
    API_URL=$(cat /tmp/current_api_url.txt)
    
    start_frontend_tunnel  
    FRONTEND_URL=$(cat /tmp/current_frontend_url.txt)
    
    update_frontend_config "$API_URL"
    
    start_rag_api
    
    start_frontend_service
    
    # 等待服务完全启动
    sleep 5
    
    health_check "$API_URL" "$FRONTEND_URL"
    
    show_final_status "$API_URL" "$FRONTEND_URL"
    
    # 保存当前配置供后续使用
    cat > /tmp/nexus_current_config.txt << EOF
API_URL=$API_URL
FRONTEND_URL=$FRONTEND_URL
STARTED_AT="$(date)"
EOF
}

# 捕获中断信号
trap 'echo -e "\n${RED}脚本被中断${NC}"; exit 1' INT TERM

# 执行主函数
main "$@"