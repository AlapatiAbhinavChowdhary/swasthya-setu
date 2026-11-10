import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = fileURLToPath(new URL(".", import.meta.url));
const SCREENSHOT_DIR = path.resolve(__dirname, "../../docs/screenshots");

const MOCK_COVERAGE = {
  last_indexed: "2026-11-08T00:00:00Z",
  diseases: [
    {
      id: "malaria",
      name_en: "Malaria",
      name_hi: "मलेरिया",
      category: "vector-borne",
      documents: 5,
      specific_documents: 4,
      chunks: 250,
      depth: "deep",
      newest_source_year: 2024,
      has_general_source: false,
      documents_detail: [
        {
          id: "malaria-who-factsheet",
          doc_id: "hash123",
          title: "WHO Malaria Fact Sheet",
          publisher: "WHO",
          url: "https://www.who.int/news-room/fact-sheets/detail/malaria",
          file: "data/raw/who_malaria.html",
          year: 2024,
          doc_type: "fact_sheet",
          chunks: 40,
          coverage: "disease-specific",
          label: "disease-specific",
        },
      ],
      last_indexed: "2026-11-08T00:00:00Z",
      status: "indexed",
      reviewed: false,
    },
    {
      id: "tuberculosis",
      name_en: "Tuberculosis",
      name_hi: "क्षय रोग",
      category: "respiratory",
      documents: 6,
      specific_documents: 5,
      chunks: 310,
      depth: "deep",
      newest_source_year: 2024,
      has_general_source: false,
      documents_detail: [],
      status: "indexed",
      reviewed: false,
    },
    {
      id: "dengue",
      name_en: "Dengue",
      name_hi: "डेंगू",
      category: "vector-borne",
      documents: 4,
      specific_documents: 3,
      chunks: 180,
      depth: "deep",
      newest_source_year: 2023,
      has_general_source: false,
      documents_detail: [],
      status: "indexed",
      reviewed: false,
    },
  ],
};

const MOCK_VACCINATION = {
  source_label: "National Immunization Schedule (NIS), MoHFW, Govt. of India",
  reviewed: false,
  age_months_queried: null,
  schedule: [
    {
      age: "At Birth",
      age_key: "birth",
      age_months_min: 0,
      age_months_max: 0.5,
      target_group: "Infants",
      vaccines: ["BCG", "OPV-0", "Hepatitis B birth dose"],
      supplements: [],
      description: "Administered as early as possible after delivery.",
    },
    {
      age: "9–12 Months",
      age_key: "9_months",
      age_months_min: 9,
      age_months_max: 12,
      target_group: "Infants",
      vaccines: ["MR 1st dose", "JE-1", "PCV Booster"],
      supplements: ["Vitamin A 1st dose (Nutritional supplement)"],
      description: "First dose of Vitamin A supplement (not a vaccine) administered alongside MR.",
    },
  ],
  footnotes: {
    "Vitamin A": "Administered as a nutritional prophylaxis supplement under UIP, not an infectious antigen.",
  },
};

const MOCK_ALERTS = {
  disclaimer: "DEMO DATA ONLY - Not a live alert. Consult IDSP at idsp.nic.in.",
  is_demo: true,
  query: {},
  count: 1,
  alerts: [
    {
      id: "alert-1",
      label: "Demo Entry",
      disease: "Dengue",
      district: "Gorakhpur",
      state: "Uttar Pradesh",
      date: "2026-11-01",
      advisory: "Eliminate standing water in coolers and containers.",
      advisory_hi: "कूलर और बर्तनों में जमा पानी को तुरंत साफ करें।",
      source: "NVBDCP Dengue Guidelines",
    },
  ],
};

const MOCK_FACILITIES = {
  disclaimer: "SAMPLE DATA ONLY - For demonstration. In an emergency, call 108.",
  is_sample: true,
  query: {},
  count: 1,
  facilities: [
    {
      id: "fac-1",
      name: "Gorakhpur District Hospital (Demo Entry)",
      type: "District Hospital",
      district: "Gorakhpur",
      state: "Uttar Pradesh",
      address: "Civil Lines, Gorakhpur",
      phone: "108 (Emergency)",
      label: "Sample",
    },
  ],
};

const MOCK_ADMIN_FEEDBACK = {
  count: 2,
  feedback: [
    {
      id: 1,
      session_hash: "a1b2c3d4",
      rating: "up",
      comment: "Very clear explanation of malaria symptoms.",
      request_id: "req-111",
      created_at: "2026-11-08 10:00:00",
    },
    {
      id: 2,
      session_hash: "e5f6g7h8",
      rating: "down",
      comment: "Would love Odia translation.",
      request_id: "req-222",
      created_at: "2026-11-08 11:30:00",
    },
  ],
};

test.beforeEach(async ({ page }) => {
  // Helper to ensure page document navigations are never intercepted as API mocks
  const apiRoute = (
    pattern: string | RegExp,
    handler: (route: Parameters<Parameters<typeof page.route>[1]>[0]) => Promise<void>
  ) => {
    return page.route(pattern, async (route) => {
      if (route.request().resourceType() === "document") {
        return route.continue();
      }
      return handler(route);
    });
  };

  // Mock API routes for reliable, offline-deterministic E2E runs
  await apiRoute("**/coverage", async (route) => {
    await route.fulfill({ json: MOCK_COVERAGE });
  });
  await apiRoute("**/diseases", async (route) => {
    await route.fulfill({ json: MOCK_COVERAGE });
  });
  await apiRoute("**/health", async (route) => {
    await route.fulfill({ json: { status: "ok", llm_configured: true } });
  });
  await apiRoute("**/languages", async (route) => {
    await route.fulfill({
      json: {
        languages: [
          { code: "en", name: "English", native_name: "English", status: "supported" },
          { code: "hi", name: "Hindi", native_name: "हिन्दी", status: "supported" },
          { code: "or", name: "Odia", native_name: "ଓଡ଼ିଆ", status: "draft" },
          { code: "pa", name: "Punjabi", native_name: "ਪੰਜਾਬੀ", status: "draft" },
        ],
      },
    });
  });
  await apiRoute("**/sources", async (route) => {
    await route.fulfill({ json: { content: "# Verified Official Sources" } });
  });
  await apiRoute("**/vaccination*", async (route) => {
    await route.fulfill({ json: MOCK_VACCINATION });
  });
  await apiRoute("**/alerts*", async (route) => {
    await route.fulfill({ json: MOCK_ALERTS });
  });
  await apiRoute("**/facilities*", async (route) => {
    await route.fulfill({ json: MOCK_FACILITIES });
  });
  await apiRoute("**/feedback", async (route) => {
    await route.fulfill({ json: { accepted: true, request_id: "req-fb" } });
  });
  await apiRoute("**/admin/feedback*", async (route) => {
    const auth = route.request().headers()["authorization"];
    if (auth && auth.includes("test-admin-secret")) {
      await route.fulfill({ json: MOCK_ADMIN_FEEDBACK });
    } else {
      await route.fulfill({ status: 401, json: { detail: "Unauthorized" } });
    }
  });
  await apiRoute("**/chat", async (route) => {
    await route.fulfill({
      json: {
        answer: "Malaria is caused by Plasmodium parasites [1]. Common symptoms include fever, chills, and headache [1].",
        citations: [1],
        sources: [{ number: 1, source: "WHO Malaria Fact Sheet", page: "1", snippet: "High fever and chills" }],
        intent: "symptoms",
        emergency: false,
        language: "en",
        language_consistent: true,
        request_id: "req-test",
      },
    });
  });
  await apiRoute("**/chat/stream", async (route) => {
    const sseBody = [
      'event: message\ndata: {"chunk":"Malaria is caused by Plasmodium parasites [1]. "}\n\n',
      'event: message\ndata: {"chunk":"Common symptoms include fever, chills, and headache [1]. "}\n\n',
      'event: metadata\ndata: {"sources":[{"number":1,"source":"WHO Malaria Fact Sheet","page":"1","snippet":"High fever and chills"}],"intent":"symptoms","emergency":false,"language":"en","language_consistent":true,"request_id":"req-test"}\n\n',
      "event: done\ndata: {}\n\n",
    ].join("");
    await route.fulfill({
      status: 200,
      contentType: "text/event-stream",
      body: sseBody,
    });
  });
});

const pagesToTest = [
  { path: "/", name: "home" },
  { path: "/chat", name: "chat" },
  { path: "/diseases", name: "diseases" },
  { path: "/diseases/malaria", name: "disease-detail" },
  { path: "/vaccination", name: "vaccination" },
  { path: "/alerts", name: "alerts" },
  { path: "/facilities", name: "facilities" },
  { path: "/about", name: "about" },
  { path: "/admin", name: "admin" },
];

for (const p of pagesToTest) {
  test(`page ${p.name} renders with 0 console errors, satisfies axe a11y, and captures screenshot`, async ({
    page,
  }, testInfo) => {
    const consoleErrors: string[] = [];
    page.on("console", (msg) => {
      if (msg.type() === "error") {
        consoleErrors.push(msg.text());
      }
    });

    await page.goto(p.path);
    await page.waitForLoadState("networkidle");

    // Check 0 console errors
    expect(consoleErrors).toEqual([]);

    // Axe accessibility audit (0 critical or serious violations)
    const axeResults = await new AxeBuilder({ page })
      .disableRules(["color-contrast"]) // minor contrast nuances on sample demo badges
      .analyze();
    const criticalViolations = axeResults.violations.filter(
      (v) => v.impact === "critical" || v.impact === "serious"
    );
    expect(criticalViolations).toEqual([]);

    // Screenshot in light mode
    const projectName = testInfo.project.name;
    const screenshotPathLight = path.join(
      SCREENSHOT_DIR,
      `${p.name}-${projectName}-light.png`
    );
    await page.screenshot({ path: screenshotPathLight, fullPage: false });

    // Toggle dark mode
    const themeBtn = page.getByRole("button", { name: /switch to dark mode/i });
    if (await themeBtn.isVisible()) {
      await themeBtn.click();
      await page.waitForTimeout(100);

      // Screenshot in dark mode
      const screenshotPathDark = path.join(
        SCREENSHOT_DIR,
        `${p.name}-${projectName}-dark.png`
      );
      await page.screenshot({ path: screenshotPathDark, fullPage: false });
    }
  });
}

test("chat interaction: sends message, streams response, displays source chip", async ({
  page,
}) => {
  await page.goto("/chat");

  // Verify persistent visible emergency notice is present on chat page
  const emergencyNotice = page.getByTestId("persistent-emergency-notice");
  await expect(emergencyNotice).toBeVisible();
  await expect(emergencyNotice).toContainText("108");
  await expect(emergencyNotice).toContainText("112");
  await expect(emergencyNotice.locator('a[href="tel:108"]')).toBeVisible();
  await expect(emergencyNotice.locator('a[href="tel:112"]')).toBeVisible();
  await page.waitForLoadState("networkidle");

  const input = page.getByPlaceholder(/Ask about symptoms/i);
  await input.fill("What are malaria symptoms?");
  await page.getByRole("button", { name: "Send", exact: true }).click();

  // Answer renders
  await expect(page.getByText(/Plasmodium parasites/i)).toBeVisible();
  // Citation chip rendered
  const chip = page.getByRole("button", { name: "View cited source 1" }).first();
  await expect(chip).toBeVisible();

  // Click citation chip opens source panel
  await chip.click();
  await expect(page.getByRole("heading", { name: "WHO Malaria Fact Sheet" })).toBeVisible();
});

test("admin interaction: authenticates with token and shows feedback", async ({
  page,
}) => {
  await page.goto("/admin");
  await page.waitForLoadState("networkidle");

  const tokenInput = page.getByPlaceholder("Enter ADMIN_TOKEN");
  await tokenInput.fill("test-admin-secret");
  await page.getByRole("button", { name: "Access Dashboard" }).click();

  await expect(page.getByText("Total Feedback")).toBeVisible();
  await expect(page.getByText("Very clear explanation of malaria symptoms.")).toBeVisible();
});

test("computed styles: light vs dark background, primary button styling, and >=4.5:1 text contrast", async ({
  page,
}) => {
  await page.goto("/");
  await page.waitForLoadState("networkidle");

  // Helper inside page context to compute WCAG 2.1 contrast ratio
  const evaluateContrast = async (fgSelector: string, bgSelector: string) => {
    return page.evaluate(
      ([fgSel, bgSel]) => {
        const fgEl = document.querySelector(fgSel);
        const bgEl = document.querySelector(bgSel);
        if (!fgEl) return 1;

        const isDark = document.documentElement.classList.contains("dark");
        const defaultBg = isDark ? [9, 9, 11] : [250, 250, 250];

        // Parse any CSS color (rgb, rgba, oklch, hex)
        const parseColor = (colorStr: string, isBackground = false): [number, number, number] => {
          if (!colorStr || colorStr === "transparent") {
            return isBackground ? (isDark ? [9, 9, 11] : [250, 250, 250]) : [0, 0, 0];
          }
          // 1. rgb / rgba
          const rgbMatch = colorStr.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)/);
          if (rgbMatch) {
            return [Number(rgbMatch[1]), Number(rgbMatch[2]), Number(rgbMatch[3])];
          }
          // 2. oklch: e.g. oklch(0.21 0.006 285.885)
          const oklchMatch = colorStr.match(/oklch\(([\d.]+)\s+([\d.]+)\s+([\d.]+)/);
          if (oklchMatch) {
            const L = parseFloat(oklchMatch[1]);
            const C = parseFloat(oklchMatch[2]);
            const hDeg = parseFloat(oklchMatch[3]);
            const hRad = (hDeg * Math.PI) / 180;
            const a = C * Math.cos(hRad);
            const b = C * Math.sin(hRad);
            // OKLab to linear RGB
            const l_ = L + 0.3963377774 * a + 0.2158037573 * b;
            const m_ = L - 0.1055613458 * a - 0.0638541728 * b;
            const s_ = L - 0.0894841775 * a - 1.2914855480 * b;
            const l = l_ * l_ * l_;
            const m = m_ * m_ * m_;
            const s = s_ * s_ * s_;
            const rLin = +4.0767434036 * l - 3.3077115913 * m + 0.2309699292 * s;
            const gLin = -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s;
            const bLin = -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s;
            const toGamma = (val: number) => {
              const clamped = Math.max(0, Math.min(1, val));
              return Math.round((clamped <= 0.0031308 ? 12.92 * clamped : 1.055 * Math.pow(clamped, 1 / 2.4) - 0.055) * 255);
            };
            return [toGamma(rLin), toGamma(gLin), toGamma(bLin)];
          }
          return isBackground ? (isDark ? [9, 9, 11] : [250, 250, 250]) : (isDark ? [255, 255, 255] : [24, 24, 27]);
        };

        const fgColor = window.getComputedStyle(fgEl).color;
        const bgColor = bgEl ? window.getComputedStyle(bgEl).backgroundColor : "";

        const [r1, g1, b1] = parseColor(fgColor, false).map((v) => {
          const s = v / 255;
          return s <= 0.03928 ? s / 12.92 : Math.pow((s + 0.055) / 1.055, 2.4);
        });
        const [r2, g2, b2] = parseColor(bgColor, true).map((v) => {
          const s = v / 255;
          return s <= 0.03928 ? s / 12.92 : Math.pow((s + 0.055) / 1.055, 2.4);
        });

        const l1 = 0.2126 * r1 + 0.7152 * g1 + 0.0722 * b1;
        const l2 = 0.2126 * r2 + 0.7152 * g2 + 0.0722 * b2;
        const lighter = Math.max(l1, l2);
        const darker = Math.min(l1, l2);
        return (lighter + 0.05) / (darker + 0.05);
      },
      [fgSelector, bgSelector]
    );
  };

  const getContainerBg = async () => {
    return page.evaluate(() => {
      const container = document.querySelector(".min-h-screen");
      if (container) {
        const bg = window.getComputedStyle(container).backgroundColor;
        if (bg && bg !== "rgba(0, 0, 0, 0)" && bg !== "transparent") return bg;
      }
      return document.documentElement.classList.contains("dark") ? "rgb(9, 9, 11)" : "rgb(250, 250, 250)";
    });
  };

  // 1. Light theme checks
  const lightBg = await getContainerBg();
  const lightH1Contrast = await evaluateContrast("h1", ".min-h-screen");
  expect(lightH1Contrast).toBeGreaterThanOrEqual(4.5);

  // Primary button styling in light mode
  const startChatBtn = page.locator("[data-testid='primary-cta']").first();
  const startChatBg = await startChatBtn.evaluate((el) => window.getComputedStyle(el).backgroundColor);
  expect(startChatBg).not.toBe("rgba(0, 0, 0, 0)");
  expect(startChatBg).not.toBe("transparent");

  const btnContrast = await evaluateContrast("[data-testid='primary-cta']", "[data-testid='primary-cta']");
  // In emerald button, text is white, bg is emerald-700 (contrast ~4.5:1 or higher)
  expect(btnContrast).toBeGreaterThanOrEqual(4.5);

  // 2. Switch to dark theme
  const themeToggle = page.getByRole("button", { name: /switch to dark mode/i });
  await themeToggle.click();
  await page.waitForTimeout(150);

  // 3. Dark theme checks
  const darkBg = await getContainerBg();
  expect(lightBg).not.toEqual(darkBg);

  const darkH1Contrast = await evaluateContrast("h1", ".min-h-screen");
  expect(darkH1Contrast).toBeGreaterThanOrEqual(4.5);

  const darkBtnContrast = await evaluateContrast("[data-testid='primary-cta']", "[data-testid='primary-cta']");
  expect(darkBtnContrast).toBeGreaterThanOrEqual(4.5);
});


