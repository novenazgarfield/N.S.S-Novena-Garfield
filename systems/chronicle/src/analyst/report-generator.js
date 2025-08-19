const moment = require('moment');
const { createModuleLogger } = require('../shared/logger');
const { formatDuration, formatBytes, safeJsonStringify } = require('../shared/utils');
const config = require('../shared/config');
const database = require('../collector/database');
const patternRecognizer = require('./pattern-recognizer');
const aiSummarizer = require('./ai-summarizer');

const logger = createModuleLogger('report-generator');

class ReportGenerator {
  constructor() {
    this.reportConfig = config.analysis.report;
  }

  /**
   * 生成会话报告
   */
  async generateSessionReport(sessionId, options = {}) {
    try {
      logger.info('Generating session report', { sessionId, options });

      // 获取会话信息
      const session = await database.getSession(sessionId);
      if (!session) {
        throw new Error(`Session not found: ${sessionId}`);
      }

      // 获取所有事件
      const events = await database.getSessionEvents(sessionId);
      
      // 获取统计信息
      const stats = await database.getSessionStats(sessionId);

      // 生成报告
      const report = await this.buildReport(session, events, stats, options);

      // 保存报告到数据库
      const reportId = await database.saveReport(
        sessionId,
        options.type || 'comprehensive',
        report.title,
        safeJsonStringify(report, 2),
        options.format || 'json',
        { generatedAt: Date.now(), options }
      );

      logger.info('Session report generated', { 
        sessionId, 
        reportId, 
        eventsProcessed: events.length 
      });

      return { reportId, report };

    } catch (error) {
      logger.error('Failed to generate session report', { 
        sessionId, 
        error: error.message 
      });
      throw error;
    }
  }

  /**
   * 构建报告
   */
  async buildReport(session, events, stats, options) {
    const reportType = options.type || 'comprehensive';
    
    switch (reportType) {
      case 'summary':
        return await this.buildSummaryReport(session, events, stats, options);
      case 'detailed':
        return await this.buildDetailedReport(session, events, stats, options);
      case 'error-focused':
        return await this.buildErrorFocusedReport(session, events, stats, options);
      case 'comprehensive':
      default:
        return await this.buildComprehensiveReport(session, events, stats, options);
    }
  }

  /**
   * 构建综合报告
   */
  async buildComprehensiveReport(session, events, stats, options) {
    const startTime = Date.now();

    // 基本信息
    const basicInfo = this.buildBasicInfo(session, stats);

    // 时间线分析
    const timeline = this.buildTimeline(events);

    // 事件分析
    const eventAnalysis = await this.analyzeEvents(events);

    // 模式识别
    const patternAnalysis = await this.analyzePatterns(events);

    // AI分析（如果启用）
    const aiAnalysis = await this.performAIAnalysis(events, session);

    // 问题和建议
    const issuesAndSuggestions = this.generateIssuesAndSuggestions(
      eventAnalysis, 
      patternAnalysis, 
      aiAnalysis
    );

    // 性能指标
    const performanceMetrics = this.calculatePerformanceMetrics(events, session);

    // 构建最终报告
    const report = {
      title: `Chronicle - ${session.project_name} 实验报告`,
      metadata: {
        sessionId: session.id,
        projectName: session.project_name,
        projectPath: session.project_path,
        generatedAt: Date.now(),
        generationTime: Date.now() - startTime,
        reportType: 'comprehensive',
        version: '1.0.0'
      },
      basicInfo,
      timeline,
      eventAnalysis,
      patternAnalysis,
      aiAnalysis,
      issuesAndSuggestions,
      performanceMetrics,
      rawData: options.includeRawData ? { events, stats } : null
    };

    return report;
  }

  /**
   * 构建摘要报告
   */
  async buildSummaryReport(session, events, stats, options) {
    const duration = session.end_time ? 
      session.end_time - session.start_time : 
      Date.now() - session.start_time;

    // 关键指标
    const keyMetrics = {
      duration: formatDuration(duration),
      totalEvents: stats.totalEvents,
      fileEvents: stats.fileEvents,
      windowEvents: stats.windowEvents,
      commandEvents: stats.commandEvents
    };

    // 快速分析
    const quickAnalysis = await this.performQuickAnalysis(events);

    return {
      title: `${session.project_name} - 快速摘要`,
      metadata: {
        sessionId: session.id,
        projectName: session.project_name,
        generatedAt: Date.now(),
        reportType: 'summary'
      },
      keyMetrics,
      quickAnalysis,
      status: session.status,
      timeRange: {
        start: moment(session.start_time).format('YYYY-MM-DD HH:mm:ss'),
        end: session.end_time ? 
          moment(session.end_time).format('YYYY-MM-DD HH:mm:ss') : 
          '进行中'
      }
    };
  }

  /**
   * 构建详细报告
   */
  async buildDetailedReport(session, events, stats, options) {
    const comprehensive = await this.buildComprehensiveReport(session, events, stats, options);
    
    // 添加详细的事件列表
    const detailedEvents = await this.buildDetailedEventList(events);
    
    // 添加文件变更历史
    const fileHistory = this.buildFileChangeHistory(events);
    
    // 添加命令执行历史
    const commandHistory = this.buildCommandHistory(events);

    return {
      ...comprehensive,
      title: `${session.project_name} - 详细报告`,
      metadata: {
        ...comprehensive.metadata,
        reportType: 'detailed'
      },
      detailedEvents,
      fileHistory,
      commandHistory
    };
  }

  /**
   * 构建错误聚焦报告
   */
  async buildErrorFocusedReport(session, events, stats, options) {
    // 过滤错误相关事件
    const errorEvents = events.filter(event => 
      this.isErrorEvent(event)
    );

    // 错误分析
    const errorAnalysis = await this.analyzeErrors(errorEvents);

    // 错误模式识别
    const errorPatterns = await this.analyzeErrorPatterns(errorEvents);

    // AI错误分析
    const aiErrorAnalysis = await this.performAIErrorAnalysis(errorEvents);

    return {
      title: `${session.project_name} - 错误分析报告`,
      metadata: {
        sessionId: session.id,
        projectName: session.project_name,
        generatedAt: Date.now(),
        reportType: 'error-focused',
        totalErrors: errorEvents.length
      },
      errorSummary: {
        totalErrors: errorEvents.length,
        errorTypes: this.categorizeErrors(errorEvents),
        severity: this.assessOverallSeverity(errorEvents)
      },
      errorAnalysis,
      errorPatterns,
      aiErrorAnalysis,
      errorEvents: errorEvents.slice(0, 20) // 限制显示数量
    };
  }

  /**
   * 构建基本信息
   */
  buildBasicInfo(session, stats) {
    const duration = session.end_time ? 
      session.end_time - session.start_time : 
      Date.now() - session.start_time;

    return {
      projectName: session.project_name,
      projectPath: session.project_path,
      sessionId: session.id,
      status: session.status,
      duration: formatDuration(duration),
      timeRange: {
        start: moment(session.start_time).format('YYYY-MM-DD HH:mm:ss'),
        end: session.end_time ? 
          moment(session.end_time).format('YYYY-MM-DD HH:mm:ss') : 
          '进行中'
      },
      eventCounts: {
        total: stats.totalEvents,
        files: stats.fileEvents,
        windows: stats.windowEvents,
        commands: stats.commandEvents
      }
    };
  }

  /**
   * 构建时间线
   */
  buildTimeline(events) {
    const timeline = events
      .sort((a, b) => a.timestamp - b.timestamp)
      .map(event => ({
        timestamp: moment(event.timestamp).format('HH:mm:ss'),
        type: event.type,
        event: this.formatEventForTimeline(event),
        importance: this.calculateEventImportance(event)
      }));

    // 提取关键时间点
    const keyMoments = timeline
      .filter(item => item.importance > 0.7)
      .slice(0, 10);

    return {
      totalEvents: timeline.length,
      keyMoments,
      fullTimeline: timeline.slice(0, 100) // 限制显示数量
    };
  }

  /**
   * 分析事件
   */
  async analyzeEvents(events) {
    const analysis = {
      byType: {},
      byHour: {},
      patterns: [],
      anomalies: []
    };

    // 按类型分组
    events.forEach(event => {
      if (!analysis.byType[event.type]) {
        analysis.byType[event.type] = 0;
      }
      analysis.byType[event.type]++;
    });

    // 按小时分组
    events.forEach(event => {
      const hour = moment(event.timestamp).format('HH');
      if (!analysis.byHour[hour]) {
        analysis.byHour[hour] = 0;
      }
      analysis.byHour[hour]++;
    });

    // 检测模式
    analysis.patterns = this.detectEventPatterns(events);

    // 检测异常
    analysis.anomalies = this.detectAnomalies(events);

    return analysis;
  }

  /**
   * 分析模式
   */
  async analyzePatterns(events) {
    const patterns = [];

    // 分析命令事件的输出
    const commandEvents = events.filter(e => e.type === 'command');
    
    for (const event of commandEvents) {
      try {
        // 获取完整的命令信息
        const commandData = await database.get(
          'SELECT * FROM command_events WHERE id = ?',
          [event.id]
        );

        if (commandData && (commandData.stderr || commandData.stdout)) {
          const text = (commandData.stderr || '') + '\n' + (commandData.stdout || '');
          const patternResult = patternRecognizer.analyzeText(text, {
            eventType: 'command',
            command: commandData.command,
            exitCode: commandData.exit_code
          });

          if (patternResult.patterns.length > 0) {
            patterns.push({
              eventId: event.id,
              command: commandData.command,
              patterns: patternResult.patterns,
              severity: patternResult.severity,
              confidence: patternResult.confidence
            });
          }
        }
      } catch (error) {
        logger.warn('Failed to analyze pattern for event', { 
          eventId: event.id, 
          error: error.message 
        });
      }
    }

    return {
      totalPatterns: patterns.length,
      severityDistribution: this.calculateSeverityDistribution(patterns),
      topPatterns: patterns
        .sort((a, b) => b.confidence - a.confidence)
        .slice(0, 10)
    };
  }

  /**
   * 执行AI分析
   */
  async performAIAnalysis(events, session) {
    if (!aiSummarizer.isEnabled) {
      return { enabled: false, message: 'AI analysis is disabled' };
    }

    try {
      const analysisResults = [];
      
      // 分析错误事件
      const errorEvents = events.filter(e => this.isErrorEvent(e));
      
      for (const event of errorEvents.slice(0, 5)) { // 限制分析数量
        try {
          const eventData = await this.getEventData(event);
          if (eventData && eventData.text) {
            const analysis = await aiSummarizer.analyzeLog(eventData.text, {
              eventType: event.type,
              sessionId: session.id,
              projectName: session.project_name
            });
            
            analysisResults.push({
              eventId: event.id,
              analysis
            });
          }
        } catch (error) {
          logger.warn('AI analysis failed for event', { 
            eventId: event.id, 
            error: error.message 
          });
        }
      }

      return {
        enabled: true,
        totalAnalyzed: analysisResults.length,
        results: analysisResults,
        summary: this.generateAISummary(analysisResults)
      };

    } catch (error) {
      logger.error('AI analysis failed', { error: error.message });
      return { 
        enabled: true, 
        error: error.message,
        totalAnalyzed: 0,
        results: []
      };
    }
  }

  /**
   * 生成问题和建议
   */
  generateIssuesAndSuggestions(eventAnalysis, patternAnalysis, aiAnalysis) {
    const issues = [];
    const suggestions = [];

    // 基于事件分析的问题
    if (eventAnalysis.anomalies.length > 0) {
      issues.push({
        type: 'anomaly',
        severity: 'medium',
        description: `检测到 ${eventAnalysis.anomalies.length} 个异常事件`,
        details: eventAnalysis.anomalies.slice(0, 3)
      });
    }

    // 基于模式分析的问题
    const highSeverityPatterns = patternAnalysis.topPatterns?.filter(p => 
      p.severity === 'high' || p.severity === 'critical'
    ) || [];

    if (highSeverityPatterns.length > 0) {
      issues.push({
        type: 'pattern',
        severity: 'high',
        description: `发现 ${highSeverityPatterns.length} 个高严重性问题模式`,
        details: highSeverityPatterns.slice(0, 3)
      });

      suggestions.push({
        type: 'pattern-based',
        priority: 'high',
        description: '建议优先解决检测到的错误模式',
        actions: [
          '检查错误日志中的具体错误信息',
          '验证相关配置和依赖',
          '考虑回滚到上一个稳定版本'
        ]
      });
    }

    // 基于AI分析的建议
    if (aiAnalysis.enabled && aiAnalysis.results) {
      const aiSuggestions = aiAnalysis.results
        .filter(r => r.analysis.suggested_actions && r.analysis.suggested_actions.length > 0)
        .slice(0, 3);

      aiSuggestions.forEach(result => {
        suggestions.push({
          type: 'ai-generated',
          priority: result.analysis.severity,
          description: result.analysis.summary,
          actions: result.analysis.suggested_actions
        });
      });
    }

    // 通用建议
    if (issues.length === 0) {
      suggestions.push({
        type: 'general',
        priority: 'low',
        description: '会话运行正常，建议继续监控',
        actions: [
          '定期检查日志输出',
          '监控系统资源使用情况',
          '保持代码和依赖的更新'
        ]
      });
    }

    return {
      issues: issues.slice(0, 10),
      suggestions: suggestions.slice(0, 10),
      summary: {
        totalIssues: issues.length,
        highPriorityIssues: issues.filter(i => i.severity === 'high' || i.severity === 'critical').length,
        totalSuggestions: suggestions.length
      }
    };
  }

  /**
   * 计算性能指标
   */
  calculatePerformanceMetrics(events, session) {
    const duration = session.end_time ? 
      session.end_time - session.start_time : 
      Date.now() - session.start_time;

    const metrics = {
      sessionDuration: formatDuration(duration),
      eventsPerMinute: Math.round((events.length / duration) * 60000),
      averageEventInterval: events.length > 1 ? 
        formatDuration(duration / events.length) : 'N/A'
    };

    // 命令执行性能
    const commandEvents = events.filter(e => e.type === 'command');
    if (commandEvents.length > 0) {
      // 这里需要从数据库获取详细的命令信息来计算执行时间
      metrics.commandMetrics = {
        totalCommands: commandEvents.length,
        averageCommandsPerHour: Math.round((commandEvents.length / duration) * 3600000)
      };
    }

    // 文件活动性能
    const fileEvents = events.filter(e => e.type === 'file');
    if (fileEvents.length > 0) {
      metrics.fileMetrics = {
        totalFileEvents: fileEvents.length,
        averageFileEventsPerHour: Math.round((fileEvents.length / duration) * 3600000)
      };
    }

    return metrics;
  }

  /**
   * 辅助方法
   */

  formatEventForTimeline(event) {
    switch (event.type) {
      case 'file':
        return `${event.event_type}: ${event.path}`;
      case 'window':
        return `窗口切换: ${event.path}`;
      case 'command':
        return `命令: ${event.path}`;
      default:
        return `${event.type}: ${event.path}`;
    }
  }

  calculateEventImportance(event) {
    // 基于事件类型和内容计算重要性
    let importance = 0.5;

    if (event.type === 'command') {
      importance += 0.3;
    }

    // 可以根据更多条件调整重要性
    return Math.min(importance, 1);
  }

  isErrorEvent(event) {
    // 判断是否为错误事件的逻辑
    if (event.type === 'command') {
      // 需要检查退出码或错误输出
      return true; // 简化实现
    }
    return false;
  }

  async getEventData(event) {
    // 根据事件类型获取详细数据
    try {
      switch (event.type) {
        case 'command':
          const commandData = await database.get(
            'SELECT * FROM command_events WHERE id = ?',
            [event.id]
          );
          return {
            text: (commandData.stderr || '') + '\n' + (commandData.stdout || ''),
            command: commandData.command,
            exitCode: commandData.exit_code
          };
        default:
          return null;
      }
    } catch (error) {
      logger.error('Failed to get event data', { eventId: event.id, error: error.message });
      return null;
    }
  }

  detectEventPatterns(events) {
    // 检测事件模式的简化实现
    return [];
  }

  detectAnomalies(events) {
    // 检测异常的简化实现
    return [];
  }

  calculateSeverityDistribution(patterns) {
    const distribution = { low: 0, medium: 0, high: 0, critical: 0 };
    patterns.forEach(p => {
      if (distribution[p.severity] !== undefined) {
        distribution[p.severity]++;
      }
    });
    return distribution;
  }

  generateAISummary(analysisResults) {
    if (analysisResults.length === 0) {
      return '未进行AI分析';
    }

    const summaries = analysisResults.map(r => r.analysis.summary);
    return `AI分析了 ${analysisResults.length} 个事件，主要发现：${summaries.slice(0, 3).join('; ')}`;
  }

  async performQuickAnalysis(events) {
    const errorCount = events.filter(e => this.isErrorEvent(e)).length;
    const fileChangeCount = events.filter(e => e.type === 'file').length;
    const commandCount = events.filter(e => e.type === 'command').length;

    return {
      summary: `处理了 ${events.length} 个事件`,
      highlights: [
        `${fileChangeCount} 个文件变更`,
        `${commandCount} 个命令执行`,
        `${errorCount} 个潜在问题`
      ],
      status: errorCount > 0 ? 'warning' : 'success'
    };
  }

  /**
   * 导出报告为不同格式
   */
  async exportReport(report, format = 'json') {
    switch (format.toLowerCase()) {
      case 'json':
        return safeJsonStringify(report, 2);
      case 'markdown':
        return this.convertToMarkdown(report);
      case 'html':
        return this.convertToHTML(report);
      default:
        throw new Error(`Unsupported export format: ${format}`);
    }
  }

  /**
   * 转换为Markdown格式
   */
  convertToMarkdown(report) {
    let markdown = `# ${report.title}\n\n`;
    
    if (report.metadata) {
      markdown += `**生成时间**: ${moment(report.metadata.generatedAt).format('YYYY-MM-DD HH:mm:ss')}\n`;
      markdown += `**项目**: ${report.metadata.projectName}\n`;
      markdown += `**会话ID**: ${report.metadata.sessionId}\n\n`;
    }

    if (report.basicInfo) {
      markdown += `## 基本信息\n\n`;
      markdown += `- **状态**: ${report.basicInfo.status}\n`;
      markdown += `- **持续时间**: ${report.basicInfo.duration}\n`;
      markdown += `- **总事件数**: ${report.basicInfo.eventCounts.total}\n\n`;
    }

    if (report.issuesAndSuggestions) {
      markdown += `## 问题和建议\n\n`;
      
      if (report.issuesAndSuggestions.issues.length > 0) {
        markdown += `### 发现的问题\n\n`;
        report.issuesAndSuggestions.issues.forEach((issue, index) => {
          markdown += `${index + 1}. **${issue.description}** (${issue.severity})\n`;
        });
        markdown += '\n';
      }

      if (report.issuesAndSuggestions.suggestions.length > 0) {
        markdown += `### 建议\n\n`;
        report.issuesAndSuggestions.suggestions.forEach((suggestion, index) => {
          markdown += `${index + 1}. ${suggestion.description}\n`;
          if (suggestion.actions) {
            suggestion.actions.forEach(action => {
              markdown += `   - ${action}\n`;
            });
          }
        });
      }
    }

    return markdown;
  }

  /**
   * 转换为HTML格式
   */
  convertToHTML(report) {
    // HTML转换的简化实现
    return `
<!DOCTYPE html>
<html>
<head>
    <title>${report.title}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .header { border-bottom: 2px solid #333; padding-bottom: 20px; }
        .section { margin: 20px 0; }
        .issue { background: #fff3cd; padding: 10px; margin: 10px 0; border-radius: 5px; }
        .suggestion { background: #d1ecf1; padding: 10px; margin: 10px 0; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>${report.title}</h1>
        <p>生成时间: ${report.metadata ? moment(report.metadata.generatedAt).format('YYYY-MM-DD HH:mm:ss') : ''}</p>
    </div>
    
    <div class="section">
        <h2>基本信息</h2>
        <p>项目: ${report.metadata?.projectName || 'N/A'}</p>
        <p>状态: ${report.basicInfo?.status || 'N/A'}</p>
        <p>持续时间: ${report.basicInfo?.duration || 'N/A'}</p>
    </div>
    
    ${report.issuesAndSuggestions ? `
    <div class="section">
        <h2>问题和建议</h2>
        ${report.issuesAndSuggestions.issues.map(issue => 
          `<div class="issue"><strong>${issue.description}</strong> (${issue.severity})</div>`
        ).join('')}
        
        ${report.issuesAndSuggestions.suggestions.map(suggestion => 
          `<div class="suggestion">${suggestion.description}</div>`
        ).join('')}
    </div>
    ` : ''}
</body>
</html>`;
  }
}

// 创建单例实例
const reportGenerator = new ReportGenerator();

module.exports = reportGenerator;