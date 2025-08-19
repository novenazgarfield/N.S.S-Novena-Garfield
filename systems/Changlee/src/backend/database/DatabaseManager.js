const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const fs = require('fs').promises;

class DatabaseManager {
  constructor() {
    this.dbPath = path.join(__dirname, '../../../database/changlee.db');
    this.db = null;
  }

  async initialize() {
    try {
      // 确保数据库目录存在
      const dbDir = path.dirname(this.dbPath);
      await fs.mkdir(dbDir, { recursive: true });

      // 连接数据库
      this.db = new sqlite3.Database(this.dbPath);
      
      // 启用外键约束
      await this.run('PRAGMA foreign_keys = ON');
      
      // 创建表结构
      await this.createTables();
      
      // 初始化数据
      await this.initializeData();
      
      console.log('📚 数据库初始化完成');
    } catch (error) {
      console.error('数据库初始化失败:', error);
      throw error;
    }
  }

  async createTables() {
    // 单词表
    await this.run(`
      CREATE TABLE IF NOT EXISTS words (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        word TEXT UNIQUE NOT NULL,
        phonetic TEXT,
        definition TEXT NOT NULL,
        difficulty INTEGER DEFAULT 1,
        category TEXT DEFAULT 'general',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
      )
    `);

    // 学习记录表
    await this.run(`
      CREATE TABLE IF NOT EXISTS learning_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        word_id INTEGER NOT NULL,
        status TEXT DEFAULT 'new',
        review_count INTEGER DEFAULT 0,
        correct_count INTEGER DEFAULT 0,
        last_reviewed DATETIME,
        next_review DATETIME,
        ease_factor REAL DEFAULT 2.5,
        interval_days INTEGER DEFAULT 1,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (word_id) REFERENCES words (id)
      )
    `);

    // AI生成内容表
    await this.run(`
      CREATE TABLE IF NOT EXISTS ai_contents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        word_id INTEGER NOT NULL,
        content_type TEXT NOT NULL,
        content TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (word_id) REFERENCES words (id)
      )
    `);

    // 拼写练习记录表
    await this.run(`
      CREATE TABLE IF NOT EXISTS spelling_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        word_id INTEGER NOT NULL,
        attempt_time DATETIME DEFAULT CURRENT_TIMESTAMP,
        is_correct BOOLEAN NOT NULL,
        time_spent INTEGER,
        mistakes INTEGER DEFAULT 0,
        FOREIGN KEY (word_id) REFERENCES words (id)
      )
    `);

    // 推送记录表
    await this.run(`
      CREATE TABLE IF NOT EXISTS push_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        word_id INTEGER,
        push_type TEXT NOT NULL,
        push_time DATETIME DEFAULT CURRENT_TIMESTAMP,
        is_opened BOOLEAN DEFAULT FALSE,
        FOREIGN KEY (word_id) REFERENCES words (id)
      )
    `);

    // 用户设置表
    await this.run(`
      CREATE TABLE IF NOT EXISTS user_settings (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
      )
    `);

    // 学习统计表
    await this.run(`
      CREATE TABLE IF NOT EXISTS learning_stats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date DATE NOT NULL,
        words_learned INTEGER DEFAULT 0,
        words_reviewed INTEGER DEFAULT 0,
        time_spent INTEGER DEFAULT 0,
        accuracy_rate REAL DEFAULT 0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
      )
    `);

    console.log('📋 数据库表结构创建完成');
  }

  async initializeData() {
    // 检查是否已有数据
    const wordCount = await this.get('SELECT COUNT(*) as count FROM words');
    if (wordCount.count > 0) {
      console.log('📖 数据库已有数据，跳过初始化');
      return;
    }

    // 插入初始单词数据（雅思核心词汇示例）
    const initialWords = [
      { word: 'abandon', phonetic: '/əˈbændən/', definition: 'v. 放弃，抛弃', difficulty: 2, category: 'ielts' },
      { word: 'ability', phonetic: '/əˈbɪləti/', definition: 'n. 能力，才能', difficulty: 1, category: 'ielts' },
      { word: 'abroad', phonetic: '/əˈbrɔːd/', definition: 'adv. 在国外，到国外', difficulty: 1, category: 'ielts' },
      { word: 'absence', phonetic: '/ˈæbsəns/', definition: 'n. 缺席，不在', difficulty: 2, category: 'ielts' },
      { word: 'absolute', phonetic: '/ˈæbsəluːt/', definition: 'adj. 绝对的，完全的', difficulty: 3, category: 'ielts' },
      { word: 'absorb', phonetic: '/əbˈzɔːb/', definition: 'v. 吸收，吸引', difficulty: 2, category: 'ielts' },
      { word: 'abstract', phonetic: '/ˈæbstrækt/', definition: 'adj. 抽象的 n. 摘要', difficulty: 3, category: 'ielts' },
      { word: 'academic', phonetic: '/ˌækəˈdemɪk/', definition: 'adj. 学术的，理论的', difficulty: 2, category: 'ielts' },
      { word: 'accelerate', phonetic: '/əkˈseləreɪt/', definition: 'v. 加速，促进', difficulty: 3, category: 'ielts' },
      { word: 'accept', phonetic: '/əkˈsept/', definition: 'v. 接受，承认', difficulty: 1, category: 'ielts' }
    ];

    for (const wordData of initialWords) {
      await this.run(
        'INSERT INTO words (word, phonetic, definition, difficulty, category) VALUES (?, ?, ?, ?, ?)',
        [wordData.word, wordData.phonetic, wordData.definition, wordData.difficulty, wordData.category]
      );

      // 为每个单词创建学习记录
      const wordId = await this.get('SELECT id FROM words WHERE word = ?', [wordData.word]);
      await this.run(
        'INSERT INTO learning_records (word_id, status, next_review) VALUES (?, ?, datetime("now", "+1 day"))',
        [wordId.id, 'new']
      );
    }

    // 初始化用户设置
    const defaultSettings = {
      'push_frequency': '3',
      'push_enabled': 'true',
      'sound_enabled': 'true',
      'auto_start': 'true',
      'pet_position_x': '800',
      'pet_position_y': '600',
      'learning_goal_daily': '5',
      'difficulty_preference': 'adaptive'
    };

    for (const [key, value] of Object.entries(defaultSettings)) {
      await this.run(
        'INSERT OR REPLACE INTO user_settings (key, value) VALUES (?, ?)',
        [key, value]
      );
    }

    console.log('🌱 初始数据插入完成');
  }

  // 数据库操作方法
  run(sql, params = []) {
    return new Promise((resolve, reject) => {
      this.db.run(sql, params, function(err) {
        if (err) {
          reject(err);
        } else {
          resolve({ id: this.lastID, changes: this.changes });
        }
      });
    });
  }

  get(sql, params = []) {
    return new Promise((resolve, reject) => {
      this.db.get(sql, params, (err, row) => {
        if (err) {
          reject(err);
        } else {
          resolve(row);
        }
      });
    });
  }

  all(sql, params = []) {
    return new Promise((resolve, reject) => {
      this.db.all(sql, params, (err, rows) => {
        if (err) {
          reject(err);
        } else {
          resolve(rows);
        }
      });
    });
  }

  // 事务支持
  async transaction(callback) {
    await this.run('BEGIN TRANSACTION');
    try {
      const result = await callback();
      await this.run('COMMIT');
      return result;
    } catch (error) {
      await this.run('ROLLBACK');
      throw error;
    }
  }

  // 关闭数据库连接
  close() {
    return new Promise((resolve, reject) => {
      this.db.close((err) => {
        if (err) {
          reject(err);
        } else {
          console.log('📚 数据库连接已关闭');
          resolve();
        }
      });
    });
  }
}

module.exports = DatabaseManager;