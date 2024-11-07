import React, { useState } from 'react';
import Sidebar from './Sidebar';
import ChatContainer from './ChatContainer';
import { Box, Typography, useTheme } from '@mui/material';
import { ChatCategory } from '../types/chat';

/**
 * ChatLayout component
 * Provides the main layout for the chat interface, including a sidebar and chat container.
 */
const ChatLayout: React.FC = () => {
  const theme = useTheme(); // Accesses the current theme for styling
  const [selectedCategory, setSelectedCategory] = useState<ChatCategory>(0); // Selected chat category state
  const [clearChat, setClearChat] = useState(false); // State to trigger chat clearing

  /**
   * Clears messages in the chat container.
   * Sets `clearChat` to true momentarily to trigger a reset.
   */
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
      sx={{
        direction: 'rtl', // Right-to-left text direction for Arabic
        backgroundColor: theme.palette.background.default, // Background color based on theme
      }}
    >
      {/* Sidebar with category selection and message clearing */}
      <Sidebar
        selectedCategory={selectedCategory} // Current selected category
        onCategorySelect={setSelectedCategory} // Handler to change selected category
        clearMessages={clearMessages} // Clears chat messages when called
      />

      {/* Main chat area */}
      <Box sx={{ padding: '0 32px', height: '99vh', width: '100%' }}>
        <Box
          sx={{
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'space-between',
            height: '95%',
          }}
        >
          {/* Chat container for displaying messages */}
          <ChatContainer
            selectedCategory={selectedCategory} // Passes selected category to filter messages
            clearChat={clearChat} // Boolean flag to clear chat on demand
          />

          {/* Informational disclaimer at the bottom of the chat */}
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
