import React from 'react';
import { Box, keyframes } from '@mui/material';

const bounce = keyframes`
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
`;

const LoadingDots: React.FC = () => (
  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
    {[...Array(3)].map((_, i) => (
      <Box
        key={i}
        sx={{
          width: 8,
          height: 8,
          backgroundColor: '#1976d2',
          borderRadius: '50%',
          margin: '0 5px',
          animation: `${bounce} 1.4s infinite ${i * 0.2}s`,
        }}
      />
    ))}
  </Box>
);

export default LoadingDots;
