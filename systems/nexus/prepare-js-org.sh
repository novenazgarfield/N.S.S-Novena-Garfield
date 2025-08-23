#!/bin/bash

echo "🚀 准备 N.S.S Novena Garfield 的 JS.ORG 域名申请"
echo "=" * 60

# 创建 GitHub Pages 准备文件
echo "📁 创建 GitHub Pages 文件..."

# 创建专门的 js.org 目录
mkdir -p js-org-site

# 复制网站文件
cp nexus-simple.html js-org-site/index.html

# 创建 CNAME 文件 (GitHub Pages 需要)
echo "nss-novena.js.org" > js-org-site/CNAME

# 创建 README
cat > js-org-site/README.md << 'EOF'
# N.S.S Novena Garfield - NEXUS Research Workstation

🚀 Official website for NEXUS Research Workstation

## Domain
- **Target**: nss-novena.js.org
- **Project**: NEXUS Research Workstation
- **Description**: Revolutionary remote power management system

## Features
- 🌍 Global remote access
- ⚡ Complete power management
- 🎯 Zero command line experience
- 📱 Mobile optimized
- 🛡️ Enterprise security
- 🔧 Unified system management

## Links
- [GitHub Repository](https://github.com/novenazgarfield/research-workstation)
- [Releases](https://github.com/novenazgarfield/research-workstation/releases)

© 2025 NEXUS Research Workstation Team
EOF

# 创建 package.json (证明是 JS 项目)
cat > js-org-site/package.json << 'EOF'
{
  "name": "nss-novena-garfield",
  "version": "1.0.0",
  "description": "NEXUS Research Workstation - N.S.S Novena Garfield Edition",
  "main": "index.html",
  "scripts": {
    "start": "python3 -m http.server 8000",
    "build": "echo 'Static site, no build needed'"
  },
  "keywords": [
    "nexus",
    "remote-control",
    "power-management",
    "workstation",
    "nss-novena-garfield"
  ],
  "author": "NEXUS Team",
  "license": "MIT",
  "homepage": "https://nss-novena.js.org"
}
EOF

# 创建部署包
echo "📦 创建部署包..."
cd js-org-site
if command -v zip &> /dev/null; then
    zip -r ../nss-novena-js-org.zip .
    echo "✅ 部署包已创建: nss-novena-js-org.zip"
else
    tar -czf ../nss-novena-js-org.tar.gz .
    echo "✅ 部署包已创建: nss-novena-js-org.tar.gz"
fi
cd ..

echo ""
echo "🎯 JS.ORG 申请准备完成！"
echo "=" * 60

echo ""
echo "📋 申请信息:"
echo "子域名: nss-novena"
echo "目标: novenazgarfield.github.io/nss-novena-garfield"
echo "描述: NEXUS Research Workstation - N.S.S Novena Garfield"
echo ""

echo "🚀 下一步操作:"
echo "1. 上传 js-org-site/ 到 GitHub 仓库"
echo "2. 启用 GitHub Pages"
echo "3. 访问 https://js.org/ 申请域名"
echo "4. 或者 Fork https://github.com/js-org/js.org 提交 PR"
echo ""

echo "💡 申请成功后，您将获得:"
echo "🌐 https://nss-novena.js.org (只有16个字符！)"
echo ""

# 创建 GitHub 仓库创建指南
cat > create-github-repo.md << 'EOF'
# 创建 GitHub 仓库指南

## 步骤1: 创建新仓库
1. 访问 https://github.com/new
2. 仓库名: `nss-novena-garfield`
3. 设为公开 (Public)
4. 勾选 "Add a README file"

## 步骤2: 上传文件
1. 上传 `js-org-site/` 中的所有文件
2. 或者使用 git 命令：
```bash
git clone https://github.com/novenazgarfield/nss-novena-garfield.git
cd nss-novena-garfield
cp -r js-org-site/* .
git add .
git commit -m "Add NEXUS N.S.S Novena Garfield website"
git push
```

## 步骤3: 启用 GitHub Pages
1. 进入仓库 Settings
2. 找到 Pages 设置
3. Source: Deploy from a branch
4. Branch: main
5. Folder: / (root)
6. 保存设置

## 步骤4: 申请 JS.ORG 域名
访问 https://js.org/ 填写申请表单，或提交 GitHub PR

目标地址: `novenazgarfield.github.io/nss-novena-garfield`
申请域名: `nss-novena.js.org`
EOF

echo "📄 GitHub 仓库创建指南: create-github-repo.md"
echo ""
echo "🎉 一切准备就绪！开始申请您的 nss-novena.js.org 域名吧！"