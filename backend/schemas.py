"""
Idea Graveyard — Pydantic Schemas
Request/response shapes and validation. Single source of truth for API contract.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


# --- Status values (single source of truth) ---
VALID_STATUSES = {"dormant", "reconsidering", "resurrected"}


# --- Error envelope ---
class ErrorDetail(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    error: ErrorDetail


# --- Content Reference ---
class ContentReferenceOut(BaseModel):
    id: int
    title: str
    url: Optional[str] = None
    performance_metric: Optional[float] = None
    published_at: Optional[datetime] = None
    tags: list[str] = []
    source_type: Optional[str] = None

    model_config = {"from_attributes": True}


# --- Idea ---
class IdeaCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    source: Optional[str] = None
    tags: list[str] = []
    captured_at: Optional[datetime] = None
    auto_analyze: bool = False


class IdeaScores(BaseModel):
    relevance_score: Optional[float] = None
    audience_fit: Optional[float] = None
    content_fit: Optional[float] = None
    freshness: Optional[float] = None
    historical_fit: Optional[float] = None
    semantic_opportunity: Optional[float] = None


class ContentBrief(BaseModel):
    new_angle: Optional[str] = None
    title: Optional[str] = None
    hook: Optional[str] = None
    structure: Optional[list[str]] = None
    key_points: Optional[list[str]] = None


class ThumbnailConcept(BaseModel):
    concept_name: str
    visual_description: str
    text_overlay: str
    color_mood: str
    image_prompt: str


class VideoScriptSection(BaseModel):
    section_title: str
    timestamp_range: str
    visual_cue: str
    dialogue: str


class VideoScript(BaseModel):
    estimated_duration: str
    target_audience: str
    sections: list[VideoScriptSection]


class SeoPackage(BaseModel):
    suggested_titles: list[str]
    youtube_description: str
    timestamps: list[str]
    tags: list[str]
    hashtag_cluster: list[str]


class SocialRepurpose(BaseModel):
    twitter_thread: list[str]
    linkedin_post: str


class ProductionKit(BaseModel):
    thumbnail_concepts: list[ThumbnailConcept]
    video_script: VideoScript
    seo_package: SeoPackage
    social_repurpose: SocialRepurpose


class IdeaOut(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    source: Optional[str] = None
    tags: list[str] = []
    status: str
    captured_at: Optional[datetime] = None
    relevance_score: Optional[float] = None
    audience_fit: Optional[float] = None
    content_fit: Optional[float] = None
    freshness: Optional[float] = None
    historical_fit: Optional[float] = None
    semantic_opportunity: Optional[float] = None
    analysis_summary: Optional[str] = None
    why_now: Optional[str] = None
    content_brief: Optional[ContentBrief] = None
    production_kit: Optional[ProductionKit] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class IdeaListOut(BaseModel):
    ideas: list[IdeaOut]
    total: int


class IdeaCandidatesOut(BaseModel):
    candidates: list[IdeaOut]
    total: int


# --- Import ---
class ImportResult(BaseModel):
    imported: int
    skipped: int
    errors: list[str] = []


# --- Analysis ---
class AnalysisResult(BaseModel):
    """Structured result from AI analysis — validated before use."""
    audience_fit: float = Field(..., ge=0, le=100)
    content_fit: float = Field(..., ge=0, le=100)
    freshness: float = Field(..., ge=0, le=100)
    historical_fit: float = Field(..., ge=0, le=100)
    semantic_opportunity: float = Field(..., ge=0, le=100)
    summary: str = Field(..., min_length=1)


class WhyNowResult(BaseModel):
    """Structured 'Why Now' from AI."""
    narrative: str = Field(..., min_length=1)
    key_changes: list[str] = Field(default_factory=list)


class ContentBriefResult(BaseModel):
    """Structured content brief from AI."""
    new_angle: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1)
    hook: str = Field(..., min_length=1)
    structure: list[str] = Field(..., min_length=1)
    key_points: list[str] = Field(..., min_length=1)


# --- Health ---
class HealthResponse(BaseModel):
    status: str
    database: str
