import { WebSocketServer } from 'ws';
import { mockResponses } from './mock-data.mjs';

const wss = new WebSocketServer({ port: 8080 });

wss.on('connection', (ws) => {
  console.log('Client connected');

  ws.on('message', (message) => {
    console.log('Raw message received:', message);

    try {
      const parsedMessage = JSON.parse(message);
      console.log('Parsed message:', parsedMessage);

      if (parsedMessage.category === 0) {
        const response = mockResponses.category1.find(
          (req) => req.request.text === parsedMessage.text
        );
        ws.send(
          JSON.stringify(
            response
              ? response.response
              : { analysis: 'No analysis found for this text.' }
          )
        );
      } else if (parsedMessage.category === 1) {
        const response = mockResponses.category2.find(
          (req) =>
            req.request.prompt === parsedMessage.prompt &&
            req.request.poet1 === parsedMessage.poet1
        );
        ws.send(
          JSON.stringify(
            response
              ? response.response
              : { bait: 'No bait found for this prompt and poet.' }
          )
        );
      } else if (parsedMessage.category === 2) {
        const response = mockResponses.category3.find(
          (req) =>
            req.request.poet1 === parsedMessage.poet1 &&
            req.request.poet2 === parsedMessage.poet2 &&
            req.request.topics === parsedMessage.topics
        );
        ws.send(
          JSON.stringify(
            response
              ? response.response
              : {
                  poet1: '',
                  poet2: '',
                  judge: 'No result found for this battle.',
                }
          )
        );
      }
    } catch (error) {
      console.error('Error parsing message:', error);
      ws.send(JSON.stringify({ error: 'Invalid message format' }));
    }
  });

  ws.on('close', () => {
    console.log('Client disconnected');
  });
});

console.log('WebSocket server running on ws://localhost:8080');
