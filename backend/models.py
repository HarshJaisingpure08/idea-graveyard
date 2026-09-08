"""
Idea Graveyard — ORM Models
"""
import hashlib
from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Float, Text, DateTime, JSON, Index
)
from database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Idea(Base):
    __tablename__ = "ideas"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    source = Column(String(200), nullable=True)
    tags = Column(JSON, default=list)

    # Status: dormant | reconsidering | resurrected
    status = Column(String(50), default="dormant", nullable=False, index=True)

    captured_at = Column(DateTime(timezone=True), nullable=True)

    # Scoring — populated by analysis
    relevance_score = Column(Float, nullable=True)
    audience_fit = Column(Float, nullable=True)
    content_fit = Column(Float, nullable=True)
    freshness = Column(Float, nullable=True)
    historical_fit = Column(Float, nullable=True)
    semantic_opportunity = Column(Float, nullable=True)

    # AI-generated text
    analysis_summary = Column(Text, nullable=True)
    why_now = Column(Text, nullable=True)
    content_brief = Column(JSON, nullable=True)
    production_kit = Column(JSON, nullable=True)

    # Deduplication
    fingerprint = Column(String(64), unique=True, nullable=False, index=True)

    created_at = Column(DateTime(timezone=True), default=_utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow, nullable=False)

    __table_args__ = (
        Index("ix_ideas_status_relevance", "status", "relevance_score"),
    )

    @staticmethod
    def make_fingerprint(title: str, source: str | None = None) -> str:
        """Deterministic fingerprint for deduplication."""
        normalized = title.strip().lower()
        if source:
            normalized += "|" + source.strip().lower()
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


class ContentReference(Base):
    __tablename__ = "content_references"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    url = Column(String(1000), nullable=True)
    performance_metric = Column(Float, nullable=True)  # e.g., views, engagement
    published_at = Column(DateTime(timezone=True), nullable=True)
    tags = Column(JSON, default=list)
    source_type = Column(String(100), nullable=True)  # youtube, blog, podcast

    fingerprint = Column(String(64), unique=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), default=_utcnow, nullable=False)

    @staticmethod
    def make_fingerprint(title: str, url: str | None = None) -> str:
        normalized = title.strip().lower()
        if url:
            normalized += "|" + url.strip().lower()
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()
