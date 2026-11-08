import { describe, it, expect, vi, beforeEach } from "vitest";
import { streamChat } from "../api/sse";

describe("streamChat SSE client", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("handles chunk, metadata, and done events properly", async () => {
    const ssePayload = [
      'event: message\ndata: {"chunk":"Tuberculosis is "}\n\n',
      'event: message\ndata: {"chunk":"curable."}\n\n',
      'event: metadata\ndata: {"sources":[],"intent":"general","emergency":false,"language":"en","language_consistent":true,"request_id":"test-123"}\n\n',
      "event: done\ndata: {}\n\n",
    ].join("");

    const encoder = new TextEncoder();
    const stream = new ReadableStream({
      start(controller) {
        controller.enqueue(encoder.encode(ssePayload));
        controller.close();
      },
    });

    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      body: stream,
    });

    const chunks: string[] = [];
    let receivedMeta = null;
    let doneCalled = false;

    await streamChat(
      { message: "Is TB curable?" },
      {
        onChunk: (c) => chunks.push(c),
        onMetadata: (m) => {
          receivedMeta = m;
        },
        onError: () => {},
        onDone: () => {
          doneCalled = true;
        },
      }
    );

    expect(chunks).toEqual(["Tuberculosis is ", "curable."]);
    expect(receivedMeta).toEqual({
      sources: [],
      intent: "general",
      emergency: false,
      language: "en",
      language_consistent: true,
      request_id: "test-123",
    });
    expect(doneCalled).toBe(true);
  });

  it("calls onError on HTTP error", async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 503,
      json: async () => ({ detail: "Busy" }),
    });

    let caughtError: Error | null = null;
    await streamChat(
      { message: "test" },
      {
        onChunk: () => {},
        onMetadata: () => {},
        onError: (err) => {
          caughtError = err;
        },
        onDone: () => {},
      }
    );

    expect(caughtError).not.toBeNull();
    const typedError = caughtError as Error | null;
    expect(typedError?.message).toContain("assistant is temporarily unavailable");
  });
});
