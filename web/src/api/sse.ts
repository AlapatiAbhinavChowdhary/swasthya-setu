import { API_BASE_URL, ApiError } from "./client";
import type { ChatRequest, SourceResponse } from "../types";

export interface SseMetadata {
  sources: SourceResponse[];
  intent: string;
  emergency: boolean;
  language: string;
  language_consistent: boolean;
  request_id: string;
}

export interface StreamChatHandlers {
  onChunk: (chunk: string) => void;
  onMetadata: (metadata: SseMetadata) => void;
  onError: (error: Error) => void;
  onDone: () => void;
}

export async function streamChat(
  payload: ChatRequest,
  handlers: StreamChatHandlers,
  signal?: AbortSignal
): Promise<void> {
  const url = `${API_BASE_URL}/chat/stream`;

  try {
    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "text/event-stream",
      },
      body: JSON.stringify(payload),
      signal,
    });

    if (!response.ok) {
      let errorDetail = "";
      try {
        const errorJson = await response.json();
        errorDetail = errorJson.detail || JSON.stringify(errorJson);
      } catch {
        errorDetail = await response.text();
      }

      if (response.status === 429) {
        throw new ApiError("Rate limit exceeded. Please wait a moment before sending another message.", 429, errorDetail);
      } else if (response.status === 503) {
        throw new ApiError("The assistant is temporarily unavailable. Please try again shortly.", 503, errorDetail);
      }
      throw new ApiError(errorDetail || `Streaming failed with status ${response.status}`, response.status);
    }

    if (!response.body) {
      throw new Error("No response stream received from the server.");
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const blocks = buffer.split("\n\n");
      // Keep unfinished block in buffer
      buffer = blocks.pop() || "";

      for (const block of blocks) {
        if (!block.trim()) continue;

        let eventType = "message";
        let dataStr = "";

        const lines = block.split("\n");
        for (const line of lines) {
          if (line.startsWith("event:")) {
            eventType = line.replace("event:", "").trim();
          } else if (line.startsWith("data:")) {
            dataStr = line.replace("data:", "").trim();
          }
        }

        if (eventType === "message" && dataStr) {
          try {
            const parsed = JSON.parse(dataStr);
            if (typeof parsed.chunk === "string") {
              handlers.onChunk(parsed.chunk);
            }
          } catch {
            handlers.onChunk(dataStr);
          }
        } else if (eventType === "metadata" && dataStr) {
          try {
            const meta = JSON.parse(dataStr) as SseMetadata;
            handlers.onMetadata(meta);
          } catch (e) {
            console.error("Failed to parse SSE metadata event:", e);
          }
        } else if (eventType === "done") {
          handlers.onDone();
          return;
        }
      }
    }

    handlers.onDone();
  } catch (err: unknown) {
    if (signal?.aborted) return;
    const error = err instanceof Error ? err : new Error(String(err));
    handlers.onError(error);
  }
}

