import React, { useState } from 'react';
import Sidebar from './Sidebar';
import ChatContainer from './ChatContainer';
import { Box, Typography } from '@mui/material';

const ChatLayout: React.FC = () => {
  const [selectedCategory, setSelectedCategory] = useState(0);
  const [clearChat, setClearChat] = useState(false);

  const clearMessages = () => {
    setClearChat(true);
    setTimeout(() => {
      setClearChat(false);
    }, 100);
  };

  return (
    <Box
      display={'flex'}
      flexDirection={'row'}
      sx={{ direction: 'rtl', backgroundColor: '#fff' }}
    >
      <Sidebar
        selectedCategory={selectedCategory}
        onCategorySelect={setSelectedCategory}
        clearMessages={clearMessages}
      />
      <Box sx={{ padding: '0 32px', height: '100vh', width: '100%' }}>
        <Box
          sx={{
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'space-between',
            height: '95%',
          }}
        >
          <ChatContainer
            selectedCategory={selectedCategory}
            clearChat={clearChat}
          />
          <Typography
            variant="caption"
            color="textSecondary"
            align="center"
            sx={{ marginY: '10px' }}
            display={'flex'}
            justifyContent={'center'}
          >
            شاعر قد يخطئ - يجب أن تأخذ في الاعتبار التحقق من المعلومات المهمة.
          </Typography>
        </Box>
      </Box>
    </Box>
  );
};

export default ChatLayout;
