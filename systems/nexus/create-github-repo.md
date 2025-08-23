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
