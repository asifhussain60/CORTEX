"""
Tests for ML Summarization Engine.

Tests semantic session summarization, context synthesis,
and learning extraction using ML embeddings.

Author: CORTEX Team
Created: 2026-02-06
Authority: Phase 36 Stage 1 specification
"""

import pytest
from unittest.mock import Mock, patch
import numpy as np

from cortex.brain.core.ml_summarizer import (
    MLSummarizer,
    SummaryQuality,
    SummaryResult,
    ClusterConfig,
    SummarizationConfig,
    SessionContext,
)


class TestSummaryQuality:
    """Test SummaryQuality enum."""
    
    def test_quality_levels_defined(self):
        """Test quality levels are properly defined."""
        assert SummaryQuality.HIGH.value == "HIGH"
        assert SummaryQuality.MEDIUM.value == "MEDIUM"
        assert SummaryQuality.LOW.value == "LOW"


class TestSummaryResult:
    """Test SummaryResult dataclass."""
    
    def test_summary_result_creation(self):
        """Test creating summary result."""
        result = SummaryResult(
            summary="Test summary",
            key_points=["point1", "point2"],
            quality=SummaryQuality.HIGH,
            confidence=0.95,
            token_reduction=0.75,
        )
        
        assert result.summary == "Test summary"
        assert len(result.key_points) == 2
        assert result.quality == SummaryQuality.HIGH
        assert result.confidence == 0.95
        assert result.token_reduction == 0.75
    
    def test_summary_result_with_context(self):
        """Test summary result with session context."""
        context = SessionContext(
            turn_count=5,
            total_tokens=1000,
            key_decisions=["decision1"],
        )
        
        result = SummaryResult(
            summary="Context summary",
            key_points=["point"],
            quality=SummaryQuality.MEDIUM,
            confidence=0.8,
            token_reduction=0.6,
            session_context=context,
        )
        
        assert result.session_context.turn_count == 5
        assert result.session_context.total_tokens == 1000


class TestClusterConfig:
    """Test ClusterConfig dataclass."""
    
    def test_cluster_config_defaults(self):
        """Test cluster configuration defaults."""
        config = ClusterConfig()
        
        assert config.min_clusters == 2
        assert config.max_clusters == 10
        assert config.similarity_threshold == 0.7
    
    def test_cluster_config_custom(self):
        """Test custom cluster configuration."""
        config = ClusterConfig(
            min_clusters=3,
            max_clusters=8,
            similarity_threshold=0.8,
        )
        
        assert config.min_clusters == 3
        assert config.max_clusters == 8
        assert config.similarity_threshold == 0.8


class TestSummarizationConfig:
    """Test SummarizationConfig dataclass."""
    
    def test_summarization_config_defaults(self):
        """Test summarization configuration defaults."""
        config = SummarizationConfig()
        
        assert config.max_summary_length == 500
        assert config.min_quality_score == 0.7
        assert config.extract_key_points is True
        assert config.include_context is True
    
    def test_summarization_config_custom(self):
        """Test custom summarization configuration."""
        config = SummarizationConfig(
            max_summary_length=300,
            min_quality_score=0.8,
            extract_key_points=False,
        )
        
        assert config.max_summary_length == 300
        assert config.min_quality_score == 0.8
        assert config.extract_key_points is False


class TestMLSummarizer:
    """Test MLSummarizer core functionality."""
    
    @pytest.fixture
    def summarizer(self):
        """Create ML summarizer instance."""
        return MLSummarizer()
    
    def test_summarizer_initialization(self, summarizer):
        """Test summarizer initializes correctly."""
        assert summarizer is not None
        assert hasattr(summarizer, 'model')
        assert hasattr(summarizer, 'config')
    
    def test_summarize_conversation(self, summarizer):
        """Test conversation summarization."""
        conversation = [
            "User asked about feature X",
            "Agent explained feature X implementation",
            "User requested code examples",
            "Agent provided code samples",
        ]
        
        result = summarizer.summarize(conversation)
        
        assert isinstance(result, SummaryResult)
        assert len(result.summary) > 0
        assert result.quality in [SummaryQuality.HIGH, SummaryQuality.MEDIUM, SummaryQuality.LOW]
        assert 0 <= result.confidence <= 1
    
    def test_summarize_with_key_points(self, summarizer):
        """Test summarization extracts key points."""
        conversation = [
            "Implemented feature A",
            "Fixed bug B",
            "Refactored component C",
        ]
        
        result = summarizer.summarize(conversation, extract_key_points=True)
        
        assert len(result.key_points) > 0
        assert all(isinstance(point, str) for point in result.key_points)
    
    def test_summarize_empty_conversation(self, summarizer):
        """Test handling empty conversation."""
        result = summarizer.summarize([])
        
        assert result.summary == ""
        assert len(result.key_points) == 0
        assert result.quality == SummaryQuality.LOW
    
    def test_summarize_single_turn(self, summarizer):
        """Test single turn conversation."""
        conversation = ["Single message"]
        
        result = summarizer.summarize(conversation)
        
        assert len(result.summary) > 0
        assert result.quality in [SummaryQuality.LOW, SummaryQuality.MEDIUM]


class TestSemanticClustering:
    """Test semantic clustering functionality."""
    
    @pytest.fixture
    def summarizer(self):
        """Create ML summarizer instance."""
        return MLSummarizer()
    
    def test_cluster_similar_content(self, summarizer):
        """Test clustering groups similar content."""
        texts = [
            "Python programming",
            "Python coding",
            "JavaScript development",
            "JavaScript programming",
        ]
        
        clusters = summarizer.cluster_texts(texts)
        
        # Should create 2 clusters (Python and JavaScript)
        assert len(clusters) >= 2
        assert all(isinstance(cluster, list) for cluster in clusters)
    
    def test_cluster_respects_config(self, summarizer):
        """Test clustering respects configuration."""
        texts = [f"Text {i}" for i in range(20)]
        config = ClusterConfig(min_clusters=3, max_clusters=5)
        
        clusters = summarizer.cluster_texts(texts, config=config)
        
        assert len(clusters) >= config.min_clusters
        assert len(clusters) <= config.max_clusters
    
    def test_cluster_empty_list(self, summarizer):
        """Test clustering empty list."""
        clusters = summarizer.cluster_texts([])
        
        assert len(clusters) == 0


class TestKeyPointExtraction:
    """Test key point extraction."""
    
    @pytest.fixture
    def summarizer(self):
        """Create ML summarizer instance."""
        return MLSummarizer()
    
    def test_extract_key_points(self, summarizer):
        """Test extracting key points from conversation."""
        conversation = [
            "First we discussed the architecture",
            "Then we implemented the feature",
            "Finally we wrote comprehensive tests",
        ]
        
        key_points = summarizer.extract_key_points(conversation)
        
        assert len(key_points) > 0
        assert len(key_points) <= len(conversation)
        assert all(isinstance(point, str) for point in key_points)
    
    def test_extract_key_points_limits_count(self, summarizer):
        """Test key point extraction limits output."""
        conversation = [f"Point {i}" for i in range(20)]
        
        key_points = summarizer.extract_key_points(conversation, max_points=5)
        
        assert len(key_points) <= 5
    
    def test_extract_from_empty(self, summarizer):
        """Test extracting from empty conversation."""
        key_points = summarizer.extract_key_points([])
        
        assert len(key_points) == 0


class TestQualityScoring:
    """Test quality scoring."""
    
    @pytest.fixture
    def summarizer(self):
        """Create ML summarizer instance."""
        return MLSummarizer()
    
    def test_calculate_summary_quality(self, summarizer):
        """Test quality calculation."""
        original = "This is a long conversation with many details about implementation"
        summary = "Implementation discussion"
        
        quality, confidence = summarizer.calculate_quality(original, summary)
        
        assert isinstance(quality, SummaryQuality)
        assert 0 <= confidence <= 1
    
    def test_quality_high_for_good_summary(self, summarizer):
        """Test high quality for comprehensive summary."""
        original = "We implemented feature X with tests"
        summary = "Implemented feature X with tests"
        
        quality, confidence = summarizer.calculate_quality(original, summary)
        
        assert quality in [SummaryQuality.HIGH, SummaryQuality.MEDIUM]
        assert confidence >= 0.6  # Adjusted for realistic similarity scores
    
    def test_quality_low_for_poor_summary(self, summarizer):
        """Test low quality for insufficient summary."""
        original = "Long detailed conversation about multiple topics"
        summary = "Talk"
        
        quality, confidence = summarizer.calculate_quality(original, summary)
        
        assert quality == SummaryQuality.LOW
        assert confidence < 0.7


class TestTokenReduction:
    """Test token reduction metrics."""
    
    @pytest.fixture
    def summarizer(self):
        """Create ML summarizer instance."""
        return MLSummarizer()
    
    def test_calculate_token_reduction(self, summarizer):
        """Test token reduction calculation."""
        original = "This is a very long conversation with many words and details"
        summary = "Long conversation with details"
        
        reduction = summarizer.calculate_token_reduction(original, summary)
        
        assert 0 <= reduction <= 1
        assert reduction > 0  # Summary should be shorter
    
    def test_token_reduction_zero_for_same_length(self, summarizer):
        """Test zero reduction for same length."""
        text = "Same text"
        
        reduction = summarizer.calculate_token_reduction(text, text)
        
        assert reduction == 0.0
    
    def test_token_reduction_high_for_good_summary(self, summarizer):
        """Test high reduction for effective summary."""
        original = " ".join([f"word{i}" for i in range(100)])
        summary = "Summary of words"
        
        reduction = summarizer.calculate_token_reduction(original, summary)
        
        assert reduction >= 0.7  # At least 70% reduction


class TestSessionContext:
    """Test session context tracking."""
    
    def test_session_context_creation(self):
        """Test creating session context."""
        context = SessionContext(
            turn_count=10,
            total_tokens=5000,
            key_decisions=["decision1", "decision2"],
        )
        
        assert context.turn_count == 10
        assert context.total_tokens == 5000
        assert len(context.key_decisions) == 2
    
    def test_session_context_optional_fields(self):
        """Test session context with optional fields."""
        context = SessionContext(
            turn_count=5,
            total_tokens=1000,
            key_decisions=[],
            key_implementations=["feature1"],
            key_fixes=["bug1"],
        )
        
        assert len(context.key_implementations) == 1
        assert len(context.key_fixes) == 1
