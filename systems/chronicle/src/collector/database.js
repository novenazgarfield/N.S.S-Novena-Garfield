const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const { createModuleLogger } = require('../shared/logger');
const config = require('../shared/config');
const { generateId, safeJsonStringify, safeJsonParse } = require('../shared/utils');

const logger = createModuleLogger('database');

class Database {
  constructor() {
    this.db = null;
    this.isInitialized = false;
  }

  /**
   * 初始化数据库连接
   */
  async init() {
    try {
      // 确保数据库目录存在
      const dbDir = path.dirname(config.database.path);
      const fs = require('fs');
      if (!fs.existsSync(dbDir)) {
        fs.mkdirSync(dbDir, { recursive: true });
      }

      // 创建数据库连接
      this.db = new sqlite3.Database(config.database.path, (err) => {
        if (err) {
          logger.error('Failed to connect to database', { error: err.message });
          throw err;
        }
        logger.info('Connected to SQLite database', { path: config.database.path });
      });

      // 启用外键约束
      await this.run('PRAGMA foreign_keys = ON');
      
      // 设置性能优化
      await this.run('PRAGMA journal_mode = WAL');
      await this.run('PRAGMA synchronous = NORMAL');
      await this.run('PRAGMA cache_size = 10000');
      await this.run('PRAGMA temp_store = MEMORY');

      // 创建表结构
      await this.createTables();
      
      this.isInitialized = true;
      logger.info('Database initialized successfully');
    } catch (error) {
      logger.error('Database initialization failed', { error: error.message });
      throw error;
    }
  }

  /**
   * 创建数据库表
   */
  async createTables() {
    const tables = [
      // 会话表
      `CREATE TABLE IF NOT EXISTS sessions (
        id TEXT PRIMARY KEY,
        project_name TEXT NOT NULL,
        project_path TEXT NOT NULL,
        start_time INTEGER NOT NULL,
        end_time INTEGER,
        status TEXT DEFAULT 'active',
        metadata TEXT,
        created_at INTEGER DEFAULT (strftime('%s', 'now')),
        updated_at INTEGER DEFAULT (strftime('%s', 'now'))
      )`,

      // 文件事件表
      `CREATE TABLE IF NOT EXISTS file_events (
        id TEXT PRIMARY KEY,
        session_id TEXT NOT NULL,
        event_type TEXT NOT NULL,
        file_path TEXT NOT NULL,
        file_name TEXT NOT NULL,
        file_extension TEXT,
        file_size INTEGER,
        timestamp INTEGER NOT NULL,
        metadata TEXT,
        FOREIGN KEY (session_id) REFERENCES sessions (id) ON DELETE CASCADE
      )`,

      // 窗口事件表
      `CREATE TABLE IF NOT EXISTS window_events (
        id TEXT PRIMARY KEY,
        session_id TEXT NOT NULL,
        window_title TEXT,
        app_name TEXT,
        app_path TEXT,
        pid INTEGER,
        timestamp INTEGER NOT NULL,
        duration INTEGER,
        metadata TEXT,
        FOREIGN KEY (session_id) REFERENCES sessions (id) ON DELETE CASCADE
      )`,

      // 命令事件表
      `CREATE TABLE IF NOT EXISTS command_events (
        id TEXT PRIMARY KEY,
        session_id TEXT NOT NULL,
        command TEXT NOT NULL,
        shell TEXT,
        working_directory TEXT,
        exit_code INTEGER,
        start_time INTEGER NOT NULL,
        end_time INTEGER,
        duration INTEGER,
        stdout TEXT,
        stderr TEXT,
        environment TEXT,
        metadata TEXT,
        FOREIGN KEY (session_id) REFERENCES sessions (id) ON DELETE CASCADE
      )`,

      // 分析结果表
      `CREATE TABLE IF NOT EXISTS analysis_results (
        id TEXT PRIMARY KEY,
        session_id TEXT NOT NULL,
        event_id TEXT,
        event_type TEXT NOT NULL,
        analysis_type TEXT NOT NULL,
        summary TEXT,
        key_lines TEXT,
        key_phrases TEXT,
        confidence REAL,
        ai_model TEXT,
        created_at INTEGER DEFAULT (strftime('%s', 'now')),
        metadata TEXT,
        FOREIGN KEY (session_id) REFERENCES sessions (id) ON DELETE CASCADE
      )`,

      // 报告表
      `CREATE TABLE IF NOT EXISTS reports (
        id TEXT PRIMARY KEY,
        session_id TEXT NOT NULL,
        report_type TEXT NOT NULL,
        title TEXT,
        content TEXT NOT NULL,
        format TEXT DEFAULT 'json',
        generated_at INTEGER DEFAULT (strftime('%s', 'now')),
        metadata TEXT,
        FOREIGN KEY (session_id) REFERENCES sessions (id) ON DELETE CASCADE
      )`
    ];

    for (const table of tables) {
      await this.run(table);
    }

    // 创建索引
    const indexes = [
      'CREATE INDEX IF NOT EXISTS idx_sessions_status ON sessions (status)',
      'CREATE INDEX IF NOT EXISTS idx_sessions_project ON sessions (project_name)',
      'CREATE INDEX IF NOT EXISTS idx_file_events_session ON file_events (session_id)',
      'CREATE INDEX IF NOT EXISTS idx_file_events_timestamp ON file_events (timestamp)',
      'CREATE INDEX IF NOT EXISTS idx_window_events_session ON window_events (session_id)',
      'CREATE INDEX IF NOT EXISTS idx_window_events_timestamp ON window_events (timestamp)',
      'CREATE INDEX IF NOT EXISTS idx_command_events_session ON command_events (session_id)',
      'CREATE INDEX IF NOT EXISTS idx_command_events_timestamp ON command_events (start_time)',
      'CREATE INDEX IF NOT EXISTS idx_analysis_results_session ON analysis_results (session_id)',
      'CREATE INDEX IF NOT EXISTS idx_reports_session ON reports (session_id)'
    ];

    for (const index of indexes) {
      await this.run(index);
    }

    logger.info('Database tables and indexes created');
  }

  /**
   * 执行SQL语句
   */
  run(sql, params = []) {
    return new Promise((resolve, reject) => {
      this.db.run(sql, params, function(err) {
        if (err) {
          logger.error('SQL execution failed', { sql, params, error: err.message });
          reject(err);
        } else {
          resolve({ id: this.lastID, changes: this.changes });
        }
      });
    });
  }

  /**
   * 查询单行数据
   */
  get(sql, params = []) {
    return new Promise((resolve, reject) => {
      this.db.get(sql, params, (err, row) => {
        if (err) {
          logger.error('SQL query failed', { sql, params, error: err.message });
          reject(err);
        } else {
          resolve(row);
        }
      });
    });
  }

  /**
   * 查询多行数据
   */
  all(sql, params = []) {
    return new Promise((resolve, reject) => {
      this.db.all(sql, params, (err, rows) => {
        if (err) {
          logger.error('SQL query failed', { sql, params, error: err.message });
          reject(err);
        } else {
          resolve(rows);
        }
      });
    });
  }

  /**
   * 创建会话
   */
  async createSession(projectName, projectPath, metadata = {}) {
    const sessionId = generateId('session');
    const now = Date.now();
    
    await this.run(
      `INSERT INTO sessions (id, project_name, project_path, start_time, metadata)
       VALUES (?, ?, ?, ?, ?)`,
      [sessionId, projectName, projectPath, now, safeJsonStringify(metadata)]
    );

    logger.audit('Session created', { sessionId, projectName, projectPath });
    return sessionId;
  }

  /**
   * 结束会话
   */
  async endSession(sessionId) {
    const now = Date.now();
    
    const result = await this.run(
      `UPDATE sessions SET end_time = ?, status = 'completed', updated_at = ?
       WHERE id = ? AND status = 'active'`,
      [now, now, sessionId]
    );

    if (result.changes > 0) {
      logger.audit('Session ended', { sessionId });
      return true;
    }
    return false;
  }

  /**
   * 获取会话信息
   */
  async getSession(sessionId) {
    const session = await this.get(
      'SELECT * FROM sessions WHERE id = ?',
      [sessionId]
    );

    if (session && session.metadata) {
      session.metadata = safeJsonParse(session.metadata, {});
    }

    return session;
  }

  /**
   * 获取活动会话列表
   */
  async getActiveSessions() {
    const sessions = await this.all(
      'SELECT * FROM sessions WHERE status = "active" ORDER BY start_time DESC'
    );

    return sessions.map(session => ({
      ...session,
      metadata: safeJsonParse(session.metadata, {})
    }));
  }

  /**
   * 记录文件事件
   */
  async recordFileEvent(sessionId, eventType, filePath, metadata = {}) {
    const eventId = generateId('file');
    const fileName = path.basename(filePath);
    const fileExtension = path.extname(filePath).slice(1);
    const now = Date.now();

    // 获取文件大小
    let fileSize = null;
    try {
      const fs = require('fs');
      const stats = fs.statSync(filePath);
      fileSize = stats.size;
    } catch (error) {
      // 文件可能已被删除
    }

    await this.run(
      `INSERT INTO file_events (id, session_id, event_type, file_path, file_name, 
       file_extension, file_size, timestamp, metadata)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)`,
      [eventId, sessionId, eventType, filePath, fileName, fileExtension, 
       fileSize, now, safeJsonStringify(metadata)]
    );

    return eventId;
  }

  /**
   * 记录窗口事件
   */
  async recordWindowEvent(sessionId, windowInfo, duration = null, metadata = {}) {
    const eventId = generateId('window');
    const now = Date.now();

    await this.run(
      `INSERT INTO window_events (id, session_id, window_title, app_name, app_path, 
       pid, timestamp, duration, metadata)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)`,
      [eventId, sessionId, windowInfo.title, windowInfo.owner?.name, 
       windowInfo.owner?.path, windowInfo.owner?.pid, now, duration, 
       safeJsonStringify(metadata)]
    );

    return eventId;
  }

  /**
   * 记录命令事件
   */
  async recordCommandEvent(sessionId, commandInfo, metadata = {}) {
    const eventId = generateId('command');
    
    await this.run(
      `INSERT INTO command_events (id, session_id, command, shell, working_directory,
       exit_code, start_time, end_time, duration, stdout, stderr, environment, metadata)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
      [eventId, sessionId, commandInfo.command, commandInfo.shell, 
       commandInfo.workingDirectory, commandInfo.exitCode, commandInfo.startTime,
       commandInfo.endTime, commandInfo.duration, commandInfo.stdout, 
       commandInfo.stderr, safeJsonStringify(commandInfo.environment || {}),
       safeJsonStringify(metadata)]
    );

    return eventId;
  }

  /**
   * 保存分析结果
   */
  async saveAnalysisResult(sessionId, eventId, eventType, analysisType, result, metadata = {}) {
    const resultId = generateId('analysis');
    
    await this.run(
      `INSERT INTO analysis_results (id, session_id, event_id, event_type, 
       analysis_type, summary, key_lines, key_phrases, confidence, ai_model, metadata)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
      [resultId, sessionId, eventId, eventType, analysisType, result.summary,
       safeJsonStringify(result.key_lines || []), 
       safeJsonStringify(result.key_phrases || []),
       result.confidence, result.ai_model, safeJsonStringify(metadata)]
    );

    return resultId;
  }

  /**
   * 保存报告
   */
  async saveReport(sessionId, reportType, title, content, format = 'json', metadata = {}) {
    const reportId = generateId('report');
    
    await this.run(
      `INSERT INTO reports (id, session_id, report_type, title, content, format, metadata)
       VALUES (?, ?, ?, ?, ?, ?, ?)`,
      [reportId, sessionId, reportType, title, content, format, safeJsonStringify(metadata)]
    );

    return reportId;
  }

  /**
   * 获取会话的所有事件
   */
  async getSessionEvents(sessionId, eventType = null, limit = null) {
    let sql = `
      SELECT 'file' as type, id, timestamp, event_type, file_path as path, metadata
      FROM file_events WHERE session_id = ?
      UNION ALL
      SELECT 'window' as type, id, timestamp, app_name as event_type, window_title as path, metadata
      FROM window_events WHERE session_id = ?
      UNION ALL
      SELECT 'command' as type, id, start_time as timestamp, shell as event_type, command as path, metadata
      FROM command_events WHERE session_id = ?
    `;

    const params = [sessionId, sessionId, sessionId];

    if (eventType) {
      sql += ' WHERE type = ?';
      params.push(eventType);
    }

    sql += ' ORDER BY timestamp DESC';

    if (limit) {
      sql += ' LIMIT ?';
      params.push(limit);
    }

    const events = await this.all(sql, params);
    
    return events.map(event => ({
      ...event,
      metadata: safeJsonParse(event.metadata, {})
    }));
  }

  /**
   * 获取会话统计信息
   */
  async getSessionStats(sessionId) {
    const [fileCount, windowCount, commandCount] = await Promise.all([
      this.get('SELECT COUNT(*) as count FROM file_events WHERE session_id = ?', [sessionId]),
      this.get('SELECT COUNT(*) as count FROM window_events WHERE session_id = ?', [sessionId]),
      this.get('SELECT COUNT(*) as count FROM command_events WHERE session_id = ?', [sessionId])
    ]);

    return {
      fileEvents: fileCount.count,
      windowEvents: windowCount.count,
      commandEvents: commandCount.count,
      totalEvents: fileCount.count + windowCount.count + commandCount.count
    };
  }

  /**
   * 清理旧数据
   */
  async cleanup(daysToKeep = 30) {
    const cutoffTime = Date.now() - (daysToKeep * 24 * 60 * 60 * 1000);
    
    const result = await this.run(
      'DELETE FROM sessions WHERE start_time < ? AND status != "active"',
      [cutoffTime]
    );

    logger.info('Database cleanup completed', { 
      deletedSessions: result.changes,
      daysToKeep 
    });

    return result.changes;
  }

  /**
   * 关闭数据库连接
   */
  async close() {
    if (this.db) {
      return new Promise((resolve) => {
        this.db.close((err) => {
          if (err) {
            logger.error('Error closing database', { error: err.message });
          } else {
            logger.info('Database connection closed');
          }
          resolve();
        });
      });
    }
  }
}

// 创建单例实例
const database = new Database();

module.exports = database;