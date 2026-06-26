import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { MessageList } from "@/components/chat/MessageList";

describe("MessageList", () => {
  it("renders placeholder when empty", () => {
    render(<MessageList messages={[]} />);
    expect(screen.getByText(/Задайте вопрос о курсах LLMStart/i)).toBeInTheDocument();
  });

  it("renders user and assistant messages", () => {
    render(
      <MessageList
        messages={[
          { role: "user", content: "Привет" },
          { role: "assistant", content: "Здравствуйте" },
        ]}
      />,
    );

    expect(screen.getByText("Привет")).toBeInTheDocument();
    expect(screen.getByText("Здравствуйте")).toBeInTheDocument();
  });
});
