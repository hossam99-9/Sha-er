import React from 'react';
import { Box, IconButton, Typography } from '@mui/material';
// import CachedIcon from '@mui/icons-material/Cached';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';

interface MessageBubbleProps {
  messageId: string;
  messages: {
    text: string;
    sender: 'user' | 'poet1' | 'poet2' | 'Judge' | 'response';
  }[];
  onRegenerate: (originalInput: string, messageId: string) => void;
  originalInput?: string;
  isLoading?: boolean;
  isStreaming?: boolean;
}

const MessageBubble: React.FC<MessageBubbleProps> = ({
  // messageId,
  messages,
  // onRegenerate,
  // originalInput,
  isStreaming,
}) => {
  const isUser = messages.some((msg) => msg.sender === 'user');
  const isJudge = messages.some((msg) => msg.sender === 'Judge');
  const isPoet1 = messages.some((msg) => msg.sender === 'poet1');
  const isPoet2 = messages.some((msg) => msg.sender === 'poet2');

  // const handleRegenerateClick = () => {
  //   if (originalInput) {
  //     onRegenerate(originalInput, messageId);
  //   }
  // };

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
        maxWidth: isJudge ? '100%' : '85%',
        padding: '15px',
        borderRadius: isJudge ? '4px' : '12px',
        backgroundColor: isJudge ? '#E2ECE3' : '#fff', // Default for user/response
        color: isJudge ? 'black' : 'black',
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
          {isPoet1 ? 'Poet 1' : 'Poet 2'}
        </Typography>
      )} */}

      {messages.map((msg, index) => (
        <Typography
          key={index}
          component="div"
          sx={{
            fontWeight: isUser ? '500' : '400',
            fontSize: '1.15rem',
            direction: 'rtl',
            textAlign: 'right',
            '&::after':
              isStreaming && messages[index + 1] ///need to recheck
                ? {
                    content: '"|"',
                    animation: 'blink 1s step-start infinite',
                    marginRight: '2px',
                    color: '#666',
                  }
                : {},
            '@keyframes blink': {
              '50%': {
                opacity: 0,
              },
            },
            fontFamily: 'Arial, sans-serif', // Ensure proper Arabic text rendering
          }}
        >
          {msg.text}
        </Typography>
      ))}

      {!isUser && !isPoet1 && !isPoet2 && (
        <Box
          sx={{ display: 'flex', justifyContent: 'flex-start', gap: 1, mt: 1 }}
        >
          {/* <IconButton
            aria-label="regenerate"
            color="secondary"
            onClick={handleRegenerateClick}
            disabled={isLoading}
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
