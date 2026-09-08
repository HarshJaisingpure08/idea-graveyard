"""
Idea Graveyard — Idea Routes
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from schemas import (
    IdeaCreate, IdeaOut, IdeaListOut, IdeaCandidatesOut, ErrorResponse
)
import repositories
from services.analysis import analyze
from services.resurrection import resurrect

router = APIRouter(prefix="/api/ideas", tags=["ideas"])


@router.get("", response_model=IdeaListOut)
def list_ideas(
    status: Optional[str] = None,
    sort_by: str = "relevance",
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    """List all ideas, optionally filtered by status."""
    ideas, total = repositories.get_ideas(db, status=status, sort_by=sort_by, limit=limit, offset=offset)
    return IdeaListOut(ideas=ideas, total=total)


@router.get("/candidates", response_model=IdeaCandidatesOut)
def get_candidates(
    min_score: float = 60.0,
    limit: int = 10,
    db: Session = Depends(get_db),
):
    """Get resurrection candidates — high-relevance dormant ideas."""
    candidates = repositories.get_resurrection_candidates(db, min_score=min_score, limit=limit)
    return IdeaCandidatesOut(candidates=candidates, total=len(candidates))


@router.get("/{idea_id}", response_model=IdeaOut)
def get_idea(idea_id: int, db: Session = Depends(get_db)):
    """Get a single idea by ID."""
    idea = repositories.get_idea(db, idea_id)
    if not idea:
        raise HTTPException(status_code=404, detail={
            "code": "IDEA_NOT_FOUND",
            "message": f"Idea {idea_id} not found."
        })
    return idea


@router.post("", response_model=IdeaOut, status_code=201)
def create_idea(data: IdeaCreate, db: Session = Depends(get_db)):
    """Create a new idea."""
    idea, created = repositories.create_idea(db, data)
    if not created:
        raise HTTPException(status_code=409, detail={
            "code": "DUPLICATE_IDEA",
            "message": "An idea with this title already exists."
        })
    return idea


@router.post("/{idea_id}/analyze", response_model=IdeaOut)
def analyze_idea(idea_id: int, db: Session = Depends(get_db)):
    """Trigger analysis for an idea."""
    idea = repositories.get_idea(db, idea_id)
    if not idea:
        raise HTTPException(status_code=404, detail={
            "code": "IDEA_NOT_FOUND",
            "message": f"Idea {idea_id} not found."
        })

    try:
        idea = analyze(db, idea)
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail={
            "code": "ANALYSIS_FAILED",
            "message": "We couldn't analyze this idea right now. Try again."
        })

    return idea


@router.post("/{idea_id}/resurrect", response_model=IdeaOut)
def resurrect_idea(idea_id: int, db: Session = Depends(get_db)):
    """Resurrect an idea — generates Why Now + Content Brief."""
    idea = repositories.get_idea(db, idea_id)
    if not idea:
        raise HTTPException(status_code=404, detail={
            "code": "IDEA_NOT_FOUND",
            "message": f"Idea {idea_id} not found."
        })

    if idea.relevance_score is None:
        raise HTTPException(status_code=400, detail={
            "code": "NOT_ANALYZED",
            "message": "This idea needs to be analyzed before it can be resurrected."
        })

    try:
        idea = resurrect(db, idea)
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail={
            "code": "RESURRECTION_FAILED",
            "message": "Resurrection failed. The idea has been returned to dormant status."
        })

    return idea
