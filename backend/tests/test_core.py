"""
Idea Graveyard — Tests
Focused on high-risk paths: scoring, dedup, validation.
"""
import pytest
from services.scoring import calculate_relevance, _clamp
from models import Idea, ContentReference
from schemas import AnalysisResult, IdeaCreate


# ─── Scoring Engine ───

class TestScoring:
    def test_deterministic(self):
        """Same inputs must always produce same output."""
        result1 = calculate_relevance(88, 91, 94, 85, 78)
        result2 = calculate_relevance(88, 91, 94, 85, 78)
        assert result1 == result2

    def test_known_value(self):
        """Verify weighted calculation is correct."""
        # 88*0.30 + 91*0.25 + 94*0.20 + 85*0.15 + 78*0.10
        # = 26.4 + 22.75 + 18.8 + 12.75 + 7.8 = 88.5
        result = calculate_relevance(88, 91, 94, 85, 78)
        assert result == 88.5

    def test_all_zeros(self):
        result = calculate_relevance(0, 0, 0, 0, 0)
        assert result == 0.0

    def test_all_hundreds(self):
        result = calculate_relevance(100, 100, 100, 100, 100)
        assert result == 100.0

    def test_clamp_within_range(self):
        assert _clamp(50) == 50
        assert _clamp(0) == 0
        assert _clamp(100) == 100

    def test_clamp_out_of_range(self):
        assert _clamp(-10) == 0
        assert _clamp(150) == 100

    def test_extreme_inputs_clamped(self):
        """Scoring should handle out-of-range inputs gracefully."""
        result = calculate_relevance(150, -10, 50, 50, 50)
        # 100*0.30 + 0*0.25 + 50*0.20 + 50*0.15 + 50*0.10
        # = 30 + 0 + 10 + 7.5 + 5 = 52.5
        assert result == 52.5


# ─── Deduplication ───

class TestDedup:
    def test_fingerprint_deterministic(self):
        fp1 = Idea.make_fingerprint("Will AI Replace Junior Developers?", "brainstorm")
        fp2 = Idea.make_fingerprint("Will AI Replace Junior Developers?", "brainstorm")
        assert fp1 == fp2

    def test_fingerprint_case_insensitive(self):
        fp1 = Idea.make_fingerprint("WILL AI REPLACE JUNIOR DEVELOPERS?", "Brainstorm")
        fp2 = Idea.make_fingerprint("will ai replace junior developers?", "brainstorm")
        assert fp1 == fp2

    def test_fingerprint_strips_whitespace(self):
        fp1 = Idea.make_fingerprint("  Test Idea  ", "source")
        fp2 = Idea.make_fingerprint("Test Idea", "source")
        assert fp1 == fp2

    def test_fingerprint_different_titles(self):
        fp1 = Idea.make_fingerprint("Idea A")
        fp2 = Idea.make_fingerprint("Idea B")
        assert fp1 != fp2

    def test_content_ref_fingerprint(self):
        fp1 = ContentReference.make_fingerprint("Title", "http://example.com")
        fp2 = ContentReference.make_fingerprint("Title", "http://example.com")
        assert fp1 == fp2


# ─── Schema Validation ───

class TestValidation:
    def test_analysis_result_valid(self):
        result = AnalysisResult(
            audience_fit=88,
            content_fit=91,
            freshness=94,
            historical_fit=85,
            semantic_opportunity=78,
            summary="Test summary",
        )
        assert result.audience_fit == 88

    def test_analysis_result_out_of_range(self):
        with pytest.raises(Exception):
            AnalysisResult(
                audience_fit=150,  # should fail: > 100
                content_fit=91,
                freshness=94,
                historical_fit=85,
                semantic_opportunity=78,
                summary="Test",
            )

    def test_analysis_result_string_score(self):
        """LLM might return 'very high' instead of a number."""
        with pytest.raises(Exception):
            AnalysisResult(
                audience_fit="very high",  # type: ignore
                content_fit=91,
                freshness=94,
                historical_fit=85,
                semantic_opportunity=78,
                summary="Test",
            )

    def test_idea_create_empty_title(self):
        with pytest.raises(Exception):
            IdeaCreate(title="")

    def test_idea_create_valid(self):
        idea = IdeaCreate(title="Valid Idea", tags=["AI", "career"])
        assert idea.title == "Valid Idea"
        assert idea.tags == ["AI", "career"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
