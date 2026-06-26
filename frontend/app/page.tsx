import { ChatWindow } from "@/components/chat/ChatWindow";
import { getTelegramBotUsername } from "@/lib/backend-config";

export const dynamic = "force-dynamic";

export default async function HomePage() {
  const botUsername = await getTelegramBotUsername();

  return (
    <main className="min-h-screen bg-zinc-100">
      <ChatWindow botUsername={botUsername} />
    </main>
  );
}
