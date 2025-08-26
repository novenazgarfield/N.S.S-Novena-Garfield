#!/usr/bin/env python3
"""
RAG系统状态检查脚本
快速检查RAG系统的运行状态和连接性
"""

import requests
import json
import subprocess
import sys
from datetime import datetime

def print_header(title):
    """打印标题"""
    print(f"\n{'='*50}")
    print(f"🔍 {title}")
    print(f"{'='*50}")

def print_status(status, message):
    """打印状态信息"""
    icons = {
        'success': '✅',
        'error': '❌',
        'warning': '⚠️',
        'info': 'ℹ️'
    }
    print(f"{icons.get(status, '•')} {message}")

def check_process():
    """检查RAG服务器进程"""
    print_header("进程状态检查")
    
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        if 'simple_rag_api' in result.stdout:
            lines = [line for line in result.stdout.split('\n') if 'simple_rag_api' in line]
            for line in lines:
                parts = line.split()
                if len(parts) >= 2:
                    pid = parts[1]
                    print_status('success', f"RAG服务器正在运行 (PID: {pid})")
                    return True
        else:
            print_status('error', "RAG服务器进程未找到")
            return False
    except Exception as e:
        print_status('error', f"无法检查进程状态: {e}")
        return False

def check_api_health():
    """检查API健康状态"""
    print_header("API健康检查")
    
    try:
        response = requests.get('http://localhost:5000/api/health', timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print_status('success', f"API服务正常 (状态码: {response.status_code})")
            print_status('info', f"系统状态: {data.get('status', 'unknown')}")
            print_status('info', f"聊天历史: {data.get('chat_history_count', 0)} 条")
            print_status('info', f"文档数量: {data.get('documents_count', 0)} 个")
            print_status('info', f"系统时间: {data.get('timestamp', 'unknown')}")
            return True
        else:
            print_status('error', f"API响应异常 (状态码: {response.status_code})")
            return False
            
    except requests.exceptions.ConnectionError:
        print_status('error', "无法连接到API服务器 (连接被拒绝)")
        return False
    except requests.exceptions.Timeout:
        print_status('error', "API请求超时")
        return False
    except Exception as e:
        print_status('error', f"API检查失败: {e}")
        return False

def check_chat_api():
    """检查聊天API"""
    print_header("聊天API测试")
    
    try:
        test_data = {
            "message": "系统状态检查测试",
            "task_name": "status_check"
        }
        
        response = requests.post(
            'http://localhost:5000/api/chat',
            json=test_data,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print_status('success', "聊天API工作正常")
                print_status('info', f"响应长度: {len(data.get('response', ''))} 字符")
                return True
            else:
                print_status('error', f"聊天API返回错误: {data.get('error', 'unknown')}")
                return False
        else:
            print_status('error', f"聊天API响应异常 (状态码: {response.status_code})")
            return False
            
    except Exception as e:
        print_status('error', f"聊天API测试失败: {e}")
        return False

def check_cors():
    """检查CORS配置"""
    print_header("CORS配置检查")
    
    try:
        headers = {
            'Origin': 'http://localhost:52943',
            'Access-Control-Request-Method': 'POST',
            'Access-Control-Request-Headers': 'Content-Type'
        }
        
        response = requests.options('http://localhost:5000/api/chat', headers=headers, timeout=5)
        
        cors_headers = {
            'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
            'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
            'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers')
        }
        
        if cors_headers['Access-Control-Allow-Origin']:
            print_status('success', f"CORS配置正常")
            print_status('info', f"允许的源: {cors_headers['Access-Control-Allow-Origin']}")
            print_status('info', f"允许的方法: {cors_headers['Access-Control-Allow-Methods']}")
            print_status('info', f"允许的头部: {cors_headers['Access-Control-Allow-Headers']}")
            return True
        else:
            print_status('warning', "CORS头部未找到，可能影响前端连接")
            return False
            
    except Exception as e:
        print_status('error', f"CORS检查失败: {e}")
        return False

def check_frontend_server():
    """检查前端服务器"""
    print_header("前端服务器检查")
    
    try:
        response = requests.get('http://localhost:52943', timeout=5)
        
        if response.status_code == 200:
            print_status('success', f"前端服务器正常 (状态码: {response.status_code})")
            return True
        else:
            print_status('error', f"前端服务器响应异常 (状态码: {response.status_code})")
            return False
            
    except requests.exceptions.ConnectionError:
        print_status('error', "无法连接到前端服务器")
        return False
    except Exception as e:
        print_status('error', f"前端服务器检查失败: {e}")
        return False

def print_summary(results):
    """打印检查结果摘要"""
    print_header("检查结果摘要")
    
    total_checks = len(results)
    passed_checks = sum(results.values())
    
    print(f"📊 总检查项: {total_checks}")
    print(f"✅ 通过检查: {passed_checks}")
    print(f"❌ 失败检查: {total_checks - passed_checks}")
    print(f"📈 成功率: {passed_checks/total_checks*100:.1f}%")
    
    if passed_checks == total_checks:
        print_status('success', "🎉 所有检查都通过了！RAG系统运行正常。")
    elif passed_checks >= total_checks * 0.8:
        print_status('warning', "⚠️ 大部分检查通过，但有一些问题需要注意。")
    else:
        print_status('error', "❌ 多项检查失败，RAG系统可能存在问题。")
    
    print(f"\n🕒 检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def print_recommendations(results):
    """打印建议"""
    print_header("问题解决建议")
    
    if not results.get('process', False):
        print("🔧 RAG服务器未运行:")
        print("   python simple_rag_api.py")
    
    if not results.get('api_health', False):
        print("🔧 API服务异常:")
        print("   检查服务器日志，重启RAG服务器")
    
    if not results.get('chat_api', False):
        print("🔧 聊天API异常:")
        print("   检查API配置，确认OpenAI API密钥")
    
    if not results.get('cors', False):
        print("🔧 CORS配置问题:")
        print("   检查服务器CORS设置，确认允许localhost:52943")
    
    if not results.get('frontend', False):
        print("🔧 前端服务器问题:")
        print("   python3 -m http.server 52943 --bind 0.0.0.0")

def main():
    """主函数"""
    print("🚀 RAG系统状态检查工具")
    print(f"⏰ 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 执行各项检查
    results = {
        'process': check_process(),
        'api_health': check_api_health(),
        'chat_api': check_chat_api(),
        'cors': check_cors(),
        'frontend': check_frontend_server()
    }
    
    # 打印结果
    print_summary(results)
    print_recommendations(results)
    
    # 返回退出码
    if all(results.values()):
        sys.exit(0)  # 所有检查通过
    else:
        sys.exit(1)  # 有检查失败

if __name__ == "__main__":
    main()