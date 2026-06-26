import { ChatWindow } from "@/components/chat/ChatWindow";
import { getTelegramBotUsername } from "@/lib/backend-config";

export default function HomePage() {
  const botUsername = getTelegramBotUsername();

  return (
    <main className="min-h-screen bg-zinc-100">
      <ChatWindow botUsername={botUsername} />
    </main>
  );
}
