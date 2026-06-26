export const dynamic = "force-dynamic";

import { getBackendApiKey, getBackendUrl } from "@/lib/backend-config";

export async function GET(
  _request: Request,
  context: { params: Promise<{ id: string }> },
) {
  const { id } = await context.params;
  const backendUrl = getBackendUrl();
  const apiKey = getBackendApiKey();

  const backendResponse = await fetch(`${backendUrl}/api/v1/sessions/${id}`, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${apiKey}`,
      Accept: "application/json",
    },
    cache: "no-store",
  });

  const body = await backendResponse.text();
  return new Response(body, {
    status: backendResponse.status,
    headers: { "Content-Type": "application/json" },
  });
}
