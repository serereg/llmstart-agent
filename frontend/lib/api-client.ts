import { consumeSseStream } from "@/lib/sse-parser";
import type { ChatRequest, SessionResponse, SseEvent } from "@/lib/types";

export class ApiClientError extends Error {
  constructor(
    message: string,
    readonly status: number,
  ) {
    super(message);
    this.name = "ApiClientError";
  }
}

async function parseErrorMessage(response: Response): Promise<string> {
  try {
    const body = (await response.json()) as { detail?: string | Array<{ msg: string }> };
    if (typeof body.detail === "string") {
      return body.detail;
    }
    if (Array.isArray(body.detail) && body.detail.length > 0) {
      return body.detail.map((item) => item.msg).join(", ");
    }
  } catch {
    // ignore JSON parse errors
  }

  return `Request failed with status ${response.status}`;
}

export async function fetchSession(sessionId: string): Promise<SessionResponse> {
  const response = await fetch(`/api/sessions/${sessionId}`);

  if (!response.ok) {
    throw new ApiClientError(await parseErrorMessage(response), response.status);
  }

  return (await response.json()) as SessionResponse;
}

export async function sendChatMessage(
  request: ChatRequest,
  onEvent: (event: SseEvent) => void,
): Promise<void> {
  const response = await fetch("/api/chat", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    throw new ApiClientError(await parseErrorMessage(response), response.status);
  }

  if (!response.body) {
    throw new ApiClientError("Empty response body", 500);
  }

  await consumeSseStream(response.body, onEvent);
}
