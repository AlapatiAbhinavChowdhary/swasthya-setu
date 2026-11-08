import React, { useState, useEffect, useMemo } from "react";
import { Link } from "react-router-dom";
import {
  Search,
  Shield,
  FileText,
  Calendar,
  AlertCircle,
  ChevronRight,
} from "lucide-react";
import type { LanguageCode } from "../i18n/translations";
import { translations } from "../i18n/translations";
import { api } from "../api/client";
import type { DiseaseCoverage } from "../types";

interface DiseasesProps {
  language: LanguageCode;
}

export const Diseases: React.FC<DiseasesProps> = ({ language }) => {
  const t = translations[language] || translations.en;
  const [diseases, setDiseases] = useState<DiseaseCoverage[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState<string>("all");

  useEffect(() => {
    let mounted = true;
    api
      .getCoverage()
      .then((res) => {
        if (mounted) {
          setDiseases(res.diseases || []);
          setLoading(false);
        }
      })
      .catch((err) => {
        if (mounted) {
          setError(err.message || "Failed to load disease directory.");
          setLoading(false);
        }
      });
    return () => {
      mounted = false;
    };
  }, []);

  const categories = [
    { id: "all", label: t.allCategories },
    { id: "infectious", label: t.infectious },
    { id: "maternal-child", label: t.maternalChild },
    { id: "non-communicable", label: t.nonCommunicable },
    { id: "environmental", label: t.environmental },
  ];

  const matchesCategory = (disease: DiseaseCoverage, cat: string) => {
    if (cat === "all") return true;
    const diseaseCat = disease.category || "";
    if (cat === "infectious") {
      return [
        "vector-borne",
        "respiratory",
        "water-food-borne",
        "vaccine-preventable",
      ].includes(diseaseCat);
    }
    if (cat === "maternal-child") {
      return ["maternal-child", "nutrition"].includes(diseaseCat);
    }
    if (cat === "non-communicable") {
      return diseaseCat === "non-communicable";
    }
    if (cat === "environmental") {
      return diseaseCat === "other";
    }
    return true;
  };

  const filteredDiseases = useMemo(() => {
    return diseases.filter((d) => {
      const q = search.toLowerCase().trim();
      const matchName =
        d.name_en.toLowerCase().includes(q) ||
        (d.name_hi && d.name_hi.toLowerCase().includes(q)) ||
        d.id.toLowerCase().includes(q);
      const matchCat = matchesCategory(d, category);
      return matchName && matchCat;
    });
  }, [diseases, search, category]);

  const getDepthBadge = (depth: string) => {
    switch (depth) {
      case "deep":
        return {
          label: t.depthDeep,
          desc: t.depthDeepDesc,
          className:
            "bg-emerald-100 text-emerald-800 dark:bg-emerald-950/80 dark:text-emerald-300 border-emerald-300 dark:border-emerald-800",
        };
      case "good":
        return {
          label: t.depthGood,
          desc: t.depthGoodDesc,
          className:
            "bg-blue-100 text-blue-800 dark:bg-blue-950/80 dark:text-blue-300 border-blue-300 dark:border-blue-800",
        };
      default:
        return {
          label: t.depthBasic,
          desc: t.depthBasicDesc,
          className:
            "bg-amber-100 text-amber-800 dark:bg-amber-950/80 dark:text-amber-300 border-amber-300 dark:border-amber-800",
        };
    }
  };

  return (
    <div className="space-y-8 py-4">
      {/* Header */}
      <div className="space-y-3">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-50 dark:bg-emerald-950/60 border border-emerald-200 dark:border-emerald-800 text-emerald-800 dark:text-emerald-300 text-xs font-semibold">
          <Shield className="w-3.5 h-3.5" aria-hidden="true" />
          <span>Official Public Health Directory</span>
        </div>
        <h1 className="text-3xl font-extrabold text-zinc-900 dark:text-white tracking-tight">
          Disease Directory & Coverage
        </h1>
        <p className="text-zinc-600 dark:text-zinc-300 max-w-3xl">
          Browse all covered diseases and health topics. Every topic is grounded exclusively in
          verified documents from the Government of India (MoHFW/ICMR) and the World Health
          Organization (WHO).
        </p>

        {/* General Disclaimer Banner */}
        <div className="p-3.5 bg-zinc-100 dark:bg-zinc-800/70 border border-zinc-200 dark:border-zinc-700/80 rounded-lg text-xs sm:text-sm text-zinc-700 dark:text-zinc-300 flex items-start gap-2.5">
          <AlertCircle className="w-4 h-4 text-emerald-600 dark:text-emerald-400 mt-0.5 flex-shrink-0" aria-hidden="true" />
          <div>
            <strong>General Information Only:</strong> Content provides community health awareness, prevention, and recognition of danger signs. Never replaces in-person medical evaluation.
          </div>
        </div>
      </div>

      {/* Search and Category Filters */}
      <div className="space-y-4">
        <div className="relative">
          <Search
            className="absolute left-3.5 top-1/2 -translate-y-1/2 w-5 h-5 text-zinc-400"
            aria-hidden="true"
          />
          <input
            type="search"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder={t.searchDiseasesPlaceholder}
            aria-label="Search diseases or health topics"
            className="w-full pl-11 pr-4 py-3 rounded-xl border border-zinc-300 dark:border-zinc-700 bg-white dark:bg-zinc-800/90 text-zinc-900 dark:text-zinc-100 placeholder-zinc-400 focus:outline-none focus:ring-2 focus:ring-emerald-500 shadow-sm"
          />
        </div>

        {/* Category Pills */}
        <div className="flex flex-wrap gap-2" role="tablist" aria-label="Disease Categories">
          {categories.map((cat) => (
            <button
              key={cat.id}
              role="tab"
              aria-selected={category === cat.id}
              onClick={() => setCategory(cat.id)}
              className={`px-3.5 py-1.5 rounded-lg text-sm font-medium transition focus:outline-none focus:ring-2 focus:ring-emerald-500 ${
                category === cat.id
                  ? "bg-emerald-600 text-white shadow-sm"
                  : "bg-zinc-100 dark:bg-zinc-800 text-zinc-700 dark:text-zinc-300 hover:bg-zinc-200 dark:hover:bg-zinc-700"
              }`}
            >
              {cat.label}
            </button>
          ))}
        </div>
      </div>

      {/* Directory Grid */}
      {loading ? (
        <div className="py-16 text-center text-zinc-500 dark:text-zinc-400 animate-pulse">
          Loading verified disease directory...
        </div>
      ) : error ? (
        <div className="p-4 bg-red-50 dark:bg-red-950/60 border border-red-200 dark:border-red-800 rounded-xl text-red-700 dark:text-red-300 text-sm">
          {error}
        </div>
      ) : filteredDiseases.length === 0 ? (
        <div className="py-12 text-center text-zinc-500 dark:text-zinc-400 space-y-2">
          <p className="font-semibold text-lg">No matching diseases or topics found</p>
          <p className="text-sm">Try broadening your search or selecting &ldquo;All Categories&rdquo;.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredDiseases.map((d) => {
            const depth = getDepthBadge(d.depth);
            return (
              <Link
                key={d.id}
                to={`/diseases/${d.id}`}
                className="group p-5 rounded-2xl bg-white dark:bg-zinc-800/90 border border-zinc-200 dark:border-zinc-700/80 hover:border-emerald-500 dark:hover:border-emerald-500 shadow-sm hover:shadow-md transition flex flex-col justify-between focus:outline-none focus:ring-2 focus:ring-emerald-500"
              >
                <div className="space-y-3">
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <h2 className="text-lg font-bold text-zinc-900 dark:text-white group-hover:text-emerald-600 dark:group-hover:text-emerald-400 transition">
                        {d.name_en}
                      </h2>
                      {d.name_hi && (
                        <p className="text-sm text-zinc-500 dark:text-zinc-400 font-medium">
                          {d.name_hi}
                        </p>
                      )}
                    </div>
                    {/* Depth Tier Badge with tooltip info */}
                    <span
                      title={depth.desc}
                      className={`px-2.5 py-0.5 rounded-full text-xs font-semibold border ${depth.className} flex-shrink-0`}
                    >
                      {depth.label}
                    </span>
                  </div>

                  <p className="text-xs text-zinc-500 dark:text-zinc-400 line-clamp-2">
                    {depth.desc}
                  </p>
                </div>

                <div className="pt-4 mt-4 border-t border-zinc-100 dark:border-zinc-700/60 flex items-center justify-between text-xs text-zinc-500 dark:text-zinc-400">
                  <div className="flex items-center gap-3">
                    <span className="flex items-center gap-1" title={`${d.documents} verified official documents`}>
                      <FileText className="w-3.5 h-3.5 text-zinc-400" aria-hidden="true" />
                      <span>{d.documents} {d.documents === 1 ? "doc" : "docs"}</span>
                    </span>
                    {d.newest_source_year && (
                      <span className="flex items-center gap-1" title={`Latest source publication: ${d.newest_source_year}`}>
                        <Calendar className="w-3.5 h-3.5 text-zinc-400" aria-hidden="true" />
                        <span>{d.newest_source_year}</span>
                      </span>
                    )}
                  </div>

                  <span className="inline-flex items-center gap-1 text-emerald-600 dark:text-emerald-400 font-semibold group-hover:translate-x-0.5 transition-transform">
                    <span>Details</span>
                    <ChevronRight className="w-4 h-4" aria-hidden="true" />
                  </span>
                </div>
              </Link>
            );
          })}
        </div>
      )}
    </div>
  );
};
