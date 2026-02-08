"use client";

import React, { useEffect, useState } from 'react';
import { ChatProvider } from './ChatProvider';
import ChatButton from './ChatButton';
import ChatPanel from './ChatPanel';

interface ChatWrapperProps {
  userId?: string;
  token?: string;
}

/**
 * ChatWrapper component that conditionally renders the chatbot
 * only when user is authenticated (has token).
 */
const ChatWrapper: React.FC<ChatWrapperProps> = ({ userId, token }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    // Store token in localStorage for chatbot API to use
    if (token && userId) {
      localStorage.setItem('chatbot_token', token);
      localStorage.setItem('chatbot_user_id', userId);
      setIsAuthenticated(true);
    } else {
      // Check if we have stored credentials
      const storedToken = localStorage.getItem('chatbot_token');
      const storedUserId = localStorage.getItem('chatbot_user_id');
      if (storedToken && storedUserId) {
        setIsAuthenticated(true);
      }
    }
  }, [token, userId]);

  // Only render chatbot if authenticated
  if (!isAuthenticated) {
    return null;
  }

  return (
    <ChatProvider>
      <ChatButton />
      <ChatPanel />
    </ChatProvider>
  );
};

export default ChatWrapper;
