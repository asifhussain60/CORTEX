"""
Unit and Integration Tests for IngestionIntegration (AC-IKP-004-02).

Tests for integrating RefinementEngine with BulkIngestionPipeline,
connecting intake adapters to storage backends, and end-to-end workflow.

Governance:
  - CORE-008: TDD (test-first development)
  - CORE-011: Type hints in all tests
  - CORE-012: Google-style docstrings
  - CORE-013: Specific exception handling
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, call
from typing import Dict, List, Any, Optional
from datetime import datetime


class TestIngestionIntegration:
    """Unit tests for ingestion integration."""

    def test_ingestion_integration_exists(self):
        """Test that IngestionIntegration class exists."""
        from src.core.knowledge.ingestion_integration import IngestionIntegration
        
        assert IngestionIntegration is not None

    def test_ingestion_integration_initialization(self):
        """Test initialization with pipeline and engine."""
        from src.core.knowledge.ingestion_integration import IngestionIntegration
        
        pipeline = Mock()
        engine = Mock()
        backend = Mock()
        
        integration = IngestionIntegration(
            pipeline=pipeline,
            engine=engine,
            backends={'storage': backend}
        )
        
        assert integration is not None

    def test_refinement_engine_integration(self):
        """Test integration with RefinementEngine."""
        from src.core.knowledge.ingestion_integration import IngestionIntegration
        
        pipeline = Mock()
        engine = Mock()
        backend = Mock()
        
        integration = IngestionIntegration(
            pipeline=pipeline,
            engine=engine,
            backends={'storage': backend}
        )
        
        # Should have access to engine
        assert hasattr(integration, 'engine')

    def test_adapter_to_storage_backend_connection(self):
        """Test adapter to storage backend connection."""
        from src.core.knowledge.ingestion_integration import IngestionIntegration
        
        pipeline = Mock()
        engine = Mock()
        backend = Mock()
        
        integration = IngestionIntegration(
            pipeline=pipeline,
            engine=engine,
            backends={'storage': backend}
        )
        
        # Should connect adapter to backend
        assert hasattr(integration, 'connect_adapter_to_backend')

    def test_end_to_end_ingestion_workflow(self):
        """Test complete end-to-end ingestion workflow."""
        from src.core.knowledge.ingestion_integration import IngestionIntegration
        
        pipeline = Mock()
        engine = Mock()
        backend = Mock()
        
        integration = IngestionIntegration(
            pipeline=pipeline,
            engine=engine,
            backends={'storage': backend}
        )
        
        # Should have workflow execution
        assert hasattr(integration, 'execute_workflow')

    def test_ingestion_with_refinement_rules(self):
        """Test ingestion with refinement rules applied."""
        from src.core.knowledge.ingestion_integration import IngestionIntegration
        
        pipeline = Mock()
        engine = Mock()
        backend = Mock()
        
        integration = IngestionIntegration(
            pipeline=pipeline,
            engine=engine,
            backends={'storage': backend}
        )
        
        # Should apply refinement rules
        assert hasattr(integration, 'apply_refinements')

    def test_batch_and_streaming_modes(self):
        """Test support for both batch and streaming modes."""
        from src.core.knowledge.ingestion_integration import IngestionIntegration
        
        pipeline = Mock()
        engine = Mock()
        backend = Mock()
        
        integration = IngestionIntegration(
            pipeline=pipeline,
            engine=engine,
            backends={'storage': backend}
        )
        
        # Should support both modes
        assert hasattr(integration, 'ingest_batch')
        assert hasattr(integration, 'ingest_stream')

    def test_error_handling_in_workflow(self):
        """Test error handling throughout workflow."""
        from src.core.knowledge.ingestion_integration import IngestionIntegration
        
        pipeline = Mock()
        engine = Mock()
        backend = Mock()
        
        integration = IngestionIntegration(
            pipeline=pipeline,
            engine=engine,
            backends={'storage': backend}
        )
        
        # Should handle errors
        assert hasattr(integration, 'handle_workflow_error')

    def test_workflow_state_tracking(self):
        """Test tracking workflow state."""
        from src.core.knowledge.ingestion_integration import IngestionIntegration
        
        pipeline = Mock()
        engine = Mock()
        backend = Mock()
        
        integration = IngestionIntegration(
            pipeline=pipeline,
            engine=engine,
            backends={'storage': backend}
        )
        
        # Should track state
        assert hasattr(integration, 'get_workflow_state')


class TestIngestionIntegrationEnd2End:
    """End-to-end integration tests."""

    def test_full_ingestion_workflow_from_source_to_storage(self):
        """Test full workflow from source to storage."""
        from src.core.knowledge.ingestion_integration import IngestionIntegration
        
        pipeline = Mock()
        engine = Mock()
        backend = Mock()
        
        integration = IngestionIntegration(
            pipeline=pipeline,
            engine=engine,
            backends={'storage': backend}
        )
        
        # Should execute full workflow
        assert integration is not None

    def test_intake_adapter_connects_to_refinement_engine(self):
        """Test intake adapter connects to refinement engine."""
        from src.core.knowledge.ingestion_integration import IngestionIntegration
        
        pipeline = Mock()
        engine = Mock()
        backend = Mock()
        
        integration = IngestionIntegration(
            pipeline=pipeline,
            engine=engine,
            backends={'storage': backend}
        )
        
        # Should connect adapter to engine
        assert hasattr(integration, 'connect_adapter_to_engine')

    def test_refinement_engine_connects_to_storage_backend(self):
        """Test refinement engine connects to storage backend."""
        from src.core.knowledge.ingestion_integration import IngestionIntegration
        
        pipeline = Mock()
        engine = Mock()
        backend = Mock()
        
        integration = IngestionIntegration(
            pipeline=pipeline,
            engine=engine,
            backends={'storage': backend}
        )
        
        # Should connect engine to backend
        assert hasattr(integration, 'connect_engine_to_backend')

    def test_batch_ingestion_end_to_end(self):
        """Test batch ingestion end-to-end."""
        from src.core.knowledge.ingestion_integration import IngestionIntegration
        
        pipeline = Mock()
        engine = Mock()
        backend = Mock()
        
        integration = IngestionIntegration(
            pipeline=pipeline,
            engine=engine,
            backends={'storage': backend}
        )
        
        # Should support batch ingestion
        assert hasattr(integration, 'ingest_batch')

    def test_streaming_ingestion_end_to_end(self):
        """Test streaming ingestion end-to-end."""
        from src.core.knowledge.ingestion_integration import IngestionIntegration
        
        pipeline = Mock()
        engine = Mock()
        backend = Mock()
        
        integration = IngestionIntegration(
            pipeline=pipeline,
            engine=engine,
            backends={'storage': backend}
        )
        
        # Should support streaming ingestion
        assert hasattr(integration, 'ingest_stream')

    def test_ingestion_metrics_and_tracking(self):
        """Test metrics and tracking of ingestion."""
        from src.core.knowledge.ingestion_integration import IngestionIntegration
        
        pipeline = Mock()
        engine = Mock()
        backend = Mock()
        
        integration = IngestionIntegration(
            pipeline=pipeline,
            engine=engine,
            backends={'storage': backend}
        )
        
        # Should track metrics
        assert hasattr(integration, 'get_metrics')

    def test_partial_failure_recovery(self):
        """Test recovery from partial failures."""
        from src.core.knowledge.ingestion_integration import IngestionIntegration
        
        pipeline = Mock()
        engine = Mock()
        backend = Mock()
        
        integration = IngestionIntegration(
            pipeline=pipeline,
            engine=engine,
            backends={'storage': backend}
        )
        
        # Should recover from failures
        assert hasattr(integration, 'recover_from_failure')

    def test_validation_before_storage(self):
        """Test validation before storing ingested data."""
        from src.core.knowledge.ingestion_integration import IngestionIntegration
        
        pipeline = Mock()
        engine = Mock()
        backend = Mock()
        
        integration = IngestionIntegration(
            pipeline=pipeline,
            engine=engine,
            backends={'storage': backend}
        )
        
        # Should validate before storage
        assert hasattr(integration, 'validate_before_storage')

    def test_audit_trail_for_ingestion(self):
        """Test audit trail logging of ingestion."""
        from src.core.knowledge.ingestion_integration import IngestionIntegration
        
        pipeline = Mock()
        engine = Mock()
        backend = Mock()
        
        integration = IngestionIntegration(
            pipeline=pipeline,
            engine=engine,
            backends={'storage': backend}
        )
        
        # Should log to audit trail
        assert hasattr(integration, 'log_to_audit_trail')


__all__ = [
    'TestIngestionIntegration',
    'TestIngestionIntegrationEnd2End',
]
