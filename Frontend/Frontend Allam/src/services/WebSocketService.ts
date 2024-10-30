export const sendCategory1Message = (
  message: { text: string },
  sendMessage: (msg: string) => void
) => {
  sendMessage(JSON.stringify(message));
};

export const sendCategory2Message = (
  message: { prompt: string; poet1: string },
  sendMessage: (msg: string) => void
) => {
  sendMessage(JSON.stringify(message));
};

export const sendCategory3Message = (
  message: { poet1: string; poet2: string; topics: string },
  sendMessage: (msg: string) => void
) => {
  sendMessage(JSON.stringify(message));
};
