import React from 'react';
import { motion } from 'framer-motion';
import styled from 'styled-components';

const StyledButton = styled(motion.button)`
  background: ${props => {
    if (props.variant === 'primary') return 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
    if (props.variant === 'secondary') return 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)';
    if (props.variant === 'success') return 'linear-gradient(135deg, #4ecdc4 0%, #44a08d 100%)';
    if (props.variant === 'danger') return 'linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%)';
    if (props.variant === 'warning') return 'linear-gradient(135deg, #feca57 0%, #ff9ff3 100%)';
    return 'linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)';
  }};
  
  border: none;
  border-radius: ${props => props.rounded ? '25px' : '12px'};
  padding: ${props => {
    if (props.size === 'small') return '8px 16px';
    if (props.size === 'large') return '16px 32px';
    return '12px 24px';
  }};
  
  color: ${props => props.variant === 'default' ? '#333' : 'white'};
  font-size: ${props => {
    if (props.size === 'small') return '0.875rem';
    if (props.size === 'large') return '1.125rem';
    return '1rem';
  }};
  font-weight: 600;
  cursor: pointer;
  
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  
  &:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
  }
  
  &:active:not(:disabled) {
    transform: translateY(0);
  }
  
  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none;
  }
  
  ${props => props.fullWidth && 'width: 100%;'}
`;

const Button = ({
  children,
  variant = 'default',
  size = 'medium',
  rounded = false,
  fullWidth = false,
  disabled = false,
  loading = false,
  icon,
  onClick,
  ...props
}) => {
  return (
    <StyledButton
      variant={variant}
      size={size}
      rounded={rounded}
      fullWidth={fullWidth}
      disabled={disabled || loading}
      onClick={onClick}
      whileHover={{ scale: disabled ? 1 : 1.02 }}
      whileTap={{ scale: disabled ? 1 : 0.98 }}
      {...props}
    >
      {loading ? (
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
        >
          ⏳
        </motion.div>
      ) : (
        <>
          {icon && <span>{icon}</span>}
          {children}
        </>
      )}
    </StyledButton>
  );
};

export default Button;