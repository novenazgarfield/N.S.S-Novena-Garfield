#!/usr/bin/env python3
"""
直接更新线上版本
"""

import requests
import json
import base64
from urllib.parse import quote

def create_data_url():
    """创建data URL直接访问"""
    print("🚀 正在创建更新的data URL...")
    
    # 读取更新后的HTML文件
    with open('dist/nexus-dashboard-restored.html', 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # 创建data URL
    encoded_html = quote(html_content, safe='')
    data_url = f"data:text/html;charset=utf-8,{encoded_html}"
    
    print("✅ Data URL 创建成功!")
    print(f"🌐 可直接访问: {data_url[:100]}...")
    
    # 保存到文件
    with open('updated-url.txt', 'w') as f:
        f.write(data_url)
    
    print("📁 URL已保存到 updated-url.txt")
    return data_url

def create_github_gist():
    """创建GitHub Gist"""
    print("🚀 正在创建GitHub Gist...")
    
    with open('dist/nexus-dashboard-restored.html', 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # GitHub Gist API
    gist_data = {
        "description": "N.S.S - Novena Garfield Dashboard (Updated)",
        "public": True,
        "files": {
            "nexus-dashboard.html": {
                "content": html_content
            }
        }
    }
    
    try:
        response = requests.post(
            'https://api.github.com/gists',
            json=gist_data,
            timeout=30
        )
        
        if response.status_code == 201:
            gist_info = response.json()
            gist_url = gist_info['html_url']
            raw_url = gist_info['files']['nexus-dashboard.html']['raw_url']
            
            print(f"✅ Gist 创建成功!")
            print(f"🌐 Gist地址: {gist_url}")
            print(f"🌐 直接访问: {raw_url}")
            
            return gist_url, raw_url
        else:
            print(f"❌ Gist创建失败: {response.status_code}")
            return None, None
            
    except Exception as e:
        print(f"❌ 创建Gist时出错: {e}")
        return None, None

def main():
    print("🎯 直接更新线上版本")
    print("=" * 50)
    
    # 方案1: Data URL
    data_url = create_data_url()
    
    # 方案2: GitHub Gist
    gist_url, raw_url = create_github_gist()
    
    print("\n🎉 更新完成!")
    print("📋 可用的访问方式:")
    print(f"1. Data URL: 已保存到 updated-url.txt")
    if gist_url:
        print(f"2. GitHub Gist: {gist_url}")
        print(f"3. 直接访问: {raw_url}")
    
    print("\n💡 建议使用GitHub Gist的raw URL进行访问")

if __name__ == "__main__":
    main()