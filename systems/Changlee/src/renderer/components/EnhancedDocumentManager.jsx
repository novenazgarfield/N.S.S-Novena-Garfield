import React, { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import styled from 'styled-components';
import { 
  Upload, FileText, Trash2, Eye, Download, 
  BookOpen, Brain, Sparkles, AlertCircle,
  CheckCircle, Clock, FileX, Search,
  MessageCircle, Layers, Target, Zap
} from 'lucide-react';

const ManagerContainer = styled(motion.div)`
  max-width: 1000px;
  margin: 0 auto;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 20px;
  padding: 30px;
  box-shadow: 0 20px 40px rgba(102, 126, 234, 0.3);
  color: white;
`;

const Header = styled.div`
  text-align: center;
  margin-bottom: 30px;
`;

const Title = styled.h2`
  margin: 0 0 10px 0;
  font-size: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 15px;
`;

const TabContainer = styled.div`
  display: flex;
  gap: 10px;
  margin-bottom: 30px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  overflow-x: auto;
`;

const Tab = styled(motion.button)`
  padding: 12px 20px;
  border: none;
  background: ${props => props.active ? 'rgba(255, 255, 255, 0.2)' : 'transparent'};
  color: white;
  border-radius: 10px 10px 0 0;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
  white-space: nowrap;
  
  &:hover {
    background: rgba(255, 255, 255, 0.1);
  }
`;

const ContentArea = styled.div`
  min-height: 500px;
`;

const SearchContainer = styled.div`
  background: rgba(255, 255, 255, 0.1);
  border-radius: 15px;
  padding: 20px;
  margin-bottom: 20px;
`;

const SearchInput = styled.input`
  width: 100%;
  padding: 15px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.9);
  color: #333;
  font-size: 1rem;
  outline: none;
  
  &:focus {
    border-color: #4ecdc4;
    box-shadow: 0 0 20px rgba(78, 205, 196, 0.3);
  }
`;

const SearchButton = styled(motion.button)`
  width: 100%;
  margin-top: 10px;
  padding: 12px;
  border: none;
  border-radius: 10px;
  background: linear-gradient(135deg, #4ecdc4, #44a08d);
  color: white;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(0,0,0,0.2);
  }
  
  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none;
  }
`;

const ResultsContainer = styled.div`
  background: rgba(255, 255, 255, 0.1);
  border-radius: 15px;
  padding: 20px;
  margin-top: 20px;
`;

const ResultItem = styled(motion.div)`
  background: rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  padding: 15px;
  margin-bottom: 15px;
  border-left: 4px solid #4ecdc4;
`;

const DocumentGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
`;

const DocumentCard = styled(motion.div)`
  background: rgba(255, 255, 255, 0.1);
  border-radius: 15px;
  padding: 20px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  position: relative;
`;

const DocumentHeader = styled.div`
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 15px;
`;

const DocumentIcon = styled.div`
  width: 50px;
  height: 50px;
  border-radius: 10px;
  background: ${props => getFileTypeColor(props.type)};
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  flex-shrink: 0;
`;

const DocumentInfo = styled.div`
  flex: 1;
  min-width: 0;
`;

const DocumentName = styled.div`
  font-size: 1.1rem;
  font-weight: 600;
  margin-bottom: 5px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
`;

const DocumentMeta = styled.div`
  font-size: 0.9rem;
  opacity: 0.8;
  display: flex;
  flex-direction: column;
  gap: 3px;
`;

const DocumentActions = styled.div`
  display: flex;
  gap: 8px;
  margin-top: 15px;
  flex-wrap: wrap;
`;

const ActionButton = styled(motion.button)`
  flex: 1;
  min-width: 80px;
  padding: 8px 12px;
  border: none;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  font-size: 0.85rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
  
  &:hover {
    background: rgba(255, 255, 255, 0.3);
    transform: translateY(-1px);
  }
  
  &.primary {
    background: linear-gradient(135deg, #4ecdc4, #44a08d);
  }
  
  &.danger {
    background: linear-gradient(135deg, #ff6b6b, #ee5a24);
  }
`;

const ChatInterface = styled.div`
  height: 400px;
  display: flex;
  flex-direction: column;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 15px;
  overflow: hidden;
`;

const MessagesArea = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 20px;
`;

const Message = styled(motion.div)`
  display: flex;
  align-items: flex-start;
  gap: 10px;
  margin-bottom: 15px;
  ${props => props.isUser ? 'flex-direction: row-reverse;' : ''}
`;

const MessageAvatar = styled.div`
  width: 35px;
  height: 35px;
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
  padding: 12px 16px;
  border-radius: 15px;
  background: ${props => props.isUser ? 
    'rgba(255, 255, 255, 0.9)' : 
    'rgba(255, 255, 255, 0.1)'};
  color: ${props => props.isUser ? '#333' : 'white'};
  line-height: 1.5;
  
  ${props => props.isUser ? `
    border-bottom-right-radius: 5px;
  ` : `
    border-bottom-left-radius: 5px;
  `}
`;

const InputArea = styled.div`
  padding: 15px;
  border-top: 1px solid rgba(255, 255, 255, 0.2);
  display: flex;
  gap: 10px;
`;

const MessageInput = styled.input`
  flex: 1;
  padding: 12px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.9);
  color: #333;
  outline: none;
  
  &:focus {
    border-color: #4ecdc4;
  }
`;

const SendButton = styled(motion.button)`
  width: 45px;
  height: 45px;
  border: none;
  border-radius: 10px;
  background: linear-gradient(135deg, #4ecdc4, #44a08d);
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  
  &:hover {
    transform: scale(1.05);
  }
`;

const AnalysisPanel = styled(motion.div)`
  background: rgba(255, 255, 255, 0.1);
  border-radius: 15px;
  padding: 20px;
  margin-top: 20px;
`;

const QuickFilters = styled.div`
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  flex-wrap: wrap;
`;

const FilterButton = styled(motion.button)`
  padding: 8px 16px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 20px;
  background: ${props => props.active ? 'rgba(78, 205, 196, 0.3)' : 'rgba(255, 255, 255, 0.1)'};
  color: white;
  font-size: 0.9rem;
  cursor: pointer;
  
  &:hover {
    background: rgba(255, 255, 255, 0.2);
  }
`;

// 辅助函数
const getFileTypeColor = (type) => {
  const colors = {
    pdf: 'linear-gradient(135deg, #ff6b6b, #ee5a24)',
    doc: 'linear-gradient(135deg, #3498db, #2980b9)',
    txt: 'linear-gradient(135deg, #2ecc71, #27ae60)',
    default: 'linear-gradient(135deg, #9b59b6, #8e44ad)'
  };
  return colors[type] || colors.default;
};

const getFileTypeIcon = (type) => {
  const icons = {
    pdf: '📄',
    doc: '📝',
    txt: '📃',
    default: '📄'
  };
  return icons[type] || icons.default;
};

const EnhancedDocumentManager = ({ onClose, onWordSelect }) => {
  const [activeTab, setActiveTab] = useState('search');
  const [documents, setDocuments] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const [chatMessages, setChatMessages] = useState([]);
  const [chatInput, setChatInput] = useState('');
  const [selectedDocument, setSelectedDocument] = useState(null);
  const [analysisResults, setAnalysisResults] = useState(null);
  const [activeFilter, setActiveFilter] = useState('all');

  const tabs = [
    { id: 'search', label: '🔍 文献检索', icon: Search },
    { id: 'chat', label: '💬 文档问答', icon: MessageCircle },
    { id: 'manage', label: '📚 文档管理', icon: FileText },
    { id: 'analysis', label: '🧠 批量分析', icon: Brain },
    { id: 'integration', label: '🔗 知识整合', icon: Layers }
  ];

  const filters = [
    { id: 'all', label: '全部文档' },
    { id: 'pdf', label: 'PDF文档' },
    { id: 'doc', label: 'Word文档' },
    { id: 'recent', label: '最近上传' },
    { id: 'analyzed', label: '已分析' }
  ];

  useEffect(() => {
    loadDocuments();
    initializeChatMessages();
  }, []);

  const loadDocuments = async () => {
    // 模拟文档数据
    const mockDocuments = [
      {
        id: 1,
        name: 'IELTS核心词汇.pdf',
        type: 'pdf',
        size: '2.5 MB',
        uploadTime: new Date('2025-08-14T10:00:00'),
        status: 'processed',
        wordCount: 156,
        summary: '包含IELTS考试核心词汇，按主题分类整理'
      },
      {
        id: 2,
        name: '英语语法大全.docx',
        type: 'doc',
        size: '1.8 MB',
        uploadTime: new Date('2025-08-14T09:30:00'),
        status: 'processed',
        wordCount: 89,
        summary: '详细的英语语法规则和例句'
      },
      {
        id: 3,
        name: '商务英语手册.pdf',
        type: 'pdf',
        size: '3.2 MB',
        uploadTime: new Date('2025-08-14T08:15:00'),
        status: 'processed',
        wordCount: 234,
        summary: '商务场景常用英语表达和词汇'
      }
    ];
    
    setDocuments(mockDocuments);
  };

  const initializeChatMessages = () => {
    setChatMessages([
      {
        id: 1,
        text: '你好！我可以帮你分析已上传的文档内容，回答相关问题。请选择一个文档开始对话，或者直接提问！',
        isUser: false,
        timestamp: new Date()
      }
    ]);
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    
    setIsSearching(true);
    
    try {
      const response = await fetch('http://localhost:3001/api/rag/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          query: searchQuery,
          options: {
            documentType: activeFilter === 'all' ? '全部' : activeFilter,
            scope: '全文',
            detail: '详细'
          }
        })
      });

      const data = await response.json();
      
      if (data.success) {
        setSearchResults([
          {
            id: Date.now(),
            query: searchQuery,
            answer: data.data.answer,
            sources: data.data.sources || [],
            timestamp: new Date()
          }
        ]);
      }
    } catch (error) {
      console.error('搜索失败:', error);
      setSearchResults([
        {
          id: Date.now(),
          query: searchQuery,
          answer: '搜索过程中出现错误，请稍后再试。',
          sources: [],
          timestamp: new Date(),
          error: true
        }
      ]);
    } finally {
      setIsSearching(false);
    }
  };

  const handleChatMessage = async () => {
    if (!chatInput.trim()) return;

    const userMessage = {
      id: Date.now(),
      text: chatInput,
      isUser: true,
      timestamp: new Date()
    };

    setChatMessages(prev => [...prev, userMessage]);
    setChatInput('');

    try {
      const endpoint = selectedDocument 
        ? '/api/rag/ask-document'
        : '/api/rag/ask';
      
      const body = selectedDocument 
        ? {
            documentId: selectedDocument.id,
            question: chatInput,
            context: { documentName: selectedDocument.name }
          }
        : {
            question: chatInput,
            context: { type: 'document_chat' }
          };

      const response = await fetch(`http://localhost:3001${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(body)
      });

      const data = await response.json();
      
      const botMessage = {
        id: Date.now() + 1,
        text: data.success ? data.data.answer : '抱歉，我无法回答这个问题。',
        isUser: false,
        timestamp: new Date(),
        sources: data.data?.sources || []
      };

      setChatMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('发送消息失败:', error);
      const errorMessage = {
        id: Date.now() + 1,
        text: '网络连接出现问题，请稍后再试。',
        isUser: false,
        timestamp: new Date()
      };
      setChatMessages(prev => [...prev, errorMessage]);
    }
  };

  const handleBatchAnalysis = async (analysisType) => {
    const selectedDocs = documents.filter(doc => doc.status === 'processed');
    
    try {
      const response = await fetch('http://localhost:3001/api/rag/batch-analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          documentIds: selectedDocs.map(doc => doc.id),
          analysisType
        })
      });

      const data = await response.json();
      
      if (data.success) {
        setAnalysisResults({
          type: analysisType,
          results: data.data.batchResults,
          timestamp: new Date()
        });
      }
    } catch (error) {
      console.error('批量分析失败:', error);
    }
  };

  const handleKnowledgeIntegration = async (topic) => {
    try {
      const response = await fetch('http://localhost:3001/api/rag/integrate-knowledge', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          topic,
          documentIds: documents.map(doc => doc.id)
        })
      });

      const data = await response.json();
      
      if (data.success) {
        setAnalysisResults({
          type: 'knowledge_integration',
          topic,
          result: data.data.answer,
          timestamp: new Date()
        });
      }
    } catch (error) {
      console.error('知识整合失败:', error);
    }
  };

  const filteredDocuments = documents.filter(doc => {
    if (activeFilter === 'all') return true;
    if (activeFilter === 'recent') return new Date() - doc.uploadTime < 24 * 60 * 60 * 1000;
    if (activeFilter === 'analyzed') return doc.status === 'processed';
    return doc.type === activeFilter;
  });

  const renderTabContent = () => {
    switch (activeTab) {
      case 'search':
        return (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
          >
            <SearchContainer>
              <h3 style={{ margin: '0 0 15px 0', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Search size={20} />
                🔍 文献检索
              </h3>
              <SearchInput
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="在已上传的文档中搜索信息..."
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              />
              <SearchButton
                onClick={handleSearch}
                disabled={isSearching || !searchQuery.trim()}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                {isSearching ? (
                  <>⏳ 搜索中...</>
                ) : (
                  <>🔍 搜索</>
                )}
              </SearchButton>
            </SearchContainer>

            {searchResults.length > 0 && (
              <ResultsContainer>
                <h4>📊 搜索结果</h4>
                {searchResults.map(result => (
                  <ResultItem
                    key={result.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                  >
                    <div style={{ fontWeight: 'bold', marginBottom: '10px' }}>
                      ❓ {result.query}
                    </div>
                    <div style={{ marginBottom: '10px' }}>
                      🤖 {result.answer}
                    </div>
                    {result.sources && result.sources.length > 0 && (
                      <div style={{ fontSize: '0.9rem', opacity: '0.8' }}>
                        📚 来源: {result.sources.map(s => s.title || s.filename).join(', ')}
                      </div>
                    )}
                  </ResultItem>
                ))}
              </ResultsContainer>
            )}
          </motion.div>
        );

      case 'chat':
        return (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
          >
            <div style={{ marginBottom: '20px' }}>
              <h3 style={{ margin: '0 0 15px 0' }}>💬 文档问答</h3>
              <select
                value={selectedDocument?.id || ''}
                onChange={(e) => {
                  const doc = documents.find(d => d.id === parseInt(e.target.value));
                  setSelectedDocument(doc);
                }}
                style={{
                  width: '100%',
                  padding: '10px',
                  borderRadius: '8px',
                  border: '2px solid rgba(255,255,255,0.3)',
                  background: 'rgba(255,255,255,0.9)',
                  color: '#333'
                }}
              >
                <option value="">选择文档进行针对性问答</option>
                {documents.map(doc => (
                  <option key={doc.id} value={doc.id}>
                    {doc.name}
                  </option>
                ))}
              </select>
            </div>

            <ChatInterface>
              <MessagesArea>
                {chatMessages.map(message => (
                  <Message key={message.id} isUser={message.isUser}>
                    <MessageAvatar isUser={message.isUser}>
                      {message.isUser ? '👤' : '🤖'}
                    </MessageAvatar>
                    <MessageBubble isUser={message.isUser}>
                      {message.text}
                      {message.sources && message.sources.length > 0 && (
                        <div style={{ marginTop: '8px', fontSize: '0.8rem', opacity: '0.8' }}>
                          📚 {message.sources.map(s => s.title || s.filename).join(', ')}
                        </div>
                      )}
                    </MessageBubble>
                  </Message>
                ))}
              </MessagesArea>
              <InputArea>
                <MessageInput
                  value={chatInput}
                  onChange={(e) => setChatInput(e.target.value)}
                  placeholder={selectedDocument ? `向长离询问关于《${selectedDocument.name}》的问题...` : '向长离提问...'}
                  onKeyPress={(e) => e.key === 'Enter' && handleChatMessage()}
                />
                <SendButton
                  onClick={handleChatMessage}
                  disabled={!chatInput.trim()}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  📤
                </SendButton>
              </InputArea>
            </ChatInterface>
          </motion.div>
        );

      case 'manage':
        return (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
          >
            <QuickFilters>
              {filters.map(filter => (
                <FilterButton
                  key={filter.id}
                  active={activeFilter === filter.id}
                  onClick={() => setActiveFilter(filter.id)}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  {filter.label}
                </FilterButton>
              ))}
            </QuickFilters>

            <DocumentGrid>
              {filteredDocuments.map(doc => (
                <DocumentCard
                  key={doc.id}
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ duration: 0.3 }}
                >
                  <DocumentHeader>
                    <DocumentIcon type={doc.type}>
                      {getFileTypeIcon(doc.type)}
                    </DocumentIcon>
                    <DocumentInfo>
                      <DocumentName>{doc.name}</DocumentName>
                      <DocumentMeta>
                        <span>📏 {doc.size}</span>
                        <span>📅 {doc.uploadTime.toLocaleDateString()}</span>
                        <span>📊 {doc.wordCount} 个单词</span>
                      </DocumentMeta>
                    </DocumentInfo>
                  </DocumentHeader>
                  
                  <div style={{ fontSize: '0.9rem', opacity: '0.9', marginBottom: '15px' }}>
                    {doc.summary}
                  </div>
                  
                  <DocumentActions>
                    <ActionButton
                      className="primary"
                      onClick={() => {
                        setSelectedDocument(doc);
                        setActiveTab('chat');
                      }}
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                    >
                      <MessageCircle size={14} />
                      问答
                    </ActionButton>
                    <ActionButton
                      onClick={() => {
                        setSearchQuery(`总结文档《${doc.name}》的主要内容`);
                        setActiveTab('search');
                      }}
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                    >
                      <Eye size={14} />
                      分析
                    </ActionButton>
                    <ActionButton
                      className="danger"
                      onClick={() => {/* 删除文档 */}}
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                    >
                      <Trash2 size={14} />
                      删除
                    </ActionButton>
                  </DocumentActions>
                </DocumentCard>
              ))}
            </DocumentGrid>
          </motion.div>
        );

      case 'analysis':
        return (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
          >
            <div style={{ marginBottom: '30px' }}>
              <h3 style={{ margin: '0 0 20px 0' }}>🧠 批量分析</h3>
              <div style={{ display: 'flex', gap: '15px', flexWrap: 'wrap' }}>
                <ActionButton
                  className="primary"
                  onClick={() => handleBatchAnalysis('summary')}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <FileText size={16} />
                  内容总结
                </ActionButton>
                <ActionButton
                  className="primary"
                  onClick={() => handleBatchAnalysis('keywords')}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <Target size={16} />
                  关键词提取
                </ActionButton>
                <ActionButton
                  className="primary"
                  onClick={() => handleBatchAnalysis('learning_points')}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <Brain size={16} />
                  学习要点
                </ActionButton>
              </div>
            </div>

            {analysisResults && (
              <AnalysisPanel
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
              >
                <h4>📊 分析结果 - {analysisResults.type}</h4>
                {analysisResults.results ? (
                  analysisResults.results.map((result, index) => (
                    <div key={index} style={{ marginBottom: '20px', padding: '15px', background: 'rgba(255,255,255,0.1)', borderRadius: '10px' }}>
                      <h5>📄 文档 {result.documentId}</h5>
                      <div>{result.result.answer}</div>
                    </div>
                  ))
                ) : (
                  <div>{analysisResults.result}</div>
                )}
              </AnalysisPanel>
            )}
          </motion.div>
        );

      case 'integration':
        return (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
          >
            <div style={{ marginBottom: '30px' }}>
              <h3 style={{ margin: '0 0 20px 0' }}>🔗 知识整合</h3>
              <p style={{ opacity: '0.9', marginBottom: '20px' }}>
                将多个文档的相关信息整合成完整的知识体系
              </p>
              <div style={{ display: 'flex', gap: '15px', flexWrap: 'wrap' }}>
                <ActionButton
                  className="primary"
                  onClick={() => handleKnowledgeIntegration('英语学习方法')}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <Zap size={16} />
                  学习方法整合
                </ActionButton>
                <ActionButton
                  className="primary"
                  onClick={() => handleKnowledgeIntegration('词汇记忆技巧')}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <Brain size={16} />
                  记忆技巧整合
                </ActionButton>
                <ActionButton
                  className="primary"
                  onClick={() => handleKnowledgeIntegration('语法知识点')}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <BookOpen size={16} />
                  语法知识整合
                </ActionButton>
              </div>
            </div>

            {analysisResults && analysisResults.type === 'knowledge_integration' && (
              <AnalysisPanel
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
              >
                <h4>🔗 知识整合结果 - {analysisResults.topic}</h4>
                <div style={{ whiteSpace: 'pre-wrap', lineHeight: '1.6' }}>
                  {analysisResults.result}
                </div>
              </AnalysisPanel>
            )}
          </motion.div>
        );

      default:
        return null;
    }
  };

  return (
    <ManagerContainer
      initial={{ scale: 0.9, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      exit={{ scale: 0.9, opacity: 0 }}
      transition={{ type: "spring", stiffness: 300, damping: 30 }}
    >
      <Header>
        <Title>
          <BookOpen size={32} />
          📚 智能文档中心
        </Title>
        <p style={{ margin: 0, opacity: 0.9 }}>
          上传、分析、检索、问答 - 让长离成为你的智能文献助手
        </p>
      </Header>

      <TabContainer>
        {tabs.map(tab => (
          <Tab
            key={tab.id}
            active={activeTab === tab.id}
            onClick={() => setActiveTab(tab.id)}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <tab.icon size={16} />
            {tab.label}
          </Tab>
        ))}
      </TabContainer>

      <ContentArea>
        {renderTabContent()}
      </ContentArea>
    </ManagerContainer>
  );
};

export default EnhancedDocumentManager;