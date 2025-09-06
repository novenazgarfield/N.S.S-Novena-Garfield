@echo off
chcp 65001 >nul

REM 🧠 N.S.S-Novena-Garfield Node.js依赖安装脚本 (Windows)
REM 多模态AI融合研究工作站 - Node.js依赖一键安装
REM 使用方法: 双击运行或在命令行执行 install_nodejs_deps.bat

echo 🧠 N.S.S-Novena-Garfield Node.js依赖安装
echo ========================================
echo.

REM 检查Node.js环境
echo 🔍 检查Node.js环境...
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js未安装，请先安装Node.js 16+
    echo 📥 下载地址: https://nodejs.org/
    pause
    exit /b 1
)

npm --version >nul 2>&1
if errorlevel 1 (
    echo ❌ npm未安装，请先安装npm
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('node --version') do set NODE_VERSION=%%i
for /f "tokens=*" %%i in ('npm --version') do set NPM_VERSION=%%i
echo ✅ Node.js版本: %NODE_VERSION%
echo ✅ npm版本: %NPM_VERSION%
echo.

REM 设置npm镜像源（可选）
echo 🌐 配置npm镜像源...
set /p USE_MIRROR="是否使用国内镜像源加速下载? (Y/n): "
if /i "%USE_MIRROR%"=="n" (
    echo 📡 使用默认npm源
) else (
    npm config set registry https://registry.npmmirror.com
    echo ✅ 已设置为国内镜像源
)
echo.

REM 开始安装
echo 🚀 开始安装Node.js依赖...
echo 📊 预计安装大小: ~1.6GB
echo ⏱️ 预计安装时间: 5-20分钟
echo.

set INSTALL_SUCCESS=true

REM 安装Chronicle系统依赖
echo 1️⃣ 安装Chronicle系统依赖...
if exist "systems\chronicle" (
    cd systems\chronicle
    npm install
    if errorlevel 1 (
        echo ❌ Chronicle依赖安装失败
        set INSTALL_SUCCESS=false
    ) else (
        echo ✅ Chronicle依赖安装成功 (~116MB)
    )
    cd ..\..
) else (
    echo ⚠️ Chronicle系统目录不存在，跳过
)
echo.

REM 安装Changlee系统依赖
echo 2️⃣ 安装Changlee系统依赖...
if exist "systems\Changlee" (
    cd systems\Changlee
    npm install
    if errorlevel 1 (
        echo ❌ Changlee依赖安装失败
        set INSTALL_SUCCESS=false
    ) else (
        echo ✅ Changlee依赖安装成功 (~558MB)
    )
    cd ..\..
) else (
    echo ⚠️ Changlee系统目录不存在，跳过
)
echo.

REM 安装NEXUS系统依赖
echo 3️⃣ 安装NEXUS系统依赖...
if exist "systems\nexus" (
    cd systems\nexus
    npm install
    if errorlevel 1 (
        echo ❌ NEXUS依赖安装失败
        set INSTALL_SUCCESS=false
    ) else (
        echo ✅ NEXUS依赖安装成功 (~918MB)
    )
    cd ..\..
) else (
    echo ⚠️ NEXUS系统目录不存在，跳过
)
echo.

REM 验证安装
echo 🔍 验证安装结果...
echo.

if exist "systems\chronicle\node_modules" (
    echo ✅ Chronicle: 已安装
    cd systems\chronicle
    node chronicle.js --help >nul 2>&1
    if errorlevel 1 (
        echo    📋 功能测试: 失败
    ) else (
        echo    📋 功能测试: 通过
    )
    cd ..\..
)

if exist "systems\Changlee\node_modules" (
    echo ✅ Changlee: 已安装
    cd systems\Changlee
    node changlee.js --help >nul 2>&1
    if errorlevel 1 (
        echo    📋 功能测试: 失败
    ) else (
        echo    📋 功能测试: 通过
    )
    cd ..\..
)

if exist "systems\nexus\node_modules" (
    echo ✅ NEXUS: 已安装
    if exist "systems\nexus\package.json" (
        echo    📋 配置文件: 存在
    ) else (
        echo    📋 配置文件: 缺失
    )
)

echo.

REM 安装总结
if "%INSTALL_SUCCESS%"=="true" (
    echo 🎉 Node.js依赖安装完成！
    echo.
    echo 📊 安装统计:
    echo   💾 总大小: ~1.6GB
    echo   📦 系统数: 3个系统
    echo.
    echo 🚀 快速启动:
    echo   📚 Chronicle: cd systems\chronicle ^&^& node chronicle.js server
    echo   🎵 Changlee: cd systems\Changlee ^&^& node changlee.js server
    echo   🌐 NEXUS: cd systems\nexus ^&^& npm run dev
    echo.
    echo 📖 更多信息请查看README.md
) else (
    echo ❌ 部分依赖安装失败
    echo.
    echo 🛠️ 故障排除:
    echo   1. 检查网络连接
    echo   2. 清理npm缓存: npm cache clean --force
    echo   3. 检查磁盘空间
    echo   4. 以管理员身份运行此脚本
    echo.
    echo 📞 如需帮助，请查看requirements.txt中的常见问题解决方案
)

echo.
pause