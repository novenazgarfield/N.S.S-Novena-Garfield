# 上传到 N.S.S-Novena-Garfield 仓库指南

## 🎯 目标仓库
https://github.com/novenazgarfield/N.S.S-Novena-Garfield

## 📁 需要上传的文件

### 1. index.html (主页)
```html
<!DOCTYPE html><html><head><meta charset="UTF-8"><title>NEXUS</title><style>*{margin:0;padding:0}body{font-family:Arial;background:linear-gradient(45deg,#667eea,#764ba2);color:#fff;height:100vh;display:flex;align-items:center;justify-content:center;text-align:center}.card{background:rgba(255,255,255,0.1);padding:2rem;border-radius:20px;backdrop-filter:blur(10px)}h1{font-size:3rem;margin-bottom:1rem}p{margin:1rem 0}.btn{background:#ff6b6b;color:#fff;padding:1rem 2rem;border:none;border-radius:50px;text-decoration:none;display:inline-block;margin:0.5rem;transition:transform 0.3s}.btn:hover{transform:translateY(-2px)}</style></head><body><div class="card"><h1>🚀 NEXUS</h1><p>N.S.S Novena Garfield</p><p>远程控制系统</p><a href="https://github.com/novenazgarfield/N.S.S-Novena-Garfield" class="btn">GitHub</a><a href="https://github.com/novenazgarfield/N.S.S-Novena-Garfield/releases" class="btn">下载</a></div></body></html>
```

### 2. CNAME (域名配置)
```
nss-novena.js.org
```

## 🚀 上传步骤

1. **访问您的仓库**
   https://github.com/novenazgarfield/N.S.S-Novena-Garfield

2. **上传 index.html**
   - 点击 "Add file" > "Create new file"
   - 文件名: `index.html`
   - 复制上面的 HTML 代码
   - 提交: "Add NEXUS website"

3. **上传 CNAME**
   - 再次点击 "Add file" > "Create new file"
   - 文件名: `CNAME`
   - 内容: `nss-novena.js.org`
   - 提交: "Add CNAME for js.org domain"

4. **启用 GitHub Pages**
   - 进入仓库 Settings
   - 找到 Pages 设置
   - Source: Deploy from a branch
   - Branch: main
   - Folder: / (root)
   - 保存

5. **申请 JS.ORG 域名**
   - 访问: https://js.org/
   - 子域名: `nss-novena`
   - 目标: `novenazgarfield.github.io/N.S.S-Novena-Garfield`
   - 项目: NEXUS Research Workstation

## 🌐 最终结果

申请成功后，您将获得:
**https://nss-novena.js.org**

## 💡 更新网站

以后想修改网站，直接在 GitHub 仓库里编辑 `index.html` 文件即可！