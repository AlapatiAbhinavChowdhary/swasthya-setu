import React, { useState } from "react";
import { Link, useLocation } from "react-router-dom";
import {
  HeartPulse,
  MessageSquare,
  Shield,
  Syringe,
  AlertTriangle,
  Hospital,
  Info,
  Lock,
  Sun,
  Moon,
  Globe,
  Menu,
  X,
} from "lucide-react";
import type { LanguageCode } from "../i18n/translations";
import { translations } from "../i18n/translations";

interface NavbarProps {
  language: LanguageCode;
  onLanguageChange: (lang: LanguageCode) => void;
  darkMode: boolean;
  onToggleDarkMode: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  language,
  onLanguageChange,
  darkMode,
  onToggleDarkMode,
}) => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const location = useLocation();
  const t = translations[language] || translations.en;

  const navLinks = [
    { to: "/", label: t.navHome, icon: HeartPulse },
    { to: "/chat", label: t.navChat, icon: MessageSquare },
    { to: "/diseases", label: t.navDiseases, icon: Shield },
    { to: "/vaccination", label: t.navVaccination, icon: Syringe },
    { to: "/alerts", label: t.navAlerts, icon: AlertTriangle },
    { to: "/facilities", label: t.navFacilities, icon: Hospital },
    { to: "/about", label: t.navAbout, icon: Info },
    { to: "/admin", label: t.navAdmin, icon: Lock },
  ];

  const languages: { code: LanguageCode; label: string }[] = [
    { code: "en", label: "English" },
    { code: "hi", label: "हिन्दी" },
    { code: "or", label: "ଓଡ଼ିଆ (Draft)" },
    { code: "pa", label: "ਪੰਜਾਬੀ (Draft)" },
  ];

  return (
    <header className="sticky top-0 z-40 bg-white/95 dark:bg-zinc-900/95 backdrop-blur border-b border-zinc-200 dark:border-zinc-800 transition-colors">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Brand */}
          <Link
            to="/"
            className="flex items-center gap-2.5 font-bold text-xl text-emerald-700 dark:text-emerald-400 focus:outline-none focus:ring-2 focus:ring-emerald-500 rounded-lg p-1"
            aria-label="Swasthya Setu Home"
          >
            <div className="p-1.5 bg-emerald-100 dark:bg-emerald-950/80 rounded-lg text-emerald-600 dark:text-emerald-400">
              <HeartPulse className="w-6 h-6" aria-hidden="true" />
            </div>
            <span className="tracking-tight">{t.appName}</span>
          </Link>

          {/* Desktop Navigation Links */}
          <nav className="hidden lg:flex items-center gap-1" aria-label="Main Navigation">
            {navLinks.map((link) => {
              const Icon = link.icon;
              const isActive = location.pathname === link.to;
              return (
                <Link
                  key={link.to}
                  to={link.to}
                  className={`inline-flex items-center gap-1.5 px-3 py-2 text-sm font-medium rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-emerald-500 ${
                    isActive
                      ? "bg-emerald-50 text-emerald-800 dark:bg-emerald-950/80 dark:text-emerald-300 font-semibold"
                      : "text-zinc-600 hover:text-zinc-900 dark:text-zinc-300 dark:hover:text-zinc-100 hover:bg-zinc-100 dark:hover:bg-zinc-800"
                  }`}
                  aria-current={isActive ? "page" : undefined}
                >
                  <Icon className="w-4 h-4" aria-hidden="true" />
                  <span>{link.label}</span>
                </Link>
              );
            })}
          </nav>

          {/* Right Controls: Language & Theme & Mobile Hamburger */}
          <div className="flex items-center gap-2">
            {/* Language Selector */}
            <div className="relative inline-flex items-center">
              <label htmlFor="language-select" className="sr-only">
                Select language
              </label>
              <Globe className="w-4 h-4 text-zinc-400 absolute left-2.5 pointer-events-none" aria-hidden="true" />
              <select
                id="language-select"
                value={language}
                onChange={(e) => onLanguageChange(e.target.value as LanguageCode)}
                className="pl-8 pr-3 py-1.5 text-xs sm:text-sm font-medium bg-zinc-50 dark:bg-zinc-800 border border-zinc-300 dark:border-zinc-700 rounded-lg text-zinc-800 dark:text-zinc-200 focus:outline-none focus:ring-2 focus:ring-emerald-500 cursor-pointer"
                aria-label="Select display and response language"
              >
                {languages.map((l) => (
                  <option key={l.code} value={l.code}>
                    {l.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Dark / Light Toggle */}
            <button
              type="button"
              onClick={onToggleDarkMode}
              className="p-2 text-zinc-500 hover:text-zinc-900 dark:text-zinc-400 dark:hover:text-zinc-100 rounded-lg hover:bg-zinc-100 dark:hover:bg-zinc-800 focus:outline-none focus:ring-2 focus:ring-emerald-500 transition-colors"
              aria-label={darkMode ? "Switch to light mode" : "Switch to dark mode"}
              title={darkMode ? "Light mode" : "Dark mode"}
            >
              {darkMode ? <Sun className="w-5 h-5 text-amber-400" aria-hidden="true" /> : <Moon className="w-5 h-5" aria-hidden="true" />}
            </button>

            {/* Mobile Menu Button */}
            <button
              type="button"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="lg:hidden p-2 text-zinc-600 dark:text-zinc-300 hover:bg-zinc-100 dark:hover:bg-zinc-800 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500"
              aria-expanded={mobileMenuOpen}
              aria-label="Toggle navigation menu"
            >
              {mobileMenuOpen ? <X className="w-6 h-6" aria-hidden="true" /> : <Menu className="w-6 h-6" aria-hidden="true" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Menu Dropdown */}
      {mobileMenuOpen && (
        <nav
          className="lg:hidden px-4 pt-2 pb-4 space-y-1 bg-white dark:bg-zinc-900 border-b border-zinc-200 dark:border-zinc-800 shadow-md animate-in slide-in-from-top-2"
          aria-label="Mobile Navigation"
        >
          {navLinks.map((link) => {
            const Icon = link.icon;
            const isActive = location.pathname === link.to;
            return (
              <Link
                key={link.to}
                to={link.to}
                onClick={() => setMobileMenuOpen(false)}
                className={`flex items-center gap-3 px-3 py-2.5 text-base font-medium rounded-lg transition-colors ${
                  isActive
                    ? "bg-emerald-50 text-emerald-800 dark:bg-emerald-950/80 dark:text-emerald-300 font-bold"
                    : "text-zinc-700 dark:text-zinc-300 hover:bg-zinc-100 dark:hover:bg-zinc-800"
                }`}
                aria-current={isActive ? "page" : undefined}
              >
                <Icon className="w-5 h-5 text-emerald-600 dark:text-emerald-400" aria-hidden="true" />
                <span>{link.label}</span>
              </Link>
            );
          })}
        </nav>
      )}
    </header>
  );
};

