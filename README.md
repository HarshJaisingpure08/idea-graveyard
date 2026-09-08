# Idea Graveyard

**Your forgotten ideas, reconsidered.**

An editorial research workspace that resurfaces dormant content ideas by analyzing them against recent performance data. Import ideas you shelved months ago, and discover which ones deserve a second look.

## How it works

```
Import ideas → Analyze relevance → Discover candidates → Resurrect → Get a content brief
```

1. **Import** — Upload a CSV or JSON of content ideas you once had
2. **Analyze** — Each idea is scored against your recent content performance data
3. **Discover** — High-relevance dormant ideas surface as resurrection candidates
4. **Resurrect** — Get a "Why Now" narrative and a full content brief

## Tech stack

| Layer | Technology |
|-------|-----------|
| Frontend | React + TypeScript + Vite |
| Backend | Python + FastAPI + SQLAlchemy |
| Database | PostgreSQL |
| AI | Google Gemini (analysis + content generation) |

## Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL running on localhost:5432
- Google Gemini API key ([get one here](https://aistudio.google.com/apikey))

### 1. Database

```sql
CREATE DATABASE idea_graveyard;
```

### 2. Backend

```bash
cd backend
uv venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux

uv pip install -r requirements.txt
```

Create `backend/.env`:
```
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/idea_graveyard
GEMINI_API_KEY=your-key-here
```

Seed demo data and start:
```bash
python seed.py
uvicorn main:app --reload --port 8000
```

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

## Project structure

```
backend/
├── config.py          # Settings (single source of truth)
├── database.py        # SQLAlchemy setup
├── models.py          # ORM models (Idea, ContentReference)
├── schemas.py         # Pydantic request/response types
├── repositories.py    # Database queries
├── main.py            # FastAPI entry point
├── seed.py            # Idempotent demo data
├── services/
│   ├── scoring.py     # Pure deterministic scoring engine
│   ├── analysis.py    # Analysis orchestrator
│   └── resurrection.py # Resurrection orchestrator
├── ai/
│   └── provider.py    # Sole Gemini SDK integration point
├── routes/
│   ├── health.py      # GET /api/health
│   ├── ideas.py       # CRUD + analyze + resurrect
│   └── import_.py     # CSV/JSON file upload
└── tests/
    └── test_core.py   # Scoring, dedup, validation tests

frontend/
├── src/
│   ├── api.ts         # Typed API client
│   ├── types.ts       # TypeScript types (mirrors Pydantic schemas)
│   ├── index.css      # Editorial design system
│   ├── App.tsx        # Root component + routing
│   └── pages/
│       ├── Dashboard.tsx    # Editorial homepage
│       ├── IdeaDetail.tsx   # Hero screen (scores + resurrection)
│       ├── Graveyard.tsx    # Archive list
│       └── Import.tsx       # File upload
```

## Running tests

```bash
cd backend
.venv\Scripts\activate
python -m pytest tests/ -v
```

## API endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | /api/health | Health check |
| GET | /api/ideas | List ideas |
| GET | /api/ideas/candidates | Resurrection candidates |
| GET | /api/ideas/{id} | Idea detail |
| POST | /api/ideas | Create idea |
| POST | /api/ideas/{id}/analyze | Trigger analysis |
| POST | /api/ideas/{id}/resurrect | Trigger resurrection |
| POST | /api/import | Import CSV/JSON file |
