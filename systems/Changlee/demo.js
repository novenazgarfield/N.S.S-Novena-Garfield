#!/usr/bin/env node

/**
 * 长离的学习胶囊 - 演示脚本
 * 展示系统核心功能的简化版本
 */

const readline = require('readline');

// 创建命令行接口
const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

class ChangleeDemo {
  constructor() {
    this.currentWord = null;
    this.learningProgress = {
      wordsLearned: 0,
      correctAnswers: 0,
      totalAttempts: 0
    };
    
    // 示例单词数据
    this.sampleWords = [
      {
        id: 1,
        word: 'abandon',
        phonetic: '/əˈbændən/',
        definition: 'v. 放弃，抛弃',
        difficulty: 2,
        memoryStory: '我是长离，记得有一次在图书馆里，看到一本被abandon（放弃）的旧书静静躺在角落。那本书虽然被主人抛弃了，但里面的知识依然闪闪发光，就像你现在学习的每个单词一样珍贵呢～',
        contextStory: '在一个雨夜，小明不得不abandon他的计划。他原本想要坚持(persist)下去，但现实迫使他放弃(give up)了这个想法。有时候，abandon并不意味着失败，而是为了更好的选择。',
        tips: '记忆技巧：a-ban-don，想象"一个禁令让人放弃"\n常用搭配：abandon hope, abandon plan\n注意事项：不要与"abundant"(丰富的)混淆'
      },
      {
        id: 2,
        word: 'ability',
        phonetic: '/əˈbɪləti/',
        definition: 'n. 能力，才能',
        difficulty: 1,
        memoryStory: '我长离最喜欢看你展现学习的ability（能力）了！每当你掌握一个新单词，我就能感受到你的能力在不断增长，就像小猫咪的爪子越来越锋利一样～',
        contextStory: '她的ability让所有人印象深刻。这种能力(capability)不是天生的天赋(talent)，而是通过不断练习获得的技能(skill)。每个人都有提升自己ability的潜力。',
        tips: '记忆技巧：able(能够) + ity(名词后缀) = ability\n常用搭配：have the ability to, ability to learn\n注意事项：ability强调具体的能力，capability更强调潜在能力'
      },
      {
        id: 3,
        word: 'academic',
        phonetic: '/ˌækəˈdemɪk/',
        definition: 'adj. 学术的，理论的',
        difficulty: 2,
        memoryStory: '在academic（学术的）世界里，我长离就像一只博学的小猫，总是在知识的海洋中游泳。每当你学习academic词汇时，我都感到特别兴奋，因为这意味着你正在向更高的学术殿堂迈进！',
        contextStory: '这所大学以其academic excellence而闻名。学术(scholarly)研究需要严谨的态度，理论(theoretical)知识与实践相结合。academic成就不仅体现在成绩上，更体现在思维方式的转变。',
        tips: '记忆技巧：academy(学院) + ic(形容词后缀)\n常用搭配：academic year, academic achievement\n注意事项：academic有时含有"理论化、不实用"的含义'
      }
    ];
  }

  async start() {
    console.log('🐱 欢迎来到长离的学习胶囊演示！');
    console.log('=====================================');
    console.log('');
    console.log('🌟 我是长离，你的AI学习伙伴！');
    console.log('📚 让我们一起开始有趣的英语学习之旅吧～');
    console.log('');
    
    await this.showMainMenu();
  }

  async showMainMenu() {
    console.log('🎯 请选择你想体验的功能：');
    console.log('1. 📮 接收漂流瓶（获取新单词）');
    console.log('2. 💊 打开学习胶囊（查看单词详情）');
    console.log('3. 🏖️  魔法沙滩练习（拼写练习）');
    console.log('4. 📊 查看学习进度');
    console.log('5. 🤖 与长离聊天');
    console.log('6. 🚪 退出演示');
    console.log('');

    const choice = await this.askQuestion('请输入选项编号 (1-6): ');
    
    switch (choice.trim()) {
      case '1':
        await this.receiveBottle();
        break;
      case '2':
        await this.openLearningCapsule();
        break;
      case '3':
        await this.magicBeachPractice();
        break;
      case '4':
        await this.showProgress();
        break;
      case '5':
        await this.chatWithChanglee();
        break;
      case '6':
        await this.exit();
        return;
      default:
        console.log('❌ 无效选项，请重新选择');
        await this.showMainMenu();
    }
  }

  async receiveBottle() {
    console.log('\n🎬 桌宠动画：长离兴奋地跑向你...');
    await this.delay(1000);
    
    console.log('🐱 长离: "喵～我为你带来了一个特别的漂流瓶！"');
    await this.delay(1000);
    
    // 随机选择一个单词
    const randomIndex = Math.floor(Math.random() * this.sampleWords.length);
    this.currentWord = this.sampleWords[randomIndex];
    
    console.log('📮 漂流瓶缓缓打开...');
    console.log(`✨ 发现新单词: ${this.currentWord.word}`);
    console.log(`🔤 发音: ${this.currentWord.phonetic}`);
    console.log(`📝 含义: ${this.currentWord.definition}`);
    console.log('');
    console.log('🐱 长离: "这个单词很有趣呢！要不要打开学习胶囊看看更多内容？"');
    
    await this.delay(2000);
    await this.showMainMenu();
  }

  async openLearningCapsule() {
    if (!this.currentWord) {
      console.log('🐱 长离: "咦？你还没有接收漂流瓶呢！先去获取一个新单词吧～"');
      await this.delay(2000);
      await this.showMainMenu();
      return;
    }

    console.log('\n💊 学习胶囊正在打开...');
    await this.delay(1000);
    
    console.log('✨ 胶囊内容展示：');
    console.log('=====================================');
    console.log(`📚 单词: ${this.currentWord.word}`);
    console.log(`🔤 发音: ${this.currentWord.phonetic}`);
    console.log(`📝 定义: ${this.currentWord.definition}`);
    console.log(`⭐ 难度: ${this.currentWord.difficulty}/5`);
    console.log('');
    
    console.log('🐱 长离的记忆:');
    console.log(this.currentWord.memoryStory);
    console.log('');
    
    console.log('📖 语境故事:');
    console.log(this.currentWord.contextStory);
    console.log('');
    
    console.log('💡 学习技巧:');
    console.log(this.currentWord.tips);
    console.log('');
    
    const action = await this.askQuestion('选择操作: 1-开始练习 2-重新生成内容 3-返回主菜单: ');
    
    switch (action.trim()) {
      case '1':
        await this.magicBeachPractice();
        break;
      case '2':
        console.log('🤖 长离正在重新生成内容...');
        await this.delay(2000);
        console.log('✨ 内容已更新！（演示版本显示相同内容）');
        await this.delay(1000);
        await this.openLearningCapsule();
        break;
      case '3':
        await this.showMainMenu();
        break;
      default:
        await this.openLearningCapsule();
    }
  }

  async magicBeachPractice() {
    if (!this.currentWord) {
      console.log('🐱 长离: "需要先选择一个单词才能练习哦～"');
      await this.delay(2000);
      await this.showMainMenu();
      return;
    }

    console.log('\n🏖️  欢迎来到魔法沙滩！');
    console.log('=====================================');
    console.log('🌊 海浪轻柔地拍打着沙滩...');
    console.log('✨ 沙滩上出现了神奇的文字...');
    await this.delay(2000);
    
    console.log('\n📝 第一阶段：描摹练习');
    console.log(`请仔细观察单词: ${this.currentWord.word}`);
    console.log('虚线轮廓: ' + this.currentWord.word.split('').map(c => c === ' ' ? ' ' : '·').join(' '));
    console.log('（在真实应用中，你可以用鼠标在沙滩上描摹）');
    
    await this.askQuestion('按回车键完成描摹...');
    
    console.log('✅ 描摹完成！沙滩上留下了美丽的轨迹～');
    await this.delay(1000);
    
    console.log('\n✍️  第二阶段：拼写挑战');
    console.log(`📖 提示: ${this.currentWord.definition}`);
    
    let attempts = 0;
    let maxAttempts = 3;
    
    while (attempts < maxAttempts) {
      const userInput = await this.askQuestion('请输入单词: ');
      attempts++;
      this.learningProgress.totalAttempts++;
      
      if (userInput.toLowerCase().trim() === this.currentWord.word.toLowerCase()) {
        console.log('🎉 太棒了！拼写正确！');
        console.log('✨ 沙滩上绽放出美丽的烟花...');
        console.log('🎆 ✨ 🎇 ✨ 🎆');
        
        this.learningProgress.wordsLearned++;
        this.learningProgress.correctAnswers++;
        
        console.log('🐱 长离: "你真厉害！我为你感到骄傲～"');
        break;
      } else {
        console.log(`❌ 拼写错误，正确答案是: ${this.currentWord.word}`);
        
        if (attempts < maxAttempts) {
          console.log(`💪 还有 ${maxAttempts - attempts} 次机会，加油！`);
          
          // 给出提示
          const hint = this.currentWord.word.substring(0, Math.ceil(this.currentWord.word.length / 3)) + '...';
          console.log(`💡 提示: ${hint}`);
        } else {
          console.log('🐱 长离: "没关系，多练习几次就会记住的！我相信你～"');
        }
      }
    }
    
    await this.delay(2000);
    await this.showMainMenu();
  }

  async showProgress() {
    console.log('\n📊 学习进度报告');
    console.log('=====================================');
    console.log(`📚 已学单词: ${this.learningProgress.wordsLearned}`);
    console.log(`✅ 正确回答: ${this.learningProgress.correctAnswers}`);
    console.log(`📝 总尝试次数: ${this.learningProgress.totalAttempts}`);
    
    const accuracy = this.learningProgress.totalAttempts > 0 ? 
      ((this.learningProgress.correctAnswers / this.learningProgress.totalAttempts) * 100).toFixed(1) : 0;
    console.log(`🎯 正确率: ${accuracy}%`);
    
    console.log('');
    console.log('📈 学习建议:');
    
    if (accuracy >= 80) {
      console.log('🌟 你的表现很棒！可以尝试更难的单词了');
    } else if (accuracy >= 60) {
      console.log('💪 继续努力！多复习几遍会更好');
    } else {
      console.log('🤗 慢慢来，每个人都有自己的学习节奏');
    }
    
    console.log('');
    console.log('🐱 长离: "无论进度如何，我都会一直陪伴着你学习～"');
    
    await this.delay(3000);
    await this.showMainMenu();
  }

  async chatWithChanglee() {
    console.log('\n🐱 长离聊天模式');
    console.log('=====================================');
    console.log('🐱 长离: "喵～想和我聊什么呢？"');
    console.log('（输入 "bye" 返回主菜单）');
    console.log('');
    
    while (true) {
      const userMessage = await this.askQuestion('你: ');
      
      if (userMessage.toLowerCase().trim() === 'bye') {
        console.log('🐱 长离: "好的～回头见！继续加油学习哦～"');
        break;
      }
      
      // 简单的聊天回复逻辑
      const responses = [
        '🐱 长离: "喵～这很有趣呢！"',
        '🐱 长离: "我觉得你说得很对！"',
        '🐱 长离: "学习英语真的很有意思呢～"',
        '🐱 长离: "你今天学习得怎么样？"',
        '🐱 长离: "我最喜欢和你一起学习新单词了！"',
        '🐱 长离: "要不要再学一个新单词？"'
      ];
      
      const randomResponse = responses[Math.floor(Math.random() * responses.length)];
      console.log(randomResponse);
      console.log('');
    }
    
    await this.showMainMenu();
  }

  async exit() {
    console.log('\n🐱 长离: "谢谢你体验我的学习胶囊！"');
    console.log('✨ 希望你喜欢这次的演示～');
    console.log('📚 记住，学习是一个持续的过程，我会一直陪伴着你！');
    console.log('');
    console.log('🎯 完整版本功能:');
    console.log('• 真实的桌面宠物动画');
    console.log('• AI生成的个性化内容');
    console.log('• 科学的间隔重复算法');
    console.log('• 智能推送系统');
    console.log('• Canvas绘制的魔法沙滩');
    console.log('• 完整的学习统计和进度跟踪');
    console.log('');
    console.log('🚀 运行 "node start.js" 启动完整应用！');
    console.log('');
    console.log('👋 再见！期待与你的下次相遇～');
    
    rl.close();
  }

  askQuestion(question) {
    return new Promise((resolve) => {
      rl.question(question, resolve);
    });
  }

  delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

// 启动演示
const demo = new ChangleeDemo();
demo.start().catch(error => {
  console.error('演示过程中出现错误:', error);
  rl.close();
});