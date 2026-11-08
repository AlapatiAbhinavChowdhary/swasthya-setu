import React from "react";
import { ExternalLink, X, BookOpen, Building2, Calendar, FileText } from "lucide-react";
import type { SourceResponse } from "../types";

interface SourcePanelProps {
  sources: SourceResponse[];
  selectedNumber: number | null;
  onClose: () => void;
}

export const SourcePanel: React.FC<SourcePanelProps> = ({
  sources,
  selectedNumber,
  onClose,
}) => {
  if (selectedNumber === null) return null;

  const currentSource = sources.find((s) => s.number === selectedNumber);

  // Validate URL to ensure it only starts with http:// or https://
  const sanitizeUrl = (url?: string | null): string | null => {
    if (!url) return null;
    const trimmed = url.trim();
    if (trimmed.startsWith("http://") || trimmed.startsWith("https://")) {
      return trimmed;
    }
    return null;
  };

  const safeUrl = sanitizeUrl(currentSource?.url);

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label={`Source citation [${selectedNumber}]`}
      className="fixed inset-y-0 right-0 z-50 w-full sm:max-w-md bg-white dark:bg-zinc-900 border-l border-zinc-200 dark:border-zinc-800 shadow-2xl flex flex-col p-6 animate-in slide-in-from-right duration-200"
    >
      <div className="flex items-center justify-between pb-4 border-b border-zinc-200 dark:border-zinc-800">
        <div className="flex items-center gap-2">
          <BookOpen className="w-5 h-5 text-emerald-600 dark:text-emerald-400" aria-hidden="true" />
          <h2 className="text-lg font-bold text-zinc-900 dark:text-zinc-100">
            Citation [{selectedNumber}] Details
          </h2>
        </div>
        <button
          type="button"
          onClick={onClose}
          className="p-1.5 text-zinc-500 hover:text-zinc-900 dark:text-zinc-400 dark:hover:text-zinc-100 rounded-lg hover:bg-zinc-100 dark:hover:bg-zinc-800 focus:outline-none focus:ring-2 focus:ring-emerald-500"
          aria-label="Close source panel"
        >
          <X className="w-5 h-5" aria-hidden="true" />
        </button>
      </div>

      <div className="flex-1 overflow-y-auto py-5 space-y-5">
        {currentSource ? (
          <>
            <div>
              <span className="text-xs font-semibold uppercase tracking-wider text-emerald-700 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/80 px-2.5 py-1 rounded-md border border-emerald-200 dark:border-emerald-800">
                Official Document Reference
              </span>
              <h3 className="text-base font-bold text-zinc-900 dark:text-zinc-100 mt-2 break-words">
                {currentSource.source.split(/[/\\]/).pop()}
              </h3>
            </div>

            <div className="grid grid-cols-1 gap-2.5 text-sm text-zinc-600 dark:text-zinc-400 bg-zinc-50 dark:bg-zinc-800/60 p-3.5 rounded-lg border border-zinc-200 dark:border-zinc-700/60">
              {currentSource.publisher && (
                <div className="flex items-start gap-2">
                  <Building2 className="w-4 h-4 mt-0.5 text-zinc-400 flex-shrink-0" aria-hidden="true" />
                  <span>
                    <strong className="text-zinc-700 dark:text-zinc-300">Publisher:</strong>{" "}
                    {currentSource.publisher}
                  </span>
                </div>
              )}
              {currentSource.year && (
                <div className="flex items-center gap-2">
                  <Calendar className="w-4 h-4 text-zinc-400 flex-shrink-0" aria-hidden="true" />
                  <span>
                    <strong className="text-zinc-700 dark:text-zinc-300">Year:</strong> {currentSource.year}
                  </span>
                </div>
              )}
              {currentSource.page && (
                <div className="flex items-start gap-2">
                  <FileText className="w-4 h-4 mt-0.5 text-zinc-400 flex-shrink-0" aria-hidden="true" />
                  <span>
                    <strong className="text-zinc-700 dark:text-zinc-300">Section / Page:</strong>{" "}
                    {currentSource.page}
                  </span>
                </div>
              )}
            </div>

            <div>
              <h4 className="text-xs font-semibold uppercase tracking-wider text-zinc-500 dark:text-zinc-400 mb-1.5">
                Retrieved Evidence Passage
              </h4>
              <blockquote className="p-3.5 bg-zinc-100 dark:bg-zinc-800/80 rounded-lg text-sm text-zinc-800 dark:text-zinc-200 border-l-4 border-emerald-600 leading-relaxed italic break-words">
                "{currentSource.snippet}"
              </blockquote>
            </div>

            {safeUrl ? (
              <div className="pt-2">
                <a
                  href={safeUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center justify-center gap-2 w-full px-4 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white font-medium text-sm rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:ring-offset-2 transition"
                >
                  <span>Open Official Document URL</span>
                  <ExternalLink className="w-4 h-4" aria-hidden="true" />
                </a>
              </div>
            ) : (
              <p className="text-xs text-zinc-500 dark:text-zinc-400">
                Local repository verified document ({currentSource.source}).
              </p>
            )}
          </>
        ) : (
          <p className="text-sm text-zinc-500">Citation details could not be found for [{selectedNumber}].</p>
        )}
      </div>

      <div className="pt-4 border-t border-zinc-200 dark:border-zinc-800 flex justify-end">
        <button
          type="button"
          onClick={onClose}
          className="px-4 py-2 bg-zinc-200 dark:bg-zinc-700 hover:bg-zinc-300 dark:hover:bg-zinc-600 text-zinc-800 dark:text-zinc-200 font-medium text-sm rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500"
        >
          Close
        </button>
      </div>
    </div>
  );
};

