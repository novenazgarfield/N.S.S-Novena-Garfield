class PushService {
  constructor(database, aiService) {
    this.db = database;
    this.aiService = aiService;
    this.dailyPushLimit = 3; // 每日推送限制
    this.pushCooldown = 2 * 60 * 60 * 1000; // 2小时冷却时间
  }

  // 检查并执行推送
  async checkAndPush() {
    try {
      // 检查是否可以推送
      const canPush = await this.canPushNow();
      if (!canPush) {
        console.log('⏰ 当前不满足推送条件');
        return null;
      }

      // 获取推送内容
      const pushData = await this.generatePushContent();
      if (!pushData) {
        console.log('📭 没有可推送的内容');
        return null;
      }

      // 执行推送
      await this.executePush(pushData);
      
      console.log('📮 推送执行成功:', pushData.word);
      return pushData;
    } catch (error) {
      console.error('推送检查失败:', error);
      return null;
    }
  }

  // 检查是否可以推送
  async canPushNow() {
    try {
      // 检查推送是否启用
      const pushEnabled = await this.db.get(
        'SELECT value FROM user_settings WHERE key = ?',
        ['push_enabled']
      );
      
      if (!pushEnabled || pushEnabled.value !== 'true') {
        return false;
      }

      // 检查今日推送次数
      const today = new Date().toISOString().split('T')[0];
      const todayPushCount = await this.db.get(
        'SELECT COUNT(*) as count FROM push_records WHERE DATE(push_time) = ?',
        [today]
      );

      if (todayPushCount.count >= this.dailyPushLimit) {
        return false;
      }

      // 检查最后推送时间（冷却时间）
      const lastPush = await this.db.get(
        'SELECT push_time FROM push_records ORDER BY push_time DESC LIMIT 1'
      );

      if (lastPush) {
        const lastPushTime = new Date(lastPush.push_time).getTime();
        const now = new Date().getTime();
        if (now - lastPushTime < this.pushCooldown) {
          return false;
        }
      }

      // 检查用户活动状态（可以通过系统API获取鼠标键盘活动）
      const isUserActive = await this.checkUserActivity();
      if (isUserActive) {
        return false; // 用户正在活跃使用电脑，不推送
      }

      return true;
    } catch (error) {
      console.error('检查推送条件失败:', error);
      return false;
    }
  }

  // 生成推送内容
  async generatePushContent() {
    try {
      // 获取需要学习的单词
      const word = await this.db.get(`
        SELECT w.*, lr.* 
        FROM words w 
        JOIN learning_records lr ON w.id = lr.word_id 
        WHERE lr.next_review <= datetime('now') 
        ORDER BY lr.next_review ASC, lr.ease_factor ASC 
        LIMIT 1
      `);

      if (!word) {
        // 如果没有需要复习的，获取新单词
        const newWord = await this.db.get(`
          SELECT w.*, lr.* 
          FROM words w 
          JOIN learning_records lr ON w.id = lr.word_id 
          WHERE lr.status = 'new' 
          ORDER BY w.difficulty ASC, RANDOM() 
          LIMIT 1
        `);
        
        if (!newWord) {
          return null;
        }
        
        return await this.createPushData(newWord, 'new_word');
      }

      return await this.createPushData(word, 'review');
    } catch (error) {
      console.error('生成推送内容失败:', error);
      return null;
    }
  }

  // 创建推送数据
  async createPushData(word, pushType) {
    try {
      // 生成长离的问候语
      const greeting = await this.aiService.generateDailyGreeting();
      
      // 生成学习提示
      const learningTip = await this.generateLearningTip(word, pushType);

      return {
        wordId: word.id,
        word: word.word,
        definition: word.definition,
        phonetic: word.phonetic,
        pushType,
        greeting,
        learningTip,
        timestamp: new Date().toISOString()
      };
    } catch (error) {
      console.error('创建推送数据失败:', error);
      return null;
    }
  }

  // 生成学习提示
  async generateLearningTip(word, pushType) {
    const tips = {
      new_word: [
        `🌟 发现了一个新单词"${word.word}"，要不要一起学习呢？`,
        `📚 长离为你准备了新单词"${word.word}"，来看看吧！`,
        `✨ 今天学点新东西怎么样？"${word.word}"等着你呢～`
      ],
      review: [
        `🔄 该复习"${word.word}"了，长离陪你一起回忆！`,
        `💭 还记得"${word.word}"吗？来复习一下吧！`,
        `⏰ 复习时间到！"${word.word}"需要你的关注～`
      ]
    };

    const tipArray = tips[pushType] || tips.new_word;
    return tipArray[Math.floor(Math.random() * tipArray.length)];
  }

  // 执行推送
  async executePush(pushData) {
    try {
      // 记录推送
      await this.db.run(
        'INSERT INTO push_records (word_id, push_type, push_time) VALUES (?, ?, datetime("now"))',
        [pushData.wordId, pushData.pushType]
      );

      // 这里可以通过IPC通知主进程显示桌宠动画
      // 实际实现中会通过事件系统通知前端
      console.log('📮 推送通知已发送:', {
        word: pushData.word,
        type: pushData.pushType,
        tip: pushData.learningTip
      });

      return true;
    } catch (error) {
      console.error('执行推送失败:', error);
      return false;
    }
  }

  // 检查用户活动状态（简化版本）
  async checkUserActivity() {
    try {
      // 这里可以集成系统API来检测用户活动
      // 简化版本：检查最近的学习活动
      const recentActivity = await this.db.get(`
        SELECT attempt_time 
        FROM spelling_records 
        WHERE attempt_time > datetime('now', '-30 minutes') 
        LIMIT 1
      `);

      return !!recentActivity;
    } catch (error) {
      console.error('检查用户活动失败:', error);
      return false;
    }
  }

  // 获取下一个推送数据（供前端调用）
  async getNextPush() {
    try {
      return await this.generatePushContent();
    } catch (error) {
      console.error('获取下一个推送失败:', error);
      return null;
    }
  }

  // 标记推送已打开
  async markPushOpened(pushId) {
    try {
      await this.db.run(
        'UPDATE push_records SET is_opened = TRUE WHERE id = ?',
        [pushId]
      );
      return true;
    } catch (error) {
      console.error('标记推送已打开失败:', error);
      return false;
    }
  }

  // 重置每日推送计数
  async resetDailyCount() {
    try {
      console.log('🌅 重置每日推送计数');
      // 这里可以添加一些清理逻辑
      return true;
    } catch (error) {
      console.error('重置每日推送计数失败:', error);
      return false;
    }
  }

  // 获取推送统计
  async getPushStatistics() {
    try {
      const stats = await this.db.get(`
        SELECT 
          COUNT(*) as total_pushes,
          COUNT(CASE WHEN is_opened THEN 1 END) as opened_pushes,
          COUNT(CASE WHEN DATE(push_time) = DATE('now') THEN 1 END) as today_pushes
        FROM push_records
      `);

      const recentPushes = await this.db.all(`
        SELECT pr.*, w.word, w.definition
        FROM push_records pr
        LEFT JOIN words w ON pr.word_id = w.id
        ORDER BY pr.push_time DESC
        LIMIT 10
      `);

      return {
        ...stats,
        openRate: stats.total_pushes > 0 ? (stats.opened_pushes / stats.total_pushes * 100).toFixed(1) : 0,
        recentPushes,
        lastUpdated: new Date().toISOString()
      };
    } catch (error) {
      console.error('获取推送统计失败:', error);
      throw error;
    }
  }

  // 更新推送设置
  async updatePushSettings(settings) {
    try {
      const { enabled, frequency, quietHours } = settings;
      
      await this.db.run(
        'INSERT OR REPLACE INTO user_settings (key, value) VALUES (?, ?)',
        ['push_enabled', enabled.toString()]
      );

      if (frequency) {
        this.dailyPushLimit = parseInt(frequency);
        await this.db.run(
          'INSERT OR REPLACE INTO user_settings (key, value) VALUES (?, ?)',
          ['push_frequency', frequency.toString()]
        );
      }

      if (quietHours) {
        await this.db.run(
          'INSERT OR REPLACE INTO user_settings (key, value) VALUES (?, ?)',
          ['quiet_hours', JSON.stringify(quietHours)]
        );
      }

      return true;
    } catch (error) {
      console.error('更新推送设置失败:', error);
      return false;
    }
  }

  // 智能推送时机判断
  async getOptimalPushTime() {
    try {
      // 分析用户的学习习惯，找出最佳推送时间
      const learningPatterns = await this.db.all(`
        SELECT 
          strftime('%H', attempt_time) as hour,
          COUNT(*) as activity_count
        FROM spelling_records
        WHERE attempt_time > datetime('now', '-30 days')
        GROUP BY strftime('%H', attempt_time)
        ORDER BY activity_count DESC
      `);

      if (learningPatterns.length === 0) {
        // 默认推送时间：上午10点，下午3点，晚上8点
        return ['10', '15', '20'];
      }

      // 返回活跃度最高的3个时间段
      return learningPatterns.slice(0, 3).map(p => p.hour);
    } catch (error) {
      console.error('获取最佳推送时间失败:', error);
      return ['10', '15', '20'];
    }
  }
}

module.exports = PushService;