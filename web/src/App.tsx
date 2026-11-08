import React, { useState, useEffect } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import type { LanguageCode } from "./i18n/translations";
import { Navbar } from "./components/Navbar";
import { Footer } from "./components/Footer";
import { Home } from "./pages/Home";
import { Chat } from "./pages/Chat";
import { Diseases } from "./pages/Diseases";
import { DiseaseDetail } from "./pages/DiseaseDetail";
import { Vaccination } from "./pages/Vaccination";
import { Alerts } from "./pages/Alerts";
import { Facilities } from "./pages/Facilities";
import { About } from "./pages/About";
import { Admin } from "./pages/Admin";

export const App: React.FC = () => {
  const [language, setLanguage] = useState<LanguageCode>(() => {
    const saved = localStorage.getItem("ss_language") as LanguageCode | null;
    return saved && ["en", "hi", "or", "pa"].includes(saved) ? saved : "en";
  });

  const [darkMode, setDarkMode] = useState<boolean>(() => {
    const saved = localStorage.getItem("ss_theme");
    if (saved) return saved === "dark";
    return window.matchMedia("(prefers-color-scheme: dark)").matches;
  });

  useEffect(() => {
    localStorage.setItem("ss_language", language);
    document.documentElement.lang = language;
  }, [language]);

  useEffect(() => {
    localStorage.setItem("ss_theme", darkMode ? "dark" : "light");
    if (darkMode) {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }
  }, [darkMode]);

  return (
    <BrowserRouter>
      <div className="min-h-screen flex flex-col bg-zinc-50 dark:bg-zinc-950 text-zinc-900 dark:text-zinc-100 transition-colors">
        <Navbar
          language={language}
          onLanguageChange={setLanguage}
          darkMode={darkMode}
          onToggleDarkMode={() => setDarkMode(!darkMode)}
        />
        <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <Routes>
            <Route path="/" element={<Home language={language} />} />
            <Route
              path="/chat"
              element={
                <Chat language={language} onLanguageChange={setLanguage} />
              }
            />
            <Route path="/diseases" element={<Diseases language={language} />} />
            <Route
              path="/diseases/:id"
              element={<DiseaseDetail language={language} />}
            />
            <Route
              path="/vaccination"
              element={<Vaccination language={language} />}
            />
            <Route path="/alerts" element={<Alerts language={language} />} />
            <Route
              path="/facilities"
              element={<Facilities language={language} />}
            />
            <Route path="/about" element={<About language={language} />} />
            <Route path="/admin" element={<Admin language={language} />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </main>
        <Footer language={language} />
      </div>
    </BrowserRouter>
  );
};

export default App;

