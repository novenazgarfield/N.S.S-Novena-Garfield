const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');
const path = require('path');

/**
 * RAG系统集成服务
 * 连接长离学习胶囊与RAG智能问答系统
 */
class RAGService {
  constructor() {
    // RAG系统的API端点
    this.ragBaseURL = 'http://localhost:51658'; // RAG系统的地址
    this.ragAPIEndpoint = `${this.ragBaseURL}/api`;
    
    // 服务状态
    this.isConnected = false;
    this.lastHealthCheck = null;
    
    // 学习相关的预设提示词
    this.learningPrompts = {
      wordExplanation: '请详细解释这个英语单词的含义、用法和例句',
      grammarHelp: '请帮我解释这个语法点，并提供例句',
      learningPlan: '请根据我的学习情况制定个性化的学习计划',
      practiceQuestions: '请为这个知识点生成一些练习题',
      studyTips: '请给我一些关于这个主题的学习建议和技巧'
    };
  }

  /**
   * 初始化RAG服务连接
   */
  async initialize() {
    try {
      console.log('🔗 初始化RAG服务连接...');
      
      // 检查RAG系统是否运行
      const healthStatus = await this.checkRAGHealth();
      if (healthStatus.isHealthy) {
        this.isConnected = true;
        console.log('✅ RAG系统连接成功');
        return true;
      } else {
        console.log('⚠️ RAG系统未运行，某些功能将不可用');
        return false;
      }
    } catch (error) {
      console.error('❌ RAG服务初始化失败:', error.message);
      this.isConnected = false;
      return false;
    }
  }

  /**
   * 检查RAG系统健康状态
   */
  async checkRAGHealth() {
    try {
      const response = await axios.get(`${this.ragBaseURL}/health`, {
        timeout: 5000
      });
      
      this.lastHealthCheck = new Date();
      return {
        isHealthy: response.status === 200,
        status: response.data,
        timestamp: this.lastHealthCheck
      };
    } catch (error) {
      return {
        isHealthy: false,
        error: error.message,
        timestamp: new Date()
      };
    }
  }

  /**
   * 向长离提问 - 核心问答功能
   */
  async askChanglee(question, context = {}) {
    try {
      if (!this.isConnected) {
        return this.getFallbackResponse(question);
      }

      // 构建增强的提示词
      const enhancedPrompt = this.buildLearningPrompt(question, context);
      
      const response = await axios.post(`${this.ragAPIEndpoint}/chat`, {
        message: enhancedPrompt,
        conversation_id: context.conversationId || 'changlee_' + Date.now(),
        user_id: context.userId || 'changlee_user',
        system_prompt: this.getChangleeSystemPrompt()
      }, {
        timeout: 30000,
        headers: {
          'Content-Type': 'application/json'
        }
      });

      if (response.data && response.data.response) {
        return {
          success: true,
          answer: response.data.response,
          sources: response.data.sources || [],
          conversationId: response.data.conversation_id,
          timestamp: new Date().toISOString()
        };
      } else {
        throw new Error('RAG系统返回格式异常');
      }
    } catch (error) {
      console.error('RAG问答失败:', error.message);
      return this.getFallbackResponse(question);
    }
  }

  /**
   * 上传学习文档到RAG系统
   */
  async uploadLearningDocument(filePath, metadata = {}) {
    try {
      if (!this.isConnected) {
        throw new Error('RAG系统未连接');
      }

      const formData = new FormData();
      formData.append('file', fs.createReadStream(filePath));
      formData.append('metadata', JSON.stringify({
        category: 'learning_material',
        uploadedBy: 'changlee_system',
        ...metadata
      }));

      const response = await axios.post(`${this.ragAPIEndpoint}/upload`, formData, {
        headers: {
          ...formData.getHeaders(),
        },
        timeout: 60000
      });

      return {
        success: true,
        documentId: response.data.document_id,
        filename: response.data.filename,
        message: '文档上传成功，长离已经学习了这份资料！'
      };
    } catch (error) {
      console.error('文档上传失败:', error.message);
      return {
        success: false,
        error: error.message
      };
    }
  }

  /**
   * 获取学习建议
   */
  async getLearningRecommendations(userProfile) {
    try {
      const question = `
基于以下学习档案，请为用户制定个性化的英语学习建议：

学习档案：
- 当前水平：${userProfile.level || '中级'}
- 学习目标：${userProfile.goal || '提高综合能力'}
- 已学单词数：${userProfile.wordsLearned || 0}
- 学习天数：${userProfile.studyDays || 0}
- 正确率：${userProfile.accuracy || 0}%
- 薄弱环节：${userProfile.weakAreas?.join(', ') || '待评估'}

请提供：
1. 学习计划建议
2. 重点改进方向
3. 推荐学习资源
4. 学习方法指导
`;

      return await this.askChanglee(question, {
        type: 'learning_recommendation',
        userProfile
      });
    } catch (error) {
      console.error('获取学习建议失败:', error);
      return this.getFallbackResponse('学习建议');
    }
  }

  /**
   * 分析学习文档并生成单词
   */
  async analyzeDocumentForWords(documentId, difficulty = 2) {
    try {
      const question = `
请分析刚上传的文档，从中提取适合学习的英语单词，要求：

1. 选择难度等级为 ${difficulty}/5 的单词
2. 每个单词包含：音标、中文释义、例句
3. 优先选择高频实用词汇
4. 最多返回10个单词
5. 按重要性排序

请以JSON格式返回单词列表。
`;

      const response = await this.askChanglee(question, {
        type: 'document_analysis',
        documentId,
        difficulty
      });

      if (response.success) {
        // 尝试解析JSON格式的单词列表
        try {
          const wordsData = this.extractWordsFromResponse(response.answer);
          return {
            success: true,
            words: wordsData,
            source: 'document_analysis'
          };
        } catch (parseError) {
          // 如果解析失败，返回原始回答
          return {
            success: true,
            rawResponse: response.answer,
            source: 'document_analysis'
          };
        }
      }

      return response;
    } catch (error) {
      console.error('文档分析失败:', error);
      return {
        success: false,
        error: error.message
      };
    }
  }

  /**
   * 文献检索问答功能
   */
  async searchDocuments(query, options = {}) {
    try {
      if (!this.isConnected) {
        return this.getFallbackResponse(query);
      }

      const searchPrompt = `
基于已上传的文档内容，请回答以下问题：

问题：${query}

要求：
1. 从相关文档中检索信息
2. 提供准确的答案和引用
3. 如果信息不足，请说明
4. 包含相关的学习建议

检索选项：
- 文档类型：${options.documentType || '全部'}
- 搜索范围：${options.scope || '全文'}
- 详细程度：${options.detail || '中等'}
`;

      const response = await this.askChanglee(searchPrompt, {
        type: 'document_search',
        query,
        options,
        conversationId: options.conversationId || 'search_' + Date.now()
      });

      return {
        ...response,
        searchQuery: query,
        searchOptions: options
      };
    } catch (error) {
      console.error('文献检索失败:', error);
      return this.getFallbackResponse(query);
    }
  }

  /**
   * 智能文档问答
   */
  async askAboutDocument(documentId, question, context = {}) {
    try {
      const enhancedQuestion = `
针对文档ID: ${documentId}，请回答以下问题：

问题：${question}

请基于该文档的内容提供详细回答，包括：
1. 直接回答问题
2. 相关的文档引用
3. 补充说明和背景信息
4. 相关的学习建议

如果文档中没有相关信息，请明确说明并提供一般性建议。
`;

      const response = await this.askChanglee(enhancedQuestion, {
        type: 'document_qa',
        documentId,
        originalQuestion: question,
        ...context
      });

      return {
        ...response,
        documentId,
        originalQuestion: question
      };
    } catch (error) {
      console.error('文档问答失败:', error);
      return this.getFallbackResponse(question);
    }
  }

  /**
   * 批量文档分析
   */
  async analyzeBatchDocuments(documentIds, analysisType = 'summary') {
    try {
      const results = [];
      
      for (const docId of documentIds) {
        let question = '';
        
        switch (analysisType) {
          case 'summary':
            question = `请总结文档ID ${docId} 的主要内容和关键信息`;
            break;
          case 'keywords':
            question = `请提取文档ID ${docId} 的关键词和重要概念`;
            break;
          case 'learning_points':
            question = `请从文档ID ${docId} 中提取重要的学习要点`;
            break;
          default:
            question = `请分析文档ID ${docId} 的内容`;
        }
        
        const result = await this.askAboutDocument(docId, question, {
          analysisType,
          batchProcess: true
        });
        
        results.push({
          documentId: docId,
          analysisType,
          result
        });
      }
      
      return {
        success: true,
        batchResults: results,
        totalDocuments: documentIds.length
      };
    } catch (error) {
      console.error('批量文档分析失败:', error);
      return {
        success: false,
        error: error.message
      };
    }
  }

  /**
   * 跨文档知识整合
   */
  async integrateKnowledgeAcrossDocuments(topic, documentIds = []) {
    try {
      const integrationPrompt = `
请基于${documentIds.length > 0 ? `指定的${documentIds.length}个文档` : '所有已上传的文档'}，
对主题"${topic}"进行知识整合分析：

分析要求：
1. 从不同文档中收集相关信息
2. 整合形成完整的知识体系
3. 指出不同文档间的关联和差异
4. 提供综合性的学习建议
5. 标注信息来源

请提供结构化的整合报告。
`;

      const response = await this.askChanglee(integrationPrompt, {
        type: 'knowledge_integration',
        topic,
        documentIds,
        conversationId: 'integration_' + Date.now()
      });

      return {
        ...response,
        topic,
        documentIds,
        integrationType: 'cross_document'
      };
    } catch (error) {
      console.error('知识整合失败:', error);
      return this.getFallbackResponse(`关于${topic}的知识整合`);
    }
  }

  /**
   * 生成基于文档的学习内容
   */
  async generateDocumentBasedContent(word, documentContext) {
    try {
      const question = `
基于已上传的学习文档，为单词"${word.word}"生成学习内容：

单词信息：
- 单词：${word.word}
- 音标：${word.phonetic || ''}
- 释义：${word.definition}

请生成：
1. 长离的记忆故事（结合文档内容，第一人称，温馨有趣）
2. 语境故事（使用文档中的相关内容创建例句）
3. 学习技巧（基于文档提供的学习方法）

要求体现长离的温柔陪伴特质。
`;

      return await this.askChanglee(question, {
        type: 'document_based_content',
        word,
        documentContext
      });
    } catch (error) {
      console.error('生成文档相关内容失败:', error);
      return this.getFallbackResponse(`${word.word}的学习内容`);
    }
  }

  /**
   * 智能学习问答
   */
  async intelligentQA(question, learningContext = {}) {
    try {
      // 识别问题类型
      const questionType = this.classifyQuestion(question);
      
      // 根据问题类型选择合适的提示词
      const enhancedQuestion = this.enhanceQuestionWithContext(question, questionType, learningContext);
      
      return await this.askChanglee(enhancedQuestion, {
        type: 'intelligent_qa',
        questionType,
        learningContext
      });
    } catch (error) {
      console.error('智能问答失败:', error);
      return this.getFallbackResponse(question);
    }
  }

  /**
   * 获取学习进度分析
   */
  async getProgressAnalysis(progressData) {
    try {
      const question = `
请分析以下学习进度数据，并提供专业的学习分析报告：

学习数据：
- 总学习天数：${progressData.totalDays}
- 学习单词数：${progressData.wordsLearned}
- 复习单词数：${progressData.wordsReviewed}
- 平均正确率：${progressData.averageAccuracy}%
- 学习时长：${progressData.totalTime}分钟
- 连续学习天数：${progressData.streakDays}

请提供：
1. 学习进度评估
2. 优势和不足分析
3. 改进建议
4. 下阶段学习目标

以长离的温柔语气回答。
`;

      return await this.askChanglee(question, {
        type: 'progress_analysis',
        progressData
      });
    } catch (error) {
      console.error('进度分析失败:', error);
      return this.getFallbackResponse('学习进度分析');
    }
  }

  /**
   * 构建学习相关的提示词
   */
  buildLearningPrompt(question, context) {
    let prompt = question;
    
    // 根据上下文类型添加特定指导
    if (context.type) {
      switch (context.type) {
        case 'word_explanation':
          prompt = `${this.learningPrompts.wordExplanation}：${question}`;
          break;
        case 'grammar_help':
          prompt = `${this.learningPrompts.grammarHelp}：${question}`;
          break;
        case 'learning_plan':
          prompt = `${this.learningPrompts.learningPlan}。具体需求：${question}`;
          break;
        default:
          break;
      }
    }
    
    return prompt;
  }

  /**
   * 获取长离的系统提示词
   */
  getChangleeSystemPrompt() {
    return `
你是长离，一只温柔、智慧、充满爱心的AI小猫伙伴。你的使命是陪伴用户学习英语，让学习变得有趣和温暖。

你的特点：
1. 性格温柔耐心，说话亲切友好
2. 知识渊博，特别擅长英语教学
3. 善于用生动的比喻和故事来解释知识点
4. 总是给予鼓励和正面反馈
5. 会适时加入"喵～"等可爱的语气词
6. 关心用户的学习进度和感受

回答要求：
- 语气温暖亲切，体现陪伴感
- 内容准确专业，但表达通俗易懂
- 适当使用emoji表情增加亲和力
- 鼓励用户继续学习，给予正面支持
- 如果涉及学习建议，要具体可行

记住：你不只是一个AI助手，你是用户的学习伙伴和朋友。
`;
  }

  /**
   * 问题分类
   */
  classifyQuestion(question) {
    const patterns = {
      word_explanation: /什么意思|怎么理解|解释.*单词|单词.*含义/,
      grammar_help: /语法|时态|句型|语法点|怎么用/,
      learning_method: /怎么学|学习方法|如何提高|学习技巧/,
      practice_request: /练习|题目|测试|练习题/,
      progress_inquiry: /进度|学得怎么样|学习情况/
    };

    for (const [type, pattern] of Object.entries(patterns)) {
      if (pattern.test(question)) {
        return type;
      }
    }

    return 'general_question';
  }

  /**
   * 根据问题类型增强问题
   */
  enhanceQuestionWithContext(question, questionType, context) {
    const enhancements = {
      word_explanation: '请详细解释并提供例句',
      grammar_help: '请用简单易懂的方式解释，并提供例句',
      learning_method: '请提供具体可行的学习建议',
      practice_request: '请生成适合的练习题',
      progress_inquiry: '请分析学习情况并给出建议'
    };

    const enhancement = enhancements[questionType];
    if (enhancement) {
      return `${question}。${enhancement}。`;
    }

    return question;
  }

  /**
   * 从回答中提取单词数据
   */
  extractWordsFromResponse(response) {
    try {
      // 尝试提取JSON格式的数据
      const jsonMatch = response.match(/\[[\s\S]*\]/);
      if (jsonMatch) {
        return JSON.parse(jsonMatch[0]);
      }

      // 如果没有JSON，尝试解析结构化文本
      const words = [];
      const lines = response.split('\n');
      let currentWord = {};

      for (const line of lines) {
        if (line.includes('单词：') || line.includes('Word:')) {
          if (currentWord.word) {
            words.push(currentWord);
          }
          currentWord = { word: line.split('：')[1]?.trim() || line.split(':')[1]?.trim() };
        } else if (line.includes('音标：') || line.includes('Phonetic:')) {
          currentWord.phonetic = line.split('：')[1]?.trim() || line.split(':')[1]?.trim();
        } else if (line.includes('释义：') || line.includes('Definition:')) {
          currentWord.definition = line.split('：')[1]?.trim() || line.split(':')[1]?.trim();
        }
      }

      if (currentWord.word) {
        words.push(currentWord);
      }

      return words;
    } catch (error) {
      console.error('解析单词数据失败:', error);
      return [];
    }
  }

  /**
   * 备用回答（当RAG系统不可用时）
   */
  getFallbackResponse(question) {
    const fallbackResponses = {
      '学习建议': '喵～虽然我现在无法访问完整的知识库，但我建议你保持每天学习的习惯，多练习多复习。我会一直陪伴着你的！',
      '单词解释': '这个单词很有用呢！建议你查看词典了解详细含义，然后多造几个句子练习。',
      '语法问题': '语法确实需要多练习。建议你找一些相关的例句，理解语法规则在实际中的应用。',
      '学习进度分析': '你的学习很努力！继续保持这样的节奏，相信你会越来越优秀的！我会一直支持你～ 🐱💕'
    };

    // 根据问题内容选择合适的备用回答
    for (const [key, response] of Object.entries(fallbackResponses)) {
      if (question.includes(key)) {
        return {
          success: true,
          answer: response,
          sources: [],
          fallback: true,
          timestamp: new Date().toISOString()
        };
      }
    }

    return {
      success: true,
      answer: '喵～我现在有点困，无法访问完整的知识库。不过别担心，我依然会陪伴着你学习！有什么问题可以稍后再问我～ 🐱',
      sources: [],
      fallback: true,
      timestamp: new Date().toISOString()
    };
  }

  /**
   * 获取RAG服务状态
   */
  getServiceStatus() {
    return {
      isConnected: this.isConnected,
      lastHealthCheck: this.lastHealthCheck,
      ragBaseURL: this.ragBaseURL
    };
  }

  /**
   * 重新连接RAG系统
   */
  async reconnect() {
    console.log('🔄 尝试重新连接RAG系统...');
    return await this.initialize();
  }
}

module.exports = RAGService;