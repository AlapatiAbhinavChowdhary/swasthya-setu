import React from "react";
import { Link } from "react-router-dom";
import {
  MessageSquare,
  ShieldCheck,
  FileText,
  Sparkles,
  ArrowRight,
  Syringe,
  AlertTriangle,
  Hospital,
} from "lucide-react";
import type { LanguageCode } from "../i18n/translations";
import { translations } from "../i18n/translations";

interface HomeProps {
  language: LanguageCode;
}

export const Home: React.FC<HomeProps> = ({ language }) => {
  const t = translations[language] || translations.en;

  const quickPrompts = [
    { text: "What are the early symptoms of malaria?", text_hi: "मलेरिया के शुरुआती लक्षण क्या हैं?" },
    { text: "How is tuberculosis treated in simple words?", text_hi: "टीबी का इलाज आसान भाषा में कैसे होता है?" },
    { text: "Which vaccines are due at 9 months?", text_hi: "9 महीने के बच्चे को कौन से टीके लगते हैं?" },
    { text: "How to prepare oral rehydration salts (ORS)?", text_hi: "दस्त में ओआरएस का घोल कैसे बनाना चाहिए?" },
    { text: "What are the warning signs of severe dengue?", text_hi: "डेंगू के गंभीर खतरे के संकेत क्या हैं?" },
    { text: "What is the first aid for snakebite?", text_hi: "सांप के काटने पर क्या प्राथमिक उपचार करना चाहिए?" },
  ];

  return (
    <div className="space-y-12 py-6">
      {/* Hero Section */}
      <section className="text-center max-w-3xl mx-auto space-y-5 px-4">
        <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-100 dark:bg-emerald-950/80 text-emerald-800 dark:text-emerald-300 text-xs sm:text-sm font-semibold border border-emerald-300 dark:border-emerald-800 shadow-sm">
          <Sparkles className="w-4 h-4 text-emerald-600 dark:text-emerald-400" aria-hidden="true" />
          <span>Grounded Public Health Assistant &middot; SIH25049</span>
        </div>

        <h1 className="text-3xl sm:text-5xl font-extrabold text-zinc-900 dark:text-white tracking-tight leading-tight">
          {t.appName}
        </h1>

        <p className="text-lg sm:text-xl text-zinc-600 dark:text-zinc-300 font-normal leading-relaxed">
          {t.tagline}
        </p>

        {/* CTA Buttons */}
        <div className="flex flex-wrap items-center justify-center gap-4 pt-2">
          <Link
            to="/chat"
            data-testid="primary-cta"
            className="inline-flex items-center gap-2 px-6 py-3.5 bg-emerald-700 hover:bg-emerald-800 text-white font-bold text-base rounded-xl shadow-md focus:outline-none focus:ring-4 focus:ring-emerald-400 transition"
          >
            <MessageSquare className="w-5 h-5" aria-hidden="true" />
            <span>Start Awareness Chat</span>
            <ArrowRight className="w-4 h-4 ml-1" aria-hidden="true" />
          </Link>
          <Link
            to="/diseases"
            className="inline-flex items-center gap-2 px-5 py-3.5 bg-white dark:bg-zinc-800 border border-zinc-300 dark:border-zinc-700 hover:bg-zinc-50 dark:hover:bg-zinc-700 text-zinc-800 dark:text-zinc-200 font-semibold text-base rounded-xl shadow-sm focus:outline-none focus:ring-4 focus:ring-zinc-400 transition"
          >
            <ShieldCheck className="w-5 h-5 text-emerald-600 dark:text-emerald-400" aria-hidden="true" />
            <span>Browse 30 Topics</span>
          </Link>
        </div>
      </section>

      {/* Honest Scope & Limits Card */}
      <section className="max-w-4xl mx-auto px-4">
        <div className="bg-amber-50/70 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-800/80 rounded-2xl p-6 shadow-sm">
          <div className="flex items-start gap-3.5">
            <ShieldCheck className="w-6 h-6 text-amber-600 dark:text-amber-400 flex-shrink-0 mt-0.5" aria-hidden="true" />
            <div className="space-y-2 text-sm text-zinc-700 dark:text-zinc-300">
              <h2 className="text-base font-bold text-amber-900 dark:text-amber-300">
                Honest Safety Boundaries & Scope
              </h2>
              <ul className="list-disc pl-5 space-y-1">
                <li>
                  <strong>Awareness Only:</strong> We explain official disease symptoms, prevention, and vaccination schedules.
                </li>
                <li>
                  <strong>No Prescriptions or Doses:</strong> We never give milligram doses, tablet counts, or individualized drug prescriptions.
                </li>
                <li>
                  <strong>Deterministic Emergency Card:</strong> Severe signals (vomiting blood, breathing difficulties, convulsions) immediately display emergency assistance with <strong>108</strong>.
                </li>
                <li>
                  <strong>Official Sources Only:</strong> Strictly verified from Ministry of Health and Family Welfare (*.gov.in), ICMR, and WHO.
                </li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* Quick-Start Prompts */}
      <section className="max-w-4xl mx-auto px-4 space-y-4">
        <h2 className="text-lg font-bold text-zinc-900 dark:text-white flex items-center gap-2">
          <FileText className="w-5 h-5 text-emerald-600 dark:text-emerald-400" aria-hidden="true" />
          <span>{t.quickQuestionsTitle}</span>
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {quickPrompts.map((q, idx) => {
            const promptText = language === "hi" ? q.text_hi : q.text;
            return (
              <Link
                key={idx}
                to={`/chat?q=${encodeURIComponent(promptText)}`}
                className="p-4 bg-white dark:bg-zinc-800 border border-zinc-200 dark:border-zinc-700/80 rounded-xl hover:border-emerald-500 dark:hover:border-emerald-500 hover:shadow-md transition text-left group focus:outline-none focus:ring-2 focus:ring-emerald-500"
              >
                <div className="flex items-center justify-between gap-2">
                  <span className="text-sm font-medium text-zinc-800 dark:text-zinc-200 group-hover:text-emerald-700 dark:group-hover:text-emerald-300">
                    "{promptText}"
                  </span>
                  <ArrowRight className="w-4 h-4 text-zinc-400 group-hover:text-emerald-600 transition flex-shrink-0" aria-hidden="true" />
                </div>
              </Link>
            );
          })}
        </div>
      </section>

      {/* Feature Highlights Grid */}
      <section className="max-w-5xl mx-auto px-4">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="p-6 bg-white dark:bg-zinc-800/80 rounded-2xl border border-zinc-200 dark:border-zinc-700/70 shadow-sm space-y-3">
            <div className="p-2.5 bg-blue-100 dark:bg-blue-950/70 rounded-xl w-fit text-blue-600 dark:text-blue-400">
              <Syringe className="w-6 h-6" aria-hidden="true" />
            </div>
            <h3 className="text-lg font-bold text-zinc-900 dark:text-white">National Immunization</h3>
            <p className="text-sm text-zinc-600 dark:text-zinc-400 leading-relaxed">
              Explore age-wise vaccine milestones from birth to 16 years, with Vitamin A supplements clearly distinguished.
            </p>
            <Link to="/vaccination" className="inline-flex items-center text-sm font-semibold text-emerald-600 dark:text-emerald-400 hover:underline">
              View Schedule &rarr;
            </Link>
          </div>

          <div className="p-6 bg-white dark:bg-zinc-800/80 rounded-2xl border border-zinc-200 dark:border-zinc-700/70 shadow-sm space-y-3">
            <div className="p-2.5 bg-amber-100 dark:bg-amber-950/70 rounded-xl w-fit text-amber-600 dark:text-amber-400">
              <AlertTriangle className="w-6 h-6" aria-hidden="true" />
            </div>
            <h3 className="text-lg font-bold text-zinc-900 dark:text-white">Outbreak Alerts (Demo)</h3>
            <p className="text-sm text-zinc-600 dark:text-zinc-400 leading-relaxed">
              Demonstration vector and waterborne alerts by district, with links to the Integrated Disease Surveillance Programme.
            </p>
            <Link to="/alerts" className="inline-flex items-center text-sm font-semibold text-emerald-600 dark:text-emerald-400 hover:underline">
              Check Alerts &rarr;
            </Link>
          </div>

          <div className="p-6 bg-white dark:bg-zinc-800/80 rounded-2xl border border-zinc-200 dark:border-zinc-700/70 shadow-sm space-y-3">
            <div className="p-2.5 bg-red-100 dark:bg-red-950/70 rounded-xl w-fit text-red-600 dark:text-red-400">
              <Hospital className="w-6 h-6" aria-hidden="true" />
            </div>
            <h3 className="text-lg font-bold text-zinc-900 dark:text-white">Healthcare Facilities</h3>
            <p className="text-sm text-zinc-600 dark:text-zinc-400 leading-relaxed">
              Search sample public health facilities by district and state, with direct emergency 108 access.
            </p>
            <Link to="/facilities" className="inline-flex items-center text-sm font-semibold text-emerald-600 dark:text-emerald-400 hover:underline">
              Search Facilities &rarr;
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
};
