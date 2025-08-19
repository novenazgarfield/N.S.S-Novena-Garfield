import React, { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import styled from 'styled-components';
import { 
  Upload, FileText, Trash2, Eye, Download, 
  BookOpen, Brain, Sparkles, AlertCircle,
  CheckCircle, Clock, FileX
} from 'lucide-react';

const ManagerContainer = styled(motion.div)`
  max-width: 900px;
  margin: 0 auto;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 20px;
  padding: 30px;
  box-shadow: 0 20px 40px rgba(102, 126, 234, 0.3);
  color: white;
`;

const ManagerHeader = styled.div`
  text-align: center;
  margin-bottom: 30px;
`;

const ManagerTitle = styled.h2`
  margin: 0 0 10px 0;
  font-size: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
`;

const ManagerSubtitle = styled.p`
  margin: 0;
  opacity: 0.9;
  font-size: 1.1rem;
`;

const UploadArea = styled(motion.div)`
  border: 2px dashed rgba(255, 255, 255, 0.3);
  border-radius: 15px;
  padding: 40px;
  text-align: center;
  margin-bottom: 30px;
  background: rgba(255, 255, 255, 0.05);
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    border-color: rgba(255, 255, 255, 0.6);
    background: rgba(255, 255, 255, 0.1);
  }
  
  &.dragover {
    border-color: #4ecdc4;
    background: rgba(78, 205, 196, 0.1);
  }
`;

const UploadIcon = styled(motion.div)`
  font-size: 3rem;
  margin-bottom: 15px;
`;

const UploadText = styled.div`
  font-size: 1.2rem;
  margin-bottom: 10px;
`;

const UploadHint = styled.div`
  font-size: 0.9rem;
  opacity: 0.7;
`;

const FileInput = styled.input`
  display: none;
`;

const DocumentGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
`;

const DocumentCard = styled(motion.div)`
  background: rgba(255, 255, 255, 0.1);
  border-radius: 15px;
  padding: 20px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  position: relative;
  overflow: hidden;
`;

const DocumentIcon = styled.div`
  width: 50px;
  height: 50px;
  border-radius: 10px;
  background: linear-gradient(135deg, #4ecdc4, #44a08d);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 15px;
  font-size: 1.5rem;
`;

const DocumentTitle = styled.h3`
  margin: 0 0 8px 0;
  font-size: 1.1rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
`;

const DocumentMeta = styled.div`
  font-size: 0.85rem;
  opacity: 0.8;
  margin-bottom: 15px;
`;

const DocumentActions = styled.div`
  display: flex;
  gap: 8px;
  margin-top: 15px;
`;

const ActionButton = styled(motion.button)`
  flex: 1;
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
  backdrop-filter: blur(10px);
  
  &:hover {
    background: rgba(255, 255, 255, 0.3);
  }
  
  &.primary {
    background: linear-gradient(135deg, #4ecdc4, #44a08d);
  }
  
  &.danger {
    background: linear-gradient(135deg, #ff6b6b, #ee5a24);
  }
`;

const ProcessingOverlay = styled(motion.div)`
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border-radius: 15px;
  backdrop-filter: blur(10px);
`;

const ProcessingSpinner = styled(motion.div)`
  width: 40px;
  height: 40px;
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-top: 3px solid #4ecdc4;
  border-radius: 50%;
  margin-bottom: 10px;
`;

const EmptyState = styled.div`
  text-align: center;
  padding: 60px 20px;
  opacity: 0.7;
`;

const EmptyIcon = styled.div`
  font-size: 4rem;
  margin-bottom: 20px;
`;

const EmptyText = styled.div`
  font-size: 1.2rem;
  margin-bottom: 10px;
`;

const EmptyHint = styled.div`
  font-size: 0.9rem;
  opacity: 0.8;
`;

const AnalysisResults = styled(motion.div)`
  background: rgba(255, 255, 255, 0.1);
  border-radius: 15px;
  padding: 20px;
  margin-top: 20px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
`;

const AnalysisTitle = styled.h3`
  margin: 0 0 15px 0;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const WordsList = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 10px;
`;

const WordItem = styled.div`
  background: rgba(255, 255, 255, 0.1);
  padding: 10px;
  border-radius: 8px;
  font-size: 0.9rem;
`;

const DocumentManager = ({ onClose, onWordsExtracted }) => {
  const [documents, setDocuments] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [processing, setProcessing] = useState({});
  const [analysisResults, setAnalysisResults] = useState(null);
  const [dragOver, setDragOver] = useState(false);

  useEffect(() => {
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    // 这里应该从后端加载文档列表
    // 暂时使用模拟数据
    const mockDocuments = [
      {
        id: 1,
        filename: 'IELTS_Vocabulary.pdf',
        size: '2.5 MB',
        uploadTime: new Date('2025-08-14T10:00:00'),
        type: 'pdf',
        status: 'processed'
      },
      {
        id: 2,
        filename: 'English_Grammar_Guide.docx',
        size: '1.8 MB',
        uploadTime: new Date('2025-08-14T09:30:00'),
        type: 'docx',
        status: 'processed'
      }
    ];
    
    setDocuments(mockDocuments);
  };

  const handleFileSelect = (files) => {
    Array.from(files).forEach(file => {
      uploadDocument(file);
    });
  };

  const uploadDocument = async (file) => {
    setUploading(true);
    
    try {
      // 创建临时文档条目
      const tempDoc = {
        id: Date.now(),
        filename: file.name,
        size: formatFileSize(file.size),
        uploadTime: new Date(),
        type: getFileType(file.name),
        status: 'uploading'
      };
      
      setDocuments(prev => [...prev, tempDoc]);
      
      // 模拟上传过程
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // 更新文档状态
      setDocuments(prev => prev.map(doc => 
        doc.id === tempDoc.id 
          ? { ...doc, status: 'processed' }
          : doc
      ));
      
      console.log('文档上传成功:', file.name);
      
    } catch (error) {
      console.error('文档上传失败:', error);
      
      // 移除失败的文档
      setDocuments(prev => prev.filter(doc => doc.id !== tempDoc.id));
      
    } finally {
      setUploading(false);
    }
  };

  const analyzeDocument = async (document) => {
    setProcessing(prev => ({ ...prev, [document.id]: true }));
    
    try {
      // 调用文档分析API
      const response = await fetch('http://localhost:3001/api/rag/analyze-document', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          documentId: document.id,
          difficulty: 2
        })
      });
      
      const data = await response.json();
      
      if (data.success) {
        setAnalysisResults({
          documentName: document.filename,
          words: data.data.words || [],
          rawResponse: data.data.rawResponse
        });
        
        // 如果有回调函数，传递提取的单词
        if (onWordsExtracted && data.data.words) {
          onWordsExtracted(data.data.words);
        }
      } else {
        throw new Error(data.error || '分析失败');
      }
      
    } catch (error) {
      console.error('文档分析失败:', error);
      alert('文档分析失败: ' + error.message);
      
    } finally {
      setProcessing(prev => ({ ...prev, [document.id]: false }));
    }
  };

  const deleteDocument = async (documentId) => {
    if (confirm('确定要删除这个文档吗？')) {
      setDocuments(prev => prev.filter(doc => doc.id !== documentId));
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    
    const files = e.dataTransfer.files;
    handleFileSelect(files);
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getFileType = (filename) => {
    const extension = filename.split('.').pop().toLowerCase();
    return extension;
  };

  const getFileIcon = (type) => {
    switch (type) {
      case 'pdf':
        return '📄';
      case 'docx':
      case 'doc':
        return '📝';
      case 'txt':
        return '📃';
      case 'md':
        return '📋';
      default:
        return '📄';
    }
  };

  const formatDate = (date) => {
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <ManagerContainer
      initial={{ scale: 0.9, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      exit={{ scale: 0.9, opacity: 0 }}
      transition={{ type: "spring", stiffness: 300, damping: 30 }}
    >
      <ManagerHeader>
        <ManagerTitle>
          <BookOpen size={28} />
          📚 学习文档管理
        </ManagerTitle>
        <ManagerSubtitle>
          上传学习资料，让长离帮你分析和提取重要单词
        </ManagerSubtitle>
      </ManagerHeader>

      <UploadArea
        className={dragOver ? 'dragover' : ''}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => document.getElementById('file-input').click()}
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
      >
        <UploadIcon
          animate={{ 
            y: [0, -10, 0],
            rotate: [0, 5, -5, 0]
          }}
          transition={{ 
            duration: 2, 
            repeat: Infinity,
            ease: "easeInOut"
          }}
        >
          📤
        </UploadIcon>
        <UploadText>
          {uploading ? '正在上传...' : '点击或拖拽文件到这里上传'}
        </UploadText>
        <UploadHint>
          支持 PDF, DOCX, TXT, MD 等格式，最大 50MB
        </UploadHint>
        
        <FileInput
          id="file-input"
          type="file"
          multiple
          accept=".pdf,.docx,.doc,.txt,.md"
          onChange={(e) => handleFileSelect(e.target.files)}
        />
      </UploadArea>

      {documents.length > 0 ? (
        <DocumentGrid>
          {documents.map((doc) => (
            <DocumentCard
              key={doc.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
            >
              <DocumentIcon>
                {getFileIcon(doc.type)}
              </DocumentIcon>
              
              <DocumentTitle>{doc.filename}</DocumentTitle>
              
              <DocumentMeta>
                大小: {doc.size}<br/>
                上传: {formatDate(doc.uploadTime)}<br/>
                状态: {doc.status === 'uploading' ? '上传中' : 
                      doc.status === 'processing' ? '处理中' : '已完成'}
              </DocumentMeta>
              
              <DocumentActions>
                <ActionButton
                  className="primary"
                  onClick={() => analyzeDocument(doc)}
                  disabled={doc.status !== 'processed' || processing[doc.id]}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <Sparkles size={14} />
                  分析
                </ActionButton>
                
                <ActionButton
                  onClick={() => {/* TODO: 预览文档 */}}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <Eye size={14} />
                  预览
                </ActionButton>
                
                <ActionButton
                  className="danger"
                  onClick={() => deleteDocument(doc.id)}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <Trash2 size={14} />
                  删除
                </ActionButton>
              </DocumentActions>
              
              {processing[doc.id] && (
                <ProcessingOverlay
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                >
                  <ProcessingSpinner
                    animate={{ rotate: 360 }}
                    transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                  />
                  <div>长离正在分析文档...</div>
                </ProcessingOverlay>
              )}
            </DocumentCard>
          ))}
        </DocumentGrid>
      ) : (
        <EmptyState>
          <EmptyIcon>📚</EmptyIcon>
          <EmptyText>还没有上传任何文档</EmptyText>
          <EmptyHint>上传你的学习资料，让长离帮你提取重要单词</EmptyHint>
        </EmptyState>
      )}

      {analysisResults && (
        <AnalysisResults
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
        >
          <AnalysisTitle>
            <Sparkles size={20} />
            📖 《{analysisResults.documentName}》分析结果
          </AnalysisTitle>
          
          {analysisResults.words && analysisResults.words.length > 0 ? (
            <WordsList>
              {analysisResults.words.map((word, index) => (
                <WordItem key={index}>
                  <strong>{word.word}</strong>
                  {word.phonetic && <div>{word.phonetic}</div>}
                  <div>{word.definition}</div>
                </WordItem>
              ))}
            </WordsList>
          ) : (
            <div>
              <p>🐱 长离的分析结果：</p>
              <div style={{ 
                background: 'rgba(255,255,255,0.1)', 
                padding: '15px', 
                borderRadius: '10px',
                marginTop: '10px',
                whiteSpace: 'pre-wrap'
              }}>
                {analysisResults.rawResponse || '分析完成，但没有提取到结构化的单词数据。'}
              </div>
            </div>
          )}
        </AnalysisResults>
      )}
    </ManagerContainer>
  );
};

export default DocumentManager;