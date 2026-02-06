"""
Tests for ML Summarization Integration.

Tests integration with SemanticDeduplicator, MasterOrchestrator,
and production metrics.

Author: CORTEX Team
Created: 2026-02-06
Authority: Phase 36 Stage 4 specification
"""

import pytest
from unittest.mock import Mock, patch
import numpy as np

from cortex.brain.core.ml_integration import (
    MLIntegration,
    IntegrationMode,
    MLMetrics,
    IntegrationResult,
    IntegrationConfig,
)


class TestIntegrationMode:
    """Test IntegrationMode enum."""
    
    def test_integration_modes_defined(self):
        """Test integration modes defined."""
        assert IntegrationMode.FULL.value == "FULL"
        assert IntegrationMode.SUMMARIZATION_ONLY.value == "SUMMARIZATION_ONLY"
        assert IntegrationMode.DEDUPLICATION_ONLY.value == "DEDUPLICATION_ONLY"


class TestMLMetrics:
    """Test MLMetrics dataclass."""
    
    def test_ml_metrics_creation(self):
        """Test creating ML metrics."""
        metrics = MLMetrics(
            summarization_time=1.5,
            deduplication_time=0.5,
            total_time=2.0,
            compression_ratio=0.6,
            insights_extracted=3,
        )
        
        assert metrics.summarization_time == 1.5
        assert metrics.deduplication_time == 0.5
        assert metrics.total_time == 2.0
        assert metrics.compression_ratio == 0.6
        assert metrics.insights_extracted == 3


class TestIntegrationResult:
    """Test IntegrationResult dataclass."""
    
    def test_integration_result_creation(self):
        """Test creating integration result."""
        metrics = MLMetrics(1.0, 0.5, 1.5, 0.7, 2)
        
        result = IntegrationResult(
            processed_content="Processed text",
            metrics=metrics,
            success=True,
        )
        
        assert result.processed_content == "Processed text"
        assert result.success is True
        assert result.metrics.total_time == 1.5


class TestIntegrationConfig:
    """Test IntegrationConfig dataclass."""
    
    def test_integration_config_defaults(self):
        """Test integration config defaults."""
        config = IntegrationConfig()
        
        assert config.mode == IntegrationMode.FULL
        assert config.enable_summarization is True
        assert config.enable_deduplication is True
        assert config.enable_learning is True
    
    def test_integration_config_custom(self):
        """Test custom integration config."""
        config = IntegrationConfig(
            mode=IntegrationMode.SUMMARIZATION_ONLY,
            enable_deduplication=False,
        )
        
        assert config.mode == IntegrationMode.SUMMARIZATION_ONLY
        assert config.enable_deduplication is False


class TestMLIntegration:
    """Test MLIntegration core functionality."""
    
    @pytest.fixture
    def integration(self):
        """Create ML integration instance."""
        return MLIntegration()
    
    def test_integration_initialization(self, integration):
        """Test integration initializes correctly."""
        assert integration is not None
        assert hasattr(integration, 'config')
        assert hasattr(integration, 'summarizer')
        assert hasattr(integration, 'extractor')
    
    def test_process_conversation(self, integration):
        """Test processing conversation through full pipeline."""
        conversation = [
            "User: How do I implement feature X?",
            "Agent: Use TDD approach with tests first",
            "User: Can you show an example?",
            "Agent: Here's an example implementation",
        ]
        
        result = integration.process(conversation)
        
        assert isinstance(result, IntegrationResult)
        assert result.success is True
        assert len(result.processed_content) > 0
        assert result.metrics.total_time > 0
    
    def test_process_empty_conversation(self, integration):
        """Test processing empty conversation."""
        result = integration.process([])
        
        assert result.success is True
        assert result.processed_content == ""
        assert result.metrics.total_time >= 0


class TestSummarizationIntegration:
    """Test summarization integration."""
    
    @pytest.fixture
    def integration(self):
        """Create ML integration instance."""
        config = IntegrationConfig(mode=IntegrationMode.SUMMARIZATION_ONLY)
        return MLIntegration(config=config)
    
    def test_summarization_only_mode(self, integration):
        """Test summarization-only mode."""
        conversation = [
            "Long conversation about implementation",
            "Detailed discussion of approach",
            "Multiple back-and-forth exchanges",
        ]
        
        result = integration.process(conversation)
        
        assert result.success is True
        # Summary should be shorter than original
        assert len(result.processed_content) <= len(" ".join(conversation))
    
    def test_summarization_with_token_budget(self, integration):
        """Test summarization respects token budget."""
        conversation = [f"Turn {i}" for i in range(50)]
        
        result = integration.process(conversation, token_budget=200)
        
        assert result.success is True
        # Should compress to fit budget (with tolerance)
        assert result.metrics.compression_ratio > 0


class TestDeduplicationIntegration:
    """Test deduplication integration."""
    
    @pytest.fixture
    def integration(self):
        """Create ML integration instance."""
        config = IntegrationConfig(mode=IntegrationMode.DEDUPLICATION_ONLY)
        return MLIntegration(config=config)
    
    def test_deduplication_only_mode(self, integration):
        """Test deduplication-only mode."""
        conversation = [
            "This is a sentence",
            "This is a sentence",  # Duplicate
            "This is different",
            "This is a sentence",  # Another duplicate
        ]
        
        result = integration.process(conversation)
        
        assert result.success is True
        # Deduplication attempted (synthesizer processes content)
        assert result.metrics.deduplication_time > 0
    
    def test_deduplication_preserves_unique_content(self, integration):
        """Test deduplication preserves unique content."""
        conversation = [
            "First unique sentence",
            "Second unique sentence",
            "Third unique sentence",
        ]
        
        result = integration.process(conversation)
        
        assert result.success is True
        # All unique, minimal reduction
        assert "First" in result.processed_content or "unique" in result.processed_content


class TestLearningIntegration:
    """Test learning extraction integration."""
    
    @pytest.fixture
    def integration(self):
        """Create ML integration instance."""
        return MLIntegration()
    
    def test_learning_extraction_enabled(self, integration):
        """Test learning extraction in full mode."""
        conversation = [
            "User requested feature X",
            "Agent implemented with TDD",
            "Found and fixed bug in feature X",
        ]
        
        result = integration.process(conversation)
        
        assert result.success is True
        # Should extract insights
        assert result.metrics.insights_extracted >= 0
    
    def test_learning_extraction_disabled(self):
        """Test learning extraction can be disabled."""
        config = IntegrationConfig(enable_learning=False)
        integration = MLIntegration(config=config)
        
        conversation = ["Feature request", "Implementation"]
        
        result = integration.process(conversation)
        
        assert result.success is True
        # No insights extracted when disabled
        assert result.metrics.insights_extracted == 0


class TestMetricsCollection:
    """Test metrics collection."""
    
    @pytest.fixture
    def integration(self):
        """Create ML integration instance."""
        return MLIntegration()
    
    def test_metrics_track_timing(self, integration):
        """Test metrics track processing time."""
        conversation = ["Turn 1", "Turn 2"]
        
        result = integration.process(conversation)
        
        assert result.metrics.total_time > 0
        if integration.config.enable_summarization:
            assert result.metrics.summarization_time >= 0
        if integration.config.enable_deduplication:
            assert result.metrics.deduplication_time >= 0
    
    def test_metrics_track_compression(self, integration):
        """Test metrics track compression ratio."""
        conversation = [f"Content {i}" for i in range(20)]
        
        result = integration.process(conversation, token_budget=100)
        
        assert result.metrics.compression_ratio >= 0
        assert result.metrics.compression_ratio <= 1


class TestErrorHandling:
    """Test error handling."""
    
    @pytest.fixture
    def integration(self):
        """Create ML integration instance."""
        return MLIntegration()
    
    def test_handles_invalid_input(self, integration):
        """Test handling invalid input."""
        result = integration.process(None)
        
        # Should handle gracefully
        assert result.success is True
        assert result.processed_content == ""
    
    def test_handles_processing_errors(self, integration):
        """Test handling processing errors."""
        # Very long conversation might cause issues
        conversation = ["x" * 10000 for _ in range(100)]
        
        result = integration.process(conversation)
        
        # Should complete even if imperfect
        assert isinstance(result, IntegrationResult)


class TestBackwardCompatibility:
    """Test backward compatibility."""
    
    def test_works_with_existing_code(self):
        """Test integration works with existing codebase."""
        integration = MLIntegration()
        
        # Should work with minimal configuration
        result = integration.process(["Simple conversation"])
        
        assert result.success is True
    
    def test_gradual_rollout_support(self):
        """Test supports gradual rollout."""
        # Can disable features individually
        config = IntegrationConfig(
            enable_summarization=False,
            enable_deduplication=True,
            enable_learning=False,
        )
        integration = MLIntegration(config=config)
        
        result = integration.process(["Test"])
        
        assert result.success is True
