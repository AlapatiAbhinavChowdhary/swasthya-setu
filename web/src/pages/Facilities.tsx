import React, { useState, useEffect } from "react";
import {
  Hospital,
  PhoneCall,
  Search,
  MapPin,
  ExternalLink,
  AlertCircle,
} from "lucide-react";
import type { LanguageCode } from "../i18n/translations";
import { translations } from "../i18n/translations";
import { api } from "../api/client";
import type { FacilitiesResponse, Facility } from "../types";

interface FacilitiesProps {
  language: LanguageCode;
}

export const Facilities: React.FC<FacilitiesProps> = ({ language }) => {
  const t = translations[language] || translations.en;
  const [data, setData] = useState<FacilitiesResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [districtFilter, setDistrictFilter] = useState("");
  const [stateFilter, setStateFilter] = useState("");

  const fetchFacilities = (district?: string, state?: string) => {
    setLoading(true);
    api
      .getFacilities({
        district: (district !== undefined ? district : districtFilter).trim() || undefined,
        state: (state !== undefined ? state : stateFilter).trim() || undefined,
        language,
      })
      .then((res) => {
        setData(res);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message || "Failed to load facility directory.");
        setLoading(false);
      });
  };

  useEffect(() => {
    let mounted = true;
    api
      .getFacilities({
        district: districtFilter.trim() || undefined,
        state: stateFilter.trim() || undefined,
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
          setError(err.message || "Failed to load facility directory.");
          setLoading(false);
        }
      });
    return () => {
      mounted = false;
    };
  }, [language, districtFilter, stateFilter]);

  return (
    <div className="space-y-8 py-4 max-w-5xl mx-auto">
      {/* Header */}
      <div className="space-y-3">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-100 dark:bg-blue-950/80 border border-blue-300 dark:border-blue-800 text-blue-900 dark:text-blue-300 text-xs font-semibold">
          <Hospital className="w-3.5 h-3.5" aria-hidden="true" />
          <span>Health Facility Locator (Prototype)</span>
        </div>
        <h1 className="text-3xl font-extrabold text-zinc-900 dark:text-white tracking-tight">
          Public Health Facilities & Emergency Directory
        </h1>
        <p className="text-zinc-600 dark:text-zinc-300 max-w-3xl">
          Demonstrates how community members can quickly discover nearby public healthcare tiers
          (Sub-Centres, PHCs, CHCs, and District Hospitals).
        </p>
      </div>

      {/* Emergency Box */}
      <div className="p-6 rounded-2xl bg-gradient-to-r from-red-600 to-rose-700 text-white shadow-md flex flex-col sm:flex-row items-center justify-between gap-6">
        <div className="space-y-1 text-center sm:text-left">
          <div className="inline-flex items-center gap-2 px-2.5 py-0.5 rounded-full bg-white/20 text-xs font-bold uppercase tracking-wider">
            <span>24x7 Free Ambulance Helpline</span>
          </div>
          <h2 className="text-2xl font-black tracking-tight">National Emergency: Call 108</h2>
          <p className="text-red-100 text-sm max-w-xl">
            Toll-free across India for emergency medical transportation, road trauma, maternal emergencies, and acute illness.
          </p>
        </div>

        <a
          href="tel:108"
          className="inline-flex items-center gap-2.5 px-6 py-3.5 rounded-xl bg-white text-red-700 hover:bg-red-50 font-extrabold text-base shadow transition focus:outline-none focus:ring-4 focus:ring-white/50 flex-shrink-0"
          aria-label="Call 108 Emergency Helpline now"
        >
          <PhoneCall className="w-5 h-5 animate-pulse" aria-hidden="true" />
          <span>Call 108 Now</span>
        </a>
      </div>

      {/* Prominent Sample Banner */}
      <div className="p-4 sm:p-5 rounded-2xl bg-zinc-100 dark:bg-zinc-800/80 border border-zinc-200 dark:border-zinc-700 text-zinc-800 dark:text-zinc-200 shadow-sm space-y-3">
        <div className="flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-zinc-500 dark:text-zinc-400 flex-shrink-0 mt-0.5" aria-hidden="true" />
          <div className="space-y-1">
            <h3 className="text-sm font-bold text-zinc-900 dark:text-zinc-100">
              SAMPLE DATA &mdash; Illustrative Directory
            </h3>
            <p className="text-xs sm:text-sm text-zinc-600 dark:text-zinc-400 leading-relaxed">
              {t.sampleFacilitiesBanner} Official real-time registries for every government hospital
              and clinic in India are cataloged on the Ayushman Bharat Digital Mission (ABDM)
              Health Facility Registry.
            </p>
          </div>
        </div>

        <div className="pt-2 border-t border-zinc-200 dark:border-zinc-700 flex items-center justify-end">
          <a
            href="https://facility.abdm.gov.in"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-zinc-200 hover:bg-zinc-300 dark:bg-zinc-700 dark:hover:bg-zinc-600 text-zinc-800 dark:text-zinc-100 font-semibold text-xs transition"
          >
            <span>Visit Official Health Facility Registry (facility.abdm.gov.in)</span>
            <ExternalLink className="w-3.5 h-3.5" aria-hidden="true" />
          </a>
        </div>
      </div>

      {/* Filter inputs */}
      <div className="p-4 sm:p-5 rounded-2xl bg-white dark:bg-zinc-800/90 border border-zinc-200 dark:border-zinc-700/80 shadow-sm space-y-3">
        <div className="flex items-center gap-2 text-zinc-700 dark:text-zinc-300 font-semibold text-sm">
          <Search className="w-4 h-4 text-emerald-600 dark:text-emerald-400" aria-hidden="true" />
          <span>Search Sample Facilities</span>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          <div>
            <label htmlFor="facilities-district-filter" className="block text-xs text-zinc-500 dark:text-zinc-400 mb-1">District</label>
            <input
              id="facilities-district-filter"
              type="text"
              value={districtFilter}
              onChange={(e) => setDistrictFilter(e.target.value)}
              placeholder="e.g. Gorakhpur, Patna"
              className="w-full px-3 py-2 rounded-lg border border-zinc-300 dark:border-zinc-700 bg-white dark:bg-zinc-900 text-zinc-900 dark:text-zinc-100 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
            />
          </div>
          <div>
            <label htmlFor="facilities-state-filter" className="block text-xs text-zinc-500 dark:text-zinc-400 mb-1">State</label>
            <input
              id="facilities-state-filter"
              type="text"
              value={stateFilter}
              onChange={(e) => setStateFilter(e.target.value)}
              placeholder="e.g. Uttar Pradesh, Bihar"
              className="w-full px-3 py-2 rounded-lg border border-zinc-300 dark:border-zinc-700 bg-white dark:bg-zinc-900 text-zinc-900 dark:text-zinc-100 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
            />
          </div>
          <div className="flex items-end">
            <button
              onClick={() => fetchFacilities()}
              className="w-full px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white font-semibold text-sm transition focus:outline-none focus:ring-2 focus:ring-emerald-500 shadow-sm"
            >
              Search
            </button>
          </div>
        </div>
      </div>

      {/* Facilities Grid */}
      {loading ? (
        <div className="py-16 text-center text-zinc-500 dark:text-zinc-400 animate-pulse">
          Loading sample facilities...
        </div>
      ) : error ? (
        <div className="p-4 bg-red-50 dark:bg-red-950/60 border border-red-200 dark:border-red-800 rounded-xl text-red-700 dark:text-red-300 text-sm">
          {error}
        </div>
      ) : !data || data.facilities.length === 0 ? (
        <div className="p-8 text-center text-zinc-500 dark:text-zinc-400 space-y-2">
          <p className="font-semibold">No sample facilities found matching the criteria.</p>
          <button
            onClick={() => {
              setDistrictFilter("");
              setStateFilter("");
              fetchFacilities("", "");
            }}
            className="text-emerald-600 dark:text-emerald-400 font-semibold underline text-sm"
          >
            Clear filters
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          <div className="text-xs text-zinc-500 dark:text-zinc-400 px-1">
            Displaying {data.facilities.length} facility entries &middot; {data.disclaimer}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {data.facilities.map((fac: Facility) => (
              <div
                key={fac.id}
                className="p-5 rounded-2xl bg-white dark:bg-zinc-800/90 border border-zinc-200 dark:border-zinc-700/80 shadow-sm space-y-3 flex flex-col justify-between"
              >
                <div className="space-y-2">
                  <div className="flex items-start justify-between gap-2">
                    <span className="px-2.5 py-0.5 rounded-full text-xs font-bold uppercase bg-zinc-100 text-zinc-700 dark:bg-zinc-700 dark:text-zinc-300 border border-zinc-200 dark:border-zinc-600">
                      {fac.type}
                    </span>
                    <span className="px-2 py-0.5 rounded text-xs font-semibold bg-amber-50 text-amber-800 dark:bg-amber-950/80 dark:text-amber-300 border border-amber-200 dark:border-amber-800">
                      {fac.label || "Sample"}
                    </span>
                  </div>

                  <h3 className="text-lg font-bold text-zinc-900 dark:text-white">
                    {fac.name}
                  </h3>

                  <div className="flex items-start gap-1.5 text-xs text-zinc-500 dark:text-zinc-400">
                    <MapPin className="w-3.5 h-3.5 text-zinc-400 mt-0.5 flex-shrink-0" aria-hidden="true" />
                    <span>
                      {fac.address}, {fac.district}, {fac.state}
                    </span>
                  </div>
                </div>

                <div className="pt-3 border-t border-zinc-100 dark:border-zinc-700/60 flex items-center justify-between text-xs">
                  <span className="text-zinc-500 dark:text-zinc-400">
                    Helpline: <strong className="text-zinc-700 dark:text-zinc-300">{fac.phone}</strong>
                  </span>
                  <a
                    href="tel:108"
                    className="inline-flex items-center gap-1 text-emerald-600 dark:text-emerald-400 font-semibold hover:underline"
                  >
                    <PhoneCall className="w-3 h-3" aria-hidden="true" />
                    <span>Ambulance 108</span>
                  </a>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
