import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import React from "react";
import { SafeAnswerRenderer } from "../components/SafeAnswerRenderer";

describe("SafeAnswerRenderer", () => {
  it("renders plain text safely", () => {
    render(<SafeAnswerRenderer text="Tuberculosis is curable." />);
    expect(screen.getByText("Tuberculosis is curable.")).toBeInTheDocument();
  });

  it("renders citation chips as interactive buttons", () => {
    const onSelect = vi.fn();
    render(
      <SafeAnswerRenderer
        text="Malaria is caused by Plasmodium parasites [1] transmitted by female Anopheles mosquitoes [2]."
        onCitationClick={onSelect}
      />
    );

    const chip1 = screen.getByRole("button", { name: "View cited source 1" });
    const chip2 = screen.getByRole("button", { name: "View cited source 2" });
    expect(chip1).toBeInTheDocument();
    expect(chip2).toBeInTheDocument();

    fireEvent.click(chip1);
    expect(onSelect).toHaveBeenCalledWith(1);
  });

  it("renders bold text formatted without dangerouslySetInnerHTML", () => {
    const { container } = render(
      <SafeAnswerRenderer text="Warning: **high fever** requires attention." />
    );
    const strong = container.querySelector("strong");
    expect(strong).not.toBeNull();
    expect(strong?.textContent).toBe("high fever");
    expect(container.innerHTML).not.toContain("dangerouslySetInnerHTML");
  });

  it("renders bullet items cleanly", () => {
    render(
      <SafeAnswerRenderer text={"- High fever\n- Chills\n- Sweats"} />
    );
    expect(screen.getByText("High fever")).toBeInTheDocument();
    expect(screen.getByText("Chills")).toBeInTheDocument();
    expect(screen.getByText("Sweats")).toBeInTheDocument();
  });
});
