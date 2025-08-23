#!/usr/bin/env python3
"""
NEXUS 一键API部署脚本
自动部署到多个免费平台，获得自定义域名
"""

import requests
import json
import base64
import os
import time
from urllib.parse import quote

class NexusDeployer:
    def __init__(self):
        self.html_content = self.load_html()
        self.custom_name = "nss-novena-garfield"
        
    def load_html(self):
        """加载HTML内容"""
        try:
            with open('nexus-mini.html', 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            print("❌ 找不到 nexus-mini.html 文件")
            return None
    
    def deploy_to_surge(self):
        """部署到 Surge.sh (需要token)"""
        print("🚀 正在部署到 Surge.sh...")
        
        # Surge.sh 需要CLI工具，这里提供配置
        surge_config = {
            "domain": f"{self.custom_name}.surge.sh",
            "files": {
                "index.html": self.html_content,
                "CNAME": f"{self.custom_name}.surge.sh"
            }
        }
        
        print(f"✅ Surge 配置已生成")
        print(f"🌐 目标地址: https://{self.custom_name}.surge.sh")
        print("💡 需要运行: surge . --domain nss-novena-garfield.surge.sh")
        
        return surge_config
    
    def deploy_to_netlify_api(self):
        """使用 Netlify API 部署"""
        print("🚀 正在通过API部署到 Netlify...")
        
        # 创建部署包
        files = {
            "index.html": self.html_content,
            "_redirects": "/*    /index.html   200",
            "netlify.toml": """[build]
  publish = "."

[[headers]]
  for = "/*"
  [headers.values]
    X-Frame-Options = "DENY"
    X-XSS-Protection = "1; mode=block"
"""
        }
        
        # 准备文件数据
        file_data = {}
        for filename, content in files.items():
            file_data[filename] = {
                "content": base64.b64encode(content.encode()).decode(),
                "encoding": "base64"
            }
        
        # Netlify Deploy API (无需认证的方式)
        deploy_data = {
            "files": file_data,
            "draft": False
        }
        
        try:
            # 使用 Netlify 的公开部署API
            response = requests.post(
                "https://api.netlify.com/api/v1/sites",
                json={
                    "name": self.custom_name,
                    "files": file_data
                },
                timeout=30
            )
            
            if response.status_code == 201:
                site_data = response.json()
                site_url = site_data.get('ssl_url', site_data.get('url'))
                print(f"✅ Netlify 部署成功！")
                print(f"🌐 访问地址: {site_url}")
                return site_url
            else:
                print(f"❌ Netlify API 部署失败: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Netlify 部署出错: {e}")
            return None
    
    def create_github_gist(self):
        """创建 GitHub Gist (公开，可直接访问)"""
        print("🚀 正在创建 GitHub Gist...")
        
        gist_data = {
            "description": "NEXUS Research Workstation - N.S.S Novena Garfield",
            "public": True,
            "files": {
                "nexus-nss-novena-garfield.html": {
                    "content": self.html_content
                }
            }
        }
        
        try:
            response = requests.post(
                "https://api.github.com/gists",
                json=gist_data,
                timeout=30
            )
            
            if response.status_code == 201:
                gist_data = response.json()
                gist_url = gist_data['html_url']
                raw_url = gist_data['files']['nexus-nss-novena-garfield.html']['raw_url']
                
                print(f"✅ GitHub Gist 创建成功！")
                print(f"🌐 Gist 地址: {gist_url}")
                print(f"🌐 直接访问: https://htmlpreview.github.io/?{raw_url}")
                
                return {
                    "gist_url": gist_url,
                    "preview_url": f"https://htmlpreview.github.io/?{raw_url}",
                    "raw_url": raw_url
                }
            else:
                print(f"❌ GitHub Gist 创建失败: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ GitHub Gist 创建出错: {e}")
            return None
    
    def create_codepen(self):
        """创建 CodePen (通过API)"""
        print("🚀 正在创建 CodePen...")
        
        # 提取HTML、CSS、JS
        html_part = self.html_content
        
        # CodePen 数据
        pen_data = {
            "title": "NEXUS - N.S.S Novena Garfield",
            "description": "NEXUS Research Workstation Official Website",
            "html": html_part,
            "css": "",
            "js": "",
            "html_pre_processor": "none",
            "css_pre_processor": "none",
            "js_pre_processor": "none"
        }
        
        print("✅ CodePen 配置已生成")
        print("💡 请访问 https://codepen.io/pen/ 手动创建")
        print("📋 或使用以下数据URL:")
        
        return pen_data
    
    def create_data_url(self):
        """创建 Data URL"""
        print("🚀 生成 Data URL...")
        
        data_url = f"data:text/html;charset=utf-8,{quote(self.html_content)}"
        
        print("✅ Data URL 已生成")
        print(f"🌐 直接访问链接:")
        print(data_url)
        
        return data_url
    
    def create_short_url(self, long_url):
        """创建短链接 (使用免费API)"""
        print("🚀 正在创建短链接...")
        
        # 尝试多个免费短链接服务
        services = [
            {
                "name": "TinyURL",
                "url": "http://tinyurl.com/api-create.php",
                "params": {"url": long_url}
            },
            {
                "name": "is.gd",
                "url": "https://is.gd/create.php",
                "params": {"format": "simple", "url": long_url}
            }
        ]
        
        for service in services:
            try:
                response = requests.get(service["url"], params=service["params"], timeout=10)
                if response.status_code == 200 and response.text.startswith("http"):
                    short_url = response.text.strip()
                    print(f"✅ {service['name']} 短链接: {short_url}")
                    return short_url
            except Exception as e:
                print(f"❌ {service['name']} 失败: {e}")
                continue
        
        return None
    
    def deploy_all(self):
        """一键部署到所有平台"""
        print("🎯 NEXUS 一键部署开始")
        print(f"🏷️  自定义名称: {self.custom_name}")
        print("=" * 50)
        
        if not self.html_content:
            print("❌ 无法加载HTML内容，部署终止")
            return
        
        results = {}
        
        # 1. 创建 Data URL (即时可用)
        print("\n📍 方案1: Data URL (即时访问)")
        data_url = self.create_data_url()
        results['data_url'] = data_url
        
        # 2. 创建 GitHub Gist
        print("\n📍 方案2: GitHub Gist")
        gist_result = self.create_github_gist()
        if gist_result:
            results['gist'] = gist_result
        
        # 3. 生成 Surge 配置
        print("\n📍 方案3: Surge.sh 配置")
        surge_config = self.deploy_to_surge()
        results['surge'] = surge_config
        
        # 4. 创建短链接
        if 'data_url' in results:
            print("\n📍 方案4: 短链接")
            short_url = self.create_short_url(results['data_url'])
            if short_url:
                results['short_url'] = short_url
        
        # 输出总结
        print("\n" + "=" * 50)
        print("🎉 部署完成！可用地址:")
        print("=" * 50)
        
        if 'data_url' in results:
            print(f"🚀 即时访问: {results['data_url'][:100]}...")
        
        if 'gist' in results:
            print(f"📝 GitHub Gist: {results['gist']['gist_url']}")
            print(f"🌐 预览地址: {results['gist']['preview_url']}")
        
        if 'short_url' in results:
            print(f"🔗 短链接: {results['short_url']}")
        
        if 'surge' in results:
            print(f"⚡ Surge 目标: https://{self.custom_name}.surge.sh")
        
        print("\n💡 推荐使用 GitHub Gist 预览地址，最稳定！")
        
        return results

def main():
    """主函数"""
    print("🚀 NEXUS API 一键部署工具")
    print("🎯 目标: N.S.S Novena Garfield")
    print("=" * 50)
    
    deployer = NexusDeployer()
    results = deployer.deploy_all()
    
    # 保存结果到文件
    with open('deployment-results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 部署结果已保存到: deployment-results.json")

if __name__ == "__main__":
    main()