import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface ChatState {
  [category: number]: {
    wsConnection: WebSocket | null;
    messages: string[];
  };
}

const initialState: ChatState = {
  0: { wsConnection: null, messages: [] },
  1: { wsConnection: null, messages: [] },
  2: { wsConnection: null, messages: [] },
};

const chatSlice = createSlice({
  name: 'chat',
  initialState,
  reducers: {
    connectWebSocket: (
      state,
      action: PayloadAction<{ category: number; url: string }>
    ) => {
      const { category, url } = action.payload;

      // Close existing connection if it exists
      state[category].wsConnection?.close();

      // Create a new WebSocket connection
      state[category].wsConnection = new WebSocket(url);
    },

    setMessage: (
      state,
      action: PayloadAction<{ category: number; message: string }>
    ) => {
      const { category, message } = action.payload;
      state[category].messages.push(message);
    },

    closeConnection: (state, action: PayloadAction<number>) => {
      const category = action.payload;

      // Close and nullify the WebSocket connection if it exists
      state[category].wsConnection?.close();
      state[category].wsConnection = null;
    },
  },
});

export const { connectWebSocket, setMessage, closeConnection } =
  chatSlice.actions;
export default chatSlice.reducer;
