/**
 * API functions for chat operations
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  toolCalls?: ToolCall[];
}

export interface ToolCall {
  tool: string;
  params: Record<string, unknown>;
  result: Record<string, unknown>;
}

export interface ChatResponse {
  conversation_id: string;
  response: string;
  tool_calls?: ToolCall[];
}

export interface ChatError {
  detail: string;
}

/**
 * Fetch messages for a specific conversation
 */
export async function fetchConversationMessages(
  userId: string,
  conversationId: string,
  token: string
): Promise<Message[]> {
  const url = `${API_BASE_URL}/api/v1/${userId}/conversations/${conversationId}/messages`;
  
  const response = await fetch(url, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    // Handle different error statuses appropriately
    if (response.status === 404) {
      // Conversation not found - throw to signal localStorage should be cleared
      throw new Error('Conversation not found');
    } else if (response.status === 403) {
      // Access denied - throw to signal localStorage should be cleared
      throw new Error('Access denied to conversation');
    }

    // For other errors, try to get error details
    try {
      const error: ChatError = await response.json();
      throw new Error(error.detail || `API Error: HTTP ${response.status}`);
    } catch (parseError) {
      if (parseError instanceof Error && parseError.message !== 'Conversation not found' && parseError.message !== 'Access denied to conversation') {
        throw new Error(`API Error: HTTP ${response.status}`);
      }
      throw parseError;
    }
  }

  try {
    const data = await response.json();
    return data.messages || [];
  } catch (error) {
    console.warn('Failed to parse response:', error);
    return [];
  }
}