import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

vi.mock("@/lib/backend-config", () => ({
  getTelegramBotUsername: () => "llmstart_bot",
}));

import HomePage from "@/app/page";

describe("HomePage", () => {
  it("renders chat widget shell", () => {
    render(<HomePage />);
    expect(screen.getByText("LLMStart Agent")).toBeInTheDocument();
    expect(screen.getByLabelText("Сообщение")).toBeInTheDocument();
  });
});
