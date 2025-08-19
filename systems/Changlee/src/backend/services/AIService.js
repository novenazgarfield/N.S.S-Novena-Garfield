const axios = require('axios');

class AIService {
  constructor() {
    // 从环境变量或配置文件获取API密钥
    this.apiKey = process.env.GEMINI_API_KEY || 'AIzaSyBOlNcGkx43zNOvnDesd_PEhD4Lj9T8Tpo';
    this.baseURL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent';
    
    // 长离的人设和背景
    this.changleePersonality = {
      name: '长离',
      personality: '温柔、耐心、充满智慧的AI伙伴',
      background: '一只来自知识海洋的神秘小猫，热爱学习和分享知识',
      speaking_style: '温暖亲切，善于用生动的故事和比喻来解释知识',
      relationship: '用户的专属学习伙伴和知心朋友'
    };
  }

  async generateLearningContent(wordData) {
    try {
      const { word, definition, phonetic, difficulty } = wordData;
      
      // 生成长离的记忆故事
      const memoryStory = await this.generateMemoryStory(word, definition, difficulty);
      
      // 生成语境故事
      const contextStory = await this.generateContextStory(word, definition, difficulty);
      
      // 生成学习提示
      const learningTips = await this.generateLearningTips(word, definition, difficulty);
      
      return {
        word,
        memoryStory,
        contextStory,
        learningTips,
        generatedAt: new Date().toISOString()
      };
    } catch (error) {
      console.error('AI内容生成失败:', error);
      throw new Error('AI内容生成失败，请稍后重试');
    }
  }

  async generateMemoryStory(word, definition, difficulty) {
    const prompt = `
你是长离，一只温柔智慧的小猫AI伙伴。请为单词"${word}"（${definition}）创作一个温馨的记忆故事。

要求：
1. 以第一人称"我"（长离）的视角讲述
2. 故事要温暖有趣，包含这个单词的使用场景
3. 体现长离的猫咪特质和温柔性格
4. 故事长度控制在100-150字
5. 难度等级：${difficulty}/5，请根据难度调整故事复杂度
6. 让用户感受到陪伴和鼓励

请直接返回故事内容，不要包含其他说明。
`;

    return await this.callGeminiAPI(prompt);
  }

  async generateContextStory(word, definition, difficulty) {
    const prompt = `
请为单词"${word}"（${definition}）创作一个生动的语境故事，帮助记忆和理解。

要求：
1. 故事要包含该单词的典型使用场景
2. 情节有趣，容易记忆
3. 自然地展示单词的含义和用法
4. 包含2-3个相关的同义词或关联词
5. 故事长度80-120字
6. 难度等级：${difficulty}/5
7. 语言生动，画面感强

请直接返回故事内容。
`;

    return await this.callGeminiAPI(prompt);
  }

  async generateLearningTips(word, definition, difficulty) {
    const prompt = `
为单词"${word}"（${definition}）提供实用的学习技巧和记忆方法。

要求：
1. 提供2-3个记忆技巧（如词根词缀、联想记忆等）
2. 给出常用搭配和例句
3. 指出容易混淆的相似词汇
4. 难度等级：${difficulty}/5
5. 语言简洁实用
6. 以长离的温柔语气给出建议

格式：
记忆技巧：...
常用搭配：...
注意事项：...
`;

    return await this.callGeminiAPI(prompt);
  }

  async generateEncouragementMessage(learningProgress) {
    const prompt = `
你是长离，用户的AI学习伙伴。根据用户的学习进度给出鼓励和建议。

学习数据：
- 今日学习单词：${learningProgress.todayWords}个
- 连续学习天数：${learningProgress.streakDays}天
- 总体正确率：${learningProgress.accuracy}%
- 当前等级：${learningProgress.level}

请以长离的温柔语气：
1. 对用户的进步给予肯定和鼓励
2. 提供个性化的学习建议
3. 体现猫咪的可爱特质
4. 长度控制在50-80字

请直接返回鼓励内容。
`;

    return await this.callGeminiAPI(prompt);
  }

  async generateDailyGreeting() {
    const currentHour = new Date().getHours();
    let timeOfDay = '早上';
    if (currentHour >= 12 && currentHour < 18) {
      timeOfDay = '下午';
    } else if (currentHour >= 18) {
      timeOfDay = '晚上';
    }

    const prompt = `
你是长离，一只温柔的AI猫咪伙伴。现在是${timeOfDay}，请生成一个温馨的问候语。

要求：
1. 体现猫咪的可爱特质
2. 根据时间段调整问候内容
3. 鼓励用户开始学习
4. 语气温暖亲切
5. 长度30-50字

请直接返回问候内容。
`;

    return await this.callGeminiAPI(prompt);
  }

  async callGeminiAPI(prompt) {
    try {
      const response = await axios.post(
        `${this.baseURL}?key=${this.apiKey}`,
        {
          contents: [{
            parts: [{
              text: prompt
            }]
          }],
          generationConfig: {
            temperature: 0.7,
            topK: 40,
            topP: 0.95,
            maxOutputTokens: 1024,
          },
          safetySettings: [
            {
              category: "HARM_CATEGORY_HARASSMENT",
              threshold: "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
              category: "HARM_CATEGORY_HATE_SPEECH",
              threshold: "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
              category: "HARM_CATEGORY_SEXUALLY_EXPLICIT",
              threshold: "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
              category: "HARM_CATEGORY_DANGEROUS_CONTENT",
              threshold: "BLOCK_MEDIUM_AND_ABOVE"
            }
          ]
        },
        {
          headers: {
            'Content-Type': 'application/json',
          },
          timeout: 30000
        }
      );

      if (response.data && response.data.candidates && response.data.candidates[0]) {
        const content = response.data.candidates[0].content.parts[0].text;
        return content.trim();
      } else {
        throw new Error('API响应格式异常');
      }
    } catch (error) {
      console.error('Gemini API调用失败:', error.response?.data || error.message);
      
      // 返回备用内容
      return this.getFallbackContent(prompt);
    }
  }

  getFallbackContent(prompt) {
    // 根据提示词类型返回不同的备用内容
    if (prompt.includes('记忆故事')) {
      return '我是长离，虽然现在无法为你生成专属的记忆故事，但我相信通过反复练习，你一定能掌握这个单词！让我们一起加油吧！🐱';
    } else if (prompt.includes('语境故事')) {
      return '这是一个很有用的单词，在日常生活中经常会遇到。建议你多看一些例句，理解它在不同语境中的用法。';
    } else if (prompt.includes('学习技巧')) {
      return '记忆技巧：可以通过联想记忆法来记住这个单词\n常用搭配：建议查看词典了解更多搭配\n注意事项：注意区分相似词汇的含义差别';
    } else if (prompt.includes('鼓励')) {
      return '你今天的学习很棒！继续保持这样的学习节奏，相信你会越来越优秀的！我会一直陪伴着你～ 🐱💕';
    } else {
      return '喵～虽然我现在有点困，但我会努力为你提供更好的学习体验！';
    }
  }

  // 检查API连接状态
  async checkAPIStatus() {
    try {
      const testPrompt = '请回复"连接正常"';
      const response = await this.callGeminiAPI(testPrompt);
      return { status: 'connected', response };
    } catch (error) {
      return { status: 'error', error: error.message };
    }
  }
}

module.exports = AIService;