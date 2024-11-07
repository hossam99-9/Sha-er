// useChat hook
import { useState, useCallback, useEffect } from 'react';
import { chatService } from '../services/chatService';
import {
  ChatState,
  Message,
  SendMessageParams,
  RegenerateParams,
  ChatCategory,
  MessageSender,
  AnalysisResponse,
} from '../types/chat';
import { useMutation } from '@tanstack/react-query';

interface AnalysisMutationParams {
  text: string;
  responseId: string;
}

const INITIAL_STATE: ChatState = {
  messages: {
    0: [],
    1: [],
    2: [],
  },
  error: null,
  isLoading: false,
};

export const useChat = (selectedCategory: ChatCategory, clearChat: boolean) => {
  const [state, setState] = useState<ChatState>(INITIAL_STATE);

  const updateMessages = useCallback(
    (category: ChatCategory, updater: (messages: Message[]) => Message[]) => {
      setState((prev) => ({
        ...prev,
        messages: {
          ...prev.messages,
          [category]: updater(prev.messages[category] || []),
        },
      }));
    },
    []
  );

  const addMessage = useCallback(
    (category: ChatCategory, message: Message) => {
      updateMessages(category, (messages) => [
        ...messages,
        {
          ...message,
          timestamp: Date.now(),
          status: 'pending',
        },
      ]);
    },
    [updateMessages]
  );

  const updateMessageStatus = useCallback(
    (
      category: ChatCategory,
      messageId: string,
      status: 'success' | 'error',
      error?: string
    ) => {
      updateMessages(category, (messages) =>
        messages.map((msg) =>
          msg.id === messageId ? { ...msg, status, error } : msg
        )
      );
    },
    [updateMessages]
  );

  const analysisMutation = useMutation<
    { data: AnalysisResponse; responseId: string },
    Error,
    AnalysisMutationParams
  >({
    mutationFn: ({ text, responseId }) =>
      chatService.analyzeText(text, responseId),
    onSuccess: ({ data, responseId }) => {
      const formattedResponse = `${data.qafya}\n${data.meter}\n${data.critic}\n${data.rhetorical}`;
      updateMessages(0, (messages) =>
        messages.map((msg) =>
          msg.id === responseId
            ? {
                ...msg,
                text: formattedResponse,
                isStreaming: false,
                status: 'success',
              }
            : msg
        )
      );
    },
    onError: (error, { responseId }) => {
      updateMessageStatus(0, responseId, 'error', error.message);
    },
  });

  const handleSimulationMessage = useCallback(
    (responseId: string, newText: string, isStreaming: boolean) => {
      updateMessages(1, (messages) =>
        messages.map((msg) =>
          msg.id === responseId
            ? {
                ...msg,
                text: msg.text + newText,
                isStreaming,
                status: isStreaming ? 'pending' : 'success',
              }
            : msg
        )
      );
    },
    [updateMessages]
  );
  const handleBattleMessage = useCallback(
    (updatedMessages: Message[]) => {
      updateMessages(2, (messages) => {
        const newMessages = [...messages];

        updatedMessages.forEach((incomingMessage) => {
          // Extract the round from the message ID (assumes round is included in the message ID or other logic to determine the round)
          const roundId = incomingMessage.id.split('-round-')[1] || '1';

          // Check if there's an existing message for this round and sender (poet1, poet2, or judge)
          const existingMessageIndex = newMessages.findIndex(
            (msg) =>
              msg.sender === incomingMessage.sender &&
              msg.id.includes(`round-${roundId}`) &&
              msg.isStreaming
          );

          if (
            incomingMessage.sender === 'poet1' ||
            incomingMessage.sender === 'poet2'
          ) {
            if (existingMessageIndex !== -1) {
              // Accumulate text for poet1 or poet2 in the current round
              newMessages[existingMessageIndex] = {
                ...newMessages[existingMessageIndex],
                text:
                  newMessages[existingMessageIndex].text + incomingMessage.text,
              };
            } else {
              // Add a new message entry for the current round's poet message
              newMessages.push({
                ...incomingMessage,
                id: `${incomingMessage.id}-round-${roundId}`,
                isStreaming: true,
                status: 'pending',
              });
            }
          } else if (incomingMessage.sender === 'Judge') {
            // Directly add judge messages for the round, finalizing them
            newMessages.push({
              ...incomingMessage,
              id: `${incomingMessage.id}-round-${roundId}`,
              isStreaming: false,
              status: 'success',
            });
          }
        });

        return newMessages;
      });
    },
    [updateMessages]
  );

  const sendMessage = useCallback(
    async ({
      text,
      sender,
      poet1,
      poet2,
      topics,
      category,
    }: SendMessageParams) => {
      const messageId = Date.now().toString();
      const responseId = `${messageId}-response`;
      chatService.setActiveResponseId(responseId);

      addMessage(category, {
        id: messageId,
        text,
        sender,
        originalInput: {
          poet1: poet1,
          poet2: poet2,
          topics: topics,
          text: text,
          sender,
          category,
        },
      });

      addMessage(category, {
        id: responseId,
        text: '',
        sender: 'response',
        isStreaming: true,
      });

      try {
        switch (category) {
          case 0:
            await analysisMutation.mutateAsync({ text, responseId });
            break;
          case 1:
            chatService.handleSimulationWebSocket(
              text,
              responseId,
              handleSimulationMessage
            );
            break;
          case 2:
            if (poet1 && poet2 && topics) {
              const { poet1Id, poet2Id, judgeId } =
                chatService.handleBattleWebSocket(
                  poet1,
                  poet2,
                  topics,
                  handleBattleMessage
                );

              [
                { id: poet1Id, sender: 'poet1' },
                { id: poet2Id, sender: 'poet2' },
                { id: judgeId, sender: 'Judge' },
              ].forEach(({ id, sender }) => {
                addMessage(2, {
                  id,
                  text: '',
                  sender: sender as MessageSender,
                  isStreaming: sender !== 'Judge',
                });
              });
            }
            break;
        }
      } catch (error) {
        setState((prev) => ({
          ...prev,
          error: error instanceof Error ? error.message : 'An error occurred',
        }));
      }
    },
    [addMessage, analysisMutation, handleSimulationMessage, handleBattleMessage]
  );

  const regenerate = useCallback(
    async ({ originalInput, messageId, category }: RegenerateParams) => {
      const categoryMessages = state.messages[category] || [];
      const originalMessage = categoryMessages.find(
        (msg) => msg.id === messageId
      );

      if (!originalMessage) return;

      chatService.cleanup();

      const newResponseId = `${Date.now()}-response`;
      chatService.setActiveResponseId(newResponseId);

      addMessage(category, {
        id: newResponseId,
        text: '',
        sender: 'response',
        isStreaming: true,
      });

      try {
        switch (category) {
          case 0:
            await analysisMutation.mutateAsync({
              text: originalInput.text,
              responseId: newResponseId,
            });
            break;
          case 1:
            chatService.handleSimulationWebSocket(
              originalInput.text,
              newResponseId,
              handleSimulationMessage
            );
            break;
          case 2:
            chatService.handleBattleWebSocket(
              originalInput.poet1 as string,
              originalInput.poet2 as string,
              originalInput.topics as string[],
              handleBattleMessage
            );
            break;
        }
      } catch (error) {
        setState((prev) => ({
          ...prev,
          error: error instanceof Error ? error.message : 'An error occurred',
        }));
      }
    },
    [
      state.messages,
      addMessage,
      analysisMutation,
      handleSimulationMessage,
      handleBattleMessage,
    ]
  );

  useEffect(() => {
    return () => {
      chatService.cleanup();
    };
  }, []);

  useEffect(() => {
    if (clearChat) {
      setState((prev) => ({
        ...prev,
        messages: {
          ...prev.messages,
          [selectedCategory]: [],
        },
      }));
      chatService.cleanup();
    }
  }, [clearChat, selectedCategory]);

  return {
    messages: state.messages[selectedCategory] || [],
    error: state.error,
    isLoading: analysisMutation.isPending,
    sendMessage,
    regenerate,
    clearError: () => setState((prev) => ({ ...prev, error: null })),
  };
};
