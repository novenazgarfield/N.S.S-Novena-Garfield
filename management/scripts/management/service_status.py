#!/usr/bin/env python3
"""
服务状态显示脚本
"""

import subprocess
import json
import requests
from datetime import datetime

def get_tunnel_urls():
    """获取隧道URL"""
    try:
        # 从日志文件中提取URL
        with open('/tmp/api_tunnel.log', 'r') as f:
            api_log = f.read()
        with open('/tmp/frontend_tunnel.log', 'r') as f:
            frontend_log = f.read()
        
        import re
        api_url = re.search(r'https://[^\s]+\.trycloudflare\.com', api_log)
        frontend_url = re.search(r'https://[^\s]+\.trycloudflare\.com', frontend_log)
        
        return (
            api_url.group(0) if api_url else None,
            frontend_url.group(0) if frontend_url else None
        )
    except:
        return None, None

def test_api_health(api_url):
    """测试API健康状态"""
    try:
        response = requests.get(f"{api_url}/api/health", timeout=5)
        return response.status_code == 200, response.json() if response.status_code == 200 else None
    except:
        return False, None

def check_process_status():
    """检查进程状态"""
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        processes = result.stdout
        
        api_running = 'smart_rag_server.py' in processes
        frontend_running = 'http.server 53870' in processes
        tunnel_running = processes.count('cloudflared') >= 2
        
        return api_running, frontend_running, tunnel_running
    except:
        return False, False, False

def main():
    print("🔍 NEXUS AI 系统状态检查")
    print("=" * 50)
    
    # 获取隧道URL
    api_url, frontend_url = get_tunnel_urls()
    
    # 检查进程状态
    api_running, frontend_running, tunnel_running = check_process_status()
    
    # 测试API健康状态
    api_healthy = False
    api_info = None
    if api_url and api_running:
        api_healthy, api_info = test_api_health(api_url)
    
    # 显示状态
    print(f"📅 检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    print("🔧 服务状态:")
    print(f"  • API服务: {'✅ 运行中' if api_running else '❌ 未运行'}")
    print(f"  • 前端服务: {'✅ 运行中' if frontend_running else '❌ 未运行'}")
    print(f"  • 隧道服务: {'✅ 运行中' if tunnel_running else '❌ 未运行'}")
    print()
    
    print("🌐 访问地址:")
    if api_url:
        print(f"  • API服务: {api_url}")
        print(f"    健康状态: {'✅ 正常' if api_healthy else '❌ 异常'}")
        if api_info:
            print(f"    文档数量: {api_info.get('documents_count', 0)}")
    else:
        print("  • API服务: ❌ 隧道URL未找到")
    
    if frontend_url:
        print(f"  • 前端界面: {frontend_url}")
    else:
        print("  • 前端界面: ❌ 隧道URL未找到")
    
    print()
    
    if api_url and frontend_url and api_healthy:
        print("🎉 所有服务运行正常！")
        print("💡 您可以:")
        print("   1. 访问前端界面开始使用")
        print("   2. 直接调用API接口")
        print("   3. 上传文档进行RAG问答")
    else:
        print("⚠️  部分服务可能存在问题，请检查日志")
    
    print("=" * 50)
    
    # 保存配置到文件
    config = {
        'api_url': api_url,
        'frontend_url': frontend_url,
        'status': {
            'api_running': api_running,
            'frontend_running': frontend_running,
            'tunnel_running': tunnel_running,
            'api_healthy': api_healthy
        },
        'timestamp': datetime.now().isoformat()
    }
    
    with open('/tmp/nexus_status.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    return config

if __name__ == "__main__":
    main()