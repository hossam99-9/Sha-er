import { useState, useEffect, useRef } from 'react';

const useWebSocket = () => {
  const [isConnected, setIsConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const socketRef = useRef<WebSocket | null>(null);
  const [streamData, setStreamData] = useState<string>('');
  const [error, setError] = useState<string | null>(null);

  const connect = async (baseUrl: string, prompt: string) => {
    if (socketRef.current) {
      socketRef.current.close();
    }

    try {
      setIsConnecting(true);
      setError(null);
      setStreamData(''); // Reset stream data on new connection

      const url = `${baseUrl}?prompt=${encodeURIComponent(prompt)}`;
      const webSocket = new WebSocket(url);
      socketRef.current = webSocket;

      webSocket.onopen = () => {
        setIsConnected(true);
        setIsConnecting(false);
        console.log('WebSocket connection established');
      };

      webSocket.onmessage = (event) => {
        try {
          // Parse the JSON message
          const jsonData = JSON.parse(event.data);

          // Extract the Arabic text from the 'bait' field
          if (jsonData.bait) {
            setStreamData((prev) => prev + jsonData.bait);
          }
        } catch (e) {
          console.error('Error processing WebSocket message:', e);
        }
      };

      webSocket.onclose = () => {
        setIsConnected(false);
        setIsConnecting(false);
        console.log('WebSocket connection closed');
      };

      webSocket.onerror = (error) => {
        setError('WebSocket connection error');
        setIsConnecting(false);
        console.error('WebSocket error:', error);
      };
    } catch (e) {
      setError('Failed to establish WebSocket connection');
      setIsConnecting(false);
      console.error('Connection error:', e);
    }
  };

  const closeConnection = () => {
    if (socketRef.current) {
      socketRef.current.close();
      socketRef.current = null;
    }
  };

  useEffect(() => {
    return () => {
      closeConnection();
    };
  }, []);

  return {
    connect,
    closeConnection,
    streamData,
    isConnected,
    isConnecting,
    error,
  };
};

export default useWebSocket;
