import { ChatRequest, ChatResponse, ConversationHistoryMessage } from '@/components/chatbot/types';

// Point to backend server - todo-app backend runs on port 8000
const API_BASE_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

class ChatbotApiClient {
  private baseUrl: string;

  constructor() {
    this.baseUrl = API_BASE_URL;
  }

  async sendMessage(
    userId: string,
    message: string,
    token: string,
    conversationId?: string
  ): Promise<ChatResponse> {
    const url = `${this.baseUrl}/api/v1/${userId}/chat`;

    const requestBody: ChatRequest = {
      message,
      conversation_id: conversationId,
    };

    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(requestBody),
        cache: 'no-store',
      });

      if (!response.ok) {
        if (response.status === 401 || response.status === 403) {
          throw new Error('Your session has expired. Please refresh and log in again.');
        }

        throw new Error('The assistant is having trouble right now. Please try again in a moment.');
      }

      const data = await response.json();
      return data;
    } catch (error) {
      if (error instanceof TypeError && error.message.includes('fetch')) {
        throw new Error('Unable to reach the server. Please check your connection.');
      }
      throw error;
    }
  }

  async getConversationHistory(userId: string, conversationId: string, token: string): Promise<ConversationHistoryMessage[]> {
    const url = `${this.baseUrl}/api/v1/${userId}/conversations/${conversationId}/messages`;
    
    try {
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        cache: 'no-store',
      });

      if (!response.ok) {
        const errorText = await response.text();
        let errorData;
        try {
          errorData = JSON.parse(errorText);
        } catch (e) {
          errorData = { detail: errorText };
        }
        throw new Error(errorData.detail || errorData.message || `Get conversation history failed: ${response.status}`);
      }

      const data = await response.json();
      
      // Transform the messages to match ChatResponse format
      return data.messages.map((msg: any) => ({
        conversation_id: conversationId,
        response: msg.content,
        role: msg.role,
      }));
    } catch (error) {
      throw error;
    }
  }

  async getRecentConversation(userId: string, token: string): Promise<any> {
    const url = `${this.baseUrl}/api/v1/${userId}/conversations/recent`;
    
    try {
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        cache: 'no-store',
      });

      if (response.status === 204) {
        // No recent conversation exists
        return null;
      }
      
      if (!response.ok) {
        const errorText = await response.text();
        let errorData;
        try {
          errorData = JSON.parse(errorText);
        } catch (e) {
          errorData = { detail: errorText };
        }
        throw new Error(errorData.detail || errorData.message || `Get recent conversation failed: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      throw error;
    }
  }

  async getConversations(userId: string, token: string, limit: number = 10): Promise<any[]> {
    const url = `${this.baseUrl}/api/v1/${userId}/conversations?limit=${limit}`;
    
    try {
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        cache: 'no-store',
      });

      if (!response.ok) {
        const errorText = await response.text();
        let errorData;
        try {
          errorData = JSON.parse(errorText);
        } catch (e) {
          errorData = { detail: errorText };
        }
        throw new Error(errorData.detail || errorData.message || `Get conversations failed: ${response.status}`);
      }

      const data = await response.json();
      return data.conversations || [];
    } catch (error) {
      throw error;
    }
  }
}

// Create a singleton instance
export const chatbotApiClient = new ChatbotApiClient();

// Export individual methods for convenience
export const sendChatMessage = chatbotApiClient.sendMessage.bind(chatbotApiClient);
