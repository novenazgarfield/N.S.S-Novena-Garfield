#!/usr/bin/env python3
"""
Bovine-Insight系统统一入口点
多摄像头牛只身份识别与体况评分系统
"""

import sys
import argparse
import os
import logging
from pathlib import Path
import yaml
import time

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.utils.config_manager import ConfigManager
from src.utils.logger import setup_logging

class BovineStarter:
    """Bovine-Insight系统启动器"""
    
    def __init__(self):
        self.config_manager = None
        self.config = None
        self.logger = None
    
    def start(self, mode, options=None):
        """主启动函数"""
        if options is None:
            options = {}
            
        try:
            print("🐄 Bovine-Insight - 多摄像头牛只身份识别与体况评分系统")
            print("=" * 60)
            print(f"📍 运行模式: {mode}")
            print("")
            
            # 初始化配置
            self.init_config(options.get('config'))
            
            # 设置日志
            self.setup_logging(options.get('debug', False))
            
            # 验证配置
            self.validate_config()
            
            # 根据模式启动相应功能
            if mode == 'system':
                self.start_system_mode(options)
            elif mode == 'detect':
                self.start_detect_mode(options)
            elif mode == 'identify':
                self.start_identify_mode(options)
            elif mode == 'test':
                self.start_test_mode(options)
            elif mode == 'demo':
                self.start_demo_mode(options)
            elif mode == 'status':
                self.show_status()
            elif mode == 'validate':
                self.validate_system()
            else:
                self.show_help()
                sys.exit(1)
                
        except KeyboardInterrupt:
            print("\n🛑 用户中断，正在退出...")
            sys.exit(0)
        except Exception as e:
            print(f"❌ 启动失败: {e}")
            if options.get('debug'):
                import traceback
                traceback.print_exc()
            sys.exit(1)
    
    def init_config(self, config_path=None):
        """初始化配置"""
        try:
            self.config_manager = ConfigManager(config_path)
            self.config = self.config_manager.get_config()
            print("✅ 配置加载成功")
        except Exception as e:
            print(f"❌ 配置加载失败: {e}")
            sys.exit(1)
    
    def setup_logging(self, debug=False):
        """设置日志"""
        log_config = self.config.get('logging', {})
        if debug:
            log_config['level'] = 'DEBUG'
        
        setup_logging(log_config)
        self.logger = logging.getLogger(__name__)
        self.logger.info("日志系统初始化完成")
    
    def validate_config(self):
        """验证配置"""
        errors = []
        
        # 检查摄像头配置
        cameras = self.config.get('cameras', {})
        if not cameras:
            errors.append("未配置摄像头")
        
        # 检查检测配置
        detection = self.config.get('detection', {})
        if not detection.get('model'):
            errors.append("未配置检测模型")
        
        # 检查模型目录
        models_dir = Path(detection.get('models_dir', 'models'))
        if not models_dir.exists():
            models_dir.mkdir(parents=True, exist_ok=True)
            print(f"📁 创建模型目录: {models_dir}")
        
        if errors:
            print("❌ 配置验证失败:")
            for error in errors:
                print(f"   {error}")
            sys.exit(1)
        
        print("✅ 配置验证通过")
    
    def start_system_mode(self, options):
        """启动完整系统模式"""
        print("🚀 启动完整系统模式...")
        
        try:
            # 导入并启动主系统
            from src.main import BovineInsightSystem
            
            system = BovineInsightSystem(self.config_manager.config_path)
            
            print("🎯 系统初始化完成，开始运行...")
            system.run()
            
        except ImportError as e:
            print(f"❌ 导入系统模块失败: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"❌ 系统运行失败: {e}")
            if options.get('debug'):
                import traceback
                traceback.print_exc()
            sys.exit(1)
    
    def start_detect_mode(self, options):
        """启动检测模式"""
        print("🔍 启动检测模式...")
        
        try:
            from src.detection import CattleDetector, ModelManager
            
            # 初始化检测器
            model_manager = ModelManager(self.config['detection'])
            detector = CattleDetector(model_manager)
            
            print("✅ 检测器初始化完成")
            
            # 检测模式的具体实现
            if options.get('input'):
                self.run_detection_on_input(detector, options['input'])
            else:
                self.run_detection_interactive(detector)
                
        except ImportError as e:
            print(f"❌ 导入检测模块失败: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"❌ 检测模式启动失败: {e}")
            sys.exit(1)
    
    def start_identify_mode(self, options):
        """启动识别模式"""
        print("🆔 启动识别模式...")
        
        try:
            from src.identification import FusedIdentifier
            
            # 初始化识别器
            identifier = FusedIdentifier(self.config['identification'])
            
            print("✅ 识别器初始化完成")
            
            # 识别模式的具体实现
            if options.get('input'):
                self.run_identification_on_input(identifier, options['input'])
            else:
                self.run_identification_interactive(identifier)
                
        except ImportError as e:
            print(f"❌ 导入识别模块失败: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"❌ 识别模式启动失败: {e}")
            sys.exit(1)
    
    def start_test_mode(self, options):
        """启动测试模式"""
        print("🧪 启动测试模式...")
        
        test_scripts = [
            'scripts/simple_test.py',
            'scripts/test_system.py'
        ]
        
        for script in test_scripts:
            script_path = project_root / script
            if script_path.exists():
                print(f"   运行: {script}")
                try:
                    import subprocess
                    result = subprocess.run([sys.executable, str(script_path)], 
                                          capture_output=True, text=True)
                    if result.returncode == 0:
                        print(f"   {script}: ✅ 通过")
                    else:
                        print(f"   {script}: ❌ 失败")
                        if options.get('verbose'):
                            print(f"   错误: {result.stderr}")
                except Exception as e:
                    print(f"   {script}: ❌ 错误 - {e}")
            else:
                print(f"   {script}: ⚠️ 文件不存在")
        
        print("🧪 测试完成")
    
    def start_demo_mode(self, options):
        """启动演示模式"""
        print("🎭 启动演示模式...")
        
        # 演示模式的实现
        print("📸 模拟摄像头数据...")
        print("🔍 模拟检测过程...")
        print("🆔 模拟识别过程...")
        print("📊 模拟结果输出...")
        
        # 简单的演示循环
        try:
            for i in range(5):
                print(f"   演示步骤 {i+1}/5: 处理中...")
                time.sleep(1)
            print("✅ 演示完成")
        except KeyboardInterrupt:
            print("\n⏹️ 演示被中断")
    
    def show_status(self):
        """显示系统状态"""
        print("📊 Bovine-Insight系统状态:")
        print(f"   配置文件: {self.config_manager.config_path}")
        print("")
        
        # 摄像头状态
        cameras = self.config.get('cameras', {})
        print("📸 摄像头配置:")
        for name, camera_config in cameras.items():
            print(f"   {name}: ID={camera_config.get('id')}, 类型={camera_config.get('type')}")
        print("")
        
        # 检测配置
        detection = self.config.get('detection', {})
        print("🔍 检测配置:")
        print(f"   模型: {detection.get('model')}")
        print(f"   设备: {detection.get('device')}")
        print(f"   置信度阈值: {detection.get('confidence_threshold')}")
        print("")
        
        # 识别配置
        identification = self.config.get('identification', {})
        print("🆔 识别配置:")
        print(f"   融合策略: {identification.get('fusion_strategy')}")
        print(f"   耳标识别: {'启用' if identification.get('ear_tag', {}).get('use_tesseract') else '禁用'}")
        print(f"   花色识别: {'启用' if identification.get('coat_pattern', {}).get('extractor_type') else '禁用'}")
        print("")
        
        # 检查依赖
        print("📦 依赖检查:")
        self.check_dependencies()
    
    def validate_system(self):
        """验证系统完整性"""
        print("🔧 验证系统完整性...")
        
        # 检查配置文件
        print("   配置文件: ✅ 正常")
        
        # 检查模块导入
        modules_to_check = [
            'src.data_processing',
            'src.detection',
            'src.identification',
            'src.database.cattle_database',
            'src.utils.config_manager'
        ]
        
        for module in modules_to_check:
            try:
                __import__(module)
                print(f"   {module}: ✅ 正常")
            except ImportError as e:
                print(f"   {module}: ❌ 导入失败 - {e}")
        
        # 检查必要目录
        dirs_to_check = ['models', 'data', 'logs']
        for dir_name in dirs_to_check:
            dir_path = project_root / dir_name
            if dir_path.exists():
                print(f"   {dir_name}/: ✅ 存在")
            else:
                print(f"   {dir_name}/: ⚠️ 不存在")
        
        print("✅ 系统验证完成")
    
    def check_dependencies(self):
        """检查依赖包"""
        required_packages = [
            'opencv-python',
            'numpy',
            'torch',
            'ultralytics',
            'pytesseract',
            'easyocr',
            'sqlite3'
        ]
        
        for package in required_packages:
            try:
                if package == 'opencv-python':
                    import cv2
                elif package == 'sqlite3':
                    import sqlite3
                else:
                    __import__(package)
                print(f"   {package}: ✅ 已安装")
            except ImportError:
                print(f"   {package}: ❌ 未安装")
    
    def run_detection_on_input(self, detector, input_path):
        """在指定输入上运行检测"""
        print(f"🔍 在输入 {input_path} 上运行检测...")
        # 具体的检测实现
        pass
    
    def run_detection_interactive(self, detector):
        """交互式检测模式"""
        print("🔍 交互式检测模式 (输入 'quit' 退出):")
        while True:
            try:
                user_input = input("请输入图片路径或摄像头ID: ").strip()
                if user_input.lower() in ['quit', 'exit', 'q']:
                    break
                # 处理用户输入
                print(f"处理输入: {user_input}")
            except KeyboardInterrupt:
                break
    
    def run_identification_on_input(self, identifier, input_path):
        """在指定输入上运行识别"""
        print(f"🆔 在输入 {input_path} 上运行识别...")
        # 具体的识别实现
        pass
    
    def run_identification_interactive(self, identifier):
        """交互式识别模式"""
        print("🆔 交互式识别模式 (输入 'quit' 退出):")
        while True:
            try:
                user_input = input("请输入图片路径: ").strip()
                if user_input.lower() in ['quit', 'exit', 'q']:
                    break
                # 处理用户输入
                print(f"处理输入: {user_input}")
            except KeyboardInterrupt:
                break
    
    def show_help(self):
        """显示帮助信息"""
        print(f"""
🐄 Bovine-Insight - 多摄像头牛只身份识别与体况评分系统

用法: python bovine.py [模式] [选项]

运行模式:
  system      - 启动完整系统 (默认)
  detect      - 仅检测模式
  identify    - 仅识别模式
  test        - 运行测试
  demo        - 演示模式
  status      - 显示系统状态
  validate    - 验证系统完整性

选项:
  --config <path>    - 指定配置文件路径
  --input <path>     - 指定输入文件/目录 (detect/identify模式)
  --debug            - 启用调试模式
  --verbose          - 详细输出 (test模式)
  --help             - 显示此帮助信息

示例:
  python bovine.py system
  python bovine.py detect --input /path/to/image.jpg
  python bovine.py identify --input /path/to/image.jpg
  python bovine.py test --verbose
  python bovine.py status
  python bovine.py validate

环境变量:
  BOVINE_CONFIG_PATH - 配置文件路径
  BOVINE_DEBUG       - 调试模式
  BOVINE_LOG_LEVEL   - 日志级别
        """)

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="Bovine-Insight系统统一入口点",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        'mode',
        nargs='?',
        default='system',
        choices=['system', 'detect', 'identify', 'test', 'demo', 'status', 'validate'],
        help='运行模式'
    )
    
    parser.add_argument(
        '--config', '-c',
        help='配置文件路径'
    )
    
    parser.add_argument(
        '--input', '-i',
        help='输入文件/目录路径'
    )
    
    parser.add_argument(
        '--debug', '-d',
        action='store_true',
        help='启用调试模式'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='详细输出'
    )
    
    return parser.parse_args()

def main():
    """主函数"""
    args = parse_args()
    
    # 处理环境变量
    if not args.config:
        args.config = os.getenv('BOVINE_CONFIG_PATH')
    
    if not args.debug:
        args.debug = os.getenv('BOVINE_DEBUG', '').lower() in ('true', '1', 'yes')
    
    # 启动系统
    starter = BovineStarter()
    starter.start(args.mode, vars(args))

if __name__ == "__main__":
    main()