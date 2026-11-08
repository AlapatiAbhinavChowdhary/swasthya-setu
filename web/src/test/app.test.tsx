import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import React from "react";
import { App } from "../App";

describe("App component", () => {
  beforeEach(() => {
    // Mock matchMedia
    Object.defineProperty(window, "matchMedia", {
      writable: true,
      value: vi.fn().mockImplementation((query) => ({
        matches: false,
        media: query,
        onchange: null,
        addListener: vi.fn(),
        removeListener: vi.fn(),
        addEventListener: vi.fn(),
        removeEventListener: vi.fn(),
        dispatchEvent: vi.fn(),
      })),
    });

    // Mock fetch for coverage / health calls
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ diseases: [] }),
    });
  });

  it("renders navbar with brand title and navigation links", () => {
    render(<App />);
    const brandElements = screen.getAllByText("Swasthya Setu");
    expect(brandElements.length).toBeGreaterThan(0);
    expect(screen.getByRole("link", { name: "Home" })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Chat" })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Diseases" })).toBeInTheDocument();
  });
});
