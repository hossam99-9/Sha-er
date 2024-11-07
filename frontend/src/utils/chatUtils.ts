// utils/chatUtils.ts
import { Message, WebSocketMessage } from '../types/chat';

export const formatAnalysisResponse = (
  qafya: string,
  meter: string,
  critic: string,
  rhetorical: string
): string => {
  return [qafya, meter, critic, rhetorical].filter(Boolean).join('\n');
};

export const generateMessageId = (prefix = ''): string => {
  return `${prefix}${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
};

export const parseWebSocketMessage = (data: string): WebSocketMessage => {
  try {
    return JSON.parse(data);
  } catch {
    return { bait: data };
  }
};

export const debounce = <T extends (...args: any[]) => any>(
  func: T,
  wait: number
): ((...args: Parameters<T>) => void) => {
  let timeout: NodeJS.Timeout;

  return (...args: Parameters<T>) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
};

export const throttle = <T extends (...args: any[]) => any>(
  func: T,
  limit: number
): ((...args: Parameters<T>) => void) => {
  let inThrottle: boolean;

  return (...args: Parameters<T>) => {
    if (!inThrottle) {
      func(...args);
      inThrottle = true;
      setTimeout(() => (inThrottle = false), limit);
    }
  };
};

export const retryWithBackoff = async <T>(
  fn: () => Promise<T>,
  maxRetries = 3,
  baseDelay = 1000
): Promise<T> => {
  let retries = 0;

  while (true) {
    try {
      return await fn();
    } catch (error) {
      if (retries >= maxRetries) throw error;

      const delay = baseDelay * Math.pow(2, retries);
      await new Promise((resolve) => setTimeout(resolve, delay));
      retries++;
    }
  }
};
