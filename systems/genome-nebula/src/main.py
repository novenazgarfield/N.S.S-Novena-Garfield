#!/usr/bin/env python3
"""
Genome Jigsaw 主程序入口
"""

import sys
import os
import argparse
import logging
from pathlib import Path

# 添加项目路径
sys.path.append(str(Path(__file__).parent))

from core.config import Config
from core.logger import setup_logger
from web.app import create_app

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Genome Jigsaw - 基因组测序分析系统")
    parser.add_argument("--config", "-c", help="配置文件路径", default="config/default.yaml")
    parser.add_argument("--mode", "-m", choices=["web", "cli", "api"], default="web", help="运行模式")
    parser.add_argument("--host", default="0.0.0.0", help="Web服务器主机地址")
    parser.add_argument("--port", type=int, default=8080, help="Web服务器端口")
    parser.add_argument("--debug", action="store_true", help="启用调试模式")
    
    args = parser.parse_args()
    
    # 初始化配置
    config = Config(args.config)
    
    # 设置日志
    logger = setup_logger(
        level=logging.DEBUG if args.debug else logging.INFO,
        log_file=config.get("logging.file", "logs/genome_jigsaw.log")
    )
    
    logger.info("🧬 启动 Genome Jigsaw 基因组测序分析系统")
    logger.info(f"   运行模式: {args.mode}")
    logger.info(f"   配置文件: {args.config}")
    
    try:
        if args.mode == "web":
            # Web模式
            app = create_app(config)
            logger.info(f"🌐 启动Web服务器: http://{args.host}:{args.port}")
            app.run(host=args.host, port=args.port, debug=args.debug)
            
        elif args.mode == "cli":
            # 命令行模式
            from cli.main import run_cli
            run_cli(config)
            
        elif args.mode == "api":
            # API模式
            from api.main import run_api
            run_api(config, host=args.host, port=args.port)
            
    except KeyboardInterrupt:
        logger.info("👋 用户中断，正在关闭系统...")
    except Exception as e:
        logger.error(f"❌ 系统启动失败: {e}")
        sys.exit(1)
    
    logger.info("✅ Genome Jigsaw 系统已关闭")

if __name__ == "__main__":
    main()