"""
Idea Graveyard — Analysis Service
Orchestrates: fetch context → AI analysis → scoring → persist.
"""
import logging
from sqlalchemy.orm import Session

from models import Idea
from repositories import get_content_references, update_idea
from services.scoring import calculate_relevance
from ai.provider import analyze_idea as ai_analyze

logger = logging.getLogger(__name__)


def analyze(db: Session, idea: Idea) -> Idea:
    """
    Run full analysis pipeline for an idea.
    Raises RuntimeError on AI failure.
    """
    logger.info(f"analysis_started idea_id={idea.id} title={idea.title!r}")

    # Fetch content references for context
    content_refs = get_content_references(db)
    refs_data = [
        {
            "title": cr.title,
            "performance_metric": cr.performance_metric,
            "tags": cr.tags or [],
            "published_at": str(cr.published_at) if cr.published_at else None,
            "source_type": cr.source_type,
        }
        for cr in content_refs
    ]

    # AI analysis — may raise on failure
    try:
        result = ai_analyze(
            idea_title=idea.title,
            idea_description=idea.description or "",
            content_refs=refs_data,
        )
    except Exception as e:
        logger.error(f"analysis_failed idea_id={idea.id} error={e}")
        raise RuntimeError(f"Analysis failed: {e}") from e

    # Deterministic scoring from AI sub-scores
    relevance = calculate_relevance(
        audience_fit=result.audience_fit,
        content_fit=result.content_fit,
        freshness=result.freshness,
        historical_fit=result.historical_fit,
        semantic_opportunity=result.semantic_opportunity,
    )

    # Persist
    idea = update_idea(
        db,
        idea,
        audience_fit=result.audience_fit,
        content_fit=result.content_fit,
        freshness=result.freshness,
        historical_fit=result.historical_fit,
        semantic_opportunity=result.semantic_opportunity,
        relevance_score=relevance,
        analysis_summary=result.summary,
    )

    logger.info(f"analysis_completed idea_id={idea.id} relevance={relevance}")
    return idea
