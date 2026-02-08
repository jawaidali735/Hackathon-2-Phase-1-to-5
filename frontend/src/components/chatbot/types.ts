export interface ChatMessage {
  id: string;
  conversationId: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  toolCalls?: ToolCallInfo[];
  isError?: boolean;
}

export interface ChatState {
  isOpen: boolean;
  messages: ChatMessage[];
  isLoading: boolean;
  conversationId: string | null;
  refreshTrigger: number;
}

export interface ToolCallInfo {
  tool: string;
  params: Record<string, unknown>;
  result: unknown;
}

export interface ChatRequest {
  conversation_id?: string;
  message: string;
}

export interface ChatResponse {
  conversation_id: string;
  response: string;
  tool_calls?: ToolCallInfo[];
}

// Type for messages returned from conversation history API
export interface ConversationHistoryMessage {
  conversation_id: string;
  response: string;  // mapped from content
  role: 'user' | 'assistant';
}
