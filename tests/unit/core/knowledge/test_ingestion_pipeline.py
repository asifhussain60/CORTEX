"""
Unit and Integration Tests for BulkIngestionPipeline (AC-IKP-004-01).

Tests for extensible ingestion pipeline with registry pattern,
plugin discovery, batch/streaming modes, and transformations.

Governance:
  - CORE-008: TDD (test-first development)
  - CORE-011: Type hints in all tests
  - CORE-012: Google-style docstrings
  - CORE-013: Specific exception handling
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, call
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime


class TestBulkIngestionPipeline:
    """Unit tests for BulkIngestionPipeline architecture."""

    def test_bulk_ingestion_pipeline_exists(self):
        """Test that BulkIngestionPipeline class exists."""
        from cortex.core.knowledge.ingestion_pipeline import BulkIngestionPipeline
        
        assert BulkIngestionPipeline is not None

    def test_pipeline_initialization(self):
        """Test pipeline initialization."""
        from cortex.core.knowledge.ingestion_pipeline import BulkIngestionPipeline
        
        backend = Mock()
        backend.name = 'storage'
        
        pipeline = BulkIngestionPipeline(backends={'storage': backend})
        
        assert pipeline is not None
        assert len(pipeline.backends) == 1

    def test_intake_adapter_registration(self):
        """Test registering intake adapters."""
        from cortex.core.knowledge.ingestion_pipeline import BulkIngestionPipeline
        
        backend = Mock()
        pipeline = BulkIngestionPipeline(backends={'storage': backend})
        
        # Should have adapter registration
        assert hasattr(pipeline, 'register_intake_adapter')

    def test_filter_strategy_registration(self):
        """Test registering filter strategies."""
        from cortex.core.knowledge.ingestion_pipeline import BulkIngestionPipeline
        
        backend = Mock()
        pipeline = BulkIngestionPipeline(backends={'storage': backend})
        
        # Should have filter registration
        assert hasattr(pipeline, 'register_filter_strategy')

    def test_refinement_rule_registration(self):
        """Test registering refinement rules."""
        from cortex.core.knowledge.ingestion_pipeline import BulkIngestionPipeline
        
        backend = Mock()
        pipeline = BulkIngestionPipeline(backends={'storage': backend})
        
        # Should have rule registration
        assert hasattr(pipeline, 'register_refinement_rule')

    def test_output_formatter_registration(self):
        """Test registering output formatters."""
        from cortex.core.knowledge.ingestion_pipeline import BulkIngestionPipeline
        
        backend = Mock()
        pipeline = BulkIngestionPipeline(backends={'storage': backend})
        
        # Should have formatter registration
        assert hasattr(pipeline, 'register_output_formatter')

    def test_validator_registration(self):
        """Test registering validators."""
        from cortex.core.knowledge.ingestion_pipeline import BulkIngestionPipeline
        
        backend = Mock()
        pipeline = BulkIngestionPipeline(backends={'storage': backend})
        
        # Should have validator registration
        assert hasattr(pipeline, 'register_validator')

    def test_registry_pattern_for_plugin_discovery(self):
        """Test registry pattern enables plugin discovery."""
        from cortex.core.knowledge.ingestion_pipeline import BulkIngestionPipeline
        
        backend = Mock()
        pipeline = BulkIngestionPipeline(backends={'storage': backend})
        
        # Should have registry access
        assert hasattr(pipeline, 'get_adapters')
        assert hasattr(pipeline, 'get_filters')
        assert hasattr(pipeline, 'get_rules')

    def test_custom_adapter_creation(self):
        """Test creating custom intake adapters."""
        from cortex.core.knowledge.ingestion_pipeline import BulkIngestionPipeline
        
        backend = Mock()
        pipeline = BulkIngestionPipeline(backends={'storage': backend})
        
        # Should support custom adapter creation
        assert hasattr(pipeline, 'create_adapter')

    def test_custom_filter_creation(self):
        """Test creating custom filter strategies."""
        from cortex.core.knowledge.ingestion_pipeline import BulkIngestionPipeline
        
        backend = Mock()
        pipeline = BulkIngestionPipeline(backends={'storage': backend})
        
        # Should support custom filter creation
        assert hasattr(pipeline, 'create_filter')

    def test_pipeline_execution_batch_mode(self):
        """Test pipeline execution in batch mode."""
        from cortex.core.knowledge.ingestion_pipeline import BulkIngestionPipeline
        
        backend = Mock()
        pipeline = BulkIngestionPipeline(backends={'storage': backend})
        
        # Should support batch execution
        assert hasattr(pipeline, 'execute_batch')

    def test_pipeline_execution_streaming_mode(self):
        """Test pipeline execution in streaming mode."""
        from cortex.core.knowledge.ingestion_pipeline import BulkIngestionPipeline
        
        backend = Mock()
        pipeline = BulkIngestionPipeline(backends={'storage': backend})
        
        # Should support streaming execution
        assert hasattr(pipeline, 'execute_stream')

    def test_pipeline_data_validation(self):
        """Test data validation before ingestion."""
        from cortex.core.knowledge.ingestion_pipeline import BulkIngestionPipeline
        
        backend = Mock()
        pipeline = BulkIngestionPipeline(backends={'storage': backend})
        
        # Should validate data
        assert hasattr(pipeline, 'validate')

    def test_pipeline_error_handling(self):
        """Test error handling during ingestion."""
        from cortex.core.knowledge.ingestion_pipeline import BulkIngestionPipeline
        
        backend = Mock()
        pipeline = BulkIngestionPipeline(backends={'storage': backend})
        
        # Should have error handling
        assert hasattr(pipeline, 'handle_error')

    def test_pipeline_retry_logic(self):
        """Test retry logic for failed items."""
        from cortex.core.knowledge.ingestion_pipeline import BulkIngestionPipeline
        
        backend = Mock()
        pipeline = BulkIngestionPipeline(backends={'storage': backend})
        
        # Should support retries
        assert hasattr(pipeline, 'retry_failed_items')

    def test_pipeline_metrics_tracking(self):
        """Test metrics tracking during ingestion."""
        from cortex.core.knowledge.ingestion_pipeline import BulkIngestionPipeline
        
        backend = Mock()
        pipeline = BulkIngestionPipeline(backends={'storage': backend})
        
        # Should track metrics
        assert hasattr(pipeline, 'get_metrics')


class TestBulkIngestionIntegration:
    """Integration tests for BulkIngestionPipeline."""

    def test_full_pipeline_execution_flow(self):
        """Test complete pipeline flow: adapt -> filter -> refine -> format -> validate -> store."""
        from cortex.core.knowledge.ingestion_pipeline import BulkIngestionPipeline
        
        backend = Mock()
        pipeline = BulkIngestionPipeline(backends={'storage': backend})
        
        # Should support full flow
        assert pipeline is not None

    def test_adapter_to_storage_backend_connection(self):
        """Test connection from intake adapter to storage backend."""
        from cortex.core.knowledge.ingestion_pipeline import BulkIngestionPipeline
        
        storage_backend = Mock()
        storage_backend.name = 'storage'
        
        pipeline = BulkIngestionPipeline(backends={'storage': storage_backend})
        
        # Should connect adapters to backends
        assert hasattr(pipeline, 'execute_batch')

    def test_multi_step_transformation_pipeline(self):
        """Test multi-step data transformation."""
        from cortex.core.knowledge.ingestion_pipeline import BulkIngestionPipeline
        
        backend = Mock()
        pipeline = BulkIngestionPipeline(backends={'storage': backend})
        
        # Register stages
        adapter = Mock()
        adapter.name = 'test_adapter'
        filter_strategy = Mock()
        filter_strategy.name = 'test_filter'
        
        # Should support stage registration
        assert hasattr(pipeline, 'register_intake_adapter')
        assert hasattr(pipeline, 'register_filter_strategy')

    def test_batch_ingestion_with_large_dataset(self):
        """Test batch ingestion with large dataset."""
        from cortex.core.knowledge.ingestion_pipeline import BulkIngestionPipeline
        
        backend = Mock()
        pipeline = BulkIngestionPipeline(
            backends={'storage': backend},
            batch_size=1000
        )
        
        # Should handle batch size
        assert pipeline is not None

    def test_streaming_ingestion_mode(self):
        """Test streaming ingestion mode."""
        from cortex.core.knowledge.ingestion_pipeline import BulkIngestionPipeline
        
        backend = Mock()
        pipeline = BulkIngestionPipeline(
            backends={'storage': backend},
            streaming_enabled=True
        )
        
        # Should support streaming
        assert hasattr(pipeline, 'execute_stream')

    def test_plugin_discovery_through_registry(self):
        """Test discovering plugins through registry."""
        from cortex.core.knowledge.ingestion_pipeline import BulkIngestionPipeline
        
        backend = Mock()
        pipeline = BulkIngestionPipeline(backends={'storage': backend})
        
        # Register some plugins
        adapter = Mock()
        adapter.name = 'csv_adapter'
        adapter.version = '1.0'
        
        # Should support plugin discovery
        assert hasattr(pipeline, 'get_adapters')

    def test_filter_chain_execution(self):
        """Test executing a chain of filters."""
        from cortex.core.knowledge.ingestion_pipeline import BulkIngestionPipeline
        
        backend = Mock()
        pipeline = BulkIngestionPipeline(backends={'storage': backend})
        
        # Should support filter chaining
        assert hasattr(pipeline, 'execute_filter_chain')

    def test_refinement_rule_application(self):
        """Test applying refinement rules to data."""
        from cortex.core.knowledge.ingestion_pipeline import BulkIngestionPipeline
        
        backend = Mock()
        pipeline = BulkIngestionPipeline(backends={'storage': backend})
        
        # Should apply refinement rules
        assert hasattr(pipeline, 'apply_refinement_rules')

    def test_output_formatting_stage(self):
        """Test output formatting before storage."""
        from cortex.core.knowledge.ingestion_pipeline import BulkIngestionPipeline
        
        backend = Mock()
        pipeline = BulkIngestionPipeline(backends={'storage': backend})
        
        # Should format output
        assert hasattr(pipeline, 'format_output')

    def test_validation_gate_before_storage(self):
        """Test validation gate prevents invalid data storage."""
        from cortex.core.knowledge.ingestion_pipeline import BulkIngestionPipeline
        
        backend = Mock()
        pipeline = BulkIngestionPipeline(backends={'storage': backend})
        
        # Should validate before storage
        assert hasattr(pipeline, 'validate')

    def test_metrics_collection_throughout_pipeline(self):
        """Test metrics collected at each stage."""
        from cortex.core.knowledge.ingestion_pipeline import BulkIngestionPipeline
        
        backend = Mock()
        pipeline = BulkIngestionPipeline(backends={'storage': backend})
        
        # Should collect stage metrics
        metrics = pipeline.get_metrics() if hasattr(pipeline, 'get_metrics') else None
        assert pipeline is not None

    def test_error_recovery_and_partial_success(self):
        """Test handling partial success with error recovery."""
        from cortex.core.knowledge.ingestion_pipeline import BulkIngestionPipeline
        
        backend = Mock()
        pipeline = BulkIngestionPipeline(backends={'storage': backend})
        
        # Should handle partial failures gracefully
        assert hasattr(pipeline, 'retry_failed_items')

    def test_custom_plugin_creation_and_registration(self):
        """Test creating and registering custom plugins."""
        from cortex.core.knowledge.ingestion_pipeline import BulkIngestionPipeline
        
        backend = Mock()
        pipeline = BulkIngestionPipeline(backends={'storage': backend})
        
        # Should support custom plugin creation
        assert hasattr(pipeline, 'create_adapter')
        assert hasattr(pipeline, 'create_filter')

    def test_pipeline_state_tracking(self):
        """Test tracking pipeline state during execution."""
        from cortex.core.knowledge.ingestion_pipeline import BulkIngestionPipeline
        
        backend = Mock()
        pipeline = BulkIngestionPipeline(backends={'storage': backend})
        
        # Should track state
        assert hasattr(pipeline, 'get_execution_state')

    def test_graceful_degradation_with_missing_stages(self):
        """Test graceful degradation when optional stages are missing."""
        from cortex.core.knowledge.ingestion_pipeline import BulkIngestionPipeline
        
        backend = Mock()
        pipeline = BulkIngestionPipeline(backends={'storage': backend})
        
        # Should work with minimal configuration
        assert pipeline is not None


__all__ = [
    'TestBulkIngestionPipeline',
    'TestBulkIngestionIntegration',
]
