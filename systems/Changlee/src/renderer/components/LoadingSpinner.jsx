import React from 'react';
import { motion } from 'framer-motion';
import styled from 'styled-components';

const SpinnerContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: ${props => props.size === 'large' ? '40px' : '20px'};
  gap: 16px;
`;

const Spinner = styled(motion.div)`
  width: ${props => {
    if (props.size === 'small') return '24px';
    if (props.size === 'large') return '64px';
    return '40px';
  }};
  height: ${props => {
    if (props.size === 'small') return '24px';
    if (props.size === 'large') return '64px';
    return '40px';
  }};
  border: 3px solid #f3f3f3;
  border-top: 3px solid #667eea;
  border-radius: 50%;
`;

const LoadingText = styled.div`
  color: #666;
  font-size: ${props => {
    if (props.size === 'small') return '0.875rem';
    if (props.size === 'large') return '1.125rem';
    return '1rem';
  }};
  text-align: center;
`;

const EmojiSpinner = styled(motion.div)`
  font-size: ${props => {
    if (props.size === 'small') return '1.5rem';
    if (props.size === 'large') return '3rem';
    return '2rem';
  }};
`;

const LoadingSpinner = ({ 
  size = 'medium', 
  text = '加载中...', 
  type = 'spinner', // 'spinner' | 'emoji'
  emoji = '🤔'
}) => {
  return (
    <SpinnerContainer size={size}>
      {type === 'spinner' ? (
        <Spinner
          size={size}
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
        />
      ) : (
        <EmojiSpinner
          size={size}
          animate={{ 
            rotate: [0, 10, -10, 0],
            scale: [1, 1.1, 1]
          }}
          transition={{ 
            duration: 2, 
            repeat: Infinity, 
            ease: "easeInOut" 
          }}
        >
          {emoji}
        </EmojiSpinner>
      )}
      
      {text && (
        <LoadingText size={size}>
          {text}
        </LoadingText>
      )}
    </SpinnerContainer>
  );
};

export default LoadingSpinner;