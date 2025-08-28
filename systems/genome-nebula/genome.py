#!/usr/bin/env python3
"""
Genome-Nebula系统统一入口点
基因组测序分析系统
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

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / 'src'))

class GenomeStarter:
    """Genome-Nebula系统启动器"""
    
    def __init__(self):
        self.config = None
        self.logger = None
        self.project_root = project_root
    
    def start(self, mode, options=None):
        """主启动函数"""
        if options is None:
            options = {}
            
        try:
            print("🧬 Genome-Nebula - 基因组测序分析系统")
            print("=" * 50)
            print(f"📍 运行模式: {mode}")
            print("")
            
            # 初始化配置
            self.init_config(options.get('config'))
            
            # 设置日志
            self.setup_logging(options.get('debug', False))
            
            # 根据模式启动相应功能
            if mode == 'web':
                self.start_web_mode(options)
            elif mode == 'pipeline':
                self.start_pipeline_mode(options)
            elif mode == 'qc':
                self.run_quality_control(options)
            elif mode == 'clean':
                self.run_data_cleaning(options)
            elif mode == 'assembly':
                self.run_genome_assembly(options)
            elif mode == 'annotation':
                self.run_genome_annotation(options)
            elif mode == 'pangenome':
                self.run_pangenome_analysis(options)
            elif mode == 'phylogeny':
                self.run_phylogenetic_analysis(options)
            elif mode == 'screening':
                self.run_gene_screening(options)
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
        if config_path is None:
            config_path = self.project_root / 'config' / 'default.yaml'
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
            print(f"✅ 配置加载成功: {config_path}")
        except Exception as e:
            print(f"❌ 配置加载失败: {e}")
            sys.exit(1)
    
    def setup_logging(self, debug=False):
        """设置日志"""
        log_level = logging.DEBUG if debug else logging.INFO
        log_dir = Path(self.config.get('paths', {}).get('logs', 'logs'))
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / 'genome_nebula.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info("日志系统初始化完成")
    
    def start_web_mode(self, options):
        """启动Web界面模式"""
        print("🌐 启动Web界面模式...")
        
        try:
            # 导入并启动Web应用
            from core.config import Config
            from web.app import create_app
            
            config = Config(self.config)
            app = create_app(config)
            
            host = options.get('host', self.config.get('web', {}).get('host', '0.0.0.0'))
            port = options.get('port', self.config.get('web', {}).get('port', 8080))
            debug = options.get('debug', self.config.get('web', {}).get('debug', False))
            
            print(f"🚀 启动Web服务器: http://{host}:{port}")
            app.run(host=host, port=port, debug=debug)
            
        except ImportError as e:
            print(f"❌ 导入Web模块失败: {e}")
            print("请确保已安装Flask等Web依赖")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Web模式启动失败: {e}")
            sys.exit(1)
    
    def start_pipeline_mode(self, options):
        """启动完整流水线模式"""
        print("🔬 启动完整流水线模式...")
        
        # 检查输入目录
        input_dir = options.get('input')
        if not input_dir:
            print("❌ 请指定输入目录 --input")
            sys.exit(1)
        
        if not Path(input_dir).exists():
            print(f"❌ 输入目录不存在: {input_dir}")
            sys.exit(1)
        
        # 检查必要工具
        if not self.check_pipeline_tools():
            print("❌ 缺少必要的分析工具，请先运行 'python genome.py check-tools'")
            sys.exit(1)
        
        # 运行bash流水线脚本
        script_path = self.project_root / 'run_genome_nebula.sh'
        if not script_path.exists():
            print(f"❌ 流水线脚本不存在: {script_path}")
            sys.exit(1)
        
        print(f"🚀 运行完整流水线: {input_dir}")
        
        # 构建命令
        cmd = [
            'bash', str(script_path),
            '--input', input_dir,
            '--output', options.get('output', 'results'),
            '--threads', str(options.get('threads', os.cpu_count())),
            '--memory', options.get('memory', '16G')
        ]
        
        if options.get('skip_qc'):
            cmd.append('--skip-qc')
        if options.get('skip_assembly'):
            cmd.append('--skip-assembly')
        
        try:
            # 运行流水线
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
                                     universal_newlines=True, bufsize=1)
            
            # 实时输出
            for line in process.stdout:
                print(line.rstrip())
            
            process.wait()
            
            if process.returncode == 0:
                print("✅ 流水线运行完成")
            else:
                print(f"❌ 流水线运行失败，退出码: {process.returncode}")
                sys.exit(1)
                
        except Exception as e:
            print(f"❌ 流水线运行失败: {e}")
            sys.exit(1)
    
    def run_quality_control(self, options):
        """运行质量控制"""
        print("🔍 运行质量控制...")
        self.run_pipeline_step('qc', options)
    
    def run_data_cleaning(self, options):
        """运行数据清洗"""
        print("🧹 运行数据清洗...")
        self.run_pipeline_step('clean', options)
    
    def run_genome_assembly(self, options):
        """运行基因组组装"""
        print("🧩 运行基因组组装...")
        self.run_pipeline_step('assembly', options)
    
    def run_genome_annotation(self, options):
        """运行基因组注释"""
        print("📝 运行基因组注释...")
        self.run_pipeline_step('annotation', options)
    
    def run_pangenome_analysis(self, options):
        """运行泛基因组分析"""
        print("🌐 运行泛基因组分析...")
        self.run_pipeline_step('pangenome', options)
    
    def run_phylogenetic_analysis(self, options):
        """运行系统发育分析"""
        print("🌳 运行系统发育分析...")
        self.run_pipeline_step('phylogeny', options)
    
    def run_gene_screening(self, options):
        """运行基因筛选"""
        print("🎯 运行基因筛选...")
        self.run_pipeline_step('screening', options)
    
    def run_pipeline_step(self, step, options):
        """运行流水线单步"""
        # 这里可以实现单步运行的逻辑
        # 目前简化为调用bash脚本的相应函数
        print(f"   运行步骤: {step}")
        print("   (单步运行功能开发中，请使用完整流水线模式)")
    
    def show_status(self):
        """显示系统状态"""
        print("📊 Genome-Nebula系统状态:")
        print(f"   配置文件: {self.config}")
        print("")
        
        # 系统配置
        system_config = self.config.get('system', {})
        print("🧬 系统信息:")
        print(f"   名称: {system_config.get('name', 'Genome Jigsaw')}")
        print(f"   版本: {system_config.get('version', '1.0.0')}")
        print(f"   描述: {system_config.get('description', '基因组测序分析系统')}")
        print("")
        
        # 路径配置
        paths = self.config.get('paths', {})
        print("📁 路径配置:")
        for key, path in paths.items():
            path_obj = Path(path)
            status = "✅ 存在" if path_obj.exists() else "❌ 不存在"
            print(f"   {key}: {path} ({status})")
        print("")
        
        # 数据库配置
        databases = self.config.get('database', {})
        print("💾 数据库配置:")
        for db_type, db_config in databases.items():
            print(f"   {db_type}: {db_config.get('host', 'localhost')}:{db_config.get('port', 'N/A')}")
        print("")
        
        # Web配置
        web_config = self.config.get('web', {})
        print("🌐 Web配置:")
        print(f"   主机: {web_config.get('host', '0.0.0.0')}")
        print(f"   端口: {web_config.get('port', 8080)}")
        print(f"   调试: {web_config.get('debug', False)}")
        print("")
        
        # 工具检查
        print("🔧 工具状态:")
        self.check_tools(verbose=False)
    
    def check_tools(self, verbose=True):
        """检查分析工具"""
        if verbose:
            print("🔧 检查分析工具...")
        
        # 定义必需的工具
        required_tools = {
            'fastqc': 'FastQC - 质量控制',
            'multiqc': 'MultiQC - 报告汇总',
            'fastp': 'fastp - 数据清洗',
            'spades.py': 'SPAdes - 基因组组装',
            'prokka': 'Prokka - 基因组注释',
            'roary': 'Roary - 泛基因组分析',
            'mafft': 'MAFFT - 多序列比对',
            'iqtree': 'IQ-TREE - 系统发育分析',
            'abricate': 'ABRicate - 基因筛选'
        }
        
        # 可选工具
        optional_tools = {
            'python3': 'Python 3',
            'conda': 'Conda 包管理器',
            'samtools': 'SAMtools',
            'bcftools': 'BCFtools'
        }
        
        all_available = True
        
        # 检查必需工具
        if verbose:
            print("\n📋 必需工具:")
        for tool, description in required_tools.items():
            available = shutil.which(tool) is not None
            status = "✅ 可用" if available else "❌ 缺失"
            print(f"   {tool}: {status} - {description}")
            if not available:
                all_available = False
        
        # 检查可选工具
        if verbose:
            print("\n📋 可选工具:")
        for tool, description in optional_tools.items():
            available = shutil.which(tool) is not None
            status = "✅ 可用" if available else "⚠️ 缺失"
            print(f"   {tool}: {status} - {description}")
        
        if verbose:
            if all_available:
                print("\n✅ 所有必需工具都已安装")
            else:
                print("\n❌ 部分必需工具缺失，请安装后再运行分析")
                print("\n💡 安装建议:")
                print("   conda install -c bioconda fastqc multiqc fastp spades prokka roary mafft iqtree abricate")
        
        return all_available
    
    def check_pipeline_tools(self):
        """检查流水线必需工具"""
        required_tools = ['fastqc', 'multiqc', 'fastp', 'spades.py', 'prokka']
        for tool in required_tools:
            if shutil.which(tool) is None:
                return False
        return True
    
    def run_setup(self):
        """运行系统设置"""
        print("⚙️ 运行系统设置...")
        
        # 创建必要目录
        paths = self.config.get('paths', {})
        for key, path in paths.items():
            path_obj = Path(path)
            if not path_obj.exists():
                path_obj.mkdir(parents=True, exist_ok=True)
                print(f"📁 创建目录: {path}")
            else:
                print(f"📁 目录已存在: {path}")
        
        # 检查Python依赖
        print("\n📦 检查Python依赖...")
        required_packages = [
            'flask', 'pyyaml', 'pandas', 'numpy', 'biopython'
        ]
        
        for package in required_packages:
            try:
                __import__(package)
                print(f"   {package}: ✅ 已安装")
            except ImportError:
                print(f"   {package}: ❌ 未安装")
        
        # 运行设置脚本（如果存在）
        setup_script = self.project_root / 'scripts' / 'setup.py'
        if setup_script.exists():
            print(f"\n🔧 运行设置脚本: {setup_script}")
            try:
                subprocess.run([sys.executable, str(setup_script)], check=True)
                print("✅ 设置脚本运行完成")
            except subprocess.CalledProcessError as e:
                print(f"❌ 设置脚本运行失败: {e}")
        
        print("\n✅ 系统设置完成")
    
    def show_help(self):
        """显示帮助信息"""
        print(f"""
🧬 Genome-Nebula - 基因组测序分析系统

用法: python genome.py [模式] [选项]

运行模式:
  web           - 启动Web界面
  pipeline      - 运行完整分析流水线
  qc            - 仅运行质量控制
  clean         - 仅运行数据清洗
  assembly      - 仅运行基因组组装
  annotation    - 仅运行基因组注释
  pangenome     - 仅运行泛基因组分析
  phylogeny     - 仅运行系统发育分析
  screening     - 仅运行基因筛选
  status        - 显示系统状态
  check-tools   - 检查分析工具
  setup         - 运行系统设置

选项:
  --config <path>       - 指定配置文件路径
  --input <path>        - 指定输入目录 (pipeline模式必需)
  --output <path>       - 指定输出目录 (默认: results)
  --host <host>         - Web服务器主机 (默认: 0.0.0.0)
  --port <port>         - Web服务器端口 (默认: 8080)
  --threads <n>         - 线程数 (默认: CPU核心数)
  --memory <size>       - 内存限制 (默认: 16G)
  --skip-qc             - 跳过质量控制
  --skip-assembly       - 跳过基因组组装
  --debug               - 启用调试模式
  --help                - 显示此帮助信息

示例:
  python genome.py web
  python genome.py web --port 8081
  python genome.py pipeline --input /path/to/fastq --output results
  python genome.py qc --input /path/to/fastq
  python genome.py status
  python genome.py check-tools
  python genome.py setup

环境变量:
  GENOME_CONFIG_PATH    - 配置文件路径
  GENOME_DEBUG          - 调试模式
  GENOME_THREADS        - 线程数
        """)

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="Genome-Nebula系统统一入口点",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        'mode',
        nargs='?',
        default='web',
        choices=['web', 'pipeline', 'qc', 'clean', 'assembly', 'annotation', 
                'pangenome', 'phylogeny', 'screening', 'status', 'check-tools', 'setup'],
        help='运行模式'
    )
    
    parser.add_argument('--config', '-c', help='配置文件路径')
    parser.add_argument('--input', '-i', help='输入目录路径')
    parser.add_argument('--output', '-o', help='输出目录路径')
    parser.add_argument('--host', help='Web服务器主机')
    parser.add_argument('--port', type=int, help='Web服务器端口')
    parser.add_argument('--threads', '-t', type=int, help='线程数')
    parser.add_argument('--memory', '-m', help='内存限制')
    parser.add_argument('--skip-qc', action='store_true', help='跳过质量控制')
    parser.add_argument('--skip-assembly', action='store_true', help='跳过基因组组装')
    parser.add_argument('--debug', '-d', action='store_true', help='启用调试模式')
    
    return parser.parse_args()

def main():
    """主函数"""
    args = parse_args()
    
    # 处理环境变量
    if not args.config:
        args.config = os.getenv('GENOME_CONFIG_PATH')
    
    if not args.debug:
        args.debug = os.getenv('GENOME_DEBUG', '').lower() in ('true', '1', 'yes')
    
    if not args.threads:
        args.threads = int(os.getenv('GENOME_THREADS', os.cpu_count()))
    
    # 启动系统
    starter = GenomeStarter()
    starter.start(args.mode, vars(args))

if __name__ == "__main__":
    main()