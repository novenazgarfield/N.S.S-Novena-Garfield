import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import styled from 'styled-components';
import { 
  MessageCircle, BookOpen, Brain, TrendingUp, 
  Sparkles, FileText, Users, Clock, Target,
  Award, Zap, Heart
} from 'lucide-react';

const DashboardContainer = styled(motion.div)`
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  color: white;
`;

const WelcomeSection = styled(motion.div)`
  text-align: center;
  margin-bottom: 40px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  padding: 40px;
  backdrop-filter: blur(10px);
`;

const WelcomeTitle = styled.h1`
  font-size: 2.5rem;
  margin: 0 0 15px 0;
  background: linear-gradient(135deg, #4ecdc4, #44a08d);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
`;

const WelcomeSubtitle = styled.p`
  font-size: 1.2rem;
  opacity: 0.9;
  margin: 0 0 30px 0;
`;

const ChangleeAvatar = styled(motion.div)`
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background: linear-gradient(135deg, #ff9a9e, #fecfef);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 4rem;
  margin: 0 auto 20px;
  box-shadow: 0 10px 30px rgba(255, 154, 158, 0.3);
`;

const FeatureGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 25px;
  margin-bottom: 40px;
`;

const FeatureCard = styled(motion.div)`
  background: rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  padding: 30px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    background: rgba(255, 255, 255, 0.15);
    transform: translateY(-5px);
    box-shadow: 0 15px 35px rgba(0, 0, 0, 0.2);
  }
`;

const FeatureIcon = styled.div`
  width: 60px;
  height: 60px;
  border-radius: 15px;
  background: ${props => props.gradient || 'linear-gradient(135deg, #4ecdc4, #44a08d)'};
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 20px;
  font-size: 1.5rem;
`;

const FeatureTitle = styled.h3`
  font-size: 1.4rem;
  margin: 0 0 10px 0;
  color: white;
`;

const FeatureDescription = styled.p`
  font-size: 1rem;
  opacity: 0.9;
  line-height: 1.6;
  margin: 0;
`;

const StatsSection = styled(motion.div)`
  background: rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  padding: 30px;
  backdrop-filter: blur(10px);
  margin-bottom: 40px;
`;

const StatsTitle = styled.h2`
  text-align: center;
  margin: 0 0 30px 0;
  font-size: 1.8rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
`;

const StatsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
`;

const StatCard = styled.div`
  text-align: center;
  padding: 20px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 15px;
  border: 1px solid rgba(255, 255, 255, 0.1);
`;

const StatValue = styled.div`
  font-size: 2.5rem;
  font-weight: bold;
  margin-bottom: 5px;
  background: linear-gradient(135deg, #4ecdc4, #44a08d);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
`;

const StatLabel = styled.div`
  font-size: 0.9rem;
  opacity: 0.8;
`;

const QuickActions = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
`;

const ActionButton = styled(motion.button)`
  background: linear-gradient(135deg, ${props => props.gradient || '#4ecdc4, #44a08d'});
  border: none;
  border-radius: 15px;
  padding: 20px;
  color: white;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  
  &:hover {
    transform: translateY(-3px);
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
  }
`;

const Dashboard = () => {
  const [stats, setStats] = useState({
    wordsLearned: 0,
    studyDays: 0,
    accuracy: 0,
    documentsUploaded: 0
  });

  const [ragStatus, setRagStatus] = useState({
    connected: false,
    lastCheck: null
  });

  useEffect(() => {
    loadDashboardData();
    checkRAGStatus();
  }, []);

  const loadDashboardData = async () => {
    try {
      // 加载学习统计
      const response = await fetch('http://localhost:3001/api/stats');
      const data = await response.json();
      
      if (data.success) {
        setStats({
          wordsLearned: data.data.overall?.mastered_words || 0,
          studyDays: data.data.streakDays || 0,
          accuracy: Math.round(data.data.overall?.accuracy_rate || 0),
          documentsUploaded: 2 // 模拟数据
        });
      }
    } catch (error) {
      console.error('加载仪表板数据失败:', error);
    }
  };

  const checkRAGStatus = async () => {
    try {
      const response = await fetch('http://localhost:3001/api/rag/status');
      const data = await response.json();
      
      if (data.success) {
        setRagStatus({
          connected: data.data.isConnected,
          lastCheck: new Date()
        });
      }
    } catch (error) {
      console.error('检查RAG状态失败:', error);
      setRagStatus({
        connected: false,
        lastCheck: new Date()
      });
    }
  };

  const features = [
    {
      icon: <MessageCircle size={24} />,
      title: '🤖 智能问答',
      description: '向长离提问任何学习相关的问题，获得个性化的解答和建议。支持单词解释、语法帮助、学习方法等。',
      gradient: 'linear-gradient(135deg, #667eea, #764ba2)',
      action: () => {
        // 触发智能问答
        if (window.showIntelligentChat) {
          window.showIntelligentChat();
        }
      }
    },
    {
      icon: <BookOpen size={24} />,
      title: '📚 文档分析',
      description: '上传学习资料，让长离智能分析并提取重点单词。支持PDF、Word等多种格式。',
      gradient: 'linear-gradient(135deg, #4ecdc4, #44a08d)',
      action: () => {
        // 触发文档管理
        if (window.showDocumentManager) {
          window.showDocumentManager();
        }
      }
    },
    {
      icon: <Brain size={24} />,
      title: '🧠 个性化学习',
      description: '基于RAG技术的智能学习系统，根据你的学习进度和偏好提供定制化内容。',
      gradient: 'linear-gradient(135deg, #ff6b6b, #ee5a24)',
      action: () => {
        // 触发个性化学习
        console.log('个性化学习功能');
      }
    },
    {
      icon: <Sparkles size={24} />,
      title: '✨ AI内容生成',
      description: '长离会为每个单词生成专属的记忆故事、语境例句和学习技巧，让学习更有趣。',
      gradient: 'linear-gradient(135deg, #feca57, #ff9ff3)',
      action: () => {
        // 触发AI内容生成演示
        console.log('AI内容生成演示');
      }
    }
  ];

  return (
    <DashboardContainer
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
    >
      <WelcomeSection
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.2, duration: 0.5 }}
      >
        <ChangleeAvatar
          animate={{ 
            rotate: [0, 5, -5, 0],
            scale: [1, 1.05, 1]
          }}
          transition={{ 
            duration: 4, 
            repeat: Infinity,
            ease: "easeInOut"
          }}
        >
          🐱
        </ChangleeAvatar>
        
        <WelcomeTitle>欢迎来到长离的学习世界！</WelcomeTitle>
        <WelcomeSubtitle>
          我是长离，你的AI学习伙伴。现在我拥有了更强大的RAG智能问答能力，
          可以帮你分析文档、回答问题、制定学习计划！
        </WelcomeSubtitle>
        
        <div style={{ 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center', 
          gap: '10px',
          fontSize: '0.9rem',
          opacity: 0.8
        }}>
          <div style={{
            width: '8px',
            height: '8px',
            borderRadius: '50%',
            background: ragStatus.connected ? '#4ecdc4' : '#ff6b6b'
          }} />
          RAG系统状态: {ragStatus.connected ? '已连接' : '离线'}
          {ragStatus.lastCheck && (
            <span>• 最后检查: {ragStatus.lastCheck.toLocaleTimeString()}</span>
          )}
        </div>
      </WelcomeSection>

      <StatsSection
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4, duration: 0.5 }}
      >
        <StatsTitle>
          <TrendingUp size={24} />
          📊 学习统计
        </StatsTitle>
        
        <StatsGrid>
          <StatCard>
            <StatValue>{stats.wordsLearned}</StatValue>
            <StatLabel>已掌握单词</StatLabel>
          </StatCard>
          
          <StatCard>
            <StatValue>{stats.studyDays}</StatValue>
            <StatLabel>连续学习天数</StatLabel>
          </StatCard>
          
          <StatCard>
            <StatValue>{stats.accuracy}%</StatValue>
            <StatLabel>学习正确率</StatLabel>
          </StatCard>
          
          <StatCard>
            <StatValue>{stats.documentsUploaded}</StatValue>
            <StatLabel>上传文档数</StatLabel>
          </StatCard>
        </StatsGrid>
      </StatsSection>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6, duration: 0.5 }}
      >
        <h2 style={{ 
          textAlign: 'center', 
          marginBottom: '30px',
          fontSize: '1.8rem',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: '10px'
        }}>
          <Zap size={24} />
          🚀 核心功能
        </h2>
        
        <FeatureGrid>
          {features.map((feature, index) => (
            <FeatureCard
              key={index}
              onClick={feature.action}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.8 + index * 0.1, duration: 0.5 }}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <FeatureIcon gradient={feature.gradient}>
                {feature.icon}
              </FeatureIcon>
              <FeatureTitle>{feature.title}</FeatureTitle>
              <FeatureDescription>{feature.description}</FeatureDescription>
            </FeatureCard>
          ))}
        </FeatureGrid>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 1.0, duration: 0.5 }}
      >
        <h2 style={{ 
          textAlign: 'center', 
          marginBottom: '30px',
          fontSize: '1.8rem',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: '10px'
        }}>
          <Target size={24} />
          ⚡ 快捷操作
        </h2>
        
        <QuickActions>
          <ActionButton
            gradient="#667eea, #764ba2"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => console.log('开始学习')}
          >
            <BookOpen size={20} />
            开始学习新单词
          </ActionButton>
          
          <ActionButton
            gradient="#4ecdc4, #44a08d"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => console.log('智能问答')}
          >
            <MessageCircle size={20} />
            向长离提问
          </ActionButton>
          
          <ActionButton
            gradient="#ff6b6b, #ee5a24"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => console.log('上传文档')}
          >
            <FileText size={20} />
            上传学习资料
          </ActionButton>
          
          <ActionButton
            gradient="#feca57, #ff9ff3"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => console.log('查看进度')}
          >
            <Award size={20} />
            查看学习进度
          </ActionButton>
        </QuickActions>
      </motion.div>
    </DashboardContainer>
  );
};

export default Dashboard;