/**
 * IdeaDetail — the hero screen.
 * Shows idea, scores, analysis, and the resurrection interaction.
 */
import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { fetchIdea, analyzeIdea, resurrectIdea } from '../api';
import type { Idea } from '../types';

function formatDate(iso: string | null): string {
  if (!iso) return '—';
  return new Date(iso).toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' });
}

function daysSince(iso: string | null): string {
  if (!iso) return '—';
  const days = Math.floor((Date.now() - new Date(iso).getTime()) / (1000 * 60 * 60 * 24));
  if (days < 30) return `${days} days`;
  if (days < 365) return `${Math.floor(days / 30)} months`;
  return `${Math.floor(days / 365)}y ${Math.floor((days % 365) / 30)}m`;
}

function ScoreBar({ label, value, type }: { label: string; value: number | null; type?: string }) {
  if (value === null) return null;
  const cls = value >= 80 ? 'high' : value >= 60 ? 'medium' : '';
  const fillCls = type === 'positive' ? 'positive' : cls;
  return (
    <div className="score-bar">
      <span className="score-bar-label">{label}</span>
      <div className="score-bar-track">
        <div className={`score-bar-fill ${fillCls}`} style={{ width: `${value}%` }} />
      </div>
      <span className="score-bar-value">{Math.round(value)}</span>
    </div>
  );
}

export default function IdeaDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [idea, setIdea] = useState<Idea | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [actionLoading, setActionLoading] = useState<string | null>(null);

  useEffect(() => {
    load();
  }, [id]);

  async function load() {
    if (!id) return;
    setLoading(true);
    setError(null);
    try {
      const data = await fetchIdea(Number(id));
      setIdea(data);
    } catch (e: any) {
      setError(e.message || 'Idea not found.');
    } finally {
      setLoading(false);
    }
  }

  async function handleAnalyze() {
    if (!idea) return;
    setActionLoading('analyzing');
    setError(null);
    try {
      const updated = await analyzeIdea(idea.id);
      setIdea(updated);
    } catch (e: any) {
      setError(e.message || 'Analysis failed.');
    } finally {
      setActionLoading(null);
    }
  }

  async function handleResurrect() {
    if (!idea) return;
    setActionLoading('resurrecting');
    setError(null);
    try {
      // Show reconsidering state
      setIdea(prev => prev ? { ...prev, status: 'reconsidering' } : prev);
      const updated = await resurrectIdea(idea.id);
      setIdea(updated);
    } catch (e: any) {
      setError(e.message || 'Resurrection failed.');
      // Reload to get actual state
      await load();
    } finally {
      setActionLoading(null);
    }
  }

  if (loading) {
    return (
      <div className="layout">
        <div className="loading-state">
          <div className="loading-spinner" />
          Loading...
        </div>
      </div>
    );
  }

  if (error && !idea) {
    return (
      <div className="layout">
        <div className="error-state">
          <p>{error}</p>
          <button className="btn btn-secondary" onClick={() => navigate('/')}>Back to dashboard</button>
        </div>
      </div>
    );
  }

  if (!idea) return null;

  const isAnalyzed = idea.relevance_score !== null;
  const isResurrected = idea.status === 'resurrected';
  const isReconsidering = idea.status === 'reconsidering';
  const brief = idea.content_brief;

  return (
    <div className="layout">
      {/* Back link */}
      <a className="detail-back" onClick={() => navigate(-1)} style={{ cursor: 'pointer' }}>
        ← Back
      </a>

      {/* Header */}
      <div className="detail-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
          <span className={`status-badge ${idea.status}`}>{idea.status}</span>
        </div>
        <h1 className="detail-title">{idea.title}</h1>
        {idea.description && (
          <p style={{ color: 'var(--text-secondary)', marginTop: '8px', maxWidth: '600px' }}>
            {idea.description}
          </p>
        )}

        <div className="detail-meta" style={{ marginTop: '20px' }}>
          <div className="detail-meta-item">
            <span className="detail-meta-label">First captured</span>
            <span className="detail-meta-value">{formatDate(idea.captured_at)}</span>
          </div>
          <div className="detail-meta-item">
            <span className="detail-meta-label">Dormant for</span>
            <span className="detail-meta-value">{daysSince(idea.captured_at)}</span>
          </div>
          {isAnalyzed && (
            <div className="detail-meta-item">
              <span className="detail-meta-label">Relevance now</span>
              <span className="detail-meta-value" style={{ fontSize: '1.25rem', fontFamily: 'var(--font-display)', color: 'var(--accent-vermilion)' }}>
                {Math.round(idea.relevance_score!)}
              </span>
            </div>
          )}
          {idea.tags.length > 0 && (
            <div className="detail-meta-item">
              <span className="detail-meta-label">Topics</span>
              <span className="detail-meta-value" style={{ fontSize: '0.8125rem' }}>
                {idea.tags.join(' · ')}
              </span>
            </div>
          )}
        </div>
      </div>

      {error && (
        <div className="error-state" style={{ textAlign: 'left', padding: '16px 0' }}>
          <p>{error}</p>
          <button className="btn btn-secondary" onClick={() => setError(null)}>Dismiss</button>
        </div>
      )}

      <hr className="divider" />

      {/* Not analyzed yet */}
      {!isAnalyzed && (
        <div className="section">
          <p style={{ color: 'var(--text-secondary)', marginBottom: '16px' }}>
            This idea hasn't been analyzed yet. Run analysis to see how relevant it is today.
          </p>
          <button
            className="btn btn-primary"
            onClick={handleAnalyze}
            disabled={actionLoading === 'analyzing'}
          >
            {actionLoading === 'analyzing' ? 'Finding connections...' : 'Analyze this idea'}
          </button>
        </div>
      )}

      {/* Scores */}
      {isAnalyzed && (
        <div className="section fade-in">
          <div className="section-title">Analysis</div>
          <div style={{ maxWidth: '420px' }}>
            <ScoreBar label="Audience fit" value={idea.audience_fit} />
            <ScoreBar label="Content fit" value={idea.content_fit} />
            <ScoreBar label="Freshness" value={idea.freshness} />
            <ScoreBar label="Historical fit" value={idea.historical_fit} />
            <ScoreBar label="Opportunity" value={idea.semantic_opportunity} />
          </div>
          {idea.analysis_summary && (
            <p style={{ marginTop: '20px', color: 'var(--text-secondary)', fontStyle: 'italic', maxWidth: '560px' }}>
              "{idea.analysis_summary}"
            </p>
          )}
        </div>
      )}

      {/* Resurrection action */}
      {isAnalyzed && !isResurrected && (
        <div className="resurrect-action">
          <div className={`resurrect-status ${idea.status}`}>
            {isReconsidering ? 'Reconsidering...' : 'Dormant'}
          </div>
          {!isReconsidering && (
            <button
              className="btn btn-primary"
              onClick={handleResurrect}
              disabled={actionLoading === 'resurrecting'}
            >
              Resurrect this idea →
            </button>
          )}
          {isReconsidering && actionLoading === 'resurrecting' && (
            <div className="loading-state" style={{ textAlign: 'left', padding: '8px 0' }}>
              <div className="loading-spinner" style={{ margin: '0' }} />
              <span style={{ marginLeft: '8px' }}>Generating fresh perspective...</span>
            </div>
          )}
        </div>
      )}

      {/* Resurrected — full content brief */}
      {isResurrected && (
        <div className="fade-in">
          <div className="resurrect-action">
            <div className="resurrect-status resurrected">Resurrected</div>
          </div>

          {/* Why Now */}
          {idea.why_now && (
            <div className="brief-section">
              <div className="brief-label">What changed</div>
              <p className="brief-content">{idea.why_now}</p>
              {brief?.key_changes && brief.key_changes.length > 0 && (
                <ul className="brief-list" style={{ marginTop: '12px' }}>
                  {brief.key_changes.map((change, i) => (
                    <li key={i}>{change}</li>
                  ))}
                </ul>
              )}
            </div>
          )}

          {/* Content Brief */}
          {brief && (
            <div className="stagger-in">
              {brief.new_angle && (
                <div className="brief-section">
                  <div className="brief-label">New angle</div>
                  <p className="brief-content">{brief.new_angle}</p>
                </div>
              )}

              {brief.title && (
                <div className="brief-section">
                  <div className="brief-label">Suggested title</div>
                  <p className="brief-content" style={{ fontFamily: 'var(--font-display)', fontSize: '1.25rem' }}>
                    {brief.title}
                  </p>
                </div>
              )}

              {brief.hook && (
                <div className="brief-section">
                  <div className="brief-label">Opening hook</div>
                  <p className="brief-content" style={{ fontStyle: 'italic' }}>{brief.hook}</p>
                </div>
              )}

              {brief.structure && brief.structure.length > 0 && (
                <div className="brief-section">
                  <div className="brief-label">Structure</div>
                  <ol style={{ paddingLeft: '20px', marginTop: '8px' }}>
                    {brief.structure.map((s, i) => (
                      <li key={i} style={{ padding: '4px 0', color: 'var(--text-primary)', fontSize: '0.9375rem' }}>{s}</li>
                    ))}
                  </ol>
                </div>
              )}

              {brief.key_points && brief.key_points.length > 0 && (
                <div className="brief-section">
                  <div className="brief-label">Key points to cover</div>
                  <ul className="brief-list">
                    {brief.key_points.map((p, i) => (
                      <li key={i}>{p}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
