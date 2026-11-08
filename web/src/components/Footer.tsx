import React from "react";
import { PhoneCall, ShieldCheck, Heart } from "lucide-react";
import type { LanguageCode } from "../i18n/translations";
import { translations } from "../i18n/translations";

interface FooterProps {
  language: LanguageCode;
}

export const Footer: React.FC<FooterProps> = ({ language }) => {
  const t = translations[language] || translations.en;

  return (
    <footer className="mt-auto bg-zinc-50 dark:bg-zinc-950 border-t border-zinc-200 dark:border-zinc-800 transition-colors">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
        {/* Emergency Callout in Footer */}
        <div className="p-4 bg-emerald-50 dark:bg-emerald-950/60 border border-emerald-200 dark:border-emerald-800/80 rounded-xl flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-3 text-emerald-900 dark:text-emerald-200">
            <ShieldCheck className="w-6 h-6 flex-shrink-0 text-emerald-600 dark:text-emerald-400" aria-hidden="true" />
            <p className="text-sm font-medium leading-snug">
              Official Indian Public Health Awareness &middot; Sources strictly from MoHFW (*.gov.in), ICMR, and WHO.
            </p>
          </div>
          <a
            href="tel:108"
            className="inline-flex items-center gap-2 px-4 py-2 bg-red-600 hover:bg-red-700 text-white font-bold text-sm rounded-lg shadow-sm transition focus:outline-none focus:ring-2 focus:ring-red-500 flex-shrink-0"
            aria-label="Call 108 national medical helpline"
          >
            <PhoneCall className="w-4 h-4" aria-hidden="true" />
            <span>Emergency: Call 108</span>
          </a>
        </div>

        {/* Disclaimer Note */}
        <div className="text-center space-y-2 text-xs text-zinc-500 dark:text-zinc-400">
          <p className="max-w-3xl mx-auto leading-relaxed">
            <strong className="text-zinc-700 dark:text-zinc-300">Disclaimer:</strong> {t.disclaimer}
          </p>
          <p className="flex items-center justify-center gap-1">
            Built with <Heart className="w-3.5 h-3.5 text-red-500 fill-red-500 inline" aria-hidden="true" /> for rural & semi-urban community awareness &middot; Associated with SIH25049.
          </p>
        </div>
      </div>
    </footer>
  );
};

