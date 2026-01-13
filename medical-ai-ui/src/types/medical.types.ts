// WebSocket message types
export interface WebSocketMessage {
  type: 'status' | 'chunk' | 'complete' | 'error';
  data: any;
}

// Query request type
export interface QueryRequest {
  query: string;
  model?: string;
  session_id?: string;
}

// Chat message types
export interface ChatMessage {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  isStreaming?: boolean;
}

// Medical diagnosis types
export interface DiagnosisData {
  diagnosis?: string;
  recomendation?: string;
  description?: string;
  medications?: string;
  first_aid?: string;
  doctor_contact?: string;
  model?: string;
  session_id?: string;
}

// WebSocket connection states
export type ConnectionState = 'connecting' | 'connected' | 'disconnected' | 'error';