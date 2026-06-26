import { cleanup, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it } from "vitest";

import { AgentActivity } from "@/components/chat/AgentActivity";

afterEach(() => {
  cleanup();
});

describe("AgentActivity", () => {
  it("renders panel header", () => {
    render(<AgentActivity items={[]} />);
    expect(screen.getByText("Agent Activity")).toBeInTheDocument();
  });

  it("renders reasoning and tool cards when expanded", async () => {
    const user = userEvent.setup();
    render(
      <AgentActivity
        items={[
          { kind: "reasoning", step: 1, content: "Analyzing request" },
          {
            kind: "tool",
            name: "list_b2c_products",
            args: {},
            status: "done",
            result: "[]",
          },
        ]}
      />,
    );

    await user.click(screen.getByRole("button", { name: /Agent Activity/i }));

    expect(screen.getByText(/Reasoning · шаг 1/i)).toBeInTheDocument();
    expect(screen.getByText("list_b2c_products")).toBeInTheDocument();
  });
});
