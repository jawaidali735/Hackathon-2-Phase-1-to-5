'use client';

import { ChatContainer } from '@/components/chat';

interface DashboardChatProps {
  userId: string;
  token: string;
}

export function DashboardChat({ userId, token }: DashboardChatProps) {
  // Callback to notify when tasks are modified via chat
  // We don't need to refresh anything here since the server will handle updates
  const handleTaskChange = () => {
    // Optionally dispatch an event if needed for other purposes
    // but don't refresh the page
    window.dispatchEvent(new CustomEvent('tasksChanged'));
  };

  return (
    <ChatContainer
      userId={userId}
      token={token}
      onTaskChange={handleTaskChange}
    />
  );
}
