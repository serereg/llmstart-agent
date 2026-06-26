import { describe, expect, it } from "vitest";

import {
  consumeSseStream,
  parseSseChunk,
  parseSseEvent,
} from "@/lib/sse-parser";

describe("parseSseChunk", () => {
  it("parses complete SSE messages", () => {
    const input = `event: reasoning
data: {"step":1,"content":"thinking"}

event: token
data: {"content":"Hi"}

`;

    const { messages, remainder } = parseSseChunk(input);
    expect(messages).toHaveLength(2);
    expect(messages[0]).toEqual({
      event: "reasoning",
      data: '{"step":1,"content":"thinking"}',
    });
    expect(remainder).toBe("");
  });

  it("keeps partial chunks in remainder", () => {
    const input = `event: token
data: {"content":"Hel`;

    const { messages, remainder } = parseSseChunk(input);
    expect(messages).toHaveLength(0);
    expect(remainder).toBe(input);
  });
});

describe("parseSseEvent", () => {
  it("parses known events", () => {
    expect(
      parseSseEvent("done", '{"session_id":"abc","reply":"ok","error":false}'),
    ).toEqual({
      type: "done",
      session_id: "abc",
      reply: "ok",
      error: false,
    });
  });

  it("returns null for invalid JSON", () => {
    expect(parseSseEvent("token", "not-json")).toBeNull();
  });
});

describe("consumeSseStream", () => {
  it("consumes success stream", async () => {
    const encoder = new TextEncoder();
    const stream = new ReadableStream({
      start(controller) {
        controller.enqueue(
          encoder.encode(
            'event: token\ndata: {"content":"Hello"}\n\nevent: done\ndata: {"session_id":"1","reply":"Hello","error":false}\n\n',
          ),
        );
        controller.close();
      },
    });

    const events: string[] = [];
    await consumeSseStream(stream, (event) => {
      events.push(event.type);
    });

    expect(events).toEqual(["token", "done"]);
  });

  it("consumes error stream", async () => {
    const encoder = new TextEncoder();
    const stream = new ReadableStream({
      start(controller) {
        controller.enqueue(
          encoder.encode(
            'event: error\ndata: {"message":"Сервис временно недоступен"}\n\nevent: done\ndata: {"session_id":"1","reply":"Сервис временно недоступен","error":true}\n\n',
          ),
        );
        controller.close();
      },
    });

    const events: string[] = [];
    await consumeSseStream(stream, (event) => {
      events.push(event.type);
    });

    expect(events).toEqual(["error", "done"]);
  });

  it("handles chunked partial data", async () => {
    const encoder = new TextEncoder();
    const chunks = [
      'event: token\ndata: {"cont',
      'ent":"Hel"}\n\nevent: token\ndata: {"content":"lo"}\n\n',
    ];
    let index = 0;
    const stream = new ReadableStream({
      pull(controller) {
        if (index < chunks.length) {
          controller.enqueue(encoder.encode(chunks[index]));
          index += 1;
        } else {
          controller.close();
        }
      },
    });

    const tokens: string[] = [];
    await consumeSseStream(stream, (event) => {
      if (event.type === "token") {
        tokens.push(event.content);
      }
    });

    expect(tokens).toEqual(["Hel", "lo"]);
  });
});
