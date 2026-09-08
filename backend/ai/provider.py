"""
Idea Graveyard — AI Provider
Sole integration point for Google Gemini SDK.
No other module should import google.generativeai.
"""
import json
import logging
from typing import Optional

import google.generativeai as genai

from config import settings
from schemas import AnalysisResult, WhyNowResult, ContentBriefResult

logger = logging.getLogger(__name__)

# Configure on module load
if settings.gemini_api_key:
    genai.configure(api_key=settings.gemini_api_key)

_model: Optional[genai.GenerativeModel] = None


def _get_model() -> genai.GenerativeModel:
    global _model
    if _model is None:
        _model = genai.GenerativeModel(settings.gemini_model)
    return _model


def _call_gemini(prompt: str, max_retries: int = 1) -> str:
    """
    Call Gemini with timeout, retry, and error handling.
    Returns raw text response.
    """
    model = _get_model()
    last_error = None

    for attempt in range(max_retries + 1):
        try:
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,
                    max_output_tokens=2048,
                ),
                request_options={"timeout": 30},
            )
            return response.text
        except Exception as e:
            last_error = e
            logger.warning(f"Gemini call attempt {attempt + 1} failed: {e}")

    raise RuntimeError(f"Gemini call failed after {max_retries + 1} attempts: {last_error}")


def _parse_json_response(text: str) -> dict:
    """Extract JSON from Gemini response, handling markdown fences."""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        # Remove markdown code fences
        lines = cleaned.split("\n")
        # Drop first and last lines (fences)
        lines = [l for l in lines[1:] if not l.strip().startswith("```")]
        cleaned = "\n".join(lines)
    return json.loads(cleaned)


def analyze_idea(
    idea_title: str,
    idea_description: str,
    content_refs: list[dict],
) -> AnalysisResult:
    """
    Analyze an idea against content references.
    Returns validated AnalysisResult or raises.
    """
    refs_text = "\n".join(
        f"- \"{r['title']}\" (performance: {r.get('performance_metric', 'N/A')}, "
        f"tags: {r.get('tags', [])}, published: {r.get('published_at', 'N/A')})"
        for r in content_refs
    )

    prompt = f"""You are an editorial content strategist analyzing whether a forgotten content idea is worth revisiting.

IDEA: {idea_title}
DESCRIPTION: {idea_description or 'No description provided.'}

RECENT/HISTORICAL CONTENT PERFORMANCE:
{refs_text}

Score this idea on 5 dimensions (each 0-100):

1. audience_fit: How well does this idea match the audience that engaged with the high-performing content above?
2. content_fit: How well does this idea align with the content themes that performed well?
3. freshness: Is this idea timely right now? Has the landscape changed to make it relevant?
4. historical_fit: Does historical performance data suggest this topic resonates?
5. semantic_opportunity: Is there a gap in the existing content that this idea could fill?

Also provide a brief summary (2-3 sentences) explaining your assessment.

Respond ONLY with valid JSON in this exact format:
{{
  "audience_fit": <number>,
  "content_fit": <number>,
  "freshness": <number>,
  "historical_fit": <number>,
  "semantic_opportunity": <number>,
  "summary": "<string>"
}}"""

    raw = _call_gemini(prompt)
    try:
        data = _parse_json_response(raw)
        return AnalysisResult(**data)
    except Exception as e:
        logger.error(f"Failed to parse analysis response: {e}\nRaw: {raw}")
        # Retry once with stricter prompt
        raw2 = _call_gemini(prompt + "\n\nIMPORTANT: Return ONLY valid JSON. No markdown. No explanation.")
        data2 = _parse_json_response(raw2)
        return AnalysisResult(**data2)


def generate_why_now(
    idea_title: str,
    idea_description: str,
    analysis_summary: str,
    content_refs: list[dict],
) -> WhyNowResult:
    """
    Generate a 'Why Now' narrative explaining why this idea is worth revisiting.
    """
    refs_text = "\n".join(
        f"- \"{r['title']}\" (performance: {r.get('performance_metric', 'N/A')}, "
        f"tags: {r.get('tags', [])})"
        for r in content_refs[:5]
    )

    prompt = f"""You are an editorial strategist explaining why a forgotten content idea deserves attention NOW.

IDEA: {idea_title}
DESCRIPTION: {idea_description or 'No description.'}
ANALYSIS: {analysis_summary}

RECENT HIGH-PERFORMING CONTENT:
{refs_text}

Write a concise narrative (3-5 sentences) explaining what changed in the landscape that makes this idea timely.
Also list 2-4 specific key changes that create this opportunity.

Be specific. Reference the actual content data above. Avoid generic statements.

Respond ONLY with valid JSON:
{{
  "narrative": "<string>",
  "key_changes": ["<string>", "<string>", ...]
}}"""

    raw = _call_gemini(prompt)
    try:
        data = _parse_json_response(raw)
        return WhyNowResult(**data)
    except Exception as e:
        logger.error(f"Failed to parse why_now response: {e}\nRaw: {raw}")
        raw2 = _call_gemini(prompt + "\n\nIMPORTANT: Return ONLY valid JSON.")
        data2 = _parse_json_response(raw2)
        return WhyNowResult(**data2)


def generate_content_brief(
    idea_title: str,
    idea_description: str,
    analysis_summary: str,
    why_now: str,
) -> ContentBriefResult:
    """
    Generate an actionable content brief for a resurrected idea.
    """
    prompt = f"""You are an editorial content strategist creating an actionable content brief.

IDEA: {idea_title}
DESCRIPTION: {idea_description or 'No description.'}
ANALYSIS: {analysis_summary}
WHY NOW: {why_now}

Create a content brief with:
1. new_angle: A fresh angle for this idea based on what changed (1-2 sentences)
2. title: A compelling, specific title for this content piece
3. hook: An opening hook that would grab the audience (2-3 sentences)
4. structure: An ordered list of 4-6 section headings for the content
5. key_points: 3-5 key points the content should cover

Be specific and actionable. Avoid generic advice.

Respond ONLY with valid JSON:
{{
  "new_angle": "<string>",
  "title": "<string>",
  "hook": "<string>",
  "structure": ["<string>", ...],
  "key_points": ["<string>", ...]
}}"""

    raw = _call_gemini(prompt)
    try:
        data = _parse_json_response(raw)
        return ContentBriefResult(**data)
    except Exception as e:
        logger.error(f"Failed to parse content_brief response: {e}\nRaw: {raw}")
        raw2 = _call_gemini(prompt + "\n\nIMPORTANT: Return ONLY valid JSON.")
        data2 = _parse_json_response(raw2)
        return ContentBriefResult(**data2)
