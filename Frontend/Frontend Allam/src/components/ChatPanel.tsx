import React from 'react';
import { Box, Avatar } from '@mui/material';
import MessageBubble from './MessageBubble';
import FeatherIcon from '../assets/icons/feather-icon.svg';
import { Message } from './ChatContainer';

interface ChatPanelProps {
  messages: Message[];
  onRegenerate: (originalInput: string, messageId: string) => void;
  isLoading: boolean;
}

const ChatPanel: React.FC<ChatPanelProps> = ({
  messages,
  onRegenerate,
  isLoading,
}) => {
  return (
    <Box
      p={3}
      sx={{
        height: '90vh',
        overflowY: 'auto',
        direction: 'rtl',
        padding: '20px',
      }}
    >
      {messages.map((message, index) => {
        const avatarSrc = message.sender === 'user' ? '' : FeatherIcon;
        return (
          <Box
            key={index}
            sx={{
              display: 'flex',
              marginY: '18px',
            }}
          >
            {message.sender !== 'Judge' && message.text && (
              <Avatar
                src={avatarSrc}
                sx={{
                  marginLeft: '10px',
                  marginRight: message.sender === 'poet2' ? '8rem' : 0,
                  backgroundColor:
                    message.sender === 'user' ? '#C3CFD4' : '#fff',
                  //   : message.sender === 'poet1'
                  // ? '#62a3d06e'
                  // : message.sender === 'poet2'
                  //   ? '#ab3e4b45'
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
                messages={[message]}
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
