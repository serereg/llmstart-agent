"use client";

import { ChevronDown, ChevronRight, Wrench } from "lucide-react";
import { useEffect, useState } from "react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";
import { ScrollArea } from "@/components/ui/scroll-area";
import type { ActivityItem } from "@/lib/types";

interface AgentActivityProps {
  items: ActivityItem[];
}

const TRUNCATE_LENGTH = 280;

function truncateJson(value: unknown): string {
  const text = typeof value === "string" ? value : JSON.stringify(value, null, 2);
  if (text.length <= TRUNCATE_LENGTH) {
    return text;
  }
  return `${text.slice(0, TRUNCATE_LENGTH)}…`;
}

function ActivityCard({ item }: { item: ActivityItem }) {
  const [expanded, setExpanded] = useState(false);

  if (item.kind === "reasoning") {
    return (
      <Card>
        <CardHeader className="pb-2">
          <CardTitle>Reasoning · шаг {item.step}</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="whitespace-pre-wrap text-sm text-zinc-700">{item.content}</p>
        </CardContent>
      </Card>
    );
  }

  const resultText = item.result ?? "";
  const isLong = resultText.length > TRUNCATE_LENGTH;

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="flex items-center gap-2">
          <Wrench className="h-4 w-4" />
          {item.name}
          <span className="text-xs font-normal text-zinc-500">
            {item.status === "running" ? "выполняется" : "готово"}
          </span>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-2 text-xs">
        {item.args && Object.keys(item.args).length > 0 ? (
          <div>
            <p className="mb-1 font-medium text-zinc-600">args</p>
            <pre className="overflow-x-auto rounded bg-zinc-50 p-2 text-zinc-800">
              {truncateJson(item.args)}
            </pre>
          </div>
        ) : null}
        {item.result ? (
          <div>
            <p className="mb-1 font-medium text-zinc-600">result</p>
            <pre className="overflow-x-auto rounded bg-zinc-50 p-2 text-zinc-800">
              {expanded || !isLong ? resultText : truncateJson(resultText)}
            </pre>
            {isLong ? (
              <button
                type="button"
                className="mt-1 text-xs text-zinc-600 underline"
                onClick={() => setExpanded((current) => !current)}
              >
                {expanded ? "Свернуть" : "Показать полностью"}
              </button>
            ) : null}
          </div>
        ) : null}
      </CardContent>
    </Card>
  );
}

export function AgentActivity({ items }: AgentActivityProps) {
  const [open, setOpen] = useState(() => {
    if (typeof window === "undefined") {
      return false;
    }
    return window.matchMedia("(min-width: 1024px)").matches;
  });

  useEffect(() => {
    const media = window.matchMedia("(min-width: 1024px)");
    const listener = (event: MediaQueryListEvent) => setOpen(event.matches);
    media.addEventListener("change", listener);
    return () => media.removeEventListener("change", listener);
  }, []);

  return (
    <Collapsible open={open} onOpenChange={setOpen} className="flex h-full flex-col border-l border-zinc-200 bg-zinc-50">
      <CollapsibleTrigger className="flex items-center justify-between border-b border-zinc-200 px-4 py-3 text-left">
        <div>
          <p className="text-sm font-semibold text-zinc-900">Agent Activity</p>
          <p className="text-xs text-zinc-500">Reasoning и вызовы tools в реальном времени</p>
        </div>
        {open ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
      </CollapsibleTrigger>
      <CollapsibleContent className="min-h-0 flex-1 data-[state=closed]:hidden">
        <ScrollArea className="h-full max-h-[calc(100vh-12rem)] lg:max-h-none">
          <div className="space-y-3 p-4">
            {items.length === 0 ? (
              <p className="text-sm text-zinc-500">Активность агента появится после отправки сообщения.</p>
            ) : (
              items.map((item, index) => <ActivityCard key={`${item.kind}-${index}`} item={item} />)
            )}
          </div>
        </ScrollArea>
      </CollapsibleContent>
    </Collapsible>
  );
}
