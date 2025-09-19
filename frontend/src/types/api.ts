// API Types for Atlan Customer Support Copilot

export interface QueryRequest {
  query: string;
  channel?: string;
  session_id?: string;
  include_followup?: boolean;
}

export interface Citation {
  doc: string;
  url: string;
}

export interface Classification {
  topic: string;
  sentiment: string;
  priority: string;
  confidence: number;
}

export interface ClassificationReasons {
  topic: string;
  sentiment: string;
  priority: string;
}

export interface FollowupSuggestion {
  question: string;
}

export interface QueryResponse {
  answer: string;
  citations: Citation[];
  classification: Classification;
  classification_reasons: ClassificationReasons;
  processing_time: number;
  cache_hit: boolean;
  followup_suggestions: FollowupSuggestion[];
  session_id: string;
  response_type: "rag_response" | "routing_message";
}

export interface ConversationMessage {
  role: string;
  content: string;
  timestamp: string;
}

export interface ConversationResponse {
  conversation: {
    session_id: string;
    messages: ConversationMessage[];
    created_at: string;
    updated_at: string;
  };
  total_messages: number;
  last_activity: string;
}

export interface HealthResponse {
  status: string;
  message: string;
}

export interface ApiError {
  detail: string;
}

export type TopicType = "How-to" | "Product" | "Connector" | "Lineage" | "API/SDK" | "SSO" | "Glossary" | "Best practices" | "Sensitive data" | "General";
export type SentimentType = "Urgent" | "Frustrated" | "Positive" | "Curious" | "Neutral";
export type PriorityType = "P0" | "P1" | "P2";

export interface TicketData extends QueryResponse {
  id: string;
  timestamp: string;
  query: string;
}
