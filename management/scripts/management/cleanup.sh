#!/bin/bash

# 项目清理脚本
# Project Cleanup Script

echo "🧹 === N.S.S Novena Garfield 项目清理脚本 === 🧹"
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 获取项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

echo -e "${BLUE}📂 项目根目录: $PROJECT_ROOT${NC}"
echo ""

# 清理函数
cleanup_python_cache() {
    echo -e "${YELLOW}🐍 清理Python缓存文件...${NC}"
    
    # 查找并删除 __pycache__ 目录
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    
    # 查找并删除 .pyc 文件
    find . -name "*.pyc" -delete 2>/dev/null || true
    find . -name "*.pyo" -delete 2>/dev/null || true
    
    echo -e "${GREEN}✅ Python缓存清理完成${NC}"
}

cleanup_browser_screenshots() {
    echo -e "${YELLOW}📸 清理浏览器截图...${NC}"
    
    local screenshot_dir="./temp/browser_screenshots"
    
    if [ -d "$screenshot_dir" ]; then
        local count=$(find "$screenshot_dir" -name "*.png" | wc -l)
        if [ "$count" -gt 0 ]; then
            echo -e "${BLUE}   发现 $count 个截图文件${NC}"
            
            # 保留最新的10个截图，删除其余的
            find "$screenshot_dir" -name "*.png" -type f -printf '%T@ %p\n' | \
            sort -rn | \
            tail -n +11 | \
            cut -d' ' -f2- | \
            xargs -r rm -f
            
            local remaining=$(find "$screenshot_dir" -name "*.png" | wc -l)
            echo -e "${GREEN}✅ 保留最新的 $remaining 个截图文件${NC}"
        else
            echo -e "${GREEN}✅ 没有找到截图文件${NC}"
        fi
    else
        echo -e "${GREEN}✅ 截图目录不存在${NC}"
    fi
}

cleanup_logs() {
    echo -e "${YELLOW}📝 清理日志文件...${NC}"
    
    # 清理大于10MB的日志文件
    find . -name "*.log" -size +10M -exec rm -f {} + 2>/dev/null || true
    
    # 清理超过7天的日志文件
    find ./logs -name "*.log" -mtime +7 -delete 2>/dev/null || true
    
    echo -e "${GREEN}✅ 日志文件清理完成${NC}"
}

cleanup_temp_files() {
    echo -e "${YELLOW}🗂️ 清理临时文件...${NC}"
    
    # 清理临时目录中的旧文件
    find ./temp -name "*.tmp" -mtime +1 -delete 2>/dev/null || true
    find ./temp -name "*.cache" -mtime +1 -delete 2>/dev/null || true
    
    echo -e "${GREEN}✅ 临时文件清理完成${NC}"
}

cleanup_node_modules() {
    echo -e "${YELLOW}📦 检查Node.js模块...${NC}"
    
    if [ -d "node_modules" ]; then
        local size=$(du -sh node_modules 2>/dev/null | cut -f1)
        echo -e "${BLUE}   node_modules 大小: $size${NC}"
        echo -e "${YELLOW}   如需清理，请手动运行: rm -rf node_modules && npm install${NC}"
    else
        echo -e "${GREEN}✅ 没有找到node_modules目录${NC}"
    fi
}

show_disk_usage() {
    echo -e "${YELLOW}💾 磁盘使用情况:${NC}"
    echo ""
    
    # 显示项目总大小
    local total_size=$(du -sh . 2>/dev/null | cut -f1)
    echo -e "${BLUE}📊 项目总大小: $total_size${NC}"
    
    # 显示各个主要目录的大小
    echo -e "${BLUE}📁 主要目录大小:${NC}"
    for dir in systems data logs temp tools docs; do
        if [ -d "$dir" ]; then
            local dir_size=$(du -sh "$dir" 2>/dev/null | cut -f1)
            echo -e "   $dir: $dir_size"
        fi
    done
    echo ""
}

# 主菜单
show_menu() {
    echo -e "${BLUE}请选择清理选项:${NC}"
    echo "1) 清理Python缓存 (__pycache__, *.pyc)"
    echo "2) 清理浏览器截图"
    echo "3) 清理日志文件"
    echo "4) 清理临时文件"
    echo "5) 检查Node.js模块"
    echo "6) 显示磁盘使用情况"
    echo "7) 全部清理 (1-4)"
    echo "8) 退出"
    echo ""
    echo -n "请输入选项 (1-8): "
}

# 主循环
while true; do
    show_menu
    read -r choice
    echo ""
    
    case $choice in
        1)
            cleanup_python_cache
            ;;
        2)
            cleanup_browser_screenshots
            ;;
        3)
            cleanup_logs
            ;;
        4)
            cleanup_temp_files
            ;;
        5)
            cleanup_node_modules
            ;;
        6)
            show_disk_usage
            ;;
        7)
            echo -e "${YELLOW}🚀 执行全部清理...${NC}"
            cleanup_python_cache
            cleanup_browser_screenshots
            cleanup_logs
            cleanup_temp_files
            echo -e "${GREEN}🎉 全部清理完成！${NC}"
            ;;
        8)
            echo -e "${GREEN}👋 清理脚本退出${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}❌ 无效选项，请重新选择${NC}"
            ;;
    esac
    
    echo ""
    echo -e "${BLUE}按回车键继续...${NC}"
    read -r
    echo ""
done