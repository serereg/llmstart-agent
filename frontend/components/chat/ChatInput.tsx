"use client";

import { Send } from "lucide-react";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { MAX_MESSAGE_LENGTH } from "@/lib/types";

interface ChatInputProps {
  disabled?: boolean;
  onSend: (message: string) => void;
}

export function ChatInput({ disabled = false, onSend }: ChatInputProps) {
  const [value, setValue] = useState("");
  const trimmed = value.trim();
  const isTooLong = value.length > MAX_MESSAGE_LENGTH;
  const canSend = trimmed.length > 0 && !isTooLong && !disabled;

  function handleSend() {
    if (!canSend) {
      return;
    }
    onSend(trimmed);
    setValue("");
  }

  return (
    <div className="border-t border-zinc-200 bg-white p-4">
      <div className="flex items-end gap-3">
        <div className="flex-1">
          <Textarea
            value={value}
            onChange={(event) => setValue(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter" && !event.shiftKey) {
                event.preventDefault();
                handleSend();
              }
            }}
            placeholder="Напишите сообщение..."
            disabled={disabled}
            rows={3}
            aria-label="Сообщение"
          />
          <div className="mt-1 flex justify-between text-xs text-zinc-500">
            <span>{isTooLong ? `Максимум ${MAX_MESSAGE_LENGTH} символов` : "Enter — отправить, Shift+Enter — новая строка"}</span>
            <span>
              {value.length}/{MAX_MESSAGE_LENGTH}
            </span>
          </div>
        </div>
        <Button onClick={handleSend} disabled={!canSend} aria-label="Отправить">
          <Send className="h-4 w-4" />
        </Button>
      </div>
    </div>
  );
}
