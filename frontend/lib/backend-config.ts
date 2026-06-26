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

export function getTelegramBotUsername(): string | null {
  return process.env.TELEGRAM_BOT_USERNAME ?? null;
}
