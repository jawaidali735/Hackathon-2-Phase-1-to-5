'use client';

import { useEffect, useRef } from 'react';
import { X, Bot } from 'lucide-react';
import { MessageBubble } from './MessageBubble';
import { ChatInput } from './ChatInput';
import { TypingIndicator } from './TypingIndicator';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

interface ChatPanelProps {
  isOpen: boolean;
  onClose: () => void;
  messages: Message[];
  isLoading: boolean;
  error: string | null;
  onSendMessage: (message: string) => void;
  onLoadConversationMessages?: () => void; // Add function to load conversation messages
}

export function ChatPanel({
  isOpen,
  onClose,
  messages,
  isLoading,
  error,
  onSendMessage,
  onLoadConversationMessages,
}: ChatPanelProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const onLoadConversationMessagesRef = useRef(onLoadConversationMessages);
  const hasLoadedOnOpenRef = useRef(false); // Track if messages have been loaded when panel opened

  // Update the ref when the function changes
  useEffect(() => {
    onLoadConversationMessagesRef.current = onLoadConversationMessages;
  }, [onLoadConversationMessages]);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, isLoading]);

  // Load conversation messages when the panel opens (only once per open session)
  useEffect(() => {
    if (isOpen && onLoadConversationMessagesRef.current && !hasLoadedOnOpenRef.current) {
      onLoadConversationMessagesRef.current();
      hasLoadedOnOpenRef.current = true; // Mark as loaded
    } else if (!isOpen) {
      hasLoadedOnOpenRef.current = false; // Reset when panel closes
    }
  }, [isOpen]); // Only depend on isOpen to prevent dependency array changes

  if (!isOpen) return null;

  return (
    <div className="fixed bottom-0 right-0 z-50 flex h-[600px] w-full flex-col sm:bottom-6 sm:right-6 sm:h-[600px] sm:w-[400px] sm:rounded-2xl overflow-hidden shadow-2xl transition-all duration-300 ease-out animate-slideIn">
      {/* Glassmorphic background */}
      <div className="absolute inset-0 bg-white/90 dark:bg-slate-900/90 backdrop-blur-xl" />

      {/* Content */}
      <div className="relative flex h-full flex-col">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-700 bg-gradient-to-r from-emerald-500 to-emerald-600 px-4 py-3">
          <div className="flex items-center gap-2 text-white">
            <Bot className="h-5 w-5" />
            <span className="font-semibold">AI Assistant</span>
          </div>
          <button
            onClick={onClose}
            className="rounded-full p-1 text-white/80 hover:bg-white/20 hover:text-white transition-colors focus:outline-none focus:ring-2 focus:ring-white/50"
            aria-label="Close chat"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Messages area */}
        <div className="flex-1 overflow-y-auto p-4 space-y-1">
          {messages.length === 0 && !isLoading && (
            <div className="flex flex-col items-center justify-center h-full text-center text-slate-500 dark:text-slate-400">
              <Bot className="h-12 w-12 mb-3 text-emerald-500" />
              <p className="font-medium mb-2">Hi! I'm your AI assistant.</p>
              <p className="text-sm">I can help you manage your tasks.</p>
              <div className="mt-4 text-xs space-y-1">
                <p>Try saying:</p>
                <p className="text-emerald-600 dark:text-emerald-400">"Add a task to buy groceries"</p>
                <p className="text-emerald-600 dark:text-emerald-400">"Show me my tasks"</p>
                <p className="text-emerald-600 dark:text-emerald-400">"Who am I?"</p>
              </div>
            </div>
          )}

          {messages.map((message) => (
            <MessageBubble
              key={message.id}
              role={message.role}
              content={message.content}
              timestamp={message.timestamp}
            />
          ))}

          {isLoading && <TypingIndicator />}

          {error && (
            <div className="mx-4 my-2 rounded-lg bg-red-50 dark:bg-red-900/20 p-3 text-sm text-red-600 dark:text-red-400">
              {error}
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input area */}
        <ChatInput onSend={onSendMessage} disabled={isLoading} />
      </div>
    </div>
  );
}
