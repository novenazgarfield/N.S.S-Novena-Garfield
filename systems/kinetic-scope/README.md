# 🔬 Kinetic Scope (动力学观测仪)

> **版本**: v1.0.0 | **创建时间**: 2025年8月20日

一个标准化、模块化的分子动力学模拟工具箱，专为GROMACS模拟工作流程设计。通过简单的参数配置，即可适应不同的研究体系（Cas14a、多糖合成酶等）。

---

## 🎯 项目概述

**Kinetic Scope (动力学观测仪)** 提供了一套完整的标准作业流程（SOP）脚本，涵盖从PDB文件到最终分析结果的整个分子动力学模拟流程。每个模块都经过精心设计，具有高度的可复用性和可配置性。

### 🌟 核心特性
- 🔧 **模块化设计**: 每个脚本对应一个标准作业流程
- ⚙️ **高度可配置**: 通过简单的变量修改适应不同体系
- 🚀 **一键运行**: 自动化执行复杂的模拟流程
- 📊 **标准化分析**: 内置常用的轨迹分析工具
- 📈 **发表级图表**: 自动生成高质量的科研图表
- 🔄 **可复用性**: 适用于各种蛋白质和酶系统

---

## 🏗️ 工具箱架构

```
Kinetic Scope (动力学观测仪)/
├── 📂 sop_scripts/           # 标准作业流程脚本
│   ├── 🔧 sop_prepare_system.sh    # 系统搭建
│   ├── 🚀 sop_run_simulation.sh    # 模拟执行
│   └── 📊 sop_analyze_trajectory.sh # 轨迹分析
├── 📂 analysis_tools/        # 分析工具
│   ├── 🐍 plot_results.py          # 数据绘图
│   └── 📈 advanced_analysis.py     # 高级分析
├── 📂 templates/             # 配置模板
│   ├── ⚙️ mdp_files/              # MDP参数文件
│   └── 📋 config_templates/        # 配置模板
├── 📂 examples/              # 使用示例
│   ├── 🧬 cas14a_example/          # Cas14a示例
│   └── 🍬 enzyme_example/          # 酶系统示例
├── 📂 utilities/             # 实用工具
└── 📂 docs/                  # 详细文档
```

---

## 🛠️ 核心模块

### 🔧 模块一：系统搭建 (sop_prepare_system.sh)
**功能**: 从PDB文件自动搭建可模拟的分子系统
- **输入**: PDB文件
- **配置参数**: 力场、水模型、盒子大小、盐浓度
- **输出**: 完整的模拟系统文件

### 🚀 模块二：模拟执行 (sop_run_simulation.sh)
**功能**: 自动执行完整的MD模拟流程
- **流程**: 能量最小化 → NVT平衡 → NPT平衡 → 成品模拟
- **配置参数**: 模拟时长、温度、压力等
- **输出**: 模拟轨迹和能量文件

### 📊 模块三：轨迹分析 (sop_analyze_trajectory.sh)
**功能**: 标准化的轨迹分析流程
- **分析内容**: RMSD、RMSF、氢键、回转半径等
- **输出**: 分析数据文件和统计结果

### 📈 模块四：数据绘图 (plot_results.py)
**功能**: 生成发表级别的科研图表
- **图表类型**: RMSD、RMSF、氢键、能量变化等
- **输出格式**: PNG、PDF、SVG等高质量格式

---

## 🚀 快速开始

### 1. 环境准备
```bash
# 确保已安装GROMACS
gmx --version

# 安装Python依赖
pip install matplotlib numpy pandas seaborn
```

### 2. 使用流程
```bash
# 1. 复制工具箱到项目目录
cp -r kinetic-scope/ my_project/

# 2. 准备PDB文件
# 将您的PDB文件放在项目目录中

# 3. 配置参数（编辑脚本开头的变量）
vim sop_scripts/sop_prepare_system.sh

# 4. 运行完整流程
./sop_scripts/sop_prepare_system.sh
./sop_scripts/sop_run_simulation.sh
./sop_scripts/sop_analyze_trajectory.sh

# 5. 生成图表
python analysis_tools/plot_results.py
```

---

## ⚙️ 配置参数

### 系统搭建参数
- `FORCE_FIELD`: 力场选择 (默认: amber99sb-ildn)
- `WATER_MODEL`: 水模型 (默认: tip3p)
- `BOX_SIZE`: 盒子边界距离 (默认: 1.0 nm)
- `SALT_CONCENTRATION`: 盐浓度 (默认: 0.15 M)

### 模拟参数
- `SIMULATION_TIME_NS`: 成品模拟时长 (默认: 100 ns)
- `TEMPERATURE`: 模拟温度 (默认: 300 K)
- `PRESSURE`: 模拟压力 (默认: 1 bar)

---

## 📊 应用场景

### 🧬 Cas14a蛋白研究
- 蛋白质稳定性分析
- 活性位点动态研究
- 底物结合模式分析

### 🍬 多糖合成酶研究
- 酶-底物相互作用
- 催化机理研究
- 构象变化分析

### 🔬 其他蛋白质系统
- 膜蛋白模拟
- 蛋白质-蛋白质相互作用
- 药物-靶点结合研究

---

## 📈 输出结果

### 模拟文件
- `system.gro`: 最终系统结构
- `md.xtc`: 模拟轨迹
- `md.edr`: 能量文件
- `md.log`: 模拟日志

### 分析结果
- `analysis/rmsd.xvg`: RMSD数据
- `analysis/rmsf.xvg`: RMSF数据
- `analysis/hbond.xvg`: 氢键数据
- `plots/`: 高质量图表

---

## 🔧 自定义扩展

工具箱设计为高度可扩展：
- 添加新的分析模块
- 自定义MDP参数文件
- 集成其他分析工具
- 适配不同的力场和水模型

---

## 📞 技术支持

- **项目主页**: [GitHub Repository](https://github.com/novenazgarfield/research-workstation)
- **使用文档**: [详细文档](docs/)
- **问题反馈**: [GitHub Issues](https://github.com/novenazgarfield/research-workstation/issues)

---

**让分子动力学模拟变得简单、标准、高效！** 🧬✨