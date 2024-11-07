import React from 'react';
import { Box, IconButton, Typography } from '@mui/material';
// import CachedIcon from '@mui/icons-material/Cached';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import { useThemeContext } from '../ThemeContext';
import { SendMessageParams } from '../types/chat';

/**
 * Props for the MessageBubble component.
 */
interface MessageBubbleProps {
  messageId: string; // Unique identifier for the message
  messages: {
    text: string; // Text content of the message
    sender: 'user' | 'poet1' | 'poet2' | 'Judge' | 'response'; // Sender type
  }[];
  onRegenerate: (originalInput: SendMessageParams, messageId: string) => void; // Function to regenerate message content
  originalInput?: SendMessageParams; // Original input for the message, if available
  isLoading?: boolean; // Indicates if regeneration is in progress
  isStreaming?: boolean; // Indicates if the message is still streaming
}

/**
 * MessageBubble component
 * Displays individual messages in a styled bubble, supporting streaming and copying to clipboard.
 *
 * @param messageId - Unique identifier for the message.
 * @param messages - List of message objects with text and sender type.
 * @param onRegenerate - Callback for regenerating message content.
 * @param originalInput - Optional original input text for the message.
 * @param isLoading - Optional flag indicating if a regeneration action is loading.
 * @param isStreaming - Optional flag for indicating if the message is streaming.
 */
const MessageBubble: React.FC<MessageBubbleProps> = ({
  // messageId,
  messages,
  // onRegenerate,
  // originalInput,
}) => {
  const isUser = messages.some((msg) => msg.sender === 'user');
  const isJudge = messages.some((msg) => msg.sender === 'Judge');
  const isPoet1 = messages.some((msg) => msg.sender === 'poet1');
  const isPoet2 = messages.some((msg) => msg.sender === 'poet2');

  const { mode } = useThemeContext(); // Theme mode from context (light or dark)

  // const handleRegenerateClick = () => {
  //   if (originalInput) {
  //     onRegenerate(originalInput, messageId);
  //   }
  // };

  /**
   * Copies the messages' text content to the clipboard.
   */
  const handleCopyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(
        messages.map((msg) => msg.text).join('\n')
      );
      console.log('Messages copied to clipboard!');
    } catch (err) {
      console.error('Failed to copy the messages: ', err);
    }
  };

  return (
    <Box
      sx={{
        maxWidth: isJudge ? '100%' : '85%', // Full width for judge messages
        padding: '0 15px',
        borderRadius: isJudge ? '4px' : '12px', // Rounded corners for user and response
        backgroundColor: isJudge
          ? mode === 'light'
            ? '#E2ECE3'
            : '#3b583e85'
          : 'transparent', // Light background for judge messages
        color: isJudge ? (mode === 'light' ? 'black' : 'white') : 'primary',
        alignSelf: messages.some((msg) => msg.sender === 'user')
          ? 'flex-start'
          : 'flex-end',
        marginBottom: '16px',
        position: 'relative',
        whiteSpace: 'pre-wrap',
        textAlign: isJudge ? 'center' : 'right',
        // boxShadow: '0 1px 2px rgba(0,0,0,0.1)',
      }}
    >
      {/* {(isPoet1 || isPoet2) && (
        <Typography
          variant="caption"
          sx={{
            position: 'absolute',
            top: '-20px',
            right: '10px',
            color: '#666',
          }}
        >
          {isPoet1 ? originalInput?.poet1 : originalInput?.poet2}
        </Typography>
      )} */}

      {messages.map((msg, index) => (
        <Typography
          key={index}
          component="div"
          sx={{
            fontWeight: isUser ? '500' : '400',
            fontSize: '1.15rem',
            direction: 'rtl', // Right-to-left text direction
            textAlign: 'right',
            fontFamily: 'Arial, sans-serif', // Ensure proper Arabic text rendering
          }}
        >
          {msg.text}
        </Typography>
      ))}

      {/* Actions (copy and regenerate buttons) for non-user and non-poet messages */}
      {!isUser && !isPoet1 && !isPoet2 && (
        <Box
          sx={{ display: 'flex', justifyContent: 'flex-start', gap: 1, mt: 1 }}
        >
          {/* <IconButton
            aria-label="regenerate"
            color="secondary"
            onClick={handleRegenerateClick}
            // disabled={isLoading}
          >
            <CachedIcon fontSize="small" />
          </IconButton> */}
          <IconButton
            aria-label="copy"
            color="secondary"
            onClick={handleCopyToClipboard}
          >
            <ContentCopyIcon fontSize="small" />
          </IconButton>
        </Box>
      )}
    </Box>
  );
};

export default MessageBubble;
