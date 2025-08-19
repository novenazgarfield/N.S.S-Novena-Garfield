import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import styled from 'styled-components';
import { Send, Upload, FileText, Brain, Sparkles, MessageCircle } from 'lucide-react';

const ChatContainer = styled(motion.div)`
  max-width: 800px;
  height: 600px;
  margin: 0 auto;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 20px;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 40px rgba(102, 126, 234, 0.3);
  overflow: hidden;
`;

const ChatHeader = styled.div`
  background: rgba(255, 255, 255, 0.1);
  padding: 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
`;

const HeaderTitle = styled.h2`
  color: white;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 1.5rem;
`;

const StatusIndicator = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 8px;
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.8);
`;

const StatusDot = styled.div`
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: ${props => props.connected ? '#4ecdc4' : '#ff6b6b'};
  animation: ${props => props.connected ? 'pulse 2s infinite' : 'none'};
  
  @keyframes pulse {
    0% { opacity: 1; }
    50% { opacity: 0.5; }
    100% { opacity: 1; }
  }
`;

const MessagesArea = styled.div`
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 15px;
  
  &::-webkit-scrollbar {
    width: 6px;
  }
  
  &::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 3px;
  }
  
  &::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.3);
    border-radius: 3px;
  }
`;

const Message = styled(motion.div)`
  display: flex;
  align-items: flex-start;
  gap: 12px;
  ${props => props.isUser ? 'flex-direction: row-reverse;' : ''}
`;

const MessageAvatar = styled.div`
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: ${props => props.isUser ? 
    'linear-gradient(135deg, #ff6b6b, #ee5a24)' : 
    'linear-gradient(135deg, #4ecdc4, #44a08d)'};
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  flex-shrink: 0;
`;

const MessageBubble = styled.div`
  max-width: 70%;
  padding: 15px 20px;
  border-radius: 20px;
  background: ${props => props.isUser ? 
    'rgba(255, 255, 255, 0.9)' : 
    'rgba(255, 255, 255, 0.1)'};
  color: ${props => props.isUser ? '#333' : 'white'};
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  line-height: 1.6;
  
  ${props => props.isUser ? `
    border-bottom-right-radius: 5px;
  ` : `
    border-bottom-left-radius: 5px;
  `}
`;

const MessageTime = styled.div`
  font-size: 0.8rem;
  opacity: 0.7;
  margin-top: 5px;
  ${props => props.isUser ? 'text-align: right;' : ''}
`;

const MessageSources = styled.div`
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid rgba(255, 255, 255, 0.2);
  font-size: 0.85rem;
  opacity: 0.8;
`;

const SourceItem = styled.div`
  display: flex;
  align-items: center;
  gap: 5px;
  margin: 3px 0;
`;

const InputArea = styled.div`
  padding: 20px;
  background: rgba(255, 255, 255, 0.1);
  border-top: 1px solid rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
`;

const InputContainer = styled.div`
  display: flex;
  gap: 10px;
  align-items: flex-end;
`;

const MessageInput = styled.textarea`
  flex: 1;
  min-height: 50px;
  max-height: 120px;
  padding: 15px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 15px;
  background: rgba(255, 255, 255, 0.9);
  color: #333;
  font-size: 1rem;
  resize: none;
  outline: none;
  
  &:focus {
    border-color: #4ecdc4;
    box-shadow: 0 0 20px rgba(78, 205, 196, 0.3);
  }
  
  &::placeholder {
    color: #999;
  }
`;

const ActionButton = styled(motion.button)`
  width: 50px;
  height: 50px;
  border: none;
  border-radius: 15px;
  background: ${props => props.primary ? 
    'linear-gradient(135deg, #4ecdc4, #44a08d)' : 
    'rgba(255, 255, 255, 0.2)'};
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(10px);
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(0,0,0,0.2);
  }
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    transform: none;
  }
`;

const QuickActions = styled.div`
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
  flex-wrap: wrap;
`;

const QuickActionButton = styled(motion.button)`
  padding: 8px 16px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.1);
  color: white;
  font-size: 0.9rem;
  cursor: pointer;
  backdrop-filter: blur(10px);
  
  &:hover {
    background: rgba(255, 255, 255, 0.2);
    border-color: rgba(255, 255, 255, 0.5);
  }
`;

const TypingIndicator = styled(motion.div)`
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 15px 20px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  border-bottom-left-radius: 5px;
  backdrop-filter: blur(10px);
  max-width: 200px;
`;

const TypingDots = styled.div`
  display: flex;
  gap: 4px;
  
  .dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.7);
    animation: typing 1.4s infinite ease-in-out;
    
    &:nth-child(1) { animation-delay: -0.32s; }
    &:nth-child(2) { animation-delay: -0.16s; }
  }
  
  @keyframes typing {
    0%, 80%, 100% { transform: scale(0.8); opacity: 0.5; }
    40% { transform: scale(1); opacity: 1; }
  }
`;

const IntelligentChat = ({ onClose }) => {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [ragStatus, setRagStatus] = useState({ connected: false });
  const messagesEndRef = useRef(null);

  const quickActions = [
    { text: '解释单词含义', type: 'word_explanation' },
    { text: '语法问题', type: 'grammar_help' },
    { text: '学习建议', type: 'learning_method' },
    { text: '练习题目', type: 'practice_request' },
    { text: '学习进度', type: 'progress_inquiry' }
  ];

  useEffect(() => {
    // 初始化聊天
    initializeChat();
    checkRAGStatus();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  const initializeChat = () => {
    const welcomeMessage = {
      id: Date.now(),
      text: '喵～你好！我是长离，你的AI学习伙伴！🐱\n\n我现在可以：\n• 回答各种英语学习问题\n• 解释单词和语法\n• 提供个性化学习建议\n• 分析你上传的学习资料\n• 陪你聊天解答疑惑\n\n有什么想问的吗？',
      isUser: false,
      timestamp: new Date(),
      sources: []
    };
    
    setMessages([welcomeMessage]);
  };

  const checkRAGStatus = async () => {
    try {
      if (window.backendAPI) {
        const response = await fetch('http://localhost:3001/api/rag/status');
        const data = await response.json();
        if (data.success) {
          setRagStatus(data.data);
        }
      }
    } catch (error) {
      console.error('检查RAG状态失败:', error);
      setRagStatus({ connected: false });
    }
  };

  const sendMessage = async (text, context = {}) => {
    if (!text.trim()) return;

    // 添加用户消息
    const userMessage = {
      id: Date.now(),
      text: text.trim(),
      isUser: true,
      timestamp: new Date()
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsTyping(true);

    try {
      // 调用RAG API
      const response = await fetch('http://localhost:3001/api/rag/ask', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          question: text,
          context: {
            conversationId: 'changlee_chat_' + Date.now(),
            userId: 'changlee_user',
            ...context
          }
        })
      });

      const data = await response.json();
      
      if (data.success && data.data) {
        const aiMessage = {
          id: Date.now() + 1,
          text: data.data.answer,
          isUser: false,
          timestamp: new Date(),
          sources: data.data.sources || [],
          fallback: data.data.fallback
        };
        
        setMessages(prev => [...prev, aiMessage]);
      } else {
        throw new Error('RAG响应格式错误');
      }
    } catch (error) {
      console.error('发送消息失败:', error);
      
      // 显示错误消息
      const errorMessage = {
        id: Date.now() + 1,
        text: '喵～我现在有点困，无法正常回答问题。请稍后再试，或者检查RAG系统是否正常运行。',
        isUser: false,
        timestamp: new Date(),
        sources: [],
        error: true
      };
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleQuickAction = (action) => {
    const prompts = {
      word_explanation: '请帮我解释一个英语单词的含义和用法',
      grammar_help: '我有一个英语语法问题需要帮助',
      learning_method: '请给我一些英语学习的建议和方法',
      practice_request: '请为我生成一些英语练习题',
      progress_inquiry: '请分析一下我的学习进度'
    };
    
    const prompt = prompts[action.type] || action.text;
    sendMessage(prompt, { type: action.type });
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage(inputValue);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const formatTime = (timestamp) => {
    return timestamp.toLocaleTimeString('zh-CN', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <ChatContainer
      initial={{ scale: 0.9, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      exit={{ scale: 0.9, opacity: 0 }}
      transition={{ type: "spring", stiffness: 300, damping: 30 }}
    >
      <ChatHeader>
        <HeaderTitle>
          <Brain size={24} />
          🐱 长离智能问答
        </HeaderTitle>
        <StatusIndicator>
          <StatusDot connected={ragStatus.connected} />
          {ragStatus.connected ? 'RAG系统已连接' : 'RAG系统离线'}
          {ragStatus.healthCheck && (
            <span>• 最后检查: {formatTime(new Date(ragStatus.healthCheck.timestamp))}</span>
          )}
        </StatusIndicator>
      </ChatHeader>

      <MessagesArea>
        <AnimatePresence>
          {messages.map((message) => (
            <Message
              key={message.id}
              isUser={message.isUser}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
            >
              <MessageAvatar isUser={message.isUser}>
                {message.isUser ? '👤' : '🐱'}
              </MessageAvatar>
              <div>
                <MessageBubble isUser={message.isUser}>
                  {message.text}
                  {message.sources && message.sources.length > 0 && (
                    <MessageSources>
                      <strong>📚 参考资料:</strong>
                      {message.sources.map((source, index) => (
                        <SourceItem key={index}>
                          <FileText size={12} />
                          {source.title || source.filename || `文档 ${index + 1}`}
                        </SourceItem>
                      ))}
                    </MessageSources>
                  )}
                  {message.fallback && (
                    <MessageSources>
                      💡 这是备用回答，RAG系统当前不可用
                    </MessageSources>
                  )}
                </MessageBubble>
                <MessageTime isUser={message.isUser}>
                  {formatTime(message.timestamp)}
                </MessageTime>
              </div>
            </Message>
          ))}
        </AnimatePresence>

        {isTyping && (
          <Message isUser={false}>
            <MessageAvatar isUser={false}>🐱</MessageAvatar>
            <TypingIndicator
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.8 }}
            >
              <TypingDots>
                <div className="dot"></div>
                <div className="dot"></div>
                <div className="dot"></div>
              </TypingDots>
              <span>长离正在思考...</span>
            </TypingIndicator>
          </Message>
        )}
        
        <div ref={messagesEndRef} />
      </MessagesArea>

      <InputArea>
        <QuickActions>
          {quickActions.map((action, index) => (
            <QuickActionButton
              key={index}
              onClick={() => handleQuickAction(action)}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              {action.text}
            </QuickActionButton>
          ))}
        </QuickActions>
        
        <InputContainer>
          <MessageInput
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="向长离提问任何学习相关的问题..."
            disabled={isTyping}
          />
          
          <ActionButton
            onClick={() => sendMessage(inputValue)}
            disabled={!inputValue.trim() || isTyping}
            primary
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <Send size={20} />
          </ActionButton>
          
          <ActionButton
            onClick={() => {/* TODO: 实现文件上传 */}}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <Upload size={20} />
          </ActionButton>
        </InputContainer>
      </InputArea>
    </ChatContainer>
  );
};

export default IntelligentChat;