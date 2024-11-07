import React from 'react';
import { styled } from '@mui/material/styles';
import { Alert, Button } from '@mui/material';
import InputArea from './InputArea';
import ChatPanel from './ChatPanel';
import { useChat } from '../hooks/useChat';
import { ChatCategory } from '../types/chat';

/**
 * Props for the ChatContainer component.
 */
interface ChatContainerProps {
  selectedCategory: ChatCategory; // Currently selected chat category (0, 1, or 2)
  clearChat: boolean; // Flag to clear the chat messages
}

// Container with flex layout for chat panel and input area
const Container = styled('div')({
  display: 'flex',
  flexDirection: 'column',
  height: '100%',
});

// Styled alert for error messages
const StyledAlert = styled(Alert)(({ theme }) => ({
  marginBottom: theme.spacing(2),
  display: 'flex',
  flexDirection: 'row-reverse', // Display alert message in RTL format
}));

/**
 * ChatContainer component
 * Manages chat messages, input, and error handling within a specified chat category.
 *
 * @param selectedCategory - Active chat category for the session.
 * @param clearChat - Boolean to trigger message clearing in the chat.
 */
const ChatContainer: React.FC<ChatContainerProps> = ({
  selectedCategory,
  clearChat,
}) => {
  // Hooks to manage chat state, message sending, regeneration, and error handling
  const { messages, error, isLoading, sendMessage, regenerate, clearError } =
    useChat(selectedCategory, clearChat);

  return (
    <Container>
      {/* Error alert */}
      {error && (
        <StyledAlert
          severity="error"
          action={
            <Button color="inherit" size="small" onClick={clearError}>
              Dismiss
            </Button>
          }
        >
          {error}
        </StyledAlert>
      )}

      {/* Chat panel to display messages */}
      <ChatPanel
        messages={messages} // Array of messages for the selected category
        onRegenerate={(originalInput, messageId) =>
          regenerate({ originalInput, messageId, category: selectedCategory })
        } // Regenerates message based on original input and messageId
        isLoading={isLoading} // Loading state for ongoing message processing
      />

      {/* Input area for user message input and sending */}
      <InputArea
        selectedCategory={selectedCategory} // Passes current category to InputArea
        onSendMessage={(message) =>
          sendMessage({ ...message, category: selectedCategory })
        } // Sends message with the current category
        isLoading={isLoading} // Disables send button if loading
      />
    </Container>
  );
};

export default ChatContainer;
