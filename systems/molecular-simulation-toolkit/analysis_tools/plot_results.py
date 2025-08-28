#!/usr/bin/env python3
"""
Kinetic Scope (动力学观测仪) - 数据绘图工具

功能: 将GROMACS分析生成的.xvg数据文件绘制成发表级别的图表
作者: Research Workstation Team
版本: 1.0.0
日期: 2025-08-20
"""

import argparse
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.style as mplstyle
import seaborn as sns
from pathlib import Path

# 设置绘图样式
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")

# 全局配置
FIGURE_SIZE = (10, 6)
DPI = 300
FONT_SIZE = 12
TITLE_SIZE = 14
LABEL_SIZE = 12

# 配置matplotlib
plt.rcParams.update({
    'font.size': FONT_SIZE,
    'axes.titlesize': TITLE_SIZE,
    'axes.labelsize': LABEL_SIZE,
    'xtick.labelsize': FONT_SIZE,
    'ytick.labelsize': FONT_SIZE,
    'legend.fontsize': FONT_SIZE,
    'figure.titlesize': TITLE_SIZE,
    'figure.dpi': DPI,
    'savefig.dpi': DPI,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.1
})

class XVGParser:
    """GROMACS XVG文件解析器"""
    
    def __init__(self, filename):
        self.filename = filename
        self.data = None
        self.title = ""
        self.xlabel = ""
        self.ylabel = ""
        self.legends = []
        
    def parse(self):
        """解析XVG文件"""
        if not os.path.exists(self.filename):
            raise FileNotFoundError(f"文件不存在: {self.filename}")
        
        data_lines = []
        
        with open(self.filename, 'r') as f:
            for line in f:
                line = line.strip()
                
                # 跳过空行
                if not line:
                    continue
                
                # 解析元数据
                if line.startswith('@'):
                    self._parse_metadata(line)
                elif line.startswith('#'):
                    continue  # 跳过注释行
                else:
                    # 解析数据行
                    try:
                        values = [float(x) for x in line.split()]
                        data_lines.append(values)
                    except ValueError:
                        continue  # 跳过无法解析的行
        
        if not data_lines:
            raise ValueError(f"文件中没有找到有效数据: {self.filename}")
        
        self.data = np.array(data_lines)
        return self.data
    
    def _parse_metadata(self, line):
        """解析XVG元数据"""
        if 'title' in line:
            self.title = line.split('"')[1] if '"' in line else ""
        elif 'xaxis' in line and 'label' in line:
            self.xlabel = line.split('"')[1] if '"' in line else ""
        elif 'yaxis' in line and 'label' in line:
            self.ylabel = line.split('"')[1] if '"' in line else ""
        elif line.startswith('@ s') and 'legend' in line:
            legend = line.split('"')[1] if '"' in line else ""
            self.legends.append(legend)

class PlotGenerator:
    """图表生成器"""
    
    def __init__(self, output_format='png', output_dir='plots'):
        self.output_format = output_format
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
    def plot_rmsd(self, xvg_file, title=None):
        """绘制RMSD图表"""
        parser = XVGParser(xvg_file)
        data = parser.parse()
        
        fig, ax = plt.subplots(figsize=FIGURE_SIZE)
        
        # 绘制数据
        time = data[:, 0]
        rmsd = data[:, 1]
        
        ax.plot(time, rmsd, linewidth=2, alpha=0.8, label='RMSD')
        
        # 添加平均线
        mean_rmsd = np.mean(rmsd)
        ax.axhline(y=mean_rmsd, color='red', linestyle='--', alpha=0.7, 
                  label=f'平均值: {mean_rmsd:.3f} nm')
        
        # 设置标签和标题
        ax.set_xlabel(parser.xlabel or 'Time (ns)')
        ax.set_ylabel(parser.ylabel or 'RMSD (nm)')
        ax.set_title(title or parser.title or 'Root Mean Square Deviation')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # 保存图片
        output_file = self.output_dir / f'rmsd.{self.output_format}'
        plt.savefig(output_file)
        plt.close()
        
        print(f"✅ RMSD图表已保存: {output_file}")
        print(f"📊 统计信息: 平均RMSD = {mean_rmsd:.3f} nm, 标准差 = {np.std(rmsd):.3f} nm")
        
        return output_file
    
    def plot_rmsf(self, xvg_file, title=None):
        """绘制RMSF图表"""
        parser = XVGParser(xvg_file)
        data = parser.parse()
        
        fig, ax = plt.subplots(figsize=FIGURE_SIZE)
        
        # 绘制数据
        residue = data[:, 0]
        rmsf = data[:, 1]
        
        ax.plot(residue, rmsf, linewidth=2, alpha=0.8, color='orange')
        ax.fill_between(residue, rmsf, alpha=0.3, color='orange')
        
        # 标记最柔性的残基
        max_idx = np.argmax(rmsf)
        max_residue = residue[max_idx]
        max_rmsf = rmsf[max_idx]
        
        ax.plot(max_residue, max_rmsf, 'ro', markersize=8, 
               label=f'最大值: 残基{int(max_residue)} ({max_rmsf:.3f} nm)')
        
        # 设置标签和标题
        ax.set_xlabel(parser.xlabel or 'Residue Number')
        ax.set_ylabel(parser.ylabel or 'RMSF (nm)')
        ax.set_title(title or parser.title or 'Root Mean Square Fluctuation')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # 保存图片
        output_file = self.output_dir / f'rmsf.{self.output_format}'
        plt.savefig(output_file)
        plt.close()
        
        print(f"✅ RMSF图表已保存: {output_file}")
        print(f"📊 统计信息: 最大RMSF = {max_rmsf:.3f} nm (残基{int(max_residue)})")
        
        return output_file
    
    def plot_hbond(self, xvg_file, title=None):
        """绘制氢键数量图表"""
        parser = XVGParser(xvg_file)
        data = parser.parse()
        
        fig, ax = plt.subplots(figsize=FIGURE_SIZE)
        
        # 绘制数据
        time = data[:, 0]
        hbonds = data[:, 1]
        
        ax.plot(time, hbonds, linewidth=2, alpha=0.8, color='green', label='氢键数量')
        
        # 添加平均线
        mean_hbonds = np.mean(hbonds)
        ax.axhline(y=mean_hbonds, color='red', linestyle='--', alpha=0.7,
                  label=f'平均值: {mean_hbonds:.1f}')
        
        # 设置标签和标题
        ax.set_xlabel(parser.xlabel or 'Time (ns)')
        ax.set_ylabel(parser.ylabel or 'Number of Hydrogen Bonds')
        ax.set_title(title or parser.title or 'Hydrogen Bond Analysis')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # 保存图片
        output_file = self.output_dir / f'hbond.{self.output_format}'
        plt.savefig(output_file)
        plt.close()
        
        print(f"✅ 氢键图表已保存: {output_file}")
        print(f"📊 统计信息: 平均氢键数 = {mean_hbonds:.1f}, 标准差 = {np.std(hbonds):.1f}")
        
        return output_file
    
    def plot_gyrate(self, xvg_file, title=None):
        """绘制回转半径图表"""
        parser = XVGParser(xvg_file)
        data = parser.parse()
        
        fig, ax = plt.subplots(figsize=FIGURE_SIZE)
        
        # 绘制数据
        time = data[:, 0]
        gyrate = data[:, 1]
        
        ax.plot(time, gyrate, linewidth=2, alpha=0.8, color='purple', label='回转半径')
        
        # 添加平均线
        mean_gyrate = np.mean(gyrate)
        ax.axhline(y=mean_gyrate, color='red', linestyle='--', alpha=0.7,
                  label=f'平均值: {mean_gyrate:.3f} nm')
        
        # 设置标签和标题
        ax.set_xlabel(parser.xlabel or 'Time (ns)')
        ax.set_ylabel(parser.ylabel or 'Radius of Gyration (nm)')
        ax.set_title(title or parser.title or 'Radius of Gyration')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # 保存图片
        output_file = self.output_dir / f'gyrate.{self.output_format}'
        plt.savefig(output_file)
        plt.close()
        
        print(f"✅ 回转半径图表已保存: {output_file}")
        print(f"📊 统计信息: 平均回转半径 = {mean_gyrate:.3f} nm, 标准差 = {np.std(gyrate):.3f} nm")
        
        return output_file
    
    def plot_energy(self, xvg_file, title=None):
        """绘制能量图表"""
        parser = XVGParser(xvg_file)
        data = parser.parse()
        
        fig, ax = plt.subplots(figsize=FIGURE_SIZE)
        
        # 绘制数据
        time = data[:, 0]
        energy = data[:, 1]
        
        ax.plot(time, energy, linewidth=2, alpha=0.8, color='blue', label='能量')
        
        # 添加平均线
        mean_energy = np.mean(energy)
        ax.axhline(y=mean_energy, color='red', linestyle='--', alpha=0.7,
                  label=f'平均值: {mean_energy:.1f}')
        
        # 设置标签和标题
        ax.set_xlabel(parser.xlabel or 'Time (ns)')
        ax.set_ylabel(parser.ylabel or 'Energy (kJ/mol)')
        ax.set_title(title or parser.title or 'Energy Analysis')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # 保存图片
        output_file = self.output_dir / f'energy.{self.output_format}'
        plt.savefig(output_file)
        plt.close()
        
        print(f"✅ 能量图表已保存: {output_file}")
        print(f"📊 统计信息: 平均能量 = {mean_energy:.1f} kJ/mol, 标准差 = {np.std(energy):.1f}")
        
        return output_file
    
    def plot_sasa(self, xvg_file, title=None):
        """绘制SASA图表"""
        parser = XVGParser(xvg_file)
        data = parser.parse()
        
        fig, ax = plt.subplots(figsize=FIGURE_SIZE)
        
        # 绘制数据
        time = data[:, 0]
        sasa = data[:, 1]
        
        ax.plot(time, sasa, linewidth=2, alpha=0.8, color='brown', label='SASA')
        
        # 添加平均线
        mean_sasa = np.mean(sasa)
        ax.axhline(y=mean_sasa, color='red', linestyle='--', alpha=0.7,
                  label=f'平均值: {mean_sasa:.1f} nm²')
        
        # 设置标签和标题
        ax.set_xlabel(parser.xlabel or 'Time (ns)')
        ax.set_ylabel(parser.ylabel or 'SASA (nm²)')
        ax.set_title(title or parser.title or 'Solvent Accessible Surface Area')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # 保存图片
        output_file = self.output_dir / f'sasa.{self.output_format}'
        plt.savefig(output_file)
        plt.close()
        
        print(f"✅ SASA图表已保存: {output_file}")
        print(f"📊 统计信息: 平均SASA = {mean_sasa:.1f} nm², 标准差 = {np.std(sasa):.1f}")
        
        return output_file
    
    def plot_multiple(self, xvg_files, labels=None, title=None, output_name='multiple'):
        """绘制多个数据系列的对比图"""
        fig, ax = plt.subplots(figsize=FIGURE_SIZE)
        
        colors = plt.cm.tab10(np.linspace(0, 1, len(xvg_files)))
        
        for i, xvg_file in enumerate(xvg_files):
            parser = XVGParser(xvg_file)
            data = parser.parse()
            
            time = data[:, 0]
            values = data[:, 1]
            
            label = labels[i] if labels and i < len(labels) else f'Series {i+1}'
            ax.plot(time, values, linewidth=2, alpha=0.8, color=colors[i], label=label)
        
        # 设置标签和标题
        ax.set_xlabel('Time (ns)')
        ax.set_ylabel('Value')
        ax.set_title(title or 'Multiple Series Comparison')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # 保存图片
        output_file = self.output_dir / f'{output_name}.{self.output_format}'
        plt.savefig(output_file)
        plt.close()
        
        print(f"✅ 多系列对比图已保存: {output_file}")
        
        return output_file

def create_summary_plot(analysis_dir, output_dir='plots'):
    """创建分析结果汇总图"""
    analysis_path = Path(analysis_dir)
    plot_gen = PlotGenerator(output_dir=output_dir)
    
    # 查找分析文件
    files_to_plot = {
        'rmsd_backbone.xvg': 'RMSD (Backbone)',
        'rmsd_protein.xvg': 'RMSD (Protein)',
        'rmsf_backbone.xvg': 'RMSF (Backbone)',
        'hbond_intra.xvg': 'Hydrogen Bonds (Intra)',
        'hbond_water.xvg': 'Hydrogen Bonds (Water)',
        'gyrate.xvg': 'Radius of Gyration',
        'sasa.xvg': 'SASA'
    }
    
    found_files = []
    for filename, description in files_to_plot.items():
        filepath = analysis_path / filename
        if filepath.exists():
            found_files.append((str(filepath), description))
    
    if not found_files:
        print("⚠️ 未找到分析文件")
        return
    
    # 创建汇总图
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    axes = axes.flatten()
    
    for i, (filepath, description) in enumerate(found_files[:4]):  # 最多显示4个图
        parser = XVGParser(filepath)
        data = parser.parse()
        
        time = data[:, 0]
        values = data[:, 1]
        
        axes[i].plot(time, values, linewidth=2, alpha=0.8)
        axes[i].set_title(description)
        axes[i].set_xlabel('Time (ns)')
        axes[i].grid(True, alpha=0.3)
    
    # 隐藏多余的子图
    for i in range(len(found_files), 4):
        axes[i].set_visible(False)
    
    plt.tight_layout()
    
    # 保存汇总图
    output_file = Path(output_dir) / 'summary.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✅ 汇总图已保存: {output_file}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='🔬 Kinetic Scope (动力学观测仪) - 数据绘图工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  %(prog)s --rmsd analysis/rmsd_backbone.xvg
  %(prog)s --rmsf analysis/rmsf_backbone.xvg
  %(prog)s --hbond analysis/hbond_intra.xvg
  %(prog)s --multiple file1.xvg file2.xvg --labels "Series 1" "Series 2"
  %(prog)s --summary analysis/
        """
    )
    
    # 单个文件绘图选项
    parser.add_argument('--rmsd', help='绘制RMSD图表')
    parser.add_argument('--rmsf', help='绘制RMSF图表')
    parser.add_argument('--hbond', help='绘制氢键图表')
    parser.add_argument('--gyrate', help='绘制回转半径图表')
    parser.add_argument('--energy', help='绘制能量图表')
    parser.add_argument('--sasa', help='绘制SASA图表')
    
    # 多文件绘图选项
    parser.add_argument('--multiple', nargs='+', help='绘制多个文件的对比图')
    parser.add_argument('--labels', nargs='+', help='多文件绘图的标签')
    
    # 汇总图选项
    parser.add_argument('--summary', help='创建分析结果汇总图 (指定分析目录)')
    
    # 输出选项
    parser.add_argument('-o', '--output', default='plots', help='输出目录 (默认: plots)')
    parser.add_argument('-f', '--format', default='png', choices=['png', 'pdf', 'svg'], 
                       help='输出格式 (默认: png)')
    parser.add_argument('-t', '--title', help='自定义图表标题')
    
    args = parser.parse_args()
    
    # 检查是否提供了任何绘图选项
    if not any([args.rmsd, args.rmsf, args.hbond, args.gyrate, args.energy, 
               args.sasa, args.multiple, args.summary]):
        parser.print_help()
        return
    
    # 创建绘图器
    plot_gen = PlotGenerator(output_format=args.format, output_dir=args.output)
    
    print("🔬 Kinetic Scope (动力学观测仪) - 数据绘图工具")
    print("=" * 60)
    
    try:
        # 单个文件绘图
        if args.rmsd:
            plot_gen.plot_rmsd(args.rmsd, args.title)
        
        if args.rmsf:
            plot_gen.plot_rmsf(args.rmsf, args.title)
        
        if args.hbond:
            plot_gen.plot_hbond(args.hbond, args.title)
        
        if args.gyrate:
            plot_gen.plot_gyrate(args.gyrate, args.title)
        
        if args.energy:
            plot_gen.plot_energy(args.energy, args.title)
        
        if args.sasa:
            plot_gen.plot_sasa(args.sasa, args.title)
        
        # 多文件对比绘图
        if args.multiple:
            plot_gen.plot_multiple(args.multiple, args.labels, args.title)
        
        # 汇总图
        if args.summary:
            create_summary_plot(args.summary, args.output)
        
        print("\n🎉 绘图完成！")
        print(f"📁 输出目录: {args.output}")
        
    except Exception as e:
        print(f"❌ 绘图过程中发生错误: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()