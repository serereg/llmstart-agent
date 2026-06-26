import type { SseEvent } from "@/lib/types";

export interface ParsedSseMessage {
  event: string;
  data: string;
}

export function parseSseChunk(buffer: string): {
  messages: ParsedSseMessage[];
  remainder: string;
} {
  const normalized = buffer.replace(/\r\n/g, "\n");
  const parts = normalized.split("\n\n");
  const remainder = parts.pop() ?? "";
  const messages: ParsedSseMessage[] = [];

  for (const part of parts) {
    if (!part.trim()) {
      continue;
    }

    let event = "message";
    const dataLines: string[] = [];

    for (const line of part.split("\n")) {
      if (line.startsWith("event:")) {
        event = line.slice(6).trim();
      } else if (line.startsWith("data:")) {
        dataLines.push(line.slice(5).trimStart());
      }
    }

    if (dataLines.length > 0) {
      messages.push({ event, data: dataLines.join("\n") });
    }
  }

  return { messages, remainder };
}

export function parseSseEvent(event: string, data: string): SseEvent | null {
  try {
    const payload = JSON.parse(data) as Record<string, unknown>;

    switch (event) {
      case "reasoning":
        return {
          type: "reasoning",
          step: Number(payload.step),
          content: String(payload.content ?? ""),
        };
      case "tool_start":
        return {
          type: "tool_start",
          name: String(payload.name ?? ""),
          args: (payload.args as Record<string, unknown>) ?? {},
        };
      case "tool_end":
        return {
          type: "tool_end",
          name: String(payload.name ?? ""),
          result: String(payload.result ?? ""),
        };
      case "token":
        return {
          type: "token",
          content: String(payload.content ?? ""),
        };
      case "error":
        return {
          type: "error",
          message: String(payload.message ?? "Сервис временно недоступен"),
        };
      case "done":
        return {
          type: "done",
          session_id: String(payload.session_id ?? ""),
          reply: String(payload.reply ?? ""),
          error: Boolean(payload.error),
        };
      default:
        return null;
    }
  } catch {
    return null;
  }
}

export async function consumeSseStream(
  stream: ReadableStream<Uint8Array>,
  onEvent: (event: SseEvent) => void,
): Promise<void> {
  const reader = stream.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) {
      break;
    }

    buffer += decoder.decode(value, { stream: true });
    const { messages, remainder } = parseSseChunk(buffer);
    buffer = remainder;

    for (const message of messages) {
      const parsed = parseSseEvent(message.event, message.data);
      if (parsed) {
        onEvent(parsed);
      }
    }
  }

  if (buffer.trim()) {
    const { messages } = parseSseChunk(`${buffer}\n\n`);
    for (const message of messages) {
      const parsed = parseSseEvent(message.event, message.data);
      if (parsed) {
        onEvent(parsed);
      }
    }
  }
}
