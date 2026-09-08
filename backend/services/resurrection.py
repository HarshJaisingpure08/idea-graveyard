"""
Idea Graveyard — Resurrection Service
Handles: status transition → Why Now → Content Brief → persist.
"""
import logging
from sqlalchemy.orm import Session

from models import Idea
from repositories import get_content_references, update_idea
from ai.provider import generate_why_now, generate_content_brief

logger = logging.getLogger(__name__)


def resurrect(db: Session, idea: Idea) -> Idea:
    """
    Full resurrection pipeline.
    Requires idea to have been analyzed first.
    """
    if idea.relevance_score is None:
        raise ValueError("Idea must be analyzed before resurrection.")

    logger.info(f"resurrection_started idea_id={idea.id}")

    # Mark as reconsidering
    idea = update_idea(db, idea, status="reconsidering")

    # Fetch content refs for context
    content_refs = get_content_references(db)
    refs_data = [
        {
            "title": cr.title,
            "performance_metric": cr.performance_metric,
            "tags": cr.tags or [],
        }
        for cr in content_refs[:8]
    ]

    try:
        # Generate Why Now
        why_now_result = generate_why_now(
            idea_title=idea.title,
            idea_description=idea.description or "",
            analysis_summary=idea.analysis_summary or "",
            content_refs=refs_data,
        )

        # Generate Content Brief
        brief_result = generate_content_brief(
            idea_title=idea.title,
            idea_description=idea.description or "",
            analysis_summary=idea.analysis_summary or "",
            why_now=why_now_result.narrative,
        )

        # Persist and mark resurrected
        idea = update_idea(
            db,
            idea,
            status="resurrected",
            why_now=why_now_result.narrative,
            content_brief={
                "new_angle": brief_result.new_angle,
                "title": brief_result.title,
                "hook": brief_result.hook,
                "structure": brief_result.structure,
                "key_points": brief_result.key_points,
                "key_changes": why_now_result.key_changes,
            },
        )

        logger.info(f"resurrection_completed idea_id={idea.id}")
        return idea

    except Exception as e:
        # Roll back to dormant on failure
        logger.error(f"resurrection_failed idea_id={idea.id} error={e}")
        update_idea(db, idea, status="dormant")
        raise RuntimeError(f"Resurrection failed: {e}") from e
