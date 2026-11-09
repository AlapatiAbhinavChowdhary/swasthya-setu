import { test, expect } from "@playwright/test";

test.use({ baseURL: "http://127.0.0.1:8000" });

test("live smoke: real end-to-end stack chat with citations and source drawer", async ({
  page,
  request,
}) => {
  // Check whether the real API is running and configured with a real LLM
  let llmConfigured = false;
  try {
    const health = await request.get("/health", { timeout: 3000 });
    if (health.ok()) {
      const data = await health.json();
      llmConfigured = Boolean(data.llm_configured);
    }
  } catch {
    llmConfigured = false;
  }

  test.skip(!llmConfigured, "Skipping live smoke test: LLM is not configured or server is offline.");

  // Navigate to live real chat page (no page.route mocks)
  await page.goto("/chat");
  await page.waitForLoadState("networkidle");

  const input = page.getByPlaceholder(/Ask about symptoms/i);
  await expect(input).toBeVisible();

  // Ask question
  await input.fill("What are the symptoms of malaria?");
  await page.getByRole("button", { name: "Send", exact: true }).click();

  // Wait for real streamed answer to appear in the DOM
  await expect(page.getByText(/fever|chills|headache|parasite/i).first()).toBeVisible({
    timeout: 35000,
  });

  // Verify at least one interactive citation chip is rendered
  const chip = page.getByRole("button", { name: /View cited source 1/i }).first();
  if (await chip.isVisible()) {
    await chip.click();
    // Confirm the source details drawer opened
    await expect(page.getByRole("dialog", { name: /Source citation/i })).toBeVisible();
    await expect(page.getByText(/Citation \[1\] Details/i)).toBeVisible();
  }
});
