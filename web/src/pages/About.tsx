import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import {
  ShieldCheck,
  Lock,
  Sparkles,
  AlertTriangle,
} from "lucide-react";
import type { LanguageCode } from "../i18n/translations";
import { api } from "../api/client";
import type { CoverageResponse, DiseaseCoverage } from "../types";

interface AboutProps {
  language: LanguageCode;
}

export const About: React.FC<AboutProps> = () => {
  const [coverage, setCoverage] = useState<CoverageResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    api
      .getCoverage()
      .then((res) => {
        if (mounted) {
          setCoverage(res);
          setLoading(false);
        }
      })
      .catch(() => {
        if (mounted) setLoading(false);
      });
    return () => {
      mounted = false;
    };
  }, []);

  return (
    <div className="space-y-12 py-6 max-w-5xl mx-auto">
      {/* Header */}
      <section className="space-y-4">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-100 dark:bg-emerald-950/80 border border-emerald-300 dark:border-emerald-800 text-emerald-800 dark:text-emerald-300 text-xs font-semibold">
          <Sparkles className="w-3.5 h-3.5" aria-hidden="true" />
          <span>Smart India Hackathon &middot; Problem Statement SIH25049</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-extrabold text-zinc-900 dark:text-white tracking-tight">
          About Swasthya Setu
        </h1>
        <p className="text-lg text-zinc-600 dark:text-zinc-300 leading-relaxed max-w-3xl">
          Swasthya Setu (&ldquo;Health Bridge&rdquo;) is an open, verified public-health awareness
          assistant engineered specifically for rural and semi-urban communities across India. It
          bridges the gap between complex national medical guidelines and ordinary citizens through
          simple, local-language explanations.
        </p>
      </section>

      {/* Core Principles */}
      <section className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="p-6 rounded-2xl bg-white dark:bg-zinc-800/90 border border-zinc-200 dark:border-zinc-700/80 shadow-sm space-y-3">
          <div className="w-10 h-10 rounded-xl bg-emerald-100 dark:bg-emerald-950/80 text-emerald-700 dark:text-emerald-300 flex items-center justify-center">
            <ShieldCheck className="w-5 h-5" aria-hidden="true" />
          </div>
          <h2 className="text-lg font-bold text-zinc-900 dark:text-white">Strict Official Grounding</h2>
          <p className="text-sm text-zinc-600 dark:text-zinc-300 leading-relaxed">
            Every clinical sentence is verified against official publications from the Ministry of
            Health & Family Welfare (*.gov.in), NVBDCP, ICMR, and the World Health Organization
            (who.int). No random blogs or unverified summaries are ever ingested.
          </p>
        </div>

        <div className="p-6 rounded-2xl bg-white dark:bg-zinc-800/90 border border-zinc-200 dark:border-zinc-700/80 shadow-sm space-y-3">
          <div className="w-10 h-10 rounded-xl bg-red-100 dark:bg-red-950/80 text-red-700 dark:text-red-300 flex items-center justify-center">
            <AlertTriangle className="w-5 h-5" aria-hidden="true" />
          </div>
          <h2 className="text-lg font-bold text-zinc-900 dark:text-white">Deterministic Safety</h2>
          <p className="text-sm text-zinc-600 dark:text-zinc-300 leading-relaxed">
            Emergency warning signs (chest pain, severe breathlessness, profuse bleeding, snakebite)
            are intercepted by deterministic safety rules before any LLM inference, directing users
            to 108 emergency services without delay.
          </p>
        </div>

        <div className="p-6 rounded-2xl bg-white dark:bg-zinc-800/90 border border-zinc-200 dark:border-zinc-700/80 shadow-sm space-y-3">
          <div className="w-10 h-10 rounded-xl bg-blue-100 dark:bg-blue-950/80 text-blue-700 dark:text-blue-300 flex items-center justify-center">
            <Lock className="w-5 h-5" aria-hidden="true" />
          </div>
          <h2 className="text-lg font-bold text-zinc-900 dark:text-white">Privacy & Honesty</h2>
          <p className="text-sm text-zinc-600 dark:text-zinc-300 leading-relaxed">
            We store zero personally identifiable information (PII). We never diagnose, prescribe,
            or give drug dosages. Missing coverage is flagged transparently as &ldquo;Coming
            Soon&rdquo; rather than hallucinating medical facts.
          </p>
        </div>
      </section>

      {/* Live Coverage Table */}
      <section className="space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div>
            <h2 className="text-2xl font-bold text-zinc-900 dark:text-white">Live Disease Coverage Index</h2>
            <p className="text-sm text-zinc-600 dark:text-zinc-400">
              Generated live from the local vectorstore and official source registry ({coverage?.diseases?.length || 30} topics).
            </p>
          </div>
          <Link
            to="/diseases"
            className="text-sm font-semibold text-emerald-600 dark:text-emerald-400 hover:underline"
          >
            Explore Directory &rarr;
          </Link>
        </div>

        {loading ? (
          <div className="py-12 text-center text-zinc-500 animate-pulse">Loading live coverage...</div>
        ) : (
          <div className="overflow-x-auto rounded-2xl border border-zinc-200 dark:border-zinc-700/80 bg-white dark:bg-zinc-850 shadow-sm">
            <table className="w-full text-left text-sm">
              <thead className="bg-zinc-50 dark:bg-zinc-800/80 text-zinc-600 dark:text-zinc-300 border-b border-zinc-200 dark:border-zinc-700/80 font-bold text-xs uppercase tracking-wider">
                <tr>
                  <th scope="col" className="px-4 py-3">Topic / Disease</th>
                  <th scope="col" className="px-4 py-3">Status</th>
                  <th scope="col" className="px-4 py-3">Depth Tier</th>
                  <th scope="col" className="px-4 py-3">Documents</th>
                  <th scope="col" className="px-4 py-3">Chunks</th>
                  <th scope="col" className="px-4 py-3">Latest Source</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-zinc-100 dark:divide-zinc-800 text-zinc-800 dark:text-zinc-200">
                {coverage?.diseases?.map((d: DiseaseCoverage) => (
                  <tr key={d.id} className="hover:bg-zinc-50/50 dark:hover:bg-zinc-800/40 transition">
                    <td className="px-4 py-3 font-semibold">
                      <Link to={`/diseases/${d.id}`} className="hover:text-emerald-600 dark:hover:text-emerald-400">
                        {d.name_en}
                      </Link>
                      {d.name_hi && (
                        <span className="block text-xs font-normal text-zinc-400">{d.name_hi}</span>
                      )}
                    </td>
                    <td className="px-4 py-3">
                      <span
                        className={`inline-block px-2 py-0.5 rounded text-xs font-semibold ${
                          d.status === "indexed"
                            ? "bg-emerald-100 text-emerald-800 dark:bg-emerald-950/80 dark:text-emerald-300"
                            : "bg-zinc-100 text-zinc-600 dark:bg-zinc-800 dark:text-zinc-400"
                        }`}
                      >
                        {d.status === "indexed" ? "Indexed" : "Coming Soon"}
                      </span>
                    </td>
                    <td className="px-4 py-3 capitalize text-xs">
                      <span
                        className={`px-2 py-0.5 rounded-full font-semibold ${
                          d.depth === "deep"
                            ? "bg-emerald-50 text-emerald-700 border border-emerald-300 dark:bg-emerald-950/40 dark:border-emerald-800"
                            : d.depth === "good"
                            ? "bg-blue-50 text-blue-700 border border-blue-300 dark:bg-blue-950/40 dark:border-blue-800"
                            : "bg-amber-50 text-amber-700 border border-amber-300 dark:bg-amber-950/40 dark:border-amber-800"
                        }`}
                      >
                        {d.depth}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-zinc-600 dark:text-zinc-400">{d.documents}</td>
                    <td className="px-4 py-3 text-zinc-600 dark:text-zinc-400">{d.chunks}</td>
                    <td className="px-4 py-3 text-zinc-500 dark:text-zinc-400">{d.newest_source_year || "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {/* Official Sources & Attribution */}
      <section className="p-6 sm:p-8 rounded-2xl bg-white dark:bg-zinc-800/90 border border-zinc-200 dark:border-zinc-700/80 shadow-sm space-y-4">
        <h2 className="text-xl font-bold text-zinc-900 dark:text-white">Attribution & Source Licensing</h2>
        <p className="text-sm text-zinc-600 dark:text-zinc-300 leading-relaxed">
          Public health guidance within this application is derived exclusively from publicly
          available official publications under open government data and public awareness frameworks:
        </p>
        <ul className="space-y-2 text-sm text-zinc-700 dark:text-zinc-300 list-disc list-inside">
          <li>
            <strong>Ministry of Health and Family Welfare (MoHFW), Government of India:</strong>{" "}
            National Immunization Schedule (NIS), National Vector Borne Disease Control Programme
            (NVBDCP), and National Health Mission guidelines.
          </li>
          <li>
            <strong>World Health Organization (WHO):</strong> WHO Fact Sheets and South-East Asia
            Regional Office (SEARO) epidemiological technical manuals.
          </li>
          <li>
            <strong>Indian Council of Medical Research (ICMR):</strong> Evidence-based community
            health monographs and prevention protocols.
          </li>
        </ul>
      </section>
    </div>
  );
};
