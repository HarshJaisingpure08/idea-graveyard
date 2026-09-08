/**
 * Idea Graveyard — API Client
 * Typed, consistent error handling. Single place for all API calls.
 */
import type { Idea, IdeaListResponse, CandidatesResponse, ImportResult, HealthResponse } from './types';

const API_BASE = 'http://localhost:8000/api';

class ApiClientError extends Error {
  code: string;
  constructor(code: string, message: string) {
    super(message);
    this.code = code;
    this.name = 'ApiClientError';
  }
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE}${path}`;
  const res = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });

  if (!res.ok) {
    let code = 'UNKNOWN_ERROR';
    let message = `Request failed (${res.status})`;
    try {
      const body = await res.json();
      if (body.detail?.code) {
        code = body.detail.code;
        message = body.detail.message;
      } else if (body.detail) {
        message = typeof body.detail === 'string' ? body.detail : JSON.stringify(body.detail);
      }
    } catch {
      // ignore parse errors
    }
    throw new ApiClientError(code, message);
  }

  return res.json();
}

// --- Ideas ---

export async function fetchIdeas(params?: {
  status?: string;
  sort_by?: string;
  limit?: number;
  offset?: number;
}): Promise<IdeaListResponse> {
  const query = new URLSearchParams();
  if (params?.status) query.set('status', params.status);
  if (params?.sort_by) query.set('sort_by', params.sort_by);
  if (params?.limit) query.set('limit', String(params.limit));
  if (params?.offset) query.set('offset', String(params.offset));
  const qs = query.toString();
  return request<IdeaListResponse>(`/ideas${qs ? `?${qs}` : ''}`);
}

export async function fetchIdea(id: number): Promise<Idea> {
  return request<Idea>(`/ideas/${id}`);
}

export async function fetchCandidates(minScore = 60): Promise<CandidatesResponse> {
  return request<CandidatesResponse>(`/ideas/candidates?min_score=${minScore}`);
}

export async function createIdea(data: {
  title: string;
  description?: string;
  source?: string;
  tags?: string[];
}): Promise<Idea> {
  return request<Idea>('/ideas', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function analyzeIdea(id: number): Promise<Idea> {
  return request<Idea>(`/ideas/${id}/analyze`, { method: 'POST' });
}

export async function resurrectIdea(id: number): Promise<Idea> {
  return request<Idea>(`/ideas/${id}/resurrect`, { method: 'POST' });
}

// --- Import ---

export async function importFile(file: File): Promise<ImportResult> {
  const formData = new FormData();
  formData.append('file', file);

  const url = `${API_BASE}/import`;
  const res = await fetch(url, { method: 'POST', body: formData });

  if (!res.ok) {
    let code = 'IMPORT_FAILED';
    let message = 'Import failed';
    try {
      const body = await res.json();
      if (body.detail?.code) {
        code = body.detail.code;
        message = body.detail.message;
      }
    } catch { /* */ }
    throw new ApiClientError(code, message);
  }

  return res.json();
}

// --- Health ---

export async function fetchHealth(): Promise<HealthResponse> {
  return request<HealthResponse>('/health');
}
