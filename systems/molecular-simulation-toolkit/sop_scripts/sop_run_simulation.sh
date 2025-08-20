#!/bin/bash

#==============================================================================
# Molecular Simulation Toolkit - 模拟执行标准作业流程
# 
# 功能: 自动执行完整的分子动力学模拟流程
# 作者: Research Workstation Team
# 版本: 1.0.0
# 日期: 2025-08-20
#==============================================================================

set -euo pipefail  # 严格模式

#==============================================================================
# 🔧 用户配置参数 - 根据您的研究需求修改这些参数
#==============================================================================

# 系统文件配置
SYSTEM_NAME="system"                       # 系统名称（与prepare_system.sh保持一致）
INPUT_GRO="${SYSTEM_NAME}_solv_ions.gro"   # 输入结构文件
INPUT_TOP="${SYSTEM_NAME}.top"             # 输入拓扑文件

# 模拟时间配置
SIMULATION_TIME_NS="100"                   # 成品模拟时长 (纳秒)
EM_STEPS="50000"                          # 能量最小化步数
NVT_TIME_PS="100"                         # NVT平衡时间 (皮秒)
NPT_TIME_PS="100"                         # NPT平衡时间 (皮秒)

# 温度和压力配置
TEMPERATURE="300"                          # 模拟温度 (K)
PRESSURE="1.0"                            # 模拟压力 (bar)
TAU_T="0.1"                               # 温度耦合时间常数 (ps)
TAU_P="2.0"                               # 压力耦合时间常数 (ps)

# 计算资源配置
NPROC="8"                                 # 使用的处理器核心数
GPU_ID=""                                 # GPU ID (留空则使用CPU)

# 输出配置
OUTPUT_FREQ="5000"                        # 轨迹输出频率 (步)
ENERGY_FREQ="1000"                        # 能量输出频率 (步)
LOG_FREQ="1000"                           # 日志输出频率 (步)

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
    local hours=$((runtime / 3600))
    local minutes=$(((runtime % 3600) / 60))
    local seconds=$((runtime % 60))
    printf "%02d:%02d:%02d" $hours $minutes $seconds
}

# 构建mdrun命令
build_mdrun_command() {
    local tpr_file=$1
    local output_prefix=$2
    
    local cmd="gmx mdrun -deffnm $output_prefix"
    
    if [[ -n "$GPU_ID" ]]; then
        cmd="$cmd -gpu_id $GPU_ID"
        log_info "使用GPU: $GPU_ID"
    fi
    
    if [[ "$NPROC" -gt 1 ]]; then
        cmd="$cmd -nt $NPROC"
        log_info "使用CPU核心数: $NPROC"
    fi
    
    echo "$cmd"
}

#==============================================================================
# 🧬 MDP文件生成函数
#==============================================================================

# 创建能量最小化MDP文件
create_em_mdp() {
    log_info "创建能量最小化MDP文件..."
    
    cat > em.mdp << EOF
; em.mdp - Energy Minimization
; Parameters describing what to do, when to stop and what to save
integrator  = steep         ; Algorithm (steep = steepest descent minimization)
emtol       = 1000.0        ; Stop minimization when the maximum force < 1000.0 kJ/mol/nm
emstep      = 0.01          ; Minimization step size
nsteps      = $EM_STEPS     ; Maximum number of (minimization) steps to perform

; Parameters describing how to find the neighbors of each atom and how to calculate the interactions
nstlist         = 1         ; Frequency to update the neighbor list and long range forces
cutoff-scheme   = Verlet    ; Buffered neighbor searching
ns_type         = grid      ; Method to determine neighbor list (simple, grid)
coulombtype     = PME       ; Treatment of long range electrostatic interactions
rcoulomb        = 1.0       ; Short-range electrostatic cut-off
rvdw            = 1.0       ; Short-range Van der Waals cut-off
pbc             = xyz       ; Periodic Boundary Conditions in all 3 dimensions
EOF

    log_success "能量最小化MDP文件创建完成"
}

# 创建NVT平衡MDP文件
create_nvt_mdp() {
    log_info "创建NVT平衡MDP文件..."
    
    cat > nvt.mdp << EOF
; nvt.mdp - NVT Equilibration
title                   = NVT equilibration 
define                  = -DPOSRES  ; position restrain the protein
; Run parameters
integrator              = md        ; leap-frog integrator
nsteps                  = $(echo "$NVT_TIME_PS * 1000 / 2" | bc)  ; 2 fs * nsteps = NVT_TIME_PS ps
dt                      = 0.002     ; 2 fs
; Output control
nstxout                 = $OUTPUT_FREQ      ; save coordinates every OUTPUT_FREQ steps
nstvout                 = $OUTPUT_FREQ      ; save velocities every OUTPUT_FREQ steps
nstenergy               = $ENERGY_FREQ      ; save energies every ENERGY_FREQ steps
nstlog                  = $LOG_FREQ         ; update log file every LOG_FREQ steps
; Bond parameters
continuation            = no        ; first dynamics run
constraint_algorithm    = lincs     ; holonomic constraints 
constraints             = h-bonds   ; bonds involving H are constrained
lincs_iter              = 1         ; accuracy of LINCS
lincs_order             = 4         ; also related to accuracy
; Nonbonded settings 
cutoff-scheme           = Verlet    ; Buffered neighbor searching
ns_type                 = grid      ; search neighboring grid cells
nstlist                 = 10        ; 20 fs, largely irrelevant with Verlet
rcoulomb                = 1.0       ; short-range electrostatic cutoff (in nm)
rvdw                    = 1.0       ; short-range van der Waals cutoff (in nm)
DispCorr                = EnerPres  ; account for cut-off vdW scheme
; Electrostatics
coulombtype             = PME       ; Particle Mesh Ewald for long-range electrostatics
pme_order               = 4         ; cubic interpolation
fourierspacing          = 0.16      ; grid spacing for FFT
; Temperature coupling is on
tcoupl                  = V-rescale     ; modified Berendsen thermostat
tc-grps                 = Protein Non-Protein   ; two coupling groups - more accurate
tau_t                   = $TAU_T $TAU_T         ; time constant, in ps
ref_t                   = $TEMPERATURE $TEMPERATURE ; reference temperature, one for each group, in K
; Pressure coupling is off
pcoupl                  = no        ; no pressure coupling in NVT
; Periodic boundary conditions
pbc                     = xyz       ; 3-D PBC
; Velocity generation
gen_vel                 = yes       ; assign velocities from Maxwell distribution
gen_temp                = $TEMPERATURE ; temperature for Maxwell distribution
gen_seed                = -1        ; generate a random seed
EOF

    log_success "NVT平衡MDP文件创建完成"
}

# 创建NPT平衡MDP文件
create_npt_mdp() {
    log_info "创建NPT平衡MDP文件..."
    
    cat > npt.mdp << EOF
; npt.mdp - NPT Equilibration
title                   = NPT equilibration 
define                  = -DPOSRES  ; position restrain the protein
; Run parameters
integrator              = md        ; leap-frog integrator
nsteps                  = $(echo "$NPT_TIME_PS * 1000 / 2" | bc)  ; 2 fs * nsteps = NPT_TIME_PS ps
dt                      = 0.002     ; 2 fs
; Output control
nstxout                 = $OUTPUT_FREQ      ; save coordinates every OUTPUT_FREQ steps
nstvout                 = $OUTPUT_FREQ      ; save velocities every OUTPUT_FREQ steps
nstenergy               = $ENERGY_FREQ      ; save energies every ENERGY_FREQ steps
nstlog                  = $LOG_FREQ         ; update log file every LOG_FREQ steps
; Bond parameters
continuation            = yes       ; continuing from NVT 
constraint_algorithm    = lincs     ; holonomic constraints 
constraints             = h-bonds   ; bonds involving H are constrained
lincs_iter              = 1         ; accuracy of LINCS
lincs_order             = 4         ; also related to accuracy
; Nonbonded settings 
cutoff-scheme           = Verlet    ; Buffered neighbor searching
ns_type                 = grid      ; search neighboring grid cells
nstlist                 = 10        ; 20 fs, largely irrelevant with Verlet scheme
rcoulomb                = 1.0       ; short-range electrostatic cutoff (in nm)
rvdw                    = 1.0       ; short-range van der Waals cutoff (in nm)
DispCorr                = EnerPres  ; account for cut-off vdW scheme
; Electrostatics
coulombtype             = PME       ; Particle Mesh Ewald for long-range electrostatics
pme_order               = 4         ; cubic interpolation
fourierspacing          = 0.16      ; grid spacing for FFT
; Temperature coupling is on
tcoupl                  = V-rescale     ; modified Berendsen thermostat
tc-grps                 = Protein Non-Protein   ; two coupling groups - more accurate
tau_t                   = $TAU_T $TAU_T         ; time constant, in ps
ref_t                   = $TEMPERATURE $TEMPERATURE ; reference temperature, one for each group, in K
; Pressure coupling is on
pcoupl                  = Parrinello-Rahman     ; Pressure coupling on in NPT
pcoupltype              = isotropic             ; uniform scaling of box vectors
tau_p                   = $TAU_P                ; time constant, in ps
ref_p                   = $PRESSURE             ; reference pressure, in bar
compressibility         = 4.5e-5               ; isothermal compressibility of water, bar^-1
; Periodic boundary conditions
pbc                     = xyz       ; 3-D PBC
; Velocity generation
gen_vel                 = no        ; velocity generation off after NVT 
EOF

    log_success "NPT平衡MDP文件创建完成"
}

# 创建成品模拟MDP文件
create_md_mdp() {
    log_info "创建成品模拟MDP文件..."
    
    local md_steps=$(echo "$SIMULATION_TIME_NS * 1000000 / 2" | bc)
    
    cat > md.mdp << EOF
; md.mdp - Production MD
title                   = Production MD simulation 
; Run parameters
integrator              = md        ; leap-frog integrator
nsteps                  = $md_steps ; 2 fs * nsteps = $SIMULATION_TIME_NS ns
dt                      = 0.002     ; 2 fs
; Output control
nstxout                 = 0         ; suppress bulky .trr file by setting nstxout=0
nstvout                 = 0         ; suppress bulky .trr file by setting nstvout=0
nstfout                 = 0         ; suppress bulky .trr file by setting nstfout=0
nstenergy               = $ENERGY_FREQ      ; save energies every ENERGY_FREQ steps
nstlog                  = $LOG_FREQ         ; update log file every LOG_FREQ steps
nstxout-compressed      = $OUTPUT_FREQ      ; save compressed coordinates every OUTPUT_FREQ steps
compressed-x-grps       = System           ; save the whole system
; Bond parameters
continuation            = yes       ; continuing from NPT 
constraint_algorithm    = lincs     ; holonomic constraints 
constraints             = h-bonds   ; bonds involving H are constrained
lincs_iter              = 1         ; accuracy of LINCS
lincs_order             = 4         ; also related to accuracy
; Nonbonded settings 
cutoff-scheme           = Verlet    ; Buffered neighbor searching
ns_type                 = grid      ; search neighboring grid cells
nstlist                 = 10        ; 20 fs, largely irrelevant with Verlet scheme
rcoulomb                = 1.0       ; short-range electrostatic cutoff (in nm)
rvdw                    = 1.0       ; short-range van der Waals cutoff (in nm)
DispCorr                = EnerPres  ; account for cut-off vdW scheme
; Electrostatics
coulombtype             = PME       ; Particle Mesh Ewald for long-range electrostatics
pme_order               = 4         ; cubic interpolation
fourierspacing          = 0.16      ; grid spacing for FFT
; Temperature coupling is on
tcoupl                  = V-rescale     ; modified Berendsen thermostat
tc-grps                 = Protein Non-Protein   ; two coupling groups - more accurate
tau_t                   = $TAU_T $TAU_T         ; time constant, in ps
ref_t                   = $TEMPERATURE $TEMPERATURE ; reference temperature, one for each group, in K
; Pressure coupling is on
pcoupl                  = Parrinello-Rahman     ; Pressure coupling on in NPT
pcoupltype              = isotropic             ; uniform scaling of box vectors
tau_p                   = $TAU_P                ; time constant, in ps
ref_p                   = $PRESSURE             ; reference pressure, in bar
compressibility         = 4.5e-5               ; isothermal compressibility of water, bar^-1
; Periodic boundary conditions
pbc                     = xyz       ; 3-D PBC
; Velocity generation
gen_vel                 = no        ; velocity generation off after equilibration
EOF

    log_success "成品模拟MDP文件创建完成"
}

#==============================================================================
# 🧬 主要模拟函数
#==============================================================================

# 步骤1: 能量最小化
run_energy_minimization() {
    log_step "开始能量最小化"
    local step_start=$(date +%s)
    
    check_file "$INPUT_GRO"
    check_file "$INPUT_TOP"
    
    # 创建MDP文件
    create_em_mdp
    
    # 运行grompp
    log_info "准备能量最小化 (grompp)..."
    gmx grompp -f em.mdp -c "$INPUT_GRO" -p "$INPUT_TOP" -o em.tpr -maxwarn 1
    
    # 运行mdrun
    log_info "执行能量最小化 (mdrun)..."
    local mdrun_cmd=$(build_mdrun_command "em.tpr" "em")
    eval $mdrun_cmd
    
    if [[ -f "em.gro" ]]; then
        log_success "能量最小化完成"
        
        # 检查最终能量
        local final_energy=$(tail -1 em.log | awk '{print $2}')
        log_info "最终势能: $final_energy kJ/mol"
    else
        log_error "能量最小化失败"
        exit 1
    fi
    
    local runtime=$(calculate_runtime $step_start)
    log_success "能量最小化耗时: $runtime"
}

# 步骤2: NVT平衡
run_nvt_equilibration() {
    log_step "开始NVT平衡"
    local step_start=$(date +%s)
    
    check_file "em.gro"
    
    # 创建MDP文件
    create_nvt_mdp
    
    # 运行grompp
    log_info "准备NVT平衡 (grompp)..."
    gmx grompp -f nvt.mdp -c em.gro -r em.gro -p "$INPUT_TOP" -o nvt.tpr -maxwarn 1
    
    # 运行mdrun
    log_info "执行NVT平衡 (mdrun)..."
    local mdrun_cmd=$(build_mdrun_command "nvt.tpr" "nvt")
    eval $mdrun_cmd
    
    if [[ -f "nvt.gro" ]]; then
        log_success "NVT平衡完成"
        
        # 检查温度稳定性
        log_info "检查温度稳定性..."
        echo "Temperature" | gmx energy -f nvt.edr -o temperature.xvg -quiet
        local avg_temp=$(tail -n +25 temperature.xvg | awk '{sum+=$2; count++} END {print sum/count}')
        log_info "平均温度: ${avg_temp} K (目标: ${TEMPERATURE} K)"
    else
        log_error "NVT平衡失败"
        exit 1
    fi
    
    local runtime=$(calculate_runtime $step_start)
    log_success "NVT平衡耗时: $runtime"
}

# 步骤3: NPT平衡
run_npt_equilibration() {
    log_step "开始NPT平衡"
    local step_start=$(date +%s)
    
    check_file "nvt.gro"
    
    # 创建MDP文件
    create_npt_mdp
    
    # 运行grompp
    log_info "准备NPT平衡 (grompp)..."
    gmx grompp -f npt.mdp -c nvt.gro -r nvt.gro -t nvt.cpt -p "$INPUT_TOP" -o npt.tpr -maxwarn 1
    
    # 运行mdrun
    log_info "执行NPT平衡 (mdrun)..."
    local mdrun_cmd=$(build_mdrun_command "npt.tpr" "npt")
    eval $mdrun_cmd
    
    if [[ -f "npt.gro" ]]; then
        log_success "NPT平衡完成"
        
        # 检查压力和密度稳定性
        log_info "检查压力稳定性..."
        echo "Pressure" | gmx energy -f npt.edr -o pressure.xvg -quiet
        local avg_pressure=$(tail -n +25 pressure.xvg | awk '{sum+=$2; count++} END {print sum/count}')
        log_info "平均压力: ${avg_pressure} bar (目标: ${PRESSURE} bar)"
        
        log_info "检查密度稳定性..."
        echo "Density" | gmx energy -f npt.edr -o density.xvg -quiet
        local avg_density=$(tail -n +25 density.xvg | awk '{sum+=$2; count++} END {print sum/count}')
        log_info "平均密度: ${avg_density} kg/m³"
    else
        log_error "NPT平衡失败"
        exit 1
    fi
    
    local runtime=$(calculate_runtime $step_start)
    log_success "NPT平衡耗时: $runtime"
}

# 步骤4: 成品模拟
run_production_simulation() {
    log_step "开始成品模拟 (${SIMULATION_TIME_NS} ns)"
    local step_start=$(date +%s)
    
    check_file "npt.gro"
    
    # 创建MDP文件
    create_md_mdp
    
    # 运行grompp
    log_info "准备成品模拟 (grompp)..."
    gmx grompp -f md.mdp -c npt.gro -t npt.cpt -p "$INPUT_TOP" -o md.tpr -maxwarn 1
    
    # 运行mdrun
    log_info "执行成品模拟 (mdrun)..."
    log_info "预计运行时间: 根据系统大小和硬件配置而定"
    local mdrun_cmd=$(build_mdrun_command "md.tpr" "md")
    eval $mdrun_cmd
    
    if [[ -f "md.xtc" ]]; then
        log_success "成品模拟完成"
        
        # 检查轨迹文件大小
        local traj_size=$(du -h md.xtc | cut -f1)
        log_info "轨迹文件大小: $traj_size"
        
        # 检查模拟完整性
        local total_frames=$(gmx check -f md.xtc 2>&1 | grep "frames" | awk '{print $3}')
        log_info "轨迹帧数: $total_frames"
    else
        log_error "成品模拟失败"
        exit 1
    fi
    
    local runtime=$(calculate_runtime $step_start)
    log_success "成品模拟耗时: $runtime"
}

# 生成模拟报告
generate_simulation_report() {
    log_step "生成模拟报告"
    
    local report_file="${SYSTEM_NAME}_simulation_report.txt"
    
    cat > "$report_file" << EOF
================================================================================
                    分子动力学模拟执行报告
================================================================================

系统名称: $SYSTEM_NAME
模拟时间: $(date)

模拟参数:
  - 总模拟时长: $SIMULATION_TIME_NS ns
  - 模拟温度: $TEMPERATURE K
  - 模拟压力: $PRESSURE bar
  - 能量最小化步数: $EM_STEPS
  - NVT平衡时间: $NVT_TIME_PS ps
  - NPT平衡时间: $NPT_TIME_PS ps

计算资源:
  - CPU核心数: $NPROC
  - GPU ID: ${GPU_ID:-"未使用"}

输出文件:
  - 最终结构: md.gro
  - 轨迹文件: md.xtc
  - 能量文件: md.edr
  - 日志文件: md.log

平衡检查:
EOF

    # 添加平衡检查结果
    if [[ -f "temperature.xvg" ]]; then
        local avg_temp=$(tail -n +25 temperature.xvg | awk '{sum+=$2; count++} END {print sum/count}')
        echo "  - NVT平均温度: ${avg_temp} K" >> "$report_file"
    fi
    
    if [[ -f "pressure.xvg" ]]; then
        local avg_pressure=$(tail -n +25 pressure.xvg | awk '{sum+=$2; count++} END {print sum/count}')
        echo "  - NPT平均压力: ${avg_pressure} bar" >> "$report_file"
    fi
    
    if [[ -f "density.xvg" ]]; then
        local avg_density=$(tail -n +25 density.xvg | awk '{sum+=$2; count++} END {print sum/count}')
        echo "  - NPT平均密度: ${avg_density} kg/m³" >> "$report_file"
    fi
    
    cat >> "$report_file" << EOF

================================================================================
                              模拟完成
================================================================================

下一步: 运行 sop_analyze_trajectory.sh 进行轨迹分析

建议的分析内容:
  1. RMSD分析 - 评估结构稳定性
  2. RMSF分析 - 评估残基柔性
  3. 氢键分析 - 评估分子间相互作用
  4. 回转半径 - 评估蛋白质紧密程度
  5. 二级结构分析 - 评估结构变化

EOF

    log_success "模拟报告已生成: $report_file"
}

#==============================================================================
# 🚀 主程序
#==============================================================================

# 显示帮助信息
show_help() {
    cat << EOF
🧬 Molecular Simulation Toolkit - 模拟执行标准作业流程

用法: $0 [选项]

选项:
    -n, --name NAME     系统名称 (默认: $SYSTEM_NAME)
    -t, --time TIME     模拟时长 (ns) (默认: $SIMULATION_TIME_NS)
    -T, --temp TEMP     温度 (K) (默认: $TEMPERATURE)
    -P, --press PRESS   压力 (bar) (默认: $PRESSURE)
    -p, --nproc NUM     处理器核心数 (默认: $NPROC)
    -g, --gpu ID        GPU ID (默认: 使用CPU)
    -h, --help          显示帮助信息

示例:
    $0                              # 使用默认参数
    $0 -t 200 -T 310               # 200ns模拟，310K温度
    $0 -p 16 -g 0                   # 16核CPU + GPU 0

流程:
    1. 能量最小化 (EM)
    2. NVT平衡 (恒温)
    3. NPT平衡 (恒温恒压)
    4. 成品模拟 (Production MD)

输出:
    - md.xtc                        # 轨迹文件
    - md.edr                        # 能量文件
    - md.gro                        # 最终结构
    - ${SYSTEM_NAME}_simulation_report.txt # 模拟报告

EOF
}

# 解析命令行参数
parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -n|--name)
                SYSTEM_NAME="$2"
                INPUT_GRO="${SYSTEM_NAME}_solv_ions.gro"
                INPUT_TOP="${SYSTEM_NAME}.top"
                shift 2
                ;;
            -t|--time)
                SIMULATION_TIME_NS="$2"
                shift 2
                ;;
            -T|--temp)
                TEMPERATURE="$2"
                shift 2
                ;;
            -P|--press)
                PRESSURE="$2"
                shift 2
                ;;
            -p|--nproc)
                NPROC="$2"
                shift 2
                ;;
            -g|--gpu)
                GPU_ID="$2"
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
    echo -e "${PURPLE}           🧬 Molecular Simulation Toolkit - 模拟执行 🧬${NC}"
    echo -e "${PURPLE}================================================================================${NC}"
    
    log_info "开始分子动力学模拟流程"
    log_info "系统名称: $SYSTEM_NAME"
    log_info "模拟时长: $SIMULATION_TIME_NS ns"
    log_info "模拟温度: $TEMPERATURE K"
    log_info "模拟压力: $PRESSURE bar"
    log_info "处理器核心: $NPROC"
    if [[ -n "$GPU_ID" ]]; then
        log_info "GPU设备: $GPU_ID"
    fi
    
    # 检查GROMACS和依赖
    check_gromacs
    
    # 检查bc命令（用于计算）
    if ! command -v bc &> /dev/null; then
        log_error "bc命令未找到，请安装bc包"
        exit 1
    fi
    
    # 执行主要流程
    local pipeline_start=$(date +%s)
    
    run_energy_minimization
    run_nvt_equilibration
    run_npt_equilibration
    run_production_simulation
    generate_simulation_report
    
    # 计算总耗时
    local total_runtime=$(calculate_runtime $pipeline_start)
    
    log_success "🎉 分子动力学模拟完成！总耗时: $total_runtime"
    log_info "下一步: 运行 sop_analyze_trajectory.sh 进行轨迹分析"
    
    # 显示结果概览
    echo ""
    echo -e "${GREEN}================================================================================${NC}"
    echo -e "${GREEN}                           🧬 模拟完成概览 🧬${NC}"
    echo -e "${GREEN}================================================================================${NC}"
    echo -e "${CYAN}📁 轨迹文件: ${NC}md.xtc"
    echo -e "${CYAN}⚡ 能量文件: ${NC}md.edr"
    echo -e "${CYAN}🏗️  最终结构: ${NC}md.gro"
    echo -e "${CYAN}📊 模拟报告: ${NC}${SYSTEM_NAME}_simulation_report.txt"
    echo -e "${CYAN}⏱️  总耗时: ${NC}$total_runtime"
    echo -e "${GREEN}================================================================================${NC}"
    echo ""
}

# 错误处理
trap 'log_error "脚本执行过程中发生错误"; exit 1' ERR

# 执行主函数
main "$@"