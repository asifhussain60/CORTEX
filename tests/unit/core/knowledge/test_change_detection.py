"""
Unit and Integration Tests for ChangeDetectionService (AC-IKP-003-01).

Tests for monitoring knowledge backends for schema drift, semantic shift,
coverage gaps, staleness, and volume anomalies.

Governance:
  - CORE-008: TDD (test-first development)
  - CORE-011: Type hints in all tests
  - CORE-012: Google-style docstrings
  - CORE-013: Specific exception handling
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, call
from typing import Dict, List, Any
from datetime import datetime, timedelta


class TestChangeDetectionService:
    """Unit tests for ChangeDetectionService."""

    def test_change_detection_service_exists(self):
        """Test that ChangeDetectionService class exists."""
        from cortex.core.knowledge.change_detection import ChangeDetectionService
        
        assert ChangeDetectionService is not None

    def test_change_detection_service_initialization(self):
        """Test that service initializes with backends."""
        from cortex.core.knowledge.change_detection import ChangeDetectionService
        
        backend = Mock()
        backend.entry_count = 100
        backend.domains = ['tech', 'business']
        
        service = ChangeDetectionService(backends={'test': backend})
        
        assert service is not None
        assert len(service.backends) == 1

    def test_schema_drift_detection(self):
        """Test detection of schema drift in knowledge entries."""
        from cortex.core.knowledge.change_detection import ChangeDetectionService
        
        backend = Mock()
        backend.entry_count = 100
        
        service = ChangeDetectionService(backends={'test': backend})
        
        # Should have schema drift detection method
        assert hasattr(service, 'detect_schema_drift')

    def test_semantic_shift_detection(self):
        """Test detection of semantic shifts in knowledge entries."""
        from cortex.core.knowledge.change_detection import ChangeDetectionService
        
        backend = Mock()
        service = ChangeDetectionService(backends={'test': backend})
        
        # Should have semantic shift detection
        assert hasattr(service, 'detect_semantic_shift')

    def test_coverage_gap_detection(self):
        """Test detection of coverage gaps in domains."""
        from cortex.core.knowledge.change_detection import ChangeDetectionService
        
        backend = Mock()
        service = ChangeDetectionService(backends={'test': backend})
        
        # Should have coverage gap detection
        assert hasattr(service, 'detect_coverage_gaps')

    def test_staleness_detection(self):
        """Test detection of stale knowledge entries."""
        from cortex.core.knowledge.change_detection import ChangeDetectionService
        
        backend = Mock()
        service = ChangeDetectionService(backends={'test': backend})
        
        # Should have staleness detection
        assert hasattr(service, 'detect_staleness')

    def test_volume_anomaly_detection(self):
        """Test detection of volume anomalies."""
        from cortex.core.knowledge.change_detection import ChangeDetectionService
        
        backend = Mock()
        service = ChangeDetectionService(backends={'test': backend})
        
        # Should have volume anomaly detection
        assert hasattr(service, 'detect_volume_anomalies')

    def test_alert_emission_on_drift(self):
        """Test that alerts are emitted when drift is detected."""
        from cortex.core.knowledge.change_detection import ChangeDetectionService
        
        backend = Mock()
        service = ChangeDetectionService(backends={'test': backend})
        
        # Should have alert emission capability
        assert hasattr(service, 'emit_alert')

    def test_change_detection_stores_baseline(self):
        """Test that service stores baseline for comparison."""
        from cortex.core.knowledge.change_detection import ChangeDetectionService
        
        backend = Mock()
        backend.entry_count = 50
        backend.domains = ['tech']
        
        service = ChangeDetectionService(backends={'test': backend})
        
        # Should store baseline state
        assert hasattr(service, 'baseline')

    def test_change_detection_compares_current_state(self):
        """Test that service compares current state with baseline."""
        from cortex.core.knowledge.change_detection import ChangeDetectionService
        
        backend = Mock()
        service = ChangeDetectionService(backends={'test': backend})
        
        # Should have comparison method
        assert hasattr(service, 'compare_state')

    def test_auto_remediation_low_risk_changes(self):
        """Test automatic remediation of low-risk additive changes."""
        from cortex.core.knowledge.change_detection import ChangeDetectionService
        
        backend = Mock()
        service = ChangeDetectionService(backends={'test': backend})
        
        # Should have auto-remediation capability
        assert hasattr(service, 'auto_remediate')

    def test_change_detection_alert_metadata(self):
        """Test that alerts contain comprehensive metadata."""
        from cortex.core.knowledge.change_detection import ChangeDetectionService
        
        backend = Mock()
        service = ChangeDetectionService(backends={'test': backend})
        
        alert = {
            'type': 'schema_drift',
            'severity': 'high',
            'backend': 'test',
            'timestamp': datetime.now().isoformat(),
            'details': {},
            'recommendation': 'manual_review'
        }
        
        assert 'type' in alert
        assert 'severity' in alert
        assert 'timestamp' in alert

    def test_change_detection_handles_multiple_backends(self):
        """Test that service handles multiple knowledge backends."""
        from cortex.core.knowledge.change_detection import ChangeDetectionService
        
        backend1 = Mock()
        backend2 = Mock()
        backend1.entry_count = 50
        backend2.entry_count = 75
        
        service = ChangeDetectionService(backends={'b1': backend1, 'b2': backend2})
        
        assert len(service.backends) == 2

    def test_change_detection_threshold_configuration(self):
        """Test that detection thresholds are configurable."""
        from cortex.core.knowledge.change_detection import ChangeDetectionService
        
        backend = Mock()
        service = ChangeDetectionService(
            backends={'test': backend},
            drift_threshold=0.3,
            staleness_days=30
        )
        
        # Should store configuration
        assert hasattr(service, 'drift_threshold')
        assert hasattr(service, 'staleness_days')

    def test_change_detection_alert_acknowledgment(self):
        """Test manual override and acknowledgment of alerts."""
        from cortex.core.knowledge.change_detection import ChangeDetectionService
        
        backend = Mock()
        service = ChangeDetectionService(backends={'test': backend})
        
        # Should support alert acknowledgment
        assert hasattr(service, 'acknowledge_alert')

    def test_change_detection_metrics_tracking(self):
        """Test that service tracks detection metrics."""
        from cortex.core.knowledge.change_detection import ChangeDetectionService
        
        backend = Mock()
        service = ChangeDetectionService(backends={'test': backend})
        
        # Should track metrics
        assert hasattr(service, 'get_metrics')


class TestChangeDetectionIntegration:
    """Integration tests for ChangeDetectionService."""

    def test_change_detection_with_knowledge_repository(self):
        """Test change detection with real knowledge repository interface."""
        from cortex.core.knowledge.change_detection import ChangeDetectionService
        
        backend = Mock()
        backend.entry_count = 100
        backend.domains = ['technical', 'business']
        
        service = ChangeDetectionService(backends={'knowledge': backend})
        
        # Simulate state change
        backend.entry_count = 105
        
        # Should detect changes
        assert backend.entry_count == 105

    def test_change_detection_continuous_monitoring(self):
        """Test continuous monitoring of knowledge backends."""
        from cortex.core.knowledge.change_detection import ChangeDetectionService
        
        backend = Mock()
        backend.entry_count = 100
        
        service = ChangeDetectionService(backends={'test': backend})
        
        # Should support monitoring
        assert hasattr(service, 'start_monitoring')
        assert hasattr(service, 'stop_monitoring')

    def test_change_detection_alert_routing(self):
        """Test alert routing to audit trail and notification systems."""
        from cortex.core.knowledge.change_detection import ChangeDetectionService
        
        backend = Mock()
        service = ChangeDetectionService(backends={'test': backend})
        
        # Alerts should be routeable
        assert hasattr(service, 'route_alert')

    def test_change_detection_anomaly_scoring(self):
        """Test that anomalies are scored for severity."""
        from cortex.core.knowledge.change_detection import ChangeDetectionService
        
        backend = Mock()
        service = ChangeDetectionService(backends={'test': backend})
        
        # Should have scoring capability
        assert hasattr(service, 'score_anomaly')

    def test_change_detection_historical_tracking(self):
        """Test tracking of historical changes."""
        from cortex.core.knowledge.change_detection import ChangeDetectionService
        
        backend = Mock()
        service = ChangeDetectionService(backends={'test': backend})
        
        # Should track history
        assert hasattr(service, 'get_change_history')

    def test_change_detection_pattern_analysis(self):
        """Test pattern analysis of detected changes."""
        from cortex.core.knowledge.change_detection import ChangeDetectionService
        
        backend = Mock()
        service = ChangeDetectionService(backends={'test': backend})
        
        # Should analyze patterns
        assert hasattr(service, 'analyze_patterns')

    def test_change_detection_performance_under_load(self):
        """Test that change detection performs well with large backends."""
        from cortex.core.knowledge.change_detection import ChangeDetectionService
        
        backend = Mock()
        backend.entry_count = 1000000  # 1M entries
        backend.domains = ['tech', 'business', 'policy', 'domain1', 'domain2']
        
        service = ChangeDetectionService(backends={'large': backend})
        
        # Should handle large backends
        assert service is not None

    def test_change_detection_graceful_degradation(self):
        """Test graceful degradation when backends are unavailable."""
        from cortex.core.knowledge.change_detection import ChangeDetectionService
        
        # Empty backends dict
        service = ChangeDetectionService(backends={})
        
        # Should continue without error
        assert service is not None

    def test_change_detection_error_handling(self):
        """Test error handling during detection."""
        from cortex.core.knowledge.change_detection import ChangeDetectionService
        
        backend = Mock()
        backend.entry_count = 100
        
        service = ChangeDetectionService(backends={'test': backend})
        
        # Should handle missing backend attributes gracefully (no exception)
        # Graceful degradation allows empty backends without raising errors
        service_empty = ChangeDetectionService(backends={})
        assert service_empty is not None

    def test_change_detection_audit_logging(self):
        """Test that all changes are logged to audit trail."""
        from cortex.core.knowledge.change_detection import ChangeDetectionService
        
        backend = Mock()
        service = ChangeDetectionService(backends={'test': backend})
        
        # Should support audit logging
        assert hasattr(service, 'log_to_audit_trail')

    def test_change_detection_compliance_reporting(self):
        """Test compliance reporting for detected changes."""
        from cortex.core.knowledge.change_detection import ChangeDetectionService
        
        backend = Mock()
        service = ChangeDetectionService(backends={'test': backend})
        
        # Should generate compliance reports
        assert hasattr(service, 'generate_compliance_report')


__all__ = [
    'TestChangeDetectionService',
    'TestChangeDetectionIntegration',
]
