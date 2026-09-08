/**
 * Idea Graveyard — TypeScript Types
 * Mirrors backend Pydantic schemas exactly.
 */

export type IdeaStatus = 'dormant' | 'reconsidering' | 'resurrected';

export interface ContentBrief {
  new_angle: string | null;
  title: string | null;
  hook: string | null;
  structure: string[] | null;
  key_points: string[] | null;
  key_changes?: string[] | null;
}

export interface Idea {
  id: number;
  title: string;
  description: string | null;
  source: string | null;
  tags: string[];
  status: IdeaStatus;
  captured_at: string | null;
  relevance_score: number | null;
  audience_fit: number | null;
  content_fit: number | null;
  freshness: number | null;
  historical_fit: number | null;
  semantic_opportunity: number | null;
  analysis_summary: string | null;
  why_now: string | null;
  content_brief: ContentBrief | null;
  created_at: string;
  updated_at: string;
}

export interface IdeaListResponse {
  ideas: Idea[];
  total: number;
}

export interface CandidatesResponse {
  candidates: Idea[];
  total: number;
}

export interface ImportResult {
  imported: number;
  skipped: number;
  errors: string[];
}

export interface HealthResponse {
  status: string;
  database: string;
}

export interface ApiError {
  error: {
    code: string;
    message: string;
  };
}
