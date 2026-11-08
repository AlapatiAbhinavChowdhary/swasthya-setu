import { describe, it, expect } from "vitest";
import { translations, type LanguageCode } from "../i18n/translations";

describe("i18n translations", () => {
  const languages: LanguageCode[] = ["en", "hi", "or", "pa"];

  it("provides dictionaries for en, hi, or, pa", () => {
    languages.forEach((lang) => {
      expect(translations[lang]).toBeDefined();
      expect(translations[lang].appName).toBeTruthy();
    });
    expect(translations.en.appName).toBe("Swasthya Setu");
    expect(translations.hi.appName).toBe("स्वास्थ्य सेतु");
  });

  it("has emergency guidance for all languages", () => {
    languages.forEach((lang) => {
      expect(translations[lang].emergencyAlert).toBeTruthy();
      expect(translations[lang].emergencyCallNow).toBeTruthy();
      expect(translations[lang].disclaimer).toBeTruthy();
    });
  });

  it("has depth tier descriptions", () => {
    expect(translations.en.depthBasic).toBe("Basic");
    expect(translations.en.depthGood).toBe("Good");
    expect(translations.en.depthDeep).toBe("Deep");
  });
});
