// The types and interfaces define the structure for chat messages, chat state, responses, and parameters.

export type MessageSender = 'user' | 'response' | 'poet1' | 'poet2' | 'Judge';

/**
 * Represents an individual message in a chat.
 */
export interface Message {
  id: string; // Unique identifier for the message
  text: string; // The message text content
  sender: MessageSender; // The sender of the message (user, response, poet1, poet2, or Judge)
  isStreaming?: boolean; // Optional flag indicating if the message is still being streamed
  originalInput?: SendMessageParams; // Original input text, mainly used for messages sent by the user
  timestamp?: number; // Optional timestamp of when the message was created
  status?: string; // Status of the message indicating its sending state
  error?: string; // Optional error message if the message failed to send
  buffer?: string;
  isLastRound?: boolean;
}

/**
 * Represents the overall state of the chat application.
 */
export interface ChatState {
  messages: Record<number, Message[]>; // Record of messages categorized by chat category (0, 1, or 2)
  error: string | null; // Current error message if any error has occurred
  isLoading: boolean; // Indicates if the chat is currently loading a response
}

/**
 * Represents the response structure from the analysis service.
 */
export interface AnalysisResponse {
  qafya: string; // Rhyming scheme analysis result
  meter: string; // Poetic meter analysis result
  critic: string; // Critique analysis or assessment of the text
  rhetorical: string; // Rhetorical analysis or literary elements found in the text
}

/**
 * Represents the structure of a message received via WebSocket.
 */
export interface WebSocketMessage {
  poet1?: string; // Optional text or response from poet1
  poet2?: string; // Optional text or response from poet2
  Judge?: string; // Optional verdict or response from the Judge
  bait?: string; // Optional field for text content or verse being analyzed
}

export type ChatCategory = 0 | 1 | 2; // Chat category: 0 for Analysis, 1 for Simulation, 2 for Battle

/**
 * Parameters required to send a new message in the chat.
 */
export interface SendMessageParams {
  text: string; // The text of the message being sent
  sender: 'user'; // The sender of the message (must be 'user')
  poet1?: string; // Optional name or ID of the first poet for battle category
  poet2?: string; // Optional name or ID of the second poet for battle category
  topics?: string[]; // Optional list of topics for the battle
  category: ChatCategory; // The chat category in which the message is sent (0, 1, or 2)
}

/**
 * Parameters required to regenerate a response message.
 */
export interface RegenerateParams {
  originalInput: SendMessageParams; // The original input text that needs to be regenerated
  messageId: string; // The ID of the message to be regenerated
  category: ChatCategory; // The chat category in which the message is being regenerated (0, 1, or 2)
}
