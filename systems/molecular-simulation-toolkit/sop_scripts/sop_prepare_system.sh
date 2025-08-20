#!/bin/bash

#==============================================================================
# Molecular Simulation Toolkit - 系统搭建标准作业流程
# 
# 功能: 从PDB文件自动搭建完整的分子动力学模拟系统
# 作者: Research Workstation Team
# 版本: 1.0.0
# 日期: 2025-08-20
#==============================================================================

set -euo pipefail  # 严格模式

#==============================================================================
# 🔧 用户配置参数 - 根据您的研究体系修改这些参数
#==============================================================================

# 输入文件配置
INPUT_PDB="protein.pdb"                    # 输入的PDB文件名
SYSTEM_NAME="system"                       # 系统名称（用于输出文件命名）

# 力场和水模型配置
FORCE_FIELD="amber99sb-ildn"               # 力场选择
WATER_MODEL="tip3p"                        # 水模型
FORCE_FIELD_NUM="1"                        # pdb2gmx中力场对应的数字（amber99sb-ildn通常是1）
WATER_MODEL_NUM="1"                        # pdb2gmx中水模型对应的数字（tip3p通常是1）

# 盒子和溶剂化配置
BOX_TYPE="cubic"                           # 盒子类型: cubic, dodecahedron, octahedron
BOX_SIZE="1.0"                             # 蛋白质到盒子边界的最小距离 (nm)
SOLVENT_NAME="SOL"                         # 溶剂分子名称

# 离子化配置
SALT_CONCENTRATION="0.15"                  # 盐浓度 (M)
POSITIVE_ION="NA"                          # 正离子类型
NEGATIVE_ION="CL"                          # 负离子类型

# 计算资源配置
NPROC="8"                                  # 使用的处理器核心数

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

# 备份文件
backup_file() {
    if [[ -f "$1" ]]; then
        cp "$1" "${1}.backup.$(date +%Y%m%d_%H%M%S)"
        log_info "备份文件: $1"
    fi
}

#==============================================================================
# 🧬 主要处理函数
#==============================================================================

# 步骤1: 蛋白质拓扑生成
generate_topology() {
    log_step "生成蛋白质拓扑结构"
    
    check_file "$INPUT_PDB"
    
    # 使用pdb2gmx生成拓扑
    log_info "运行 pdb2gmx..."
    echo -e "${FORCE_FIELD_NUM}\n${WATER_MODEL_NUM}" | gmx pdb2gmx \
        -f "$INPUT_PDB" \
        -o "${SYSTEM_NAME}_processed.gro" \
        -p "${SYSTEM_NAME}.top" \
        -i "${SYSTEM_NAME}_posre.itp" \
        -water "$WATER_MODEL" \
        -ff "$FORCE_FIELD" \
        -ignh
    
    if [[ -f "${SYSTEM_NAME}_processed.gro" ]]; then
        log_success "蛋白质拓扑生成完成"
        log_info "输出文件:"
        log_info "  - 结构文件: ${SYSTEM_NAME}_processed.gro"
        log_info "  - 拓扑文件: ${SYSTEM_NAME}.top"
        log_info "  - 位置限制: ${SYSTEM_NAME}_posre.itp"
    else
        log_error "蛋白质拓扑生成失败"
        exit 1
    fi
}

# 步骤2: 定义模拟盒子
define_box() {
    log_step "定义模拟盒子"
    
    check_file "${SYSTEM_NAME}_processed.gro"
    
    # 使用editconf定义盒子
    log_info "运行 editconf..."
    gmx editconf \
        -f "${SYSTEM_NAME}_processed.gro" \
        -o "${SYSTEM_NAME}_newbox.gro" \
        -c \
        -d "$BOX_SIZE" \
        -bt "$BOX_TYPE"
    
    if [[ -f "${SYSTEM_NAME}_newbox.gro" ]]; then
        log_success "模拟盒子定义完成"
        
        # 显示盒子信息
        local box_info=$(tail -1 "${SYSTEM_NAME}_newbox.gro")
        log_info "盒子尺寸: $box_info"
    else
        log_error "模拟盒子定义失败"
        exit 1
    fi
}

# 步骤3: 添加溶剂
add_solvent() {
    log_step "添加溶剂分子"
    
    check_file "${SYSTEM_NAME}_newbox.gro"
    check_file "${SYSTEM_NAME}.top"
    
    # 使用solvate添加水分子
    log_info "运行 solvate..."
    gmx solvate \
        -cp "${SYSTEM_NAME}_newbox.gro" \
        -cs spc216.gro \
        -o "${SYSTEM_NAME}_solv.gro" \
        -p "${SYSTEM_NAME}.top"
    
    if [[ -f "${SYSTEM_NAME}_solv.gro" ]]; then
        log_success "溶剂添加完成"
        
        # 统计水分子数量
        local water_count=$(grep -c "$SOLVENT_NAME" "${SYSTEM_NAME}_solv.gro" || echo "0")
        log_info "添加的水分子数量: $water_count"
    else
        log_error "溶剂添加失败"
        exit 1
    fi
}

# 步骤4: 添加离子
add_ions() {
    log_step "添加离子以中和系统"
    
    check_file "${SYSTEM_NAME}_solv.gro"
    check_file "${SYSTEM_NAME}.top"
    
    # 创建离子化所需的MDP文件
    create_ions_mdp
    
    # 使用grompp准备离子化
    log_info "准备离子化 (grompp)..."
    gmx grompp \
        -f ions.mdp \
        -c "${SYSTEM_NAME}_solv.gro" \
        -p "${SYSTEM_NAME}.top" \
        -o ions.tpr \
        -maxwarn 1
    
    # 使用genion添加离子
    log_info "运行 genion..."
    echo "SOL" | gmx genion \
        -s ions.tpr \
        -o "${SYSTEM_NAME}_solv_ions.gro" \
        -p "${SYSTEM_NAME}.top" \
        -pname "$POSITIVE_ION" \
        -nname "$NEGATIVE_ION" \
        -neutral \
        -conc "$SALT_CONCENTRATION"
    
    if [[ -f "${SYSTEM_NAME}_solv_ions.gro" ]]; then
        log_success "离子添加完成"
        
        # 统计离子数量
        local na_count=$(grep -c "$POSITIVE_ION" "${SYSTEM_NAME}_solv_ions.gro" || echo "0")
        local cl_count=$(grep -c "$NEGATIVE_ION" "${SYSTEM_NAME}_solv_ions.gro" || echo "0")
        log_info "添加的离子: ${POSITIVE_ION}+ = $na_count, ${NEGATIVE_ION}- = $cl_count"
    else
        log_error "离子添加失败"
        exit 1
    fi
}

# 创建离子化MDP文件
create_ions_mdp() {
    log_info "创建离子化MDP文件..."
    
    cat > ions.mdp << 'EOF'
; ions.mdp - used as input into grompp to generate ions.tpr
; Parameters describing what to do, when to stop and what to save
integrator  = steep         ; Algorithm (steep = steepest descent minimization)
emtol       = 1000.0        ; Stop minimization when the maximum force < 1000.0 kJ/mol/nm
emstep      = 0.01          ; Minimization step size
nsteps      = 50000         ; Maximum number of (minimization) steps to perform

; Parameters describing how to find the neighbors of each atom and how to calculate the interactions
nstlist         = 1         ; Frequency to update the neighbor list and long range forces
cutoff-scheme   = Verlet    ; Buffered neighbor searching
ns_type         = grid      ; Method to determine neighbor list (simple, grid)
coulombtype     = PME       ; Treatment of long range electrostatic interactions
rcoulomb        = 1.0       ; Short-range electrostatic cut-off
rvdw            = 1.0       ; Short-range Van der Waals cut-off
pbc             = xyz       ; Periodic Boundary Conditions in all 3 dimensions
EOF

    log_success "离子化MDP文件创建完成"
}

# 系统信息统计
system_statistics() {
    log_step "生成系统统计信息"
    
    local final_gro="${SYSTEM_NAME}_solv_ions.gro"
    check_file "$final_gro"
    
    # 创建统计报告
    local stats_file="${SYSTEM_NAME}_system_stats.txt"
    
    cat > "$stats_file" << EOF
================================================================================
                    分子动力学模拟系统统计报告
================================================================================

系统名称: $SYSTEM_NAME
创建时间: $(date)
输入PDB文件: $INPUT_PDB

力场参数:
  - 力场: $FORCE_FIELD
  - 水模型: $WATER_MODEL

盒子参数:
  - 盒子类型: $BOX_TYPE
  - 边界距离: $BOX_SIZE nm
  - 盒子尺寸: $(tail -1 "$final_gro")

溶剂化参数:
  - 盐浓度: $SALT_CONCENTRATION M
  - 正离子: $POSITIVE_ION
  - 负离子: $NEGATIVE_ION

系统组成:
EOF

    # 统计各种分子数量
    if [[ -f "$final_gro" ]]; then
        local total_atoms=$(head -2 "$final_gro" | tail -1 | awk '{print $1}')
        local protein_atoms=$(grep -v "$SOLVENT_NAME\|$POSITIVE_ION\|$NEGATIVE_ION" "$final_gro" | grep -v "^[[:space:]]*[0-9]" | wc -l || echo "0")
        local water_molecules=$(grep -c "$SOLVENT_NAME" "$final_gro" || echo "0")
        local na_ions=$(grep -c "$POSITIVE_ION" "$final_gro" || echo "0")
        local cl_ions=$(grep -c "$NEGATIVE_ION" "$final_gro" || echo "0")
        
        cat >> "$stats_file" << EOF
  - 总原子数: $total_atoms
  - 蛋白质原子数: $protein_atoms
  - 水分子数: $water_molecules
  - ${POSITIVE_ION}+ 离子数: $na_ions
  - ${NEGATIVE_ION}- 离子数: $cl_ions

输出文件:
  - 最终结构: $final_gro
  - 拓扑文件: ${SYSTEM_NAME}.top
  - 位置限制: ${SYSTEM_NAME}_posre.itp

================================================================================
                              系统搭建完成
================================================================================

下一步: 运行 sop_run_simulation.sh 开始分子动力学模拟

EOF
    fi
    
    log_success "系统统计报告已生成: $stats_file"
    
    # 显示关键信息
    echo ""
    echo -e "${GREEN}================================================================================${NC}"
    echo -e "${GREEN}                           🧬 系统搭建完成 🧬${NC}"
    echo -e "${GREEN}================================================================================${NC}"
    echo -e "${CYAN}📁 最终结构文件: ${NC}${SYSTEM_NAME}_solv_ions.gro"
    echo -e "${CYAN}📋 拓扑文件: ${NC}${SYSTEM_NAME}.top"
    echo -e "${CYAN}📊 统计报告: ${NC}$stats_file"
    echo -e "${GREEN}================================================================================${NC}"
    echo ""
}

#==============================================================================
# 🚀 主程序
#==============================================================================

# 显示帮助信息
show_help() {
    cat << EOF
🧬 Molecular Simulation Toolkit - 系统搭建标准作业流程

用法: $0 [选项]

选项:
    -i, --input FILE    输入PDB文件 (默认: $INPUT_PDB)
    -n, --name NAME     系统名称 (默认: $SYSTEM_NAME)
    -f, --forcefield FF 力场 (默认: $FORCE_FIELD)
    -w, --water MODEL   水模型 (默认: $WATER_MODEL)
    -b, --box SIZE      盒子大小 (默认: $BOX_SIZE nm)
    -c, --conc CONC     盐浓度 (默认: $SALT_CONCENTRATION M)
    -p, --nproc NUM     处理器核心数 (默认: $NPROC)
    -h, --help          显示帮助信息

示例:
    $0                                    # 使用默认参数
    $0 -i my_protein.pdb -n my_system    # 指定输入文件和系统名
    $0 -f amber03 -w tip4p -b 1.5        # 自定义力场和参数

流程:
    1. 蛋白质拓扑生成 (pdb2gmx)
    2. 定义模拟盒子 (editconf)
    3. 添加溶剂分子 (solvate)
    4. 添加离子中和 (genion)
    5. 生成系统统计

输出:
    - ${SYSTEM_NAME}_solv_ions.gro  # 最终系统结构
    - ${SYSTEM_NAME}.top            # 拓扑文件
    - ${SYSTEM_NAME}_system_stats.txt # 统计报告

EOF
}

# 解析命令行参数
parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -i|--input)
                INPUT_PDB="$2"
                shift 2
                ;;
            -n|--name)
                SYSTEM_NAME="$2"
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
            -b|--box)
                BOX_SIZE="$2"
                shift 2
                ;;
            -c|--conc)
                SALT_CONCENTRATION="$2"
                shift 2
                ;;
            -p|--nproc)
                NPROC="$2"
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
    echo -e "${PURPLE}           🧬 Molecular Simulation Toolkit - 系统搭建 🧬${NC}"
    echo -e "${PURPLE}================================================================================${NC}"
    
    log_info "开始系统搭建流程"
    log_info "输入PDB文件: $INPUT_PDB"
    log_info "系统名称: $SYSTEM_NAME"
    log_info "力场: $FORCE_FIELD"
    log_info "水模型: $WATER_MODEL"
    log_info "盒子大小: $BOX_SIZE nm"
    log_info "盐浓度: $SALT_CONCENTRATION M"
    
    # 检查GROMACS
    check_gromacs
    
    # 执行主要流程
    local start_time=$(date +%s)
    
    generate_topology
    define_box
    add_solvent
    add_ions
    system_statistics
    
    # 计算总耗时
    local end_time=$(date +%s)
    local runtime=$((end_time - start_time))
    local minutes=$((runtime / 60))
    local seconds=$((runtime % 60))
    
    log_success "🎉 系统搭建完成！总耗时: ${minutes}分${seconds}秒"
    log_info "下一步: 运行 sop_run_simulation.sh 开始模拟"
}

# 错误处理
trap 'log_error "脚本执行过程中发生错误"; exit 1' ERR

# 执行主函数
main "$@"