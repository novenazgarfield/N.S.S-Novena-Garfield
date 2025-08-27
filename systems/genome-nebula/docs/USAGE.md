# 🧬 Genome Jigsaw 使用指南

## 📋 快速开始

### 1. 环境准备

首先创建并激活 conda 环境：

```bash
# 创建环境
conda env create -f environment.yml

# 激活环境
conda activate genome-jigsaw
```

### 2. 数据准备

确保您的原始测序数据按以下格式命名：
- `sample1_R1.fastq.gz` 和 `sample1_R2.fastq.gz`
- `sample2_R1.fastq.gz` 和 `sample2_R2.fastq.gz`
- 或者 `sample1_1.fastq.gz` 和 `sample1_2.fastq.gz`

### 3. 运行分析

```bash
# 基本用法
./run_genome_jigsaw.sh /path/to/your/fastq/files

# 自定义参数
./run_genome_jigsaw.sh -o my_results -t 16 -m 32G /path/to/your/fastq/files
```

## 🔧 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `-o, --output` | 输出目录 | `results` |
| `-t, --threads` | 线程数 | 自动检测 |
| `-m, --memory` | 内存限制 | `16G` |
| `-h, --help` | 显示帮助 | - |

## 📊 输出结果

分析完成后，结果将保存在以下目录结构中：

```
results/
├── 01_qc/                      # 质量控制结果
│   ├── multiqc_raw_data.html   # 原始数据质量报告
│   └── *.html, *.zip           # FastQC 报告
├── 02_clean/                   # 数据清洗结果
│   ├── *_clean_R1.fastq.gz     # 清洗后的 R1 文件
│   ├── *_clean_R2.fastq.gz     # 清洗后的 R2 文件
│   ├── *_fastp.html            # fastp 报告
│   └── qc/                     # 清洗后数据质量控制
├── 03_assembly/                # 基因组组装结果
│   ├── *_contigs.fasta         # 组装的基因组
│   ├── assembly_stats.txt      # 组装统计信息
│   └── */                      # 各样本的详细组装结果
├── 04_annotation/              # 基因组注释结果
│   ├── annotation_stats.txt    # 注释统计信息
│   └── */                      # 各样本的注释结果
│       ├── *.gff               # 基因注释文件
│       ├── *.faa               # 蛋白质序列
│       └── *.ffn               # 基因序列
├── 05_pangenome/               # 泛基因组分析结果
│   ├── gene_presence_absence.csv # 基因存在/缺失矩阵
│   ├── pangenome_stats.txt     # 泛基因组统计
│   ├── core_gene_alignment.aln # 核心基因比对
│   └── *.Rtab                  # Roary 输出文件
├── 06_phylogenetics/           # 系统发育分析结果
│   ├── core_genes_tree.treefile # 系统发育树
│   ├── core_genes_mafft.aln    # MAFFT 比对结果
│   ├── tree_stats.txt          # 树统计信息
│   └── core_genes_tree.*       # IQ-TREE 输出文件
├── 07_screening/               # 基因筛选结果
│   ├── screening_summary.txt   # 筛选结果汇总
│   ├── resfinder/              # 耐药基因筛选
│   ├── card/                   # CARD 数据库筛选
│   ├── vfdb/                   # 毒力基因筛选
│   ├── plasmidfinder/          # 质粒基因筛选
│   └── ncbi/                   # NCBI 数据库筛选
├── GENOME_JIGSAW_REPORT.txt    # 最终分析报告
└── genome_jigsaw_*.log         # 详细日志文件
```

## 🔍 关键结果文件

### 1. 质量控制报告
- **文件**: `01_qc/multiqc_raw_data.html`
- **内容**: 原始数据质量评估，包括序列质量、GC含量、重复序列等

### 2. 基因组组装统计
- **文件**: `03_assembly/assembly_stats.txt`
- **内容**: 每个样本的组装质量指标（N50、总长度、contig数量等）

### 3. 泛基因组分析
- **文件**: `05_pangenome/gene_presence_absence.csv`
- **内容**: 所有样本的基因存在/缺失矩阵，用于比较基因组学分析

### 4. 系统发育树
- **文件**: `06_phylogenetics/core_genes_tree.treefile`
- **内容**: 基于核心基因的系统发育树，可用于进化分析

### 5. 基因筛选结果
- **文件**: `07_screening/*_summary.txt`
- **内容**: 耐药基因、毒力基因、质粒基因等的筛选结果

## 🧬 下游分析建议

### 1. 分子演化研究
```bash
# 使用 R 或 Python 分析系统发育树
# 计算进化距离
# 分析基因获得/丢失模式
```

### 2. 特异性靶点筛选
```bash
# 分析核心基因组
# 筛选保守序列
# 设计特异性引物/探针
```

### 3. 比较基因组学
```bash
# 分析基因组结构变异
# 识别水平基因转移
# 比较不同菌株特征
```

## ⚠️ 注意事项

1. **内存要求**: 建议至少 16GB 内存，大基因组或多样本分析需要更多内存
2. **存储空间**: 确保有足够的磁盘空间（通常是原始数据的 5-10 倍）
3. **运行时间**: 完整分析可能需要几小时到几天，取决于样本数量和基因组大小
4. **数据质量**: 低质量的测序数据可能影响下游分析结果

## 🐛 故障排除

### 常见问题

1. **环境问题**
   ```bash
   # 重新创建环境
   conda env remove -n genome-jigsaw
   conda env create -f environment.yml
   ```

2. **内存不足**
   ```bash
   # 减少线程数或增加内存限制
   ./run_genome_jigsaw.sh -t 4 -m 8G /path/to/data
   ```

3. **磁盘空间不足**
   ```bash
   # 清理临时文件
   rm -rf results/*/tmp/
   ```

4. **工具版本问题**
   ```bash
   # 检查工具版本
   conda list
   ```

### 日志分析
详细的错误信息请查看日志文件：
```bash
tail -f results/genome_jigsaw_*.log
```

## 📞 技术支持

如遇到问题，请：
1. 查看日志文件中的错误信息
2. 检查输入数据格式是否正确
3. 确认系统资源是否充足
4. 联系技术支持团队

---

*Genome Jigsaw v1.0.0 - 让基因组分析变得简单！* 🧬✨