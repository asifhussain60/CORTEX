"""
Tests for Duplication Detection (Phase 4)
Validates FTS5 integration, keyword extraction, similarity scoring, and merge options.

RED Phase Test Creation - These tests should fail initially.
"""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
from datetime import datetime

from src.operations.modules.learning.duplication_detector import (
    DuplicationDetector,
    DuplicateMatch,
    extract_keywords
)
from src.operations.modules.learning.lesson_capture import CapturedLesson


@pytest.fixture
def sample_lesson():
    """Create sample captured lesson for testing."""
    return CapturedLesson(
        problem="Payment processing failed with null pointer exception",
        root_cause="Missing null check in payment validator",
        solution="Added null checks before processing payment data",
        prevention_rules=["Always validate inputs before processing", "Use Optional types"],
        time_cost="2h",
        commit_hash="abc123",
        confidence=0.85
    )


@pytest.fixture
def duplication_detector():
    """Create DuplicationDetector instance with mocked KnowledgeGraph."""
    with patch('src.operations.modules.learning.duplication_detector.KnowledgeGraph') as mock_kg:
        detector = DuplicationDetector()
        detector.kg = mock_kg.return_value
        return detector


class TestKeywordExtraction:
    """Test keyword extraction from captured lessons."""
    
    def test_extract_keywords_from_problem(self, sample_lesson):
        """Test that keywords are extracted from problem field."""
        keywords = extract_keywords(sample_lesson)
        
        assert isinstance(keywords, list)
        assert len(keywords) > 0
        assert "payment" in keywords
        assert "processing" in keywords
        assert "null" in keywords
        
    def test_extract_keywords_filters_stopwords(self, sample_lesson):
        """Test that common stopwords are filtered out."""
        keywords = extract_keywords(sample_lesson)
        
        # Common stopwords should be excluded
        assert "the" not in keywords
        assert "with" not in keywords
        assert "in" not in keywords
        
    def test_extract_keywords_includes_solution_and_root_cause(self, sample_lesson):
        """Test that keywords include terms from solution and root_cause."""
        keywords = extract_keywords(sample_lesson)
        
        # From root_cause: "validator"
        assert "validator" in keywords
        # From solution: "checks"
        assert "checks" in keywords


class TestFTS5Integration:
    """Test FTS5 full-text search integration with Tier 2."""
    
    def test_search_existing_lessons(self, duplication_detector, sample_lesson):
        """Test that detector searches KnowledgeGraph FTS5 index."""
        # Mock FTS5 search results with high similarity
        duplication_detector.kg.search_lessons.return_value = [
            {
                'id': 'lesson-001',
                'problem': 'Payment processing failed with null pointer exception',
                'root_cause': 'Missing null check in validator',
                'solution': 'Added null checks before processing',
                'rank': 0.92
            }
        ]
        
        matches = duplication_detector.find_duplicates(sample_lesson, threshold=0.60)
        
        assert duplication_detector.kg.search_lessons.called
        assert len(matches) > 0
        
    def test_search_with_no_results(self, duplication_detector, sample_lesson):
        """Test handling when no duplicates found."""
        duplication_detector.kg.search_lessons.return_value = []
        
        matches = duplication_detector.find_duplicates(sample_lesson)
        
        assert isinstance(matches, list)
        assert len(matches) == 0
        
    def test_search_query_construction(self, duplication_detector, sample_lesson):
        """Test that search query is constructed from keywords."""
        duplication_detector.kg.search_lessons.return_value = []
        
        duplication_detector.find_duplicates(sample_lesson)
        
        # Verify search was called with keyword-based query
        call_args = duplication_detector.kg.search_lessons.call_args
        assert call_args is not None
        query = call_args[0][0]
        assert "payment" in query.lower()
        assert "null" in query.lower()


class TestSimilarityScoring:
    """Test similarity score calculation and thresholding."""
    
    def test_calculate_similarity_score_high_match(self, duplication_detector):
        """Test high similarity score for nearly identical lessons."""
        lesson1 = CapturedLesson(
            problem="Null pointer in payment processing",
            root_cause="Missing validation",
            solution="Added null checks",
            prevention_rules=["Validate inputs"],
            time_cost="2h",
            commit_hash="abc123",
            confidence=0.85
        )
        
        existing = {
            'problem': 'Null pointer in payment processing',
            'root_cause': 'Missing validation',
            'solution': 'Added null checks'
        }
        
        score = duplication_detector._calculate_similarity(lesson1, existing)
        
        assert score >= 0.85  # Very high similarity
        
    def test_calculate_similarity_score_low_match(self, duplication_detector):
        """Test low similarity score for different lessons."""
        lesson1 = CapturedLesson(
            problem="Database connection timeout",
            root_cause="Connection pool exhausted",
            solution="Increased pool size",
            prevention_rules=["Monitor connections"],
            time_cost="1h",
            commit_hash="xyz789",
            confidence=0.80
        )
        
        existing = {
            'problem': 'Null pointer in payment processing',
            'root_cause': 'Missing validation',
            'solution': 'Added null checks'
        }
        
        score = duplication_detector._calculate_similarity(lesson1, existing)
        
        assert score < 0.5  # Low similarity
        
    def test_threshold_filtering(self, duplication_detector, sample_lesson):
        """Test that only matches above threshold are returned."""
        # Mock FTS5 returns 3 results with different similarity
        duplication_detector.kg.search_lessons.return_value = [
            {'id': 'lesson-001', 'problem': 'Payment null error', 'solution': 'Added checks', 'rank': 0.85},
            {'id': 'lesson-002', 'problem': 'Similar payment issue', 'solution': 'Fixed validation', 'rank': 0.55},
            {'id': 'lesson-003', 'problem': 'Unrelated database issue', 'solution': 'Changed config', 'rank': 0.30}
        ]
        
        with patch.object(duplication_detector, '_calculate_similarity') as mock_calc:
            mock_calc.side_effect = [0.85, 0.55, 0.30]
            matches = duplication_detector.find_duplicates(sample_lesson, threshold=0.70)
        
        # Only lesson-001 (0.85) should pass threshold
        assert len(matches) == 1
        assert matches[0].lesson_id == 'lesson-001'


class TestDuplicateMatchStructure:
    """Test DuplicateMatch dataclass structure."""
    
    def test_duplicate_match_has_required_fields(self):
        """Test that DuplicateMatch contains all required fields."""
        match = DuplicateMatch(
            lesson_id="lesson-001",
            problem="Test problem",
            solution="Test solution",
            similarity_score=0.85,
            explanation="High keyword overlap"
        )
        
        assert match.lesson_id == "lesson-001"
        assert match.problem == "Test problem"
        assert match.solution == "Test solution"
        assert match.similarity_score == 0.85
        assert match.explanation == "High keyword overlap"
        
    def test_duplicate_matches_are_sortable_by_score(self):
        """Test that matches can be sorted by similarity score."""
        matches = [
            DuplicateMatch("l1", "p1", "s1", 0.75, ""),
            DuplicateMatch("l2", "p2", "s2", 0.90, ""),
            DuplicateMatch("l3", "p3", "s3", 0.65, "")
        ]
        
        sorted_matches = sorted(matches, key=lambda m: m.similarity_score, reverse=True)
        
        assert sorted_matches[0].similarity_score == 0.90
        assert sorted_matches[1].similarity_score == 0.75
        assert sorted_matches[2].similarity_score == 0.65
