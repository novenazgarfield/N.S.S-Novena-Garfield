const crypto = require('crypto');
const path = require('path');
const fs = require('fs');
const { promisify } = require('util');

/**
 * 生成唯一ID
 */
function generateId(prefix = '') {
  const timestamp = Date.now().toString(36);
  const random = crypto.randomBytes(4).toString('hex');
  return prefix ? `${prefix}_${timestamp}_${random}` : `${timestamp}_${random}`;
}

/**
 * 生成会话ID
 */
function generateSessionId() {
  return generateId('session');
}

/**
 * 安全的JSON解析
 */
function safeJsonParse(str, defaultValue = null) {
  try {
    return JSON.parse(str);
  } catch (error) {
    return defaultValue;
  }
}

/**
 * 安全的JSON字符串化
 */
function safeJsonStringify(obj, space = null) {
  try {
    return JSON.stringify(obj, null, space);
  } catch (error) {
    return '{}';
  }
}

/**
 * 延迟函数
 */
function delay(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * 防抖函数
 */
function debounce(func, wait, immediate = false) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      timeout = null;
      if (!immediate) func.apply(this, args);
    };
    const callNow = immediate && !timeout;
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
    if (callNow) func.apply(this, args);
  };
}

/**
 * 节流函数
 */
function throttle(func, limit) {
  let inThrottle;
  return function executedFunction(...args) {
    if (!inThrottle) {
      func.apply(this, args);
      inThrottle = true;
      setTimeout(() => inThrottle = false, limit);
    }
  };
}

/**
 * 格式化字节大小
 */
function formatBytes(bytes, decimals = 2) {
  if (bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
  
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

/**
 * 格式化持续时间
 */
function formatDuration(ms) {
  if (ms < 1000) return `${ms}ms`;
  if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`;
  if (ms < 3600000) return `${(ms / 60000).toFixed(1)}m`;
  return `${(ms / 3600000).toFixed(1)}h`;
}

/**
 * 获取文件扩展名
 */
function getFileExtension(filePath) {
  return path.extname(filePath).toLowerCase().slice(1);
}

/**
 * 检查文件是否存在
 */
async function fileExists(filePath) {
  try {
    await promisify(fs.access)(filePath, fs.constants.F_OK);
    return true;
  } catch {
    return false;
  }
}

/**
 * 确保目录存在
 */
async function ensureDir(dirPath) {
  try {
    await promisify(fs.mkdir)(dirPath, { recursive: true });
    return true;
  } catch (error) {
    return false;
  }
}

/**
 * 获取文件统计信息
 */
async function getFileStats(filePath) {
  try {
    const stats = await promisify(fs.stat)(filePath);
    return {
      size: stats.size,
      created: stats.birthtime,
      modified: stats.mtime,
      accessed: stats.atime,
      isFile: stats.isFile(),
      isDirectory: stats.isDirectory()
    };
  } catch (error) {
    return null;
  }
}

/**
 * 截断文本
 */
function truncateText(text, maxLength, suffix = '...') {
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength - suffix.length) + suffix;
}

/**
 * 清理文本（移除ANSI转义序列等）
 */
function cleanText(text) {
  // 移除ANSI转义序列
  const ansiRegex = /\x1b\[[0-9;]*m/g;
  return text.replace(ansiRegex, '').trim();
}

/**
 * 提取错误信息
 */
function extractErrorInfo(text) {
  const errorPatterns = [
    /error:\s*(.+)/gi,
    /exception:\s*(.+)/gi,
    /failed:\s*(.+)/gi,
    /fatal:\s*(.+)/gi,
    /panic:\s*(.+)/gi
  ];
  
  const errors = [];
  for (const pattern of errorPatterns) {
    const matches = text.matchAll(pattern);
    for (const match of matches) {
      errors.push(match[1].trim());
    }
  }
  
  return errors;
}

/**
 * 检测文本语言
 */
function detectLanguage(text) {
  // 简单的语言检测
  const chineseRegex = /[\u4e00-\u9fff]/;
  const englishRegex = /[a-zA-Z]/;
  
  const hasChinese = chineseRegex.test(text);
  const hasEnglish = englishRegex.test(text);
  
  if (hasChinese && hasEnglish) return 'mixed';
  if (hasChinese) return 'zh';
  if (hasEnglish) return 'en';
  return 'unknown';
}

/**
 * 计算文本相似度
 */
function calculateSimilarity(str1, str2) {
  const longer = str1.length > str2.length ? str1 : str2;
  const shorter = str1.length > str2.length ? str2 : str1;
  
  if (longer.length === 0) return 1.0;
  
  const editDistance = levenshteinDistance(longer, shorter);
  return (longer.length - editDistance) / longer.length;
}

/**
 * 计算编辑距离
 */
function levenshteinDistance(str1, str2) {
  const matrix = [];
  
  for (let i = 0; i <= str2.length; i++) {
    matrix[i] = [i];
  }
  
  for (let j = 0; j <= str1.length; j++) {
    matrix[0][j] = j;
  }
  
  for (let i = 1; i <= str2.length; i++) {
    for (let j = 1; j <= str1.length; j++) {
      if (str2.charAt(i - 1) === str1.charAt(j - 1)) {
        matrix[i][j] = matrix[i - 1][j - 1];
      } else {
        matrix[i][j] = Math.min(
          matrix[i - 1][j - 1] + 1,
          matrix[i][j - 1] + 1,
          matrix[i - 1][j] + 1
        );
      }
    }
  }
  
  return matrix[str2.length][str1.length];
}

/**
 * 重试函数
 */
async function retry(fn, maxAttempts = 3, delay = 1000) {
  let lastError;
  
  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error;
      if (attempt < maxAttempts) {
        await new Promise(resolve => setTimeout(resolve, delay * attempt));
      }
    }
  }
  
  throw lastError;
}

/**
 * 超时包装器
 */
function withTimeout(promise, timeoutMs) {
  return Promise.race([
    promise,
    new Promise((_, reject) => 
      setTimeout(() => reject(new Error('Operation timed out')), timeoutMs)
    )
  ]);
}

/**
 * 批处理函数
 */
async function batch(items, batchSize, processor) {
  const results = [];
  
  for (let i = 0; i < items.length; i += batchSize) {
    const batch = items.slice(i, i + batchSize);
    const batchResults = await Promise.all(batch.map(processor));
    results.push(...batchResults);
  }
  
  return results;
}

/**
 * 内存使用情况
 */
function getMemoryUsage() {
  const usage = process.memoryUsage();
  return {
    rss: formatBytes(usage.rss),
    heapTotal: formatBytes(usage.heapTotal),
    heapUsed: formatBytes(usage.heapUsed),
    external: formatBytes(usage.external),
    arrayBuffers: formatBytes(usage.arrayBuffers)
  };
}

/**
 * 系统信息
 */
function getSystemInfo() {
  const os = require('os');
  return {
    platform: os.platform(),
    arch: os.arch(),
    cpus: os.cpus().length,
    totalMemory: formatBytes(os.totalmem()),
    freeMemory: formatBytes(os.freemem()),
    uptime: formatDuration(os.uptime() * 1000),
    nodeVersion: process.version
  };
}

module.exports = {
  generateId,
  generateSessionId,
  safeJsonParse,
  safeJsonStringify,
  delay,
  debounce,
  throttle,
  formatBytes,
  formatDuration,
  getFileExtension,
  fileExists,
  ensureDir,
  getFileStats,
  truncateText,
  cleanText,
  extractErrorInfo,
  detectLanguage,
  calculateSimilarity,
  levenshteinDistance,
  retry,
  withTimeout,
  batch,
  getMemoryUsage,
  getSystemInfo
};