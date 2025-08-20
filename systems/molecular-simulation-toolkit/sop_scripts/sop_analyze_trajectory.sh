#!/bin/bash

#==============================================================================
# Molecular Simulation Toolkit - 轨迹分析标准作业流程
# 
# 功能: 自动化执行分子动力学轨迹的标准分析
# 作者: Research Workstation Team
# 版本: 1.0.0
# 日期: 2025-08-20
#==============================================================================

set -euo pipefail  # 严格模式

#==============================================================================
# 🔧 用户配置参数 - 根据您的分析需求修改这些参数
#==============================================================================

# 输入文件配置
SYSTEM_NAME="system"                       # 系统名称
TRAJECTORY_FILE="md.xtc"                   # 轨迹文件
STRUCTURE_FILE="md.gro"                    # 结构文件
TOPOLOGY_FILE="${SYSTEM_NAME}.top"         # 拓扑文件
TPR_FILE="md.tpr"                          # 运行参数文件

# 分析时间范围配置
START_TIME="0"                             # 分析起始时间 (ps)
END_TIME="-1"                              # 分析结束时间 (ps, -1表示到结尾)
TIME_STEP="10"                             # 时间步长 (ps)

# 分析组配置
PROTEIN_GROUP="Protein"                    # 蛋白质组名
BACKBONE_GROUP="Backbone"                  # 主链组名
SYSTEM_GROUP="System"                      # 整个系统组名

# 输出配置
OUTPUT_DIR="analysis"                      # 输出目录
PLOT_FORMAT="png"                          # 图片格式 (png, pdf, svg)

#==============================================================================
# 🎨 颜色和日志配置
#==============================================================================

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

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

#==============================================================================
# 🛠️ 工具函数
#==============================================================================

# 检查文件是否存在
check_file() {
    if [[ ! -f "$1" ]]; then
        log_error "文件不存在: $1"
        exit 1
    fi
}

# 检查GROMACS命令是否可用
check_gromacs() {
    if ! command -v gmx &> /dev/null; then
        log_error "GROMACS未安装或未在PATH中"
        exit 1
    fi
    log_success "GROMACS检查通过: $(gmx --version | head -1)"
}

# 创建目录
create_directory() {
    if [[ ! -d "$1" ]]; then
        mkdir -p "$1"
        log_info "创建目录: $1"
    fi
}

# 计算运行时间
calculate_runtime() {
    local start_time=$1
    local end_time=$(date +%s)
    local runtime=$((end_time - start_time))
    local minutes=$((runtime / 60))
    local seconds=$((runtime % 60))
    printf "%02d:%02d" $minutes $seconds
}

# 构建时间参数
build_time_params() {
    local params=""
    if [[ "$START_TIME" != "0" ]]; then
        params="$params -b $START_TIME"
    fi
    if [[ "$END_TIME" != "-1" ]]; then
        params="$params -e $END_TIME"
    fi
    if [[ "$TIME_STEP" != "10" ]]; then
        params="$params -dt $TIME_STEP"
    fi
    echo "$params"
}

#==============================================================================
# 🧬 主要分析函数
#==============================================================================

# 分析1: RMSD分析 (均方根偏差)
analyze_rmsd() {
    log_step "RMSD分析 - 评估结构稳定性"
    local step_start=$(date +%s)
    
    check_file "$TRAJECTORY_FILE"
    check_file "$STRUCTURE_FILE"
    
    local time_params=$(build_time_params)
    
    # 对主链进行RMSD分析
    log_info "计算主链RMSD..."
    echo -e "${BACKBONE_GROUP}\n${BACKBONE_GROUP}" | gmx rms \
        -s "$STRUCTURE_FILE" \
        -f "$TRAJECTORY_FILE" \
        -o "$OUTPUT_DIR/rmsd_backbone.xvg" \
        -tu ns \
        $time_params \
        -quiet
    
    # 对整个蛋白质进行RMSD分析
    log_info "计算蛋白质RMSD..."
    echo -e "${PROTEIN_GROUP}\n${PROTEIN_GROUP}" | gmx rms \
        -s "$STRUCTURE_FILE" \
        -f "$TRAJECTORY_FILE" \
        -o "$OUTPUT_DIR/rmsd_protein.xvg" \
        -tu ns \
        $time_params \
        -quiet
    
    if [[ -f "$OUTPUT_DIR/rmsd_backbone.xvg" && -f "$OUTPUT_DIR/rmsd_protein.xvg" ]]; then
        log_success "RMSD分析完成"
        
        # 计算平均RMSD
        local avg_rmsd_backbone=$(tail -n +25 "$OUTPUT_DIR/rmsd_backbone.xvg" | awk '{sum+=$2; count++} END {print sum/count}')
        local avg_rmsd_protein=$(tail -n +25 "$OUTPUT_DIR/rmsd_protein.xvg" | awk '{sum+=$2; count++} END {print sum/count}')
        
        log_info "主链平均RMSD: ${avg_rmsd_backbone} nm"
        log_info "蛋白质平均RMSD: ${avg_rmsd_protein} nm"
    else
        log_error "RMSD分析失败"
    fi
    
    local runtime=$(calculate_runtime $step_start)
    log_success "RMSD分析耗时: $runtime"
}

# 分析2: RMSF分析 (均方根涨落)
analyze_rmsf() {
    log_step "RMSF分析 - 评估残基柔性"
    local step_start=$(date +%s)
    
    check_file "$TRAJECTORY_FILE"
    check_file "$STRUCTURE_FILE"
    
    local time_params=$(build_time_params)
    
    # 计算主链RMSF
    log_info "计算主链RMSF..."
    echo "$BACKBONE_GROUP" | gmx rmsf \
        -s "$STRUCTURE_FILE" \
        -f "$TRAJECTORY_FILE" \
        -o "$OUTPUT_DIR/rmsf_backbone.xvg" \
        -res \
        $time_params \
        -quiet
    
    # 计算侧链RMSF
    log_info "计算蛋白质RMSF..."
    echo "$PROTEIN_GROUP" | gmx rmsf \
        -s "$STRUCTURE_FILE" \
        -f "$TRAJECTORY_FILE" \
        -o "$OUTPUT_DIR/rmsf_protein.xvg" \
        -res \
        $time_params \
        -quiet
    
    if [[ -f "$OUTPUT_DIR/rmsf_backbone.xvg" && -f "$OUTPUT_DIR/rmsf_protein.xvg" ]]; then
        log_success "RMSF分析完成"
        
        # 找出最柔性的残基
        local max_rmsf_residue=$(tail -n +25 "$OUTPUT_DIR/rmsf_backbone.xvg" | awk 'BEGIN{max=0; res=0} {if($2>max){max=$2; res=$1}} END{print res}')
        local max_rmsf_value=$(tail -n +25 "$OUTPUT_DIR/rmsf_backbone.xvg" | awk 'BEGIN{max=0} {if($2>max){max=$2}} END{print max}')
        
        log_info "最柔性残基: ${max_rmsf_residue} (RMSF = ${max_rmsf_value} nm)"
    else
        log_error "RMSF分析失败"
    fi
    
    local runtime=$(calculate_runtime $step_start)
    log_success "RMSF分析耗时: $runtime"
}

# 分析3: 氢键分析
analyze_hydrogen_bonds() {
    log_step "氢键分析 - 评估分子间相互作用"
    local step_start=$(date +%s)
    
    check_file "$TRAJECTORY_FILE"
    check_file "$TPR_FILE"
    
    local time_params=$(build_time_params)
    
    # 分析蛋白质内部氢键
    log_info "分析蛋白质内部氢键..."
    echo -e "${PROTEIN_GROUP}\n${PROTEIN_GROUP}" | gmx hbond \
        -s "$TPR_FILE" \
        -f "$TRAJECTORY_FILE" \
        -num "$OUTPUT_DIR/hbond_intra.xvg" \
        -tu ns \
        $time_params \
        -quiet
    
    # 分析蛋白质-水氢键
    log_info "分析蛋白质-水氢键..."
    echo -e "${PROTEIN_GROUP}\nWater" | gmx hbond \
        -s "$TPR_FILE" \
        -f "$TRAJECTORY_FILE" \
        -num "$OUTPUT_DIR/hbond_water.xvg" \
        -tu ns \
        $time_params \
        -quiet
    
    if [[ -f "$OUTPUT_DIR/hbond_intra.xvg" && -f "$OUTPUT_DIR/hbond_water.xvg" ]]; then
        log_success "氢键分析完成"
        
        # 计算平均氢键数量
        local avg_hbond_intra=$(tail -n +25 "$OUTPUT_DIR/hbond_intra.xvg" | awk '{sum+=$2; count++} END {print sum/count}')
        local avg_hbond_water=$(tail -n +25 "$OUTPUT_DIR/hbond_water.xvg" | awk '{sum+=$2; count++} END {print sum/count}')
        
        log_info "蛋白质内部平均氢键数: ${avg_hbond_intra}"
        log_info "蛋白质-水平均氢键数: ${avg_hbond_water}"
    else
        log_error "氢键分析失败"
    fi
    
    local runtime=$(calculate_runtime $step_start)
    log_success "氢键分析耗时: $runtime"
}

# 分析4: 回转半径分析
analyze_radius_of_gyration() {
    log_step "回转半径分析 - 评估蛋白质紧密程度"
    local step_start=$(date +%s)
    
    check_file "$TRAJECTORY_FILE"
    check_file "$TPR_FILE"
    
    local time_params=$(build_time_params)
    
    # 计算回转半径
    log_info "计算回转半径..."
    echo "$PROTEIN_GROUP" | gmx gyrate \
        -s "$TPR_FILE" \
        -f "$TRAJECTORY_FILE" \
        -o "$OUTPUT_DIR/gyrate.xvg" \
        -tu ns \
        $time_params \
        -quiet
    
    if [[ -f "$OUTPUT_DIR/gyrate.xvg" ]]; then
        log_success "回转半径分析完成"
        
        # 计算平均回转半径
        local avg_gyrate=$(tail -n +25 "$OUTPUT_DIR/gyrate.xvg" | awk '{sum+=$2; count++} END {print sum/count}')
        log_info "平均回转半径: ${avg_gyrate} nm"
    else
        log_error "回转半径分析失败"
    fi
    
    local runtime=$(calculate_runtime $step_start)
    log_success "回转半径分析耗时: $runtime"
}

# 分析5: 溶剂可及表面积分析
analyze_sasa() {
    log_step "溶剂可及表面积分析 - 评估蛋白质表面暴露"
    local step_start=$(date +%s)
    
    check_file "$TRAJECTORY_FILE"
    check_file "$TPR_FILE"
    
    local time_params=$(build_time_params)
    
    # 计算SASA
    log_info "计算溶剂可及表面积..."
    echo "$PROTEIN_GROUP" | gmx sasa \
        -s "$TPR_FILE" \
        -f "$TRAJECTORY_FILE" \
        -o "$OUTPUT_DIR/sasa.xvg" \
        -or "$OUTPUT_DIR/sasa_residue.xvg" \
        -tu ns \
        $time_params \
        -quiet
    
    if [[ -f "$OUTPUT_DIR/sasa.xvg" ]]; then
        log_success "SASA分析完成"
        
        # 计算平均SASA
        local avg_sasa=$(tail -n +25 "$OUTPUT_DIR/sasa.xvg" | awk '{sum+=$2; count++} END {print sum/count}')
        log_info "平均SASA: ${avg_sasa} nm²"
    else
        log_error "SASA分析失败"
    fi
    
    local runtime=$(calculate_runtime $step_start)
    log_success "SASA分析耗时: $runtime"
}

# 分析6: 二级结构分析
analyze_secondary_structure() {
    log_step "二级结构分析 - 评估结构变化"
    local step_start=$(date +%s)
    
    check_file "$TRAJECTORY_FILE"
    check_file "$TPR_FILE"
    
    local time_params=$(build_time_params)
    
    # 计算二级结构
    log_info "计算二级结构..."
    echo "$PROTEIN_GROUP" | gmx do_dssp \
        -s "$TPR_FILE" \
        -f "$TRAJECTORY_FILE" \
        -o "$OUTPUT_DIR/dssp.xpm" \
        -sc "$OUTPUT_DIR/dssp_count.xvg" \
        -tu ns \
        $time_params \
        -quiet 2>/dev/null || log_warning "DSSP分析可能需要安装dssp程序"
    
    if [[ -f "$OUTPUT_DIR/dssp_count.xvg" ]]; then
        log_success "二级结构分析完成"
        
        # 计算平均二级结构含量
        local avg_helix=$(tail -n +25 "$OUTPUT_DIR/dssp_count.xvg" | awk '{sum+=$2; count++} END {print sum/count}')
        local avg_sheet=$(tail -n +25 "$OUTPUT_DIR/dssp_count.xvg" | awk '{sum+=$3; count++} END {print sum/count}')
        
        log_info "平均α螺旋含量: ${avg_helix}%"
        log_info "平均β折叠含量: ${avg_sheet}%"
    else
        log_warning "二级结构分析未完成，可能需要安装DSSP"
    fi
    
    local runtime=$(calculate_runtime $step_start)
    log_success "二级结构分析耗时: $runtime"
}

# 分析7: 能量分析
analyze_energy() {
    log_step "能量分析 - 评估系统能量变化"
    local step_start=$(date +%s)
    
    check_file "md.edr"
    
    # 分析各种能量项
    local energy_terms=("Potential" "Kinetic" "Total-Energy" "Temperature" "Pressure" "Density")
    
    for term in "${energy_terms[@]}"; do
        log_info "分析 $term..."
        echo "$term" | gmx energy \
            -f md.edr \
            -o "$OUTPUT_DIR/energy_${term,,}.xvg" \
            -quiet 2>/dev/null || log_warning "$term 分析失败"
    done
    
    log_success "能量分析完成"
    
    local runtime=$(calculate_runtime $step_start)
    log_success "能量分析耗时: $runtime"
}

# 生成分析报告
generate_analysis_report() {
    log_step "生成分析报告"
    
    local report_file="${OUTPUT_DIR}/${SYSTEM_NAME}_analysis_report.txt"
    
    cat > "$report_file" << EOF
================================================================================
                    分子动力学轨迹分析报告
================================================================================

系统名称: $SYSTEM_NAME
分析时间: $(date)
轨迹文件: $TRAJECTORY_FILE

分析参数:
  - 起始时间: $START_TIME ps
  - 结束时间: $END_TIME ps
  - 时间步长: $TIME_STEP ps

分析结果:
================================================================================

1. RMSD分析 (结构稳定性):
EOF

    # 添加RMSD结果
    if [[ -f "$OUTPUT_DIR/rmsd_backbone.xvg" ]]; then
        local avg_rmsd_backbone=$(tail -n +25 "$OUTPUT_DIR/rmsd_backbone.xvg" | awk '{sum+=$2; count++} END {print sum/count}')
        local avg_rmsd_protein=$(tail -n +25 "$OUTPUT_DIR/rmsd_protein.xvg" | awk '{sum+=$2; count++} END {print sum/count}')
        cat >> "$report_file" << EOF
   - 主链平均RMSD: ${avg_rmsd_backbone} nm
   - 蛋白质平均RMSD: ${avg_rmsd_protein} nm
   - 数据文件: rmsd_backbone.xvg, rmsd_protein.xvg
EOF
    fi
    
    cat >> "$report_file" << EOF

2. RMSF分析 (残基柔性):
EOF

    # 添加RMSF结果
    if [[ -f "$OUTPUT_DIR/rmsf_backbone.xvg" ]]; then
        local max_rmsf_residue=$(tail -n +25 "$OUTPUT_DIR/rmsf_backbone.xvg" | awk 'BEGIN{max=0; res=0} {if($2>max){max=$2; res=$1}} END{print res}')
        local max_rmsf_value=$(tail -n +25 "$OUTPUT_DIR/rmsf_backbone.xvg" | awk 'BEGIN{max=0} {if($2>max){max=$2}} END{print max}')
        cat >> "$report_file" << EOF
   - 最柔性残基: ${max_rmsf_residue} (RMSF = ${max_rmsf_value} nm)
   - 数据文件: rmsf_backbone.xvg, rmsf_protein.xvg
EOF
    fi
    
    cat >> "$report_file" << EOF

3. 氢键分析 (分子间相互作用):
EOF

    # 添加氢键结果
    if [[ -f "$OUTPUT_DIR/hbond_intra.xvg" ]]; then
        local avg_hbond_intra=$(tail -n +25 "$OUTPUT_DIR/hbond_intra.xvg" | awk '{sum+=$2; count++} END {print sum/count}')
        local avg_hbond_water=$(tail -n +25 "$OUTPUT_DIR/hbond_water.xvg" | awk '{sum+=$2; count++} END {print sum/count}')
        cat >> "$report_file" << EOF
   - 蛋白质内部平均氢键数: ${avg_hbond_intra}
   - 蛋白质-水平均氢键数: ${avg_hbond_water}
   - 数据文件: hbond_intra.xvg, hbond_water.xvg
EOF
    fi
    
    cat >> "$report_file" << EOF

4. 回转半径分析 (蛋白质紧密程度):
EOF

    # 添加回转半径结果
    if [[ -f "$OUTPUT_DIR/gyrate.xvg" ]]; then
        local avg_gyrate=$(tail -n +25 "$OUTPUT_DIR/gyrate.xvg" | awk '{sum+=$2; count++} END {print sum/count}')
        cat >> "$report_file" << EOF
   - 平均回转半径: ${avg_gyrate} nm
   - 数据文件: gyrate.xvg
EOF
    fi
    
    cat >> "$report_file" << EOF

5. 溶剂可及表面积分析:
EOF

    # 添加SASA结果
    if [[ -f "$OUTPUT_DIR/sasa.xvg" ]]; then
        local avg_sasa=$(tail -n +25 "$OUTPUT_DIR/sasa.xvg" | awk '{sum+=$2; count++} END {print sum/count}')
        cat >> "$report_file" << EOF
   - 平均SASA: ${avg_sasa} nm²
   - 数据文件: sasa.xvg, sasa_residue.xvg
EOF
    fi
    
    cat >> "$report_file" << EOF

================================================================================
                              分析完成
================================================================================

输出文件位置: $OUTPUT_DIR/
建议下一步: 运行 plot_results.py 生成可视化图表

可视化命令示例:
  python ../analysis_tools/plot_results.py --rmsd $OUTPUT_DIR/rmsd_backbone.xvg
  python ../analysis_tools/plot_results.py --rmsf $OUTPUT_DIR/rmsf_backbone.xvg
  python ../analysis_tools/plot_results.py --hbond $OUTPUT_DIR/hbond_intra.xvg

EOF

    log_success "分析报告已生成: $report_file"
}

#==============================================================================
# 🚀 主程序
#==============================================================================

# 显示帮助信息
show_help() {
    cat << EOF
🧬 Molecular Simulation Toolkit - 轨迹分析标准作业流程

用法: $0 [选项]

选项:
    -n, --name NAME     系统名称 (默认: $SYSTEM_NAME)
    -f, --traj FILE     轨迹文件 (默认: $TRAJECTORY_FILE)
    -s, --struct FILE   结构文件 (默认: $STRUCTURE_FILE)
    -b, --begin TIME    起始时间 (ps) (默认: $START_TIME)
    -e, --end TIME      结束时间 (ps) (默认: $END_TIME)
    -dt, --timestep DT  时间步长 (ps) (默认: $TIME_STEP)
    -o, --output DIR    输出目录 (默认: $OUTPUT_DIR)
    -h, --help          显示帮助信息

示例:
    $0                              # 使用默认参数
    $0 -b 10000 -e 50000           # 分析10-50ns时间段
    $0 -f my_traj.xtc -o my_analysis # 自定义输入输出

分析内容:
    1. RMSD分析 - 结构稳定性
    2. RMSF分析 - 残基柔性
    3. 氢键分析 - 分子间相互作用
    4. 回转半径 - 蛋白质紧密程度
    5. SASA分析 - 表面暴露
    6. 二级结构 - 结构变化
    7. 能量分析 - 系统能量

输出:
    - analysis/                     # 分析结果目录
    - *.xvg                        # GROMACS数据文件
    - ${SYSTEM_NAME}_analysis_report.txt # 分析报告

EOF
}

# 解析命令行参数
parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -n|--name)
                SYSTEM_NAME="$2"
                TOPOLOGY_FILE="${SYSTEM_NAME}.top"
                shift 2
                ;;
            -f|--traj)
                TRAJECTORY_FILE="$2"
                shift 2
                ;;
            -s|--struct)
                STRUCTURE_FILE="$2"
                shift 2
                ;;
            -b|--begin)
                START_TIME="$2"
                shift 2
                ;;
            -e|--end)
                END_TIME="$2"
                shift 2
                ;;
            -dt|--timestep)
                TIME_STEP="$2"
                shift 2
                ;;
            -o|--output)
                OUTPUT_DIR="$2"
                shift 2
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                log_error "未知参数: $1"
                show_help
                exit 1
                ;;
        esac
    done
}

# 主函数
main() {
    # 解析命令行参数
    parse_arguments "$@"
    
    # 显示开始信息
    echo -e "${PURPLE}================================================================================${NC}"
    echo -e "${PURPLE}           🧬 Molecular Simulation Toolkit - 轨迹分析 🧬${NC}"
    echo -e "${PURPLE}================================================================================${NC}"
    
    log_info "开始轨迹分析流程"
    log_info "系统名称: $SYSTEM_NAME"
    log_info "轨迹文件: $TRAJECTORY_FILE"
    log_info "结构文件: $STRUCTURE_FILE"
    log_info "分析时间范围: $START_TIME - $END_TIME ps"
    log_info "输出目录: $OUTPUT_DIR"
    
    # 检查GROMACS
    check_gromacs
    
    # 创建输出目录
    create_directory "$OUTPUT_DIR"
    
    # 执行主要分析流程
    local pipeline_start=$(date +%s)
    
    analyze_rmsd
    analyze_rmsf
    analyze_hydrogen_bonds
    analyze_radius_of_gyration
    analyze_sasa
    analyze_secondary_structure
    analyze_energy
    generate_analysis_report
    
    # 计算总耗时
    local total_runtime=$(calculate_runtime $pipeline_start)
    
    log_success "🎉 轨迹分析完成！总耗时: $total_runtime"
    log_info "下一步: 运行 plot_results.py 生成可视化图表"
    
    # 显示结果概览
    echo ""
    echo -e "${GREEN}================================================================================${NC}"
    echo -e "${GREEN}                           🧬 分析完成概览 🧬${NC}"
    echo -e "${GREEN}================================================================================${NC}"
    echo -e "${CYAN}📁 分析目录: ${NC}$OUTPUT_DIR/"
    echo -e "${CYAN}📊 分析报告: ${NC}${OUTPUT_DIR}/${SYSTEM_NAME}_analysis_report.txt"
    echo -e "${CYAN}📈 数据文件: ${NC}*.xvg"
    echo -e "${CYAN}⏱️  总耗时: ${NC}$total_runtime"
    echo -e "${GREEN}================================================================================${NC}"
    echo ""
    
    # 提示可视化命令
    echo -e "${YELLOW}💡 可视化建议:${NC}"
    echo -e "${CYAN}   python ../analysis_tools/plot_results.py --rmsd $OUTPUT_DIR/rmsd_backbone.xvg${NC}"
    echo -e "${CYAN}   python ../analysis_tools/plot_results.py --rmsf $OUTPUT_DIR/rmsf_backbone.xvg${NC}"
    echo -e "${CYAN}   python ../analysis_tools/plot_results.py --hbond $OUTPUT_DIR/hbond_intra.xvg${NC}"
    echo ""
}

# 错误处理
trap 'log_error "脚本执行过程中发生错误"; exit 1' ERR

# 执行主函数
main "$@"