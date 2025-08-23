#!/bin/bash

echo "🚀 使用现有仓库申请 JS.ORG 域名"
echo "仓库: research-workstation"
echo "=" * 40

# 创建简单的申请信息
cat > js-org-simple-application.txt << 'EOF'
JS.ORG 域名申请信息
==================

子域名: nss-novena
目标地址: novenazgarfield.github.io/research-workstation
项目: NEXUS Research Workstation - N.S.S Novena Garfield
GitHub: https://github.com/novenazgarfield/research-workstation

申请理由:
- 开源远程控制系统项目
- 已有完整的代码和文档
- 需要一个简短易记的官方域名
- N.S.S Novena Garfield 是项目的特别版本

最终域名: https://nss-novena.js.org
EOF

echo "✅ 申请信息已生成: js-org-simple-application.txt"

# 创建用于 GitHub Pages 的简单文件
mkdir -p github-pages-simple
cp nexus-simple.html github-pages-simple/index.html

# 创建 CNAME 文件
echo "nss-novena.js.org" > github-pages-simple/CNAME

echo "✅ GitHub Pages 文件已准备: github-pages-simple/"

echo ""
echo "🎯 超简单申请步骤:"
echo "1. 把 github-pages-simple/ 里的文件上传到您的仓库"
echo "2. 在仓库 Settings > Pages 启用 GitHub Pages"
echo "3. 访问 https://js.org/ 申请域名"
echo ""
echo "📋 申请时填写:"
echo "• 子域名: nss-novena"
echo "• 目标: novenazgarfield.github.io/research-workstation"
echo ""
echo "🌐 成功后获得: https://nss-novena.js.org"
echo ""
echo "💡 更新网站: 直接在 GitHub 仓库里修改文件即可！"