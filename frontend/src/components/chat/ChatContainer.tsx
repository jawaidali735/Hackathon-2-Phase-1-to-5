'use client';

import { useState } from 'react';
import { ChatButton } from './ChatButton';
import { ChatPanel } from './ChatPanel';
import { useChat } from '@/hooks/useChat';

interface ChatContainerProps {
  userId: string;
  token: string;
  onTaskChange?: () => void;
}

export function ChatContainer({ userId, token, onTaskChange }: ChatContainerProps) {
  const [isOpen, setIsOpen] = useState(false);

  const {
    messages,
    isLoading,
    error,
    sendMessage,
    loadConversationMessages,
  } = useChat({
    userId,
    token,
    onTaskChange,
  });

  const handleOpen = () => setIsOpen(true);
  const handleClose = () => setIsOpen(false);

  return (
    <>
      <ChatButton onClick={handleOpen} isOpen={isOpen} />
      <ChatPanel
        isOpen={isOpen}
        onClose={handleClose}
        messages={messages}
        isLoading={isLoading}
        error={error}
        onSendMessage={sendMessage}
        onLoadConversationMessages={loadConversationMessages}
      />
    </>
  );
}
