'use client';

import { useState, useEffect, useCallback } from 'react';

export interface ChatSession {
  id: string;
  title: string;
  preview: string;
  createdAt: string;
  updatedAt: string;
  messages: ChatMessage[];
  schema?: any;
  jobId?: string;
  datasetId?: string;
  status: 'active' | 'completed' | 'error';
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
  metadata?: {
    schema?: any;
    settings?: {
      name?: string;
      rowCount?: number;
      outputFormat?: string;
    };
    status?: 'thinking' | 'ready' | 'generating' | 'complete' | 'error';
    jobId?: string;
    datasetId?: string;
  };
}

const STORAGE_KEY = 'synthesize_chat_history';
const MAX_SESSIONS = 50;

function getStoredSessions(): ChatSession[] {
  if (typeof window === 'undefined') return [];
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    return stored ? JSON.parse(stored) : [];
  } catch {
    return [];
  }
}

function storeSessions(sessions: ChatSession[]) {
  if (typeof window === 'undefined') return;
  try {
    // Keep only the most recent sessions
    const trimmed = sessions.slice(0, MAX_SESSIONS);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(trimmed));
  } catch (error) {
    console.error('Failed to store chat sessions:', error);
  }
}

export function useChatHistory() {
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
  const [isLoaded, setIsLoaded] = useState(false);

  // Load sessions from localStorage on mount
  useEffect(() => {
    const stored = getStoredSessions();
    setSessions(stored);
    setIsLoaded(true);
  }, []);

  // Save sessions to localStorage whenever they change
  useEffect(() => {
    if (isLoaded) {
      storeSessions(sessions);
    }
  }, [sessions, isLoaded]);

  // Create a new session
  const createSession = useCallback((firstMessage?: string): ChatSession => {
    const session: ChatSession = {
      id: `session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      title: firstMessage?.slice(0, 50) || 'New Chat',
      preview: firstMessage?.slice(0, 100) || '',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      messages: [],
      status: 'active',
    };
    
    setSessions(prev => [session, ...prev]);
    setCurrentSessionId(session.id);
    return session;
  }, []);

  // Get current session
  const getCurrentSession = useCallback((): ChatSession | null => {
    if (!currentSessionId) return null;
    return sessions.find(s => s.id === currentSessionId) || null;
  }, [currentSessionId, sessions]);

  // Add message to current session
  const addMessage = useCallback((message: Omit<ChatMessage, 'id' | 'timestamp'>) => {
    const newMessage: ChatMessage = {
      ...message,
      id: `msg-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      timestamp: new Date().toISOString(),
    };

    setSessions(prev => prev.map(session => {
      if (session.id === currentSessionId) {
        // Update title from first user message
        const title = session.messages.length === 0 && message.role === 'user'
          ? message.content.slice(0, 50)
          : session.title;
        
        return {
          ...session,
          title,
          preview: message.content.slice(0, 100),
          updatedAt: new Date().toISOString(),
          messages: [...session.messages, newMessage],
        };
      }
      return session;
    }));

    return newMessage;
  }, [currentSessionId]);

  // Update message in current session
  const updateMessage = useCallback((messageId: string, updates: Partial<ChatMessage>) => {
    setSessions(prev => prev.map(session => {
      if (session.id === currentSessionId) {
        return {
          ...session,
          updatedAt: new Date().toISOString(),
          messages: session.messages.map(msg => 
            msg.id === messageId ? { ...msg, ...updates } : msg
          ),
        };
      }
      return session;
    }));
  }, [currentSessionId]);

  // Remove message from current session
  const removeMessage = useCallback((messageId: string) => {
    setSessions(prev => prev.map(session => {
      if (session.id === currentSessionId) {
        return {
          ...session,
          updatedAt: new Date().toISOString(),
          messages: session.messages.filter(msg => msg.id !== messageId),
        };
      }
      return session;
    }));
  }, [currentSessionId]);

  // Update session metadata
  const updateSession = useCallback((updates: Partial<ChatSession>) => {
    setSessions(prev => prev.map(session => {
      if (session.id === currentSessionId) {
        return {
          ...session,
          ...updates,
          updatedAt: new Date().toISOString(),
        };
      }
      return session;
    }));
  }, [currentSessionId]);

  // Load a specific session
  const loadSession = useCallback((sessionId: string) => {
    setCurrentSessionId(sessionId);
  }, []);

  // Delete a session
  const deleteSession = useCallback((sessionId: string) => {
    setSessions(prev => prev.filter(s => s.id !== sessionId));
    if (currentSessionId === sessionId) {
      setCurrentSessionId(null);
    }
  }, [currentSessionId]);

  // Clear all sessions
  const clearAllSessions = useCallback(() => {
    setSessions([]);
    setCurrentSessionId(null);
    localStorage.removeItem(STORAGE_KEY);
  }, []);

  // Start new chat (clear current session)
  const startNewChat = useCallback(() => {
    setCurrentSessionId(null);
  }, []);

  return {
    sessions,
    currentSessionId,
    currentSession: getCurrentSession(),
    isLoaded,
    createSession,
    addMessage,
    updateMessage,
    removeMessage,
    updateSession,
    loadSession,
    deleteSession,
    clearAllSessions,
    startNewChat,
    setCurrentSessionId,
  };
}
