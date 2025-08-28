#!/bin/bash

#==============================================================================
# Kinetic Scope (动力学观测仪) - 批量运行工具
# 
# 功能: 批量处理多个PDB文件的分子动力学模拟
# 作者: Research Workstation Team
# 版本: 1.0.0
# 日期: 2025-08-20
#==============================================================================

set -euo pipefail

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

# 日志函数
log_info() {
    echo -e "${BLUE}[$(date '+%H:%M:%S')] ℹ️  INFO: $1${NC}"
}

log_success() {
    echo -e "${GREEN}[$(date '+%H:%M:%S')] ✅ SUCCESS: $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}[$(date '+%H:%M:%S')] ⚠️  WARNING: $1${NC}"
}

log_error() {
    echo -e "${RED}[$(date '+%H:%M:%S')] ❌ ERROR: $1${NC}"
}

log_step() {
    echo -e "${PURPLE}[$(date '+%H:%M:%S')] 🔬 STEP: $1${NC}"
}

# 显示帮助信息
show_help() {
    cat << EOF
🧬 Kinetic Scope (动力学观测仪) - 批量运行工具

用法: $0 [选项] <PDB文件目录>

选项:
    -s, --stage STAGE       运行阶段 (prepare|simulate|analyze|all)
    -t, --time TIME         模拟时长 (ns) (默认: 100)
    -p, --nproc NUM         处理器核心数 (默认: 8)
    -f, --forcefield FF     力场 (默认: amber99sb-ildn)
    -w, --water MODEL       水模型 (默认: tip3p)
    -c, --conc CONC         盐浓度 (默认: 0.15)
    -o, --output DIR        输出根目录 (默认: batch_results)
    --dry-run               仅显示将要执行的命令，不实际运行
    -h, --help              显示帮助信息

阶段说明:
    prepare     仅执行系统搭建
    simulate    仅执行模拟 (需要先完成prepare)
    analyze     仅执行分析 (需要先完成simulate)
    all         执行完整流程 (默认)

示例:
    $0 pdb_files/                           # 处理pdb_files目录中的所有PDB文件
    $0 -s prepare pdb_files/                # 仅进行系统搭建
    $0 -t 200 -p 16 pdb_files/             # 200ns模拟，16核并行
    $0 --dry-run pdb_files/                 # 预览将要执行的操作

EOF
}

# 默认参数
STAGE="all"
SIMULATION_TIME="100"
NPROC="8"
FORCE_FIELD="amber99sb-ildn"
WATER_MODEL="tip3p"
SALT_CONCENTRATION="0.15"
OUTPUT_DIR="batch_results"
DRY_RUN=false
PDB_DIR=""

# 解析命令行参数
parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -s|--stage)
                STAGE="$2"
                shift 2
                ;;
            -t|--time)
                SIMULATION_TIME="$2"
                shift 2
                ;;
            -p|--nproc)
                NPROC="$2"
                shift 2
                ;;
            -f|--forcefield)
                FORCE_FIELD="$2"
                shift 2
                ;;
            -w|--water)
                WATER_MODEL="$2"
                shift 2
                ;;
            -c|--conc)
                SALT_CONCENTRATION="$2"
                shift 2
                ;;
            -o|--output)
                OUTPUT_DIR="$2"
                shift 2
                ;;
            --dry-run)
                DRY_RUN=true
                shift
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
                if [[ -z "$PDB_DIR" ]]; then
                    PDB_DIR="$1"
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

# 验证输入
validate_inputs() {
    if [[ -z "$PDB_DIR" ]]; then
        log_error "请提供PDB文件目录"
        show_help
        exit 1
    fi
    
    if [[ ! -d "$PDB_DIR" ]]; then
        log_error "PDB目录不存在: $PDB_DIR"
        exit 1
    fi
    
    # 检查PDB文件
    local pdb_count=$(find "$PDB_DIR" -name "*.pdb" | wc -l)
    if [[ $pdb_count -eq 0 ]]; then
        log_error "在 $PDB_DIR 中未找到PDB文件"
        exit 1
    fi
    
    log_info "找到 $pdb_count 个PDB文件"
    
    # 验证阶段参数
    case $STAGE in
        prepare|simulate|analyze|all)
            ;;
        *)
            log_error "无效的阶段: $STAGE"
            exit 1
            ;;
    esac
}

# 创建工作目录
setup_workspace() {
    local system_name=$1
    local work_dir="$OUTPUT_DIR/$system_name"
    
    mkdir -p "$work_dir"
    
    # 复制脚本到工作目录
    cp ../sop_scripts/*.sh "$work_dir/"
    cp -r ../analysis_tools "$work_dir/"
    cp -r ../templates "$work_dir/"
    
    echo "$work_dir"
}

# 修改脚本参数
modify_script_parameters() {
    local work_dir=$1
    local pdb_file=$2
    local system_name=$3
    
    # 修改系统搭建脚本
    sed -i "s|INPUT_PDB=.*|INPUT_PDB=\"$(basename "$pdb_file")\"|" "$work_dir/sop_prepare_system.sh"
    sed -i "s|SYSTEM_NAME=.*|SYSTEM_NAME=\"$system_name\"|" "$work_dir/sop_prepare_system.sh"
    sed -i "s|FORCE_FIELD=.*|FORCE_FIELD=\"$FORCE_FIELD\"|" "$work_dir/sop_prepare_system.sh"
    sed -i "s|WATER_MODEL=.*|WATER_MODEL=\"$WATER_MODEL\"|" "$work_dir/sop_prepare_system.sh"
    sed -i "s|SALT_CONCENTRATION=.*|SALT_CONCENTRATION=\"$SALT_CONCENTRATION\"|" "$work_dir/sop_prepare_system.sh"
    sed -i "s|NPROC=.*|NPROC=\"$NPROC\"|" "$work_dir/sop_prepare_system.sh"
    
    # 修改模拟脚本
    sed -i "s|SYSTEM_NAME=.*|SYSTEM_NAME=\"$system_name\"|" "$work_dir/sop_run_simulation.sh"
    sed -i "s|SIMULATION_TIME_NS=.*|SIMULATION_TIME_NS=\"$SIMULATION_TIME\"|" "$work_dir/sop_run_simulation.sh"
    sed -i "s|NPROC=.*|NPROC=\"$NPROC\"|" "$work_dir/sop_run_simulation.sh"
    
    # 修改分析脚本
    sed -i "s|SYSTEM_NAME=.*|SYSTEM_NAME=\"$system_name\"|" "$work_dir/sop_analyze_trajectory.sh"
}

# 执行单个系统的处理
process_system() {
    local pdb_file=$1
    local system_name=$(basename "$pdb_file" .pdb)
    
    log_step "处理系统: $system_name"
    
    # 创建工作目录
    local work_dir=$(setup_workspace "$system_name")
    
    # 复制PDB文件
    cp "$pdb_file" "$work_dir/"
    
    # 修改脚本参数
    modify_script_parameters "$work_dir" "$pdb_file" "$system_name"
    
    # 进入工作目录
    cd "$work_dir"
    
    local system_start=$(date +%s)
    
    # 执行相应阶段
    case $STAGE in
        prepare|all)
            log_info "[$system_name] 开始系统搭建..."
            if [[ "$DRY_RUN" == "true" ]]; then
                echo "DRY RUN: ./sop_prepare_system.sh"
            else
                if ./sop_prepare_system.sh; then
                    log_success "[$system_name] 系统搭建完成"
                else
                    log_error "[$system_name] 系统搭建失败"
                    cd - > /dev/null
                    return 1
                fi
            fi
            ;&  # 继续执行下一个case (仅当STAGE=all时)
        simulate)
            if [[ "$STAGE" == "all" || "$STAGE" == "simulate" ]]; then
                log_info "[$system_name] 开始模拟执行..."
                if [[ "$DRY_RUN" == "true" ]]; then
                    echo "DRY RUN: ./sop_run_simulation.sh"
                else
                    if ./sop_run_simulation.sh; then
                        log_success "[$system_name] 模拟执行完成"
                    else
                        log_error "[$system_name] 模拟执行失败"
                        cd - > /dev/null
                        return 1
                    fi
                fi
            fi
            ;&  # 继续执行下一个case (仅当STAGE=all时)
        analyze)
            if [[ "$STAGE" == "all" || "$STAGE" == "analyze" ]]; then
                log_info "[$system_name] 开始轨迹分析..."
                if [[ "$DRY_RUN" == "true" ]]; then
                    echo "DRY RUN: ./sop_analyze_trajectory.sh"
                    echo "DRY RUN: python analysis_tools/plot_results.py --summary analysis/"
                else
                    if ./sop_analyze_trajectory.sh; then
                        log_success "[$system_name] 轨迹分析完成"
                        
                        # 生成图表
                        log_info "[$system_name] 生成分析图表..."
                        python analysis_tools/plot_results.py --summary analysis/ || log_warning "[$system_name] 图表生成失败"
                    else
                        log_error "[$system_name] 轨迹分析失败"
                        cd - > /dev/null
                        return 1
                    fi
                fi
            fi
            ;;
    esac
    
    # 计算耗时
    local system_end=$(date +%s)
    local system_runtime=$((system_end - system_start))
    local hours=$((system_runtime / 3600))
    local minutes=$(((system_runtime % 3600) / 60))
    local seconds=$((system_runtime % 60))
    
    log_success "[$system_name] 处理完成，耗时: ${hours}h ${minutes}m ${seconds}s"
    
    cd - > /dev/null
    return 0
}

# 生成批量报告
generate_batch_report() {
    local report_file="$OUTPUT_DIR/batch_report.txt"
    
    cat > "$report_file" << EOF
================================================================================
                        批量分子动力学模拟报告
================================================================================

处理时间: $(date)
PDB目录: $PDB_DIR
输出目录: $OUTPUT_DIR
处理阶段: $STAGE

参数配置:
  - 模拟时长: $SIMULATION_TIME ns
  - 处理器核心: $NPROC
  - 力场: $FORCE_FIELD
  - 水模型: $WATER_MODEL
  - 盐浓度: $SALT_CONCENTRATION M

处理结果:
================================================================================

EOF

    # 统计处理结果
    local total_systems=0
    local successful_systems=0
    local failed_systems=0
    
    for system_dir in "$OUTPUT_DIR"/*/; do
        if [[ -d "$system_dir" ]]; then
            local system_name=$(basename "$system_dir")
            total_systems=$((total_systems + 1))
            
            # 检查是否成功完成
            local success=true
            case $STAGE in
                prepare|all)
                    if [[ ! -f "$system_dir/${system_name}_solv_ions.gro" ]]; then
                        success=false
                    fi
                    ;&
                simulate)
                    if [[ "$STAGE" == "all" || "$STAGE" == "simulate" ]]; then
                        if [[ ! -f "$system_dir/md.xtc" ]]; then
                            success=false
                        fi
                    fi
                    ;&
                analyze)
                    if [[ "$STAGE" == "all" || "$STAGE" == "analyze" ]]; then
                        if [[ ! -f "$system_dir/analysis/${system_name}_analysis_report.txt" ]]; then
                            success=false
                        fi
                    fi
                    ;;
            esac
            
            if [[ "$success" == "true" ]]; then
                echo "✅ $system_name - 成功" >> "$report_file"
                successful_systems=$((successful_systems + 1))
            else
                echo "❌ $system_name - 失败" >> "$report_file"
                failed_systems=$((failed_systems + 1))
            fi
        fi
    done
    
    cat >> "$report_file" << EOF

================================================================================
                              统计汇总
================================================================================

总系统数: $total_systems
成功处理: $successful_systems
处理失败: $failed_systems
成功率: $(( successful_systems * 100 / total_systems ))%

================================================================================

各系统详细结果请查看对应的子目录。

EOF

    log_success "批量报告已生成: $report_file"
}

# 主函数
main() {
    # 解析参数
    parse_arguments "$@"
    
    # 显示开始信息
    echo -e "${PURPLE}================================================================================${NC}"
    echo -e "${PURPLE}           🧬 Kinetic Scope (动力学观测仪) - 批量运行工具 🧬${NC}"
    echo -e "${PURPLE}================================================================================${NC}"
    
    log_info "批量处理开始"
    log_info "PDB目录: $PDB_DIR"
    log_info "输出目录: $OUTPUT_DIR"
    log_info "处理阶段: $STAGE"
    log_info "模拟时长: $SIMULATION_TIME ns"
    log_info "处理器核心: $NPROC"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log_warning "DRY RUN模式 - 仅显示将要执行的命令"
    fi
    
    # 验证输入
    validate_inputs
    
    # 创建输出目录
    mkdir -p "$OUTPUT_DIR"
    
    # 记录开始时间
    local batch_start=$(date +%s)
    
    # 处理所有PDB文件
    local total_files=0
    local successful_files=0
    local failed_files=0
    
    for pdb_file in "$PDB_DIR"/*.pdb; do
        if [[ -f "$pdb_file" ]]; then
            total_files=$((total_files + 1))
            
            if process_system "$pdb_file"; then
                successful_files=$((successful_files + 1))
            else
                failed_files=$((failed_files + 1))
            fi
        fi
    done
    
    # 计算总耗时
    local batch_end=$(date +%s)
    local batch_runtime=$((batch_end - batch_start))
    local hours=$((batch_runtime / 3600))
    local minutes=$(((batch_runtime % 3600) / 60))
    local seconds=$((batch_runtime % 60))
    
    # 生成批量报告
    if [[ "$DRY_RUN" == "false" ]]; then
        generate_batch_report
    fi
    
    # 显示最终结果
    echo ""
    echo -e "${GREEN}================================================================================${NC}"
    echo -e "${GREEN}                           🧬 批量处理完成 🧬${NC}"
    echo -e "${GREEN}================================================================================${NC}"
    echo -e "${CYAN}📁 输出目录: ${NC}$OUTPUT_DIR"
    echo -e "${CYAN}📊 总文件数: ${NC}$total_files"
    echo -e "${CYAN}✅ 成功处理: ${NC}$successful_files"
    echo -e "${CYAN}❌ 处理失败: ${NC}$failed_files"
    echo -e "${CYAN}📈 成功率: ${NC}$(( successful_files * 100 / total_files ))%"
    echo -e "${CYAN}⏱️  总耗时: ${NC}${hours}h ${minutes}m ${seconds}s"
    echo -e "${GREEN}================================================================================${NC}"
    echo ""
    
    if [[ $failed_files -gt 0 ]]; then
        log_warning "有 $failed_files 个系统处理失败，请检查日志"
        exit 1
    else
        log_success "所有系统处理成功！"
    fi
}

# 错误处理
trap 'log_error "批量处理过程中发生错误"; exit 1' ERR

# 执行主函数
main "$@"