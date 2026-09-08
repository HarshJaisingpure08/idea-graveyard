"""
Idea Graveyard — Repository Layer
All database queries in one place. No business logic here.
"""
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from models import Idea, ContentReference
from schemas import IdeaCreate


def get_ideas(
    db: Session,
    status: Optional[str] = None,
    sort_by: str = "relevance",
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[Idea], int]:
    """List ideas with optional status filter and sorting."""
    query = db.query(Idea)

    if status:
        query = query.filter(Idea.status == status)

    # Total before pagination
    total = query.count()

    # Sort
    if sort_by == "relevance":
        query = query.order_by(desc(Idea.relevance_score).nulls_last(), desc(Idea.created_at))
    elif sort_by == "captured":
        query = query.order_by(desc(Idea.captured_at).nulls_last())
    else:
        query = query.order_by(desc(Idea.created_at))

    ideas = query.offset(offset).limit(limit).all()
    return ideas, total


def get_idea(db: Session, idea_id: int) -> Optional[Idea]:
    """Get single idea by ID."""
    return db.query(Idea).filter(Idea.id == idea_id).first()


def create_idea(db: Session, data: IdeaCreate) -> tuple[Idea, bool]:
    """
    Create idea with dedup. Returns (idea, created).
    If fingerprint exists, returns existing idea with created=False.
    """
    fingerprint = Idea.make_fingerprint(data.title, data.source)

    existing = db.query(Idea).filter(Idea.fingerprint == fingerprint).first()
    if existing:
        return existing, False

    idea = Idea(
        title=data.title.strip(),
        description=data.description,
        source=data.source,
        tags=data.tags,
        captured_at=data.captured_at,
        fingerprint=fingerprint,
    )
    db.add(idea)
    db.commit()
    db.refresh(idea)
    return idea, True


def create_ideas_bulk(db: Session, items: list[IdeaCreate]) -> tuple[int, int]:
    """
    Bulk create with dedup. Returns (imported_count, skipped_count).
    Uses a single transaction.
    """
    imported = 0
    skipped = 0

    # Pre-fetch existing fingerprints to avoid N+1
    fingerprints = [Idea.make_fingerprint(item.title, item.source) for item in items]
    existing_fps = set(
        row[0] for row in db.query(Idea.fingerprint)
        .filter(Idea.fingerprint.in_(fingerprints))
        .all()
    )

    new_ideas = []
    for item, fp in zip(items, fingerprints):
        if fp in existing_fps:
            skipped += 1
            continue
        existing_fps.add(fp)  # prevent dupes within same batch
        new_ideas.append(Idea(
            title=item.title.strip(),
            description=item.description,
            source=item.source,
            tags=item.tags,
            captured_at=item.captured_at,
            fingerprint=fp,
        ))
        imported += 1

    if new_ideas:
        db.add_all(new_ideas)
        db.commit()

    return imported, skipped


def update_idea(db: Session, idea: Idea, **kwargs) -> Idea:
    """Partial update — only set provided fields."""
    for key, value in kwargs.items():
        setattr(idea, key, value)
    db.commit()
    db.refresh(idea)
    return idea


def get_resurrection_candidates(db: Session, min_score: float = 60.0, limit: int = 10) -> list[Idea]:
    """Ideas with high relevance that are still dormant — worth resurrecting."""
    return (
        db.query(Idea)
        .filter(Idea.status == "dormant")
        .filter(Idea.relevance_score.isnot(None))
        .filter(Idea.relevance_score >= min_score)
        .order_by(desc(Idea.relevance_score))
        .limit(limit)
        .all()
    )


def get_content_references(db: Session, limit: int = 100) -> list[ContentReference]:
    """All content references for scoring context."""
    return db.query(ContentReference).order_by(desc(ContentReference.published_at)).limit(limit).all()


def get_ideas_count_by_status(db: Session) -> dict[str, int]:
    """Count ideas grouped by status."""
    rows = db.query(Idea.status, func.count(Idea.id)).group_by(Idea.status).all()
    return {status: count for status, count in rows}
