# 🍬 多糖合成酶分子动力学模拟示例

这个示例展示了如何使用Kinetic Scope (动力学观测仪)对多糖合成酶进行分子动力学模拟，重点关注酶-底物相互作用和催化机理研究。

## 📋 准备工作

### 1. 准备结构文件
```bash
# 将您的多糖合成酶PDB文件命名为 enzyme.pdb
# 如果有底物结合的复合物结构，命名为 enzyme_substrate.pdb

# 示例：从PDB数据库下载糖基转移酶结构
wget https://files.rcsb.org/download/YOUR_ENZYME_PDB_ID.pdb -O enzyme.pdb
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

# 修改以下参数（针对酶系统优化）:
INPUT_PDB="enzyme.pdb"
SYSTEM_NAME="enzyme"
FORCE_FIELD="amber99sb-ildn"  # 适合蛋白质
WATER_MODEL="tip3p"
BOX_SIZE="1.5"  # 酶系统通常需要更大的盒子
SALT_CONCENTRATION="0.15"

# 运行系统搭建
./sop_prepare_system.sh
```

### 步骤2: 执行模拟
```bash
# 编辑模拟参数
vim sop_run_simulation.sh

# 修改以下参数（针对酶动力学优化）:
SYSTEM_NAME="enzyme"
SIMULATION_TIME_NS="300"  # 酶系统通常需要更长的模拟时间
TEMPERATURE="310"  # 生理温度
PRESSURE="1.0"
NPROC="16"

# 运行模拟
./sop_run_simulation.sh
```

### 步骤3: 轨迹分析
```bash
# 编辑分析参数
vim sop_analyze_trajectory.sh

# 修改以下参数:
SYSTEM_NAME="enzyme"
TRAJECTORY_FILE="md.xtc"
START_TIME="100000"  # 从100ns开始分析

# 运行分析
./sop_analyze_trajectory.sh
```

## 🧬 酶特异性分析

### 1. 活性位点分析
```bash
# 创建活性位点索引文件（假设活性位点残基为150-180）
echo "r 150-180" | gmx make_ndx -f enzyme_solv_ions.gro -o active_site.ndx

# 分析活性位点RMSD
echo "Active_site Active_site" | gmx rms -s md.tpr -f md.xtc -n active_site.ndx -o analysis/rmsd_active_site.xvg

# 分析活性位点体积变化
echo "Active_site" | gmx select -s md.tpr -f md.xtc -select 'resid 150 to 180' -os analysis/active_site_size.xvg
```

### 2. 底物结合口袋分析
```bash
# 创建结合口袋索引
echo "r 120-140 | r 200-220" | gmx make_ndx -f enzyme_solv_ions.gro -o binding_pocket.ndx

# 分析结合口袋柔性
echo "Binding_pocket" | gmx rmsf -s md.tpr -f md.xtc -n binding_pocket.ndx -o analysis/rmsf_binding_pocket.xvg -res

# 绘制结合口袋柔性图
python analysis_tools/plot_results.py --rmsf analysis/rmsf_binding_pocket.xvg --title "Enzyme Binding Pocket Flexibility"
```

### 3. 催化残基分析
```bash
# 假设催化三联体为His155, Asp180, Ser200
echo "r 155 | r 180 | r 200" | gmx make_ndx -f enzyme_solv_ions.gro -o catalytic_triad.ndx

# 分析催化残基间距离
echo "r_155 r_180" | gmx distance -s md.tpr -f md.xtc -n catalytic_triad.ndx -o analysis/dist_his_asp.xvg
echo "r_155 r_200" | gmx distance -s md.tpr -f md.xtc -n catalytic_triad.ndx -o analysis/dist_his_ser.xvg
echo "r_180 r_200" | gmx distance -s md.tpr -f md.xtc -n catalytic_triad.ndx -o analysis/dist_asp_ser.xvg

# 绘制催化残基距离变化
python analysis_tools/plot_results.py --multiple analysis/dist_*.xvg --labels "His-Asp" "His-Ser" "Asp-Ser" --title "Catalytic Triad Distances"
```

### 4. 结构域运动分析
```bash
# 分析不同结构域的运动（假设有两个主要结构域）
echo "r 1-150" | gmx make_ndx -f enzyme_solv_ions.gro -o domain1.ndx
echo "r 151-300" | gmx make_ndx -f enzyme_solv_ions.gro -o domain2.ndx

# 分析结构域间角度变化
gmx gangle -s md.tpr -f md.xtc -n1 domain1.ndx -n2 domain2.ndx -g1 plane -g2 plane -oav analysis/domain_angle.xvg

# 绘制结构域角度变化
python analysis_tools/plot_results.py --energy analysis/domain_angle.xvg --title "Inter-domain Angle Variation"
```

### 5. 溶剂通道分析
```bash
# 分析溶剂可及性变化
echo "Protein" | gmx sasa -s md.tpr -f md.xtc -o analysis/sasa_total.xvg -or analysis/sasa_residue.xvg

# 分析特定区域的溶剂暴露
echo "Active_site" | gmx sasa -s md.tpr -f md.xtc -n active_site.ndx -o analysis/sasa_active_site.xvg

# 绘制溶剂可及性变化
python analysis_tools/plot_results.py --sasa analysis/sasa_active_site.xvg --title "Active Site Solvent Accessibility"
```

## 📊 高级分析

### 1. 主成分分析 (PCA)
```bash
# 对活性位点进行PCA分析
echo "Active_site" | gmx covar -s md.tpr -f md.xtc -n active_site.ndx -o eigenval.xvg -v eigenvec.trr -ascii

# 投影到主成分空间
echo "Active_site" | gmx anaeig -s md.tpr -f md.xtc -v eigenvec.trr -n active_site.ndx -2d 2dproj.xvg -first 1 -last 2

# 生成自由能景观
gmx sham -f 2dproj.xvg -ls gibbs.xpm -notime

# 转换为图片
gmx xpm2ps -f gibbs.xpm -o gibbs.eps
```

### 2. 动态网络分析
```bash
# 计算残基间相关性
echo "Protein" | gmx covar -s md.tpr -f md.xtc -o eigenval.xvg -v eigenvec.trr -ascii -xpm -nofit

# 分析动态交叉相关
python -c "
import numpy as np
import matplotlib.pyplot as plt

# 读取相关矩阵
corr_matrix = np.loadtxt('covar.dat')

# 绘制相关性热图
plt.figure(figsize=(10, 8))
plt.imshow(corr_matrix, cmap='RdBu', vmin=-1, vmax=1)
plt.colorbar(label='Cross-correlation')
plt.title('Dynamic Cross-Correlation Map')
plt.xlabel('Residue Number')
plt.ylabel('Residue Number')
plt.savefig('plots/correlation_map.png', dpi=300, bbox_inches='tight')
plt.close()
print('✅ 动态交叉相关图已保存: plots/correlation_map.png')
"
```

### 3. 氢键网络分析
```bash
# 分析活性位点氢键网络
echo "Active_site Active_site" | gmx hbond -s md.tpr -f md.xtc -n active_site.ndx -num analysis/hbond_active_site.xvg -hbn analysis/hbond_network.ndx

# 分析特定氢键的存在时间
gmx hbond -s md.tpr -f md.xtc -n analysis/hbond_network.ndx -life analysis/hbond_lifetime.xvg

# 绘制氢键分析结果
python analysis_tools/plot_results.py --hbond analysis/hbond_active_site.xvg --title "Active Site Hydrogen Bond Network"
```

## 📈 预期结果与解释

### 结构稳定性指标
- **整体RMSD**: 0.2-0.5 nm（酶通常比小蛋白质更柔性）
- **活性位点RMSD**: 0.1-0.3 nm（应保持相对稳定）
- **回转半径**: 变化<5%（表明整体折叠稳定）

### 动态特性
- **活性位点柔性**: 中等柔性，允许底物结合和产物释放
- **结构域运动**: 可能观察到开合运动（induced fit）
- **环区柔性**: 通常表现出较高的RMSF值

### 催化相关
- **催化残基距离**: 应在催化活性范围内保持稳定
- **氢键网络**: 催化相关氢键应得到维持
- **溶剂通道**: 底物进入和产物离开的通道应保持开放

## 🔬 实验验证建议

1. **酶活性测定**: 与模拟预测的构象变化相关联
2. **突变实验**: 验证关键残基的重要性
3. **结构生物学**: 与晶体结构或冷冻电镜结构对比
4. **动力学参数**: 与实验测定的Km、kcat值比较

## 📝 特殊注意事项

1. **糖类参数**: 如涉及糖类底物，需要使用GLYCAM等专用力场
2. **金属离子**: 某些酶需要金属离子，注意参数化
3. **pH效应**: 考虑生理pH下的质子化状态
4. **温度效应**: 可进行不同温度下的模拟比较
5. **抑制剂结合**: 可模拟抑制剂结合状态进行对比

---

*此示例为多糖合成酶分子动力学模拟的专业流程，可根据具体酶系统和研究目标进行调整。*