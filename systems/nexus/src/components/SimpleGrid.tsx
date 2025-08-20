import React from 'react';
import { Box, BoxProps } from '@mui/material';

interface SimpleGridProps extends BoxProps {
  container?: boolean;
  spacing?: number;
  size?: {
    xs?: number;
    sm?: number;
    md?: number;
    lg?: number;
    xl?: number;
  };
}

export const SimpleGrid: React.FC<SimpleGridProps> = ({ 
  container, 
  spacing = 0, 
  size, 
  children, 
  sx,
  ...props 
}) => {
  if (container) {
    return (
      <Box
        sx={{
          display: 'flex',
          flexWrap: 'wrap',
          gap: spacing,
          ...sx
        }}
        {...props}
      >
        {children}
      </Box>
    );
  }

  // Calculate flex basis based on size
  const getFlexBasis = () => {
    if (!size) return 'auto';
    
    // Use the largest defined size for simplicity
    const { xs = 12, sm, md, lg, xl } = size;
    const activeSize = xl || lg || md || sm || xs;
    
    return `${(activeSize / 12) * 100}%`;
  };

  return (
    <Box
      sx={{
        flexBasis: getFlexBasis(),
        minWidth: 0,
        ...sx
      }}
      {...props}
    >
      {children}
    </Box>
  );
};