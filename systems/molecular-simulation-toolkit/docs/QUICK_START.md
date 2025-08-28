# 🚀 Kinetic Scope (动力学观测仪) 快速开始指南

## 📋 系统要求

### 必需软件
- **GROMACS** (版本 2020 或更高)
- **Python** (版本 3.7 或更高)
- **bc** (用于数学计算)

### Python依赖包
```bash
pip install matplotlib numpy pandas seaborn biopython
```

### 推荐硬件配置
- **CPU**: 8核或更多
- **内存**: 16GB或更多
- **存储**: 100GB可用空间
- **GPU**: NVIDIA GPU (可选，用于加速)

## 🔧 安装与配置

### 1. 检查GROMACS安装
```bash
gmx --version
```

### 2. 克隆工具箱
```bash
# 复制工具箱到您的项目目录
cp -r /path/to/kinetic-scope /path/to/your/project/
cd /path/to/your/project/kinetic-scope
```

### 3. 设置权限
```bash
chmod +x sop_scripts/*.sh
chmod +x analysis_tools/*.py
```

## 🧬 基本使用流程

### 步骤1: 准备PDB文件
```bash
# 将您的蛋白质PDB文件放在工作目录中
# 文件名示例: protein.pdb
```

### 步骤2: 系统搭建
```bash
# 复制脚本到工作目录
cp sop_scripts/sop_prepare_system.sh .

# 编辑配置参数
vim sop_prepare_system.sh
# 修改以下关键参数:
# INPUT_PDB="your_protein.pdb"
# SYSTEM_NAME="your_system"
# FORCE_FIELD="amber99sb-ildn"
# WATER_MODEL="tip3p"
# BOX_SIZE="1.0"
# SALT_CONCENTRATION="0.15"

# 运行系统搭建
./sop_prepare_system.sh
```

### 步骤3: 执行模拟
```bash
# 复制模拟脚本
cp sop_scripts/sop_run_simulation.sh .

# 编辑模拟参数
vim sop_run_simulation.sh
# 修改以下关键参数:
# SYSTEM_NAME="your_system"
# SIMULATION_TIME_NS="100"
# TEMPERATURE="300"
# NPROC="8"

# 运行模拟
./sop_run_simulation.sh
```

### 步骤4: 轨迹分析
```bash
# 复制分析脚本
cp sop_scripts/sop_analyze_trajectory.sh .
cp -r analysis_tools .

# 编辑分析参数
vim sop_analyze_trajectory.sh
# 修改以下参数:
# SYSTEM_NAME="your_system"
# TRAJECTORY_FILE="md.xtc"
# START_TIME="10000"  # 跳过前10ns

# 运行分析
./sop_analyze_trajectory.sh
```

### 步骤5: 生成图表
```bash
# 生成各种分析图表
python analysis_tools/plot_results.py --rmsd analysis/rmsd_backbone.xvg
python analysis_tools/plot_results.py --rmsf analysis/rmsf_backbone.xvg
python analysis_tools/plot_results.py --hbond analysis/hbond_intra.xvg

# 生成汇总图
python analysis_tools/plot_results.py --summary analysis/
```

## 📊 输出文件说明

### 系统搭建输出
```
your_system_solv_ions.gro    # 最终系统结构
your_system.top              # 拓扑文件
your_system_system_stats.txt # 系统统计报告
```

### 模拟输出
```
md.xtc                       # 轨迹文件
md.edr                       # 能量文件
md.gro                       # 最终结构
md.log                       # 模拟日志
your_system_simulation_report.txt # 模拟报告
```

### 分析输出
```
analysis/
├── rmsd_backbone.xvg        # 主链RMSD
├── rmsd_protein.xvg         # 蛋白质RMSD
├── rmsf_backbone.xvg        # 主链RMSF
├── hbond_intra.xvg          # 蛋白质内部氢键
├── hbond_water.xvg          # 蛋白质-水氢键
├── gyrate.xvg               # 回转半径
├── sasa.xvg                 # 溶剂可及表面积
└── your_system_analysis_report.txt # 分析报告
```

### 图表输出
```
plots/
├── rmsd.png                 # RMSD图表
├── rmsf.png                 # RMSF图表
├── hbond.png                # 氢键图表
├── gyrate.png               # 回转半径图表
└── summary.png              # 汇总图表
```

## ⚙️ 常用参数配置

### 力场选择
```bash
# 蛋白质系统推荐
FORCE_FIELD="amber99sb-ildn"  # AMBER力场，适合蛋白质
FORCE_FIELD="charmm27"        # CHARMM力场，另一选择

# 核酸系统
FORCE_FIELD="amber99bsc1"     # AMBER力场，适合DNA/RNA
```

### 水模型选择
```bash
WATER_MODEL="tip3p"           # 标准三点水模型
WATER_MODEL="tip4p"           # 四点水模型，更准确
WATER_MODEL="spc"             # SPC水模型
```

### 盒子大小建议
```bash
BOX_SIZE="1.0"                # 小蛋白质 (<100残基)
BOX_SIZE="1.2"                # 中等蛋白质 (100-300残基)
BOX_SIZE="1.5"                # 大蛋白质 (>300残基)
BOX_SIZE="2.0"                # 蛋白质复合物
```

### 模拟时长建议
```bash
SIMULATION_TIME_NS="50"       # 快速测试
SIMULATION_TIME_NS="100"      # 标准分析
SIMULATION_TIME_NS="200"      # 深入研究
SIMULATION_TIME_NS="500"      # 长时间动力学
```

## 🔍 故障排除

### 常见问题1: GROMACS命令未找到
```bash
# 检查GROMACS安装
which gmx
# 如果未找到，需要安装GROMACS或添加到PATH
export PATH=/path/to/gromacs/bin:$PATH
```

### 常见问题2: 内存不足
```bash
# 减少线程数
NPROC="4"
# 或增加系统内存
```

### 常见问题3: 磁盘空间不足
```bash
# 检查磁盘空间
df -h .
# 清理不必要的文件
rm -f *.trr *.cpt.* *.log.*
```

### 常见问题4: 模拟崩溃
```bash
# 检查日志文件
tail -50 md.log
# 常见原因：
# - 初始结构问题：重新进行能量最小化
# - 参数设置问题：检查MDP文件
# - 系统不稳定：增加平衡时间
```

## 📚 进阶使用

### 自定义分析
```bash
# 创建自定义索引文件
gmx make_ndx -f your_system_solv_ions.gro -o custom.ndx

# 分析特定区域
echo "your_selection" | gmx rms -s md.tpr -f md.xtc -n custom.ndx -o custom_rmsd.xvg
```

### 并行计算
```bash
# 使用MPI并行
mpirun -np 16 gmx_mpi mdrun -deffnm md

# 使用GPU加速
gmx mdrun -deffnm md -gpu_id 0
```

### 批量处理
```bash
# 创建批量处理脚本
for pdb in *.pdb; do
    name=$(basename $pdb .pdb)
    # 修改脚本参数
    sed "s/INPUT_PDB=.*/INPUT_PDB=\"$pdb\"/" sop_prepare_system.sh > prepare_${name}.sh
    sed "s/SYSTEM_NAME=.*/SYSTEM_NAME=\"$name\"/" prepare_${name}.sh > temp && mv temp prepare_${name}.sh
    # 运行脚本
    ./prepare_${name}.sh
done
```

## 📞 获取帮助

### 查看脚本帮助
```bash
./sop_prepare_system.sh --help
./sop_run_simulation.sh --help
./sop_analyze_trajectory.sh --help
python analysis_tools/plot_results.py --help
```

### 在线资源
- [GROMACS官方文档](http://manual.gromacs.org/)
- [GROMACS教程](http://www.mdtutorials.com/gmx/)
- [分子动力学基础](https://en.wikipedia.org/wiki/Molecular_dynamics)

---

**开始您的分子动力学模拟之旅！** 🧬✨