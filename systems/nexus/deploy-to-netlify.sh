#!/bin/bash

# NEXUS 一键部署到 Netlify Drop
# 自动生成部署包

echo "🚀 NEXUS Netlify 部署包生成器"
echo "目标: 生成可拖拽到 Netlify Drop 的部署包"
echo "=================================="

# 创建部署目录
echo "📁 准备部署文件..."
mkdir -p netlify-deploy
cp nexus-mini.html netlify-deploy/index.html

# 创建 _redirects 文件（Netlify 配置）
cat > netlify-deploy/_redirects << 'EOF'
/*    /index.html   200
EOF

# 创建 netlify.toml 配置文件
cat > netlify-deploy/netlify.toml << 'EOF'
[build]
  publish = "."

[[headers]]
  for = "/*"
  [headers.values]
    X-Frame-Options = "DENY"
    X-XSS-Protection = "1; mode=block"
    X-Content-Type-Options = "nosniff"
    Referrer-Policy = "strict-origin-when-cross-origin"

[[headers]]
  for = "*.html"
  [headers.values]
    Cache-Control = "public, max-age=0, must-revalidate"

[[headers]]
  for = "*.css"
  [headers.values]
    Cache-Control = "public, max-age=31536000, immutable"

[[headers]]
  for = "*.js"
  [headers.values]
    Cache-Control = "public, max-age=31536000, immutable"
EOF

# 打包为 zip 文件
echo "📦 正在打包..."
cd netlify-deploy
zip -r ../nexus-netlify-deploy.zip .
cd ..

echo ""
echo "🎉 部署包已生成！"
echo "📦 文件位置: nexus-netlify-deploy.zip"
echo ""
echo "🌐 部署步骤:"
echo "1. 访问: https://app.netlify.com/drop"
echo "2. 拖拽 nexus-netlify-deploy.zip 到页面"
echo "3. 等待部署完成"
echo "4. 获得类似 https://amazing-name-123456.netlify.app 的地址"
echo ""
echo "💡 提示: 可以在 Netlify 后台修改站点名称为:"
echo "   nss-novena-garfield (如果可用)"
echo "   最终地址: https://nss-novena-garfield.netlify.app"

# 清理临时文件
rm -rf netlify-deploy