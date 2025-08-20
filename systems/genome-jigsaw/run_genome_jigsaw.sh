#!/bin/bash

#==============================================================================
# Genome Jigsaw - 自动化细菌全基因组测序分析流水线
# 
# 作者: Research Workstation Team
# 版本: 1.0.0
# 日期: 2025-08-20
#
# 描述: 从质量控制到比较基因组学的完整分析流水线
#       处理细菌全基因组测序数据，输出分子演化和靶点筛选数据
#==============================================================================

set -euo pipefail  # 严格模式：遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 全局变量
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE=""
INPUT_DIR=""
OUTPUT_DIR="results"
THREADS=$(nproc)
MEMORY="16G"

#==============================================================================
# 工具函数
#==============================================================================

# 打印带颜色的消息
print_message() {
    local color=$1
    local message=$2
    echo -e "${color}[$(date '+%Y-%m-%d %H:%M:%S')] ${message}${NC}" | tee -a "$LOG_FILE"
}

# 信息消息
log_info() {
    print_message "$BLUE" "ℹ️  INFO: $1"
}

# 成功消息
log_success() {
    print_message "$GREEN" "✅ SUCCESS: $1"
}

# 警告消息
log_warning() {
    print_message "$YELLOW" "⚠️  WARNING: $1"
}

# 错误消息
log_error() {
    print_message "$RED" "❌ ERROR: $1"
}

# 步骤开始
log_step() {
    print_message "$PURPLE" "🔬 STEP: $1"
}

# 检查命令是否存在
check_command() {
    if ! command -v "$1" &> /dev/null; then
        log_error "命令 '$1' 未找到。请确保已安装并激活 conda 环境。"
        exit 1
    fi
}

# 检查文件是否存在
check_file() {
    if [[ ! -f "$1" ]]; then
        log_error "文件不存在: $1"
        exit 1
    fi
}

# 检查目录是否存在
check_directory() {
    if [[ ! -d "$1" ]]; then
        log_error "目录不存在: $1"
        exit 1
    fi
}

# 创建目录
create_directory() {
    if [[ ! -d "$1" ]]; then
        mkdir -p "$1"
        log_info "创建目录: $1"
    fi
}

# 获取样本名称（从文件名中提取）
get_sample_name() {
    local file_path=$1
    basename "$file_path" | sed 's/_R[12]\.fastq\.gz$//' | sed 's/_[12]\.fastq\.gz$//'
}

# 计算运行时间
calculate_runtime() {
    local start_time=$1
    local end_time=$(date +%s)
    local runtime=$((end_time - start_time))
    local hours=$((runtime / 3600))
    local minutes=$(((runtime % 3600) / 60))
    local seconds=$((runtime % 60))
    printf "%02d:%02d:%02d" $hours $minutes $seconds
}

#==============================================================================
# 主要分析函数
#==============================================================================

# 1. 质量控制 (Quality Control)
run_quality_control() {
    log_step "开始质量控制分析"
    local step_start=$(date +%s)
    
    local qc_dir="$OUTPUT_DIR/01_qc"
    create_directory "$qc_dir"
    
    # 查找所有 FASTQ 文件
    local fastq_files=($(find "$INPUT_DIR" -name "*.fastq.gz" -o -name "*.fq.gz" | sort))
    
    if [[ ${#fastq_files[@]} -eq 0 ]]; then
        log_error "在 $INPUT_DIR 中未找到 FASTQ 文件"
        exit 1
    fi
    
    log_info "找到 ${#fastq_files[@]} 个 FASTQ 文件"
    
    # 运行 FastQC
    log_info "运行 FastQC..."
    fastqc "${fastq_files[@]}" \
        --outdir "$qc_dir" \
        --threads "$THREADS" \
        --quiet
    
    # 运行 MultiQC 汇总报告
    log_info "生成 MultiQC 汇总报告..."
    multiqc "$qc_dir" \
        --outdir "$qc_dir" \
        --filename "multiqc_raw_data" \
        --title "Raw Data Quality Control" \
        --quiet
    
    local runtime=$(calculate_runtime $step_start)
    log_success "质量控制完成 (耗时: $runtime)"
}

# 2. 数据清洗 (Data Cleaning)
run_data_cleaning() {
    log_step "开始数据清洗"
    local step_start=$(date +%s)
    
    local clean_dir="$OUTPUT_DIR/02_clean"
    local qc_clean_dir="$OUTPUT_DIR/02_clean/qc"
    create_directory "$clean_dir"
    create_directory "$qc_clean_dir"
    
    # 查找成对的 FASTQ 文件
    local r1_files=($(find "$INPUT_DIR" -name "*_R1.fastq.gz" -o -name "*_1.fastq.gz" | sort))
    
    if [[ ${#r1_files[@]} -eq 0 ]]; then
        log_error "未找到 R1 文件"
        exit 1
    fi
    
    log_info "找到 ${#r1_files[@]} 个样本进行清洗"
    
    # 处理每个样本
    for r1_file in "${r1_files[@]}"; do
        local sample_name=$(get_sample_name "$r1_file")
        local r2_file=$(echo "$r1_file" | sed 's/_R1\.fastq\.gz$/_R2.fastq.gz/' | sed 's/_1\.fastq\.gz$/_2.fastq.gz/')
        
        if [[ ! -f "$r2_file" ]]; then
            log_warning "未找到对应的 R2 文件: $r2_file，跳过样本 $sample_name"
            continue
        fi
        
        log_info "清洗样本: $sample_name"
        
        # 使用 fastp 进行清洗
        fastp \
            --in1 "$r1_file" \
            --in2 "$r2_file" \
            --out1 "$clean_dir/${sample_name}_clean_R1.fastq.gz" \
            --out2 "$clean_dir/${sample_name}_clean_R2.fastq.gz" \
            --json "$clean_dir/${sample_name}_fastp.json" \
            --html "$clean_dir/${sample_name}_fastp.html" \
            --thread "$THREADS" \
            --detect_adapter_for_pe \
            --correction \
            --cut_front \
            --cut_tail \
            --cut_window_size 4 \
            --cut_mean_quality 20 \
            --qualified_quality_phred 20 \
            --unqualified_percent_limit 40 \
            --length_required 50 \
            --low_complexity_filter \
            --complexity_threshold 30 \
            --overrepresentation_analysis \
            --quiet
    done
    
    # 对清洗后的数据运行 FastQC
    log_info "对清洗后的数据运行质量控制..."
    local clean_fastq_files=($(find "$clean_dir" -name "*_clean_*.fastq.gz" | sort))
    
    if [[ ${#clean_fastq_files[@]} -gt 0 ]]; then
        fastqc "${clean_fastq_files[@]}" \
            --outdir "$qc_clean_dir" \
            --threads "$THREADS" \
            --quiet
        
        # 生成清洗后数据的 MultiQC 报告
        multiqc "$qc_clean_dir" "$clean_dir" \
            --outdir "$qc_clean_dir" \
            --filename "multiqc_clean_data" \
            --title "Clean Data Quality Control" \
            --quiet
    fi
    
    local runtime=$(calculate_runtime $step_start)
    log_success "数据清洗完成 (耗时: $runtime)"
}

# 3. 基因组组装 (Genome Assembly)
run_genome_assembly() {
    log_step "开始基因组组装"
    local step_start=$(date +%s)
    
    local assembly_dir="$OUTPUT_DIR/03_assembly"
    create_directory "$assembly_dir"
    
    local clean_dir="$OUTPUT_DIR/02_clean"
    local r1_files=($(find "$clean_dir" -name "*_clean_R1.fastq.gz" | sort))
    
    if [[ ${#r1_files[@]} -eq 0 ]]; then
        log_error "未找到清洗后的 FASTQ 文件"
        exit 1
    fi
    
    log_info "找到 ${#r1_files[@]} 个样本进行组装"
    
    # 处理每个样本
    for r1_file in "${r1_files[@]}"; do
        local sample_name=$(basename "$r1_file" | sed 's/_clean_R1\.fastq\.gz$//')
        local r2_file=$(echo "$r1_file" | sed 's/_R1\.fastq\.gz$/_R2.fastq.gz/')
        
        if [[ ! -f "$r2_file" ]]; then
            log_warning "未找到对应的 R2 文件: $r2_file，跳过样本 $sample_name"
            continue
        fi
        
        log_info "组装样本: $sample_name"
        
        local sample_assembly_dir="$assembly_dir/$sample_name"
        
        # 使用 SPAdes 进行组装
        spades.py \
            --pe1-1 "$r1_file" \
            --pe1-2 "$r2_file" \
            --out "$sample_assembly_dir" \
            --threads "$THREADS" \
            --memory $(echo "$MEMORY" | sed 's/G//') \
            --careful \
            --cov-cutoff auto
        
        # 复制最终的组装结果到统一目录
        if [[ -f "$sample_assembly_dir/contigs.fasta" ]]; then
            cp "$sample_assembly_dir/contigs.fasta" "$assembly_dir/${sample_name}_contigs.fasta"
            log_success "样本 $sample_name 组装完成"
        else
            log_error "样本 $sample_name 组装失败"
        fi
    done
    
    # 生成组装统计信息
    log_info "生成组装统计信息..."
    echo -e "Sample\tContigs\tTotal_Length\tN50\tLargest_Contig" > "$assembly_dir/assembly_stats.txt"
    
    for contig_file in "$assembly_dir"/*_contigs.fasta; do
        if [[ -f "$contig_file" ]]; then
            local sample_name=$(basename "$contig_file" | sed 's/_contigs\.fasta$//')
            local stats=$(python3 -c "
import sys
from Bio import SeqIO
import numpy as np

contigs = list(SeqIO.parse('$contig_file', 'fasta'))
lengths = [len(seq) for seq in contigs]
lengths.sort(reverse=True)

total_length = sum(lengths)
num_contigs = len(lengths)

# Calculate N50
cumsum = 0
n50 = 0
for length in lengths:
    cumsum += length
    if cumsum >= total_length * 0.5:
        n50 = length
        break

largest = lengths[0] if lengths else 0

print(f'$sample_name\t{num_contigs}\t{total_length}\t{n50}\t{largest}')
")
            echo "$stats" >> "$assembly_dir/assembly_stats.txt"
        fi
    done
    
    local runtime=$(calculate_runtime $step_start)
    log_success "基因组组装完成 (耗时: $runtime)"
}

# 4. 基因组注释 (Genome Annotation)
run_genome_annotation() {
    log_step "开始基因组注释"
    local step_start=$(date +%s)
    
    local annotation_dir="$OUTPUT_DIR/04_annotation"
    create_directory "$annotation_dir"
    
    local assembly_dir="$OUTPUT_DIR/03_assembly"
    local contig_files=($(find "$assembly_dir" -name "*_contigs.fasta" | sort))
    
    if [[ ${#contig_files[@]} -eq 0 ]]; then
        log_error "未找到组装的基因组文件"
        exit 1
    fi
    
    log_info "找到 ${#contig_files[@]} 个基因组进行注释"
    
    # 处理每个基因组
    for contig_file in "${contig_files[@]}"; do
        local sample_name=$(basename "$contig_file" | sed 's/_contigs\.fasta$//')
        
        log_info "注释样本: $sample_name"
        
        local sample_annotation_dir="$annotation_dir/$sample_name"
        
        # 使用 Prokka 进行注释
        prokka \
            --outdir "$sample_annotation_dir" \
            --prefix "$sample_name" \
            --genus "Bacteria" \
            --species "sp." \
            --strain "$sample_name" \
            --locustag "$sample_name" \
            --cpus "$THREADS" \
            --force \
            --quiet \
            "$contig_file"
        
        if [[ -f "$sample_annotation_dir/${sample_name}.gff" ]]; then
            log_success "样本 $sample_name 注释完成"
        else
            log_error "样本 $sample_name 注释失败"
        fi
    done
    
    # 生成注释统计信息
    log_info "生成注释统计信息..."
    echo -e "Sample\tCDS\ttRNA\trRNA\ttmRNA\tmisc_RNA" > "$annotation_dir/annotation_stats.txt"
    
    for sample_dir in "$annotation_dir"/*/; do
        if [[ -d "$sample_dir" ]]; then
            local sample_name=$(basename "$sample_dir")
            local gff_file="$sample_dir/${sample_name}.gff"
            
            if [[ -f "$gff_file" ]]; then
                local cds_count=$(grep -c "CDS" "$gff_file" || echo "0")
                local trna_count=$(grep -c "tRNA" "$gff_file" || echo "0")
                local rrna_count=$(grep -c "rRNA" "$gff_file" || echo "0")
                local tmrna_count=$(grep -c "tmRNA" "$gff_file" || echo "0")
                local misc_rna_count=$(grep -c "misc_RNA" "$gff_file" || echo "0")
                
                echo -e "$sample_name\t$cds_count\t$trna_count\t$rrna_count\t$tmrna_count\t$misc_rna_count" >> "$annotation_dir/annotation_stats.txt"
            fi
        fi
    done
    
    local runtime=$(calculate_runtime $step_start)
    log_success "基因组注释完成 (耗时: $runtime)"
}

# 5. 泛基因组分析 (Pan-genome Analysis)
run_pangenome_analysis() {
    log_step "开始泛基因组分析"
    local step_start=$(date +%s)
    
    local pangenome_dir="$OUTPUT_DIR/05_pangenome"
    create_directory "$pangenome_dir"
    
    local annotation_dir="$OUTPUT_DIR/04_annotation"
    local gff_files=($(find "$annotation_dir" -name "*.gff" | sort))
    
    if [[ ${#gff_files[@]} -eq 0 ]]; then
        log_error "未找到注释文件 (.gff)"
        exit 1
    fi
    
    if [[ ${#gff_files[@]} -lt 2 ]]; then
        log_warning "泛基因组分析需要至少2个基因组，当前只有 ${#gff_files[@]} 个"
        return
    fi
    
    log_info "找到 ${#gff_files[@]} 个基因组进行泛基因组分析"
    
    # 复制 GFF 文件到泛基因组分析目录
    local gff_input_dir="$pangenome_dir/gff_files"
    create_directory "$gff_input_dir"
    
    for gff_file in "${gff_files[@]}"; do
        cp "$gff_file" "$gff_input_dir/"
    done
    
    # 运行 Roary
    log_info "运行 Roary 泛基因组分析..."
    roary \
        -p "$THREADS" \
        -e \
        -n \
        -v \
        -f "$pangenome_dir" \
        "$gff_input_dir"/*.gff
    
    if [[ -f "$pangenome_dir/gene_presence_absence.csv" ]]; then
        log_success "泛基因组分析完成"
        
        # 生成泛基因组统计信息
        log_info "生成泛基因组统计信息..."
        python3 -c "
import pandas as pd
import sys

# 读取基因存在/缺失矩阵
df = pd.read_csv('$pangenome_dir/gene_presence_absence.csv', low_memory=False)

# 计算统计信息
total_genes = len(df)
core_genes = len(df[df.iloc[:, 14:].notna().all(axis=1)])  # 所有样本都有的基因
accessory_genes = total_genes - core_genes
num_samples = len(df.columns) - 14  # 减去前14个元数据列

# 输出统计信息
with open('$pangenome_dir/pangenome_stats.txt', 'w') as f:
    f.write(f'Total genes: {total_genes}\n')
    f.write(f'Core genes: {core_genes}\n')
    f.write(f'Accessory genes: {accessory_genes}\n')
    f.write(f'Number of samples: {num_samples}\n')
    f.write(f'Core genome percentage: {core_genes/total_genes*100:.2f}%\n')

print(f'泛基因组统计: 总基因 {total_genes}, 核心基因 {core_genes}, 辅助基因 {accessory_genes}')
"
    else
        log_error "泛基因组分析失败"
    fi
    
    local runtime=$(calculate_runtime $step_start)
    log_success "泛基因组分析完成 (耗时: $runtime)"
}

# 6. 系统发育分析 (Phylogenetic Analysis)
run_phylogenetic_analysis() {
    log_step "开始系统发育分析"
    local step_start=$(date +%s)
    
    local phylo_dir="$OUTPUT_DIR/06_phylogenetics"
    create_directory "$phylo_dir"
    
    local pangenome_dir="$OUTPUT_DIR/05_pangenome"
    local core_gene_alignment="$pangenome_dir/core_gene_alignment.aln"
    
    if [[ ! -f "$core_gene_alignment" ]]; then
        log_error "未找到核心基因比对文件: $core_gene_alignment"
        return
    fi
    
    log_info "使用核心基因比对文件进行系统发育分析"
    
    # 使用 MAFFT 重新优化比对（如果需要）
    log_info "使用 MAFFT 优化多序列比对..."
    mafft \
        --auto \
        --thread "$THREADS" \
        --quiet \
        "$core_gene_alignment" > "$phylo_dir/core_genes_mafft.aln"
    
    # 使用 IQ-TREE 构建系统发育树
    log_info "使用 IQ-TREE 构建系统发育树..."
    iqtree \
        -s "$phylo_dir/core_genes_mafft.aln" \
        -m MFP \
        -bb 1000 \
        -alrt 1000 \
        -nt "$THREADS" \
        -pre "$phylo_dir/core_genes_tree" \
        -quiet
    
    if [[ -f "$phylo_dir/core_genes_tree.treefile" ]]; then
        log_success "系统发育树构建完成"
        
        # 生成树的统计信息
        log_info "生成系统发育树统计信息..."
        echo "Phylogenetic Analysis Results" > "$phylo_dir/tree_stats.txt"
        echo "=============================" >> "$phylo_dir/tree_stats.txt"
        echo "Tree file: core_genes_tree.treefile" >> "$phylo_dir/tree_stats.txt"
        echo "Bootstrap support: 1000 replicates" >> "$phylo_dir/tree_stats.txt"
        echo "SH-aLRT support: 1000 replicates" >> "$phylo_dir/tree_stats.txt"
        
        # 计算序列数量
        local num_sequences=$(grep -c ">" "$phylo_dir/core_genes_mafft.aln")
        echo "Number of sequences: $num_sequences" >> "$phylo_dir/tree_stats.txt"
        
        # 计算比对长度
        local alignment_length=$(head -2 "$phylo_dir/core_genes_mafft.aln" | tail -1 | wc -c)
        echo "Alignment length: $alignment_length bp" >> "$phylo_dir/tree_stats.txt"
        
    else
        log_error "系统发育树构建失败"
    fi
    
    local runtime=$(calculate_runtime $step_start)
    log_success "系统发育分析完成 (耗时: $runtime)"
}

# 7. 特定基因筛选 (Gene Screening)
run_gene_screening() {
    log_step "开始特定基因筛选"
    local step_start=$(date +%s)
    
    local screening_dir="$OUTPUT_DIR/07_screening"
    create_directory "$screening_dir"
    
    local assembly_dir="$OUTPUT_DIR/03_assembly"
    local contig_files=($(find "$assembly_dir" -name "*_contigs.fasta" | sort))
    
    if [[ ${#contig_files[@]} -eq 0 ]]; then
        log_error "未找到组装的基因组文件"
        exit 1
    fi
    
    log_info "找到 ${#contig_files[@]} 个基因组进行基因筛选"
    
    # 定义要筛选的数据库
    local databases=("resfinder" "card" "vfdb" "plasmidfinder" "ncbi")
    
    # 为每个数据库创建输出目录
    for db in "${databases[@]}"; do
        create_directory "$screening_dir/$db"
    done
    
    # 对每个基因组运行 ABRicate
    for contig_file in "${contig_files[@]}"; do
        local sample_name=$(basename "$contig_file" | sed 's/_contigs\.fasta$//')
        
        log_info "筛选样本: $sample_name"
        
        # 对每个数据库运行筛选
        for db in "${databases[@]}"; do
            log_info "  使用数据库: $db"
            
            abricate \
                --db "$db" \
                --threads "$THREADS" \
                --minid 80 \
                --mincov 80 \
                "$contig_file" > "$screening_dir/$db/${sample_name}_${db}.txt"
        done
    done
    
    # 汇总所有结果
    log_info "汇总筛选结果..."
    for db in "${databases[@]}"; do
        log_info "  汇总数据库: $db"
        
        # 合并所有样本的结果
        abricate --summary "$screening_dir/$db"/*.txt > "$screening_dir/${db}_summary.txt"
        
        # 生成统计信息
        echo "Database: $db" > "$screening_dir/${db}_stats.txt"
        echo "=============" >> "$screening_dir/${db}_stats.txt"
        
        local total_hits=0
        local files_with_hits=0
        
        for result_file in "$screening_dir/$db"/*.txt; do
            if [[ -f "$result_file" ]]; then
                local hits=$(tail -n +2 "$result_file" | wc -l)
                total_hits=$((total_hits + hits))
                if [[ $hits -gt 0 ]]; then
                    files_with_hits=$((files_with_hits + 1))
                fi
            fi
        done
        
        echo "Total hits: $total_hits" >> "$screening_dir/${db}_stats.txt"
        echo "Samples with hits: $files_with_hits" >> "$screening_dir/${db}_stats.txt"
        echo "Total samples: ${#contig_files[@]}" >> "$screening_dir/${db}_stats.txt"
    done
    
    # 生成综合报告
    log_info "生成综合筛选报告..."
    echo "Gene Screening Summary Report" > "$screening_dir/screening_summary.txt"
    echo "=============================" >> "$screening_dir/screening_summary.txt"
    echo "Generated on: $(date)" >> "$screening_dir/screening_summary.txt"
    echo "" >> "$screening_dir/screening_summary.txt"
    
    for db in "${databases[@]}"; do
        echo "Database: $db" >> "$screening_dir/screening_summary.txt"
        cat "$screening_dir/${db}_stats.txt" | tail -n +2 >> "$screening_dir/screening_summary.txt"
        echo "" >> "$screening_dir/screening_summary.txt"
    done
    
    local runtime=$(calculate_runtime $step_start)
    log_success "特定基因筛选完成 (耗时: $runtime)"
}

#==============================================================================
# 报告生成函数
#==============================================================================

generate_final_report() {
    log_step "生成最终分析报告"
    
    local report_file="$OUTPUT_DIR/GENOME_JIGSAW_REPORT.txt"
    
    cat > "$report_file" << EOF
================================================================================
                        GENOME JIGSAW 分析报告
================================================================================

分析时间: $(date)
输入目录: $INPUT_DIR
输出目录: $OUTPUT_DIR
使用线程: $THREADS
分配内存: $MEMORY

================================================================================
                            分析步骤概览
================================================================================

✅ 1. 质量控制 (Quality Control)
   - 工具: FastQC, MultiQC
   - 输出: $OUTPUT_DIR/01_qc/

✅ 2. 数据清洗 (Data Cleaning)
   - 工具: fastp
   - 输出: $OUTPUT_DIR/02_clean/

✅ 3. 基因组组装 (Genome Assembly)
   - 工具: SPAdes
   - 输出: $OUTPUT_DIR/03_assembly/

✅ 4. 基因组注释 (Genome Annotation)
   - 工具: Prokka
   - 输出: $OUTPUT_DIR/04_annotation/

✅ 5. 泛基因组分析 (Pan-genome Analysis)
   - 工具: Roary
   - 输出: $OUTPUT_DIR/05_pangenome/

✅ 6. 系统发育分析 (Phylogenetic Analysis)
   - 工具: MAFFT, IQ-TREE
   - 输出: $OUTPUT_DIR/06_phylogenetics/

✅ 7. 特定基因筛选 (Gene Screening)
   - 工具: ABRicate
   - 输出: $OUTPUT_DIR/07_screening/

================================================================================
                            关键结果文件
================================================================================

📊 质量控制报告:
   - $OUTPUT_DIR/01_qc/multiqc_raw_data.html
   - $OUTPUT_DIR/02_clean/qc/multiqc_clean_data.html

🧬 基因组组装:
   - $OUTPUT_DIR/03_assembly/assembly_stats.txt
   - $OUTPUT_DIR/03_assembly/*_contigs.fasta

📝 基因组注释:
   - $OUTPUT_DIR/04_annotation/annotation_stats.txt
   - $OUTPUT_DIR/04_annotation/*/

🔍 泛基因组分析:
   - $OUTPUT_DIR/05_pangenome/gene_presence_absence.csv
   - $OUTPUT_DIR/05_pangenome/pangenome_stats.txt

🌳 系统发育树:
   - $OUTPUT_DIR/06_phylogenetics/core_genes_tree.treefile
   - $OUTPUT_DIR/06_phylogenetics/tree_stats.txt

🎯 基因筛选:
   - $OUTPUT_DIR/07_screening/screening_summary.txt
   - $OUTPUT_DIR/07_screening/*_summary.txt

================================================================================
                            下游分析建议
================================================================================

1. 分子演化研究:
   - 使用系统发育树 (core_genes_tree.treefile) 进行进化分析
   - 分析泛基因组的基因获得/丢失模式
   - 计算进化距离和分化时间

2. 特异性靶点筛选:
   - 分析核心基因组中的保守序列
   - 筛选种/株特异性基因
   - 结合耐药/毒力基因信息进行靶点设计

3. 比较基因组学:
   - 分析基因组结构变异
   - 比较不同菌株的基因组特征
   - 识别水平基因转移事件

================================================================================
                              分析完成
================================================================================

总运行时间: $(calculate_runtime $PIPELINE_START)
日志文件: $LOG_FILE

如有问题，请查看详细日志文件或联系分析团队。

EOF

    log_success "最终报告已生成: $report_file"
}

#==============================================================================
# 主程序
#==============================================================================

# 显示帮助信息
show_help() {
    cat << EOF
🧬 Genome Jigsaw - 自动化细菌全基因组测序分析流水线

用法: $0 [选项] <输入目录>

参数:
    <输入目录>          包含原始 FASTQ 文件的目录路径
                       文件命名格式: *_R1.fastq.gz 和 *_R2.fastq.gz

选项:
    -o, --output DIR    输出目录 (默认: results)
    -t, --threads NUM   使用的线程数 (默认: 自动检测)
    -m, --memory SIZE   内存限制 (默认: 16G)
    -h, --help          显示此帮助信息

示例:
    $0 /path/to/fastq/files
    $0 -o my_results -t 8 -m 32G /path/to/fastq/files

分析流程:
    1. 质量控制 (FastQC)
    2. 数据清洗 (fastp)
    3. 基因组组装 (SPAdes)
    4. 基因组注释 (Prokka)
    5. 泛基因组分析 (Roary)
    6. 系统发育分析 (MAFFT + IQ-TREE)
    7. 特定基因筛选 (ABRicate)

注意:
    - 请确保已激活 genome-jigsaw conda 环境
    - 输入目录中应包含成对的 FASTQ 文件
    - 建议至少 16GB 内存和 8 个 CPU 核心

EOF
}

# 解析命令行参数
parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -o|--output)
                OUTPUT_DIR="$2"
                shift 2
                ;;
            -t|--threads)
                THREADS="$2"
                shift 2
                ;;
            -m|--memory)
                MEMORY="$2"
                shift 2
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            -*)
                log_error "未知选项: $1"
                show_help
                exit 1
                ;;
            *)
                if [[ -z "$INPUT_DIR" ]]; then
                    INPUT_DIR="$1"
                else
                    log_error "多余的参数: $1"
                    show_help
                    exit 1
                fi
                shift
                ;;
        esac
    done
}

# 验证输入参数
validate_inputs() {
    if [[ -z "$INPUT_DIR" ]]; then
        log_error "请提供输入目录路径"
        show_help
        exit 1
    fi
    
    check_directory "$INPUT_DIR"
    
    # 检查是否有 FASTQ 文件
    local fastq_count=$(find "$INPUT_DIR" -name "*.fastq.gz" -o -name "*.fq.gz" | wc -l)
    if [[ $fastq_count -eq 0 ]]; then
        log_error "输入目录中未找到 FASTQ 文件 (*.fastq.gz 或 *.fq.gz)"
        exit 1
    fi
    
    # 检查成对文件
    local r1_count=$(find "$INPUT_DIR" -name "*_R1.fastq.gz" -o -name "*_1.fastq.gz" | wc -l)
    if [[ $r1_count -eq 0 ]]; then
        log_error "未找到 R1 文件 (*_R1.fastq.gz 或 *_1.fastq.gz)"
        exit 1
    fi
    
    log_info "输入验证通过: 找到 $fastq_count 个 FASTQ 文件，$r1_count 个样本"
}

# 检查依赖工具
check_dependencies() {
    log_info "检查依赖工具..."
    
    local tools=("fastqc" "multiqc" "fastp" "spades.py" "prokka" "roary" "mafft" "iqtree" "abricate")
    local missing_tools=()
    
    for tool in "${tools[@]}"; do
        if command -v "$tool" &> /dev/null; then
            log_info "  ✅ $tool"
        else
            log_error "  ❌ $tool"
            missing_tools+=("$tool")
        fi
    done
    
    if [[ ${#missing_tools[@]} -gt 0 ]]; then
        log_error "缺少以下工具: ${missing_tools[*]}"
        log_error "请确保已正确安装并激活 genome-jigsaw conda 环境"
        exit 1
    fi
    
    log_success "所有依赖工具检查通过"
}

# 初始化环境
initialize_environment() {
    # 创建输出目录
    create_directory "$OUTPUT_DIR"
    
    # 设置日志文件
    LOG_FILE="$OUTPUT_DIR/genome_jigsaw_${TIMESTAMP}.log"
    
    # 记录开始信息
    log_info "🧬 Genome Jigsaw 分析流水线启动"
    log_info "版本: 1.0.0"
    log_info "时间: $(date)"
    log_info "输入目录: $INPUT_DIR"
    log_info "输出目录: $OUTPUT_DIR"
    log_info "线程数: $THREADS"
    log_info "内存限制: $MEMORY"
    log_info "日志文件: $LOG_FILE"
    
    # 记录系统信息
    log_info "系统信息:"
    log_info "  操作系统: $(uname -s)"
    log_info "  内核版本: $(uname -r)"
    log_info "  CPU 核心: $(nproc)"
    log_info "  可用内存: $(free -h | grep '^Mem:' | awk '{print $7}')"
    log_info "  磁盘空间: $(df -h . | tail -1 | awk '{print $4}')"
}

# 主函数
main() {
    # 记录流水线开始时间
    PIPELINE_START=$(date +%s)
    
    # 解析命令行参数
    parse_arguments "$@"
    
    # 初始化环境
    initialize_environment
    
    # 验证输入
    validate_inputs
    
    # 检查依赖
    check_dependencies
    
    # 执行分析流程
    log_info "🚀 开始执行分析流程..."
    
    run_quality_control
    run_data_cleaning
    run_genome_assembly
    run_genome_annotation
    run_pangenome_analysis
    run_phylogenetic_analysis
    run_gene_screening
    
    # 生成最终报告
    generate_final_report
    
    # 计算总运行时间
    local total_runtime=$(calculate_runtime $PIPELINE_START)
    
    log_success "🎉 Genome Jigsaw 分析流水线完成！"
    log_success "总运行时间: $total_runtime"
    log_success "结果目录: $OUTPUT_DIR"
    log_success "分析报告: $OUTPUT_DIR/GENOME_JIGSAW_REPORT.txt"
    
    # 显示结果概览
    echo ""
    echo -e "${GREEN}================================================================================${NC}"
    echo -e "${GREEN}                           🧬 分析完成概览 🧬${NC}"
    echo -e "${GREEN}================================================================================${NC}"
    echo -e "${CYAN}📁 结果目录: ${NC}$OUTPUT_DIR"
    echo -e "${CYAN}📊 分析报告: ${NC}$OUTPUT_DIR/GENOME_JIGSAW_REPORT.txt"
    echo -e "${CYAN}📝 日志文件: ${NC}$LOG_FILE"
    echo -e "${CYAN}⏱️  总耗时: ${NC}$total_runtime"
    echo -e "${GREEN}================================================================================${NC}"
    echo ""
}

# 错误处理
trap 'log_error "脚本执行过程中发生错误，请查看日志文件: $LOG_FILE"; exit 1' ERR

# 执行主函数
main "$@"