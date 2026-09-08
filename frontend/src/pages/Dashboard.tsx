/**
 * Dashboard — editorial homepage
 * Shows resurrection candidates and a story-driven layout.
 */
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { fetchCandidates, fetchIdeas, analyzeIdea } from '../api';
import type { Idea } from '../types';

function formatDate(iso: string | null): string {
  if (!iso) return '—';
  const d = new Date(iso);
  return d.toLocaleDateString('en-US', { month: 'short', year: 'numeric' });
}

function daysSince(iso: string | null): number | null {
  if (!iso) return null;
  const then = new Date(iso).getTime();
  const now = Date.now();
  return Math.floor((now - then) / (1000 * 60 * 60 * 24));
}

export default function Dashboard() {
  const navigate = useNavigate();
  const [candidates, setCandidates] = useState<Idea[]>([]);
  const [allIdeas, setAllIdeas] = useState<Idea[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [analyzingIds, setAnalyzingIds] = useState<Set<number>>(new Set());

  useEffect(() => {
    loadData();
  }, []);

  async function loadData() {
    setLoading(true);
    setError(null);
    try {
      const [candRes, ideaRes] = await Promise.all([
        fetchCandidates(50),
        fetchIdeas({ sort_by: 'relevance', limit: 50 }),
      ]);
      setCandidates(candRes.candidates);
      setAllIdeas(ideaRes.ideas);
    } catch (e: any) {
      setError(e.message || 'Failed to load data.');
    } finally {
      setLoading(false);
    }
  }

  async function handleAnalyze(id: number, e: React.MouseEvent) {
    e.stopPropagation();
    setAnalyzingIds(prev => new Set(prev).add(id));
    try {
      await analyzeIdea(id);
      await loadData();
    } catch (err: any) {
      setError(err.message || 'Analysis failed.');
    } finally {
      setAnalyzingIds(prev => {
        const next = new Set(prev);
        next.delete(id);
        return next;
      });
    }
  }

  const unanalyzedIdeas = allIdeas.filter(i => i.relevance_score === null);
  const totalIdeas = allIdeas.length;
  const candidateCount = candidates.length;

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

  return (
    <div className="layout">
      {/* Editorial introduction */}
      <div className="editorial-header">
        <h1>Idea Graveyard</h1>
        <p className="editorial-subtitle">
          Some ideas were early. Some were forgotten.<br />
          A few are ready now.
        </p>
      </div>

      {error && (
        <div className="error-state">
          <p>{error}</p>
          <button className="btn btn-secondary" onClick={loadData}>Try again</button>
        </div>
      )}

      {/* Stats */}
      <div className="dash-stats">
        <div>
          <div className="dash-stat-value">{totalIdeas}</div>
          <div className="dash-stat-label">Ideas archived</div>
        </div>
        <div>
          <div className="dash-stat-value">{candidateCount}</div>
          <div className="dash-stat-label">Worth another look</div>
        </div>
        <div>
          <div className="dash-stat-value">{unanalyzedIdeas.length}</div>
          <div className="dash-stat-label">Not yet analyzed</div>
        </div>
      </div>

      <hr className="divider" />

      {/* Candidates */}
      {candidateCount > 0 && (
        <div className="section">
          <div className="section-title">Worth revisiting</div>
          <div className="stagger-in">
            {candidates.map((idea) => (
              <div
                key={idea.id}
                className="candidate-highlight"
                onClick={() => navigate(`/idea/${idea.id}`)}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <div>
                    <div className="candidate-score">{Math.round(idea.relevance_score!)}</div>
                    <div className="candidate-title">{idea.title}</div>
                    {idea.analysis_summary && (
                      <p className="candidate-summary">"{idea.analysis_summary}"</p>
                    )}
                    <div className="idea-entry-meta" style={{ marginTop: '12px' }}>
                      <span>Captured {formatDate(idea.captured_at)}</span>
                      {daysSince(idea.captured_at) !== null && (
                        <span>Dormant {daysSince(idea.captured_at)} days</span>
                      )}
                    </div>
                  </div>
                </div>
                <div className="candidate-actions">
                  <button
                    className="btn btn-ghost"
                    onClick={(e) => { e.stopPropagation(); navigate(`/idea/${idea.id}`); }}
                  >
                    Why now →
                  </button>
                  <button
                    className="btn btn-primary"
                    onClick={(e) => { e.stopPropagation(); navigate(`/idea/${idea.id}`); }}
                  >
                    Resurrect →
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Unanalyzed ideas */}
      {unanalyzedIdeas.length > 0 && (
        <>
          <hr className="divider" />
          <div className="section">
            <div className="section-title">Awaiting analysis</div>
            <div className="stagger-in">
              {unanalyzedIdeas.map((idea, i) => (
                <div key={idea.id} className="idea-entry" onClick={() => navigate(`/idea/${idea.id}`)}>
                  <div className="idea-entry-number">{String(i + 1).padStart(2, '0')}</div>
                  <div className="idea-entry-title">{idea.title}</div>
                  <div className="idea-entry-meta">
                    {idea.tags.length > 0 && (
                      <span className="idea-entry-tags">{idea.tags.join(' · ')}</span>
                    )}
                    <span>Captured {formatDate(idea.captured_at)}</span>
                    <button
                      className="btn btn-ghost"
                      disabled={analyzingIds.has(idea.id)}
                      onClick={(e) => handleAnalyze(idea.id, e)}
                    >
                      {analyzingIds.has(idea.id) ? 'Analyzing...' : 'Analyze →'}
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </>
      )}

      {totalIdeas === 0 && !error && (
        <div className="empty-state">
          <p>No ideas yet. Import your first batch to get started.</p>
          <button className="btn btn-secondary" onClick={() => navigate('/import')} style={{ marginTop: '16px' }}>
            Import ideas
          </button>
        </div>
      )}
    </div>
  );
}
