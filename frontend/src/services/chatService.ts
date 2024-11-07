/* eslint-disable @typescript-eslint/no-explicit-any */
import axios from 'axios';
import { AnalysisResponse, Message } from '../types/chat';
import {
  ANALYSIS_URL,
  BATTLE_WS_URL,
  SIMULATION_WS_URL,
} from '../constants/url';

export class ChatService {
  private webSocket: WebSocket | null = null;
  private activeResponseId: string | null = null;

  /**
   * Sends a POST request to analyze a given text.
   *
   * @param text - The text to analyze.
   * @param responseId - A unique identifier for the response message.
   *
   * @returns An object containing the analysis response data and the response ID.
   */
  async analyzeText(
    text: string,
    responseId: string
  ): Promise<{ data: AnalysisResponse; responseId: string }> {
    const response = await axios.post<AnalysisResponse>(`${ANALYSIS_URL}`, {
      bait: text,
    });
    return { data: response.data, responseId };
  }

  /**
   * Connects to a WebSocket server and listens for incoming messages.
   *
   * @param url - The WebSocket URL to connect to.
   * @param onMessage - Callback function to handle incoming messages.
   *
   * @returns The connected WebSocket instance.
   */
  connectWebSocket(
    url: string,
    onMessage: (event: MessageEvent) => void
  ): WebSocket {
    if (this.webSocket) {
      this.webSocket.close();
    }

    const ws = new WebSocket(url);
    this.webSocket = ws;
    ws.onmessage = onMessage;

    return ws;
  }

  /**
   * Initiates a WebSocket connection to handle simulation messages.
   *
   * @param text - The prompt text for the simulation.
   * @param responseId - The response ID to identify the message being updated.
   * @param onMessageUpdate - Callback function to update the message content.
   */
  handleSimulationWebSocket(
    text: string,
    responseId: string,
    onMessageUpdate: (
      responseId: string,
      text: string,
      isStreaming: boolean
    ) => void
  ): void {
    const ws = this.connectWebSocket(
      `${SIMULATION_WS_URL}?prompt=${text}`,
      (event) => {
        try {
          const data = JSON.parse(event.data);
          onMessageUpdate(responseId, data.bait || '', true);
        } catch (e) {
          onMessageUpdate(responseId, event.data, true);
        }
      }
    );

    ws.onopen = () => {
      ws.send(JSON.stringify({ verse: text }));
    };
  }

  /**
   * Initiates a WebSocket connection for a battle between two poets.
   *
   * @param poet1 - The first poet's name or ID.
   * @param poet2 - The second poet's name or ID.
   * @param topics - The list of topics for the battle.
   * @param updateMessages - Callback function to update messages for each participant.
   *
   * @returns An object with unique IDs for each participant in the battle (poet1, poet2, and Judge).
   */

  handleBattleWebSocket = (
    poet1: string,
    poet2: string,
    topics: string[],
    updateMessages: (
      updatedMessages: Message[],
      shouldAddNewMessages: boolean
    ) => void
  ) => {
    const createRoundMessageIds = (round: number) => {
      const timestamp = Date.now().toString();
      return {
        poet1Id: `${timestamp}-poet1-round-${round}`,
        poet2Id: `${timestamp}-poet2-round-${round}`,
        judgeId: `${timestamp}-judge-round-${round}`,
      };
    };

    let currentRound = 1; // Track the current round number
    let currentMessageIds = createRoundMessageIds(currentRound); // Generate initial message IDs for round 1
    let lastMessageWasJudge = false;

    const ws = this.connectWebSocket(
      `${BATTLE_WS_URL}?poet1=${poet1}&poet2=${poet2}&topics=${topics}`,
      (event) => {
        const data = JSON.parse(event.data);
        const updatedMessages: Message[] = [];
        let shouldAddNewMessages = false;

        if (lastMessageWasJudge) {
          // Start a new round by creating fresh message IDs
          currentRound++;
          currentMessageIds = createRoundMessageIds(currentRound);
          shouldAddNewMessages = true;
          lastMessageWasJudge = false;
        }

        // Add new messages for `poet1`, `poet2`, and `judge` as per the current round
        if (data.poet1) {
          updatedMessages.push({
            id: currentMessageIds.poet1Id,
            text: data.poet1,
            sender: 'poet1',
            isStreaming: true,
          });
        }
        if (data.poet2) {
          updatedMessages.push({
            id: currentMessageIds.poet2Id,
            text: data.poet2,
            sender: 'poet2',
            isStreaming: true,
          });
        }
        if (data.Judge) {
          updatedMessages.push({
            id: currentMessageIds.judgeId,
            text: data.Judge,
            sender: 'Judge',
            isStreaming: false,
          });
          lastMessageWasJudge = true; // Mark that the round ended with a judge's message
        }

        // Send the accumulated messages to update the UI
        updateMessages(updatedMessages, shouldAddNewMessages);
      }
    );

    ws.onopen = () => {
      ws.send(JSON.stringify({ verse: poet1, verse2: poet2, topics }));
    };

    return currentMessageIds;
  };

  /**
   * Cleans up the current WebSocket connection by closing it.
   */
  cleanup(): void {
    if (this.webSocket) {
      this.webSocket.close();
    }
  }

  /**
   * Sets the currently active response ID for tracking purposes.
   *
   * @param id - The ID of the active response.
   */
  setActiveResponseId(id: string): void {
    this.activeResponseId = id;
  }

  /**
   * Retrieves the currently active response ID.
   *
   * @returns The active response ID or null if no ID is set.
   */
  getActiveResponseId(): string | null {
    return this.activeResponseId;
  }
}

export const chatService = new ChatService();
