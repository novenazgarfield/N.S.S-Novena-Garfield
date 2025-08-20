/**
 * Chronicle集成组件
 * 显示学习记录状态和分析报告
 */

import React, { useState, useEffect } from 'react';
import './ChronicleIntegration.css';

const ChronicleIntegration = () => {
  const [chronicleStatus, setChronicleStatus] = useState(null);
  const [activeSessions, setActiveSessions] = useState([]);
  const [isRecording, setIsRecording] = useState(false);
  const [currentSessionId, setCurrentSessionId] = useState(null);
  const [learningReport, setLearningReport] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // 检查Chronicle服务状态
  const checkChronicleStatus = async () => {
    try {
      const response = await fetch('/api/chronicle/status');
      const result = await response.json();
      
      if (result.success) {
        setChronicleStatus(result.data);
        setError(null);
      } else {
        setError('获取Chronicle状态失败');
      }
    } catch (err) {
      setError('Chronicle服务连接失败');
      setChronicleStatus(null);
    }
  };

  // 获取活动会话列表
  const fetchActiveSessions = async () => {
    try {
      const response = await fetch('/api/chronicle/sessions/active');
      const result = await response.json();
      
      if (result.success) {
        setActiveSessions(result.data);
      }
    } catch (err) {
      console.error('获取活动会话失败:', err);
    }
  };

  // 开始学习记录
  const startLearningRecord = async (learningType = 'general') => {
    if (isRecording) return;

    setLoading(true);
    try {
      const sessionData = {
        sessionId: `changlee_${Date.now()}`,
        userId: 'changlee_user',
        learningType,
        subject: '英语学习',
        difficulty: 'intermediate',
        monitorFiles: true,
        monitorWindows: true,
        monitorCommands: false,
        metadata: {
          app_version: '1.0.0',
          learning_mode: 'interactive',
          start_timestamp: new Date().toISOString()
        }
      };

      const response = await fetch('/api/chronicle/sessions/start', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(sessionData)
      });

      const result = await response.json();
      
      if (result.success) {
        setIsRecording(true);
        setCurrentSessionId(sessionData.sessionId);
        setError(null);
        await fetchActiveSessions();
        
        // 显示成功消息
        showNotification('📊 学习记录已开始', 'success');
      } else {
        setError(result.error || '启动学习记录失败');
      }
    } catch (err) {
      setError('启动学习记录时发生错误');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // 停止学习记录
  const stopLearningRecord = async () => {
    if (!isRecording || !currentSessionId) return;

    setLoading(true);
    try {
      const summary = {
        outcomes: ['完成单词学习', '练习拼写'],
        metrics: {
          words_learned: 10,
          accuracy_rate: 0.85,
          time_spent: Date.now() - new Date().getTime()
        },
        notes: '本次学习会话完成'
      };

      const response = await fetch(`/api/chronicle/sessions/${currentSessionId}/stop`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ summary })
      });

      const result = await response.json();
      
      if (result.success) {
        setIsRecording(false);
        setCurrentSessionId(null);
        setError(null);
        await fetchActiveSessions();
        
        // 显示成功消息
        showNotification('✅ 学习记录已停止', 'success');
      } else {
        setError(result.error || '停止学习记录失败');
      }
    } catch (err) {
      setError('停止学习记录时发生错误');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // 获取学习报告
  const fetchLearningReport = async (sessionId) => {
    setLoading(true);
    try {
      const response = await fetch(`/api/chronicle/sessions/${sessionId}/report`);
      const result = await response.json();
      
      if (result.success) {
        setLearningReport(result.data);
        setError(null);
      } else {
        setError(result.error || '获取学习报告失败');
      }
    } catch (err) {
      setError('获取学习报告时发生错误');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // 重连Chronicle服务
  const reconnectChronicle = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/chronicle/reconnect', {
        method: 'POST'
      });
      
      const result = await response.json();
      
      if (result.success) {
        await checkChronicleStatus();
        showNotification('🔄 Chronicle服务重连成功', 'success');
      } else {
        setError(result.error || '重连失败');
      }
    } catch (err) {
      setError('重连Chronicle服务时发生错误');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // 显示通知
  const showNotification = (message, type = 'info') => {
    // 这里可以集成到Changlee的通知系统
    console.log(`[${type.toUpperCase()}] ${message}`);
  };

  // 格式化时间
  const formatDuration = (ms) => {
    const seconds = Math.floor(ms / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    
    if (hours > 0) {
      return `${hours}小时${minutes % 60}分钟`;
    } else if (minutes > 0) {
      return `${minutes}分钟${seconds % 60}秒`;
    } else {
      return `${seconds}秒`;
    }
  };

  // 组件挂载时检查状态
  useEffect(() => {
    checkChronicleStatus();
    fetchActiveSessions();
    
    // 定期更新状态
    const interval = setInterval(() => {
      checkChronicleStatus();
      fetchActiveSessions();
    }, 30000); // 每30秒更新一次
    
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="chronicle-integration">
      <div className="chronicle-header">
        <h3>📊 学习记录系统</h3>
        <div className="chronicle-status">
          {chronicleStatus ? (
            <span className={`status-indicator ${chronicleStatus.client.isConnected ? 'connected' : 'disconnected'}`}>
              {chronicleStatus.client.isConnected ? '已连接' : '未连接'}
            </span>
          ) : (
            <span className="status-indicator disconnected">检查中...</span>
          )}
        </div>
      </div>

      {error && (
        <div className="error-message">
          <span>⚠️ {error}</span>
          <button onClick={reconnectChronicle} disabled={loading}>
            重连
          </button>
        </div>
      )}

      <div className="chronicle-controls">
        <div className="recording-section">
          <h4>学习会话记录</h4>
          <div className="recording-controls">
            {!isRecording ? (
              <div className="start-options">
                <button 
                  onClick={() => startLearningRecord('word_learning')}
                  disabled={loading || !chronicleStatus?.client.isConnected}
                  className="start-btn word-learning"
                >
                  📝 开始单词学习记录
                </button>
                <button 
                  onClick={() => startLearningRecord('spelling_practice')}
                  disabled={loading || !chronicleStatus?.client.isConnected}
                  className="start-btn spelling"
                >
                  ✏️ 开始拼写练习记录
                </button>
                <button 
                  onClick={() => startLearningRecord('reading_session')}
                  disabled={loading || !chronicleStatus?.client.isConnected}
                  className="start-btn reading"
                >
                  📖 开始阅读会话记录
                </button>
              </div>
            ) : (
              <div className="recording-active">
                <div className="recording-indicator">
                  <span className="recording-dot"></span>
                  正在记录学习过程...
                </div>
                <button 
                  onClick={stopLearningRecord}
                  disabled={loading}
                  className="stop-btn"
                >
                  ⏹️ 停止记录
                </button>
              </div>
            )}
          </div>
        </div>

        <div className="sessions-section">
          <h4>活动会话 ({activeSessions.length})</h4>
          <div className="sessions-list">
            {activeSessions.length === 0 ? (
              <p className="no-sessions">暂无活动会话</p>
            ) : (
              activeSessions.map((session) => (
                <div key={session.changlee_session_id} className="session-item">
                  <div className="session-info">
                    <span className="session-type">{session.type}</span>
                    <span className="session-duration">
                      {formatDuration(session.duration)}
                    </span>
                  </div>
                  <button 
                    onClick={() => fetchLearningReport(session.changlee_session_id)}
                    className="report-btn"
                    disabled={loading}
                  >
                    📊 查看报告
                  </button>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      {learningReport && (
        <div className="learning-report">
          <h4>📈 学习分析报告</h4>
          <div className="report-content">
            <div className="report-summary">
              <h5>会话摘要</h5>
              <p>开始时间: {new Date(learningReport.start_time).toLocaleString('zh-CN')}</p>
              <p>结束时间: {new Date(learningReport.end_time).toLocaleString('zh-CN')}</p>
              <p>持续时间: {formatDuration(learningReport.duration)}</p>
            </div>
            
            {learningReport.changlee_analysis && (
              <div className="changlee-analysis">
                <h5>学习洞察</h5>
                {learningReport.changlee_analysis.learning_insights.map((insight, index) => (
                  <div key={index} className="insight-item">
                    <strong>{insight.insight}</strong>
                    <p>{JSON.stringify(insight.details, null, 2)}</p>
                  </div>
                ))}
                
                <h5>学习建议</h5>
                {learningReport.changlee_analysis.recommendations.map((rec, index) => (
                  <div key={index} className="recommendation-item">
                    <p>💡 {rec}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
          
          <button 
            onClick={() => setLearningReport(null)}
            className="close-report-btn"
          >
            关闭报告
          </button>
        </div>
      )}

      {chronicleStatus && (
        <div className="chronicle-info">
          <h4>系统信息</h4>
          <div className="info-grid">
            <div className="info-item">
              <span>服务状态:</span>
              <span>{chronicleStatus.service.is_connected ? '✅ 正常' : '❌ 异常'}</span>
            </div>
            <div className="info-item">
              <span>活动会话:</span>
              <span>{chronicleStatus.service.active_sessions}</span>
            </div>
            <div className="info-item">
              <span>最后检查:</span>
              <span>{chronicleStatus.service.last_health_check ? 
                new Date(chronicleStatus.service.last_health_check).toLocaleString('zh-CN') : 
                '未知'
              }</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ChronicleIntegration;