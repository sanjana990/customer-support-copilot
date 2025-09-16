import { useState, useEffect } from 'react';
import { v4 as uuidv4 } from 'uuid';

export function useSession() {
  const [sessionId, setSessionId] = useState<string>('');

  useEffect(() => {
    // Try to get existing session from localStorage
    const stored = localStorage.getItem('atlan-session-id');
    if (stored) {
      setSessionId(stored);
    } else {
      // Generate new session ID
      const newId = uuidv4();
      setSessionId(newId);
      localStorage.setItem('atlan-session-id', newId);
    }
  }, []);

  const createNewSession = () => {
    const newId = uuidv4();
    setSessionId(newId);
    localStorage.setItem('atlan-session-id', newId);
    return newId;
  };

  const clearSession = () => {
    localStorage.removeItem('atlan-session-id');
    createNewSession();
  };

  return {
    sessionId,
    createNewSession,
    clearSession,
  };
}