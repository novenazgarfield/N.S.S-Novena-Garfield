class WordService {
  constructor(database) {
    this.db = database;
  }

  async getWordById(wordId) {
    try {
      const word = await this.db.get(
        'SELECT * FROM words WHERE id = ?',
        [wordId]
      );

      if (!word) {
        throw new Error('单词不存在');
      }

      // 获取学习记录
      const learningRecord = await this.db.get(
        'SELECT * FROM learning_records WHERE word_id = ?',
        [wordId]
      );

      // 获取AI生成的内容
      const aiContents = await this.db.all(
        'SELECT * FROM ai_contents WHERE word_id = ? ORDER BY created_at DESC',
        [wordId]
      );

      // 获取拼写练习记录
      const spellingRecords = await this.db.all(
        'SELECT * FROM spelling_records WHERE word_id = ? ORDER BY attempt_time DESC LIMIT 5',
        [wordId]
      );

      return {
        ...word,
        learningRecord,
        aiContents: this.formatAIContents(aiContents),
        spellingRecords,
        lastUpdated: new Date().toISOString()
      };
    } catch (error) {
      console.error('获取单词详情失败:', error);
      throw error;
    }
  }

  async getWordsByCategory(category, limit = 50) {
    try {
      const words = await this.db.all(
        `SELECT w.*, lr.status, lr.next_review 
         FROM words w 
         LEFT JOIN learning_records lr ON w.id = lr.word_id 
         WHERE w.category = ? 
         ORDER BY w.difficulty, w.word 
         LIMIT ?`,
        [category, limit]
      );

      return words;
    } catch (error) {
      console.error('获取分类单词失败:', error);
      throw error;
    }
  }

  async searchWords(query, limit = 20) {
    try {
      const words = await this.db.all(
        `SELECT w.*, lr.status 
         FROM words w 
         LEFT JOIN learning_records lr ON w.id = lr.word_id 
         WHERE w.word LIKE ? OR w.definition LIKE ? 
         ORDER BY w.word 
         LIMIT ?`,
        [`%${query}%`, `%${query}%`, limit]
      );

      return words;
    } catch (error) {
      console.error('搜索单词失败:', error);
      throw error;
    }
  }

  async addWord(wordData) {
    try {
      const { word, phonetic, definition, difficulty = 1, category = 'custom' } = wordData;

      // 检查单词是否已存在
      const existingWord = await this.db.get('SELECT id FROM words WHERE word = ?', [word]);
      if (existingWord) {
        throw new Error('单词已存在');
      }

      // 插入新单词
      const result = await this.db.run(
        'INSERT INTO words (word, phonetic, definition, difficulty, category) VALUES (?, ?, ?, ?, ?)',
        [word, phonetic, definition, difficulty, category]
      );

      // 创建学习记录
      await this.db.run(
        'INSERT INTO learning_records (word_id, status, next_review) VALUES (?, ?, datetime("now", "+1 day"))',
        [result.id, 'new']
      );

      return { id: result.id, ...wordData };
    } catch (error) {
      console.error('添加单词失败:', error);
      throw error;
    }
  }

  async updateWord(wordId, updateData) {
    try {
      const { word, phonetic, definition, difficulty, category } = updateData;
      
      await this.db.run(
        `UPDATE words 
         SET word = ?, phonetic = ?, definition = ?, difficulty = ?, category = ?, updated_at = CURRENT_TIMESTAMP 
         WHERE id = ?`,
        [word, phonetic, definition, difficulty, category, wordId]
      );

      return await this.getWordById(wordId);
    } catch (error) {
      console.error('更新单词失败:', error);
      throw error;
    }
  }

  async deleteWord(wordId) {
    try {
      await this.db.transaction(async () => {
        // 删除相关记录
        await this.db.run('DELETE FROM learning_records WHERE word_id = ?', [wordId]);
        await this.db.run('DELETE FROM ai_contents WHERE word_id = ?', [wordId]);
        await this.db.run('DELETE FROM spelling_records WHERE word_id = ?', [wordId]);
        await this.db.run('DELETE FROM push_records WHERE word_id = ?', [wordId]);
        
        // 删除单词
        await this.db.run('DELETE FROM words WHERE id = ?', [wordId]);
      });

      return { success: true };
    } catch (error) {
      console.error('删除单词失败:', error);
      throw error;
    }
  }

  async getWordStatistics() {
    try {
      const stats = await this.db.get(`
        SELECT 
          COUNT(*) as total_words,
          COUNT(CASE WHEN lr.status = 'new' THEN 1 END) as new_words,
          COUNT(CASE WHEN lr.status = 'learning' THEN 1 END) as learning_words,
          COUNT(CASE WHEN lr.status = 'mastered' THEN 1 END) as mastered_words,
          AVG(w.difficulty) as avg_difficulty
        FROM words w
        LEFT JOIN learning_records lr ON w.id = lr.word_id
      `);

      const categoryStats = await this.db.all(`
        SELECT 
          w.category,
          COUNT(*) as count,
          AVG(w.difficulty) as avg_difficulty
        FROM words w
        GROUP BY w.category
        ORDER BY count DESC
      `);

      return {
        ...stats,
        categoryStats,
        lastUpdated: new Date().toISOString()
      };
    } catch (error) {
      console.error('获取单词统计失败:', error);
      throw error;
    }
  }

  async saveAIContent(wordId, contentType, content) {
    try {
      await this.db.run(
        'INSERT INTO ai_contents (word_id, content_type, content) VALUES (?, ?, ?)',
        [wordId, contentType, content]
      );

      return { success: true };
    } catch (error) {
      console.error('保存AI内容失败:', error);
      throw error;
    }
  }

  async getRandomWords(count = 1, difficulty = null, category = null) {
    try {
      let sql = `
        SELECT w.*, lr.status 
        FROM words w 
        LEFT JOIN learning_records lr ON w.id = lr.word_id 
        WHERE 1=1
      `;
      const params = [];

      if (difficulty) {
        sql += ' AND w.difficulty = ?';
        params.push(difficulty);
      }

      if (category) {
        sql += ' AND w.category = ?';
        params.push(category);
      }

      sql += ' ORDER BY RANDOM() LIMIT ?';
      params.push(count);

      const words = await this.db.all(sql, params);
      return count === 1 ? words[0] : words;
    } catch (error) {
      console.error('获取随机单词失败:', error);
      throw error;
    }
  }

  formatAIContents(aiContents) {
    const formatted = {};
    aiContents.forEach(content => {
      formatted[content.content_type] = {
        content: content.content,
        createdAt: content.created_at
      };
    });
    return formatted;
  }

  // 批量导入单词
  async importWords(wordsData) {
    try {
      const results = [];
      
      await this.db.transaction(async () => {
        for (const wordData of wordsData) {
          try {
            const result = await this.addWord(wordData);
            results.push({ success: true, word: wordData.word, id: result.id });
          } catch (error) {
            results.push({ success: false, word: wordData.word, error: error.message });
          }
        }
      });

      return {
        total: wordsData.length,
        successful: results.filter(r => r.success).length,
        failed: results.filter(r => !r.success).length,
        results
      };
    } catch (error) {
      console.error('批量导入单词失败:', error);
      throw error;
    }
  }

  // 导出单词数据
  async exportWords(category = null) {
    try {
      let sql = `
        SELECT w.*, lr.status, lr.review_count, lr.correct_count 
        FROM words w 
        LEFT JOIN learning_records lr ON w.id = lr.word_id
      `;
      const params = [];

      if (category) {
        sql += ' WHERE w.category = ?';
        params.push(category);
      }

      sql += ' ORDER BY w.word';

      const words = await this.db.all(sql, params);
      return words;
    } catch (error) {
      console.error('导出单词数据失败:', error);
      throw error;
    }
  }
}

module.exports = WordService;