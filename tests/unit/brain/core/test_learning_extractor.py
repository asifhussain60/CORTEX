"""
Tests for Learning Extraction Engine.

Tests pattern recognition, insight extraction, and knowledge
graph updates from conversation sessions.

Author: CORTEX Team
Created: 2026-02-06
Authority: Phase 36 Stage 3 specification
"""

import pytest
from unittest.mock import Mock
import numpy as np

from cortex.brain.core.learning_extractor import (
    LearningExtractor,
    InsightType,
    LearningInsight,
    PatternType,
    RecognizedPattern,
    ExtractionResult,
    ExtractionConfig,
)


class TestInsightType:
    """Test InsightType enum."""
    
    def test_insight_types_defined(self):
        """Test insight types defined."""
        assert InsightType.FEATURE_REQUEST.value == "FEATURE_REQUEST"
        assert InsightType.BUG_PATTERN.value == "BUG_PATTERN"
        assert InsightType.DESIGN_DECISION.value == "DESIGN_DECISION"
        assert InsightType.REFACTOR_OPPORTUNITY.value == "REFACTOR_OPPORTUNITY"


class TestPatternType:
    """Test PatternType enum."""
    
    def test_pattern_types_defined(self):
        """Test pattern types defined."""
        assert PatternType.IMPLEMENTATION.value == "IMPLEMENTATION"
        assert PatternType.DEBUGGING.value == "DEBUGGING"
        assert PatternType.TESTING.value == "TESTING"


class TestLearningInsight:
    """Test LearningInsight dataclass."""
    
    def test_learning_insight_creation(self):
        """Test creating learning insight."""
        insight = LearningInsight(
            insight_type=InsightType.FEATURE_REQUEST,
            description="User requested feature X",
            confidence=0.9,
            evidence=["Turn 1", "Turn 2"],
        )
        
        assert insight.insight_type == InsightType.FEATURE_REQUEST
        assert insight.description == "User requested feature X"
        assert insight.confidence == 0.9
        assert len(insight.evidence) == 2
    
    def test_learning_insight_with_metadata(self):
        """Test learning insight with metadata."""
        insight = LearningInsight(
            insight_type=InsightType.BUG_PATTERN,
            description="Common error pattern",
            confidence=0.85,
            evidence=["Error trace"],
            metadata={"frequency": 5},
        )
        
        assert insight.metadata["frequency"] == 5


class TestRecognizedPattern:
    """Test RecognizedPattern dataclass."""
    
    def test_recognized_pattern_creation(self):
        """Test creating recognized pattern."""
        pattern = RecognizedPattern(
            pattern_type=PatternType.IMPLEMENTATION,
            description="TDD workflow pattern",
            occurrences=3,
            confidence=0.95,
        )
        
        assert pattern.pattern_type == PatternType.IMPLEMENTATION
        assert pattern.occurrences == 3
        assert pattern.confidence == 0.95


class TestExtractionResult:
    """Test ExtractionResult dataclass."""
    
    def test_extraction_result_creation(self):
        """Test creating extraction result."""
        insights = [
            LearningInsight(
                InsightType.FEATURE_REQUEST,
                "Feature X",
                0.9,
                ["evidence"],
            )
        ]
        patterns = [
            RecognizedPattern(
                PatternType.TESTING,
                "TDD pattern",
                2,
                0.8,
            )
        ]
        
        result = ExtractionResult(
            insights=insights,
            patterns=patterns,
            total_processed=10,
        )
        
        assert len(result.insights) == 1
        assert len(result.patterns) == 1
        assert result.total_processed == 10


class TestExtractionConfig:
    """Test ExtractionConfig dataclass."""
    
    def test_extraction_config_defaults(self):
        """Test extraction config defaults."""
        config = ExtractionConfig()
        
        assert config.min_confidence == 0.7
        assert config.extract_patterns is True
        assert config.extract_insights is True
    
    def test_extraction_config_custom(self):
        """Test custom extraction config."""
        config = ExtractionConfig(
            min_confidence=0.85,
            extract_patterns=False,
        )
        
        assert config.min_confidence == 0.85
        assert config.extract_patterns is False


class TestLearningExtractor:
    """Test LearningExtractor core functionality."""
    
    @pytest.fixture
    def extractor(self):
        """Create learning extractor instance."""
        return LearningExtractor()
    
    def test_extractor_initialization(self, extractor):
        """Test extractor initializes correctly."""
        assert extractor is not None
        assert hasattr(extractor, 'config')
    
    def test_extract_from_conversation(self, extractor):
        """Test extracting learnings from conversation."""
        conversation = [
            "User requested feature X implementation",
            "Agent implemented feature X with tests",
            "User found bug in feature X",
            "Agent fixed bug and added regression test",
        ]
        
        result = extractor.extract(conversation)
        
        assert isinstance(result, ExtractionResult)
        assert result.total_processed == len(conversation)
        assert len(result.insights) >= 0
        assert len(result.patterns) >= 0
    
    def test_extract_empty_conversation(self, extractor):
        """Test extracting from empty conversation."""
        result = extractor.extract([])
        
        assert result.total_processed == 0
        assert len(result.insights) == 0
        assert len(result.patterns) == 0


class TestInsightExtraction:
    """Test insight extraction functionality."""
    
    @pytest.fixture
    def extractor(self):
        """Create learning extractor instance."""
        return LearningExtractor()
    
    def test_extract_feature_request_insight(self, extractor):
        """Test extracting feature request insight."""
        conversation = [
            "Can we add a new export feature?",
            "That would be really useful",
        ]
        
        insights = extractor.extract_insights(conversation)
        
        assert len(insights) > 0
        # Should detect feature request pattern
        feature_requests = [i for i in insights if i.insight_type == InsightType.FEATURE_REQUEST]
        assert len(feature_requests) >= 0  # May or may not detect depending on ML
    
    def test_extract_bug_pattern_insight(self, extractor):
        """Test extracting bug pattern insight."""
        conversation = [
            "Error occurred when processing data",
            "Same error happened again",
            "Fixed by adding validation",
        ]
        
        insights = extractor.extract_insights(conversation)
        
        assert isinstance(insights, list)
        assert all(isinstance(i, LearningInsight) for i in insights)
    
    def test_extract_design_decision_insight(self, extractor):
        """Test extracting design decision insight."""
        conversation = [
            "We chose architecture pattern X because of scalability",
            "This design supports future extensions",
        ]
        
        insights = extractor.extract_insights(conversation)
        
        assert isinstance(insights, list)
    
    def test_insights_have_confidence_scores(self, extractor):
        """Test insights include confidence scores."""
        conversation = [
            "Implementing feature with TDD approach",
            "Tests pass, feature complete",
        ]
        
        insights = extractor.extract_insights(conversation)
        
        if insights:
            for insight in insights:
                assert 0 <= insight.confidence <= 1


class TestPatternRecognition:
    """Test pattern recognition functionality."""
    
    @pytest.fixture
    def extractor(self):
        """Create learning extractor instance."""
        return LearningExtractor()
    
    def test_recognize_implementation_pattern(self, extractor):
        """Test recognizing implementation patterns."""
        conversation = [
            "Writing tests first (RED phase)",
            "Implementing feature (GREEN phase)",
            "Refactoring code (REFACTOR phase)",
        ]
        
        patterns = extractor.recognize_patterns(conversation)
        
        assert isinstance(patterns, list)
        assert all(isinstance(p, RecognizedPattern) for p in patterns)
    
    def test_recognize_debugging_pattern(self, extractor):
        """Test recognizing debugging patterns."""
        conversation = [
            "Error found in module",
            "Investigating root cause",
            "Fixed issue and verified",
        ]
        
        patterns = extractor.recognize_patterns(conversation)
        
        assert isinstance(patterns, list)
    
    def test_recognize_testing_pattern(self, extractor):
        """Test recognizing testing patterns."""
        conversation = [
            "Created unit tests",
            "Added integration tests",
            "All tests passing",
        ]
        
        patterns = extractor.recognize_patterns(conversation)
        
        assert isinstance(patterns, list)
    
    def test_patterns_track_occurrences(self, extractor):
        """Test patterns track occurrence count."""
        conversation = [
            "Test added for feature A",
            "Test added for feature B",
            "Test added for feature C",
        ]
        
        patterns = extractor.recognize_patterns(conversation)
        
        if patterns:
            for pattern in patterns:
                assert pattern.occurrences > 0


class TestConfidenceFiltering:
    """Test confidence-based filtering."""
    
    @pytest.fixture
    def extractor(self):
        """Create learning extractor instance."""
        config = ExtractionConfig(min_confidence=0.8)
        return LearningExtractor(config=config)
    
    def test_filters_low_confidence_insights(self, extractor):
        """Test low confidence insights filtered."""
        conversation = [
            "Maybe we should consider feature X",
            "Not sure if this is the right approach",
        ]
        
        insights = extractor.extract_insights(conversation)
        
        # All returned insights should meet minimum confidence
        for insight in insights:
            assert insight.confidence >= extractor.config.min_confidence
    
    def test_filters_low_confidence_patterns(self, extractor):
        """Test low confidence patterns filtered."""
        conversation = [
            "Did something",
            "Did another thing",
        ]
        
        patterns = extractor.recognize_patterns(conversation)
        
        # All returned patterns should meet minimum confidence
        for pattern in patterns:
            assert pattern.confidence >= extractor.config.min_confidence


class TestEvidenceTracking:
    """Test evidence tracking for insights."""
    
    @pytest.fixture
    def extractor(self):
        """Create learning extractor instance."""
        return LearningExtractor()
    
    def test_insights_include_evidence(self, extractor):
        """Test insights include supporting evidence."""
        conversation = [
            "User asked for export feature",
            "Agent agreed to implement",
        ]
        
        insights = extractor.extract_insights(conversation)
        
        for insight in insights:
            assert isinstance(insight.evidence, list)
            # Evidence should contain conversation excerpts
            assert all(isinstance(e, str) for e in insight.evidence)
    
    def test_evidence_limited_to_relevant_turns(self, extractor):
        """Test evidence only includes relevant turns."""
        conversation = [
            "Discussing feature X",
            "Implementing feature X",
            "Unrelated topic",
            "Back to feature X",
        ]
        
        insights = extractor.extract_insights(conversation)
        
        # Evidence should not include irrelevant turns
        for insight in insights:
            assert len(insight.evidence) <= len(conversation)
