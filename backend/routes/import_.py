"""
Idea Graveyard — Import Route
CSV/JSON file upload with validation, normalization, dedup, and transaction.
"""
import csv
import json
import io
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from schemas import IdeaCreate, ImportResult

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["import"])

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


@router.post("/import", response_model=ImportResult)
async def import_ideas(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Import ideas from CSV or JSON file."""
    if not file.filename:
        raise HTTPException(status_code=400, detail={
            "code": "NO_FILE",
            "message": "No file was uploaded."
        })

    # Read file
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail={
            "code": "FILE_TOO_LARGE",
            "message": "File must be under 5MB."
        })

    # Parse
    filename = file.filename.lower()
    try:
        if filename.endswith(".csv"):
            ideas = _parse_csv(content)
        elif filename.endswith(".json"):
            ideas = _parse_json(content)
        else:
            raise HTTPException(status_code=400, detail={
                "code": "UNSUPPORTED_FORMAT",
                "message": "Only CSV and JSON files are supported."
            })
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"import_parse_error: {e}")
        raise HTTPException(status_code=400, detail={
            "code": "PARSE_ERROR",
            "message": f"Could not parse the file: {str(e)}"
        })

    if not ideas:
        raise HTTPException(status_code=400, detail={
            "code": "EMPTY_FILE",
            "message": "The file contains no valid ideas."
        })

    # Bulk create with dedup
    from repositories import create_ideas_bulk
    imported, skipped = create_ideas_bulk(db, ideas)

    logger.info(f"idea_imported count={imported} skipped={skipped}")

    return ImportResult(imported=imported, skipped=skipped)


def _parse_csv(content: bytes) -> list[IdeaCreate]:
    """Parse CSV content into IdeaCreate objects."""
    text = content.decode("utf-8-sig")  # Handle BOM
    reader = csv.DictReader(io.StringIO(text))
    ideas = []
    errors = []

    for i, row in enumerate(reader, start=2):
        title = row.get("title", "").strip()
        if not title:
            errors.append(f"Row {i}: missing title")
            continue

        captured_at = None
        if row.get("captured_at"):
            try:
                captured_at = datetime.fromisoformat(row["captured_at"].strip())
                if captured_at.tzinfo is None:
                    captured_at = captured_at.replace(tzinfo=timezone.utc)
            except ValueError:
                pass

        tags = []
        if row.get("tags"):
            tags = [t.strip() for t in row["tags"].split(",") if t.strip()]

        ideas.append(IdeaCreate(
            title=title,
            description=row.get("description", "").strip() or None,
            source=row.get("source", "").strip() or None,
            tags=tags,
            captured_at=captured_at,
        ))

    return ideas


def _parse_json(content: bytes) -> list[IdeaCreate]:
    """Parse JSON content into IdeaCreate objects."""
    data = json.loads(content.decode("utf-8"))

    if isinstance(data, dict):
        data = data.get("ideas", [data])
    if not isinstance(data, list):
        raise ValueError("JSON must be an array of ideas or an object with 'ideas' key.")

    ideas = []
    for item in data:
        if not isinstance(item, dict) or not item.get("title"):
            continue

        captured_at = None
        if item.get("captured_at"):
            try:
                captured_at = datetime.fromisoformat(str(item["captured_at"]))
                if captured_at.tzinfo is None:
                    captured_at = captured_at.replace(tzinfo=timezone.utc)
            except ValueError:
                pass

        ideas.append(IdeaCreate(
            title=str(item["title"]).strip(),
            description=str(item.get("description", "")).strip() or None,
            source=str(item.get("source", "")).strip() or None,
            tags=item.get("tags", []),
            captured_at=captured_at,
        ))

    return ideas
