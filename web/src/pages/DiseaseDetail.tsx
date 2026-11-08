import React, { useState, useEffect } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import {
  ArrowLeft,
  Shield,
  ExternalLink,
  MessageSquare,
  AlertCircle,
  Clock,
} from "lucide-react";
import type { LanguageCode } from "../i18n/translations";
import { translations } from "../i18n/translations";
import { api } from "../api/client";
import type { DiseaseCoverage } from "../types";

interface DiseaseDetailProps {
  language: LanguageCode;
}

export const DiseaseDetail: React.FC<DiseaseDetailProps> = ({ language }) => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const t = translations[language] || translations.en;

  const [disease, setDisease] = useState<DiseaseCoverage | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    api
      .getCoverage()
      .then((res) => {
        if (mounted) {
          const match = (res.diseases || []).find((d) => d.id === id);
          if (match) {
            setDisease(match);
          } else {
            setError(`Topic or disease "${id}" not found.`);
          }
          setLoading(false);
        }
      })
      .catch((err) => {
        if (mounted) {
          setError(err.message || "Failed to load disease details.");
          setLoading(false);
        }
      });
    return () => {
      mounted = false;
    };
  }, [id]);

  if (loading) {
    return (
      <div className="py-20 text-center text-zinc-500 dark:text-zinc-400 animate-pulse">
        Loading official disease coverage details...
      </div>
    );
  }

  if (error || !disease) {
    return (
      <div className="py-12 space-y-4 max-w-lg mx-auto text-center">
        <div className="p-4 bg-red-50 dark:bg-red-950/60 border border-red-200 dark:border-red-800 rounded-xl text-red-700 dark:text-red-300 text-sm">
          {error || "Disease not found."}
        </div>
        <Link
          to="/diseases"
          className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-zinc-200 dark:bg-zinc-800 text-zinc-800 dark:text-zinc-200 font-semibold text-sm hover:bg-zinc-300 dark:hover:bg-zinc-700 transition"
        >
          <ArrowLeft className="w-4 h-4" aria-hidden="true" />
          <span>Back to Directory</span>
        </Link>
      </div>
    );
  }

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

  const depth = getDepthBadge(disease.depth);
  const askPrompt = `Tell me about ${disease.name_en}: symptoms, causes, and prevention in simple words`;

  return (
    <div className="space-y-8 py-4 max-w-4xl mx-auto">
      {/* Back Link */}
      <div>
        <Link
          to="/diseases"
          className="inline-flex items-center gap-1.5 text-sm font-semibold text-zinc-600 dark:text-zinc-400 hover:text-emerald-600 dark:hover:text-emerald-400 transition"
        >
          <ArrowLeft className="w-4 h-4" aria-hidden="true" />
          <span>Back to All Diseases</span>
        </Link>
      </div>

      {/* Main Header Card */}
      <div className="p-6 sm:p-8 rounded-2xl bg-white dark:bg-zinc-800/90 border border-zinc-200 dark:border-zinc-700/80 shadow-sm space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
          <div className="space-y-2">
            <div className="flex items-center gap-2 flex-wrap">
              <span className={`px-3 py-1 rounded-full text-xs font-bold border ${depth.className}`}>
                Coverage: {depth.label}
              </span>
              {disease.category && (
                <span className="px-2.5 py-0.5 rounded-full text-xs font-medium bg-zinc-100 dark:bg-zinc-700 text-zinc-600 dark:text-zinc-300 capitalize">
                  {disease.category.replace(/-/g, " ")}
                </span>
              )}
            </div>
            <h1 className="text-3xl sm:text-4xl font-extrabold text-zinc-900 dark:text-white tracking-tight">
              {disease.name_en}
            </h1>
            {disease.name_hi && (
              <p className="text-lg text-zinc-500 dark:text-zinc-400 font-semibold">
                {disease.name_hi}
              </p>
            )}
          </div>

          <button
            onClick={() => navigate(`/chat?q=${encodeURIComponent(askPrompt)}`)}
            className="inline-flex items-center justify-center gap-2 px-5 py-3 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-sm shadow-sm transition focus:outline-none focus:ring-2 focus:ring-emerald-500 flex-shrink-0"
          >
            <MessageSquare className="w-4 h-4" aria-hidden="true" />
            <span>Ask in Chat</span>
          </button>
        </div>

        {/* Stats Row */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-4 border-t border-zinc-100 dark:border-zinc-700/60">
          <div className="p-3 rounded-xl bg-zinc-50 dark:bg-zinc-900/60 border border-zinc-200/60 dark:border-zinc-700/40">
            <p className="text-xs text-zinc-500 dark:text-zinc-400">Total Documents</p>
            <p className="text-xl font-bold text-zinc-900 dark:text-white mt-0.5">
              {disease.documents}
            </p>
          </div>
          <div className="p-3 rounded-xl bg-zinc-50 dark:bg-zinc-900/60 border border-zinc-200/60 dark:border-zinc-700/40">
            <p className="text-xs text-zinc-500 dark:text-zinc-400">Disease-Specific</p>
            <p className="text-xl font-bold text-emerald-600 dark:text-emerald-400 mt-0.5">
              {disease.specific_documents}
            </p>
          </div>
          <div className="p-3 rounded-xl bg-zinc-50 dark:bg-zinc-900/60 border border-zinc-200/60 dark:border-zinc-700/40">
            <p className="text-xs text-zinc-500 dark:text-zinc-400">Indexed Chunks</p>
            <p className="text-xl font-bold text-zinc-900 dark:text-white mt-0.5">
              {disease.chunks}
            </p>
          </div>
          <div className="p-3 rounded-xl bg-zinc-50 dark:bg-zinc-900/60 border border-zinc-200/60 dark:border-zinc-700/40">
            <p className="text-xs text-zinc-500 dark:text-zinc-400">Latest Source Year</p>
            <p className="text-xl font-bold text-zinc-900 dark:text-white mt-0.5">
              {disease.newest_source_year || "—"}
            </p>
          </div>
        </div>
      </div>

      {/* Verified Official Source Documents */}
      <section className="space-y-4">
        <div className="flex items-center gap-2">
          <Shield className="w-5 h-5 text-emerald-600 dark:text-emerald-400" aria-hidden="true" />
          <h2 className="text-xl font-bold text-zinc-900 dark:text-white">
            Verified Official Sources ({disease.documents_detail?.length || 0})
          </h2>
        </div>
        <p className="text-sm text-zinc-600 dark:text-zinc-400">
          Answers in Swasthya Setu for this topic are retrieved directly and only from these
          government and WHO documents.
        </p>

        <div className="space-y-3">
          {disease.documents_detail && disease.documents_detail.length > 0 ? (
            disease.documents_detail.map((doc, idx) => (
              <div
                key={doc.doc_id || idx}
                className="p-4 sm:p-5 rounded-xl bg-white dark:bg-zinc-800/90 border border-zinc-200 dark:border-zinc-700/80 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-4"
              >
                <div className="space-y-1.5 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="px-2 py-0.5 rounded text-xs font-semibold uppercase bg-zinc-100 dark:bg-zinc-700 text-zinc-700 dark:text-zinc-300">
                      {doc.publisher || "Official Source"}
                    </span>
                    <span
                      className={`px-2 py-0.5 rounded text-xs font-semibold ${
                        doc.coverage === "disease-specific"
                          ? "bg-emerald-100 text-emerald-800 dark:bg-emerald-950/80 dark:text-emerald-300"
                          : "bg-zinc-100 text-zinc-600 dark:bg-zinc-700 dark:text-zinc-300"
                      }`}
                    >
                      {doc.label}
                    </span>
                    {doc.year && (
                      <span className="text-xs text-zinc-500 dark:text-zinc-400">
                        ({doc.year})
                      </span>
                    )}
                  </div>

                  <h3 className="text-base font-bold text-zinc-900 dark:text-white leading-snug">
                    {doc.title}
                  </h3>

                  <div className="text-xs text-zinc-500 dark:text-zinc-400 flex items-center gap-3">
                    <span>Format: {doc.doc_type}</span>
                    <span>&middot;</span>
                    <span>Chunks: {doc.chunks}</span>
                  </div>
                </div>

                {doc.url && (
                  <a
                    href={doc.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1.5 px-3 py-2 rounded-lg bg-zinc-100 hover:bg-zinc-200 dark:bg-zinc-700 dark:hover:bg-zinc-600 text-zinc-800 dark:text-zinc-200 text-xs font-semibold transition flex-shrink-0 focus:outline-none focus:ring-2 focus:ring-emerald-500"
                    aria-label={`Open source document ${doc.title} on official website`}
                  >
                    <span>View Official Source</span>
                    <ExternalLink className="w-3.5 h-3.5" aria-hidden="true" />
                  </a>
                )}
              </div>
            ))
          ) : (
            <div className="p-4 bg-zinc-100 dark:bg-zinc-800 rounded-xl text-zinc-500 text-sm">
              No individual source documents listed.
            </div>
          )}
        </div>
      </section>

      {/* Honest Coming Soon Guidance Section */}
      <section className="p-6 rounded-2xl bg-zinc-50 dark:bg-zinc-850 border border-zinc-200 dark:border-zinc-800 space-y-3">
        <div className="flex items-center gap-2 text-zinc-700 dark:text-zinc-300">
          <Clock className="w-5 h-5 text-amber-500" aria-hidden="true" />
          <h3 className="text-base font-bold">
            Detailed Clinical Guidelines (Pending Human Expert Review)
          </h3>
        </div>
        <p className="text-sm text-zinc-600 dark:text-zinc-400 leading-relaxed">
          Full disease management monographs and structured algorithmic flowcharts are staged for
          future release after formal clinical review by certified public health professionals. In
          the meantime, interactive awareness questions can be queried directly via our RAG-grounded
          assistant.
        </p>
      </section>

      {/* Safety Notice */}
      <div className="p-4 bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-800/60 rounded-xl flex items-start gap-3 text-amber-900 dark:text-amber-200 text-xs sm:text-sm">
        <AlertCircle className="w-5 h-5 flex-shrink-0 text-amber-600 dark:text-amber-400 mt-0.5" aria-hidden="true" />
        <p>
          <strong>Medical Disclaimer:</strong> This platform is purely educational. If you or someone
          near you experiences sudden shortness of breath, severe chest pain, prolonged high fever with
          confusion, or profuse bleeding, contact <strong>108</strong> or visit your nearest hospital
          immediately.
        </p>
      </div>
    </div>
  );
};
