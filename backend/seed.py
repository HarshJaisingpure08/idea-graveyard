"""
Idea Graveyard — Seed Data
Idempotent: running twice won't create duplicates.

Creates engineered demo data where:
- Content references represent real-looking YouTube/blog performance data
- Ideas are dormant, captured months ago
- The data naturally produces 1-2 strong resurrection candidates when analyzed
"""
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session

from database import SessionLocal, init_db
from models import Idea, ContentReference


def _utc(year: int, month: int, day: int) -> datetime:
    return datetime(year, month, day, tzinfo=timezone.utc)


CONTENT_REFERENCES = [
    # Recent high-performers (establishes what the audience cares about NOW)
    {
        "title": "I Built an AI Agent That Codes Better Than Most Juniors",
        "url": "https://youtube.com/example/ai-agent-coding",
        "performance_metric": 485000,
        "published_at": _utc(2026, 8, 15),
        "tags": ["AI", "coding", "agents", "LangGraph"],
        "source_type": "youtube",
    },
    {
        "title": "The Truth About AI Replacing Developers in 2026",
        "url": "https://youtube.com/example/ai-replacing-devs",
        "performance_metric": 720000,
        "published_at": _utc(2026, 7, 22),
        "tags": ["AI", "career", "developers", "future"],
        "source_type": "youtube",
    },
    {
        "title": "LangGraph Tutorial: Build Production AI Agents",
        "url": "https://youtube.com/example/langgraph-tutorial",
        "performance_metric": 310000,
        "published_at": _utc(2026, 8, 2),
        "tags": ["LangGraph", "AI", "agents", "tutorial"],
        "source_type": "youtube",
    },
    {
        "title": "Why Every Developer Needs to Learn Prompt Engineering",
        "url": "https://youtube.com/example/prompt-engineering",
        "performance_metric": 290000,
        "published_at": _utc(2026, 6, 18),
        "tags": ["prompt engineering", "AI", "career", "skills"],
        "source_type": "youtube",
    },
    # Historical high-performers (establishes proven topics)
    {
        "title": "Complete Python Roadmap for Data Science 2025",
        "url": "https://youtube.com/example/python-roadmap",
        "performance_metric": 1200000,
        "published_at": _utc(2025, 3, 10),
        "tags": ["Python", "data science", "roadmap", "career"],
        "source_type": "youtube",
    },
    {
        "title": "Machine Learning Projects That Actually Get You Hired",
        "url": "https://youtube.com/example/ml-projects",
        "performance_metric": 890000,
        "published_at": _utc(2025, 5, 20),
        "tags": ["machine learning", "career", "projects", "portfolio"],
        "source_type": "youtube",
    },
    {
        "title": "How I Built a RAG Pipeline from Scratch",
        "url": "https://youtube.com/example/rag-pipeline",
        "performance_metric": 410000,
        "published_at": _utc(2026, 4, 5),
        "tags": ["RAG", "AI", "LLM", "tutorial"],
        "source_type": "youtube",
    },
    {
        "title": "The Career Advice No One Gives Junior Developers",
        "url": "https://blog.example.com/career-advice-juniors",
        "performance_metric": 95000,
        "published_at": _utc(2025, 9, 12),
        "tags": ["career", "developers", "advice", "junior"],
        "source_type": "blog",
    },
]

IDEAS = [
    # HIGH POTENTIAL — should score well (AI + career + current audience interest)
    {
        "title": "Will AI Replace Junior Developers?",
        "description": "Explore whether AI coding assistants and agents are eliminating entry-level developer roles, or creating new ones. Look at actual job market data.",
        "source": "brainstorm",
        "tags": ["AI", "career", "developers", "future"],
        "captured_at": _utc(2025, 4, 15),
    },
    # HIGH POTENTIAL — should score well (prompt engineering evolution)
    {
        "title": "From Prompt Engineering to Agent Engineering",
        "description": "The shift from writing prompts to designing autonomous agent systems. What skills matter now vs 12 months ago.",
        "source": "brainstorm",
        "tags": ["AI", "agents", "prompt engineering", "skills"],
        "captured_at": _utc(2025, 6, 20),
    },
    # MEDIUM POTENTIAL
    {
        "title": "Building a Portfolio That Stands Out in the AI Era",
        "description": "Traditional portfolio projects are now trivial for AI to build. What should aspiring developers showcase instead?",
        "source": "audience question",
        "tags": ["career", "portfolio", "AI", "projects"],
        "captured_at": _utc(2025, 8, 3),
    },
    # MEDIUM POTENTIAL
    {
        "title": "The Case for Learning Boring Technologies",
        "description": "Why junior developers should master databases, networking, and operating systems before chasing the latest AI framework.",
        "source": "tweet thread",
        "tags": ["career", "fundamentals", "advice"],
        "captured_at": _utc(2025, 2, 28),
    },
    # LOWER POTENTIAL — older, less aligned
    {
        "title": "Introduction to Kubernetes for ML Engineers",
        "description": "Basic Kubernetes concepts tailored for people deploying machine learning models.",
        "source": "content calendar",
        "tags": ["Kubernetes", "MLOps", "DevOps", "deployment"],
        "captured_at": _utc(2024, 11, 10),
    },
    # LOWER POTENTIAL — niche
    {
        "title": "Web Scraping Ethics and Best Practices",
        "description": "When is scraping okay? Legal considerations, rate limiting, and responsible data collection.",
        "source": "viewer request",
        "tags": ["web scraping", "ethics", "data", "Python"],
        "captured_at": _utc(2025, 1, 5),
    },
]


def seed():
    """Idempotent seed — checks fingerprint before creating."""
    init_db()
    db = SessionLocal()

    try:
        # Seed content references
        cr_count = 0
        for ref_data in CONTENT_REFERENCES:
            fp = ContentReference.make_fingerprint(ref_data["title"], ref_data.get("url"))
            existing = db.query(ContentReference).filter(ContentReference.fingerprint == fp).first()
            if not existing:
                cr = ContentReference(**ref_data, fingerprint=fp)
                db.add(cr)
                cr_count += 1

        db.commit()
        print(f"Content references: {cr_count} created, {len(CONTENT_REFERENCES) - cr_count} already existed.")

        # Seed ideas
        idea_count = 0
        for idea_data in IDEAS:
            fp = Idea.make_fingerprint(idea_data["title"], idea_data.get("source"))
            existing = db.query(Idea).filter(Idea.fingerprint == fp).first()
            if not existing:
                idea = Idea(**idea_data, fingerprint=fp)
                db.add(idea)
                idea_count += 1

        db.commit()
        print(f"Ideas: {idea_count} created, {len(IDEAS) - idea_count} already existed.")
        print("Seed complete.")

    finally:
        db.close()


if __name__ == "__main__":
    seed()
