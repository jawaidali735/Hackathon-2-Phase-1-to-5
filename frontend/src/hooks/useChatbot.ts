import { useState, useCallback, useRef } from 'react';
import { ChatMessage, ChatState, ChatResponse } from '@/components/chatbot/types';
import { sendChatMessage, chatbotApiClient } from '@/lib/chatbot-api';

export const useChatbot = () => {
  const [chatState, setChatState] = useState<ChatState>(() => {
    // Initialize from localStorage to preserve conversation across page refreshes
    const savedConversationId = typeof window !== 'undefined'
      ? localStorage.getItem('current_conversation_id')
      : null;

    return {
      isOpen: false,
      messages: [],
      isLoading: false,
      conversationId: savedConversationId,
      refreshTrigger: 0,
    };
  });

  // Track if we've already loaded history for the current conversation
  const historyLoadedRef = useRef<string | null>(null);

  const loadConversationHistory = useCallback(async (conversationId: string, forceReload: boolean = false) => {
    // Skip if we've already loaded this conversation (unless force reload)
    if (!forceReload && historyLoadedRef.current === conversationId) {
      return;
    }

    const token = localStorage.getItem('chatbot_token');
    const userId = localStorage.getItem('chatbot_user_id');

    if (!token || !userId) {
      throw new Error('User not authenticated');
    }

    try {
      // Show loading state
      setChatState(prev => ({
        ...prev,
        isLoading: true,
        conversationId: conversationId,
      }));

      try {
        // Try to fetch conversation history from backend first
        const history = await chatbotApiClient.getConversationHistory(userId, conversationId, token);

        // Convert the history to the format expected by the chat interface
        // The API returns { response, role, conversation_id, toolCalls } for each message
        const chatMessages: ChatMessage[] = history.map((msg, index) => ({
          id: `hist-${index}-${Date.now()}`,
          conversationId: msg.conversation_id,
          role: (msg.role as 'user' | 'assistant') || 'assistant',
          content: msg.response, // getConversationHistory maps content -> response
          timestamp: new Date(),
          toolCalls: (msg as any).toolCalls, // Include tool calls if present
        }));

        // Mark this conversation as loaded
        historyLoadedRef.current = conversationId;

        // Update the chat state with the loaded messages
        setChatState(prev => ({
          ...prev,
          messages: chatMessages,
          isLoading: false,
          conversationId: conversationId,
        }));
      } catch (backendError) {

        // Mark as loaded even on error to prevent infinite retries
        historyLoadedRef.current = conversationId;

        // Clear loading state
        setChatState(prev => ({
          ...prev,
          messages: [],
          isLoading: false,
          conversationId: conversationId,
        }));
      }
    } catch (error) {
      setChatState(prev => ({
        ...prev,
        isLoading: false,
      }));
      throw error;
    }
  }, []);

  const openChat = useCallback(async () => {
    // Always open the chat
    setChatState(prev => ({ ...prev, isOpen: true }));

    const token = localStorage.getItem('chatbot_token');
    const userId = localStorage.getItem('chatbot_user_id');

    if (!token || !userId) {
      return;
    }

    // If we already have messages loaded, don't reload
    if (chatState.messages.length > 0) {
      return;
    }

    // If we have a saved conversation ID, load its history
    if (chatState.conversationId) {
      try {
        await loadConversationHistory(chatState.conversationId, true); // Force reload
        return;
      } catch (error) {
        // Clear the invalid conversation ID
        localStorage.removeItem('current_conversation_id');
        setChatState(prev => ({ ...prev, conversationId: null }));
      }
    }

    // If no saved conversation or it failed, try to load the most recent one
    try {
      // Try to get the user's most recent conversation
      const recentConversation = await chatbotApiClient.getRecentConversation(userId, token);

      if (recentConversation) {
        // Save to localStorage for persistence
        localStorage.setItem('current_conversation_id', recentConversation.id);
        // Load the most recent conversation
        await loadConversationHistory(recentConversation.id, true);
      }
    } catch (error) {
      // This is OK - we can continue with a new conversation
    }
  }, [chatState.conversationId, chatState.messages.length, loadConversationHistory]);

  const closeChat = useCallback(() => {
    setChatState(prev => ({ ...prev, isOpen: false }));
  }, []);

  const toggleChat = useCallback(async () => {
    if (!chatState.isOpen) {
      // When opening, use openChat to load conversation history
      await openChat();
    } else {
      // When closing, just close
      closeChat();
    }
  }, [chatState.isOpen, openChat, closeChat]);

  const sendMessage = useCallback(async (message: string) => {
    if (!message.trim()) return;

    // Get token and userId from localStorage (stored by ChatWrapper)
    const token = localStorage.getItem('chatbot_token');
    const userId = localStorage.getItem('chatbot_user_id');

    if (!token || !userId) {
      throw new Error('User not authenticated. Please log in.');
    }

    // Add user message to chat
    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      conversationId: chatState.conversationId || 'new',
      role: 'user',
      content: message,
      timestamp: new Date(),
    };

    setChatState(prev => ({
      ...prev,
      messages: [...prev.messages, userMessage],
      isLoading: true,
    }));

    try {
      // Send message to backend
      const response: ChatResponse = await sendChatMessage(
        userId,
        message,
        token,
        chatState.conversationId || undefined
      );

      // Update conversation ID if it's new and save to localStorage
      if (!chatState.conversationId || chatState.conversationId !== response.conversation_id) {
        localStorage.setItem('current_conversation_id', response.conversation_id);
        setChatState(prev => ({ ...prev, conversationId: response.conversation_id }));
        // Update the history loaded ref to the new conversation ID
        historyLoadedRef.current = response.conversation_id;
      }

      // Add assistant response to chat
      const assistantMessage: ChatMessage = {
        id: `assistant-${Date.now()}`,
        conversationId: response.conversation_id,
        role: 'assistant',
        content: response.response,
        timestamp: new Date(),
        toolCalls: response.tool_calls,
      };

      setChatState(prev => ({
        ...prev,
        messages: [...prev.messages, assistantMessage],
        isLoading: false,
        conversationId: response.conversation_id,
        refreshTrigger: prev.refreshTrigger + 1,
      }));

      // Dispatch event to refresh tasks if tool was executed
      if (response.tool_calls && response.tool_calls.length > 0) {
        window.dispatchEvent(new CustomEvent('tasksChanged'));
      }
    } catch (error) {
      // Determine user-friendly error message
      let friendlyMessage = 'Something went wrong. Please try again in a moment.';
      if (error instanceof Error) {
        const msg = error.message.toLowerCase();
        if (msg.includes('connect') || msg.includes('network') || msg.includes('fetch')) {
          friendlyMessage = 'Unable to reach the server. Please check your connection and try again.';
        } else if (msg.includes('not authenticated') || msg.includes('log in')) {
          friendlyMessage = 'Your session has expired. Please refresh the page and log in again.';
        } else if (msg.includes('having trouble') || msg.includes('try again')) {
          friendlyMessage = error.message;
        } else {
          friendlyMessage = 'Something went wrong. Please try again in a moment.';
        }
      }

      const errorMessage: ChatMessage = {
        id: `error-${Date.now()}`,
        conversationId: chatState.conversationId || 'new',
        role: 'assistant',
        content: friendlyMessage,
        timestamp: new Date(),
        isError: true,
      };

      setChatState(prev => ({
        ...prev,
        messages: [...prev.messages, errorMessage],
        isLoading: false,
      }));
    }
  }, [chatState.conversationId]);

  const clearChat = useCallback(() => {
    // Clear localStorage when clearing chat
    localStorage.removeItem('current_conversation_id');
    historyLoadedRef.current = null;
    setChatState(prev => ({
      ...prev,
      messages: [],
      conversationId: null,
    }));
  }, []);

  return {
    chatState,
    openChat,
    closeChat,
    toggleChat,
    sendMessage,
    clearChat,
    loadConversationHistory,
  };
};
