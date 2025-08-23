#!/bin/bash

# NEXUS 终极一键部署脚本
# 支持多个平台，自动选择最佳方案

echo "🚀 NEXUS 终极一键部署脚本"
echo "目标域名: N.S.S-Novena-Garfield"
echo "=================================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${CYAN}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 检查依赖
check_dependencies() {
    print_info "检查系统依赖..."
    
    # 检查 Node.js
    if command -v node &> /dev/null; then
        print_success "Node.js 已安装 ($(node --version))"
    else
        print_warning "Node.js 未安装，某些功能可能不可用"
    fi
    
    # 检查 npm
    if command -v npm &> /dev/null; then
        print_success "npm 已安装 ($(npm --version))"
    else
        print_warning "npm 未安装，无法使用 Surge.sh"
    fi
    
    # 检查 curl
    if command -v curl &> /dev/null; then
        print_success "curl 已安装"
    else
        print_error "curl 未安装，请先安装 curl"
        exit 1
    fi
}

# 方案1: Surge.sh 部署
deploy_surge() {
    print_info "方案1: 部署到 Surge.sh"
    
    if ! command -v npm &> /dev/null; then
        print_error "需要 npm 来安装 Surge"
        return 1
    fi
    
    # 安装 surge
    print_info "安装 Surge.sh..."
    npm install -g surge
    
    # 准备文件
    mkdir -p surge-deploy
    cp nexus-mini.html surge-deploy/index.html
    echo "nss-novena-garfield.surge.sh" > surge-deploy/CNAME
    
    cd surge-deploy
    print_info "部署到 Surge.sh..."
    print_warning "首次使用需要注册账号（免费，只需邮箱）"
    
    surge . nss-novena-garfield.surge.sh
    
    if [ $? -eq 0 ]; then
        print_success "部署成功！"
        print_success "🌐 访问地址: https://nss-novena-garfield.surge.sh"
        cd ..
        rm -rf surge-deploy
        return 0
    else
        print_error "Surge 部署失败"
        cd ..
        rm -rf surge-deploy
        return 1
    fi
}

# 方案2: 生成 Netlify 部署包
generate_netlify_package() {
    print_info "方案2: 生成 Netlify 部署包"
    
    mkdir -p netlify-deploy
    cp nexus-mini.html netlify-deploy/index.html
    
    # 创建 Netlify 配置
    cat > netlify-deploy/_redirects << 'EOF'
/*    /index.html   200
EOF
    
    cat > netlify-deploy/netlify.toml << 'EOF'
[build]
  publish = "."

[[headers]]
  for = "/*"
  [headers.values]
    X-Frame-Options = "DENY"
    X-XSS-Protection = "1; mode=block"
    X-Content-Type-Options = "nosniff"
EOF
    
    cd netlify-deploy
    if command -v zip &> /dev/null; then
        zip -r ../nexus-netlify-deploy.zip .
        print_success "部署包已生成: nexus-netlify-deploy.zip"
    else
        tar -czf ../nexus-netlify-deploy.tar.gz .
        print_success "部署包已生成: nexus-netlify-deploy.tar.gz"
    fi
    cd ..
    rm -rf netlify-deploy
    
    print_info "📋 Netlify 部署步骤:"
    echo "1. 访问: https://app.netlify.com/drop"
    echo "2. 拖拽部署包到页面"
    echo "3. 在设置中修改站点名称为: nss-novena-garfield"
    echo "4. 最终地址: https://nss-novena-garfield.netlify.app"
    
    return 0
}

# 方案3: 生成 GitHub Pages 配置
generate_github_pages() {
    print_info "方案3: 生成 GitHub Pages 配置"
    
    mkdir -p github-pages
    cp nexus-mini.html github-pages/index.html
    
    # 创建 GitHub Actions 工作流
    mkdir -p github-pages/.github/workflows
    cat > github-pages/.github/workflows/deploy.yml << 'EOF'
name: Deploy to GitHub Pages

on:
  push:
    branches: [ main ]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

jobs:
  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      - name: Setup Pages
        uses: actions/configure-pages@v4
      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: '.'
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
EOF
    
    # 创建 README
    cat > github-pages/README.md << 'EOF'
# N.S.S Novena Garfield - NEXUS Official Website

🚀 NEXUS Research Workstation 官方网站

## 访问地址
- GitHub Pages: https://novenazgarfield.github.io/nss-novena-garfield/
- 项目主页: https://github.com/novenazgarfield/research-workstation

## 部署说明
1. 创建新仓库名为: nss-novena-garfield
2. 上传所有文件到仓库
3. 在 Settings > Pages 中启用 GitHub Pages
4. 选择 GitHub Actions 作为部署源

自动部署完成后即可访问！
EOF
    
    if command -v zip &> /dev/null; then
        cd github-pages
        zip -r ../nexus-github-pages.zip .
        cd ..
        print_success "GitHub Pages 包已生成: nexus-github-pages.zip"
    else
        tar -czf nexus-github-pages.tar.gz github-pages/
        print_success "GitHub Pages 包已生成: nexus-github-pages.tar.gz"
    fi
    
    rm -rf github-pages
    
    print_info "📋 GitHub Pages 部署步骤:"
    echo "1. 在 GitHub 创建新仓库: nss-novena-garfield"
    echo "2. 上传解压后的文件到仓库"
    echo "3. 在 Settings > Pages 启用 GitHub Actions"
    echo "4. 最终地址: https://novenazgarfield.github.io/nss-novena-garfield/"
    
    return 0
}

# 方案4: 使用免费短链接服务
create_short_links() {
    print_info "方案4: 创建短链接"
    
    # 原始 data URL
    DATA_URL="data:text/html;charset=utf-8,%3C%21DOCTYPE%20html%3E%3Chtml%3E%3Chead%3E%3Cmeta%20charset%3D%22UTF-8%22%3E%3Ctitle%3ENEXUS%20-%20%E8%BF%9C%E7%A8%8B%E6%8E%A7%E5%88%B6%E7%B3%BB%E7%BB%9F%3C/title%3E%3Cstyle%3E%2A%7Bmargin%3A0%3Bpadding%3A0%3Bbox-sizing%3Aborder-box%7Dbody%7Bfont-family%3A-apple-system%2Csans-serif%3Bbackground%3Alinear-gradient%28135deg%2C%23667eea%2C%23764ba2%29%3Bcolor%3A%23fff%3Bmin-height%3A100vh%3Bdisplay%3Aflex%3Balign-items%3Acenter%3Bjustify-content%3Acenter%7D.container%7Btext-align%3Acenter%3Bpadding%3A2rem%7D.hero%20h1%7Bfont-size%3A4rem%3Bmargin-bottom%3A1rem%3Btext-shadow%3A2px%202px%204px%20rgba%280%2C0%2C0%2C0.3%29%7D.subtitle%7Bfont-size%3A1.5rem%3Bmargin-bottom%3A2rem%3Bopacity%3A0.9%7D.features%7Bdisplay%3Agrid%3Bgrid-template-columns%3Arepeat%28auto-fit%2Cminmax%28250px%2C1fr%29%29%3Bgap%3A1.5rem%3Bmargin%3A3rem%200%7D.card%7Bbackground%3Argba%28255%2C255%2C255%2C0.1%29%3Bpadding%3A1.5rem%3Bborder-radius%3A15px%3Bbackdrop-filter%3Ablur%2810px%29%3Btransition%3Atransform%200.3s%7D.card%3Ahover%7Btransform%3AtranslateY%28-5px%29%7D.icon%7Bfont-size%3A2.5rem%3Bmargin-bottom%3A1rem%7D.btn%7Bbackground%3Alinear-gradient%2845deg%2C%23ff6b6b%2C%23ee5a24%29%3Bcolor%3A%23fff%3Bpadding%3A1rem%202rem%3Bborder%3Anone%3Bborder-radius%3A50px%3Bfont-size%3A1.1rem%3Btext-decoration%3Anone%3Bdisplay%3Ainline-block%3Bmargin%3A0.5rem%3Btransition%3Atransform%200.3s%7D.btn%3Ahover%7Btransform%3AtranslateY%28-2px%29%7D%40media%28max-width%3A768px%29%7B.hero%20h1%7Bfont-size%3A2.5rem%7D.features%7Bgrid-template-columns%3A1fr%7D%7D%3C/style%3E%3C/head%3E%3Cbody%3E%3Cdiv%20class%3D%22container%22%3E%3Cdiv%20class%3D%22hero%22%3E%3Ch1%3E%F0%9F%9A%80%20NEXUS%3C/h1%3E%3Cdiv%20class%3D%22subtitle%22%3E%E9%9D%A9%E5%91%BD%E6%80%A7%E8%BF%9C%E7%A8%8B%E6%8C%87%E6%8C%A5%E4%B8%8E%E6%8E%A7%E5%88%B6%E7%B3%BB%E7%BB%9F%3C/div%3E%3Cp%3E%E7%AA%81%E7%A0%B4%E5%B1%80%E5%9F%9F%E7%BD%91%E9%99%90%E5%88%B6%EF%BC%8C%E5%AE%9E%E7%8E%B0%E7%9C%9F%E6%AD%A3%E7%9A%84%E5%85%A8%E7%90%83%E8%BF%9C%E7%A8%8B%E7%94%B5%E6%BA%90%E7%AE%A1%E7%90%86%3C/p%3E%3C/div%3E%3Cdiv%20class%3D%22features%22%3E%3Cdiv%20class%3D%22card%22%3E%3Cdiv%20class%3D%22icon%22%3E%F0%9F%8C%8D%3C/div%3E%3Ch3%3E%E5%85%A8%E7%90%83%E8%BF%9C%E7%A8%8B%E8%AE%BF%E9%97%AE%3C/h3%3E%3Cp%3E%E7%AA%81%E7%A0%B4%E5%B1%80%E5%9F%9F%E7%BD%91%E9%99%90%E5%88%B6%EF%BC%8C%E4%BA%91%E6%9C%8D%E5%8A%A1%E5%99%A8%E4%B8%AD%E8%BD%AC%3C/p%3E%3C/div%3E%3Cdiv%20class%3D%22card%22%3E%3Cdiv%20class%3D%22icon%22%3E%E2%9A%A1%3C/div%3E%3Ch3%3E%E5%AE%8C%E6%95%B4%E7%94%B5%E6%BA%90%E7%AE%A1%E7%90%86%3C/h3%3E%3Cp%3E%E8%BF%9C%E7%A8%8B%E5%BC%80%E6%9C%BA%E3%80%81%E5%85%B3%E6%9C%BA%E3%80%81%E9%87%8D%E5%90%AF%3C/p%3E%3C/div%3E%3Cdiv%20class%3D%22card%22%3E%3Cdiv%20class%3D%22icon%22%3E%F0%9F%8E%AF%3C/div%3E%3Ch3%3E%E9%9B%B6%E5%91%BD%E4%BB%A4%E8%A1%8C%E4%BD%93%E9%AA%8C%3C/h3%3E%3Cp%3E%E5%AE%8C%E5%85%A8%E5%9B%BE%E5%BD%A2%E5%8C%96%E7%95%8C%E9%9D%A2%3C/p%3E%3C/div%3E%3Cdiv%20class%3D%22card%22%3E%3Cdiv%20class%3D%22icon%22%3E%F0%9F%93%B1%3C/div%3E%3Ch3%3E%E7%A7%BB%E5%8A%A8%E7%AB%AF%E4%BC%98%E5%8C%96%3C/h3%3E%3Cp%3EPWA%E5%8E%9F%E7%94%9F%E4%BD%93%E9%AA%8C%3C/p%3E%3C/div%3E%3Cdiv%20class%3D%22card%22%3E%3Cdiv%20class%3D%22icon%22%3E%F0%9F%9B%A1%EF%B8%8F%3C/div%3E%3Ch3%3E%E4%BC%81%E4%B8%9A%E7%BA%A7%E5%AE%89%E5%85%A8%3C/h3%3E%3Cp%3E256%E4%BD%8D%E5%8A%A0%E5%AF%86%E4%BF%9D%E9%9A%9C%3C/p%3E%3C/div%3E%3Cdiv%20class%3D%22card%22%3E%3Cdiv%20class%3D%22icon%22%3E%F0%9F%94%A7%3C/div%3E%3Ch3%3E%E7%BB%9F%E4%B8%80%E7%AE%A1%E7%90%86%3C/h3%3E%3Cp%3E%E4%B8%80%E7%AB%99%E5%BC%8F%E7%B3%BB%E7%BB%9F%E7%AE%A1%E7%90%86%3C/p%3E%3C/div%3E%3C/div%3E%3Cdiv%3E%3Ca%20href%3D%22https%3A//github.com/novenazgarfield/research-workstation/releases%22%20class%3D%22btn%22%3E%E2%AC%87%EF%B8%8F%20%E7%AB%8B%E5%8D%B3%E4%B8%8B%E8%BD%BD%3C/a%3E%3Ca%20href%3D%22https%3A//github.com/novenazgarfield/research-workstation%22%20class%3D%22btn%22%3E%F0%9F%93%9A%20%E6%9F%A5%E7%9C%8B%E6%96%87%E6%A1%A3%3C/a%3E%3C/div%3E%3Cp%20style%3D%22margin-top%3A2rem%3Bopacity%3A0.8%22%3E%C2%A9%202025%20NEXUS%20Research%20Workstation%3C/p%3E%3C/div%3E%3Cscript%3Econsole.log%28%27%F0%9F%9A%80%20%E6%AC%A2%E8%BF%8E%E4%BD%BF%E7%94%A8NEXUS%EF%BC%81%27%29%3B%3C/script%3E%3C/body%3E%3C/html%3E"
    
    print_success "✅ 即时访问链接（复制到浏览器）:"
    echo "$DATA_URL"
    
    print_info "💡 可以使用以下短链接服务:"
    echo "1. TinyURL: https://tinyurl.com/"
    echo "2. Bit.ly: https://bit.ly/"
    echo "3. Short.link: https://short.link/"
    echo "4. T.ly: https://t.ly/"
    
    return 0
}

# 主菜单
show_menu() {
    echo ""
    print_info "请选择部署方案:"
    echo "1) Surge.sh - 自定义域名 (nss-novena-garfield.surge.sh)"
    echo "2) Netlify - 生成部署包 (nss-novena-garfield.netlify.app)"
    echo "3) GitHub Pages - 生成配置 (github.io/nss-novena-garfield)"
    echo "4) 即时访问 - Data URL (立即可用)"
    echo "5) 全部生成"
    echo "0) 退出"
    echo ""
    read -p "请输入选择 (0-5): " choice
    
    case $choice in
        1)
            deploy_surge
            ;;
        2)
            generate_netlify_package
            ;;
        3)
            generate_github_pages
            ;;
        4)
            create_short_links
            ;;
        5)
            print_info "生成所有部署方案..."
            generate_netlify_package
            generate_github_pages
            create_short_links
            print_success "所有方案已生成完成！"
            ;;
        0)
            print_info "退出部署脚本"
            exit 0
            ;;
        *)
            print_error "无效选择，请重新输入"
            show_menu
            ;;
    esac
}

# 主程序
main() {
    check_dependencies
    echo ""
    print_success "🎯 目标域名: N.S.S-Novena-Garfield"
    print_info "所有方案都将使用您指定的自定义名称"
    show_menu
}

# 运行主程序
main