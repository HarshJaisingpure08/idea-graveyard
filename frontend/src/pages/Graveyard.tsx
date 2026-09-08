/**
 * Graveyard — archive-style list of all ideas.
 * Filterable by status, editorial layout.
 */
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { fetchIdeas } from '../api';
import type { Idea } from '../types';

function formatDate(iso: string | null): string {
  if (!iso) return '—';
  return new Date(iso).toLocaleDateString('en-US', { month: 'short', year: 'numeric' });
}

const STATUS_FILTERS: { label: string; value: string | null }[] = [
  { label: 'All', value: null },
  { label: 'Dormant', value: 'dormant' },
  { label: 'Resurrected', value: 'resurrected' },
];

export default function Graveyard() {
  const navigate = useNavigate();
  const [ideas, setIdeas] = useState<Idea[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState<string | null>(null);

  useEffect(() => {
    load();
  }, [statusFilter]);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const res = await fetchIdeas({
        status: statusFilter || undefined,
        sort_by: 'relevance',
        limit: 100,
      });
      setIdeas(res.ideas);
      setTotal(res.total);
    } catch (e: any) {
      setError(e.message || 'Failed to load.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="layout">
      <div className="editorial-header">
        <h1>Archive</h1>
        <p className="editorial-subtitle">
          Every idea you've ever shelved, in one place.
        </p>
      </div>

      {/* Filters */}
      <div className="filter-bar">
        {STATUS_FILTERS.map(f => (
          <button
            key={f.label}
            className={`filter-btn${statusFilter === f.value ? ' active' : ''}`}
            onClick={() => setStatusFilter(f.value)}
          >
            {f.label}
          </button>
        ))}
        <span style={{ marginLeft: 'auto', fontSize: '0.8125rem', color: 'var(--text-muted)' }}>
          {total} idea{total !== 1 ? 's' : ''}
        </span>
      </div>

      {error && (
        <div className="error-state">
          <p>{error}</p>
          <button className="btn btn-secondary" onClick={load}>Try again</button>
        </div>
      )}

      {loading ? (
        <div className="loading-state">
          <div className="loading-spinner" />
          Loading...
        </div>
      ) : ideas.length === 0 ? (
        <div className="empty-state">
          <p>No ideas found.</p>
        </div>
      ) : (
        <div className="stagger-in">
          {ideas.map((idea, i) => (
            <div
              key={idea.id}
              className="idea-entry"
              onClick={() => navigate(`/idea/${idea.id}`)}
            >
              <div style={{ display: 'flex', alignItems: 'baseline', gap: '16px' }}>
                <span className="idea-entry-number">{String(i + 1).padStart(2, '0')}</span>
                <div style={{ flex: 1 }}>
                  <div className="idea-entry-title">{idea.title}</div>
                  <div className="idea-entry-meta">
                    {idea.tags.length > 0 && (
                      <span className="idea-entry-tags">{idea.tags.join(' · ')}</span>
                    )}
                    <span>Captured {formatDate(idea.captured_at)}</span>
                    {idea.relevance_score !== null && (
                      <span className={`idea-entry-score${idea.relevance_score >= 70 ? ' high' : ''}`}>
                        Relevance {Math.round(idea.relevance_score)}
                      </span>
                    )}
                    <span className={`status-badge ${idea.status}`}>{idea.status}</span>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
