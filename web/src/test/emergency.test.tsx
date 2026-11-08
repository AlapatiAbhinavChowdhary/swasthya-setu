import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import React from "react";
import { EmergencyCard } from "../components/EmergencyCard";

describe("EmergencyCard", () => {
  it("renders the 108 emergency call link", () => {
    render(<EmergencyCard />);
    const link = screen.getByRole("link", { name: /Call 108/i });
    expect(link).toBeInTheDocument();
    expect(link).toHaveAttribute("href", "tel:108");
    expect(screen.getByText("Call 108 Emergency Helpline")).toBeInTheDocument();
  });

  it("renders emergency banner with custom message when provided", () => {
    render(
      <EmergencyCard
        message="यह एक आपातकालीन स्थिति हो सकती है।"
        callLabel="तुरंत 108 पर कॉल करें"
      />
    );
    expect(screen.getByText("यह एक आपातकालीन स्थिति हो सकती है।")).toBeInTheDocument();
    expect(screen.getByText("तुरंत 108 पर कॉल करें")).toBeInTheDocument();
  });
});
