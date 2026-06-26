"use client";

import { ExternalLink } from "lucide-react";

import { Button } from "@/components/ui/button";

interface TelegramHandoffProps {
  sessionId: string | null;
  botUsername: string | null;
}

export function TelegramHandoff({ sessionId, botUsername }: TelegramHandoffProps) {
  const disabled = !sessionId || !botUsername;
  const href =
    sessionId && botUsername
      ? `https://t.me/${botUsername}?start=session_${sessionId}`
      : undefined;

  const hint = !botUsername
    ? "Укажите TELEGRAM_BOT_USERNAME в .env (username бота из @BotFather)"
    : !sessionId
      ? "Ссылка появится после первого ответа агента"
      : "Продолжите диалог в Telegram с сохранённой историей";

  return (
    <div className="border-t border-zinc-200 bg-zinc-50 px-4 py-3">
      <Button
        asChild={!disabled}
        variant="outline"
        className="w-full"
        disabled={disabled}
      >
        {disabled ? (
          <span className="inline-flex items-center gap-2">
            <ExternalLink className="h-4 w-4" />
            Перейти в Telegram
          </span>
        ) : (
          <a href={href} target="_blank" rel="noopener noreferrer">
            <ExternalLink className="h-4 w-4" />
            Перейти в Telegram
          </a>
        )}
      </Button>
      <p className="mt-2 text-center text-xs text-zinc-500">{hint}</p>
    </div>
  );
}
