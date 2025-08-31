#!/usr/bin/env python3
"""
系统稳定性分析和修复工具
分析系统不稳定的原因并提供解决方案
"""

import os
import sys
import time
import psutil
import subprocess
import json
from pathlib import Path
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Any

class SystemStabilityAnalyzer:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.log_dir = Path("/tmp")
        self.analysis_results = {}
        
        # 设置日志
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def log(self, message):
        """日志输出"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {message}")
        self.logger.info(message)
    
    def analyze_system_resources(self) -> Dict[str, Any]:
        """分析系统资源使用情况"""
        self.log("🔍 分析系统资源...")
        
        # CPU使用率
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        
        # 内存使用情况
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_available = memory.available / (1024**3)  # GB
        memory_total = memory.total / (1024**3)  # GB
        
        # 磁盘使用情况
        disk = psutil.disk_usage('/')
        disk_percent = (disk.used / disk.total) * 100
        disk_free = disk.free / (1024**3)  # GB
        
        # 网络连接数
        connections = len(psutil.net_connections())
        
        resource_analysis = {
            "cpu": {
                "usage_percent": cpu_percent,
                "core_count": cpu_count,
                "status": "正常" if cpu_percent < 80 else "高负载" if cpu_percent < 95 else "严重负载"
            },
            "memory": {
                "usage_percent": memory_percent,
                "available_gb": round(memory_available, 2),
                "total_gb": round(memory_total, 2),
                "status": "正常" if memory_percent < 80 else "紧张" if memory_percent < 95 else "严重不足"
            },
            "disk": {
                "usage_percent": round(disk_percent, 2),
                "free_gb": round(disk_free, 2),
                "status": "正常" if disk_percent < 80 else "空间紧张" if disk_percent < 95 else "空间严重不足"
            },
            "network": {
                "connections": connections,
                "status": "正常" if connections < 1000 else "连接较多"
            }
        }
        
        self.analysis_results["resources"] = resource_analysis
        return resource_analysis
    
    def analyze_process_stability(self) -> Dict[str, Any]:
        """分析进程稳定性"""
        self.log("🔍 分析进程稳定性...")
        
        # 查找相关进程
        target_processes = ['python', 'node', 'cloudflared', 'vite']
        process_info = {}
        zombie_processes = []
        high_memory_processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'status', 'memory_percent', 'cpu_percent', 'cmdline', 'create_time']):
            try:
                proc_info = proc.info
                cmdline = ' '.join(proc_info['cmdline'] or [])
                
                # 检查是否是目标进程
                is_target = any(target in proc_info['name'].lower() for target in target_processes)
                is_nexus_related = any(keyword in cmdline.lower() for keyword in ['nexus', 'rag', 'smart_rag_server', 'vite'])
                
                if is_target or is_nexus_related:
                    # 计算运行时间
                    create_time = datetime.fromtimestamp(proc_info['create_time'])
                    uptime = datetime.now() - create_time
                    
                    process_data = {
                        'pid': proc_info['pid'],
                        'name': proc_info['name'],
                        'status': proc_info['status'],
                        'memory_percent': proc_info['memory_percent'],
                        'cpu_percent': proc_info['cpu_percent'],
                        'cmdline': cmdline[:100] + '...' if len(cmdline) > 100 else cmdline,
                        'uptime_seconds': uptime.total_seconds(),
                        'uptime_human': str(uptime).split('.')[0]
                    }
                    
                    process_info[proc_info['pid']] = process_data
                    
                    # 检查僵尸进程
                    if proc_info['status'] in ['zombie', 'stopped']:
                        zombie_processes.append(process_data)
                    
                    # 检查高内存使用
                    if proc_info['memory_percent'] > 10:  # 超过10%内存
                        high_memory_processes.append(process_data)
                        
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        
        stability_analysis = {
            "total_processes": len(process_info),
            "zombie_processes": zombie_processes,
            "high_memory_processes": high_memory_processes,
            "process_details": process_info,
            "stability_score": self.calculate_stability_score(process_info, zombie_processes, high_memory_processes)
        }
        
        self.analysis_results["processes"] = stability_analysis
        return stability_analysis
    
    def calculate_stability_score(self, processes: Dict, zombies: List, high_memory: List) -> Dict[str, Any]:
        """计算稳定性分数"""
        score = 100
        issues = []
        
        # 僵尸进程扣分
        if zombies:
            score -= len(zombies) * 20
            issues.append(f"{len(zombies)} 个僵尸进程")
        
        # 高内存使用扣分
        if high_memory:
            score -= len(high_memory) * 10
            issues.append(f"{len(high_memory)} 个高内存使用进程")
        
        # 进程数量过多扣分
        if len(processes) > 10:
            score -= (len(processes) - 10) * 5
            issues.append(f"进程数量过多 ({len(processes)} 个)")
        
        # 短时间内重启的进程扣分
        recent_restarts = [p for p in processes.values() if p['uptime_seconds'] < 300]  # 5分钟内
        if recent_restarts:
            score -= len(recent_restarts) * 15
            issues.append(f"{len(recent_restarts)} 个进程最近重启")
        
        score = max(0, score)
        
        if score >= 90:
            status = "优秀"
        elif score >= 70:
            status = "良好"
        elif score >= 50:
            status = "一般"
        else:
            status = "差"
        
        return {
            "score": score,
            "status": status,
            "issues": issues
        }
    
    def analyze_port_conflicts(self) -> Dict[str, Any]:
        """分析端口冲突"""
        self.log("🔍 分析端口冲突...")
        
        # 常用端口范围
        port_ranges = {
            "rag_ports": range(5000, 5010),
            "frontend_ports": range(52300, 52310),
            "energy_ports": range(56400, 56410)
        }
        
        port_usage = {}
        conflicts = []
        
        # 获取所有网络连接
        connections = psutil.net_connections(kind='inet')
        
        for conn in connections:
            if conn.laddr:
                port = conn.laddr.port
                status = conn.status
                
                if port not in port_usage:
                    port_usage[port] = []
                
                port_usage[port].append({
                    'status': status,
                    'pid': conn.pid
                })
        
        # 检查目标端口范围的冲突
        for range_name, port_range in port_ranges.items():
            range_conflicts = []
            for port in port_range:
                if port in port_usage:
                    processes = port_usage[port]
                    if len(processes) > 1:
                        range_conflicts.append({
                            'port': port,
                            'processes': processes
                        })
            
            if range_conflicts:
                conflicts.append({
                    'range_name': range_name,
                    'conflicts': range_conflicts
                })
        
        port_analysis = {
            "total_ports_used": len(port_usage),
            "conflicts": conflicts,
            "port_usage_summary": {
                range_name: [port for port in port_range if port in port_usage]
                for range_name, port_range in port_ranges.items()
            }
        }
        
        self.analysis_results["ports"] = port_analysis
        return port_analysis
    
    def analyze_log_files(self) -> Dict[str, Any]:
        """分析日志文件"""
        self.log("🔍 分析日志文件...")
        
        log_files = [
            self.log_dir / "rag_server.log",
            self.log_dir / "frontend_server.log",
            self.log_dir / "nexus_tunnel.log",
            self.log_dir / "rag_tunnel.log"
        ]
        
        log_analysis = {}
        error_patterns = [
            "error", "Error", "ERROR",
            "exception", "Exception", "EXCEPTION",
            "failed", "Failed", "FAILED",
            "timeout", "Timeout", "TIMEOUT",
            "connection refused", "Connection refused",
            "port already in use", "Port already in use"
        ]
        
        for log_file in log_files:
            if log_file.exists():
                try:
                    with open(log_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # 统计错误
                    errors = []
                    for pattern in error_patterns:
                        if pattern in content:
                            lines = content.split('\n')
                            error_lines = [line for line in lines if pattern in line]
                            errors.extend(error_lines[-5:])  # 最近5个错误
                    
                    # 文件大小和修改时间
                    stat = log_file.stat()
                    
                    log_analysis[log_file.name] = {
                        "exists": True,
                        "size_bytes": stat.st_size,
                        "modified_time": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        "error_count": len(errors),
                        "recent_errors": errors[:10]  # 最多显示10个错误
                    }
                    
                except Exception as e:
                    log_analysis[log_file.name] = {
                        "exists": True,
                        "error": f"读取失败: {e}"
                    }
            else:
                log_analysis[log_file.name] = {
                    "exists": False
                }
        
        self.analysis_results["logs"] = log_analysis
        return log_analysis
    
    def analyze_dependency_issues(self) -> Dict[str, Any]:
        """分析依赖问题"""
        self.log("🔍 分析依赖问题...")
        
        dependency_analysis = {
            "python_packages": {},
            "node_packages": {},
            "system_tools": {}
        }
        
        # 检查Python包
        try:
            result = subprocess.run([sys.executable, '-m', 'pip', 'list'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                packages = result.stdout.split('\n')[2:]  # 跳过标题行
                dependency_analysis["python_packages"]["status"] = "可用"
                dependency_analysis["python_packages"]["count"] = len([p for p in packages if p.strip()])
            else:
                dependency_analysis["python_packages"]["status"] = "错误"
                dependency_analysis["python_packages"]["error"] = result.stderr
        except Exception as e:
            dependency_analysis["python_packages"]["status"] = "检查失败"
            dependency_analysis["python_packages"]["error"] = str(e)
        
        # 检查Node.js和npm
        for tool in ['node', 'npm']:
            try:
                result = subprocess.run([tool, '--version'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    dependency_analysis["system_tools"][tool] = {
                        "status": "可用",
                        "version": result.stdout.strip()
                    }
                else:
                    dependency_analysis["system_tools"][tool] = {
                        "status": "不可用",
                        "error": result.stderr
                    }
            except Exception as e:
                dependency_analysis["system_tools"][tool] = {
                    "status": "检查失败",
                    "error": str(e)
                }
        
        # 检查cloudflared
        try:
            result = subprocess.run(['cloudflared', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                dependency_analysis["system_tools"]["cloudflared"] = {
                    "status": "可用",
                    "version": result.stdout.strip()
                }
            else:
                dependency_analysis["system_tools"]["cloudflared"] = {
                    "status": "不可用",
                    "error": result.stderr
                }
        except Exception as e:
            dependency_analysis["system_tools"]["cloudflared"] = {
                "status": "检查失败",
                "error": str(e)
            }
        
        self.analysis_results["dependencies"] = dependency_analysis
        return dependency_analysis
    
    def generate_stability_recommendations(self) -> List[str]:
        """生成稳定性建议"""
        recommendations = []
        
        # 基于资源分析的建议
        if "resources" in self.analysis_results:
            resources = self.analysis_results["resources"]
            
            if resources["memory"]["status"] != "正常":
                recommendations.append("🔧 内存使用率过高，建议：")
                recommendations.append("  - 重启高内存使用的进程")
                recommendations.append("  - 增加系统内存或使用swap")
                recommendations.append("  - 优化应用程序内存使用")
            
            if resources["cpu"]["status"] != "正常":
                recommendations.append("🔧 CPU使用率过高，建议：")
                recommendations.append("  - 检查是否有死循环或无限递归")
                recommendations.append("  - 优化算法和代码逻辑")
                recommendations.append("  - 考虑使用多进程或异步处理")
        
        # 基于进程分析的建议
        if "processes" in self.analysis_results:
            processes = self.analysis_results["processes"]
            
            if processes["zombie_processes"]:
                recommendations.append("🔧 发现僵尸进程，建议：")
                recommendations.append("  - 使用 kill -9 强制终止僵尸进程")
                recommendations.append("  - 检查父进程是否正确处理子进程退出")
                recommendations.append("  - 使用进程管理工具如supervisor")
            
            if processes["stability_score"]["score"] < 70:
                recommendations.append("🔧 进程稳定性较差，建议：")
                recommendations.append("  - 使用nohup或screen运行长期进程")
                recommendations.append("  - 添加进程监控和自动重启机制")
                recommendations.append("  - 检查进程日志找出崩溃原因")
        
        # 基于端口分析的建议
        if "ports" in self.analysis_results:
            ports = self.analysis_results["ports"]
            
            if ports["conflicts"]:
                recommendations.append("🔧 发现端口冲突，建议：")
                recommendations.append("  - 使用动态端口分配")
                recommendations.append("  - 在启动前检查端口可用性")
                recommendations.append("  - 终止占用端口的无用进程")
        
        # 基于日志分析的建议
        if "logs" in self.analysis_results:
            logs = self.analysis_results["logs"]
            
            high_error_logs = [name for name, info in logs.items() 
                             if info.get("exists") and info.get("error_count", 0) > 5]
            
            if high_error_logs:
                recommendations.append("🔧 发现大量错误日志，建议：")
                recommendations.append("  - 检查错误日志找出根本原因")
                recommendations.append("  - 修复配置或代码问题")
                recommendations.append("  - 定期清理和轮转日志文件")
        
        # 通用稳定性建议
        recommendations.extend([
            "",
            "🛡️ 通用稳定性建议：",
            "  - 使用进程管理器（如systemd、supervisor）",
            "  - 实现健康检查和自动重启",
            "  - 设置资源限制防止资源耗尽",
            "  - 定期监控系统状态",
            "  - 使用容器化部署提高隔离性",
            "  - 实现优雅关闭和错误恢复机制"
        ])
        
        return recommendations
    
    def fix_common_issues(self):
        """修复常见问题"""
        self.log("🔧 开始修复常见问题...")
        
        fixed_issues = []
        
        # 1. 清理僵尸进程
        if "processes" in self.analysis_results:
            zombie_processes = self.analysis_results["processes"]["zombie_processes"]
            for zombie in zombie_processes:
                try:
                    pid = zombie['pid']
                    os.kill(pid, 9)
                    fixed_issues.append(f"清理僵尸进程 PID {pid}")
                except:
                    pass
        
        # 2. 清理临时文件
        temp_patterns = [
            "/tmp/*.log",
            "/tmp/nexus_*",
            "/tmp/rag_*"
        ]
        
        for pattern in temp_patterns:
            try:
                import glob
                files = glob.glob(pattern)
                for file in files:
                    file_path = Path(file)
                    if file_path.exists() and file_path.stat().st_size > 100 * 1024 * 1024:  # 大于100MB
                        file_path.unlink()
                        fixed_issues.append(f"清理大型临时文件: {file}")
            except:
                pass
        
        # 3. 重置端口（如果有冲突）
        # 这里可以添加端口重置逻辑
        
        self.log(f"✅ 修复完成，共修复 {len(fixed_issues)} 个问题")
        for issue in fixed_issues:
            self.log(f"  - {issue}")
        
        return fixed_issues
    
    def run_full_analysis(self):
        """运行完整分析"""
        self.log("🚀 开始系统稳定性分析...")
        
        # 运行各项分析
        self.analyze_system_resources()
        self.analyze_process_stability()
        self.analyze_port_conflicts()
        self.analyze_log_files()
        self.analyze_dependency_issues()
        
        # 生成建议
        recommendations = self.generate_stability_recommendations()
        
        # 生成报告
        report = {
            "analysis_time": datetime.now().isoformat(),
            "analysis_results": self.analysis_results,
            "recommendations": recommendations,
            "summary": self.generate_summary()
        }
        
        # 保存报告
        report_file = self.project_root / "system_stability_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        self.log(f"📊 分析报告已保存: {report_file}")
        
        # 显示摘要
        self.display_summary(report)
        
        return report
    
    def generate_summary(self) -> Dict[str, Any]:
        """生成分析摘要"""
        summary = {
            "overall_status": "良好",
            "critical_issues": 0,
            "warnings": 0,
            "recommendations_count": 0
        }
        
        # 统计问题
        if "processes" in self.analysis_results:
            stability_score = self.analysis_results["processes"]["stability_score"]["score"]
            if stability_score < 50:
                summary["overall_status"] = "差"
                summary["critical_issues"] += 1
            elif stability_score < 70:
                summary["overall_status"] = "一般"
                summary["warnings"] += 1
        
        if "resources" in self.analysis_results:
            resources = self.analysis_results["resources"]
            if resources["memory"]["status"] == "严重不足":
                summary["critical_issues"] += 1
            elif resources["memory"]["status"] == "紧张":
                summary["warnings"] += 1
        
        return summary
    
    def display_summary(self, report: Dict[str, Any]):
        """显示分析摘要"""
        self.log("\n" + "="*60)
        self.log("📊 系统稳定性分析报告")
        self.log("="*60)
        
        summary = report["summary"]
        self.log(f"🎯 总体状态: {summary['overall_status']}")
        self.log(f"🚨 严重问题: {summary['critical_issues']} 个")
        self.log(f"⚠️  警告: {summary['warnings']} 个")
        
        # 显示资源状态
        if "resources" in self.analysis_results:
            resources = self.analysis_results["resources"]
            self.log(f"\n💻 系统资源:")
            self.log(f"  CPU: {resources['cpu']['usage_percent']:.1f}% ({resources['cpu']['status']})")
            self.log(f"  内存: {resources['memory']['usage_percent']:.1f}% ({resources['memory']['status']})")
            self.log(f"  磁盘: {resources['disk']['usage_percent']:.1f}% ({resources['disk']['status']})")
        
        # 显示进程状态
        if "processes" in self.analysis_results:
            processes = self.analysis_results["processes"]
            stability = processes["stability_score"]
            self.log(f"\n🔄 进程状态:")
            self.log(f"  稳定性评分: {stability['score']}/100 ({stability['status']})")
            self.log(f"  运行进程: {processes['total_processes']} 个")
            self.log(f"  僵尸进程: {len(processes['zombie_processes'])} 个")
        
        # 显示建议
        recommendations = report["recommendations"]
        if recommendations:
            self.log(f"\n💡 改进建议:")
            for rec in recommendations[:5]:  # 显示前5个建议
                if rec.strip():
                    self.log(f"  {rec}")
        
        self.log("="*60)

def main():
    analyzer = SystemStabilityAnalyzer()
    
    import argparse
    parser = argparse.ArgumentParser(description='系统稳定性分析工具')
    parser.add_argument('--fix', action='store_true', help='自动修复常见问题')
    parser.add_argument('--monitor', action='store_true', help='持续监控模式')
    
    args = parser.parse_args()
    
    # 运行分析
    report = analyzer.run_full_analysis()
    
    # 自动修复
    if args.fix:
        analyzer.fix_common_issues()
    
    # 持续监控
    if args.monitor:
        analyzer.log("👁️ 进入持续监控模式...")
        try:
            while True:
                time.sleep(60)  # 每分钟检查一次
                analyzer.analyze_system_resources()
                analyzer.analyze_process_stability()
        except KeyboardInterrupt:
            analyzer.log("监控已停止")

if __name__ == "__main__":
    main()