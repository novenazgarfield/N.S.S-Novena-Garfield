import { useState, useCallback } from 'react';
import { ragService } from '../../../services/ragService';

export const useRagChat = () => {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  // 发送消息
  const sendMessage = useCallback(async (content) => {
    if (!content.trim()) return;

    // 添加用户消息
    const userMessage = {
      id: `user_${Date.now()}`,
      type: 'user',
      content: content.trim(),
      timestamp: Date.now()
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);
    setError(null);

    try {
      // 调用RAG服务
      const response = await ragService.query(content.trim());
      
      // 添加AI回复
      const aiMessage = {
        id: `ai_${Date.now()}`,
        type: 'assistant',
        content: response.answer || response.response || '抱歉，我没有理解你的问题。',
        timestamp: Date.now(),
        sources: response.sources || []
      };

      setMessages(prev => [...prev, aiMessage]);
    } catch (err) {
      console.error('RAG查询失败:', err);
      
      // 添加错误消息
      const errorMessage = {
        id: `error_${Date.now()}`,
        type: 'assistant',
        content: '抱歉，我现在无法回答你的问题。请稍后再试。',
        timestamp: Date.now()
      };

      setMessages(prev => [...prev, errorMessage]);
      setError('连接服务失败，请检查网络连接或稍后重试。');
    } finally {
      setIsLoading(false);
    }
  }, []);

  // 清空聊天记录
  const clearChat = useCallback(() => {
    setMessages([]);
    setError(null);
  }, []);

  // 重新发送最后一条消息
  const resendLastMessage = useCallback(() => {
    const lastUserMessage = messages
      .slice()
      .reverse()
      .find(msg => msg.type === 'user');
    
    if (lastUserMessage) {
      // 移除最后的AI回复（如果有的话）
      setMessages(prev => {
        const lastIndex = prev.findIndex(msg => msg.id === lastUserMessage.id);
        return prev.slice(0, lastIndex + 1);
      });
      
      // 重新发送
      sendMessage(lastUserMessage.content);
    }
  }, [messages, sendMessage]);

  return {
    messages,
    isLoading,
    error,
    sendMessage,
    clearChat,
    resendLastMessage
  };
};