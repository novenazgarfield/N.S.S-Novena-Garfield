/**
 * 🛡️ Chronicle黑匣子与免疫系统 (Black Box & Immune System)
 * ========================================================
 * 
 * 从RAG系统剥离的"工程大脑" - 专门处理故障记录和免疫系统
 * - 独立的故障数据库 (failure_log.db)
 * - 自动伤害记录仪 (Auto Damage Recorder)
 * - 免疫系统构建 (Immune System Builder)
 * - 故障模式识别与预防
 * 
 * Author: N.S.S-Novena-Garfield Project
 * Version: 2.0.0 - "Chronicle Genesis Federation"
 */

const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const fs = require('fs');
const crypto = require('crypto');
const logger = require('../shared/logger');

// 故障状态枚举
const FailureStatus = {
  DETECTED: 'detected',
  ANALYZING: 'analyzing', 
  FIXING: 'fixing',
  FIXED: 'fixed',
  FAILED: 'failed',
  IMMUNE: 'immune'
};

// 系统来源枚举
const SystemSource = {
  RAG_SYSTEM: 'rag_system',
  CHRONICLE: 'chronicle',
  TRINITY_CHUNKER: 'trinity_chunker',
  MEMORY_NEBULA: 'memory_nebula',
  SHIELDS_OF_ORDER: 'shields_of_order',
  FIRE_CONTROL: 'fire_control',
  INTELLIGENCE_BRAIN: 'intelligence_brain',
  UNKNOWN: 'unknown'
};

// 故障严重程度
const FailureSeverity = {
  LOW: 'low',
  MEDIUM: 'medium', 
  HIGH: 'high',
  CRITICAL: 'critical'
};

class FailureRecord {
  constructor({
    id = null,
    timestamp = new Date(),
    source = SystemSource.UNKNOWN,
    function_name = '',
    error_type = '',
    error_message = '',
    stack_trace = '',
    context = {},
    severity = FailureSeverity.MEDIUM,
    status = FailureStatus.DETECTED,
    healing_attempts = 0,
    healing_strategy = null,
    resolution_notes = '',
    immune_signature = null
  } = {}) {
    this.id = id;
    this.timestamp = timestamp;
    this.source = source;
    this.function_name = function_name;
    this.error_type = error_type;
    this.error_message = error_message;
    this.stack_trace = stack_trace;
    this.context = context;
    this.severity = severity;
    this.status = status;
    this.healing_attempts = healing_attempts;
    this.healing_strategy = healing_strategy;
    this.resolution_notes = resolution_notes;
    this.immune_signature = immune_signature || this.generateImmuneSignature();
  }

  generateImmuneSignature() {
    const signature_data = `${this.source}:${this.function_name}:${this.error_type}:${this.error_message}`;
    return crypto.createHash('md5').update(signature_data).digest('hex');
  }
}

class ChronicleBlackBox {
  constructor(db_path = null) {
    this.db_path = db_path || path.join(__dirname, '../../data/chronicle_failures.db');
    this.db = null;
    this.immune_cache = new Map();
    this.failure_patterns = new Map();
    
    this.initializeDatabase();
    logger.info('🛡️ Chronicle黑匣子系统已启动 - 中央医院开始运营');
  }

  initializeDatabase() {
    try {
      // 确保数据库目录存在
      const dbDir = path.dirname(this.db_path);
      if (!fs.existsSync(dbDir)) {
        fs.mkdirSync(dbDir, { recursive: true });
      }

      this.db = new sqlite3.Database(this.db_path);
      
      // 创建故障记录表
      this.db.run(`
        CREATE TABLE IF NOT EXISTS failure_records (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          timestamp TEXT NOT NULL,
          source TEXT NOT NULL,
          function_name TEXT NOT NULL,
          error_type TEXT NOT NULL,
          error_message TEXT NOT NULL,
          stack_trace TEXT,
          context TEXT,
          severity TEXT NOT NULL,
          status TEXT NOT NULL,
          healing_attempts INTEGER DEFAULT 0,
          healing_strategy TEXT,
          resolution_notes TEXT,
          immune_signature TEXT NOT NULL,
          created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
          updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
      `);

      // 创建免疫系统表
      this.db.run(`
        CREATE TABLE IF NOT EXISTS immune_system (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          immune_signature TEXT UNIQUE NOT NULL,
          source TEXT NOT NULL,
          function_name TEXT NOT NULL,
          error_pattern TEXT NOT NULL,
          prevention_strategy TEXT,
          success_rate REAL DEFAULT 0.0,
          last_triggered DATETIME,
          trigger_count INTEGER DEFAULT 0,
          created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
          updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
      `);

      // 创建系统健康度表
      this.db.run(`
        CREATE TABLE IF NOT EXISTS system_health (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          source TEXT NOT NULL,
          health_score REAL NOT NULL,
          total_failures INTEGER DEFAULT 0,
          resolved_failures INTEGER DEFAULT 0,
          immune_responses INTEGER DEFAULT 0,
          last_failure DATETIME,
          last_healing DATETIME,
          created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
          updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
      `);

      logger.info('🛡️ Chronicle黑匣子数据库初始化完成');
    } catch (error) {
      logger.error('❌ Chronicle黑匣子数据库初始化失败:', error);
      throw error;
    }
  }

  /**
   * 🚨 记录故障 - 中央医院接收求救信号
   */
  async recordFailure(failureData) {
    return new Promise((resolve, reject) => {
      try {
        const record = new FailureRecord(failureData);
        
        const stmt = this.db.prepare(`
          INSERT INTO failure_records (
            timestamp, source, function_name, error_type, error_message,
            stack_trace, context, severity, status, healing_attempts,
            healing_strategy, resolution_notes, immune_signature
          ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        `);

        stmt.run([
          record.timestamp.toISOString(),
          record.source,
          record.function_name,
          record.error_type,
          record.error_message,
          record.stack_trace,
          JSON.stringify(record.context),
          record.severity,
          record.status,
          record.healing_attempts,
          record.healing_strategy,
          record.resolution_notes,
          record.immune_signature
        ], function(err) {
          if (err) {
            logger.error('❌ 故障记录失败:', err);
            reject(err);
          } else {
            record.id = this.lastID;
            logger.info(`🛡️ 故障已记录 [ID: ${record.id}] ${record.source}:${record.function_name}`);
            resolve(record);
          }
        });

        stmt.finalize();
      } catch (error) {
        logger.error('❌ 记录故障时发生错误:', error);
        reject(error);
      }
    });
  }

  /**
   * 🏥 请求治疗 - 中央医院提供治疗方案
   */
  async requestHealing(failureId, healingStrategy = null) {
    return new Promise((resolve, reject) => {
      try {
        // 获取故障记录
        this.db.get(
          'SELECT * FROM failure_records WHERE id = ?',
          [failureId],
          async (err, row) => {
            if (err) {
              reject(err);
              return;
            }

            if (!row) {
              reject(new Error(`故障记录不存在: ${failureId}`));
              return;
            }

            // 检查是否已有免疫
            const isImmune = await this.checkImmunity(row.immune_signature);
            if (isImmune) {
              logger.info(`🛡️ 系统已对此故障免疫: ${row.immune_signature}`);
              resolve({
                success: true,
                strategy: 'immune_response',
                message: '系统已具备免疫能力，自动跳过此类故障'
              });
              return;
            }

            // 生成治疗方案
            const healingPlan = await this.generateHealingPlan(row, healingStrategy);
            
            // 更新故障记录
            this.db.run(
              `UPDATE failure_records 
               SET status = ?, healing_attempts = healing_attempts + 1, 
                   healing_strategy = ?, updated_at = CURRENT_TIMESTAMP
               WHERE id = ?`,
              [FailureStatus.FIXING, healingPlan.strategy, failureId],
              (updateErr) => {
                if (updateErr) {
                  logger.error('❌ 更新故障记录失败:', updateErr);
                }
              }
            );

            logger.info(`🏥 为故障 [${failureId}] 生成治疗方案: ${healingPlan.strategy}`);
            resolve(healingPlan);
          }
        );
      } catch (error) {
        logger.error('❌ 请求治疗时发生错误:', error);
        reject(error);
      }
    });
  }

  /**
   * 🧬 生成治疗方案
   */
  async generateHealingPlan(failureRecord, preferredStrategy = null) {
    const strategies = {
      'retry_simple': {
        strategy: 'retry_simple',
        description: '简单重试策略',
        max_attempts: 3,
        delay: 1000,
        success_rate: 0.6
      },
      'ai_analyze_fix': {
        strategy: 'ai_analyze_fix', 
        description: 'AI智能分析修复',
        max_attempts: 2,
        delay: 2000,
        success_rate: 0.8
      },
      'fallback_mode': {
        strategy: 'fallback_mode',
        description: '降级模式运行',
        max_attempts: 1,
        delay: 500,
        success_rate: 0.9
      },
      'emergency_stop': {
        strategy: 'emergency_stop',
        description: '紧急停止保护',
        max_attempts: 0,
        delay: 0,
        success_rate: 1.0
      }
    };

    // 根据故障严重程度选择策略
    let selectedStrategy;
    if (preferredStrategy && strategies[preferredStrategy]) {
      selectedStrategy = strategies[preferredStrategy];
    } else {
      switch (failureRecord.severity) {
        case FailureSeverity.LOW:
          selectedStrategy = strategies.retry_simple;
          break;
        case FailureSeverity.MEDIUM:
          selectedStrategy = strategies.ai_analyze_fix;
          break;
        case FailureSeverity.HIGH:
          selectedStrategy = strategies.fallback_mode;
          break;
        case FailureSeverity.CRITICAL:
          selectedStrategy = strategies.emergency_stop;
          break;
        default:
          selectedStrategy = strategies.retry_simple;
      }
    }

    return {
      ...selectedStrategy,
      failure_id: failureRecord.id,
      immune_signature: failureRecord.immune_signature,
      context: JSON.parse(failureRecord.context || '{}')
    };
  }

  /**
   * 🛡️ 检查免疫状态
   */
  async checkImmunity(immuneSignature) {
    return new Promise((resolve, reject) => {
      this.db.get(
        'SELECT * FROM immune_system WHERE immune_signature = ?',
        [immuneSignature],
        (err, row) => {
          if (err) {
            reject(err);
          } else {
            resolve(!!row);
          }
        }
      );
    });
  }

  /**
   * 💉 建立免疫
   */
  async buildImmunity(failureRecord, preventionStrategy) {
    return new Promise((resolve, reject) => {
      const stmt = this.db.prepare(`
        INSERT OR REPLACE INTO immune_system (
          immune_signature, source, function_name, error_pattern,
          prevention_strategy, success_rate, last_triggered, 
          trigger_count, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, 
          COALESCE((SELECT trigger_count FROM immune_system WHERE immune_signature = ?), 0) + 1,
          CURRENT_TIMESTAMP)
      `);

      stmt.run([
        failureRecord.immune_signature,
        failureRecord.source,
        failureRecord.function_name,
        failureRecord.error_type,
        preventionStrategy,
        0.8, // 初始成功率
        new Date().toISOString(),
        failureRecord.immune_signature
      ], function(err) {
        if (err) {
          logger.error('❌ 建立免疫失败:', err);
          reject(err);
        } else {
          logger.info(`💉 已为 ${failureRecord.source}:${failureRecord.function_name} 建立免疫`);
          resolve(true);
        }
      });

      stmt.finalize();
    });
  }

  /**
   * 📊 获取系统健康报告
   */
  async getHealthReport(source = null) {
    return new Promise((resolve, reject) => {
      let query = `
        SELECT 
          source,
          COUNT(*) as total_failures,
          SUM(CASE WHEN status = 'fixed' THEN 1 ELSE 0 END) as resolved_failures,
          AVG(CASE WHEN status = 'fixed' THEN 1.0 ELSE 0.0 END) as success_rate,
          MAX(timestamp) as last_failure
        FROM failure_records
      `;
      
      let params = [];
      if (source) {
        query += ' WHERE source = ?';
        params.push(source);
      }
      
      query += ' GROUP BY source ORDER BY total_failures DESC';

      this.db.all(query, params, (err, rows) => {
        if (err) {
          reject(err);
        } else {
          resolve(rows);
        }
      });
    });
  }

  /**
   * 🔍 获取故障统计
   */
  async getFailureStats(timeRange = '24h') {
    return new Promise((resolve, reject) => {
      let timeFilter = '';
      switch (timeRange) {
        case '1h':
          timeFilter = "datetime(timestamp) > datetime('now', '-1 hour')";
          break;
        case '24h':
          timeFilter = "datetime(timestamp) > datetime('now', '-1 day')";
          break;
        case '7d':
          timeFilter = "datetime(timestamp) > datetime('now', '-7 days')";
          break;
        default:
          timeFilter = "1=1";
      }

      const query = `
        SELECT 
          COUNT(*) as total_failures,
          COUNT(DISTINCT source) as affected_systems,
          SUM(CASE WHEN status = 'fixed' THEN 1 ELSE 0 END) as resolved_count,
          SUM(CASE WHEN status = 'immune' THEN 1 ELSE 0 END) as immune_count,
          AVG(healing_attempts) as avg_healing_attempts
        FROM failure_records 
        WHERE ${timeFilter}
      `;

      this.db.get(query, [], (err, row) => {
        if (err) {
          reject(err);
        } else {
          resolve(row);
        }
      });
    });
  }

  /**
   * 🧹 清理过期记录
   */
  async cleanupOldRecords(daysToKeep = 30) {
    return new Promise((resolve, reject) => {
      this.db.run(
        `DELETE FROM failure_records 
         WHERE datetime(created_at) < datetime('now', '-${daysToKeep} days')`,
        [],
        function(err) {
          if (err) {
            reject(err);
          } else {
            logger.info(`🧹 清理了 ${this.changes} 条过期故障记录`);
            resolve(this.changes);
          }
        }
      );
    });
  }

  /**
   * 🔒 关闭数据库连接
   */
  close() {
    if (this.db) {
      this.db.close((err) => {
        if (err) {
          logger.error('❌ 关闭黑匣子数据库失败:', err);
        } else {
          logger.info('🛡️ Chronicle黑匣子数据库已关闭');
        }
      });
    }
  }
}

// 单例模式
let chronicleBlackBoxInstance = null;

function getChronicleBlackBox(db_path = null) {
  if (!chronicleBlackBoxInstance) {
    chronicleBlackBoxInstance = new ChronicleBlackBox(db_path);
  }
  return chronicleBlackBoxInstance;
}

module.exports = {
  ChronicleBlackBox,
  FailureRecord,
  FailureStatus,
  SystemSource,
  FailureSeverity,
  getChronicleBlackBox
};