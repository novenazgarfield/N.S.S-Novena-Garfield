@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM 长离的学习胶囊 - Windows 安装脚本

echo 🐱 欢迎使用长离的学习胶囊安装程序
echo ========================================

REM 检查管理员权限
net session >nul 2>&1
if %errorLevel% == 0 (
    echo ✅ 检测到管理员权限
) else (
    echo ⚠️  建议以管理员身份运行此脚本
)

REM 检查 Node.js
echo 🔍 检查系统要求...
node --version >nul 2>&1
if %errorLevel% == 0 (
    for /f "tokens=*" %%i in ('node --version') do set NODE_VERSION=%%i
    echo ✅ Node.js 已安装: !NODE_VERSION!
    
    REM 检查版本
    for /f "tokens=1 delims=." %%a in ("!NODE_VERSION:v=!") do set NODE_MAJOR=%%a
    if !NODE_MAJOR! LSS 16 (
        echo ❌ 需要 Node.js 16 或更高版本，当前版本: !NODE_VERSION!
        echo 请访问 https://nodejs.org 下载安装
        pause
        exit /b 1
    )
) else (
    echo ❌ 未找到 Node.js，请先安装 Node.js 16+
    echo 请访问 https://nodejs.org 下载安装
    pause
    exit /b 1
)

REM 检查 npm
npm --version >nul 2>&1
if %errorLevel% == 0 (
    for /f "tokens=*" %%i in ('npm --version') do set NPM_VERSION=%%i
    echo ✅ npm 已安装: !NPM_VERSION!
) else (
    echo ❌ 未找到 npm
    pause
    exit /b 1
)

REM 检查 Python
python --version >nul 2>&1
if %errorLevel% == 0 (
    for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
    echo ✅ Python 已安装: !PYTHON_VERSION!
) else (
    echo ⚠️  未找到 Python，某些功能可能无法正常工作
    echo 建议安装 Python 3.8+ 从 https://python.org
)

REM 安装 Windows 构建工具
echo 📦 检查 Windows 构建工具...
npm list -g windows-build-tools >nul 2>&1
if %errorLevel% neq 0 (
    echo 🔧 安装 Windows 构建工具...
    npm install -g windows-build-tools
    if %errorLevel% neq 0 (
        echo ⚠️  构建工具安装失败，某些 native 模块可能无法编译
    )
) else (
    echo ✅ Windows 构建工具已安装
)

REM 安装项目依赖
echo 📦 安装项目依赖...
call npm install
if %errorLevel% neq 0 (
    echo ❌ 主项目依赖安装失败
    pause
    exit /b 1
)

REM 安装渲染进程依赖
if exist "src\renderer\package.json" (
    echo 📦 安装渲染进程依赖...
    cd src\renderer
    call npm install
    if %errorLevel% neq 0 (
        echo ❌ 渲染进程依赖安装失败
        cd ..\..
        pause
        exit /b 1
    )
    cd ..\..
)

echo ✅ 项目依赖安装完成

REM 配置环境
echo ⚙️  配置环境...

REM 创建必要的目录
if not exist "database" mkdir database
if not exist "logs" mkdir logs
if not exist "assets\sounds" mkdir assets\sounds
if not exist "assets\images" mkdir assets\images

REM 配置 API 密钥
if not defined GEMINI_API_KEY (
    echo ⚠️  未设置 GEMINI_API_KEY 环境变量
    set /p API_KEY="请输入你的 Gemini API 密钥 (可选，回车跳过): "
    
    if not "!API_KEY!"=="" (
        echo GEMINI_API_KEY=!API_KEY!> .env
        echo ✅ API 密钥已保存到 .env 文件
    ) else (
        echo ℹ️  跳过 API 密钥配置，稍后可在设置中配置
    )
) else (
    echo GEMINI_API_KEY=%GEMINI_API_KEY%> .env
    echo ✅ 使用环境变量中的 API 密钥
)

echo ✅ 环境配置完成

REM 运行测试
echo 🧪 运行系统测试...
node test_system.js
if %errorLevel% == 0 (
    echo ✅ 系统测试通过
) else (
    echo ⚠️  系统测试失败，但安装可以继续
)

REM 创建桌面快捷方式
echo 🔗 创建桌面快捷方式...
set CURRENT_DIR=%CD%
set DESKTOP=%USERPROFILE%\Desktop
set SHORTCUT_PATH=%DESKTOP%\长离的学习胶囊.bat

echo @echo off > "%SHORTCUT_PATH%"
echo cd /d "%CURRENT_DIR%" >> "%SHORTCUT_PATH%"
echo node start.js >> "%SHORTCUT_PATH%"
echo pause >> "%SHORTCUT_PATH%"

echo ✅ 已创建桌面快捷方式

REM 安装完成
echo.
echo 🎉 安装完成！
echo.
echo 📚 使用方法:
echo   • 启动应用: node start.js
echo   • 运行测试: node test_system.js
echo   • 查看文档: docs\DEVELOPMENT.md
echo   • 桌面快捷方式: 长离的学习胶囊.bat
echo.
echo 🐱 长离正在等待与你一起学习英语！
echo.

REM 询问是否立即启动
set /p START_NOW="是否现在启动应用？(y/N): "
if /i "!START_NOW!"=="y" (
    echo 🚀 启动长离的学习胶囊...
    node start.js
) else (
    echo ℹ️  稍后可以运行 'node start.js' 或双击桌面快捷方式启动应用
)

pause