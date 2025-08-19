const { createModuleLogger } = require('../shared/logger');
const { extractErrorInfo, detectLanguage } = require('../shared/utils');

const logger = createModuleLogger('pattern-recognizer');

class PatternRecognizer {
  constructor() {
    this.patterns = this.initializePatterns();
  }

  /**
   * 初始化模式定义
   */
  initializePatterns() {
    return {
      // 错误模式
      errors: {
        // 编译错误
        compilation: {
          patterns: [
            /error:\s*(.+)/gi,
            /fatal error:\s*(.+)/gi,
            /compilation terminated/gi,
            /undefined reference to/gi,
            /cannot find symbol/gi,
            /syntax error/gi
          ],
          severity: 'high',
          category: 'compilation'
        },

        // 运行时错误
        runtime: {
          patterns: [
            /exception:\s*(.+)/gi,
            /traceback/gi,
            /segmentation fault/gi,
            /core dumped/gi,
            /null pointer/gi,
            /access violation/gi
          ],
          severity: 'high',
          category: 'runtime'
        },

        // 网络错误
        network: {
          patterns: [
            /connection refused/gi,
            /timeout/gi,
            /network unreachable/gi,
            /dns resolution failed/gi,
            /certificate verify failed/gi,
            /ssl error/gi
          ],
          severity: 'medium',
          category: 'network'
        },

        // 文件系统错误
        filesystem: {
          patterns: [
            /no such file or directory/gi,
            /permission denied/gi,
            /disk full/gi,
            /file not found/gi,
            /access denied/gi,
            /directory not empty/gi
          ],
          severity: 'medium',
          category: 'filesystem'
        },

        // 依赖错误
        dependency: {
          patterns: [
            /module not found/gi,
            /package not found/gi,
            /import error/gi,
            /missing dependency/gi,
            /version conflict/gi,
            /incompatible version/gi
          ],
          severity: 'medium',
          category: 'dependency'
        }
      },

      // 警告模式
      warnings: {
        deprecation: {
          patterns: [
            /deprecated/gi,
            /warning.*deprecated/gi,
            /will be removed in/gi
          ],
          severity: 'low',
          category: 'deprecation'
        },

        performance: {
          patterns: [
            /slow query/gi,
            /performance warning/gi,
            /memory leak/gi,
            /high cpu usage/gi
          ],
          severity: 'medium',
          category: 'performance'
        }
      },

      // 成功模式
      success: {
        build: {
          patterns: [
            /build successful/gi,
            /compilation successful/gi,
            /test.*passed/gi,
            /all tests passed/gi
          ],
          severity: 'info',
          category: 'success'
        },

        deployment: {
          patterns: [
            /deployed successfully/gi,
            /deployment complete/gi,
            /server started/gi,
            /listening on port/gi
          ],
          severity: 'info',
          category: 'deployment'
        }
      },

      // 特定技术栈模式
      tech_specific: {
        // Python
        python: {
          patterns: [
            /traceback \(most recent call last\)/gi,
            /modulenotfounderror/gi,
            /syntaxerror/gi,
            /indentationerror/gi,
            /keyerror/gi,
            /attributeerror/gi
          ],
          language: 'python',
          category: 'python_error'
        },

        // JavaScript/Node.js
        javascript: {
          patterns: [
            /referenceerror/gi,
            /typeerror/gi,
            /syntaxerror/gi,
            /rangeerror/gi,
            /cannot read property/gi,
            /is not a function/gi
          ],
          language: 'javascript',
          category: 'javascript_error'
        },

        // Java
        java: {
          patterns: [
            /exception in thread/gi,
            /nullpointerexception/gi,
            /classnotfoundexception/gi,
            /illegalargumentexception/gi,
            /at\s+[\w.]+\([\w.]+:\d+\)/gi
          ],
          language: 'java',
          category: 'java_error'
        },

        // C/C++
        cpp: {
          patterns: [
            /segmentation fault/gi,
            /core dumped/gi,
            /undefined reference/gi,
            /fatal error.*\.h.*no such file/gi,
            /error:\s*expected/gi
          ],
          language: 'cpp',
          category: 'cpp_error'
        },

        // Git
        git: {
          patterns: [
            /merge conflict/gi,
            /fatal: not a git repository/gi,
            /error: failed to push/gi,
            /rejected.*non-fast-forward/gi,
            /your branch is behind/gi
          ],
          tool: 'git',
          category: 'git_error'
        },

        // Docker
        docker: {
          patterns: [
            /docker: error response from daemon/gi,
            /container.*exited with code/gi,
            /image.*not found/gi,
            /port.*already in use/gi,
            /no space left on device/gi
          ],
          tool: 'docker',
          category: 'docker_error'
        }
      }
    };
  }

  /**
   * 分析文本并识别模式
   */
  analyzeText(text, context = {}) {
    const results = {
      patterns: [],
      severity: 'info',
      categories: new Set(),
      language: detectLanguage(text),
      confidence: 0,
      metadata: {
        textLength: text.length,
        lineCount: text.split('\n').length,
        context
      }
    };

    try {
      // 分析各种模式
      this.analyzeErrorPatterns(text, results);
      this.analyzeWarningPatterns(text, results);
      this.analyzeSuccessPatterns(text, results);
      this.analyzeTechSpecificPatterns(text, results);

      // 计算整体严重程度
      results.severity = this.calculateOverallSeverity(results.patterns);

      // 计算置信度
      results.confidence = this.calculateConfidence(results.patterns, text);

      // 转换Set为Array
      results.categories = Array.from(results.categories);

      logger.debug('Pattern analysis completed', {
        patternsFound: results.patterns.length,
        severity: results.severity,
        categories: results.categories,
        confidence: results.confidence
      });

      return results;

    } catch (error) {
      logger.error('Pattern analysis failed', { error: error.message });
      return results;
    }
  }

  /**
   * 分析错误模式
   */
  analyzeErrorPatterns(text, results) {
    for (const [errorType, config] of Object.entries(this.patterns.errors)) {
      const matches = this.findPatternMatches(text, config.patterns);
      if (matches.length > 0) {
        results.patterns.push({
          type: 'error',
          subtype: errorType,
          severity: config.severity,
          category: config.category,
          matches: matches,
          confidence: this.calculatePatternConfidence(matches, text)
        });
        results.categories.add(config.category);
      }
    }
  }

  /**
   * 分析警告模式
   */
  analyzeWarningPatterns(text, results) {
    for (const [warningType, config] of Object.entries(this.patterns.warnings)) {
      const matches = this.findPatternMatches(text, config.patterns);
      if (matches.length > 0) {
        results.patterns.push({
          type: 'warning',
          subtype: warningType,
          severity: config.severity,
          category: config.category,
          matches: matches,
          confidence: this.calculatePatternConfidence(matches, text)
        });
        results.categories.add(config.category);
      }
    }
  }

  /**
   * 分析成功模式
   */
  analyzeSuccessPatterns(text, results) {
    for (const [successType, config] of Object.entries(this.patterns.success)) {
      const matches = this.findPatternMatches(text, config.patterns);
      if (matches.length > 0) {
        results.patterns.push({
          type: 'success',
          subtype: successType,
          severity: config.severity,
          category: config.category,
          matches: matches,
          confidence: this.calculatePatternConfidence(matches, text)
        });
        results.categories.add(config.category);
      }
    }
  }

  /**
   * 分析技术特定模式
   */
  analyzeTechSpecificPatterns(text, results) {
    for (const [techType, config] of Object.entries(this.patterns.tech_specific)) {
      const matches = this.findPatternMatches(text, config.patterns);
      if (matches.length > 0) {
        results.patterns.push({
          type: 'tech_specific',
          subtype: techType,
          severity: 'medium',
          category: config.category,
          language: config.language,
          tool: config.tool,
          matches: matches,
          confidence: this.calculatePatternConfidence(matches, text)
        });
        results.categories.add(config.category);
      }
    }
  }

  /**
   * 查找模式匹配
   */
  findPatternMatches(text, patterns) {
    const matches = [];
    const lines = text.split('\n');

    for (const pattern of patterns) {
      const globalMatches = text.matchAll(pattern);
      for (const match of globalMatches) {
        // 找到匹配所在的行号
        const beforeMatch = text.substring(0, match.index);
        const lineNumber = beforeMatch.split('\n').length;
        
        matches.push({
          pattern: pattern.source,
          match: match[0],
          fullMatch: match,
          lineNumber: lineNumber,
          lineContent: lines[lineNumber - 1] || '',
          index: match.index
        });
      }
    }

    return matches;
  }

  /**
   * 计算模式置信度
   */
  calculatePatternConfidence(matches, text) {
    if (matches.length === 0) return 0;

    // 基础置信度基于匹配数量
    let confidence = Math.min(matches.length * 0.2, 0.8);

    // 根据匹配的具体性调整
    const specificityBonus = matches.reduce((sum, match) => {
      // 更具体的模式（更长的匹配）获得更高分数
      return sum + Math.min(match.match.length / 50, 0.1);
    }, 0);

    confidence += specificityBonus;

    // 根据文本长度调整
    const textLengthFactor = Math.min(text.length / 1000, 1);
    confidence *= (0.5 + textLengthFactor * 0.5);

    return Math.min(confidence, 1);
  }

  /**
   * 计算整体严重程度
   */
  calculateOverallSeverity(patterns) {
    if (patterns.length === 0) return 'info';

    const severityLevels = { 'low': 1, 'medium': 2, 'high': 3, 'critical': 4 };
    let maxSeverity = 0;

    for (const pattern of patterns) {
      const level = severityLevels[pattern.severity] || 0;
      if (level > maxSeverity) {
        maxSeverity = level;
      }
    }

    const severityMap = { 1: 'low', 2: 'medium', 3: 'high', 4: 'critical' };
    return severityMap[maxSeverity] || 'info';
  }

  /**
   * 计算整体置信度
   */
  calculateConfidence(patterns, text) {
    if (patterns.length === 0) return 0;

    // 计算平均置信度
    const avgConfidence = patterns.reduce((sum, p) => sum + p.confidence, 0) / patterns.length;

    // 根据模式数量调整
    const patternCountFactor = Math.min(patterns.length / 5, 1);

    // 根据文本长度调整
    const textLengthFactor = Math.min(text.length / 500, 1);

    return Math.min(avgConfidence * patternCountFactor * textLengthFactor, 1);
  }

  /**
   * 提取关键行
   */
  extractKeyLines(text, patterns, maxLines = 5) {
    const lines = text.split('\n');
    const keyLineNumbers = new Set();

    // 从模式匹配中提取行号
    for (const pattern of patterns) {
      for (const match of pattern.matches) {
        keyLineNumbers.add(match.lineNumber);
        
        // 添加上下文行
        if (match.lineNumber > 1) {
          keyLineNumbers.add(match.lineNumber - 1);
        }
        if (match.lineNumber < lines.length) {
          keyLineNumbers.add(match.lineNumber + 1);
        }
      }
    }

    // 转换为排序数组并限制数量
    const sortedLineNumbers = Array.from(keyLineNumbers)
      .sort((a, b) => a - b)
      .slice(0, maxLines);

    return sortedLineNumbers.map(lineNum => ({
      lineNumber: lineNum,
      content: lines[lineNum - 1] || ''
    }));
  }

  /**
   * 提取关键短语
   */
  extractKeyPhrases(patterns, maxPhrases = 5) {
    const phrases = new Set();

    for (const pattern of patterns) {
      for (const match of pattern.matches) {
        // 添加完整匹配
        phrases.add(match.match.trim());
        
        // 如果有捕获组，添加捕获的内容
        if (match.fullMatch.length > 1) {
          for (let i = 1; i < match.fullMatch.length; i++) {
            if (match.fullMatch[i]) {
              phrases.add(match.fullMatch[i].trim());
            }
          }
        }
      }
    }

    return Array.from(phrases)
      .filter(phrase => phrase.length > 3) // 过滤太短的短语
      .slice(0, maxPhrases);
  }

  /**
   * 生成模式摘要
   */
  generatePatternSummary(analysisResult) {
    const { patterns, severity, categories } = analysisResult;

    if (patterns.length === 0) {
      return '未检测到特定模式';
    }

    // 按类型分组
    const errorPatterns = patterns.filter(p => p.type === 'error');
    const warningPatterns = patterns.filter(p => p.type === 'warning');
    const successPatterns = patterns.filter(p => p.type === 'success');
    const techPatterns = patterns.filter(p => p.type === 'tech_specific');

    let summary = '';

    if (errorPatterns.length > 0) {
      const errorTypes = errorPatterns.map(p => p.subtype).join(', ');
      summary += `检测到${errorPatterns.length}个错误模式: ${errorTypes}`;
    }

    if (warningPatterns.length > 0) {
      if (summary) summary += '; ';
      const warningTypes = warningPatterns.map(p => p.subtype).join(', ');
      summary += `${warningPatterns.length}个警告: ${warningTypes}`;
    }

    if (successPatterns.length > 0) {
      if (summary) summary += '; ';
      const successTypes = successPatterns.map(p => p.subtype).join(', ');
      summary += `${successPatterns.length}个成功指标: ${successTypes}`;
    }

    if (techPatterns.length > 0) {
      if (summary) summary += '; ';
      const techTypes = [...new Set(techPatterns.map(p => p.language || p.tool))].join(', ');
      summary += `涉及技术: ${techTypes}`;
    }

    return summary || '检测到多种模式';
  }

  /**
   * 添加自定义模式
   */
  addCustomPattern(category, name, config) {
    if (!this.patterns[category]) {
      this.patterns[category] = {};
    }
    this.patterns[category][name] = config;
    logger.info('Custom pattern added', { category, name });
  }

  /**
   * 获取所有模式统计
   */
  getPatternStats() {
    const stats = {
      totalPatterns: 0,
      categories: {}
    };

    for (const [category, patterns] of Object.entries(this.patterns)) {
      const count = Object.keys(patterns).length;
      stats.categories[category] = count;
      stats.totalPatterns += count;
    }

    return stats;
  }
}

// 创建单例实例
const patternRecognizer = new PatternRecognizer();

module.exports = patternRecognizer;