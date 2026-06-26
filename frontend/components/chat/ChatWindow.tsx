"use client";

import { useCallback, useEffect, useState, type Dispatch, type SetStateAction } from "react";

import { AgentActivity } from "@/components/chat/AgentActivity";
import { ChatInput } from "@/components/chat/ChatInput";
import { MessageList } from "@/components/chat/MessageList";
import { TelegramHandoff } from "@/components/chat/TelegramHandoff";
import { ApiClientError, fetchSession, sendChatMessage } from "@/lib/api-client";
import { getStoredSessionId, setStoredSessionId } from "@/lib/session";
import type { ActivityItem, ChatMessage, SseEvent } from "@/lib/types";

interface ChatWindowProps {
  botUsername: string | null;
}

function applySseEvent(
  event: SseEvent,
  setActivity: Dispatch<SetStateAction<ActivityItem[]>>,
  setStreamingContent: Dispatch<SetStateAction<string>>,
  setSessionId: Dispatch<SetStateAction<string | null>>,
  setMessages: Dispatch<SetStateAction<ChatMessage[]>>,
): string | null {
  switch (event.type) {
    case "reasoning":
      setActivity((current) => [
        ...current,
        { kind: "reasoning", step: event.step, content: event.content },
      ]);
      return null;
    case "tool_start":
      setActivity((current) => [
        ...current,
        { kind: "tool", name: event.name, args: event.args, status: "running" },
      ]);
      return null;
    case "tool_end":
      setActivity((current) => {
        const next = [...current];
        for (let index = next.length - 1; index >= 0; index -= 1) {
          const item = next[index];
          if (item.kind === "tool" && item.name === event.name && item.status === "running") {
            next[index] = { ...item, result: event.result, status: "done" };
            return next;
          }
        }
        return [
          ...next,
          { kind: "tool", name: event.name, result: event.result, status: "done" },
        ];
      });
      return null;
    case "token":
      setStreamingContent((current) => current + event.content);
      return null;
    case "error":
      return event.message;
    case "done": {
      setSessionId(event.session_id);
      setStoredSessionId(event.session_id);
      setMessages((current) => [...current, { role: "assistant", content: event.reply }]);
      setStreamingContent("");
      return event.error ? event.reply : null;
    }
    default:
      return null;
  }
}

function readStoredSessionId(): string | null {
  if (typeof window === "undefined") {
    return null;
  }
  return getStoredSessionId();
}

export function ChatWindow({ botUsername }: ChatWindowProps) {
  const [initialSessionId] = useState(readStoredSessionId);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [activity, setActivity] = useState<ActivityItem[]>([]);
  const [sessionId, setSessionId] = useState<string | null>(initialSessionId);
  const [streamingContent, setStreamingContent] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isRestoring, setIsRestoring] = useState(() => Boolean(initialSessionId));

  useEffect(() => {
    if (!initialSessionId) {
      return;
    }

    void fetchSession(initialSessionId)
      .then((session) => {
        setMessages(session.messages);
      })
      .catch(() => {
        setSessionId(null);
      })
      .finally(() => {
        setIsRestoring(false);
      });
  }, [initialSessionId]);

  const handleSend = useCallback(
    async (message: string) => {
      setErrorMessage(null);
      setActivity([]);
      setStreamingContent("");
      setMessages((current) => [...current, { role: "user", content: message }]);
      setIsStreaming(true);

      try {
        let streamError: string | null = null;
        await sendChatMessage(
          {
            session_id: sessionId,
            message,
          },
          (event) => {
            const error = applySseEvent(
              event,
              setActivity,
              setStreamingContent,
              setSessionId,
              setMessages,
            );
            if (error) {
              streamError = error;
            }
          },
        );
        if (streamError) {
          setErrorMessage(streamError);
        }
      } catch (error) {
        if (error instanceof ApiClientError) {
          setErrorMessage(error.message);
        } else {
          setErrorMessage("Не удалось связаться с сервисом. Попробуйте ещё раз.");
        }
      } finally {
        setIsStreaming(false);
      }
    },
    [sessionId],
  );

  return (
    <div className="grid h-[calc(100vh-4rem)] grid-cols-1 lg:grid-cols-[minmax(0,1fr)_360px]">
      <section className="flex min-h-0 flex-col border-r border-zinc-200 bg-white">
        <header className="border-b border-zinc-200 px-4 py-4">
          <h1 className="text-lg font-semibold text-zinc-900">LLMStart Agent</h1>
          <p className="text-sm text-zinc-500">
            {isRestoring
              ? "Восстанавливаем историю..."
              : sessionId
                ? `Сессия: ${sessionId.slice(0, 8)}…`
                : "Новая сессия"}
          </p>
        </header>

        {errorMessage ? (
          <div className="border-b border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
            {errorMessage}
            <button
              type="button"
              className="ml-3 underline"
              onClick={() => setErrorMessage(null)}
            >
              Закрыть
            </button>
          </div>
        ) : null}

        <div className="min-h-0 flex-1">
          <MessageList messages={messages} streamingContent={streamingContent} />
        </div>

        <TelegramHandoff sessionId={sessionId} botUsername={botUsername} />
        <ChatInput disabled={isStreaming || isRestoring} onSend={handleSend} />
      </section>

      <aside className="min-h-0">
        <AgentActivity items={activity} />
      </aside>
    </div>
  );
}
