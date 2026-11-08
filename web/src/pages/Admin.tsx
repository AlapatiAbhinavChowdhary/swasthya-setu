import React, { useState } from "react";
import {
  Lock,
  KeyRound,
  ThumbsUp,
  ThumbsDown,
  RefreshCw,
} from "lucide-react";
import type { LanguageCode } from "../i18n/translations";
import { translations } from "../i18n/translations";
import { api, ApiError } from "../api/client";
import type { AdminFeedbackResponse, FeedbackRecordItem } from "../types";

interface AdminProps {
  language: LanguageCode;
}

export const Admin: React.FC<AdminProps> = ({ language }) => {
  const t = translations[language] || translations.en;
  const [token, setToken] = useState("");
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<AdminFeedbackResponse | null>(null);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!token.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const res = await api.getAdminFeedback(token.trim());
      setData(res);
      setIsAuthenticated(true);
    } catch (err: unknown) {
      if (err instanceof ApiError) {
        if (err.status === 401) {
          setError("Invalid admin token. Access denied.");
        } else if (err.status === 404) {
          setError(
            "Admin feedback endpoint is currently disabled on this server (ADMIN_TOKEN not set)."
          );
        } else {
          setError(err.message);
        }
      } else {
        setError("Unable to authenticate with the admin service.");
      }
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    if (!token) return;
    setLoading(true);
    try {
      const res = await api.getAdminFeedback(token);
      setData(res);
    } catch (err: unknown) {
      if (err instanceof ApiError) {
        setError(err.message);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    setToken("");
    setIsAuthenticated(false);
    setData(null);
    setError(null);
  };

  const upvotes = data?.feedback.filter((f) => f.rating === "up").length || 0;
  const downvotes = data?.feedback.filter((f) => f.rating === "down").length || 0;
  const total = data?.count || 0;
  const satisfaction = total > 0 ? Math.round((upvotes / total) * 100) : 0;

  return (
    <div className="space-y-8 py-6 max-w-4xl mx-auto">
      {/* Header */}
      <div className="space-y-2">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-zinc-100 dark:bg-zinc-800 text-zinc-700 dark:text-zinc-300 text-xs font-semibold border border-zinc-200 dark:border-zinc-700">
          <Lock className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400" aria-hidden="true" />
          <span>Operator Dashboard</span>
        </div>
        <h1 className="text-3xl font-extrabold text-zinc-900 dark:text-white tracking-tight">
          Admin & Feedback Review
        </h1>
        <p className="text-zinc-600 dark:text-zinc-300 text-sm">
          Review community ratings and user feedback collected across sessions. Protected by
          constant-time bearer token verification. Tokens are held in-memory and never stored.
        </p>
      </div>

      {!isAuthenticated ? (
        /* Token Entry Form */
        <div className="max-w-md mx-auto p-6 sm:p-8 rounded-2xl bg-white dark:bg-zinc-800/90 border border-zinc-200 dark:border-zinc-700/80 shadow-sm space-y-6">
          <div className="w-12 h-12 rounded-2xl bg-emerald-100 dark:bg-emerald-950/80 text-emerald-700 dark:text-emerald-300 flex items-center justify-center mx-auto">
            <KeyRound className="w-6 h-6" aria-hidden="true" />
          </div>

          <div className="text-center space-y-1">
            <h2 className="text-xl font-bold text-zinc-900 dark:text-white">Admin Authentication</h2>
            <p className="text-xs text-zinc-500 dark:text-zinc-400">
              Enter your configured ADMIN_TOKEN secret to inspect feedback logs.
            </p>
          </div>

          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label htmlFor="admin-token-input" className="block text-xs font-semibold text-zinc-700 dark:text-zinc-300 mb-1">
                Admin Token
              </label>
              <input
                id="admin-token-input"
                type="password"
                value={token}
                onChange={(e) => setToken(e.target.value)}
                placeholder="Enter ADMIN_TOKEN"
                autoComplete="off"
                className="w-full px-3.5 py-2.5 rounded-xl border border-zinc-300 dark:border-zinc-700 bg-white dark:bg-zinc-900 text-zinc-900 dark:text-zinc-100 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
              />
            </div>

            {error && (
              <div className="p-3 bg-red-50 dark:bg-red-950/60 border border-red-200 dark:border-red-800 rounded-lg text-xs text-red-700 dark:text-red-300">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading || !token.trim()}
              className="w-full py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-sm shadow-sm transition disabled:opacity-50 focus:outline-none focus:ring-2 focus:ring-emerald-500"
            >
              {loading ? "Authenticating..." : "Access Dashboard"}
            </button>
          </form>
        </div>
      ) : (
        /* Authenticated Feedback View */
        <div className="space-y-6">
          {/* Controls Bar */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="inline-block w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse" />
              <span className="text-xs font-semibold text-zinc-600 dark:text-zinc-400">
                Session Active (Token verified)
              </span>
            </div>

            <div className="flex items-center gap-3">
              <button
                onClick={handleRefresh}
                disabled={loading}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-zinc-100 hover:bg-zinc-200 dark:bg-zinc-800 dark:hover:bg-zinc-700 text-zinc-700 dark:text-zinc-300 text-xs font-semibold transition"
              >
                <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} aria-hidden="true" />
                <span>Refresh</span>
              </button>
              <button
                onClick={handleLogout}
                className="px-3 py-1.5 rounded-lg bg-zinc-200 hover:bg-zinc-300 dark:bg-zinc-700 dark:hover:bg-zinc-600 text-zinc-800 dark:text-zinc-200 text-xs font-semibold transition"
              >
                Lock Session
              </button>
            </div>
          </div>

          {/* Stats Cards */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div className="p-4 rounded-2xl bg-white dark:bg-zinc-800/90 border border-zinc-200 dark:border-zinc-700/80 shadow-sm">
              <p className="text-xs text-zinc-500 dark:text-zinc-400">Total Feedback</p>
              <p className="text-2xl font-black text-zinc-900 dark:text-white mt-1">{total}</p>
            </div>
            <div className="p-4 rounded-2xl bg-white dark:bg-zinc-800/90 border border-zinc-200 dark:border-zinc-700/80 shadow-sm">
              <p className="text-xs text-zinc-500 dark:text-zinc-400">Helpful (Upvotes)</p>
              <p className="text-2xl font-black text-emerald-600 dark:text-emerald-400 mt-1">{upvotes}</p>
            </div>
            <div className="p-4 rounded-2xl bg-white dark:bg-zinc-800/90 border border-zinc-200 dark:border-zinc-700/80 shadow-sm">
              <p className="text-xs text-zinc-500 dark:text-zinc-400">Needs Work (Downvotes)</p>
              <p className="text-2xl font-black text-red-600 dark:text-red-400 mt-1">{downvotes}</p>
            </div>
            <div className="p-4 rounded-2xl bg-white dark:bg-zinc-800/90 border border-zinc-200 dark:border-zinc-700/80 shadow-sm">
              <p className="text-xs text-zinc-500 dark:text-zinc-400">Satisfaction Rate</p>
              <p className="text-2xl font-black text-blue-600 dark:text-blue-400 mt-1">
                {total > 0 ? `${satisfaction}%` : "—"}
              </p>
            </div>
          </div>

          {/* Records Table / List */}
          <div className="p-6 rounded-2xl bg-white dark:bg-zinc-800/90 border border-zinc-200 dark:border-zinc-700/80 shadow-sm space-y-4">
            <h2 className="text-lg font-bold text-zinc-900 dark:text-white">Recent Feedback Entries</h2>

            {!data || data.feedback.length === 0 ? (
              <p className="text-sm text-zinc-500 py-8 text-center">{t.adminNoFeedback}</p>
            ) : (
              <div className="divide-y divide-zinc-100 dark:divide-zinc-800 space-y-3">
                {data.feedback.map((item: FeedbackRecordItem) => (
                  <div key={item.id} className="pt-3 first:pt-0 space-y-1.5">
                    <div className="flex items-center justify-between text-xs">
                      <div className="flex items-center gap-2">
                        {item.rating === "up" ? (
                          <span className="inline-flex items-center gap-1 text-emerald-600 dark:text-emerald-400 font-bold">
                            <ThumbsUp className="w-3.5 h-3.5" aria-hidden="true" />
                            <span>Helpful</span>
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1 text-red-600 dark:text-red-400 font-bold">
                            <ThumbsDown className="w-3.5 h-3.5" aria-hidden="true" />
                            <span>Not Helpful</span>
                          </span>
                        )}
                        <span className="text-zinc-400">&middot;</span>
                        <span className="text-zinc-400 font-mono text-[11px]">
                          req: {item.request_id ? item.request_id.slice(0, 8) : "—"}
                        </span>
                      </div>
                      {item.created_at && (
                        <span className="text-zinc-400">{item.created_at}</span>
                      )}
                    </div>

                    {item.comment ? (
                      <p className="text-sm text-zinc-700 dark:text-zinc-300 bg-zinc-50 dark:bg-zinc-900/60 p-2.5 rounded-lg border border-zinc-200/60 dark:border-zinc-800">
                        &ldquo;{item.comment}&rdquo;
                      </p>
                    ) : (
                      <p className="text-xs text-zinc-400 italic">No comment provided</p>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
