const express = require('express');
const cors = require('cors');
const path = require('path');
const cron = require('node-cron');

const DatabaseManager = require('./database/DatabaseManager');
const AIService = require('./services/AIService');
const WordService = require('./services/WordService');
const LearningService = require('./services/LearningService');
const PushService = require('./services/PushService');
const RAGService = require('./services/RAGService');
const MusicService = require('./services/MusicService');

class ChangleeServer {
  constructor() {
    this.app = express();
    this.port = 3001;
    this.db = new DatabaseManager();
    this.aiService = new AIService();
    this.ragService = new RAGService();
    this.wordService = new WordService(this.db);
    this.learningService = new LearningService(this.db);
    this.pushService = new PushService(this.db, this.aiService);
    this.musicService = new MusicService();
  }

  async initialize() {
    // 初始化数据库
    await this.db.initialize();
    
    // 初始化RAG服务
    await this.ragService.initialize();
    
    // 配置中间件
    this.setupMiddleware();
    
    // 配置路由
    this.setupRoutes();
    
    // 启动定时任务
    this.setupScheduledTasks();
    
    // 启动服务器
    this.startServer();
  }

  setupMiddleware() {
    this.app.use(cors());
    this.app.use(express.json());
    this.app.use(express.static(path.join(__dirname, '../../assets')));
    
    // 请求日志
    this.app.use((req, res, next) => {
      console.log(`📡 ${req.method} ${req.path} - ${new Date().toISOString()}`);
      next();
    });
  }

  setupRoutes() {
    // 健康检查
    this.app.get('/health', (req, res) => {
      res.json({ 
        status: 'healthy', 
        timestamp: new Date().toISOString(),
        service: '长离的学习胶囊后端服务'
      });
    });

    // 单词相关路由
    this.app.get('/api/words/next', async (req, res) => {
      try {
        const nextWord = await this.learningService.getNextWordToLearn();
        res.json({ success: true, data: nextWord });
      } catch (error) {
        console.error('获取下一个单词失败:', error);
        res.status(500).json({ success: false, error: error.message });
      }
    });

    this.app.get('/api/words/:id', async (req, res) => {
      try {
        const word = await this.wordService.getWordById(req.params.id);
        res.json({ success: true, data: word });
      } catch (error) {
        console.error('获取单词失败:', error);
        res.status(500).json({ success: false, error: error.message });
      }
    });

    this.app.post('/api/words/:id/status', async (req, res) => {
      try {
        const { status } = req.body;
        await this.learningService.updateWordStatus(req.params.id, status);
        res.json({ success: true });
      } catch (error) {
        console.error('更新单词状态失败:', error);
        res.status(500).json({ success: false, error: error.message });
      }
    });

    this.app.post('/api/words/:id/spelling', async (req, res) => {
      try {
        const result = await this.learningService.submitSpellingResult(req.params.id, req.body);
        res.json({ success: true, data: result });
      } catch (error) {
        console.error('提交拼写结果失败:', error);
        res.status(500).json({ success: false, error: error.message });
      }
    });

    // 学习进度路由
    this.app.get('/api/progress', async (req, res) => {
      try {
        const progress = await this.learningService.getLearningProgress();
        res.json({ success: true, data: progress });
      } catch (error) {
        console.error('获取学习进度失败:', error);
        res.status(500).json({ success: false, error: error.message });
      }
    });

    // AI内容生成路由
    this.app.post('/api/ai/generate', async (req, res) => {
      try {
        const content = await this.aiService.generateLearningContent(req.body);
        res.json({ success: true, data: content });
      } catch (error) {
        console.error('AI内容生成失败:', error);
        res.status(500).json({ success: false, error: error.message });
      }
    });

    // 推送服务路由
    this.app.get('/api/push/next', async (req, res) => {
      try {
        const pushData = await this.pushService.getNextPush();
        res.json({ success: true, data: pushData });
      } catch (error) {
        console.error('获取推送数据失败:', error);
        res.status(500).json({ success: false, error: error.message });
      }
    });

    // 统计信息路由
    this.app.get('/api/stats', async (req, res) => {
      try {
        const stats = await this.learningService.getStatistics();
        res.json({ success: true, data: stats });
      } catch (error) {
        console.error('获取统计信息失败:', error);
        res.status(500).json({ success: false, error: error.message });
      }
    });

    // RAG系统集成路由
    this.app.post('/api/rag/ask', async (req, res) => {
      try {
        const { question, context } = req.body;
        const response = await this.ragService.askChanglee(question, context);
        res.json({ success: true, data: response });
      } catch (error) {
        console.error('RAG问答失败:', error);
        res.status(500).json({ success: false, error: error.message });
      }
    });

    this.app.post('/api/rag/upload', async (req, res) => {
      try {
        // 这里需要处理文件上传
        const { filePath, metadata } = req.body;
        const result = await this.ragService.uploadLearningDocument(filePath, metadata);
        res.json({ success: true, data: result });
      } catch (error) {
        console.error('文档上传失败:', error);
        res.status(500).json({ success: false, error: error.message });
      }
    });

    this.app.post('/api/rag/recommendations', async (req, res) => {
      try {
        const { userProfile } = req.body;
        const recommendations = await this.ragService.getLearningRecommendations(userProfile);
        res.json({ success: true, data: recommendations });
      } catch (error) {
        console.error('获取学习建议失败:', error);
        res.status(500).json({ success: false, error: error.message });
      }
    });

    this.app.post('/api/rag/analyze-document', async (req, res) => {
      try {
        const { documentId, difficulty } = req.body;
        const analysis = await this.ragService.analyzeDocumentForWords(documentId, difficulty);
        res.json({ success: true, data: analysis });
      } catch (error) {
        console.error('文档分析失败:', error);
        res.status(500).json({ success: false, error: error.message });
      }
    });

    // Changlee's Groove: 音乐播放模块API路由
    // 获取播放列表
    this.app.get('/api/music/playlist', async (req, res) => {
      try {
        const result = this.musicService.getPlaylist();
        res.json(result);
      } catch (error) {
        console.error('获取播放列表失败:', error);
        res.status(500).json({ success: false, error: error.message });
      }
    });

    // 搜索音乐
    this.app.get('/api/music/search', async (req, res) => {
      try {
        const { q } = req.query;
        const result = this.musicService.searchMusic(q);
        res.json(result);
      } catch (error) {
        console.error('搜索音乐失败:', error);
        res.status(500).json({ success: false, error: error.message });
      }
    });

    // 按艺术家分组获取音乐
    this.app.get('/api/music/artists', async (req, res) => {
      try {
        const result = this.musicService.getMusicByArtist();
        res.json(result);
      } catch (error) {
        console.error('获取艺术家分组失败:', error);
        res.status(500).json({ success: false, error: error.message });
      }
    });

    // 设置音乐文件夹
    this.app.post('/api/music/folders', async (req, res) => {
      try {
        const { folders } = req.body;
        const result = await this.musicService.setMusicFolders(folders);
        res.json(result);
      } catch (error) {
        console.error('设置音乐文件夹失败:', error);
        res.status(500).json({ success: false, error: error.message });
      }
    });

    // 扫描音乐文件
    this.app.post('/api/music/scan', async (req, res) => {
      try {
        const result = await this.musicService.scanMusic();
        res.json(result);
      } catch (error) {
        console.error('扫描音乐失败:', error);
        res.status(500).json({ success: false, error: error.message });
      }
    });

    // 播放指定音乐
    this.app.post('/api/music/play/:trackId', async (req, res) => {
      try {
        const result = this.musicService.playTrack(req.params.trackId);
        res.json(result);
      } catch (error) {
        console.error('播放音乐失败:', error);
        res.status(500).json({ success: false, error: error.message });
      }
    });

    // 暂停播放
    this.app.post('/api/music/pause', async (req, res) => {
      try {
        const result = this.musicService.pauseTrack();
        res.json(result);
      } catch (error) {
        console.error('暂停播放失败:', error);
        res.status(500).json({ success: false, error: error.message });
      }
    });

    // 恢复播放
    this.app.post('/api/music/resume', async (req, res) => {
      try {
        const result = this.musicService.resumeTrack();
        res.json(result);
      } catch (error) {
        console.error('恢复播放失败:', error);
        res.status(500).json({ success: false, error: error.message });
      }
    });

    // 停止播放
    this.app.post('/api/music/stop', async (req, res) => {
      try {
        const result = this.musicService.stopTrack();
        res.json(result);
      } catch (error) {
        console.error('停止播放失败:', error);
        res.status(500).json({ success: false, error: error.message });
      }
    });

    // 下一首
    this.app.post('/api/music/next', async (req, res) => {
      try {
        const result = this.musicService.nextTrack();
        res.json(result);
      } catch (error) {
        console.error('切换下一首失败:', error);
        res.status(500).json({ success: false, error: error.message });
      }
    });

    // 上一首
    this.app.post('/api/music/previous', async (req, res) => {
      try {
        const result = this.musicService.previousTrack();
        res.json(result);
      } catch (error) {
        console.error('切换上一首失败:', error);
        res.status(500).json({ success: false, error: error.message });
      }
    });

    // 设置音量
    this.app.post('/api/music/volume', async (req, res) => {
      try {
        const { volume } = req.body;
        const result = await this.musicService.setVolume(volume);
        res.json(result);
      } catch (error) {
        console.error('设置音量失败:', error);
        res.status(500).json({ success: false, error: error.message });
      }
    });

    // 设置播放模式
    this.app.post('/api/music/playmode', async (req, res) => {
      try {
        const { mode } = req.body;
        const result = await this.musicService.setPlayMode(mode);
        res.json(result);
      } catch (error) {
        console.error('设置播放模式失败:', error);
        res.status(500).json({ success: false, error: error.message });
      }
    });

    // 更新播放进度
    this.app.post('/api/music/progress', async (req, res) => {
      try {
        const { currentTime, duration } = req.body;
        const result = this.musicService.updateProgress(currentTime, duration);
        res.json(result);
      } catch (error) {
        console.error('更新播放进度失败:', error);
        res.status(500).json({ success: false, error: error.message });
      }
    });

    // 获取播放状态
    this.app.get('/api/music/state', async (req, res) => {
      try {
        const result = this.musicService.getPlaybackState();
        res.json(result);
      } catch (error) {
        console.error('获取播放状态失败:', error);
        res.status(500).json({ success: false, error: error.message });
      }
    });

    // 获取音乐文件URL
    this.app.get('/api/music/url/:trackId', async (req, res) => {
      try {
        const result = this.musicService.getTrackUrl(req.params.trackId);
        res.json(result);
      } catch (error) {
        console.error('获取音乐URL失败:', error);
        res.status(500).json({ success: false, error: error.message });
      }
    });

    // 创建随机播放列表
    this.app.post('/api/music/random-playlist', async (req, res) => {
      try {
        const { count } = req.body;
        const result = this.musicService.createRandomPlaylist(count);
        res.json(result);
      } catch (error) {
        console.error('创建随机播放列表失败:', error);
        res.status(500).json({ success: false, error: error.message });
      }
    });

    this.app.post('/api/rag/progress-analysis', async (req, res) => {
      try {
        const { progressData } = req.body;
        const analysis = await this.ragService.getProgressAnalysis(progressData);
        res.json({ success: true, data: analysis });
      } catch (error) {
        console.error('进度分析失败:', error);
        res.status(500).json({ success: false, error: error.message });
      }
    });

    this.app.get('/api/rag/status', async (req, res) => {
      try {
        const status = this.ragService.getServiceStatus();
        const healthCheck = await this.ragService.checkRAGHealth();
        res.json({ 
          success: true, 
          data: { 
            ...status, 
            healthCheck 
          } 
        });
      } catch (error) {
        console.error('获取RAG状态失败:', error);
        res.status(500).json({ success: false, error: error.message });
      }
    });

    // 文献检索问答路由
    this.app.post('/api/rag/search', async (req, res) => {
      try {
        const { query, options } = req.body;
        const result = await this.ragService.searchDocuments(query, options);
        res.json({ success: true, data: result });
      } catch (error) {
        console.error('文献检索失败:', error);
        res.status(500).json({ success: false, error: error.message });
      }
    });

    this.app.post('/api/rag/ask-document', async (req, res) => {
      try {
        const { documentId, question, context } = req.body;
        const result = await this.ragService.askAboutDocument(documentId, question, context);
        res.json({ success: true, data: result });
      } catch (error) {
        console.error('文档问答失败:', error);
        res.status(500).json({ success: false, error: error.message });
      }
    });

    this.app.post('/api/rag/batch-analyze', async (req, res) => {
      try {
        const { documentIds, analysisType } = req.body;
        const result = await this.ragService.analyzeBatchDocuments(documentIds, analysisType);
        res.json({ success: true, data: result });
      } catch (error) {
        console.error('批量分析失败:', error);
        res.status(500).json({ success: false, error: error.message });
      }
    });

    this.app.post('/api/rag/integrate-knowledge', async (req, res) => {
      try {
        const { topic, documentIds } = req.body;
        const result = await this.ragService.integrateKnowledgeAcrossDocuments(topic, documentIds);
        res.json({ success: true, data: result });
      } catch (error) {
        console.error('知识整合失败:', error);
        res.status(500).json({ success: false, error: error.message });
      }
    });

    // 错误处理中间件
    this.app.use((error, req, res, next) => {
      console.error('服务器错误:', error);
      res.status(500).json({ 
        success: false, 
        error: '服务器内部错误',
        message: error.message 
      });
    });

    // 404处理
    this.app.use((req, res) => {
      res.status(404).json({ 
        success: false, 
        error: '接口不存在',
        path: req.path 
      });
    });
  }

  setupScheduledTasks() {
    // 每小时检查是否需要推送学习内容
    cron.schedule('0 * * * *', async () => {
      try {
        console.log('🕐 执行定时推送检查...');
        await this.pushService.checkAndPush();
      } catch (error) {
        console.error('定时推送检查失败:', error);
      }
    });

    // 每天凌晨重置推送计数
    cron.schedule('0 0 * * *', async () => {
      try {
        console.log('🌅 重置每日推送计数...');
        await this.pushService.resetDailyCount();
      } catch (error) {
        console.error('重置推送计数失败:', error);
      }
    });

    // 每周更新学习统计
    cron.schedule('0 0 * * 0', async () => {
      try {
        console.log('📊 更新学习统计...');
        await this.learningService.updateWeeklyStats();
      } catch (error) {
        console.error('更新学习统计失败:', error);
      }
    });

    console.log('⏰ 定时任务已设置');
  }

  startServer() {
    this.app.listen(this.port, () => {
      console.log(`🚀 长离的学习胶囊后端服务已启动`);
      console.log(`📡 服务地址: http://localhost:${this.port}`);
      console.log(`🕐 启动时间: ${new Date().toLocaleString('zh-CN')}`);
    });
  }
}

// 启动服务器
const server = new ChangleeServer();
server.initialize().catch(error => {
  console.error('服务器启动失败:', error);
  process.exit(1);
});

// 优雅关闭
process.on('SIGINT', () => {
  console.log('\n🛑 正在关闭服务器...');
  process.exit(0);
});

process.on('SIGTERM', () => {
  console.log('\n🛑 正在关闭服务器...');
  process.exit(0);
});

module.exports = ChangleeServer;