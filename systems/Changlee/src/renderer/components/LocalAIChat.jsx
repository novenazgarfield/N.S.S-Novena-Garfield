/**
 * 本地AI聊天组件
 * 与长离的本地AI核心进行交互
 */

import React, { useState, useEffect, useRef } from 'react';
import './LocalAIChat.css';

const LocalAIChat = () => {
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [aiStatus, setAiStatus] = useState(null);
  const [currentContext, setCurrentContext] = useState('daily_greeting');
  const [showSettings, setShowSettings] = useState(false);
  const messagesEndRef = useRef(null);

  // 上下文类型
  const contextTypes = {
    'daily_greeting': { name: '日常问候', icon: '👋', color: '#4CAF50' },
    'word_learning': { name: '单词学习', icon: '📚', color: '#2196F3' },
    'spelling_practice': { name: '拼写练习', icon: '✏️', color: '#FF9800' },
    'encouragement': { name: '学习鼓励', icon: '💪', color: '#E91E63' },
    'explanation': { name: '概念解释', icon: '💡', color: '#9C27B0' }
  };

  // 初始化时检查AI状态
  useEffect(() => {
    checkAIStatus();
    addWelcomeMessage();
  }, []);

  // 自动滚动到底部
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const checkAIStatus = async () => {
    try {
      const response = await fetch('/api/local-ai/health');
      const result = await response.json();
      setAiStatus(result.data);
    } catch (error) {
      console.error('检查AI状态失败:', error);
      setAiStatus({ status: 'error', message: '无法连接到AI服务' });
    }
  };

  const addWelcomeMessage = () => {
    const welcomeMessage = {
      id: Date.now(),
      type: 'ai',
      content: '你好！我是长离，你的本地AI学习伙伴~ 有什么可以帮助你的吗？',
      timestamp: new Date(),
      context: 'daily_greeting'
    };
    setMessages([welcomeMessage]);
  };

  const sendMessage = async () => {
    if (!inputText.trim() || isLoading) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: inputText,
      timestamp: new Date(),
      context: currentContext
    };

    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setIsLoading(true);

    try {
      const response = await fetch('/api/local-ai/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          prompt: inputText,
          context: currentContext,
          max_length: 80,
          use_cache: true
        })
      });

      const result = await response.json();

      if (result.success) {
        const aiMessage = {
          id: Date.now() + 1,
          type: 'ai',
          content: result.response,
          timestamp: new Date(),
          context: currentContext,
          metadata: result.metadata,
          fromCache: result.from_cache
        };
        setMessages(prev => [...prev, aiMessage]);
      } else {
        throw new Error(result.error || '生成响应失败');
      }
    } catch (error) {
      console.error('发送消息失败:', error);
      const errorMessage = {
        id: Date.now() + 1,
        type: 'ai',
        content: '抱歉，我遇到了一些问题，请稍后再试~',
        timestamp: new Date(),
        context: currentContext,
        isError: true
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const quickActions = [
    {
      label: '每日问候',
      action: () => generateQuickResponse('greeting', { time_of_day: getTimeOfDay() })
    },
    {
      label: '学习鼓励',
      action: () => generateQuickResponse('encouragement', { 
        words_learned: 5, 
        accuracy: 0.8, 
        study_time: 30 
      })
    },
    {
      label: '单词提示',
      action: () => {
        const word = prompt('请输入要学习的单词:');
        if (word) {
          generateQuickResponse('word_hint', { word, difficulty: 'intermediate' });
        }
      }
    }
  ];

  const generateQuickResponse = async (type, params) => {
    setIsLoading(true);
    
    try {
      let endpoint = '';
      let requestBody = {};
      
      switch (type) {
        case 'greeting':
          endpoint = '/api/local-ai/greeting';
          requestBody = { time_of_day: params.time_of_day };
          break;
        case 'encouragement':
          endpoint = '/api/local-ai/encouragement';
          requestBody = params;
          break;
        case 'word_hint':
          endpoint = '/api/local-ai/word-hint';
          requestBody = params;
          break;
        default:
          throw new Error('未知的快捷操作类型');
      }

      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestBody)
      });

      const result = await response.json();

      if (result.success) {
        const aiMessage = {
          id: Date.now(),
          type: 'ai',
          content: result.response,
          timestamp: new Date(),
          context: result.context || type,
          metadata: result.metadata,
          isQuickAction: true
        };
        setMessages(prev => [...prev, aiMessage]);
      } else {
        throw new Error(result.error || '快捷操作失败');
      }
    } catch (error) {
      console.error('快捷操作失败:', error);
      const errorMessage = {
        id: Date.now(),
        type: 'ai',
        content: '快捷操作失败，请稍后再试~',
        timestamp: new Date(),
        isError: true
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const getTimeOfDay = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'morning';
    if (hour < 18) return 'afternoon';
    return 'evening';
  };

  const clearChat = () => {
    setMessages([]);
    addWelcomeMessage();
  };

  const optimizeMemory = async () => {
    try {
      const response = await fetch('/api/local-ai/memory/optimize', {
        method: 'POST'
      });
      const result = await response.json();
      
      if (result.success) {
        alert('内存优化完成！');
      } else {
        alert('内存优化失败: ' + result.error);
      }
    } catch (error) {
      alert('内存优化失败: ' + error.message);
    }
  };

  return (
    <div className="local-ai-chat">
      <div className="chat-header">
        <div className="header-left">
          <div className="ai-avatar">🤖</div>
          <div className="ai-info">
            <h3>长离 AI</h3>
            <div className="ai-status">
              <span className={`status-dot ${aiStatus?.status || 'unknown'}`}></span>
              <span className="status-text">
                {aiStatus?.status === 'healthy' ? '在线' : 
                 aiStatus?.status === 'loading' ? '加载中' : 
                 aiStatus?.status === 'disabled' ? '已禁用' : '离线'}
              </span>
            </div>
          </div>
        </div>
        
        <div className="header-actions">
          <button 
            className="context-selector"
            onClick={() => setShowSettings(!showSettings)}
          >
            <span className="context-icon">
              {contextTypes[currentContext]?.icon}
            </span>
            <span className="context-name">
              {contextTypes[currentContext]?.name}
            </span>
          </button>
          
          <button onClick={clearChat} className="clear-btn" title="清空对话">
            🗑️
          </button>
          
          <button onClick={optimizeMemory} className="optimize-btn" title="优化内存">
            ⚡
          </button>
        </div>
      </div>

      {showSettings && (
        <div className="settings-panel">
          <h4>对话上下文</h4>
          <div className="context-options">
            {Object.entries(contextTypes).map(([key, config]) => (
              <button
                key={key}
                className={`context-option ${currentContext === key ? 'active' : ''}`}
                onClick={() => {
                  setCurrentContext(key);
                  setShowSettings(false);
                }}
                style={{ borderColor: config.color }}
              >
                <span className="option-icon">{config.icon}</span>
                <span className="option-name">{config.name}</span>
              </button>
            ))}
          </div>
        </div>
      )}

      <div className="chat-messages">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`message ${message.type} ${message.isError ? 'error' : ''}`}
          >
            <div className="message-avatar">
              {message.type === 'user' ? '👤' : '🤖'}
            </div>
            
            <div className="message-content">
              <div className="message-text">{message.content}</div>
              
              <div className="message-meta">
                <span className="message-time">
                  {message.timestamp.toLocaleTimeString('zh-CN', { 
                    hour: '2-digit', 
                    minute: '2-digit' 
                  })}
                </span>
                
                {message.context && (
                  <span className="message-context">
                    {contextTypes[message.context]?.icon} {contextTypes[message.context]?.name}
                  </span>
                )}
                
                {message.fromCache && (
                  <span className="cache-indicator" title="来自缓存">💾</span>
                )}
                
                {message.isQuickAction && (
                  <span className="quick-action-indicator" title="快捷操作">⚡</span>
                )}
              </div>
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div className="message ai loading">
            <div className="message-avatar">🤖</div>
            <div className="message-content">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      <div className="quick-actions">
        {quickActions.map((action, index) => (
          <button
            key={index}
            className="quick-action-btn"
            onClick={action.action}
            disabled={isLoading}
          >
            {action.label}
          </button>
        ))}
      </div>

      <div className="chat-input">
        <div className="input-container">
          <textarea
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="和长离聊聊吧..."
            disabled={isLoading || aiStatus?.status !== 'healthy'}
            rows={1}
          />
          
          <button
            onClick={sendMessage}
            disabled={!inputText.trim() || isLoading || aiStatus?.status !== 'healthy'}
            className="send-btn"
          >
            {isLoading ? '⏳' : '📤'}
          </button>
        </div>
        
        <div className="input-hint">
          按 Enter 发送，Shift + Enter 换行
        </div>
      </div>
    </div>
  );
};

export default LocalAIChat;