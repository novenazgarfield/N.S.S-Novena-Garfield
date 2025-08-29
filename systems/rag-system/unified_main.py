#!/usr/bin/env python3
"""
🚀 RAG系统统一主入口
==================

整合所有启动脚本功能，提供统一的CLI接口
- 支持所有原有启动方式
- 统一的命令行参数
- 向后兼容保证

使用方法:
    python unified_main.py --mode intelligence  # 智能大脑模式
    python unified_main.py --mode enhanced     # 增强版模式
    python unified_main.py --mode basic        # 基础版模式
    python unified_main.py --mode simple       # 简化版模式
    python unified_main.py --mode online       # 在线版模式
"""

import argparse
import sys
import os
from pathlib import Path
import subprocess
from typing import Optional

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent))

from utils.logger import logger
from unified_config import config_manager

class UnifiedRAGLauncher:
    """统一RAG启动器"""
    
    def __init__(self):
        self.modes = {
            "intelligence": {
                "name": "智能大脑",
                "app": "intelligence_app.py",
                "description": "最新的中央情报大脑系统"
            },
            "enhanced": {
                "name": "增强版",
                "app": "app_enhanced.py", 
                "description": "支持多API切换和分布式计算监控"
            },
            "basic": {
                "name": "基础版",
                "app": "app.py",
                "description": "标准RAG功能，稳定可靠"
            },
            "simple": {
                "name": "简化版",
                "app": "app_simple.py",
                "description": "轻量级版本，快速启动"
            },
            "online": {
                "name": "在线版",
                "app": "app_online.py",
                "description": "在线部署版本，支持远程访问"
            },
            "unified": {
                "name": "统一版",
                "app": "unified_app.py",
                "description": "新的统一界面，包含所有功能"
            }
        }
    
    def parse_args(self):
        """解析命令行参数"""
        parser = argparse.ArgumentParser(
            description="RAG智能系统统一启动器",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog=self._get_help_text()
        )
        
        parser.add_argument(
            "--mode", "-m",
            choices=list(self.modes.keys()),
            default="unified",
            help="选择运行模式"
        )
        
        parser.add_argument(
            "--port", "-p",
            type=int,
            default=8501,
            help="Streamlit服务端口 (默认: 8501)"
        )
        
        parser.add_argument(
            "--host",
            default="localhost",
            help="服务主机地址 (默认: localhost)"
        )
        
        parser.add_argument(
            "--debug",
            action="store_true",
            help="启用调试模式"
        )
        
        parser.add_argument(
            "--config",
            help="指定配置文件路径"
        )
        
        parser.add_argument(
            "--list-modes",
            action="store_true",
            help="列出所有可用模式"
        )
        
        return parser.parse_args()
    
    def _get_help_text(self):
        """获取帮助文本"""
        help_text = "\n可用模式:\n"
        for mode, info in self.modes.items():
            help_text += f"  {mode:<12} - {info['name']}: {info['description']}\n"
        
        help_text += "\n使用示例:\n"
        help_text += "  python unified_main.py --mode intelligence\n"
        help_text += "  python unified_main.py --mode enhanced --port 8502\n"
        help_text += "  python unified_main.py --mode basic --debug\n"
        
        return help_text
    
    def list_modes(self):
        """列出所有可用模式"""
        print("🎯 RAG系统可用模式:")
        print("=" * 50)
        
        for mode, info in self.modes.items():
            status = "✅" if self._check_app_exists(info['app']) else "❌"
            print(f"{status} {mode:<12} - {info['name']}")
            print(f"   📝 {info['description']}")
            print(f"   📄 应用文件: {info['app']}")
            print()
    
    def _check_app_exists(self, app_file: str) -> bool:
        """检查应用文件是否存在"""
        app_path = Path(__file__).parent / app_file
        return app_path.exists()
    
    def run(self, args):
        """运行指定模式的应用"""
        mode = args.mode
        
        if args.list_modes:
            self.list_modes()
            return
        
        if mode not in self.modes:
            logger.error(f"不支持的模式: {mode}")
            self.list_modes()
            return
        
        mode_info = self.modes[mode]
        app_file = mode_info['app']
        
        # 检查应用文件是否存在
        app_path = Path(__file__).parent / app_file
        if not app_path.exists():
            logger.error(f"应用文件不存在: {app_file}")
            return
        
        # 设置环境变量
        env = os.environ.copy()
        if args.debug:
            env['STREAMLIT_LOGGER_LEVEL'] = 'debug'
        
        if args.config:
            env['RAG_CONFIG_FILE'] = args.config
        
        # 构建Streamlit命令
        cmd = [
            sys.executable, "-m", "streamlit", "run",
            str(app_path),
            "--server.port", str(args.port),
            "--server.address", args.host,
            "--server.headless", "true",
            "--browser.gatherUsageStats", "false"
        ]
        
        logger.info(f"启动 {mode_info['name']} 模式...")
        logger.info(f"访问地址: http://{args.host}:{args.port}")
        
        try:
            # 启动Streamlit应用
            subprocess.run(cmd, env=env, check=True)
        except KeyboardInterrupt:
            logger.info("用户中断，正在关闭...")
        except subprocess.CalledProcessError as e:
            logger.error(f"启动失败: {e}")
        except Exception as e:
            logger.error(f"未知错误: {e}")

def main():
    """主函数"""
    launcher = UnifiedRAGLauncher()
    args = launcher.parse_args()
    launcher.run(args)

if __name__ == "__main__":
    main()