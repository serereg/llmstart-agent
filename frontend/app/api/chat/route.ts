export const dynamic = "force-dynamic";

import { getBackendApiKey, getBackendUrl } from "@/lib/backend-config";
import { NextRequest } from "next/server";

export async function POST(request: NextRequest) {
  let body: { session_id?: string | null; message?: string };
  try {
    body = (await request.json()) as { session_id?: string | null; message?: string };
  } catch {
    return Response.json({ detail: "Invalid JSON body" }, { status: 400 });
  }

  if (!body.message?.trim()) {
    return Response.json({ detail: "message is required" }, { status: 422 });
  }

  const backendUrl = getBackendUrl();
  const apiKey = getBackendApiKey();

  const backendResponse = await fetch(`${backendUrl}/api/v1/chat`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${apiKey}`,
      "Content-Type": "application/json",
      Accept: "text/event-stream",
    },
    body: JSON.stringify({
      session_id: body.session_id ?? null,
      message: body.message,
      channel: "web",
    }),
  });

  if (!backendResponse.ok) {
    const errorBody = await backendResponse.text();
    return new Response(errorBody, {
      status: backendResponse.status,
      headers: { "Content-Type": "application/json" },
    });
  }

  if (!backendResponse.body) {
    return Response.json({ detail: "Empty backend response" }, { status: 502 });
  }

  return new Response(backendResponse.body, {
    status: 200,
    headers: {
      "Content-Type": "text/event-stream",
      "Cache-Control": "no-cache, no-transform",
      Connection: "keep-alive",
    },
  });
}
