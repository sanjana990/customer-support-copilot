import { QueryRequest, QueryResponse, ConversationResponse, HealthResponse, ApiError } from "@/types/api";

const BASE_URL = import.meta.env.VITE_BACKEND_URL || "http://localhost:8000";

class ApiService {
  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${BASE_URL}${endpoint}`;
    
    const response = await fetch(url, {
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      const error: ApiError = await response.json().catch(() => ({ 
        detail: `HTTP ${response.status}: ${response.statusText}` 
      }));
      throw new Error(error.detail);
    }

    return response.json();
  }

  async submitQuery(data: QueryRequest): Promise<QueryResponse> {
    return this.request<QueryResponse>("/api/query", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async submitFollowupQuery(data: QueryRequest): Promise<QueryResponse> {
    return this.request<QueryResponse>("/api/query/conversation", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async getConversation(sessionId: string): Promise<ConversationResponse> {
    return this.request<ConversationResponse>(`/api/conversation/${sessionId}`);
  }

  async clearConversation(sessionId: string): Promise<{ message: string }> {
    return this.request<{ message: string }>(`/api/conversation/${sessionId}`, {
      method: "DELETE",
    });
  }

  async healthCheck(): Promise<HealthResponse> {
    return this.request<HealthResponse>("/health");
  }

  async getRootMessage(): Promise<{ message: string }> {
    return this.request<{ message: string }>("/");
  }
}

export const apiService = new ApiService();