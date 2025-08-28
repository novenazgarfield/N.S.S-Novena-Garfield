# 🧬 Cas14a蛋白质分子动力学模拟示例

这个示例展示了如何使用Kinetic Scope (动力学观测仪)对Cas14a蛋白质进行完整的分子动力学模拟分析。

## 📋 准备工作

### 1. 准备PDB文件
```bash
# 将您的Cas14a PDB文件命名为 cas14a.pdb 并放在此目录中
# 或者从PDB数据库下载
wget https://files.rcsb.org/download/YOUR_PDB_ID.pdb -O cas14a.pdb
```

### 2. 复制工具箱脚本
```bash
# 复制SOP脚本到当前目录
cp ../../sop_scripts/*.sh .
cp -r ../../analysis_tools .
cp -r ../../templates .
```

## 🚀 运行模拟

### 步骤1: 系统搭建
```bash
# 编辑脚本配置参数
vim sop_prepare_system.sh

# 修改以下参数:
INPUT_PDB="cas14a.pdb"
SYSTEM_NAME="cas14a"
FORCE_FIELD="amber99sb-ildn"
WATER_MODEL="tip3p"
BOX_SIZE="1.2"
SALT_CONCENTRATION="0.15"

# 运行系统搭建
./sop_prepare_system.sh
```

### 步骤2: 执行模拟
```bash
# 编辑模拟参数
vim sop_run_simulation.sh

# 修改以下参数:
SYSTEM_NAME="cas14a"
SIMULATION_TIME_NS="200"  # 200ns模拟
TEMPERATURE="300"
NPROC="16"  # 根据您的CPU核心数调整

# 运行模拟
./sop_run_simulation.sh
```

### 步骤3: 轨迹分析
```bash
# 编辑分析参数
vim sop_analyze_trajectory.sh

# 修改以下参数:
SYSTEM_NAME="cas14a"
TRAJECTORY_FILE="md.xtc"
START_TIME="50000"  # 从50ns开始分析，跳过平衡阶段

# 运行分析
./sop_analyze_trajectory.sh
```

### 步骤4: 生成图表
```bash
# 生成各种分析图表
python analysis_tools/plot_results.py --rmsd analysis/rmsd_backbone.xvg
python analysis_tools/plot_results.py --rmsf analysis/rmsf_backbone.xvg
python analysis_tools/plot_results.py --hbond analysis/hbond_intra.xvg
python analysis_tools/plot_results.py --gyrate analysis/gyrate.xvg

# 生成汇总图
python analysis_tools/plot_results.py --summary analysis/
```

## 📊 Cas14a特异性分析

### 活性位点分析
```bash
# 创建活性位点索引文件
echo "r 100-120" | gmx make_ndx -f cas14a_solv_ions.gro -o active_site.ndx

# 分析活性位点RMSD
echo "Active_site Active_site" | gmx rms -s md.tpr -f md.xtc -n active_site.ndx -o analysis/rmsd_active_site.xvg

# 绘制活性位点RMSD
python analysis_tools/plot_results.py --rmsd analysis/rmsd_active_site.xvg --title "Cas14a Active Site RMSD"
```

### DNA结合域分析
```bash
# 假设DNA结合域为残基50-80
echo "r 50-80" | gmx make_ndx -f cas14a_solv_ions.gro -o dna_binding.ndx

# 分析DNA结合域柔性
echo "DNA_binding" | gmx rmsf -s md.tpr -f md.xtc -n dna_binding.ndx -o analysis/rmsf_dna_binding.xvg -res

# 绘制DNA结合域RMSF
python analysis_tools/plot_results.py --rmsf analysis/rmsf_dna_binding.xvg --title "Cas14a DNA Binding Domain Flexibility"
```

### 蛋白质-蛋白质相互作用分析
```bash
# 如果有蛋白质复合物，分析界面接触
gmx mindist -s md.tpr -f md.xtc -n protein_complex.ndx -od analysis/mindist.xvg -pi

# 绘制最小距离变化
python analysis_tools/plot_results.py --energy analysis/mindist.xvg --title "Protein-Protein Interface Distance"
```

## 📈 预期结果

### 结构稳定性
- **RMSD**: Cas14a主链RMSD应在0.2-0.4 nm范围内稳定
- **回转半径**: 应保持相对稳定，表明蛋白质结构紧密

### 动态特性
- **RMSF**: 环区和末端区域通常表现出较高的柔性
- **活性位点**: 应保持相对稳定的构象

### 相互作用
- **氢键**: 蛋白质内部氢键数量应保持稳定
- **盐桥**: 重要的盐桥相互作用应得到维持

## 🔬 进一步分析建议

1. **主成分分析 (PCA)**
   ```bash
   gmx covar -s md.tpr -f md.xtc -o eigenval.xvg -v eigenvec.trr
   gmx anaeig -s md.tpr -f md.xtc -v eigenvec.trr -2d 2dproj.xvg -first 1 -last 2
   ```

2. **自由能景观分析**
   ```bash
   gmx sham -f 2dproj.xvg -ls gibbs.xpm -notime
   ```

3. **动态交叉相关分析**
   ```bash
   gmx covar -s md.tpr -f md.xtc -ascii -xpm -nofit
   ```

## 📝 注意事项

1. **计算资源**: Cas14a模拟建议使用至少16核CPU，200ns模拟大约需要1-3天
2. **存储空间**: 确保有足够的磁盘空间（约50-100GB）
3. **参数优化**: 根据具体研究目标调整模拟参数
4. **结果验证**: 与实验数据或已发表的模拟结果进行对比验证

---

*此示例为Cas14a蛋白质分子动力学模拟的标准流程，可根据具体研究需求进行调整。*