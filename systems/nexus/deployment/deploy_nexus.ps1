# NEXUS Research Workstation 一键部署脚本 (Windows PowerShell)
# 支持用户交互和自动化部署

param(
    [string]$InstallPath = "",
    [string]$GitHubToken = "",
    [switch]$Silent = $false,
    [switch]$Help = $false
)

# 显示帮助信息
if ($Help) {
    Write-Host @"
NEXUS Research Workstation 一键部署脚本

用法:
    .\deploy_nexus.ps1 [参数]

参数:
    -InstallPath <路径>    指定安装路径 (默认: C:\NEXUS)
    -GitHubToken <令牌>    GitHub个人访问令牌
    -Silent               静默模式，不显示交互提示
    -Help                 显示此帮助信息

示例:
    .\deploy_nexus.ps1
    .\deploy_nexus.ps1 -InstallPath "D:\Tools\NEXUS" -GitHubToken "ghp_xxxx"
    .\deploy_nexus.ps1 -Silent

"@
    exit 0
}

# 颜色输出函数
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

function Write-Success {
    param([string]$Message)
    Write-ColorOutput "✅ $Message" "Green"
}

function Write-Error {
    param([string]$Message)
    Write-ColorOutput "❌ $Message" "Red"
}

function Write-Warning {
    param([string]$Message)
    Write-ColorOutput "⚠️  $Message" "Yellow"
}

function Write-Info {
    param([string]$Message)
    Write-ColorOutput "ℹ️  $Message" "Cyan"
}

# 检查管理员权限
function Test-Administrator {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# 请求管理员权限
function Request-Administrator {
    if (-not (Test-Administrator)) {
        Write-Warning "需要管理员权限来安装系统依赖项"
        Write-Info "正在请求管理员权限..."
        
        $arguments = "-File `"$($MyInvocation.MyCommand.Path)`""
        if ($InstallPath) { $arguments += " -InstallPath `"$InstallPath`"" }
        if ($GitHubToken) { $arguments += " -GitHubToken `"$GitHubToken`"" }
        if ($Silent) { $arguments += " -Silent" }
        
        Start-Process PowerShell -Verb RunAs -ArgumentList $arguments
        exit 0
    }
}

# 检查依赖项
function Test-Dependency {
    param(
        [string]$Command,
        [string]$Name
    )
    
    try {
        $null = Get-Command $Command -ErrorAction Stop
        Write-Success "$Name 已安装"
        return $true
    }
    catch {
        Write-Warning "$Name 未安装"
        return $false
    }
}

# 安装依赖项
function Install-Dependency {
    param(
        [string]$Name,
        [string]$WingetId,
        [string]$InstallLocation = ""
    )
    
    Write-Info "正在安装 $Name..."
    
    try {
        $arguments = "install --id $WingetId --accept-package-agreements --accept-source-agreements"
        if ($InstallLocation) {
            $arguments += " --location `"$InstallLocation`""
        }
        
        $process = Start-Process -FilePath "winget" -ArgumentList $arguments -Wait -PassThru -NoNewWindow
        
        if ($process.ExitCode -eq 0) {
            Write-Success "$Name 安装成功"
            return $true
        }
        else {
            Write-Error "$Name 安装失败 (退出码: $($process.ExitCode))"
            return $false
        }
    }
    catch {
        Write-Error "$Name 安装失败: $($_.Exception.Message)"
        return $false
    }
}

# 克隆代码库
function Clone-Repository {
    param(
        [string]$RepoUrl,
        [string]$TargetPath,
        [string]$Token = ""
    )
    
    Write-Info "正在克隆代码库到 $TargetPath..."
    
    # 如果提供了令牌，修改URL
    if ($Token) {
        $RepoUrl = $RepoUrl -replace "https://github.com/", "https://$Token@github.com/"
    }
    
    try {
        if (Test-Path $TargetPath) {
            Write-Warning "目标目录已存在，正在更新..."
            Set-Location $TargetPath
            & git pull
        }
        else {
            & git clone $RepoUrl $TargetPath
        }
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "代码库克隆/更新成功"
            return $true
        }
        else {
            Write-Error "代码库克隆/更新失败"
            return $false
        }
    }
    catch {
        Write-Error "代码库操作失败: $($_.Exception.Message)"
        return $false
    }
}

# 安装Node.js依赖
function Install-NodeDependencies {
    param([string]$Path)
    
    Write-Info "正在安装Node.js依赖..."
    
    try {
        Set-Location $Path
        & npm install
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Node.js依赖安装成功"
            return $true
        }
        else {
            Write-Error "Node.js依赖安装失败"
            return $false
        }
    }
    catch {
        Write-Error "Node.js依赖安装失败: $($_.Exception.Message)"
        return $false
    }
}

# 安装Python依赖
function Install-PythonDependencies {
    param([string]$Path)
    
    Write-Info "正在安装Python依赖..."
    
    try {
        Set-Location $Path
        
        # 检查是否有requirements.txt
        if (Test-Path "requirements.txt") {
            & pip install -r requirements.txt
        }
        
        # 检查是否有其他Python依赖文件
        if (Test-Path "backend\requirements.txt") {
            & pip install -r backend\requirements.txt
        }
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Python依赖安装成功"
            return $true
        }
        else {
            Write-Error "Python依赖安装失败"
            return $false
        }
    }
    catch {
        Write-Error "Python依赖安装失败: $($_.Exception.Message)"
        return $false
    }
}

# 创建启动脚本
function Create-LaunchScript {
    param([string]$InstallPath)
    
    $scriptPath = Join-Path $InstallPath "launch_nexus.ps1"
    
    $scriptContent = @"
# NEXUS 启动脚本
Set-Location "$InstallPath\systems\nexus"

Write-Host "🚀 启动 NEXUS Research Workstation..." -ForegroundColor Green

# 启动后端WebSocket服务器
Start-Process PowerShell -ArgumentList "-Command", "cd '$InstallPath\systems\nexus\backend'; python websocket_server.py" -WindowStyle Minimized

# 等待后端启动
Start-Sleep -Seconds 3

# 启动前端开发服务器
Start-Process PowerShell -ArgumentList "-Command", "cd '$InstallPath\systems\nexus'; npm run dev" -WindowStyle Normal

Write-Host "✅ NEXUS 启动完成!" -ForegroundColor Green
Write-Host "📱 前端界面: http://localhost:5173" -ForegroundColor Cyan
Write-Host "🔌 WebSocket服务: ws://localhost:8765" -ForegroundColor Cyan
Write-Host "🌐 测试页面: http://localhost:52333/test_remote_center.html" -ForegroundColor Cyan

# 等待用户输入
Read-Host "按回车键退出"
"@

    try {
        $scriptContent | Out-File -FilePath $scriptPath -Encoding UTF8
        Write-Success "启动脚本创建成功: $scriptPath"
        return $true
    }
    catch {
        Write-Error "启动脚本创建失败: $($_.Exception.Message)"
        return $false
    }
}

# 创建桌面快捷方式
function Create-DesktopShortcut {
    param(
        [string]$InstallPath,
        [string]$ScriptPath
    )
    
    try {
        $WshShell = New-Object -comObject WScript.Shell
        $Shortcut = $WshShell.CreateShortcut("$env:USERPROFILE\Desktop\NEXUS Research Workstation.lnk")
        $Shortcut.TargetPath = "PowerShell.exe"
        $Shortcut.Arguments = "-ExecutionPolicy Bypass -File `"$ScriptPath`""
        $Shortcut.WorkingDirectory = $InstallPath
        $Shortcut.IconLocation = "$InstallPath\systems\nexus\public\vite.svg"
        $Shortcut.Description = "NEXUS Research Workstation - 远程指挥与控制系统"
        $Shortcut.Save()
        
        Write-Success "桌面快捷方式创建成功"
        return $true
    }
    catch {
        Write-Error "桌面快捷方式创建失败: $($_.Exception.Message)"
        return $false
    }
}

# 主函数
function Main {
    Write-ColorOutput @"
🚀 NEXUS Research Workstation 一键部署脚本
================================================
版本: 1.0.0
平台: Windows PowerShell
================================================
"@ "Magenta"

    # 请求管理员权限
    Request-Administrator

    # 获取用户输入
    if (-not $Silent) {
        if (-not $InstallPath) {
            $InstallPath = Read-Host "请输入安装路径 (默认: C:\NEXUS)"
            if (-not $InstallPath) {
                $InstallPath = "C:\NEXUS"
            }
        }

        if (-not $GitHubToken) {
            Write-Info "GitHub个人访问令牌用于访问私有仓库"
            Write-Info "如果仓库是公开的，可以直接按回车跳过"
            $GitHubToken = Read-Host "请输入GitHub个人访问令牌 (可选)"
        }
    }
    else {
        if (-not $InstallPath) { $InstallPath = "C:\NEXUS" }
    }

    Write-Info "安装路径: $InstallPath"
    Write-Info "GitHub令牌: $(if ($GitHubToken) { '已提供' } else { '未提供' })"

    # 创建安装目录
    if (-not (Test-Path $InstallPath)) {
        try {
            New-Item -ItemType Directory -Path $InstallPath -Force | Out-Null
            Write-Success "创建安装目录: $InstallPath"
        }
        catch {
            Write-Error "创建安装目录失败: $($_.Exception.Message)"
            exit 1
        }
    }

    # 检查和安装依赖项
    Write-Info "检查系统依赖项..."
    
    $dependencies = @(
        @{ Command = "winget"; Name = "Windows Package Manager"; Required = $true },
        @{ Command = "git"; Name = "Git"; WingetId = "Git.Git"; Required = $true },
        @{ Command = "node"; Name = "Node.js"; WingetId = "OpenJS.NodeJS"; Required = $true },
        @{ Command = "python"; Name = "Python"; WingetId = "Python.Python.3.11"; Required = $true }
    )

    $missingDeps = @()
    foreach ($dep in $dependencies) {
        if (-not (Test-Dependency $dep.Command $dep.Name)) {
            if ($dep.Required) {
                $missingDeps += $dep
            }
        }
    }

    # 安装缺失的依赖项
    if ($missingDeps.Count -gt 0) {
        Write-Info "需要安装以下依赖项:"
        foreach ($dep in $missingDeps) {
            Write-Host "  - $($dep.Name)"
        }

        if (-not $Silent) {
            $confirm = Read-Host "是否继续安装? (y/N)"
            if ($confirm -ne "y" -and $confirm -ne "Y") {
                Write-Warning "用户取消安装"
                exit 0
            }
        }

        foreach ($dep in $missingDeps) {
            if ($dep.WingetId) {
                $installLocation = if ($dep.Name -eq "Git") { "$InstallPath\Git" } elseif ($dep.Name -eq "Python") { "$InstallPath\Python" } else { "" }
                if (-not (Install-Dependency $dep.Name $dep.WingetId $installLocation)) {
                    Write-Error "依赖项安装失败，无法继续"
                    exit 1
                }
            }
        }

        Write-Info "刷新环境变量..."
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")
    }

    # 克隆代码库
    $repoUrl = "https://github.com/novenazgarfield/research-workstation.git"
    if (-not (Clone-Repository $repoUrl $InstallPath $GitHubToken)) {
        Write-Error "代码库克隆失败，无法继续"
        exit 1
    }

    # 切换到NEXUS目录
    $nexusPath = Join-Path $InstallPath "systems\nexus"
    if (-not (Test-Path $nexusPath)) {
        Write-Error "NEXUS目录不存在: $nexusPath"
        exit 1
    }

    # 安装Node.js依赖
    if (-not (Install-NodeDependencies $nexusPath)) {
        Write-Error "Node.js依赖安装失败"
        exit 1
    }

    # 安装Python依赖
    if (-not (Install-PythonDependencies $nexusPath)) {
        Write-Warning "Python依赖安装失败，但继续执行"
    }

    # 创建启动脚本
    $launchScript = Join-Path $InstallPath "launch_nexus.ps1"
    if (-not (Create-LaunchScript $InstallPath)) {
        Write-Warning "启动脚本创建失败"
    }

    # 创建桌面快捷方式
    if (-not (Create-DesktopShortcut $InstallPath $launchScript)) {
        Write-Warning "桌面快捷方式创建失败"
    }

    # 完成安装
    Write-ColorOutput @"

🎉 NEXUS Research Workstation 安装完成!
========================================

📁 安装路径: $InstallPath
🚀 启动脚本: $launchScript
🖥️  桌面快捷方式: 已创建

📱 访问地址:
   - 主界面: http://localhost:5173
   - 测试页面: http://localhost:52333/test_remote_center.html
   - WebSocket: ws://localhost:8765

🔧 手动启动:
   1. 打开PowerShell
   2. 运行: & "$launchScript"

📚 文档: $InstallPath\README.md

"@ "Green"

    if (-not $Silent) {
        $launch = Read-Host "是否立即启动NEXUS? (Y/n)"
        if ($launch -ne "n" -and $launch -ne "N") {
            Write-Info "正在启动NEXUS..."
            & $launchScript
        }
    }
}

# 错误处理
trap {
    Write-Error "脚本执行出错: $($_.Exception.Message)"
    Write-Error "错误位置: $($_.InvocationInfo.ScriptLineNumber):$($_.InvocationInfo.OffsetInLine)"
    exit 1
}

# 执行主函数
Main