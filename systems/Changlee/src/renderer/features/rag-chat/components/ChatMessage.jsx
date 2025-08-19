import React from 'react';

const ChatMessage = ({ message }) => {
  const { type, content, timestamp, sources } = message;

  const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString('zh-CN', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className={`chat-message ${type}`}>
      <div className="message-header">
        <div className="message-avatar">
          {type === 'user' ? '👤' : '🤖'}
        </div>
        <div className="message-info">
          <span className="message-sender">
            {type === 'user' ? '你' : '长离'}
          </span>
          <span className="message-time">
            {formatTime(timestamp)}
          </span>
        </div>
      </div>
      
      <div className="message-content">
        {typeof content === 'string' ? (
          <div className="message-text">
            {content.split('\n').map((line, index) => (
              <p key={index}>{line}</p>
            ))}
          </div>
        ) : (
          <div className="message-text">{content}</div>
        )}
        
        {sources && sources.length > 0 && (
          <div className="message-sources">
            <div className="sources-header">📚 参考资料：</div>
            <div className="sources-list">
              {sources.map((source, index) => (
                <div key={index} className="source-item">
                  <span className="source-title">{source.title}</span>
                  {source.score && (
                    <span className="source-score">
                      相关度: {(source.score * 100).toFixed(1)}%
                    </span>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ChatMessage;