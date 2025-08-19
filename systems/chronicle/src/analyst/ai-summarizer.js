const axios = require('axios');
const { createModuleLogger } = require('../shared/logger');
const { retry, withTimeout, truncateText } = require('../shared/utils');
const config = require('../shared/config');

const logger = createModuleLogger('ai-summarizer');

class AISummarizer {
  constructor() {
    this.provider = config.ai.provider;
    this.apiKey = config.ai.apiKey;
    this.model = config.ai.model;
    this.maxTokens = config.ai.maxTokens;
    this.temperature = config.ai.temperature;
    this.timeout = config.ai.timeout;
    this.isEnabled = !!this.apiKey;
    
    if (!this.isEnabled) {
      logger.warn('AI summarizer is disabled - no API key provided');
    }
  }

  /**
   * 分析日志并生成摘要
   */
  async analyzeLog(logText, context = {}) {
    if (!this.isEnabled) {
      logger.warn('AI analysis skipped - service disabled');
      return this.createFallbackSummary(logText, context);
    }

    try {
      // 检查是否需要AI分析
      if (!this.shouldTriggerAI(logText, context)) {
        return this.createSimpleSummary(logText, context);
      }

      logger.info('Starting AI analysis', { 
        textLength: logText.length,
        provider: this.provider,
        model: this.model
      });

      // 构建分析提示
      const prompt = this.buildAnalysisPrompt(logText, context);
      
      // 调用AI服务
      const result = await retry(
        () => withTimeout(this.callAIService(prompt), this.timeout),
        3,
        1000
      );

      // 验证和处理结果
      const processedResult = this.processAIResult(result, logText, context);
      
      logger.info('AI analysis completed', {
        summary: processedResult.summary.substring(0, 100),
        keyLinesCount: processedResult.key_lines.length,
        keyPhrasesCount: processedResult.key_phrases.length,
        confidence: processedResult.confidence
      });

      return processedResult;

    } catch (error) {
      logger.error('AI analysis failed', { error: error.message });
      return this.createFallbackSummary(logText, context, error);
    }
  }

  /**
   * 判断是否应该触发AI分析
   */
  shouldTriggerAI(logText, context) {
    const threshold = config.analysis.aiTriggerThreshold;
    
    // 文本长度检查
    if (logText.length < threshold.logLength) {
      return false;
    }

    // 错误关键词检查
    const hasErrors = threshold.errorKeywords.some(keyword => 
      logText.toLowerCase().includes(keyword)
    );

    // 警告关键词检查
    const hasWarnings = threshold.warningKeywords.some(keyword => 
      logText.toLowerCase().includes(keyword)
    );

    // 上下文检查
    const isErrorContext = context.eventType === 'command' && context.exitCode !== 0;
    const isStderrContent = context.streamType === 'stderr';

    return hasErrors || hasWarnings || isErrorContext || isStderrContent;
  }

  /**
   * 构建AI分析提示
   */
  buildAnalysisPrompt(logText, context) {
    const contextInfo = this.buildContextInfo(context);
    const truncatedText = truncateText(logText, 8000); // 限制输入长度

    return `你是一个专业的日志分析专家。请分析以下日志内容并提供结构化的分析结果。

上下文信息：
${contextInfo}

日志内容：
\`\`\`
${truncatedText}
\`\`\`

请以JSON格式返回分析结果，包含以下字段：
{
  "summary": "一句话核心问题概括（中文，不超过100字）",
  "key_lines": [关键行号数组，最多5个],
  "key_phrases": ["关键词组数组，最多5个"],
  "error_type": "错误类型（如果有）",
  "severity": "严重程度：low/medium/high/critical",
  "suggested_actions": ["建议的解决步骤数组，最多3个"],
  "confidence": 0.85
}

分析要求：
1. 重点关注错误、异常、警告信息
2. 识别Stack Trace、编译错误、运行时错误等模式
3. 提取最关键的行号和关键词
4. 给出实用的解决建议
5. 评估分析的置信度

请确保返回有效的JSON格式。`;
  }

  /**
   * 构建上下文信息
   */
  buildContextInfo(context) {
    const info = [];
    
    if (context.eventType) {
      info.push(`事件类型: ${context.eventType}`);
    }
    
    if (context.command) {
      info.push(`执行命令: ${context.command}`);
    }
    
    if (context.exitCode !== undefined) {
      info.push(`退出码: ${context.exitCode}`);
    }
    
    if (context.shell) {
      info.push(`Shell环境: ${context.shell}`);
    }
    
    if (context.workingDirectory) {
      info.push(`工作目录: ${context.workingDirectory}`);
    }
    
    if (context.streamType) {
      info.push(`输出流: ${context.streamType}`);
    }
    
    if (context.fileExtension) {
      info.push(`文件类型: ${context.fileExtension}`);
    }

    return info.length > 0 ? info.join('\n') : '无特定上下文';
  }

  /**
   * 调用AI服务
   */
  async callAIService(prompt) {
    switch (this.provider) {
      case 'gemini':
        return await this.callGeminiAPI(prompt);
      case 'openai':
        return await this.callOpenAIAPI(prompt);
      default:
        throw new Error(`Unsupported AI provider: ${this.provider}`);
    }
  }

  /**
   * 调用Gemini API
   */
  async callGeminiAPI(prompt) {
    const url = `https://generativelanguage.googleapis.com/v1beta/models/${this.model}:generateContent?key=${this.apiKey}`;
    
    const requestData = {
      contents: [{
        parts: [{
          text: prompt
        }]
      }],
      generationConfig: {
        temperature: this.temperature,
        maxOutputTokens: this.maxTokens,
        topP: 0.8,
        topK: 10
      }
    };

    const response = await axios.post(url, requestData, {
      headers: {
        'Content-Type': 'application/json'
      },
      timeout: this.timeout
    });

    if (!response.data.candidates || response.data.candidates.length === 0) {
      throw new Error('No response from Gemini API');
    }

    const content = response.data.candidates[0].content.parts[0].text;
    return this.extractJSONFromResponse(content);
  }

  /**
   * 调用OpenAI API
   */
  async callOpenAIAPI(prompt) {
    const url = 'https://api.openai.com/v1/chat/completions';
    
    const requestData = {
      model: this.model,
      messages: [
        {
          role: 'system',
          content: '你是一个专业的日志分析专家，专门分析技术日志并提供结构化的分析结果。'
        },
        {
          role: 'user',
          content: prompt
        }
      ],
      temperature: this.temperature,
      max_tokens: this.maxTokens,
      response_format: { type: 'json_object' }
    };

    const response = await axios.post(url, requestData, {
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.apiKey}`
      },
      timeout: this.timeout
    });

    if (!response.data.choices || response.data.choices.length === 0) {
      throw new Error('No response from OpenAI API');
    }

    const content = response.data.choices[0].message.content;
    return JSON.parse(content);
  }

  /**
   * 从响应中提取JSON
   */
  extractJSONFromResponse(text) {
    try {
      // 尝试直接解析
      return JSON.parse(text);
    } catch (error) {
      // 尝试提取JSON代码块
      const jsonMatch = text.match(/```json\s*([\s\S]*?)\s*```/);
      if (jsonMatch) {
        return JSON.parse(jsonMatch[1]);
      }

      // 尝试提取大括号内容
      const braceMatch = text.match(/\{[\s\S]*\}/);
      if (braceMatch) {
        return JSON.parse(braceMatch[0]);
      }

      throw new Error('Could not extract JSON from AI response');
    }
  }

  /**
   * 处理AI分析结果
   */
  processAIResult(aiResult, originalText, context) {
    const lines = originalText.split('\n');
    
    // 验证和清理结果
    const result = {
      summary: this.validateSummary(aiResult.summary),
      key_lines: this.validateKeyLines(aiResult.key_lines, lines.length),
      key_phrases: this.validateKeyPhrases(aiResult.key_phrases),
      error_type: aiResult.error_type || null,
      severity: this.validateSeverity(aiResult.severity),
      suggested_actions: this.validateSuggestedActions(aiResult.suggested_actions),
      confidence: this.validateConfidence(aiResult.confidence),
      ai_model: this.model,
      analysis_timestamp: Date.now(),
      context: context
    };

    // 提取关键行的实际内容
    result.key_line_contents = result.key_lines.map(lineNum => ({
      line_number: lineNum,
      content: lines[lineNum - 1] || ''
    }));

    return result;
  }

  /**
   * 验证摘要
   */
  validateSummary(summary) {
    if (!summary || typeof summary !== 'string') {
      return '日志分析完成，未发现明显问题';
    }
    return truncateText(summary.trim(), 200);
  }

  /**
   * 验证关键行号
   */
  validateKeyLines(keyLines, totalLines) {
    if (!Array.isArray(keyLines)) {
      return [];
    }
    
    return keyLines
      .filter(line => Number.isInteger(line) && line > 0 && line <= totalLines)
      .slice(0, 5);
  }

  /**
   * 验证关键短语
   */
  validateKeyPhrases(keyPhrases) {
    if (!Array.isArray(keyPhrases)) {
      return [];
    }
    
    return keyPhrases
      .filter(phrase => typeof phrase === 'string' && phrase.trim().length > 0)
      .map(phrase => phrase.trim())
      .slice(0, 5);
  }

  /**
   * 验证严重程度
   */
  validateSeverity(severity) {
    const validSeverities = ['low', 'medium', 'high', 'critical'];
    return validSeverities.includes(severity) ? severity : 'medium';
  }

  /**
   * 验证建议操作
   */
  validateSuggestedActions(actions) {
    if (!Array.isArray(actions)) {
      return [];
    }
    
    return actions
      .filter(action => typeof action === 'string' && action.trim().length > 0)
      .map(action => action.trim())
      .slice(0, 3);
  }

  /**
   * 验证置信度
   */
  validateConfidence(confidence) {
    const conf = parseFloat(confidence);
    if (isNaN(conf) || conf < 0 || conf > 1) {
      return 0.5;
    }
    return conf;
  }

  /**
   * 创建简单摘要（不使用AI）
   */
  createSimpleSummary(logText, context) {
    const lines = logText.split('\n');
    const summary = this.generateSimpleSummary(logText, context);
    
    return {
      summary,
      key_lines: this.findImportantLines(lines),
      key_phrases: this.extractSimpleKeyPhrases(logText),
      error_type: this.detectSimpleErrorType(logText),
      severity: this.assessSimpleSeverity(logText, context),
      suggested_actions: [],
      confidence: 0.3,
      ai_model: 'rule-based',
      analysis_timestamp: Date.now(),
      context: context,
      key_line_contents: []
    };
  }

  /**
   * 创建回退摘要
   */
  createFallbackSummary(logText, context, error = null) {
    const lines = logText.split('\n');
    const summary = error 
      ? `日志分析失败: ${error.message}` 
      : '日志内容已记录，等待进一步分析';
    
    return {
      summary,
      key_lines: [],
      key_phrases: [],
      error_type: null,
      severity: 'low',
      suggested_actions: [],
      confidence: 0.1,
      ai_model: 'fallback',
      analysis_timestamp: Date.now(),
      context: context,
      key_line_contents: [],
      error: error ? error.message : null
    };
  }

  /**
   * 生成简单摘要
   */
  generateSimpleSummary(logText, context) {
    if (context.exitCode && context.exitCode !== 0) {
      return `命令执行失败，退出码: ${context.exitCode}`;
    }
    
    if (logText.toLowerCase().includes('error')) {
      return '检测到错误信息';
    }
    
    if (logText.toLowerCase().includes('warning')) {
      return '检测到警告信息';
    }
    
    return '日志记录完成';
  }

  /**
   * 查找重要行
   */
  findImportantLines(lines) {
    const importantLines = [];
    const keywords = ['error', 'exception', 'failed', 'fatal', 'warning'];
    
    lines.forEach((line, index) => {
      const lowerLine = line.toLowerCase();
      if (keywords.some(keyword => lowerLine.includes(keyword))) {
        importantLines.push(index + 1);
      }
    });
    
    return importantLines.slice(0, 5);
  }

  /**
   * 提取简单关键短语
   */
  extractSimpleKeyPhrases(logText) {
    const phrases = [];
    const patterns = [
      /error:\s*([^.\n]+)/gi,
      /exception:\s*([^.\n]+)/gi,
      /failed:\s*([^.\n]+)/gi,
      /warning:\s*([^.\n]+)/gi
    ];
    
    for (const pattern of patterns) {
      const matches = logText.matchAll(pattern);
      for (const match of matches) {
        if (match[1]) {
          phrases.push(match[1].trim());
        }
      }
    }
    
    return phrases.slice(0, 5);
  }

  /**
   * 检测简单错误类型
   */
  detectSimpleErrorType(logText) {
    const lowerText = logText.toLowerCase();
    
    if (lowerText.includes('compilation') || lowerText.includes('syntax')) {
      return 'compilation';
    }
    if (lowerText.includes('network') || lowerText.includes('connection')) {
      return 'network';
    }
    if (lowerText.includes('permission') || lowerText.includes('access')) {
      return 'permission';
    }
    if (lowerText.includes('file') || lowerText.includes('directory')) {
      return 'filesystem';
    }
    
    return null;
  }

  /**
   * 评估简单严重程度
   */
  assessSimpleSeverity(logText, context) {
    const lowerText = logText.toLowerCase();
    
    if (lowerText.includes('fatal') || lowerText.includes('critical')) {
      return 'critical';
    }
    if (lowerText.includes('error') || (context.exitCode && context.exitCode !== 0)) {
      return 'high';
    }
    if (lowerText.includes('warning')) {
      return 'medium';
    }
    
    return 'low';
  }

  /**
   * 批量分析多个日志
   */
  async analyzeBatch(logEntries, concurrency = 3) {
    const results = [];
    
    for (let i = 0; i < logEntries.length; i += concurrency) {
      const batch = logEntries.slice(i, i + concurrency);
      const batchPromises = batch.map(entry => 
        this.analyzeLog(entry.text, entry.context)
          .then(result => ({ ...entry, analysis: result }))
          .catch(error => ({ ...entry, analysis: null, error: error.message }))
      );
      
      const batchResults = await Promise.all(batchPromises);
      results.push(...batchResults);
    }
    
    return results;
  }

  /**
   * 获取分析统计
   */
  getAnalysisStats() {
    return {
      provider: this.provider,
      model: this.model,
      isEnabled: this.isEnabled,
      maxTokens: this.maxTokens,
      temperature: this.temperature,
      timeout: this.timeout
    };
  }

  /**
   * 更新配置
   */
  updateConfig(newConfig) {
    if (newConfig.provider) this.provider = newConfig.provider;
    if (newConfig.model) this.model = newConfig.model;
    if (newConfig.maxTokens) this.maxTokens = newConfig.maxTokens;
    if (newConfig.temperature !== undefined) this.temperature = newConfig.temperature;
    if (newConfig.timeout) this.timeout = newConfig.timeout;
    
    logger.info('AI summarizer configuration updated', newConfig);
  }
}

// 创建单例实例
const aiSummarizer = new AISummarizer();

module.exports = aiSummarizer;