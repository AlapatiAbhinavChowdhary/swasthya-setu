import React, { useState, useEffect } from "react";
import {
  Syringe,
  ShieldCheck,
  Calendar,
  Baby,
  Info,
} from "lucide-react";
import type { LanguageCode } from "../i18n/translations";
import { translations } from "../i18n/translations";
import { api } from "../api/client";
import type { VaccinationResponse, VaccinationItem } from "../types";

interface VaccinationProps {
  language: LanguageCode;
}

export const Vaccination: React.FC<VaccinationProps> = ({ language }) => {
  const t = translations[language] || translations.en;
  const [data, setData] = useState<VaccinationResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedAgeMonths, setSelectedAgeMonths] = useState<number | null>(null);

  const handleSelectAge = (months: number | null) => {
    setSelectedAgeMonths(months);
    setLoading(true);
  };

  useEffect(() => {
    let mounted = true;
    api
      .getVaccination(selectedAgeMonths)
      .then((res) => {
        if (mounted) {
          setData(res);
          setLoading(false);
        }
      })
      .catch((err) => {
        if (mounted) {
          setError(err.message || "Failed to load vaccination schedule.");
          setLoading(false);
        }
      });
    return () => {
      mounted = false;
    };
  }, [selectedAgeMonths]);

  const ageMilestones = [
    { label: "All Milestones", months: null },
    { label: "At Birth (0 m)", months: 0 },
    { label: "6 Weeks (1.5 m)", months: 1.5 },
    { label: "10 Weeks (2.5 m)", months: 2.5 },
    { label: "14 Weeks (3.5 m)", months: 3.5 },
    { label: "9–12 Months", months: 9 },
    { label: "16–24 Months", months: 18 },
    { label: "5–6 Years", months: 60 },
    { label: "10 Years", months: 120 },
    { label: "16 Years", months: 192 },
  ];

  return (
    <div className="space-y-8 py-4 max-w-5xl mx-auto">
      {/* Header */}
      <div className="space-y-3">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-50 dark:bg-emerald-950/60 border border-emerald-200 dark:border-emerald-800 text-emerald-800 dark:text-emerald-300 text-xs font-semibold">
          <Syringe className="w-3.5 h-3.5" aria-hidden="true" />
          <span>Official National Immunization Schedule</span>
        </div>
        <h1 className="text-3xl font-extrabold text-zinc-900 dark:text-white tracking-tight">
          Universal Immunization Schedule (UIP)
        </h1>
        <p className="text-zinc-600 dark:text-zinc-300 max-w-3xl">
          Based strictly on the official National Immunization Schedule published by the Ministry of
          Health and Family Welfare (MoHFW), Government of India. Provided free of charge at all
          government health centres, sub-centres, and Anganwadi sessions.
        </p>
      </div>

      {/* Age Milestone Picker */}
      <div className="p-4 sm:p-5 rounded-2xl bg-white dark:bg-zinc-800/90 border border-zinc-200 dark:border-zinc-700/80 shadow-sm space-y-3">
        <div className="flex items-center gap-2 text-zinc-700 dark:text-zinc-300 font-semibold text-sm">
          <Calendar className="w-4 h-4 text-emerald-600 dark:text-emerald-400" aria-hidden="true" />
          <span>{t.agePickerLabel}</span>
        </div>
        <div className="flex flex-wrap gap-2">
          {ageMilestones.map((m) => (
            <button
              key={m.label}
              onClick={() => handleSelectAge(m.months)}
              className={`px-3 py-1.5 rounded-lg text-xs sm:text-sm font-semibold transition focus:outline-none focus:ring-2 focus:ring-emerald-500 ${
                selectedAgeMonths === m.months
                  ? "bg-emerald-600 text-white shadow-sm"
                  : "bg-zinc-100 dark:bg-zinc-700 text-zinc-700 dark:text-zinc-300 hover:bg-zinc-200 dark:hover:bg-zinc-600"
              }`}
            >
              {m.label}
            </button>
          ))}
        </div>
      </div>

      {/* Schedule Table / Cards */}
      {loading ? (
        <div className="py-16 text-center text-zinc-500 dark:text-zinc-400 animate-pulse">
          Loading immunization schedule...
        </div>
      ) : error ? (
        <div className="p-4 bg-red-50 dark:bg-red-950/60 border border-red-200 dark:border-red-800 rounded-xl text-red-700 dark:text-red-300 text-sm">
          {error}
        </div>
      ) : !data || data.schedule.length === 0 ? (
        <div className="p-8 text-center text-zinc-500 dark:text-zinc-400 space-y-2">
          <p className="font-semibold">No vaccines found for this age milestone.</p>
          <button
            onClick={() => setSelectedAgeMonths(null)}
            className="text-emerald-600 dark:text-emerald-400 font-semibold underline text-sm"
          >
            Show all milestones
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          <div className="flex items-center justify-between text-xs text-zinc-500 dark:text-zinc-400 px-1">
            <span>Showing {data.schedule.length} milestone(s)</span>
            <span className="font-medium text-emerald-700 dark:text-emerald-300">
              {data.source_label}
            </span>
          </div>

          <div className="space-y-4">
            {data.schedule.map((item: VaccinationItem, idx: number) => {
              const hasSupplements =
                item.supplements && item.supplements.length > 0;
              return (
                <div
                  key={item.age_key || idx}
                  className="p-5 sm:p-6 rounded-2xl bg-white dark:bg-zinc-800/90 border border-zinc-200 dark:border-zinc-700/80 shadow-sm space-y-4"
                >
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-zinc-100 dark:border-zinc-700/60">
                    <div className="flex items-center gap-2">
                      <span className="p-2 rounded-lg bg-emerald-100 dark:bg-emerald-950/80 text-emerald-700 dark:text-emerald-300">
                        <Baby className="w-5 h-5" aria-hidden="true" />
                      </span>
                      <div>
                        <h2 className="text-lg font-bold text-zinc-900 dark:text-white">
                          {item.age}
                        </h2>
                        <p className="text-xs text-zinc-500 dark:text-zinc-400 font-medium">
                          Target Group: {item.target_group}
                        </p>
                      </div>
                    </div>
                  </div>

                  {/* Vaccines List */}
                  <div className="space-y-2">
                    <p className="text-xs font-bold text-zinc-500 dark:text-zinc-400 uppercase tracking-wider">
                      {t.vaccinesDueTitle}
                    </p>
                    <div className="flex flex-wrap gap-2">
                      {item.vaccines && item.vaccines.length > 0 ? (
                        item.vaccines.map((v, vIdx) => (
                          <span
                            key={vIdx}
                            className="px-3 py-1.5 rounded-lg text-sm font-semibold bg-emerald-50 dark:bg-emerald-950/70 text-emerald-900 dark:text-emerald-200 border border-emerald-200 dark:border-emerald-800"
                          >
                            {v}
                          </span>
                        ))
                      ) : (
                        <span className="text-xs text-zinc-500">None</span>
                      )}
                    </div>
                  </div>

                  {/* Supplements List - separated clearly with no dose! */}
                  {hasSupplements && (
                    <div className="p-3 rounded-xl bg-amber-50/80 dark:bg-amber-950/40 border border-amber-200/80 dark:border-amber-800/60 space-y-1.5">
                      <p className="text-xs font-bold text-amber-900 dark:text-amber-200 uppercase tracking-wider flex items-center gap-1.5">
                        <Info className="w-3.5 h-3.5" aria-hidden="true" />
                        <span>{t.supplementsTitle}</span>
                      </p>
                      <div className="flex flex-wrap gap-2">
                        {item.supplements!.map((s, sIdx) => (
                          <span
                            key={sIdx}
                            className="px-2.5 py-1 rounded-md text-xs font-medium bg-amber-100 text-amber-900 dark:bg-amber-900/60 dark:text-amber-200"
                          >
                            {s}
                          </span>
                        ))}
                      </div>
                      <p className="text-xs text-amber-800/90 dark:text-amber-300/80">
                        * Vitamin A is administered as a routine preventive nutritional supplement
                        at public immunization sessions; it is not an infectious vaccine.
                      </p>
                    </div>
                  )}

                  {/* Description / Schedule details */}
                  {item.description && (
                    <p className="text-xs sm:text-sm text-zinc-600 dark:text-zinc-300 leading-relaxed">
                      {item.description}
                    </p>
                  )}
                </div>
              );
            })}
          </div>

          {/* Footnotes */}
          {data.footnotes && Object.keys(data.footnotes).length > 0 && (
            <div className="p-5 rounded-2xl bg-zinc-50 dark:bg-zinc-850 border border-zinc-200 dark:border-zinc-800 space-y-2">
              <h3 className="text-xs font-bold uppercase tracking-wider text-zinc-500 dark:text-zinc-400">
                Official Programme Notes & Explanations
              </h3>
              <ul className="text-xs text-zinc-600 dark:text-zinc-400 space-y-1 list-disc list-inside">
                {Object.entries(data.footnotes).map(([k, v]) => (
                  <li key={k}>
                    <strong>{k}:</strong> {v}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* Safety Reminder */}
      <div className="p-4 bg-emerald-50 dark:bg-emerald-950/60 border border-emerald-200 dark:border-emerald-800 rounded-xl flex items-start gap-3 text-emerald-950 dark:text-emerald-200 text-xs sm:text-sm">
        <ShieldCheck className="w-5 h-5 flex-shrink-0 text-emerald-600 dark:text-emerald-400 mt-0.5" aria-hidden="true" />
        <div>
          <p className="font-bold">Village Health Sanitation & Nutrition Day (VHSND):</p>
          <p className="mt-0.5">
            Vaccination sessions are organized regularly in every village by your local ANM and
            ASHA workers. Bring your Mother & Child Protection (MCP) card to each session. In case of
            any illness or fever on the vaccination day, consult the ANM before vaccination.
          </p>
        </div>
      </div>
    </div>
  );
};
