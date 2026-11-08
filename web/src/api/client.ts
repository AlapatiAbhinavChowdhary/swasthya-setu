import type {
  ChatRequest,
  ChatResponse,
  CoverageResponse,
  FeedbackRequest,
  FeedbackResponse,
  VaccinationResponse,
  AlertsResponse,
  FacilitiesResponse,
  LanguagesResponse,
  AdminFeedbackResponse,
} from "../types";

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "";

export class ApiError extends Error {
  status: number;
  data: unknown;

  constructor(message: string, status: number, data?: unknown) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.data = data;
  }
}

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
        ...(options.headers || {}),
      },
    });

    if (!response.ok) {
      let errorDetail = "";
      try {
        const errorJson = await response.json();
        errorDetail = errorJson.detail || JSON.stringify(errorJson);
      } catch {
        errorDetail = await response.text();
      }

      if (response.status === 422) {
        throw new ApiError("Please check your input and try again.", 422, errorDetail);
      } else if (response.status === 429) {
        throw new ApiError("Too many requests. Please wait a moment before asking again.", 429, errorDetail);
      } else if (response.status === 503) {
        throw new ApiError("The assistant is temporarily busy or unavailable. Please try again shortly.", 503, errorDetail);
      } else if (response.status === 401) {
        throw new ApiError("Invalid or missing authentication token.", 401, errorDetail);
      } else if (response.status === 404) {
        throw new ApiError("Requested resource or endpoint not found.", 404, errorDetail);
      }

      throw new ApiError(errorDetail || `Request failed with status ${response.status}`, response.status);
    }

    return (await response.json()) as T;
  } catch (err: unknown) {
    if (err instanceof ApiError) {
      throw err;
    }
    const message = err instanceof Error ? err.message : "Network error";
    throw new ApiError(`Unable to reach the health server: ${message}`, 0);
  }
}

export const api = {
  getHealth: () => request<{ status: string; llm_configured: boolean }>("/health"),

  getLanguages: () => request<LanguagesResponse>("/languages"),

  getCoverage: () => request<CoverageResponse>("/coverage"),

  getDiseases: () => request<CoverageResponse>("/diseases"),

  getVaccination: (ageMonths?: number | null) => {
    const query = typeof ageMonths === "number" ? `?age_months=${ageMonths}` : "";
    return request<VaccinationResponse>(`/vaccination${query}`);
  },

  getAlerts: (params: { district?: string; disease?: string; state?: string; language?: string } = {}) => {
    const search = new URLSearchParams();
    if (params.district) search.set("district", params.district);
    if (params.disease) search.set("disease", params.disease);
    if (params.state) search.set("state", params.state);
    if (params.language) search.set("language", params.language);
    const qs = search.toString();
    return request<AlertsResponse>(`/alerts${qs ? `?${qs}` : ""}`);
  },

  getFacilities: (params: { district?: string; state?: string; language?: string } = {}) => {
    const search = new URLSearchParams();
    if (params.district) search.set("district", params.district);
    if (params.state) search.set("state", params.state);
    if (params.language) search.set("language", params.language);
    const qs = search.toString();
    return request<FacilitiesResponse>(`/facilities${qs ? `?${qs}` : ""}`);
  },

  getSourcesMarkdown: () => request<{ content: string }>("/sources"),

  postChat: (payload: ChatRequest) =>
    request<ChatResponse>("/chat", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  postFeedback: (payload: FeedbackRequest) =>
    request<FeedbackResponse>("/feedback", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  getAdminFeedback: (token: string) =>
    request<AdminFeedbackResponse>("/admin/feedback", {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }),
};

