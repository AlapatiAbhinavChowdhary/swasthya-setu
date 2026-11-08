export interface SourceResponse {
  number: number;
  source: string;
  page: string;
  snippet: string;
  publisher?: string | null;
  year?: number | null;
  url?: string | null;
}

export interface ChatResponse {
  answer: string;
  citations: number[];
  sources: SourceResponse[];
  intent: string;
  language: string;
  emergency: boolean;
  language_consistent: boolean;
  request_id: string;
}

export interface ChatRequest {
  message: string;
  session_id?: string | null;
  language?: "en" | "hi" | "or" | "pa" | null;
}

export interface FeedbackRequest {
  session_id: string;
  rating: "up" | "down";
  comment?: string | null;
}

export interface FeedbackResponse {
  accepted: boolean;
  request_id: string;
}

export interface DiseaseDocument {
  id: string;
  doc_id: string;
  title: string;
  publisher: string;
  url: string;
  file: string;
  year?: number | null;
  doc_type: string;
  chunks: number;
  coverage: string;
  label: string;
}

export interface DiseaseCoverage {
  id: string;
  name_en: string;
  name_hi: string;
  category?: string;
  documents: number;
  specific_documents: number;
  chunks: number;
  depth: "basic" | "good" | "deep" | string;
  newest_source_year?: number | null;
  has_general_source: boolean;
  documents_detail: DiseaseDocument[];
  last_indexed?: string | null;
  status: "indexed" | "coming_soon" | string;
}

export interface CoverageResponse {
  diseases: DiseaseCoverage[];
}

export interface VaccinationItem {
  age: string;
  age_key: string;
  age_months_min?: number;
  age_months_max?: number;
  target_group: string;
  vaccines: string[];
  supplements?: string[];
  description: string;
}

export interface VaccinationResponse {
  source_label: string;
  reviewed: boolean;
  age_months_queried?: number | null;
  schedule: VaccinationItem[];
  footnotes: Record<string, string>;
}

export interface OutbreakAlert {
  id: string;
  label: string;
  disease: string;
  district: string;
  state: string;
  date: string;
  advisory: string;
  advisory_hi?: string;
  source: string;
}

export interface AlertsResponse {
  disclaimer: string;
  is_demo: boolean;
  query: {
    district?: string | null;
    state?: string | null;
    disease?: string | null;
  };
  count: number;
  alerts: OutbreakAlert[];
}

export interface Facility {
  id: string;
  name: string;
  type: string;
  district: string;
  state: string;
  address: string;
  phone: string;
  label: string;
}

export interface FacilitiesResponse {
  disclaimer: string;
  is_sample: boolean;
  query: {
    district?: string | null;
    state?: string | null;
  };
  count: number;
  facilities: Facility[];
}

export interface LanguageItem {
  code: string;
  name: string;
  native_name: string;
  status: "supported" | "draft" | string;
}

export interface LanguagesResponse {
  languages: LanguageItem[];
}

export interface FeedbackRecordItem {
  id: number;
  session_hash: string;
  rating: "up" | "down";
  comment?: string | null;
  request_id: string;
  created_at?: string | null;
}

export interface AdminFeedbackResponse {
  feedback: FeedbackRecordItem[];
  count: number;
}
