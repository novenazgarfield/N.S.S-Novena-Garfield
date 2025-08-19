import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import styled from 'styled-components';
import { Sparkles, RotateCcw, CheckCircle, AlertCircle } from 'lucide-react';

const BeachContainer = styled(motion.div)`
  max-width: 600px;
  margin: 0 auto;
  background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
  border-radius: 20px;
  padding: 30px;
  box-shadow: 0 20px 40px rgba(252, 182, 159, 0.3);
  position: relative;
  overflow: hidden;
`;

const BeachTitle = styled.h2`
  text-align: center;
  color: #8b4513;
  font-size: 2rem;
  margin-bottom: 20px;
  text-shadow: 0 2px 4px rgba(139, 69, 19, 0.3);
`;

const SandCanvas = styled.canvas`
  width: 100%;
  height: 200px;
  background: linear-gradient(135deg, #f4e4bc 0%, #e6d3a3 100%);
  border-radius: 15px;
  border: 3px solid #d4af37;
  cursor: crosshair;
  box-shadow: inset 0 4px 8px rgba(0,0,0,0.1);
`;

const WordDisplay = styled(motion.div)`
  text-align: center;
  margin: 20px 0;
  font-size: 2.5rem;
  font-weight: bold;
  color: #8b4513;
  text-shadow: 0 2px 4px rgba(139, 69, 19, 0.2);
  letter-spacing: 3px;
`;

const TracingWord = styled.div`
  font-size: 3rem;
  font-weight: bold;
  color: rgba(139, 69, 19, 0.3);
  text-align: center;
  margin: 20px 0;
  letter-spacing: 4px;
  text-shadow: 0 2px 4px rgba(139, 69, 19, 0.1);
  position: relative;
  
  &::after {
    content: '';
    position: absolute;
    bottom: -5px;
    left: 0;
    right: 0;
    height: 2px;
    background: repeating-linear-gradient(
      to right,
      #d4af37,
      #d4af37 10px,
      transparent 10px,
      transparent 20px
    );
  }
`;

const InputArea = styled.div`
  margin: 20px 0;
  text-align: center;
`;

const SpellingInput = styled(motion.input)`
  font-size: 2rem;
  padding: 15px 20px;
  border: 3px solid #d4af37;
  border-radius: 15px;
  background: rgba(255, 255, 255, 0.9);
  color: #8b4513;
  text-align: center;
  letter-spacing: 2px;
  font-weight: bold;
  width: 300px;
  max-width: 100%;
  
  &:focus {
    outline: none;
    border-color: #ff6b6b;
    box-shadow: 0 0 20px rgba(255, 107, 107, 0.3);
  }
  
  &.correct {
    border-color: #4ecdc4;
    background: rgba(78, 205, 196, 0.1);
  }
  
  &.incorrect {
    border-color: #ff6b6b;
    background: rgba(255, 107, 107, 0.1);
  }
`;

const ProgressBar = styled.div`
  width: 100%;
  height: 8px;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 4px;
  margin: 20px 0;
  overflow: hidden;
`;

const ProgressFill = styled(motion.div)`
  height: 100%;
  background: linear-gradient(90deg, #4ecdc4, #44a08d);
  border-radius: 4px;
`;

const ActionButtons = styled.div`
  display: flex;
  gap: 15px;
  justify-content: center;
  margin-top: 20px;
`;

const ActionButton = styled(motion.button)`
  background: ${props => {
    if (props.primary) return 'linear-gradient(135deg, #4ecdc4, #44a08d)';
    if (props.danger) return 'linear-gradient(135deg, #ff6b6b, #ee5a24)';
    return 'linear-gradient(135deg, #ffecd2, #fcb69f)';
  }};
  border: none;
  border-radius: 25px;
  padding: 12px 24px;
  color: ${props => props.primary || props.danger ? 'white' : '#8b4513'};
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.1);
  
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

const FeedbackMessage = styled(motion.div)`
  text-align: center;
  padding: 15px;
  border-radius: 15px;
  margin: 20px 0;
  font-size: 1.2rem;
  font-weight: 600;
  
  &.success {
    background: linear-gradient(135deg, #4ecdc4, #44a08d);
    color: white;
  }
  
  &.error {
    background: linear-gradient(135deg, #ff6b6b, #ee5a24);
    color: white;
  }
  
  &.hint {
    background: linear-gradient(135deg, #ffecd2, #fcb69f);
    color: #8b4513;
    border: 2px solid #d4af37;
  }
`;

const Fireworks = styled(motion.div)`
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  z-index: 10;
`;

const MagicBeach = ({ wordData, onComplete, onClose }) => {
  const [phase, setPhase] = useState('tracing'); // 'tracing' | 'spelling'
  const [userInput, setUserInput] = useState('');
  const [feedback, setFeedback] = useState(null);
  const [mistakes, setMistakes] = useState(0);
  const [startTime, setStartTime] = useState(Date.now());
  const [showFireworks, setShowFireworks] = useState(false);
  const [tracingProgress, setTracingProgress] = useState(0);
  
  const canvasRef = useRef(null);
  const isDrawing = useRef(false);
  const lastPos = useRef({ x: 0, y: 0 });

  useEffect(() => {
    if (phase === 'tracing') {
      initializeCanvas();
    }
  }, [phase, wordData]);

  const initializeCanvas = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const rect = canvas.getBoundingClientRect();
    
    // 设置canvas实际大小
    canvas.width = rect.width * window.devicePixelRatio;
    canvas.height = rect.height * window.devicePixelRatio;
    ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
    
    // 绘制沙滩背景
    drawSandBackground(ctx, rect.width, rect.height);
    
    // 绘制单词轮廓
    drawWordOutline(ctx, wordData.word, rect.width, rect.height);
  };

  const drawSandBackground = (ctx, width, height) => {
    // 绘制沙滩纹理
    ctx.fillStyle = '#f4e4bc';
    ctx.fillRect(0, 0, width, height);
    
    // 添加沙粒效果
    for (let i = 0; i < 100; i++) {
      ctx.fillStyle = `rgba(212, 175, 55, ${Math.random() * 0.3})`;
      ctx.beginPath();
      ctx.arc(
        Math.random() * width,
        Math.random() * height,
        Math.random() * 2,
        0,
        Math.PI * 2
      );
      ctx.fill();
    }
  };

  const drawWordOutline = (ctx, word, width, height) => {
    ctx.font = 'bold 48px Arial';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    
    // 绘制虚线轮廓
    ctx.strokeStyle = '#d4af37';
    ctx.lineWidth = 3;
    ctx.setLineDash([10, 5]);
    ctx.strokeText(word, width / 2, height / 2);
    ctx.setLineDash([]);
  };

  const handleCanvasMouseDown = (e) => {
    isDrawing.current = true;
    const rect = canvasRef.current.getBoundingClientRect();
    lastPos.current = {
      x: e.clientX - rect.left,
      y: e.clientY - rect.top
    };
  };

  const handleCanvasMouseMove = (e) => {
    if (!isDrawing.current) return;
    
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    const rect = canvas.getBoundingClientRect();
    
    const currentPos = {
      x: e.clientX - rect.left,
      y: e.clientY - rect.top
    };
    
    // 绘制描摹轨迹
    ctx.strokeStyle = '#8b4513';
    ctx.lineWidth = 4;
    ctx.lineCap = 'round';
    ctx.beginPath();
    ctx.moveTo(lastPos.current.x, lastPos.current.y);
    ctx.lineTo(currentPos.x, currentPos.y);
    ctx.stroke();
    
    lastPos.current = currentPos;
    
    // 更新描摹进度
    setTracingProgress(prev => Math.min(prev + 1, 100));
  };

  const handleCanvasMouseUp = () => {
    isDrawing.current = false;
    
    // 检查描摹完成度
    if (tracingProgress >= 80) {
      setFeedback({
        type: 'success',
        message: '描摹完成！现在试试默写吧！'
      });
      
      setTimeout(() => {
        setPhase('spelling');
        setFeedback(null);
      }, 2000);
    }
  };

  const handleInputChange = (e) => {
    const value = e.target.value.toLowerCase();
    setUserInput(value);
    
    // 实时检查拼写
    const targetWord = wordData.word.toLowerCase();
    if (value === targetWord) {
      handleSpellingComplete(true);
    } else if (value.length >= targetWord.length) {
      handleSpellingComplete(false);
    }
  };

  const handleSpellingComplete = (isCorrect) => {
    const timeSpent = Date.now() - startTime;
    
    if (isCorrect) {
      setFeedback({
        type: 'success',
        message: '🎉 太棒了！拼写正确！'
      });
      
      setShowFireworks(true);
      
      // 播放成功音效
      if (window.utils) {
        window.utils.playSound('success');
      }
      
      setTimeout(() => {
        if (onComplete) {
          onComplete({
            wordId: wordData.id,
            isCorrect: true,
            timeSpent,
            mistakes,
            userInput
          });
        }
      }, 3000);
      
    } else {
      setMistakes(prev => prev + 1);
      setFeedback({
        type: 'error',
        message: `拼写错误，再试一次！错误次数：${mistakes + 1}`
      });
      
      // 清空输入
      setTimeout(() => {
        setUserInput('');
        setFeedback(null);
      }, 2000);
    }
  };

  const resetTracing = () => {
    setTracingProgress(0);
    initializeCanvas();
  };

  const skipToSpelling = () => {
    setPhase('spelling');
    setFeedback(null);
  };

  const showHint = () => {
    const word = wordData.word;
    const hintLength = Math.ceil(word.length / 3);
    const hint = word.substring(0, hintLength) + '...';
    
    setFeedback({
      type: 'hint',
      message: `提示：${hint}`
    });
    
    setTimeout(() => setFeedback(null), 3000);
  };

  if (!wordData) return null;

  return (
    <BeachContainer
      initial={{ scale: 0.8, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      exit={{ scale: 0.8, opacity: 0 }}
      transition={{ type: "spring", stiffness: 300, damping: 30 }}
    >
      <BeachTitle>
        🏖️ 魔法沙滩 - {phase === 'tracing' ? '描摹练习' : '拼写挑战'}
      </BeachTitle>

      {phase === 'tracing' ? (
        <>
          <TracingWord>{wordData.word}</TracingWord>
          <SandCanvas
            ref={canvasRef}
            onMouseDown={handleCanvasMouseDown}
            onMouseMove={handleCanvasMouseMove}
            onMouseUp={handleCanvasMouseUp}
            onMouseLeave={handleCanvasMouseUp}
          />
          <ProgressBar>
            <ProgressFill
              initial={{ width: 0 }}
              animate={{ width: `${tracingProgress}%` }}
              transition={{ duration: 0.3 }}
            />
          </ProgressBar>
          <div style={{ textAlign: 'center', color: '#8b4513' }}>
            描摹进度: {tracingProgress}%
          </div>
        </>
      ) : (
        <>
          <WordDisplay>
            {wordData.definition}
          </WordDisplay>
          <InputArea>
            <SpellingInput
              type="text"
              value={userInput}
              onChange={handleInputChange}
              placeholder="在这里输入单词..."
              className={feedback?.type === 'success' ? 'correct' : 
                       feedback?.type === 'error' ? 'incorrect' : ''}
              autoFocus
            />
          </InputArea>
        </>
      )}

      <AnimatePresence>
        {feedback && (
          <FeedbackMessage
            className={feedback.type}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
          >
            {feedback.message}
          </FeedbackMessage>
        )}
      </AnimatePresence>

      <ActionButtons>
        {phase === 'tracing' ? (
          <>
            <ActionButton onClick={resetTracing}>
              <RotateCcw size={20} />
              重新描摹
            </ActionButton>
            <ActionButton onClick={skipToSpelling} primary>
              <Sparkles size={20} />
              跳过描摹
            </ActionButton>
          </>
        ) : (
          <>
            <ActionButton onClick={showHint}>
              <AlertCircle size={20} />
              提示
            </ActionButton>
            <ActionButton onClick={() => setPhase('tracing')}>
              <RotateCcw size={20} />
              重新描摹
            </ActionButton>
          </>
        )}
        
        <ActionButton onClick={onClose} danger>
          关闭
        </ActionButton>
      </ActionButtons>

      <AnimatePresence>
        {showFireworks && (
          <Fireworks
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            {[...Array(20)].map((_, i) => (
              <motion.div
                key={i}
                style={{
                  position: 'absolute',
                  left: `${Math.random() * 100}%`,
                  top: `${Math.random() * 100}%`,
                  fontSize: '2rem',
                }}
                initial={{ scale: 0, rotate: 0 }}
                animate={{ 
                  scale: [0, 1, 0], 
                  rotate: 360,
                  y: [0, -50, 0]
                }}
                transition={{ 
                  duration: 2, 
                  delay: i * 0.1,
                  repeat: 2
                }}
              >
                ✨
              </motion.div>
            ))}
          </Fireworks>
        )}
      </AnimatePresence>
    </BeachContainer>
  );
};

export default MagicBeach;