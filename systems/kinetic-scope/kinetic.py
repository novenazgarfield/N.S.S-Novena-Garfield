#!/usr/bin/env python3
"""
Kinetic-Scope系统统一入口点
分子动力学模拟系统
"""

import sys
import argparse
import os
import logging
import subprocess
import shutil
from pathlib import Path
import yaml
import time
import json

# 项目根目录
project_root = Path(__file__).parent

class KineticStarter:
    """Kinetic-Scope系统启动器"""
    
    def __init__(self):
        self.config = None
        self.logger = None
        self.project_root = project_root
    
    def start(self, mode, options=None):
        """主启动函数"""
        if options is None:
            options = {}
            
        try:
            print("🔬 Kinetic-Scope - 分子动力学模拟系统")
            print("=" * 45)
            print(f"📍 运行模式: {mode}")
            print("")
            
            # 初始化配置
            self.init_config(options.get('config'))
            
            # 设置日志
            self.setup_logging(options.get('debug', False))
            
            # 根据模式启动相应功能
            if mode == 'pipeline':
                self.run_full_pipeline(options)
            elif mode == 'prepare':
                self.run_system_preparation(options)
            elif mode == 'simulate':
                self.run_simulation(options)
            elif mode == 'analyze':
                self.run_trajectory_analysis(options)
            elif mode == 'batch':
                self.run_batch_processing(options)
            elif mode == 'plot':
                self.run_data_plotting(options)
            elif mode == 'status':
                self.show_status()
            elif mode == 'check-tools':
                self.check_tools()
            elif mode == 'setup':
                self.run_setup()
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
        # 创建默认配置
        self.config = {
            'system': {
                'name': 'Kinetic-Scope',
                'version': '1.0.0',
                'description': '分子动力学模拟系统'
            },
            'paths': {
                'sop_scripts': str(self.project_root / 'sop_scripts'),
                'analysis_tools': str(self.project_root / 'analysis_tools'),
                'utilities': str(self.project_root / 'utilities'),
                'templates': str(self.project_root / 'templates'),
                'examples': str(self.project_root / 'examples'),
                'output': './output',
                'logs': './logs'
            },
            'simulation': {
                'force_field': 'amber99sb-ildn',
                'water_model': 'tip3p',
                'box_type': 'cubic',
                'box_size': 1.0,
                'salt_concentration': 0.15,
                'positive_ion': 'NA',
                'negative_ion': 'CL',
                'nproc': os.cpu_count()
            },
            'analysis': {
                'figure_size': [10, 6],
                'dpi': 300,
                'font_size': 12
            }
        }
        
        # 如果提供了配置文件，尝试加载
        if config_path and Path(config_path).exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    user_config = yaml.safe_load(f)
                    self.config.update(user_config)
                print(f"✅ 配置加载成功: {config_path}")
            except Exception as e:
                print(f"⚠️ 配置加载失败，使用默认配置: {e}")
        else:
            print("✅ 使用默认配置")
    
    def setup_logging(self, debug=False):
        """设置日志"""
        log_level = logging.DEBUG if debug else logging.INFO
        log_dir = Path(self.config.get('paths', {}).get('logs', 'logs'))
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / 'kinetic_scope.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info("日志系统初始化完成")
    
    def run_full_pipeline(self, options):
        """运行完整流水线"""
        print("🚀 运行完整分子动力学模拟流水线...")
        
        # 检查输入文件
        input_pdb = options.get('input')
        if not input_pdb:
            print("❌ 请指定输入PDB文件 --input")
            sys.exit(1)
        
        if not Path(input_pdb).exists():
            print(f"❌ 输入PDB文件不存在: {input_pdb}")
            sys.exit(1)
        
        # 检查GROMACS工具
        if not self.check_gromacs_tools():
            print("❌ 缺少GROMACS工具，请先安装GROMACS")
            sys.exit(1)
        
        # 创建工作目录
        work_dir = Path(options.get('output', 'output'))
        work_dir.mkdir(exist_ok=True)
        
        print(f"📁 工作目录: {work_dir}")
        
        # 步骤1: 系统准备
        print("\n🔧 步骤1: 系统准备...")
        self.run_sop_script('sop_prepare_system.sh', {
            'INPUT_PDB': input_pdb,
            'SYSTEM_NAME': options.get('name', 'system'),
            'NPROC': str(options.get('nproc', self.config['simulation']['nproc']))
        }, work_dir)
        
        # 步骤2: 运行模拟
        if not options.get('skip_simulation'):
            print("\n🏃 步骤2: 运行模拟...")
            self.run_sop_script('sop_run_simulation.sh', {
                'SYSTEM_NAME': options.get('name', 'system'),
                'NPROC': str(options.get('nproc', self.config['simulation']['nproc']))
            }, work_dir)
        
        # 步骤3: 轨迹分析
        if not options.get('skip_analysis'):
            print("\n📊 步骤3: 轨迹分析...")
            self.run_sop_script('sop_analyze_trajectory.sh', {
                'SYSTEM_NAME': options.get('name', 'system'),
                'NPROC': str(options.get('nproc', self.config['simulation']['nproc']))
            }, work_dir)
        
        print("\n✅ 完整流水线运行完成")
    
    def run_system_preparation(self, options):
        """运行系统准备"""
        print("🔧 运行系统准备...")
        
        input_pdb = options.get('input')
        if not input_pdb:
            print("❌ 请指定输入PDB文件 --input")
            sys.exit(1)
        
        work_dir = Path(options.get('output', 'output'))
        work_dir.mkdir(exist_ok=True)
        
        self.run_sop_script('sop_prepare_system.sh', {
            'INPUT_PDB': input_pdb,
            'SYSTEM_NAME': options.get('name', 'system'),
            'NPROC': str(options.get('nproc', self.config['simulation']['nproc']))
        }, work_dir)
    
    def run_simulation(self, options):
        """运行模拟"""
        print("🏃 运行分子动力学模拟...")
        
        work_dir = Path(options.get('output', 'output'))
        if not work_dir.exists():
            print(f"❌ 工作目录不存在: {work_dir}")
            sys.exit(1)
        
        self.run_sop_script('sop_run_simulation.sh', {
            'SYSTEM_NAME': options.get('name', 'system'),
            'NPROC': str(options.get('nproc', self.config['simulation']['nproc']))
        }, work_dir)
    
    def run_trajectory_analysis(self, options):
        """运行轨迹分析"""
        print("📊 运行轨迹分析...")
        
        work_dir = Path(options.get('output', 'output'))
        if not work_dir.exists():
            print(f"❌ 工作目录不存在: {work_dir}")
            sys.exit(1)
        
        self.run_sop_script('sop_analyze_trajectory.sh', {
            'SYSTEM_NAME': options.get('name', 'system'),
            'NPROC': str(options.get('nproc', self.config['simulation']['nproc']))
        }, work_dir)
    
    def run_batch_processing(self, options):
        """运行批量处理"""
        print("📦 运行批量处理...")
        
        input_dir = options.get('input')
        if not input_dir:
            print("❌ 请指定输入目录 --input")
            sys.exit(1)
        
        if not Path(input_dir).exists():
            print(f"❌ 输入目录不存在: {input_dir}")
            sys.exit(1)
        
        # 运行批量处理脚本
        batch_script = self.project_root / 'utilities' / 'batch_runner.sh'
        if not batch_script.exists():
            print(f"❌ 批量处理脚本不存在: {batch_script}")
            sys.exit(1)
        
        cmd = [
            'bash', str(batch_script),
            input_dir
        ]
        
        if options.get('output'):
            cmd.extend(['--output', options['output']])
        if options.get('nproc'):
            cmd.extend(['--nproc', str(options['nproc'])])
        
        try:
            subprocess.run(cmd, check=True, cwd=self.project_root)
            print("✅ 批量处理完成")
        except subprocess.CalledProcessError as e:
            print(f"❌ 批量处理失败: {e}")
            sys.exit(1)
    
    def run_data_plotting(self, options):
        """运行数据绘图"""
        print("📈 运行数据绘图...")
        
        input_file = options.get('input')
        if not input_file:
            print("❌ 请指定输入XVG文件 --input")
            sys.exit(1)
        
        if not Path(input_file).exists():
            print(f"❌ 输入文件不存在: {input_file}")
            sys.exit(1)
        
        # 运行绘图脚本
        plot_script = self.project_root / 'analysis_tools' / 'plot_results.py'
        if not plot_script.exists():
            print(f"❌ 绘图脚本不存在: {plot_script}")
            sys.exit(1)
        
        cmd = [sys.executable, str(plot_script), input_file]
        
        if options.get('output'):
            cmd.extend(['--output', options['output']])
        if options.get('title'):
            cmd.extend(['--title', options['title']])
        if options.get('xlabel'):
            cmd.extend(['--xlabel', options['xlabel']])
        if options.get('ylabel'):
            cmd.extend(['--ylabel', options['ylabel']])
        
        try:
            subprocess.run(cmd, check=True, cwd=self.project_root)
            print("✅ 数据绘图完成")
        except subprocess.CalledProcessError as e:
            print(f"❌ 数据绘图失败: {e}")
            sys.exit(1)
    
    def run_sop_script(self, script_name, env_vars, work_dir):
        """运行SOP脚本"""
        script_path = self.project_root / 'sop_scripts' / script_name
        if not script_path.exists():
            print(f"❌ SOP脚本不存在: {script_path}")
            sys.exit(1)
        
        # 设置环境变量
        env = os.environ.copy()
        env.update(env_vars)
        
        try:
            process = subprocess.Popen(
                ['bash', str(script_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1,
                cwd=work_dir,
                env=env
            )
            
            # 实时输出
            for line in process.stdout:
                print(line.rstrip())
            
            process.wait()
            
            if process.returncode != 0:
                print(f"❌ SOP脚本运行失败: {script_name}")
                sys.exit(1)
                
        except Exception as e:
            print(f"❌ SOP脚本执行失败: {e}")
            sys.exit(1)
    
    def show_status(self):
        """显示系统状态"""
        print("📊 Kinetic-Scope系统状态:")
        print("")
        
        # 系统信息
        system_config = self.config.get('system', {})
        print("🔬 系统信息:")
        print(f"   名称: {system_config.get('name', 'Kinetic-Scope')}")
        print(f"   版本: {system_config.get('version', '1.0.0')}")
        print(f"   描述: {system_config.get('description', '分子动力学模拟系统')}")
        print("")
        
        # 路径配置
        paths = self.config.get('paths', {})
        print("📁 路径配置:")
        for key, path in paths.items():
            path_obj = Path(path)
            status = "✅ 存在" if path_obj.exists() else "❌ 不存在"
            print(f"   {key}: {path} ({status})")
        print("")
        
        # 模拟配置
        simulation = self.config.get('simulation', {})
        print("⚗️ 模拟配置:")
        print(f"   力场: {simulation.get('force_field', 'amber99sb-ildn')}")
        print(f"   水模型: {simulation.get('water_model', 'tip3p')}")
        print(f"   盒子类型: {simulation.get('box_type', 'cubic')}")
        print(f"   盒子大小: {simulation.get('box_size', 1.0)} nm")
        print(f"   盐浓度: {simulation.get('salt_concentration', 0.15)} M")
        print(f"   处理器核心数: {simulation.get('nproc', os.cpu_count())}")
        print("")
        
        # 工具状态
        print("🔧 工具状态:")
        self.check_tools(verbose=False)
    
    def check_tools(self, verbose=True):
        """检查分析工具"""
        if verbose:
            print("🔧 检查分析工具...")
        
        # GROMACS工具
        gromacs_tools = {
            'gmx': 'GROMACS主程序',
            'gmx_mpi': 'GROMACS MPI版本',
            'pdb2gmx': 'PDB转换工具',
            'editconf': '配置编辑工具',
            'solvate': '溶剂化工具',
            'genion': '离子添加工具',
            'grompp': '预处理工具',
            'mdrun': '分子动力学运行工具'
        }
        
        # Python工具
        python_packages = {
            'numpy': 'NumPy数值计算',
            'matplotlib': 'Matplotlib绘图',
            'seaborn': 'Seaborn统计绘图',
            'pandas': 'Pandas数据处理'
        }
        
        # 其他工具
        other_tools = {
            'python3': 'Python 3',
            'bash': 'Bash Shell'
        }
        
        all_available = True
        
        # 检查GROMACS工具
        if verbose:
            print("\n🧬 GROMACS工具:")
        gromacs_available = False
        for tool, description in gromacs_tools.items():
            available = shutil.which(tool) is not None
            if tool == 'gmx' and available:
                gromacs_available = True
            status = "✅ 可用" if available else "❌ 缺失"
            print(f"   {tool}: {status} - {description}")
            if tool in ['gmx', 'pdb2gmx', 'mdrun'] and not available:
                all_available = False
        
        # 检查Python包
        if verbose:
            print("\n🐍 Python包:")
        for package, description in python_packages.items():
            try:
                __import__(package)
                status = "✅ 已安装"
            except ImportError:
                status = "❌ 未安装"
                if package in ['numpy', 'matplotlib']:
                    all_available = False
            print(f"   {package}: {status} - {description}")
        
        # 检查其他工具
        if verbose:
            print("\n🔧 其他工具:")
        for tool, description in other_tools.items():
            available = shutil.which(tool) is not None
            status = "✅ 可用" if available else "❌ 缺失"
            print(f"   {tool}: {status} - {description}")
        
        if verbose:
            if gromacs_available:
                print("\n✅ GROMACS已安装")
            else:
                print("\n❌ GROMACS未安装")
                print("\n💡 安装建议:")
                print("   conda install -c conda-forge gromacs")
                print("   或访问: http://www.gromacs.org/")
        
        return all_available and gromacs_available
    
    def check_gromacs_tools(self):
        """检查GROMACS必需工具"""
        required_tools = ['gmx', 'pdb2gmx', 'mdrun']
        for tool in required_tools:
            if shutil.which(tool) is None:
                # 尝试检查gmx命令的子命令
                if tool != 'gmx':
                    try:
                        result = subprocess.run(['gmx', tool.replace('gmx_', ''), '-h'], 
                                              capture_output=True, text=True)
                        if result.returncode == 0:
                            continue
                    except:
                        pass
                return False
        return True
    
    def run_setup(self):
        """运行系统设置"""
        print("⚙️ 运行系统设置...")
        
        # 创建必要目录
        paths = self.config.get('paths', {})
        for key, path in paths.items():
            if key in ['output', 'logs']:  # 只创建输出和日志目录
                path_obj = Path(path)
                if not path_obj.exists():
                    path_obj.mkdir(parents=True, exist_ok=True)
                    print(f"📁 创建目录: {path}")
                else:
                    print(f"📁 目录已存在: {path}")
        
        # 检查脚本权限
        print("\n🔧 检查脚本权限...")
        script_dirs = ['sop_scripts', 'utilities']
        for script_dir in script_dirs:
            script_path = self.project_root / script_dir
            if script_path.exists():
                for script_file in script_path.glob('*.sh'):
                    if not os.access(script_file, os.X_OK):
                        os.chmod(script_file, 0o755)
                        print(f"   设置执行权限: {script_file}")
                    else:
                        print(f"   权限正常: {script_file}")
        
        # 检查Python依赖
        print("\n📦 检查Python依赖...")
        required_packages = ['numpy', 'matplotlib', 'seaborn', 'pandas']
        
        for package in required_packages:
            try:
                __import__(package)
                print(f"   {package}: ✅ 已安装")
            except ImportError:
                print(f"   {package}: ❌ 未安装")
        
        print("\n✅ 系统设置完成")
    
    def show_help(self):
        """显示帮助信息"""
        print(f"""
🔬 Kinetic-Scope - 分子动力学模拟系统

用法: python kinetic.py [模式] [选项]

运行模式:
  pipeline      - 运行完整分子动力学流水线
  prepare       - 仅运行系统准备
  simulate      - 仅运行分子动力学模拟
  analyze       - 仅运行轨迹分析
  batch         - 批量处理多个PDB文件
  plot          - 绘制分析结果图表
  status        - 显示系统状态
  check-tools   - 检查分析工具
  setup         - 运行系统设置

选项:
  --config <path>       - 指定配置文件路径
  --input <path>        - 指定输入文件/目录
  --output <path>       - 指定输出目录 (默认: output)
  --name <name>         - 指定系统名称 (默认: system)
  --nproc <n>           - 处理器核心数 (默认: CPU核心数)
  --skip-simulation     - 跳过模拟步骤 (仅pipeline模式)
  --skip-analysis       - 跳过分析步骤 (仅pipeline模式)
  --title <title>       - 图表标题 (仅plot模式)
  --xlabel <label>      - X轴标签 (仅plot模式)
  --ylabel <label>      - Y轴标签 (仅plot模式)
  --debug               - 启用调试模式
  --help                - 显示此帮助信息

示例:
  python kinetic.py pipeline --input protein.pdb --name my_system
  python kinetic.py prepare --input protein.pdb --output results
  python kinetic.py simulate --name my_system --output results
  python kinetic.py analyze --name my_system --output results
  python kinetic.py batch --input pdb_files/ --output batch_results
  python kinetic.py plot --input rmsd.xvg --title "RMSD Analysis"
  python kinetic.py status
  python kinetic.py check-tools

环境变量:
  KINETIC_CONFIG_PATH   - 配置文件路径
  KINETIC_DEBUG         - 调试模式
  KINETIC_NPROC         - 处理器核心数
        """)

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="Kinetic-Scope系统统一入口点",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        'mode',
        nargs='?',
        default='status',
        choices=['pipeline', 'prepare', 'simulate', 'analyze', 'batch', 'plot', 
                'status', 'check-tools', 'setup'],
        help='运行模式'
    )
    
    parser.add_argument('--config', '-c', help='配置文件路径')
    parser.add_argument('--input', '-i', help='输入文件/目录路径')
    parser.add_argument('--output', '-o', help='输出目录路径')
    parser.add_argument('--name', '-n', help='系统名称')
    parser.add_argument('--nproc', '-p', type=int, help='处理器核心数')
    parser.add_argument('--skip-simulation', action='store_true', help='跳过模拟步骤')
    parser.add_argument('--skip-analysis', action='store_true', help='跳过分析步骤')
    parser.add_argument('--title', help='图表标题')
    parser.add_argument('--xlabel', help='X轴标签')
    parser.add_argument('--ylabel', help='Y轴标签')
    parser.add_argument('--debug', '-d', action='store_true', help='启用调试模式')
    
    return parser.parse_args()

def main():
    """主函数"""
    args = parse_args()
    
    # 处理环境变量
    if not args.config:
        args.config = os.getenv('KINETIC_CONFIG_PATH')
    
    if not args.debug:
        args.debug = os.getenv('KINETIC_DEBUG', '').lower() in ('true', '1', 'yes')
    
    if not args.nproc:
        args.nproc = int(os.getenv('KINETIC_NPROC', os.cpu_count()))
    
    # 启动系统
    starter = KineticStarter()
    starter.start(args.mode, vars(args))

if __name__ == "__main__":
    main()