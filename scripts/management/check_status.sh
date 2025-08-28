#!/bin/bash

# NEXUS AI 系统状态检查脚本

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🔍 === NEXUS AI 系统状态检查 === 🔍${NC}"
echo ""

# 检查配置文件
if [ -f /tmp/nexus_current_config.txt ]; then
    source /tmp/nexus_current_config.txt
    echo -e "${GREEN}📋 当前配置:${NC}"
    echo "   API地址: $API_URL"
    echo "   前端地址: $FRONTEND_URL"
    echo "   启动时间: $STARTED_AT"
    echo ""
else
    echo -e "${YELLOW}⚠️  未找到配置文件，系统可能未启动${NC}"
    echo ""
fi

# 检查进程状态
echo -e "${BLUE}🔧 进程状态:${NC}"

# 检查cloudflared隧道
TUNNEL_COUNT=$(ps aux | grep -c "cloudflared.*tunnel" | grep -v grep || echo "0")
if [ "$TUNNEL_COUNT" -gt 0 ]; then
    echo -e "   隧道服务: ${GREEN}✅ 运行中 ($TUNNEL_COUNT 个)${NC}"
else
    echo -e "   隧道服务: ${RED}❌ 未运行${NC}"
fi

# 检查RAG API
if ps aux | grep -q "online_rag_api.py" | grep -v grep; then
    echo -e "   RAG API: ${GREEN}✅ 运行中${NC}"
else
    echo -e "   RAG API: ${RED}❌ 未运行${NC}"
fi

# 检查前端服务
if ps aux | grep -q "python.*http.server.*52943" | grep -v grep; then
    echo -e "   前端服务: ${GREEN}✅ 运行中${NC}"
else
    echo -e "   前端服务: ${RED}❌ 未运行${NC}"
fi

echo ""

# 网络连接测试
if [ ! -z "$API_URL" ]; then
    echo -e "${BLUE}🌐 网络连接测试:${NC}"
    
    # 测试API连接
    if curl -s "$API_URL/api/health" | grep -q '"status":"ok"'; then
        echo -e "   API连接: ${GREEN}✅ 正常${NC}"
        
        # 获取API状态
        API_STATS=$(curl -s "$API_URL/api/stats" | jq -r '"文档数: " + (.documents_count | tostring) + ", 向量数: " + (.vector_count | tostring)' 2>/dev/null || echo "无法获取统计信息")
        echo -e "   API状态: ${GREEN}$API_STATS${NC}"
    else
        echo -e "   API连接: ${RED}❌ 失败${NC}"
    fi
    
    # 测试前端连接
    if curl -s "$FRONTEND_URL" | grep -q "NEXUS AI" >/dev/null 2>&1; then
        echo -e "   前端连接: ${GREEN}✅ 正常${NC}"
    else
        echo -e "   前端连接: ${RED}❌ 失败${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  无法进行网络测试，未找到服务地址${NC}"
fi

echo ""

# 提供操作建议
echo -e "${BLUE}💡 操作建议:${NC}"
if [ "$TUNNEL_COUNT" -eq 0 ]; then
    echo "   • 运行 ./start_tunnels.sh 启动所有服务"
elif ! curl -s "$API_URL/api/health" >/dev/null 2>&1; then
    echo "   • 服务可能需要重启: ./start_tunnels.sh"
else
    echo "   • 系统运行正常，可以正常使用"
    echo "   • 前端地址: $FRONTEND_URL"
fi

echo ""