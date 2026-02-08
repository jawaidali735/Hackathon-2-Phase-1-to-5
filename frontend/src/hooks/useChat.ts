'use client';

import { useState, useCallback, useEffect } from 'react';
import { sendChatMessage, ChatResponse, ToolCall } from '@/lib/chat-api';

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  toolCalls?: ToolCall[];
}

export interface UseChatOptions {
  userId: string;
  token: string;
  onTaskChange?: () => void; // Callback when a task is modified
}

export interface UseChatReturn {
  messages: Message[];
  isLoading: boolean;
  error: string | null;
  conversationId: string | null;
  sendMessage: (message: string) => Promise<void>;
  clearError: () => void;
  clearMessages: () => void;
  loadConversationMessages: () => Promise<void>;
}

function generateId(): string {
  return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}

function formatTimestamp(date: Date): string {
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

export function useChat({ userId, token, onTaskChange }: UseChatOptions): UseChatReturn {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isSendingMessage, setIsSendingMessage] = useState(false);
  
  // Initialize conversationId from localStorage
  const getInitialConversationId = (): string | null => {
    if (typeof window !== 'undefined') {
      return localStorage.getItem(`chat-conversation-${userId}`);
    }
    return null;
  };
  
  const [conversationId, setConversationId] = useState<string | null>(null);

  // Initialize conversationId from localStorage
  useEffect(() => {
    if (userId) {
      const storedConversationId = typeof window !== 'undefined' 
        ? localStorage.getItem(`chat-conversation-${userId}`) 
        : null;
      
      if (storedConversationId) {
        setConversationId(storedConversationId);
      }
    }
  }, [userId]);
  
  // Load existing messages when conversationId, userId, or token changes
  useEffect(() => {
    let isMounted = true; // Track if component is still mounted

    const loadExistingMessages = async () => {
      // Skip loading if we're currently sending a message to prevent flickering
      if (isSendingMessage) {
        return;
      }

      if (isMounted && conversationId && userId && token) {
        try {
          const { fetchConversationMessages } = await import('@/lib/conversation-api');
          const existingMessages = await fetchConversationMessages(userId, conversationId, token);

          // Only update state if component is still mounted
          if (isMounted) {
            // Format the messages to match our Message interface
            const formattedMessages: Message[] = existingMessages.map(msg => ({
              id: msg.id,
              role: msg.role as 'user' | 'assistant',
              content: msg.content,
              timestamp: formatTimestamp(new Date(msg.timestamp)), // Format the timestamp consistently
              toolCalls: msg.toolCalls
            }));

            setMessages(formattedMessages);
          }
        } catch (error) {
          console.error('Failed to load existing conversation messages:', error);
          // If conversation doesn't exist (e.g., invalid ID in localStorage), clear it
          if (isMounted && typeof window !== 'undefined') {
            localStorage.removeItem(`chat-conversation-${userId}`);
          }
          if (isMounted) {
            setConversationId(null);
            setMessages([]);
          }
        }
      } else if (isMounted) {
        // If no conversation exists yet, start with empty messages
        setMessages([]);
      }
    };

    // Load messages when dependencies change
    loadExistingMessages();

    // Cleanup function
    return () => {
      isMounted = false;
    };
  }, [userId, token, conversationId, isSendingMessage]);

  const sendMessage = useCallback(async (content: string) => {
    if (!content.trim() || !userId || !token) return;

    const userMessage: Message = {
      id: generateId(),
      role: 'user',
      content,
      timestamp: formatTimestamp(new Date()),
    };

    // Add user message immediately
    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);
    setIsSendingMessage(true); // Set sending flag to prevent useEffect from reloading
    setError(null);

    try {
      const response: ChatResponse = await sendChatMessage(
        userId,
        content,
        token,
        conversationId || undefined
      );

      // Update conversation ID if we got one back from the server
      if (response.conversation_id) {
        setConversationId(response.conversation_id);
        // Persist the conversation ID to localStorage
        if (typeof window !== 'undefined') {
          localStorage.setItem(`chat-conversation-${userId}`, response.conversation_id);
        }
      } else {
        // If no conversation_id was returned but we have one locally, make sure it's saved
        if (conversationId && typeof window !== 'undefined') {
          localStorage.setItem(`chat-conversation-${userId}`, conversationId);
        }
      }

      // Add assistant response
      const assistantMessage: Message = {
        id: generateId(),
        role: 'assistant',
        content: response.response,
        timestamp: formatTimestamp(new Date()),
        toolCalls: response.tool_calls,
      };

      // Update messages with both user and assistant messages to ensure consistency
      setMessages((prev) => {
        // Find if user message is already in the list (it should be)
        const userMsgExists = prev.some(msg => msg.id === userMessage.id && msg.role === 'user');
        
        if (userMsgExists) {
          // If user message exists, just append the assistant message
          return [...prev, assistantMessage];
        } else {
          // If for some reason user message is missing, add both
          return [...prev, userMessage, assistantMessage];
        }
      });

      // Check if any task-modifying tools were called
      if (response.tool_calls && response.tool_calls.length > 0) {
        const taskModifyingTools = ['add_task', 'complete_task', 'delete_task', 'update_task'];
        const hasTaskChange = response.tool_calls.some(
          (tc) => taskModifyingTools.includes(tc.tool) && tc.result && !('error' in tc.result)
        );
        if (hasTaskChange && onTaskChange) {
          onTaskChange();
        }
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to send message';
      setError(errorMessage);
      
      // Remove the user message if the API call failed
      setMessages(prev => prev.filter(msg => msg.id !== userMessage.id));
    } finally {
      setIsLoading(false);
      setIsSendingMessage(false); // Reset sending flag after completion
    }
  }, [userId, token, conversationId, onTaskChange]);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  const clearMessages = useCallback(() => {
    setMessages([]);
    setConversationId(null);
    setError(null);
    // Clear the persisted conversation ID from localStorage
    if (typeof window !== 'undefined') {
      localStorage.removeItem(`chat-conversation-${userId}`);
    }
  }, [userId]);

  // Function to explicitly load conversation messages
  const loadConversationMessages = useCallback(async () => {
    if (conversationId && userId && token) {
      try {
        const { fetchConversationMessages } = await import('@/lib/conversation-api');
        const existingMessages = await fetchConversationMessages(userId, conversationId, token);

        // Format the messages to match our Message interface
        const formattedMessages: Message[] = existingMessages.map(msg => ({
          id: msg.id,
          role: msg.role as 'user' | 'assistant',
          content: msg.content,
          timestamp: formatTimestamp(new Date(msg.timestamp)), // Format the timestamp consistently
          toolCalls: msg.toolCalls
        }));

        // Replace all messages with the database messages to ensure consistency
        setMessages(formattedMessages);
      } catch (error) {
        console.error('Failed to load conversation messages:', error);
        // Clear invalid conversation ID if it doesn't exist
        if (typeof window !== 'undefined') {
          localStorage.removeItem(`chat-conversation-${userId}`);
        }
        setConversationId(null);
        setMessages([]);
      }
    }
  }, [conversationId, userId, token]);

  return {
    messages,
    isLoading,
    error,
    conversationId,
    sendMessage,
    clearError,
    clearMessages,
    loadConversationMessages, // Export the new function
  };
}
