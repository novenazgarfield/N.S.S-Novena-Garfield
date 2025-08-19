import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import styled from 'styled-components';
import { Volume2, RotateCcw, CheckCircle, XCircle } from 'lucide-react';

const CapsuleContainer = styled(motion.div)`
  max-width: 500px;
  margin: 0 auto;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 20px;
  padding: 30px;
  box-shadow: 0 20px 40px rgba(102, 126, 234, 0.3);
  color: white;
  position: relative;
  overflow: hidden;
  
  &::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: linear-gradient(45deg, transparent, rgba(255,255,255,0.1), transparent);
    transform: rotate(45deg);
    animation: shimmer 3s infinite;
  }
  
  @keyframes shimmer {
    0% { transform: translateX(-100%) translateY(-100%) rotate(45deg); }
    100% { transform: translateX(100%) translateY(100%) rotate(45deg); }
  }
`;

const WordHeader = styled.div`
  text-align: center;
  margin-bottom: 30px;
  position: relative;
  z-index: 1;
`;

const MainWord = styled(motion.h1)`
  font-size: 3rem;
  font-weight: bold;
  margin: 0;
  text-shadow: 0 4px 8px rgba(0,0,0,0.3);
  letter-spacing: 2px;
`;

const Phonetic = styled.div`
  font-size: 1.2rem;
  opacity: 0.9;
  margin: 10px 0;
  font-family: 'Courier New', monospace;
`;

const Definition = styled.div`
  font-size: 1.1rem;
  opacity: 0.95;
  margin-bottom: 20px;
`;

const PronunciationButton = styled(motion.button)`
  background: rgba(255, 255, 255, 0.2);
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50px;
  padding: 12px 20px;
  color: white;
  font-size: 1rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0 auto;
  backdrop-filter: blur(10px);
  
  &:hover {
    background: rgba(255, 255, 255, 0.3);
    border-color: rgba(255, 255, 255, 0.5);
  }
`;

const ContentSection = styled(motion.div)`
  background: rgba(255, 255, 255, 0.1);
  border-radius: 15px;
  padding: 20px;
  margin: 20px 0;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
`;

const SectionTitle = styled.h3`
  margin: 0 0 15px 0;
  font-size: 1.3rem;
  display: flex;
  align-items: center;
  gap: 10px;
`;

const SectionContent = styled.div`
  line-height: 1.6;
  font-size: 1rem;
  opacity: 0.95;
`;

const ExpandableSection = styled(motion.div)`
  cursor: pointer;
  
  .content {
    overflow: hidden;
  }
`;

const ActionButtons = styled.div`
  display: flex;
  gap: 15px;
  justify-content: center;
  margin-top: 30px;
`;

const ActionButton = styled(motion.button)`
  background: ${props => props.primary ? 
    'linear-gradient(135deg, #ff6b6b, #ee5a24)' : 
    'rgba(255, 255, 255, 0.2)'};
  border: none;
  border-radius: 25px;
  padding: 12px 24px;
  color: white;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  backdrop-filter: blur(10px);
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(0,0,0,0.2);
  }
`;

const LearningCapsule = ({ wordData, onClose, onStartPractice }) => {
  const [aiContent, setAiContent] = useState(null);
  const [loading, setLoading] = useState(true);
  const [expandedSections, setExpandedSections] = useState({
    memory: false,
    context: false,
    tips: false
  });

  useEffect(() => {
    loadAIContent();
  }, [wordData]);

  const loadAIContent = async () => {
    try {
      setLoading(true);
      if (window.backendAPI && wordData) {
        const response = await window.backendAPI.generateAIContent(wordData);
        if (response.success) {
          setAiContent(response.data);
        }
      }
    } catch (error) {
      console.error('加载AI内容失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const playPronunciation = () => {
    if (window.utils) {
      window.utils.playSound('pronunciation');
    }
    
    // 使用Web Speech API播放发音
    if ('speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(wordData.word);
      utterance.lang = 'en-US';
      utterance.rate = 0.8;
      speechSynthesis.speak(utterance);
    }
  };

  const toggleSection = (section) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  const handleStartPractice = () => {
    if (onStartPractice) {
      onStartPractice(wordData);
    }
  };

  if (!wordData) return null;

  return (
    <AnimatePresence>
      <CapsuleContainer
        initial={{ scale: 0.8, opacity: 0, y: 50 }}
        animate={{ scale: 1, opacity: 1, y: 0 }}
        exit={{ scale: 0.8, opacity: 0, y: 50 }}
        transition={{ type: "spring", stiffness: 300, damping: 30 }}
      >
        <WordHeader>
          <MainWord
            initial={{ y: -20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.2 }}
          >
            {wordData.word}
          </MainWord>
          
          {wordData.phonetic && (
            <Phonetic>{wordData.phonetic}</Phonetic>
          )}
          
          <Definition>{wordData.definition}</Definition>
          
          <PronunciationButton
            onClick={playPronunciation}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <Volume2 size={20} />
            发音
          </PronunciationButton>
        </WordHeader>

        {loading ? (
          <ContentSection>
            <div style={{ textAlign: 'center', padding: '20px' }}>
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                style={{ display: 'inline-block' }}
              >
                ⏳
              </motion.div>
              <div style={{ marginTop: '10px' }}>长离正在为你准备专属内容...</div>
            </div>
          </ContentSection>
        ) : (
          <>
            {aiContent?.memoryStory && (
              <ExpandableSection onClick={() => toggleSection('memory')}>
                <ContentSection
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.3 }}
                >
                  <SectionTitle>
                    🐱 长离的记忆
                    <motion.span
                      animate={{ rotate: expandedSections.memory ? 180 : 0 }}
                      style={{ fontSize: '0.8em' }}
                    >
                      ▼
                    </motion.span>
                  </SectionTitle>
                  <AnimatePresence>
                    {expandedSections.memory && (
                      <motion.div
                        className="content"
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: 'auto', opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        transition={{ duration: 0.3 }}
                      >
                        <SectionContent>{aiContent.memoryStory}</SectionContent>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </ContentSection>
              </ExpandableSection>
            )}

            {aiContent?.contextStory && (
              <ExpandableSection onClick={() => toggleSection('context')}>
                <ContentSection
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.4 }}
                >
                  <SectionTitle>
                    📖 语境故事
                    <motion.span
                      animate={{ rotate: expandedSections.context ? 180 : 0 }}
                      style={{ fontSize: '0.8em' }}
                    >
                      ▼
                    </motion.span>
                  </SectionTitle>
                  <AnimatePresence>
                    {expandedSections.context && (
                      <motion.div
                        className="content"
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: 'auto', opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        transition={{ duration: 0.3 }}
                      >
                        <SectionContent>{aiContent.contextStory}</SectionContent>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </ContentSection>
              </ExpandableSection>
            )}

            {aiContent?.learningTips && (
              <ExpandableSection onClick={() => toggleSection('tips')}>
                <ContentSection
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.5 }}
                >
                  <SectionTitle>
                    💡 学习技巧
                    <motion.span
                      animate={{ rotate: expandedSections.tips ? 180 : 0 }}
                      style={{ fontSize: '0.8em' }}
                    >
                      ▼
                    </motion.span>
                  </SectionTitle>
                  <AnimatePresence>
                    {expandedSections.tips && (
                      <motion.div
                        className="content"
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: 'auto', opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        transition={{ duration: 0.3 }}
                      >
                        <SectionContent style={{ whiteSpace: 'pre-line' }}>
                          {aiContent.learningTips}
                        </SectionContent>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </ContentSection>
              </ExpandableSection>
            )}
          </>
        )}

        <ActionButtons>
          <ActionButton
            onClick={handleStartPractice}
            primary
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <CheckCircle size={20} />
            开始练习
          </ActionButton>
          
          <ActionButton
            onClick={loadAIContent}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <RotateCcw size={20} />
            重新生成
          </ActionButton>
          
          <ActionButton
            onClick={onClose}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <XCircle size={20} />
            关闭
          </ActionButton>
        </ActionButtons>
      </CapsuleContainer>
    </AnimatePresence>
  );
};

export default LearningCapsule;