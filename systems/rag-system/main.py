#!/usr/bin/env python3
"""
RAG系统统一入口点
支持多种运行模式：web, desktop, mobile, api, cli
"""
import sys
import argparse
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.config.config_manager import init_config, get_config
from utils.logger import logger

def setup_logging():
    """设置日志"""
    import logging
    config = get_config()
    
    # 配置根日志器
    logging.basicConfig(
        level=getattr(logging, config.system.log_level),
        format=config.get('logging.format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(config.storage.logs_dir / config.get('logging.file', 'rag_system.log'))
        ]
    )

def run_web_interface():
    """运行Web界面"""
    logger.info("启动Web界面...")
    
    try:
        # 导入并运行原有的streamlit应用
        from src.interfaces.web import run_web_app
        run_web_app()
    except ImportError:
        # 如果新接口还没创建，使用原有的app.py
        logger.info("使用原有Web界面...")
        import subprocess
        import os
        
        config = get_config()
        port = config.interfaces.web.get('port', 8501)
        host = config.interfaces.web.get('host', 'localhost')
        
        # 使用原有的app.py启动streamlit
        cmd = [
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port", str(port),
            "--server.address", host
        ]
        
        os.execvp(cmd[0], cmd)

def run_desktop_interface():
    """运行桌面界面"""
    logger.info("启动桌面界面...")
    
    try:
        from src.interfaces.desktop import run_desktop_app
        run_desktop_app()
    except ImportError:
        # 使用原有的desktop_app.py
        logger.info("使用原有桌面界面...")
        from desktop_app import main as desktop_main
        desktop_main()

def run_mobile_interface():
    """运行移动界面"""
    logger.info("启动移动界面...")
    
    try:
        from src.interfaces.mobile import run_mobile_app
        run_mobile_app()
    except ImportError:
        # 使用原有的mobile_app.py
        logger.info("使用原有移动界面...")
        from mobile_app import main as mobile_main
        mobile_main()

def run_api_server():
    """运行API服务器"""
    logger.info("启动API服务器...")
    
    try:
        from src.api.server import run_api_server
        run_api_server()
    except ImportError:
        # 使用原有的api_server.py
        logger.info("使用原有API服务器...")
        from api_server import main as api_main
        api_main()

def run_cli_interface():
    """运行命令行界面"""
    logger.info("启动命令行界面...")
    
    try:
        from src.interfaces.cli import run_cli_app
        run_cli_app()
    except ImportError:
        # 使用原有的app_simple.py
        logger.info("使用原有命令行界面...")
        from app_simple import main as cli_main
        cli_main()

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="RAG系统统一入口点",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
运行模式:
  web      - Web界面 (默认)
  desktop  - 桌面应用
  mobile   - 移动端界面
  api      - API服务器
  cli      - 命令行界面

示例:
  python main.py --mode web --port 8501
  python main.py --mode api --host 0.0.0.0 --port 8000
  python main.py --mode cli
        """
    )
    
    parser.add_argument(
        '--mode', '-m',
        choices=['web', 'desktop', 'mobile', 'api', 'cli'],
        default='web',
        help='运行模式 (默认: web)'
    )
    
    parser.add_argument(
        '--config', '-c',
        help='配置文件路径'
    )
    
    parser.add_argument(
        '--host',
        help='服务器主机地址'
    )
    
    parser.add_argument(
        '--port', '-p',
        type=int,
        help='服务器端口'
    )
    
    parser.add_argument(
        '--debug', '-d',
        action='store_true',
        help='启用调试模式'
    )
    
    parser.add_argument(
        '--version', '-v',
        action='version',
        version='RAG System 2.0.0'
    )
    
    args = parser.parse_args()
    
    try:
        # 初始化配置
        config = init_config(args.config)
        
        # 设置调试模式
        if args.debug:
            config.system.debug = True
            config.system.log_level = 'DEBUG'
        
        # 设置日志
        setup_logging()
        
        logger.info(f"RAG系统启动 - 模式: {args.mode}")
        logger.info(f"配置文件: {config.config_path}")
        logger.info(f"数据目录: {config.storage.data_dir}")
        
        # 根据模式运行相应的界面
        if args.mode == 'web':
            run_web_interface()
        elif args.mode == 'desktop':
            run_desktop_interface()
        elif args.mode == 'mobile':
            run_mobile_interface()
        elif args.mode == 'api':
            run_api_server()
        elif args.mode == 'cli':
            run_cli_interface()
        else:
            logger.error(f"未知的运行模式: {args.mode}")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("用户中断，正在退出...")
        sys.exit(0)
    except Exception as e:
        logger.error(f"启动失败: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()