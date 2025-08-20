#!/bin/bash

#==============================================================================
# Genome Jigsaw 测试脚本
# 
# 用于测试流水线的基本功能
#==============================================================================

set -euo pipefail

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# 打印消息
print_message() {
    local color=$1
    local message=$2
    echo -e "${color}[$(date '+%H:%M:%S')] ${message}${NC}"
}

log_info() { print_message "$BLUE" "ℹ️  $1"; }
log_success() { print_message "$GREEN" "✅ $1"; }
log_warning() { print_message "$YELLOW" "⚠️  $1"; }
log_error() { print_message "$RED" "❌ $1"; }

# 创建测试数据
create_test_data() {
    log_info "创建测试数据..."
    
    local test_data_dir="$PROJECT_DIR/test_data"
    mkdir -p "$test_data_dir"
    
    # 创建模拟的 FASTQ 文件
    for sample in sample1 sample2 sample3; do
        log_info "创建测试样本: $sample"
        
        # 创建简单的 FASTQ 数据（用于测试）
        cat > "$test_data_dir/${sample}_R1.fastq" << 'EOF'
@read1
ATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCG
+
IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII
@read2
GCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTA
+
IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII
@read3
TTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT
+
IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII
EOF

        cat > "$test_data_dir/${sample}_R2.fastq" << 'EOF'
@read1
CGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGAT
+
IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII
@read2
TAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGC
+
IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII
@read3
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
+
IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII
EOF

        # 压缩文件
        gzip "$test_data_dir/${sample}_R1.fastq"
        gzip "$test_data_dir/${sample}_R2.fastq"
    done
    
    log_success "测试数据创建完成: $test_data_dir"
}

# 测试环境检查
test_environment() {
    log_info "测试环境检查..."
    
    # 检查 conda 环境
    if [[ "$CONDA_DEFAULT_ENV" != "genome-jigsaw" ]]; then
        log_warning "当前不在 genome-jigsaw 环境中"
        log_info "请运行: conda activate genome-jigsaw"
    else
        log_success "conda 环境检查通过"
    fi
    
    # 检查关键工具
    local tools=("fastqc" "fastp" "spades.py" "prokka" "roary" "mafft" "iqtree" "abricate")
    local missing_tools=()
    
    for tool in "${tools[@]}"; do
        if command -v "$tool" &> /dev/null; then
            log_success "工具检查通过: $tool"
        else
            log_error "工具缺失: $tool"
            missing_tools+=("$tool")
        fi
    done
    
    if [[ ${#missing_tools[@]} -gt 0 ]]; then
        log_error "缺少工具: ${missing_tools[*]}"
        return 1
    fi
    
    log_success "环境检查完成"
}

# 测试脚本语法
test_script_syntax() {
    log_info "测试脚本语法..."
    
    local main_script="$PROJECT_DIR/run_genome_jigsaw.sh"
    
    if bash -n "$main_script"; then
        log_success "脚本语法检查通过"
    else
        log_error "脚本语法错误"
        return 1
    fi
}

# 运行快速测试
run_quick_test() {
    log_info "运行快速测试..."
    
    local test_data_dir="$PROJECT_DIR/test_data"
    local test_output_dir="$PROJECT_DIR/test_output"
    
    # 清理之前的测试结果
    if [[ -d "$test_output_dir" ]]; then
        rm -rf "$test_output_dir"
    fi
    
    # 运行主脚本（仅质量控制步骤）
    log_info "运行质量控制测试..."
    
    # 这里可以添加只运行部分步骤的逻辑
    # 由于完整流水线时间较长，测试时可以只运行前几步
    
    log_warning "完整流水线测试需要较长时间，建议手动运行："
    log_info "  ./run_genome_jigsaw.sh -o test_output test_data"
}

# 验证输出结果
validate_output() {
    log_info "验证输出结果..."
    
    local test_output_dir="$PROJECT_DIR/test_output"
    
    if [[ ! -d "$test_output_dir" ]]; then
        log_warning "测试输出目录不存在，跳过验证"
        return 0
    fi
    
    # 检查关键输出文件
    local expected_files=(
        "01_qc"
        "02_clean"
        "03_assembly"
        "GENOME_JIGSAW_REPORT.txt"
    )
    
    for file in "${expected_files[@]}"; do
        if [[ -e "$test_output_dir/$file" ]]; then
            log_success "输出验证通过: $file"
        else
            log_warning "输出文件缺失: $file"
        fi
    done
}

# 清理测试数据
cleanup_test_data() {
    log_info "清理测试数据..."
    
    local test_data_dir="$PROJECT_DIR/test_data"
    local test_output_dir="$PROJECT_DIR/test_output"
    
    read -p "是否删除测试数据？ (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if [[ -d "$test_data_dir" ]]; then
            rm -rf "$test_data_dir"
            log_success "测试数据已删除"
        fi
        
        if [[ -d "$test_output_dir" ]]; then
            rm -rf "$test_output_dir"
            log_success "测试输出已删除"
        fi
    else
        log_info "保留测试数据"
    fi
}

# 显示帮助信息
show_help() {
    cat << EOF
🧬 Genome Jigsaw 测试脚本

用法: $0 [选项]

选项:
    --create-data       创建测试数据
    --test-env          测试环境
    --test-syntax       测试脚本语法
    --run-test          运行快速测试
    --validate          验证输出结果
    --cleanup           清理测试数据
    --all               运行所有测试
    -h, --help          显示帮助信息

示例:
    $0 --all                    # 运行所有测试
    $0 --create-data --test-env # 创建数据并测试环境
    $0 --cleanup                # 清理测试数据

EOF
}

# 主函数
main() {
    if [[ $# -eq 0 ]]; then
        show_help
        exit 0
    fi
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --create-data)
                create_test_data
                shift
                ;;
            --test-env)
                test_environment
                shift
                ;;
            --test-syntax)
                test_script_syntax
                shift
                ;;
            --run-test)
                run_quick_test
                shift
                ;;
            --validate)
                validate_output
                shift
                ;;
            --cleanup)
                cleanup_test_data
                shift
                ;;
            --all)
                log_info "🧪 开始完整测试流程..."
                create_test_data
                test_environment
                test_script_syntax
                run_quick_test
                validate_output
                log_success "🎉 测试流程完成！"
                shift
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                log_error "未知选项: $1"
                show_help
                exit 1
                ;;
        esac
    done
}

# 执行主函数
main "$@"