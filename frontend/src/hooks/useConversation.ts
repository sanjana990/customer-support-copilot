import { useState, useEffect } from 'react';
import { QueryResponse } from '@/types/api';

export interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  response?: QueryResponse;
}

export function useConversation(sessionId: string) {
  const [messages, setMessages] = useState<Message[]>([]);

  useEffect(() => {
    // Load messages from localStorage when sessionId changes
    const stored = localStorage.getItem(`atlan-conversation-${sessionId}`);
    if (stored) {
      try {
        const parsedMessages = JSON.parse(stored).map((msg: any) => ({
          ...msg,
          timestamp: new Date(msg.timestamp)
        }));
        setMessages(parsedMessages);
      } catch (error) {
        console.error('Failed to load conversation:', error);
        setMessages([]);
      }
    } else {
      setMessages([]);
    }
  }, [sessionId]);

  const addMessage = (message: Message) => {
    setMessages(prev => {
      const newMessages = [...prev, message];
      // Save to localStorage
      localStorage.setItem(`atlan-conversation-${sessionId}`, JSON.stringify(newMessages));
      return newMessages;
    });
  };

  const clearMessages = () => {
    setMessages([]);
    localStorage.removeItem(`atlan-conversation-${sessionId}`);
  };

  return {
    messages,
    addMessage,
    clearMessages,
  };
}
