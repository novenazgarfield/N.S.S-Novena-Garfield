import React, { useRef, useEffect } from 'react';
import { useRagChat } from '../hooks/useRagChat';
import ChatMessage from './ChatMessage';
import ChatInput from './ChatInput';

const RagChat = ({ onAnimationChange }) => {
  const {
    messages,
    isLoading,
    sendMessage,
    clearChat,
    error
  } = useRagChat();

  const messagesEndRef = useRef(null);

  // 自动滚动到最新消息
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // 当有消息时，通知桌宠切换到思考动画
  useEffect(() => {
    if (onAnimationChange) {
      if (isLoading) {
        onAnimationChange('thinking');
      } else if (messages.length > 0) {
        onAnimationChange('talking');
      } else {
        onAnimationChange('idle');
      }
    }
  }, [isLoading, messages.length, onAnimationChange]);

  const handleSendMessage = async (message) => {
    await sendMessage(message);
  };

  return (
    <div className="rag-chat">
      <div className="chat-header">
        <h3>🤖 智能问答</h3>
        <div className="chat-actions">
          <button 
            className="clear-btn"
            onClick={clearChat}
            disabled={messages.length === 0}
          >
            🗑️ 清空
          </button>
        </div>
      </div>

      {error && (
        <div className="error-message">
          <span>❌ {error}</span>
        </div>
      )}

      <div className="chat-messages">
        {messages.length === 0 ? (
          <div className="empty-chat">
            <div className="welcome-message">
              <h4>👋 你好！我是长离</h4>
              <p>我可以帮你回答问题、查找资料、学习知识。</p>
              <p>试试问我一些问题吧！</p>
            </div>
          </div>
        ) : (
          messages.map((message) => (
            <ChatMessage
              key={message.id}
              message={message}
            />
          ))
        )}
        
        {isLoading && (
          <div className="loading-message">
            <div className="loading-indicator">
              <span>🤔</span>
              <span>长离正在思考...</span>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      <ChatInput
        onSendMessage={handleSendMessage}
        disabled={isLoading}
        placeholder={isLoading ? "长离正在思考中..." : "输入你的问题..."}
      />
    </div>
  );
};

export default RagChat;