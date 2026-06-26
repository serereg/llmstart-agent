export const MAX_MESSAGE_LENGTH = 4000;

export interface ChatRequest {
  session_id: string | null;
  message: string;
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  timestamp?: string;
}

export interface SessionResponse {
  session_id: string;
  channel: string;
  segment: string | null;
  messages: ChatMessage[];
  payment: {
    status: string;
    mock_link: string | null;
  };
  created_at: string;
  updated_at: string;
}

export interface ReasoningEvent {
  type: "reasoning";
  step: number;
  content: string;
}

export interface ToolStartEvent {
  type: "tool_start";
  name: string;
  args: Record<string, unknown>;
}

export interface ToolEndEvent {
  type: "tool_end";
  name: string;
  result: string;
}

export interface TokenEvent {
  type: "token";
  content: string;
}

export interface ErrorEvent {
  type: "error";
  message: string;
}

export interface DoneEvent {
  type: "done";
  session_id: string;
  reply: string;
  error: boolean;
}

export type SseEvent =
  | ReasoningEvent
  | ToolStartEvent
  | ToolEndEvent
  | TokenEvent
  | ErrorEvent
  | DoneEvent;

export type ActivityItem =
  | { kind: "reasoning"; step: number; content: string }
  | { kind: "tool"; name: string; args?: Record<string, unknown>; result?: string; status: "running" | "done" };
