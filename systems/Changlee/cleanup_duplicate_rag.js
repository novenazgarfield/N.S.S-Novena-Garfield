#!/usr/bin/env node

/**
 * 清理重复的RAG系统
 * 在确认合并成功后，清理不再需要的重复系统
 */

const fs = require('fs');
const path = require('path');
const readline = require('readline');

class RAGCleanup {
  constructor() {
    this.duplicateRagPath = path.resolve(__dirname, '../../systems/rag-system');
    this.mainRagPath = path.resolve(__dirname, '../../../rag_system');
  }

  async start() {
    console.log('🧹 RAG系统清理工具');
    console.log('=====================================');
    
    await this.showStatus();
    await this.confirmCleanup();
  }

  async showStatus() {
    console.log('\n📊 当前RAG系统状态:');
    console.log('=====================================');
    
    // 检查主RAG系统
    if (fs.existsSync(this.mainRagPath)) {
      console.log('✅ 主RAG系统: /workspace/rag_system/');
      console.log('   📁 包含模块:', this.listModules(this.mainRagPath));
      
      // 检查增强版应用
      const enhancedApp = path.join(this.mainRagPath, 'enhanced_app.py');
      if (fs.existsSync(enhancedApp)) {
        console.log('   🚀 增强版应用: 已安装');
      }
    } else {
      console.log('❌ 主RAG系统: 不存在');
    }
    
    // 检查重复RAG系统
    if (fs.existsSync(this.duplicateRagPath)) {
      console.log('⚠️  重复RAG系统: /workspace/systems/rag-system/');
      console.log('   📁 包含模块:', this.listModules(this.duplicateRagPath));
      console.log('   💾 占用空间:', this.getDirectorySize(this.duplicateRagPath));
    } else {
      console.log('✅ 重复RAG系统: 已清理');
    }
    
    console.log('\n🎯 建议操作:');
    if (fs.existsSync(this.duplicateRagPath)) {
      console.log('• 主RAG系统功能完整，已整合重复系统的优秀模块');
      console.log('• 可以安全删除重复的RAG系统以节省空间');
      console.log('• 桌宠系统将继续使用主RAG系统');
    } else {
      console.log('• 系统已经清理完毕，无需额外操作');
    }
  }

  listModules(ragPath) {
    try {
      const items = fs.readdirSync(ragPath, { withFileTypes: true });
      const modules = items
        .filter(item => item.isDirectory() && !item.name.startsWith('.'))
        .map(item => item.name)
        .slice(0, 5); // 只显示前5个
      
      return modules.length > 0 ? modules.join(', ') : '无';
    } catch (error) {
      return '无法读取';
    }
  }

  getDirectorySize(dirPath) {
    try {
      let totalSize = 0;
      const items = fs.readdirSync(dirPath, { withFileTypes: true });
      
      for (const item of items) {
        const itemPath = path.join(dirPath, item.name);
        if (item.isDirectory()) {
          totalSize += this.getDirectorySizeRecursive(itemPath);
        } else {
          const stats = fs.statSync(itemPath);
          totalSize += stats.size;
        }
      }
      
      return this.formatBytes(totalSize);
    } catch (error) {
      return '未知';
    }
  }

  getDirectorySizeRecursive(dirPath) {
    let totalSize = 0;
    try {
      const items = fs.readdirSync(dirPath, { withFileTypes: true });
      
      for (const item of items) {
        const itemPath = path.join(dirPath, item.name);
        if (item.isDirectory()) {
          totalSize += this.getDirectorySizeRecursive(itemPath);
        } else {
          const stats = fs.statSync(itemPath);
          totalSize += stats.size;
        }
      }
    } catch (error) {
      // 忽略权限错误等
    }
    
    return totalSize;
  }

  formatBytes(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }

  async confirmCleanup() {
    if (!fs.existsSync(this.duplicateRagPath)) {
      console.log('\n✅ 系统已经清理完毕！');
      return;
    }

    const rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout
    });

    console.log('\n🤔 清理选项:');
    console.log('1. 🗑️  删除重复的RAG系统 (推荐)');
    console.log('2. 📦 创建备份后删除');
    console.log('3. 🚫 取消清理');
    console.log('');

    const choice = await new Promise(resolve => {
      rl.question('请选择操作 (1-3): ', resolve);
    });

    rl.close();

    switch (choice.trim()) {
      case '1':
        await this.deleteDuplicateSystem();
        break;
      case '2':
        await this.backupAndDelete();
        break;
      case '3':
        console.log('🚫 取消清理操作');
        break;
      default:
        console.log('❌ 无效选择');
    }
  }

  async deleteDuplicateSystem() {
    console.log('\n🗑️  正在删除重复的RAG系统...');
    
    try {
      this.removeDirectory(this.duplicateRagPath);
      console.log('✅ 重复RAG系统删除成功！');
      console.log('💾 节省空间:', this.getDirectorySize(this.duplicateRagPath));
      console.log('🔗 桌宠系统继续使用主RAG系统');
    } catch (error) {
      console.error('❌ 删除失败:', error.message);
    }
  }

  async backupAndDelete() {
    console.log('\n📦 正在创建备份...');
    
    try {
      const backupPath = this.duplicateRagPath + '_backup_' + Date.now();
      this.copyDirectory(this.duplicateRagPath, backupPath);
      console.log('✅ 备份创建成功:', backupPath);
      
      console.log('🗑️  正在删除原系统...');
      this.removeDirectory(this.duplicateRagPath);
      console.log('✅ 清理完成！');
      console.log('📦 备份位置:', backupPath);
    } catch (error) {
      console.error('❌ 备份和删除失败:', error.message);
    }
  }

  removeDirectory(dirPath) {
    if (fs.existsSync(dirPath)) {
      fs.rmSync(dirPath, { recursive: true, force: true });
    }
  }

  copyDirectory(src, dest) {
    if (!fs.existsSync(src)) return;
    
    fs.mkdirSync(dest, { recursive: true });
    const items = fs.readdirSync(src, { withFileTypes: true });
    
    for (const item of items) {
      const srcPath = path.join(src, item.name);
      const destPath = path.join(dest, item.name);
      
      if (item.isDirectory()) {
        this.copyDirectory(srcPath, destPath);
      } else {
        fs.copyFileSync(srcPath, destPath);
      }
    }
  }
}

// 主函数
async function main() {
  const cleanup = new RAGCleanup();
  await cleanup.start();
}

// 如果直接运行此脚本
if (require.main === module) {
  main().catch(error => {
    console.error('清理过程中出现错误:', error);
    process.exit(1);
  });
}

module.exports = RAGCleanup;