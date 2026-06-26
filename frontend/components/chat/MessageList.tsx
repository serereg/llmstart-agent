"use client";

import ReactMarkdown from "react-markdown";

import { ScrollArea } from "@/components/ui/scroll-area";
import { cn } from "@/lib/utils";
import type { ChatMessage } from "@/lib/types";

interface MessageListProps {
  messages: ChatMessage[];
  streamingContent?: string;
}

export function MessageList({ messages, streamingContent }: MessageListProps) {
  const displayMessages = [...messages];
  if (streamingContent) {
    displayMessages.push({ role: "assistant", content: streamingContent });
  }

  return (
    <ScrollArea className="h-full">
      <div className="flex flex-col gap-4 p-4">
        {displayMessages.length === 0 ? (
          <p className="text-sm text-zinc-500">
            Задайте вопрос о курсах LLMStart — агент подберёт продукт или ответит по базе знаний.
          </p>
        ) : (
          displayMessages.map((message, index) => (
            <div
              key={`${message.role}-${index}`}
              className={cn(
                "max-w-[85%] rounded-2xl px-4 py-3 text-sm leading-relaxed",
                message.role === "user"
                  ? "ml-auto bg-zinc-900 text-white"
                  : "mr-auto border border-zinc-200 bg-white text-zinc-900",
              )}
            >
              {message.role === "assistant" ? (
                <div className="prose prose-sm max-w-none prose-p:my-2 prose-ul:my-2 prose-ol:my-2">
                  <ReactMarkdown>{message.content}</ReactMarkdown>
                </div>
              ) : (
                <p className="whitespace-pre-wrap">{message.content}</p>
              )}
            </div>
          ))
        )}
      </div>
    </ScrollArea>
  );
}
