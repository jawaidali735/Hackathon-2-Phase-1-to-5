/**
 * Chat API client for communicating with the backend chat endpoint.
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

export interface ChatRequest {
  conversation_id?: string;
  message: string;
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
 * Send a message to the chat API.
 *
 * @param userId - The authenticated user's ID
 * @param message - The message to send
 * @param conversationId - Optional conversation ID to continue
 * @param token - JWT token for authentication
 * @returns Chat response from the API
 */
export async function sendChatMessage(
  userId: string,
  message: string,
  token: string,
  conversationId?: string
): Promise<ChatResponse> {
  const url = `${API_BASE_URL}/api/v1/${userId}/chat`;

  const body: ChatRequest = {
    message,
  };

  if (conversationId) {
    body.conversation_id = conversationId;
  }

  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    const error: ChatError = await response.json().catch(() => ({ detail: 'An error occurred' }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  return response.json();
}
