import React from 'react';
import { Box, Avatar } from '@mui/material';
import MessageBubble from './MessageBubble';
import FeatherIcon from '../assets/icons/feather-icon.svg';
import { Message, SendMessageParams } from '../types/chat';

/**
 * Props for the ChatPanel component.
 */
interface ChatPanelProps {
  messages: Message[]; // Array of messages to display in the chat panel
  onRegenerate: (originalInput: SendMessageParams, messageId: string) => void; // Callback function to regenerate a message
  isLoading: boolean; // Indicates if a message is being processed
}

/**
 * ChatPanel component
 * Displays messages in a chat format with avatars and message bubbles.
 *
 * @param messages - List of messages to display.
 * @param onRegenerate - Callback to handle regenerating a message.
 * @param isLoading - Boolean indicating if a regeneration request is loading.
 */
const ChatPanel: React.FC<ChatPanelProps> = ({
  messages,
  onRegenerate,
  isLoading,
}) => {
  return (
    <Box
      p={3}
      sx={{
        height: '88vh',
        overflowY: 'auto', // Enables scrolling for overflow content
        direction: 'rtl', // Right-to-left direction for Arabic text alignment
        padding: '20px',
      }}
    >
      {messages.map((message, index) => {
        const avatarSrc = message.sender === 'user' ? '' : FeatherIcon; // Uses FeatherIcon for non-user avatars

        return (
          <Box
            key={index}
            sx={{
              display: 'flex',
              marginY: '18px', // Adds vertical space between message blocks
              boxShadow: '-moz-initial',
            }}
          >
            {message.sender !== 'Judge' && message.text && (
              <Avatar
                src={avatarSrc}
                sx={{
                  marginLeft: '10px',
                  marginRight: message.sender === 'poet2' ? 'auto' : 0, // Adjusts alignment for poet2 messages
                  backgroundColor:
                    message.sender === 'user' ? '#C3CFD4' : '#fff', // Light background for user avatar

                  width: '40px',
                  height: '40px',
                  border: '0.02px solid #C3CFD4',
                  '& .MuiAvatar-img': {
                    width: message.sender === 'user' ? '16px' : '25px',
                    height: message.sender === 'user' ? '16px' : '25px',
                  },
                }}
              />
            )}
            {message.text && (
              <MessageBubble
                key={index}
                messageId={message.id}
                messages={[message]} // Wraps each message individually in a MessageBubble
                onRegenerate={onRegenerate}
                originalInput={message.originalInput}
                isLoading={isLoading}
                isStreaming={message.isStreaming}
              />
            )}
          </Box>
        );
      })}
    </Box>
  );
};

export default ChatPanel;
