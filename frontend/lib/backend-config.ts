import { cache } from "react";

const PLACEHOLDER_USERNAMES = new Set(["", "your_bot_username"]);

function normalizeUsername(username: string): string {
  return username.trim().replace(/^@/, "");
}

function isPlaceholderUsername(username: string | undefined): boolean {
  if (!username) {
    return true;
  }
  return PLACEHOLDER_USERNAMES.has(username.trim());
}

async function fetchBotUsernameFromTelegram(token: string): Promise<string | null> {
  try {
    const response = await fetch(`https://api.telegram.org/bot${token}/getMe`, {
      next: { revalidate: 3600 },
    });
    if (!response.ok) {
      return null;
    }
    const body = (await response.json()) as {
      ok: boolean;
      result?: { username?: string };
    };
    if (!body.ok || !body.result?.username) {
      return null;
    }
    return normalizeUsername(body.result.username);
  } catch {
    return null;
  }
}

function requireEnv(name: string): string {
  const value = process.env[name];
  if (!value) {
    throw new Error(`Missing required environment variable: ${name}`);
  }
  return value;
}

export function getBackendUrl(): string {
  return process.env.BACKEND_URL ?? "http://localhost:8000";
}

export function getBackendApiKey(): string {
  return requireEnv("BACKEND_API_KEY");
}

/** Resolve Telegram bot username from env or Telegram getMe API (server-only). */
export const getTelegramBotUsername = cache(async (): Promise<string | null> => {
  const configured = process.env.TELEGRAM_BOT_USERNAME;
  if (!isPlaceholderUsername(configured)) {
    return normalizeUsername(configured!);
  }

  const token = process.env.TELEGRAM_BOT_TOKEN?.trim();
  if (!token) {
    return null;
  }

  return fetchBotUsernameFromTelegram(token);
});
