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
const ChronicleService = require('./services/ChronicleService');
const { createChronicleClient, LearningSessionManager } = require('./services/ChronicleClient');

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
    
    // Chronicle集成服务
    this.chronicleService = new ChronicleService({
      chronicleUrl: process.env.CHRONICLE_URL || 'http://localhost:3000',
      apiKey: process.env.CHRONICLE_API_KEY
    });
    
    // Chronicle客户端和会话管理器
    this.chronicleClient = createChronicleClient({
      baseUrl: process.env.CHRONICLE_URL || 'http://localhost:3000',
      apiKey: process.env.CHRONICLE_API_KEY
    });
    this.sessionManager = new LearningSessionManager(this.chronicleClient);
    
    // AI服务配置
    try {
      const { aiConfig, getAvailableServices, getPreferredService, validateConfig } = require('../../config/ai_config');
      
      // 验证AI配置
      const configValidation = validateConfig();
      if (configValidation.errors.length > 0) {
        console.error('❌ AI配置错误:');
        configValidation.errors.forEach(error => console.error(`   - ${error}`));
      }
      if (configValidation.warnings.length > 0) {
        console.warn('⚠️ AI配置警告:');
        configValidation.warnings.forEach(warning => console.warn(`   - ${warning}`));
      }

      // 显示可用的AI服务
      const availableServices = getAvailableServices();
      console.log('🤖 可用的AI服务:');
      availableServices.forEach(service => {
        console.log(`   ✅ ${service.name} (${service.type}) - ${service.description}`);
      });

      const preferredService = getPreferredService();
      console.log(`🎯 首选AI服务: ${preferredService || '无'}`);

      this.aiConfig = aiConfig;
      this.availableServices = availableServices;
      this.preferredService = preferredService;
    } catch (error) {
      console.warn('⚠️ 无法加载AI配置，使用默认配置:', error.message);
      this.aiConfig = null;
      this.availableServices = [];
      this.preferredService = null;
    }

    // 兼容性配置（保持向后兼容）
    this.localAIConfig = {
      enabled: this.aiConfig?.local?.enabled || process.env.LOCAL_AI_ENABLED !== 'false',
      url: this.aiConfig?.local?.serverUrl || process.env.LOCAL_AI_URL || 'http://localhost:8001',
      timeout: this.aiConfig?.hybrid?.timeout || parseInt(process.env.LOCAL_AI_TIMEOUT) || 10000,
      retryAttempts: this.aiConfig?.hybrid?.retryAttempts || parseInt(process.env.LOCAL_AI_RETRY) || 2
    };
  }

  async initialize() {
    // 初始化数据库
    await this.db.initialize();
    
    // 初始化RAG服务
    await this.ragService.initialize();
    
    // 初始化Chronicle服务
    try {
      await this.chronicleService.initialize();
      await this.chronicleClient.connect();
      console.log('✅ Chronicle集成服务初始化成功');
    } catch (error) {
      console.warn('⚠️ Chronicle服务初始化失败，将在后台重试:', error.message);
    }
    
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

    // Chronicle学习记录集成路由
    // 开始学习会话记录
    this.app.post('/api/chronicle/sessions/start', async (req, res) => {
      try {
        const sessionData = {
          id: req.body.sessionId || `changlee_${Date.now()}`,
          userId: req.body.userId,
          type: req.body.learningType || 'general',
          subject: req.body.subject,
          difficulty: req.body.difficulty,
          projectPath: req.body.projectPath,
          monitorFiles: req.body.monitorFiles,
          monitorWindows: req.body.monitorWindows,
          monitorCommands: req.body.monitorCommands,
          metadata: req.body.metadata || {}
        };

        const result = await this.sessionManager.startLearningSession(sessionData);
        res.json({ success: true, data: result });
      } catch (error) {
        console.error('启动Chronicle学习会话失败:', error);
        res.status(500).json({ success: false, error: error.message });
      }
    });

    // 结束学习会话记录
    this.app.post('/api/chronicle/sessions/:sessionId/stop', async (req, res) => {
      try {
        const { sessionId } = req.params;
        const summary = req.body.summary || {};
        
        const result = await this.sessionManager.endLearningSession(sessionId, summary);
        res.json({ success: true, data: result });
      } catch (error) {
        console.error('停止Chronicle学习会话失败:', error);
        res.status(500).json({ success: false, error: error.message });
      }
    });

    // 获取学习会话报告
    this.app.get('/api/chronicle/sessions/:sessionId/report', async (req, res) => {
      try {
        const { sessionId } = req.params;
        const includeRawData = req.query.includeRaw === 'true';
        
        const report = await this.sessionManager.getLearningReport(sessionId, includeRawData);
        res.json({ success: true, data: report });
      } catch (error) {
        console.error('获取Chronicle学习报告失败:', error);
        res.status(500).json({ success: false, error: error.message });
      }
    });

    // 获取活动学习会话列表
    this.app.get('/api/chronicle/sessions/active', async (req, res) => {
      try {
        const activeSessions = this.sessionManager.getActiveSessions();
        res.json({ success: true, data: activeSessions });
      } catch (error) {
        console.error('获取活动会话列表失败:', error);
        res.status(500).json({ success: false, error: error.message });
      }
    });

    // 获取Chronicle服务状态
    this.app.get('/api/chronicle/status', async (req, res) => {
      try {
        const chronicleStatus = this.chronicleService.getServiceStatus();
        const clientStatus = this.chronicleClient.getConnectionStatus();
        
        res.json({ 
          success: true, 
          data: {
            service: chronicleStatus,
            client: clientStatus,
            integration_status: 'active'
          }
        });
      } catch (error) {
        console.error('获取Chronicle状态失败:', error);
        res.status(500).json({ success: false, error: error.message });
      }
    });

    // 获取学习历史分析
    this.app.get('/api/chronicle/analysis/history', async (req, res) => {
      try {
        const options = {
          limit: parseInt(req.query.limit) || 50,
          userId: req.query.userId,
          learningType: req.query.type
        };
        
        const analysis = await this.chronicleService.analyzeLearningHistory(options);
        res.json({ success: true, data: analysis });
      } catch (error) {
        console.error('获取学习历史分析失败:', error);
        res.status(500).json({ success: false, error: error.message });
      }
    });

    // 获取所有Chronicle会话统计
    this.app.get('/api/chronicle/stats', async (req, res) => {
      try {
        const stats = await this.chronicleService.getAllSessionsStats();
        res.json({ success: true, data: stats });
      } catch (error) {
        console.error('获取Chronicle统计信息失败:', error);
        res.status(500).json({ success: false, error: error.message });
      }
    });

    // Chronicle健康检查
    this.app.get('/api/chronicle/health', async (req, res) => {
      try {
        const health = await this.chronicleClient.checkHealth();
        res.json({ success: true, data: health });
      } catch (error) {
        console.error('Chronicle健康检查失败:', error);
        res.status(500).json({ success: false, error: error.message });
      }
    });

    // 手动重连Chronicle服务
    this.app.post('/api/chronicle/reconnect', async (req, res) => {
      try {
        await this.chronicleClient.connect();
        res.json({ success: true, message: 'Chronicle服务重连成功' });
      } catch (error) {
        console.error('Chronicle重连失败:', error);
        res.status(500).json({ success: false, error: error.message });
      }
    });

    // 本地AI服务集成路由
    // 通用AI生成接口
    this.app.post('/api/local-ai/generate', async (req, res) => {
      try {
        if (!this.localAIConfig.enabled) {
          return res.status(503).json({ 
            success: false, 
            error: '本地AI服务未启用' 
          });
        }

        const { prompt, context = 'daily_greeting', max_length = 50, use_cache = true } = req.body;
        
        if (!prompt) {
          return res.status(400).json({ 
            success: false, 
            error: '缺少prompt参数' 
          });
        }

        const response = await this.callLocalAI('/generate', {
          prompt,
          context,
          max_length,
          use_cache
        });

        res.json(response);
      } catch (error) {
        console.error('本地AI生成失败:', error);
        res.status(500).json({ success: false, error: error.message });
      }
    });

    // 单词学习提示
    this.app.post('/api/local-ai/word-hint', async (req, res) => {
      try {
        if (!this.localAIConfig.enabled) {
          return res.status(503).json({ 
            success: false, 
            error: '本地AI服务未启用' 
          });
        }

        const { word, difficulty = 'intermediate' } = req.body;
        
        if (!word) {
          return res.status(400).json({ 
            success: false, 
            error: '缺少word参数' 
          });
        }

        const response = await this.callLocalAI('/word_hint', {
          word,
          difficulty
        });

        res.json(response);
      } catch (error) {
        console.error('单词提示生成失败:', error);
        res.status(500).json({ success: false, error: error.message });
      }
    });

    // 学习鼓励语
    this.app.post('/api/local-ai/encouragement', async (req, res) => {
      try {
        if (!this.localAIConfig.enabled) {
          return res.status(503).json({ 
            success: false, 
            error: '本地AI服务未启用' 
          });
        }

        const { 
          words_learned = 0, 
          accuracy = 0.0, 
          study_time = 0 
        } = req.body;

        const response = await this.callLocalAI('/encouragement', {
          words_learned,
          accuracy,
          study_time
        });

        res.json(response);
      } catch (error) {
        console.error('鼓励语生成失败:', error);
        res.status(500).json({ success: false, error: error.message });
      }
    });

    // 每日问候语
    this.app.post('/api/local-ai/greeting', async (req, res) => {
      try {
        if (!this.localAIConfig.enabled) {
          return res.status(503).json({ 
            success: false, 
            error: '本地AI服务未启用' 
          });
        }

        const { time_of_day = 'morning' } = req.body;

        const response = await this.callLocalAI('/greeting', {
          time_of_day
        });

        res.json(response);
      } catch (error) {
        console.error('问候语生成失败:', error);
        res.status(500).json({ success: false, error: error.message });
      }
    });

    // 概念解释
    this.app.post('/api/local-ai/explanation', async (req, res) => {
      try {
        if (!this.localAIConfig.enabled) {
          return res.status(503).json({ 
            success: false, 
            error: '本地AI服务未启用' 
          });
        }

        const { concept, user_level = 'beginner' } = req.body;
        
        if (!concept) {
          return res.status(400).json({ 
            success: false, 
            error: '缺少concept参数' 
          });
        }

        const response = await this.callLocalAI('/explanation', {
          concept,
          user_level
        });

        res.json(response);
      } catch (error) {
        console.error('概念解释生成失败:', error);
        res.status(500).json({ success: false, error: error.message });
      }
    });

    // 本地AI服务状态
    this.app.get('/api/local-ai/status', async (req, res) => {
      try {
        if (!this.localAIConfig.enabled) {
          return res.json({ 
            success: true, 
            data: { 
              enabled: false, 
              message: '本地AI服务未启用' 
            } 
          });
        }

        const response = await this.callLocalAI('/status', null, 'GET');
        res.json({ success: true, data: response });
      } catch (error) {
        console.error('获取本地AI状态失败:', error);
        res.status(500).json({ success: false, error: error.message });
      }
    });

    // 本地AI健康检查
    this.app.get('/api/local-ai/health', async (req, res) => {
      try {
        if (!this.localAIConfig.enabled) {
          return res.json({ 
            success: true, 
            data: { 
              status: 'disabled', 
              message: '本地AI服务未启用' 
            } 
          });
        }

        const response = await this.callLocalAI('/health', null, 'GET');
        res.json({ success: true, data: response });
      } catch (error) {
        console.error('本地AI健康检查失败:', error);
        res.status(500).json({ 
          success: false, 
          error: error.message,
          data: { status: 'unhealthy' }
        });
      }
    });

    // 清理本地AI缓存
    this.app.post('/api/local-ai/cache/clear', async (req, res) => {
      try {
        if (!this.localAIConfig.enabled) {
          return res.status(503).json({ 
            success: false, 
            error: '本地AI服务未启用' 
          });
        }

        const response = await this.callLocalAI('/cache/clear');
        res.json(response);
      } catch (error) {
        console.error('清理本地AI缓存失败:', error);
        res.status(500).json({ success: false, error: error.message });
      }
    });

    // 优化本地AI内存
    this.app.post('/api/local-ai/memory/optimize', async (req, res) => {
      try {
        if (!this.localAIConfig.enabled) {
          return res.status(503).json({ 
            success: false, 
            error: '本地AI服务未启用' 
          });
        }

        const response = await this.callLocalAI('/memory/optimize');
        res.json(response);
      } catch (error) {
        console.error('优化本地AI内存失败:', error);
        res.status(500).json({ success: false, error: error.message });
      }
    });

    // 混合AI服务路由
    this.app.get('/api/ai/services', async (req, res) => {
      try {
        res.json({
          success: true,
          data: {
            available_services: this.availableServices || [],
            preferred_service: this.preferredService,
            hybrid_enabled: !!this.aiConfig?.hybrid?.enabled,
            local_ai_enabled: this.localAIConfig.enabled
          }
        });
      } catch (error) {
        console.error('获取AI服务列表失败:', error);
        res.status(500).json({ success: false, error: error.message });
      }
    });

    this.app.post('/api/ai/switch-service', async (req, res) => {
      try {
        const { service_type } = req.body;
        
        if (!this.localAIConfig.enabled) {
          return res.status(400).json({
            success: false,
            error: '本地AI服务未启用，无法切换服务'
          });
        }

        const response = await this.callLocalAI('/switch_service', {
          service_type: service_type
        });
        
        res.json({ success: true, data: response });
      } catch (error) {
        console.error('切换AI服务失败:', error);
        res.status(500).json({ success: false, error: error.message });
      }
    });

    this.app.post('/api/ai/generate', async (req, res) => {
      try {
        const { prompt, context = 'daily_greeting', service_type, max_length = 256, temperature = 0.7 } = req.body;
        
        if (!this.localAIConfig.enabled) {
          // 如果本地AI未启用，尝试使用传统AI服务
          const response = await this.aiService.generateResponse(prompt, context);
          return res.json({
            success: true,
            response: response,
            metadata: {
              service: 'traditional',
              context: context,
              fallback: true
            }
          });
        }

        const response = await this.callLocalAI('/generate', {
          prompt,
          context,
          service_type,
          max_length,
          temperature
        });
        
        res.json({ success: true, ...response });
      } catch (error) {
        console.error('AI生成失败:', error);
        
        // 尝试回退到传统AI服务
        try {
          const fallbackResponse = await this.aiService.generateResponse(req.body.prompt, req.body.context || 'daily_greeting');
          res.json({
            success: true,
            response: fallbackResponse,
            metadata: {
              service: 'traditional',
              context: req.body.context || 'daily_greeting',
              fallback: true,
              original_error: error.message
            }
          });
        } catch (fallbackError) {
          res.status(500).json({ 
            success: false, 
            error: error.message,
            fallback_error: fallbackError.message
          });
        }
      }
    });

    this.app.get('/api/ai/config', async (req, res) => {
      try {
        const config = {
          hybrid_enabled: !!this.aiConfig?.hybrid?.enabled,
          available_services: this.availableServices || [],
          preferred_service: this.preferredService,
          local_ai: {
            enabled: this.localAIConfig.enabled,
            url: this.localAIConfig.url,
            timeout: this.localAIConfig.timeout
          },
          personality: this.aiConfig?.personality || {
            name: '长离',
            description: '温暖、智慧的AI学习伙伴'
          },
          supported_contexts: this.aiConfig?.personality?.contexts ? 
            Object.keys(this.aiConfig.personality.contexts) : 
            ['daily_greeting', 'word_learning', 'encouragement']
        };
        
        res.json({ success: true, data: config });
      } catch (error) {
        console.error('获取AI配置失败:', error);
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

  /**
   * 调用本地AI服务
   */
  async callLocalAI(endpoint, data = null, method = 'POST') {
    const axios = require('axios');
    
    try {
      const config = {
        method,
        url: `${this.localAIConfig.url}${endpoint}`,
        timeout: this.localAIConfig.timeout,
        headers: {
          'Content-Type': 'application/json'
        }
      };

      if (data && method === 'POST') {
        config.data = data;
      }

      let lastError;
      
      // 重试机制
      for (let attempt = 1; attempt <= this.localAIConfig.retryAttempts; attempt++) {
        try {
          const response = await axios(config);
          return response.data;
        } catch (error) {
          lastError = error;
          
          if (attempt < this.localAIConfig.retryAttempts) {
            console.warn(`本地AI请求失败，第${attempt}次重试...`);
            await new Promise(resolve => setTimeout(resolve, 1000 * attempt));
          }
        }
      }

      throw lastError;
      
    } catch (error) {
      console.error(`本地AI服务调用失败 ${endpoint}:`, error.message);
      
      // 返回友好的错误响应
      if (error.code === 'ECONNREFUSED') {
        throw new Error('本地AI服务未启动或无法连接');
      } else if (error.code === 'ETIMEDOUT') {
        throw new Error('本地AI服务响应超时');
      } else {
        throw new Error(`本地AI服务错误: ${error.message}`);
      }
    }
  }

  startServer() {
    this.server = this.app.listen(this.port, () => {
      console.log(`🚀 长离的学习胶囊后端服务已启动`);
      console.log(`📡 服务地址: http://localhost:${this.port}`);
      console.log(`🕐 启动时间: ${new Date().toLocaleString('zh-CN')}`);
      
      // Chronicle集成状态
      if (this.chronicleClient.getConnectionStatus().isConnected) {
        console.log(`📊 Chronicle集成服务已连接`);
      } else {
        console.log(`⚠️ Chronicle集成服务未连接，将在后台重试`);
      }
      
      // 本地AI服务状态
      if (this.localAIConfig.enabled) {
        console.log(`🤖 本地AI服务已启用: ${this.localAIConfig.url}`);
      } else {
        console.log(`⚠️ 本地AI服务未启用`);
      }
    });
  }

  /**
   * 优雅关闭服务器
   */
  async gracefulShutdown(signal) {
    console.log(`\n🛑 收到${signal}信号，正在优雅关闭服务器...`);
    
    try {
      // 停止接受新连接
      if (this.server) {
        this.server.close(() => {
          console.log('✅ HTTP服务器已关闭');
        });
      }

      // 清理Chronicle资源
      if (this.chronicleService) {
        await this.chronicleService.cleanup();
      }
      
      if (this.chronicleClient) {
        this.chronicleClient.disconnect();
      }

      // 关闭数据库连接
      if (this.db) {
        await this.db.close();
        console.log('✅ 数据库连接已关闭');
      }

      console.log('✅ 服务器优雅关闭完成');
      process.exit(0);
      
    } catch (error) {
      console.error('❌ 关闭服务器时发生错误:', error);
      process.exit(1);
    }
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
  server.gracefulShutdown('SIGINT');
});

process.on('SIGTERM', () => {
  server.gracefulShutdown('SIGTERM');
});

// 处理未捕获的异常
process.on('uncaughtException', (error) => {
  console.error('未捕获的异常:', error);
  server.gracefulShutdown('uncaughtException');
});

process.on('unhandledRejection', (reason, promise) => {
  console.error('未处理的Promise拒绝:', reason);
  server.gracefulShutdown('unhandledRejection');
});

module.exports = ChangleeServer;