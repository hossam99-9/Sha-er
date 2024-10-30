import React, { useRef, useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import axios from 'axios';
import InputArea from './InputArea';
import ChatPanel from './ChatPanel';

interface ChatContainerProps {
  selectedCategory: number;
  clearChat: boolean;
}

export interface Message {
  id: string;
  text: string;
  sender: 'user' | 'response' | 'poet1' | 'poet2' | 'Judge';
  originalInput?: string;
  isStreaming?: boolean;
  responseId?: string; // ID of the associated response message
}

type AnalysisResponse = {
  qafya: string;
  meter: string;
  critic: string;
  rhetorical: string;
};

const ChatContainer: React.FC<ChatContainerProps> = ({
  selectedCategory,
  clearChat,
}) => {
  // const queryClient = useQueryClient();
  const [messages, setMessages] = useState<Record<number, Message[]>>({
    0: [], // Analysis
    1: [], // Simulation
    2: [], // Battle
  });
  const webSocketRef = useRef<WebSocket | null>(null);
  const activeResponseIdRef = useRef<string | null>(null);

  // Analysis mutation using React Query
  const analysisMutation = useMutation({
    mutationFn: async ({
      text,
      responseId,
    }: {
      text: string;
      responseId: string;
    }) => {
      const response = await axios.post<AnalysisResponse>(
        'http://18.159.254.217:8002/analysis',
        {
          bait: text,
        }
      );
      return { data: response.data, responseId };
    },
    onSuccess: ({ data, responseId }) => {
      const formattedResponse = `${data.qafya}\n${data.meter}\n${data.critic}\n${data.rhetorical}`;
      updateResponseMessage(0, responseId, formattedResponse);
    },
  });

  const updateResponseMessage = (
    category: number,
    responseId: string,
    text: string
  ) => {
    setMessages((prev) => ({
      ...prev,
      [category]: prev[category].map((msg) =>
        msg.id === responseId ? { ...msg, text, isStreaming: false } : msg
      ),
    }));
  };

  const connectWebSocket = (
    url: string,
    onMessage: (event: MessageEvent) => void
  ) => {
    if (webSocketRef.current) {
      webSocketRef.current.close();
    }

    const ws = new WebSocket(url);
    webSocketRef.current = ws;
    ws.onmessage = onMessage;

    return ws;
  };

  const handleSimulationWebSocket = (text: string, responseId: string) => {
    const ws = connectWebSocket(
      `ws://18.159.254.217:8001/ws/generate?prompt=${text}`,
      (event) => {
        try {
          const data = JSON.parse(event.data);
          // Append only the new Arabic text
          setMessages((prev) => ({
            ...prev,
            1: prev[1].map((msg) =>
              msg.id === responseId
                ? {
                    ...msg,
                    text: msg.text + (data.bait || ''),
                    isStreaming: true,
                  }
                : msg
            ),
          }));
        } catch (e) {
          // If not JSON, treat as raw text
          setMessages((prev) => ({
            ...prev,
            1: prev[1].map((msg) =>
              msg.id === responseId
                ? { ...msg, text: msg.text + event.data, isStreaming: true }
                : msg
            ),
          }));
        }
      }
    );

    ws.onopen = () => {
      ws.send(JSON.stringify({ verse: text }));
    };
  };

  const handleBattleWebSocket = (
    poet1: string,
    poet2: string,
    topics: string
  ) => {
    // Create message IDs for each participant
    const poet1Id = Date.now().toString() + '-poet1';
    const poet2Id = Date.now().toString() + '-poet2';
    const judgeId = Date.now().toString() + '-Judge';

    // Initialize empty messages for all participants
    addMessage(2, {
      id: poet1Id,
      text: '',
      sender: 'poet1',
      isStreaming: true,
    });
    addMessage(2, {
      id: poet2Id,
      text: '',
      sender: 'poet2',
      isStreaming: true,
    });
    addMessage(2, {
      id: judgeId,
      text: '',
      sender: 'Judge',
      isStreaming: false, // Judge's response is not streamed
    });

    const ws = connectWebSocket(
      `ws://18.159.254.217:8000/ws/battle?poet1=${poet1}&poet2=${poet2}&topics=${topics}`,
      (event) => {
        const data = JSON.parse(event.data);

        setMessages((prev) => ({
          ...prev,
          2: prev[2].map((msg) => {
            if (msg.id === poet1Id && data.poet1) {
              return { ...msg, text: msg.text + data.poet1, isStreaming: true };
            }
            if (msg.id === poet2Id && data.poet2) {
              return { ...msg, text: msg.text + data.poet2, isStreaming: true };
            }
            if (msg.id === judgeId && data.Judge) {
              return {
                ...msg,
                text: (msg.text ? `${msg.text}\n\n` : '') + data.Judge,
                isStreaming: false, // Judge's response is not streamed
              };
            }
            return msg;
          }),
        }));
      }
    );

    ws.onopen = () => {
      ws.send(JSON.stringify({ verse: poet1, verse2: poet2, topics }));
    };
  };

  const addMessage = (category: number, message: Message) => {
    setMessages((prev) => ({
      ...prev,
      [category]: [...prev[category], message],
    }));
  };

  const handleSendMessage = async (message: {
    text: string;
    sender: 'user';
    poet1?: string;
    poet2?: string;
    topics?: string;
  }) => {
    const messageId = Date.now().toString();
    const responseId = messageId + '-response';
    activeResponseIdRef.current = responseId;

    // Add user message
    addMessage(selectedCategory, {
      id: messageId,
      ...message,
      originalInput: message.text,
    });

    // Add empty response message that will be updated
    addMessage(selectedCategory, {
      id: responseId,
      text: '',
      sender: 'response',
      isStreaming: true,
    });

    switch (selectedCategory) {
      case 0:
        analysisMutation.mutate({ text: message.text, responseId });
        break;
      case 1:
        handleSimulationWebSocket(message.text, responseId);
        break;
      case 2:
        if (message.poet1 && message.poet2 && message.topics) {
          handleBattleWebSocket(message.poet1, message.poet2, message.topics);
        }
        break;
    }
  };

  const handleRegenerate = async (originalInput: string, messageId: string) => {
    // Find the original message and its associated response
    const categoryMessages = messages[selectedCategory];
    const originalMessage = categoryMessages.find(
      (msg) => msg.id === messageId
    );

    if (!originalMessage) return;

    // Close existing WebSocket if any
    if (webSocketRef.current) {
      webSocketRef.current.close();
    }

    // Create new response message ID
    const newResponseId = Date.now().toString() + '-response';
    activeResponseIdRef.current = newResponseId;

    // Add new empty response message
    addMessage(selectedCategory, {
      id: newResponseId,
      text: '',
      sender: 'response',
      isStreaming: true,
    });

    // Handle regeneration based on category
    switch (selectedCategory) {
      case 0:
        analysisMutation.mutate({
          text: originalInput,
          responseId: newResponseId,
        });
        break;
      case 1:
        handleSimulationWebSocket(originalInput, newResponseId);
        break;
      case 2:
        // For battle category, we need to extract the original poets and topics
        const originalMessageData = JSON.parse(originalInput);
        handleBattleWebSocket(
          originalMessageData.poet1,
          originalMessageData.poet2,
          originalMessageData.topics
        );
        break;
    }
  };

  // Cleanup effect
  React.useEffect(() => {
    return () => {
      if (webSocketRef.current) {
        webSocketRef.current.close();
      }
    };
  }, []);

  // Clear messages effect
  React.useEffect(() => {
    if (clearChat) {
      setMessages((prev) => ({
        ...prev,
        [selectedCategory]: [],
      }));
      if (webSocketRef.current) {
        webSocketRef.current.close();
      }
    }
  }, [clearChat, selectedCategory]);

  return (
    <div>
      <ChatPanel
        messages={messages[selectedCategory] || []}
        onRegenerate={handleRegenerate}
        isLoading={analysisMutation.isPending}
      />
      <InputArea
        selectedCategory={selectedCategory}
        onSendMessage={handleSendMessage}
        isLoading={analysisMutation.isPending}
      />
    </div>
  );
};
export default ChatContainer;
