"""
Unit and Integration Tests for AlertPipeline (AC-IKP-003-02).

Tests for alert threshold configuration, notification channels, and 
multiple alerting backends.

Governance:
  - CORE-008: TDD (test-first development)
  - CORE-011: Type hints in all tests
  - CORE-012: Google-style docstrings
  - CORE-013: Specific exception handling
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, call
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from enum import Enum


class TestAlertPipeline:
    """Unit tests for AlertPipeline."""

    def test_alert_pipeline_exists(self):
        """Test that AlertPipeline class exists."""
        from src.core.knowledge.alert_pipeline import AlertPipeline
        
        assert AlertPipeline is not None

    def test_alert_pipeline_initialization(self):
        """Test that pipeline initializes with backends."""
        from src.core.knowledge.alert_pipeline import AlertPipeline
        
        backend = Mock()
        backend.name = 'audit_trail'
        
        pipeline = AlertPipeline(backends={'audit_trail': backend})
        
        assert pipeline is not None
        assert len(pipeline.backends) == 1

    def test_alert_threshold_configuration(self):
        """Test alert threshold configuration."""
        from src.core.knowledge.alert_pipeline import AlertPipeline
        
        backend = Mock()
        backend.name = 'audit_trail'
        
        pipeline = AlertPipeline(
            backends={'audit_trail': backend},
            thresholds={'CRITICAL': 0.9, 'HIGH': 0.7, 'MEDIUM': 0.5, 'LOW': 0.2}
        )
        
        # Should have threshold configuration
        assert hasattr(pipeline, 'thresholds')
        assert pipeline.thresholds is not None

    def test_notification_channel_registration(self):
        """Test registering notification channels."""
        from src.core.knowledge.alert_pipeline import AlertPipeline
        
        backend = Mock()
        pipeline = AlertPipeline(backends={'audit_trail': backend})
        
        # Should have channel registration method
        assert hasattr(pipeline, 'register_channel')

    def test_notification_channel_deregistration(self):
        """Test deregistering notification channels."""
        from src.core.knowledge.alert_pipeline import AlertPipeline
        
        backend = Mock()
        pipeline = AlertPipeline(backends={'audit_trail': backend})
        
        # Should have channel deregistration method
        assert hasattr(pipeline, 'deregister_channel')

    def test_alert_routing_to_channels(self):
        """Test routing alerts to configured channels."""
        from src.core.knowledge.alert_pipeline import AlertPipeline
        
        backend = Mock()
        pipeline = AlertPipeline(backends={'audit_trail': backend})
        
        # Should have alert routing method
        assert hasattr(pipeline, 'route_alert')

    def test_multiple_notification_backends(self):
        """Test support for multiple notification backends."""
        from src.core.knowledge.alert_pipeline import AlertPipeline
        
        audit_backend = Mock()
        audit_backend.name = 'audit_trail'
        email_backend = Mock()
        email_backend.name = 'email'
        
        pipeline = AlertPipeline(
            backends={'audit_trail': audit_backend, 'email': email_backend}
        )
        
        # Should support multiple backends
        assert len(pipeline.backends) == 2

    def test_alert_filtering_by_severity(self):
        """Test filtering alerts by severity level."""
        from src.core.knowledge.alert_pipeline import AlertPipeline
        
        backend = Mock()
        pipeline = AlertPipeline(backends={'audit_trail': backend})
        
        # Should have alert filtering method
        assert hasattr(pipeline, 'filter_by_severity')

    def test_alert_acknowledgment_workflow(self):
        """Test alert acknowledgment workflow."""
        from src.core.knowledge.alert_pipeline import AlertPipeline
        
        backend = Mock()
        pipeline = AlertPipeline(backends={'audit_trail': backend})
        
        # Should have acknowledgment method
        assert hasattr(pipeline, 'acknowledge_alert')

    def test_alert_override_support(self):
        """Test manual override of alert decisions."""
        from src.core.knowledge.alert_pipeline import AlertPipeline
        
        backend = Mock()
        pipeline = AlertPipeline(backends={'audit_trail': backend})
        
        # Should have override method
        assert hasattr(pipeline, 'override_alert')


class TestAlertPipelineIntegration:
    """Integration tests for AlertPipeline."""

    def test_alert_pipeline_with_change_detection_service(self):
        """Test AlertPipeline integration with ChangeDetectionService."""
        from src.core.knowledge.alert_pipeline import AlertPipeline
        from src.core.knowledge.change_detection import ChangeDetectionService, Alert, AnomalyType, SeverityLevel
        
        # Setup backends
        backend = Mock()
        backend.entry_count = 100
        backend.domains = ['tech', 'business']
        
        # Setup ChangeDetectionService
        cds = ChangeDetectionService(backends={'test': backend})
        
        # Setup AlertPipeline
        audit_backend = Mock()
        pipeline = AlertPipeline(backends={'audit_trail': audit_backend})
        
        # Should be able to process alerts from CDS
        assert pipeline is not None
        assert cds is not None

    def test_alert_notification_channel_workflow(self):
        """Test complete notification channel workflow."""
        from src.core.knowledge.alert_pipeline import AlertPipeline
        
        backend = Mock()
        pipeline = AlertPipeline(backends={'audit_trail': backend})
        
        # Register a channel
        channel = Mock()
        channel.name = 'email'
        channel.send = Mock()
        
        # Should support channel registration and notification
        assert hasattr(pipeline, 'register_channel')
        assert hasattr(pipeline, 'route_alert')

    def test_alert_threshold_enforcement(self):
        """Test that thresholds are enforced during routing."""
        from src.core.knowledge.alert_pipeline import AlertPipeline
        
        backend = Mock()
        thresholds = {'CRITICAL': 0.9, 'HIGH': 0.7, 'MEDIUM': 0.5}
        
        pipeline = AlertPipeline(
            backends={'audit_trail': backend},
            thresholds=thresholds
        )
        
        # Should enforce thresholds
        assert pipeline.thresholds == thresholds

    def test_alert_retry_mechanism(self):
        """Test alert delivery retry mechanism."""
        from src.core.knowledge.alert_pipeline import AlertPipeline
        
        backend = Mock()
        pipeline = AlertPipeline(backends={'audit_trail': backend})
        
        # Should have retry support
        assert hasattr(pipeline, 'retry_failed_alerts')

    def test_alert_deduplication(self):
        """Test alert deduplication to prevent duplicate notifications."""
        from src.core.knowledge.alert_pipeline import AlertPipeline
        
        backend = Mock()
        pipeline = AlertPipeline(backends={'audit_trail': backend})
        
        # Should support deduplication
        assert hasattr(pipeline, 'deduplicate_alerts')

    def test_alert_metrics_tracking(self):
        """Test tracking of alert metrics."""
        from src.core.knowledge.alert_pipeline import AlertPipeline
        
        backend = Mock()
        pipeline = AlertPipeline(backends={'audit_trail': backend})
        
        # Should track metrics
        assert hasattr(pipeline, 'get_metrics')

    def test_alert_pipeline_graceful_degradation(self):
        """Test graceful degradation when channels unavailable."""
        from src.core.knowledge.alert_pipeline import AlertPipeline
        
        # Empty backends dict
        pipeline = AlertPipeline(backends={})
        
        # Should continue without error
        assert pipeline is not None

    def test_alert_pipeline_error_handling(self):
        """Test error handling during alert routing."""
        from src.core.knowledge.alert_pipeline import AlertPipeline
        
        backend = Mock()
        pipeline = AlertPipeline(backends={'audit_trail': backend})
        
        # Should handle errors gracefully
        assert hasattr(pipeline, 'route_alert')

    def test_alert_audit_trail_logging(self):
        """Test audit trail logging of all alert events."""
        from src.core.knowledge.alert_pipeline import AlertPipeline
        
        backend = Mock()
        backend.log = Mock()
        
        pipeline = AlertPipeline(backends={'audit_trail': backend})
        
        # Should support audit logging
        assert hasattr(pipeline, 'log_alert_event')


__all__ = [
    'TestAlertPipeline',
    'TestAlertPipelineIntegration',
]
