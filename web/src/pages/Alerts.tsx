import React, { useState, useEffect } from "react";
import {
  AlertTriangle,
  ExternalLink,
  ShieldAlert,
  Filter,
  Calendar,
  MapPin,
} from "lucide-react";
import type { LanguageCode } from "../i18n/translations";
import { translations } from "../i18n/translations";
import { api } from "../api/client";
import type { AlertsResponse, OutbreakAlert } from "../types";

interface AlertsProps {
  language: LanguageCode;
}

export const Alerts: React.FC<AlertsProps> = ({ language }) => {
  const t = translations[language] || translations.en;
  const [data, setData] = useState<AlertsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [districtFilter, setDistrictFilter] = useState("");
  const [diseaseFilter, setDiseaseFilter] = useState("");

  const fetchAlerts = (district?: string, disease?: string) => {
    setLoading(true);
    api
      .getAlerts({
        district: (district !== undefined ? district : districtFilter).trim() || undefined,
        disease: (disease !== undefined ? disease : diseaseFilter).trim() || undefined,
        language,
      })
      .then((res) => {
        setData(res);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message || "Failed to load outbreak advisories.");
        setLoading(false);
      });
  };

  useEffect(() => {
    let mounted = true;
    api
      .getAlerts({
        district: districtFilter.trim() || undefined,
        disease: diseaseFilter.trim() || undefined,
        language,
      })
      .then((res) => {
        if (mounted) {
          setData(res);
          setLoading(false);
        }
      })
      .catch((err) => {
        if (mounted) {
          setError(err.message || "Failed to load outbreak advisories.");
          setLoading(false);
        }
      });
    return () => {
      mounted = false;
    };
  }, [language, districtFilter, diseaseFilter]);

  return (
    <div className="space-y-8 py-4 max-w-5xl mx-auto">
      {/* Header */}
      <div className="space-y-3">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-100 dark:bg-amber-950/80 border border-amber-300 dark:border-amber-800 text-amber-900 dark:text-amber-300 text-xs font-semibold">
          <AlertTriangle className="w-3.5 h-3.5" aria-hidden="true" />
          <span>Simulated Community Surveillance Alerts</span>
        </div>
        <h1 className="text-3xl font-extrabold text-zinc-900 dark:text-white tracking-tight">
          Public Health & Outbreak Advisories
        </h1>
        <p className="text-zinc-600 dark:text-zinc-300 max-w-3xl">
          Seasonal advisories and outbreak alerts illustrate how district-level disease warnings
          can be communicated in local languages to rural communities.
        </p>
      </div>

      {/* Prominent DEMO Banner */}
      <div className="p-4 sm:p-5 rounded-2xl bg-amber-50 dark:bg-amber-950/60 border-2 border-amber-400 dark:border-amber-700/80 text-amber-950 dark:text-amber-200 shadow-sm space-y-3">
        <div className="flex items-start gap-3">
          <ShieldAlert className="w-6 h-6 text-amber-600 dark:text-amber-400 flex-shrink-0 mt-0.5" aria-hidden="true" />
          <div className="space-y-1">
            <h2 className="text-base font-bold text-amber-900 dark:text-amber-100">
              DEMONSTRATION ONLY &mdash; Not Live Clinical Surveillance
            </h2>
            <p className="text-xs sm:text-sm text-amber-900/90 dark:text-amber-200/90 leading-relaxed">
              {t.demoDataBanner} Live epidemic surveillance across India is maintained by the
              Integrated Disease Surveillance Programme (IDSP) under the National Centre for
              Disease Control (NCDC).
            </p>
          </div>
        </div>

        <div className="pt-2 border-t border-amber-200 dark:border-amber-800/60 flex items-center justify-end">
          <a
            href="https://idsp.mohfw.gov.in"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-amber-600 hover:bg-amber-700 text-white font-bold text-xs transition shadow-sm"
          >
            <span>Visit Official IDSP Portal (idsp.mohfw.gov.in)</span>
            <ExternalLink className="w-3.5 h-3.5" aria-hidden="true" />
          </a>
        </div>
      </div>

      {/* Filters */}
      <div className="p-4 sm:p-5 rounded-2xl bg-white dark:bg-zinc-800/90 border border-zinc-200 dark:border-zinc-700/80 shadow-sm space-y-3">
        <div className="flex items-center gap-2 text-zinc-700 dark:text-zinc-300 font-semibold text-sm">
          <Filter className="w-4 h-4 text-emerald-600 dark:text-emerald-400" aria-hidden="true" />
          <span>Filter Advisories (Demo Records)</span>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          <div>
            <label htmlFor="alerts-district-filter" className="block text-xs text-zinc-500 dark:text-zinc-400 mb-1">
              District
            </label>
            <input
              id="alerts-district-filter"
              type="text"
              value={districtFilter}
              onChange={(e) => setDistrictFilter(e.target.value)}
              placeholder="e.g. Gorakhpur, Patna"
              className="w-full px-3 py-2 rounded-lg border border-zinc-300 dark:border-zinc-700 bg-white dark:bg-zinc-900 text-zinc-900 dark:text-zinc-100 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
            />
          </div>
          <div>
            <label htmlFor="alerts-disease-filter" className="block text-xs text-zinc-500 dark:text-zinc-400 mb-1">
              Disease
            </label>
            <input
              id="alerts-disease-filter"
              type="text"
              value={diseaseFilter}
              onChange={(e) => setDiseaseFilter(e.target.value)}
              placeholder="e.g. Dengue, Cholera"
              className="w-full px-3 py-2 rounded-lg border border-zinc-300 dark:border-zinc-700 bg-white dark:bg-zinc-900 text-zinc-900 dark:text-zinc-100 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
            />
          </div>
          <div className="flex items-end">
            <button
              onClick={() => fetchAlerts()}
              className="w-full px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white font-semibold text-sm transition focus:outline-none focus:ring-2 focus:ring-emerald-500 shadow-sm"
            >
              Apply Filter
            </button>
          </div>
        </div>
      </div>

      {/* Advisories Grid */}
      {loading ? (
        <div className="py-16 text-center text-zinc-500 dark:text-zinc-400 animate-pulse">
          Loading advisories...
        </div>
      ) : error ? (
        <div className="p-4 bg-red-50 dark:bg-red-950/60 border border-red-200 dark:border-red-800 rounded-xl text-red-700 dark:text-red-300 text-sm">
          {error}
        </div>
      ) : !data || data.alerts.length === 0 ? (
        <div className="p-8 text-center text-zinc-500 dark:text-zinc-400 space-y-2">
          <p className="font-semibold">No sample advisories found matching the criteria.</p>
          <button
            onClick={() => {
              setDistrictFilter("");
              setDiseaseFilter("");
              fetchAlerts("", "");
            }}
            className="text-emerald-600 dark:text-emerald-400 font-semibold underline text-sm"
          >
            Clear filters
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          <div className="text-xs text-zinc-500 dark:text-zinc-400 px-1">
            Displaying {data.alerts.length} advisory records &middot; {data.disclaimer}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {data.alerts.map((alert: OutbreakAlert) => (
              <div
                key={alert.id}
                className="p-5 rounded-2xl bg-white dark:bg-zinc-800/90 border border-zinc-200 dark:border-zinc-700/80 shadow-sm space-y-3 flex flex-col justify-between"
              >
                <div className="space-y-2">
                  <div className="flex items-start justify-between gap-2">
                    <span className="px-2.5 py-0.5 rounded-full text-xs font-bold uppercase bg-amber-100 text-amber-900 dark:bg-amber-950/80 dark:text-amber-300 border border-amber-300 dark:border-amber-800">
                      {alert.label || "Demo Entry"}
                    </span>
                    <span className="text-xs text-zinc-500 dark:text-zinc-400 flex items-center gap-1">
                      <Calendar className="w-3.5 h-3.5" aria-hidden="true" />
                      <span>{alert.date}</span>
                    </span>
                  </div>

                  <h3 className="text-lg font-bold text-zinc-900 dark:text-white">
                    {alert.disease} Advisory
                  </h3>

                  <div className="flex items-center gap-1.5 text-xs text-zinc-500 dark:text-zinc-400 font-medium">
                    <MapPin className="w-3.5 h-3.5 text-zinc-400" aria-hidden="true" />
                    <span>
                      {alert.district}, {alert.state}
                    </span>
                  </div>

                  <p className="text-sm text-zinc-700 dark:text-zinc-300 leading-relaxed pt-1">
                    {language === "hi" && alert.advisory_hi
                      ? alert.advisory_hi
                      : alert.advisory}
                  </p>
                </div>

                <div className="pt-3 border-t border-zinc-100 dark:border-zinc-700/60 text-xs text-zinc-400">
                  <span>Source Template: {alert.source}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
