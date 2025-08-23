#!/usr/bin/env node

/**
 * NEXUS Research Workstation 自动化部署脚本
 * 支持多平台构建、发布和部署
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const os = require('os');

// 配置
const config = {
  platforms: ['win', 'mac', 'linux'],
  outputDir: 'dist-electron',
  releaseDir: 'releases',
  version: require('../package.json').version,
  productName: 'NEXUS Research Workstation'
};

// 颜色输出
const colors = {
  reset: '\x1b[0m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m'
};

function log(message, color = 'reset') {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

function success(message) {
  log(`✅ ${message}`, 'green');
}

function error(message) {
  log(`❌ ${message}`, 'red');
}

function warning(message) {
  log(`⚠️  ${message}`, 'yellow');
}

function info(message) {
  log(`ℹ️  ${message}`, 'cyan');
}

function header(message) {
  log(`\n🚀 ${message}`, 'magenta');
  log('='.repeat(50), 'magenta');
}

// 执行命令
function exec(command, options = {}) {
  try {
    info(`执行: ${command}`);
    const result = execSync(command, { 
      stdio: 'inherit', 
      encoding: 'utf8',
      ...options 
    });
    return result;
  } catch (err) {
    error(`命令执行失败: ${command}`);
    throw err;
  }
}

// 检查依赖
function checkDependencies() {
  header('检查构建依赖');
  
  const dependencies = [
    { cmd: 'node --version', name: 'Node.js' },
    { cmd: 'npm --version', name: 'npm' },
    { cmd: 'git --version', name: 'Git' }
  ];

  for (const dep of dependencies) {
    try {
      const version = execSync(dep.cmd, { encoding: 'utf8' }).trim();
      success(`${dep.name}: ${version}`);
    } catch (err) {
      error(`${dep.name} 未安装或不可用`);
      process.exit(1);
    }
  }
}

// 清理构建目录
function cleanBuild() {
  header('清理构建目录');
  
  const dirsToClean = [config.outputDir, config.releaseDir, 'dist'];
  
  for (const dir of dirsToClean) {
    if (fs.existsSync(dir)) {
      exec(`rm -rf ${dir}`);
      success(`清理目录: ${dir}`);
    }
  }
}

// 安装依赖
function installDependencies() {
  header('安装项目依赖');
  
  exec('npm ci');
  success('Node.js 依赖安装完成');
  
  // 检查Python依赖
  if (fs.existsSync('backend/requirements.txt')) {
    try {
      exec('pip install -r backend/requirements.txt');
      success('Python 依赖安装完成');
    } catch (err) {
      warning('Python 依赖安装失败，但继续构建');
    }
  }
}

// 运行测试
function runTests() {
  header('运行测试套件');
  
  try {
    exec('npm run test:run');
    success('所有测试通过');
  } catch (err) {
    warning('测试失败，但继续构建');
  }
}

// 构建应用
function buildApp() {
  header('构建应用');
  
  exec('npm run build');
  success('应用构建完成');
}

// 构建Electron应用
function buildElectron(platforms = config.platforms) {
  header(`构建Electron应用 (${platforms.join(', ')})`);
  
  // 创建发布目录
  if (!fs.existsSync(config.releaseDir)) {
    fs.mkdirSync(config.releaseDir, { recursive: true });
  }
  
  for (const platform of platforms) {
    info(`构建 ${platform} 平台...`);
    
    try {
      exec(`npm run dist-${platform}`);
      success(`${platform} 平台构建完成`);
      
      // 移动构建产物到发布目录
      moveArtifacts(platform);
    } catch (err) {
      error(`${platform} 平台构建失败`);
      throw err;
    }
  }
}

// 移动构建产物
function moveArtifacts(platform) {
  const sourceDir = config.outputDir;
  const targetDir = path.join(config.releaseDir, platform);
  
  if (!fs.existsSync(targetDir)) {
    fs.mkdirSync(targetDir, { recursive: true });
  }
  
  if (fs.existsSync(sourceDir)) {
    const files = fs.readdirSync(sourceDir);
    for (const file of files) {
      const sourcePath = path.join(sourceDir, file);
      const targetPath = path.join(targetDir, file);
      
      if (fs.statSync(sourcePath).isFile()) {
        fs.copyFileSync(sourcePath, targetPath);
        info(`移动文件: ${file} -> ${platform}/`);
      }
    }
  }
}

// 生成校验和
function generateChecksums() {
  header('生成文件校验和');
  
  const releaseDir = config.releaseDir;
  if (!fs.existsSync(releaseDir)) {
    warning('发布目录不存在，跳过校验和生成');
    return;
  }
  
  const platforms = fs.readdirSync(releaseDir);
  for (const platform of platforms) {
    const platformDir = path.join(releaseDir, platform);
    if (fs.statSync(platformDir).isDirectory()) {
      const files = fs.readdirSync(platformDir);
      const checksumFile = path.join(platformDir, 'checksums.txt');
      
      let checksums = '';
      for (const file of files) {
        const filePath = path.join(platformDir, file);
        if (fs.statSync(filePath).isFile() && file !== 'checksums.txt') {
          try {
            const checksum = execSync(`shasum -a 256 "${filePath}"`, { encoding: 'utf8' });
            checksums += checksum;
          } catch (err) {
            warning(`无法生成 ${file} 的校验和`);
          }
        }
      }
      
      if (checksums) {
        fs.writeFileSync(checksumFile, checksums);
        success(`生成校验和文件: ${platform}/checksums.txt`);
      }
    }
  }
}

// 创建发布说明
function createReleaseNotes() {
  header('创建发布说明');
  
  const releaseNotes = `# NEXUS Research Workstation v${config.version}

## 🚀 新功能
- 革命性远程电源管理系统
- 全球远程访问支持
- 企业级安全保障
- 完美移动端体验

## 🔧 技术改进
- WebSocket双向通信
- PWA离线支持
- 跨平台兼容性
- 自动更新机制

## 📦 安装包
| 平台 | 文件 | 大小 |
|------|------|------|
| Windows | NEXUS-Setup.exe | ~150MB |
| macOS | NEXUS-Research-Workstation.dmg | ~160MB |
| Linux | NEXUS-Research-Workstation.AppImage | ~140MB |

## 🔒 安全校验
每个安装包都包含SHA256校验和，请在安装前验证文件完整性。

## 📚 文档
- [安装指南](deployment/README.md)
- [使用文档](README.md)
- [API文档](docs/API.md)

---

**完整更新日志**: https://github.com/novenazgarfield/research-workstation/compare/v${getPreviousVersion()}...v${config.version}
`;

  const releaseNotesPath = path.join(config.releaseDir, 'RELEASE_NOTES.md');
  fs.writeFileSync(releaseNotesPath, releaseNotes);
  success('发布说明创建完成');
}

// 获取上一个版本号（简化实现）
function getPreviousVersion() {
  const parts = config.version.split('.');
  const patch = parseInt(parts[2]) - 1;
  return `${parts[0]}.${parts[1]}.${Math.max(0, patch)}`;
}

// 打包发布文件
function packageReleases() {
  header('打包发布文件');
  
  const releaseDir = config.releaseDir;
  if (!fs.existsSync(releaseDir)) {
    error('发布目录不存在');
    return;
  }
  
  const platforms = fs.readdirSync(releaseDir);
  for (const platform of platforms) {
    const platformDir = path.join(releaseDir, platform);
    if (fs.statSync(platformDir).isDirectory()) {
      const archiveName = `nexus-${config.version}-${platform}.zip`;
      const archivePath = path.join(releaseDir, archiveName);
      
      try {
        exec(`cd ${releaseDir} && zip -r ${archiveName} ${platform}/`);
        success(`创建压缩包: ${archiveName}`);
      } catch (err) {
        warning(`创建 ${platform} 压缩包失败`);
      }
    }
  }
}

// 显示构建摘要
function showSummary() {
  header('构建摘要');
  
  info(`产品名称: ${config.productName}`);
  info(`版本: ${config.version}`);
  info(`构建时间: ${new Date().toLocaleString()}`);
  info(`构建平台: ${os.platform()} ${os.arch()}`);
  
  if (fs.existsSync(config.releaseDir)) {
    const files = fs.readdirSync(config.releaseDir, { recursive: true });
    info(`生成文件数: ${files.length}`);
    
    let totalSize = 0;
    for (const file of files) {
      const filePath = path.join(config.releaseDir, file);
      if (fs.existsSync(filePath) && fs.statSync(filePath).isFile()) {
        totalSize += fs.statSync(filePath).size;
      }
    }
    
    info(`总大小: ${(totalSize / 1024 / 1024).toFixed(2)} MB`);
  }
  
  success('🎉 构建完成！');
  info(`发布文件位于: ${path.resolve(config.releaseDir)}`);
}

// 主函数
async function main() {
  const args = process.argv.slice(2);
  const command = args[0] || 'build';
  
  log(`\n🚀 NEXUS Research Workstation 部署脚本`, 'magenta');
  log(`版本: ${config.version}`, 'cyan');
  log(`命令: ${command}`, 'cyan');
  log('='.repeat(60), 'magenta');
  
  try {
    switch (command) {
      case 'build':
        checkDependencies();
        cleanBuild();
        installDependencies();
        runTests();
        buildApp();
        buildElectron();
        generateChecksums();
        createReleaseNotes();
        packageReleases();
        showSummary();
        break;
        
      case 'build-platform':
        const platform = args[1];
        if (!platform || !config.platforms.includes(platform)) {
          error(`无效平台: ${platform}. 支持的平台: ${config.platforms.join(', ')}`);
          process.exit(1);
        }
        checkDependencies();
        buildApp();
        buildElectron([platform]);
        success(`${platform} 平台构建完成`);
        break;
        
      case 'clean':
        cleanBuild();
        break;
        
      case 'test':
        runTests();
        break;
        
      case 'install':
        installDependencies();
        break;
        
      default:
        error(`未知命令: ${command}`);
        info('可用命令: build, build-platform <platform>, clean, test, install');
        process.exit(1);
    }
  } catch (err) {
    error(`部署失败: ${err.message}`);
    process.exit(1);
  }
}

// 错误处理
process.on('uncaughtException', (err) => {
  error(`未捕获的异常: ${err.message}`);
  process.exit(1);
});

process.on('unhandledRejection', (reason, promise) => {
  error(`未处理的Promise拒绝: ${reason}`);
  process.exit(1);
});

// 运行主函数
if (require.main === module) {
  main();
}

module.exports = {
  config,
  checkDependencies,
  cleanBuild,
  installDependencies,
  runTests,
  buildApp,
  buildElectron,
  generateChecksums,
  createReleaseNotes,
  packageReleases,
  showSummary
};