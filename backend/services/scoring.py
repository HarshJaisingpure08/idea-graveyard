"""
Idea Graveyard — Scoring Engine
Pure, deterministic. Same inputs → same output. No LLM here.
"""


# Weights — single source of truth
WEIGHTS = {
    "audience_fit": 0.30,
    "content_fit": 0.25,
    "freshness": 0.20,
    "historical_fit": 0.15,
    "semantic_opportunity": 0.10,
}


def calculate_relevance(
    audience_fit: float,
    content_fit: float,
    freshness: float,
    historical_fit: float,
    semantic_opportunity: float,
) -> float:
    """
    Calculate overall relevance score from sub-scores.
    All inputs should be 0-100. Output is 0-100.
    Deterministic: identical inputs always produce identical output.
    """
    scores = {
        "audience_fit": _clamp(audience_fit),
        "content_fit": _clamp(content_fit),
        "freshness": _clamp(freshness),
        "historical_fit": _clamp(historical_fit),
        "semantic_opportunity": _clamp(semantic_opportunity),
    }
    return round(sum(scores[k] * WEIGHTS[k] for k in WEIGHTS), 2)


def _clamp(value: float, lo: float = 0.0, hi: float = 100.0) -> float:
    """Clamp a value to [lo, hi] range."""
    return max(lo, min(hi, value))
