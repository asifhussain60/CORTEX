"""
Tests for CORE-030 Performance Baselines

Validates:
- SLA definitions are consistent and realistic
- Compliance checking works correctly
- Performance monitoring tracks violations
- Convenience functions work as expected

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import pytest
from cortex.core.governance.core_030_baselines import (
    PerformanceSLA,
    PerformanceMonitor,
    ComplianceViolation,
    CORE_030_BASELINES,
    ComponentName,
    MetricType,
    check_sla,
    record_measurement,
    get_monitor,
)
from datetime import datetime


class TestPerformanceSLA:
    """Test PerformanceSLA dataclass."""
    
    def test_valid_sla_creation(self):
        """SLA should create successfully with valid constraints."""
        sla = PerformanceSLA(
            component="test",
            metric="latency",
            target=100,
            p99=500,
            maximum=1000,
            unit="ms",
            description="Test SLA"
        )
        
        assert sla.component == "test"
        assert sla.target == 100
        assert sla.p99 == 500
        assert sla.maximum == 1000
    
    def test_invalid_sla_target_greater_than_p99(self):
        """SLA should reject target > p99."""
        with pytest.raises(ValueError):
            PerformanceSLA(
                component="test",
                metric="latency",
                target=600,  # Greater than p99
                p99=500,
                maximum=1000
            )
    
    def test_invalid_sla_p99_greater_than_maximum(self):
        """SLA should reject p99 > maximum."""
        with pytest.raises(ValueError):
            PerformanceSLA(
                component="test",
                metric="latency",
                target=100,
                p99=1100,  # Greater than maximum
                maximum=1000
            )
    
    def test_check_compliance_ok(self):
        """Value within target should return ok."""
        sla = PerformanceSLA(
            component="test",
            metric="latency",
            target=100,
            p99=500,
            maximum=1000
        )
        
        compliant, severity = sla.check_compliance(50)
        assert compliant is True
        assert severity == "ok"
    
    def test_check_compliance_warning(self):
        """Value between target and p99 should return warning."""
        sla = PerformanceSLA(
            component="test",
            metric="latency",
            target=100,
            p99=500,
            maximum=1000
        )
        
        compliant, severity = sla.check_compliance(300)
        assert compliant is True
        assert severity == "warning"
    
    def test_check_compliance_critical(self):
        """Value between p99 and maximum should return critical."""
        sla = PerformanceSLA(
            component="test",
            metric="latency",
            target=100,
            p99=500,
            maximum=1000
        )
        
        compliant, severity = sla.check_compliance(800)
        assert compliant is True
        assert severity == "critical"
    
    def test_check_compliance_violation(self):
        """Value exceeding maximum should return violation."""
        sla = PerformanceSLA(
            component="test",
            metric="latency",
            target=100,
            p99=500,
            maximum=1000
        )
        
        compliant, severity = sla.check_compliance(1200)
        assert compliant is False
        assert severity == "violation"


class TestBaselineDefinitions:
    """Test CORE_030_BASELINES definitions."""
    
    def test_all_baselines_valid(self):
        """All baselines should have valid SLA constraints."""
        for component, metrics in CORE_030_BASELINES.items():
            for metric, sla in metrics.items():
                # Should not raise ValueError due to invalid constraints
                assert sla.component == component
                assert sla.metric == metric
    
    def test_intent_router_slas_defined(self):
        """Intent router should have required SLAs."""
        intent_router = CORE_030_BASELINES[ComponentName.INTENT_ROUTER.value]
        
        assert MetricType.RESPONSE_TIME_MS.value in intent_router
        assert MetricType.THROUGHPUT_RPS.value in intent_router
        assert MetricType.ERROR_RATE_PCT.value in intent_router
    
    def test_audit_logging_slas_defined(self):
        """Audit logging should have required SLAs."""
        audit = CORE_030_BASELINES[ComponentName.AUDIT_LOGGING.value]
        
        assert MetricType.LATENCY_MS.value in audit
        assert MetricType.AVAILABILITY_PCT.value in audit
    
    def test_output_validation_slas_defined(self):
        """Output validation should have required SLAs."""
        output = CORE_030_BASELINES[ComponentName.OUTPUT_VALIDATION.value]
        
        assert MetricType.LATENCY_MS.value in output
        assert MetricType.ERROR_RATE_PCT.value in output
    
    def test_realistic_thresholds(self):
        """Thresholds should be realistic."""
        # Intent router response time should be in milliseconds
        intent_router = CORE_030_BASELINES[ComponentName.INTENT_ROUTER.value]
        response_sla = intent_router[MetricType.RESPONSE_TIME_MS.value]
        
        assert response_sla.target < 2000  # Less than 2 seconds
        assert response_sla.maximum < 5000  # Less than 5 seconds
    
    def test_audit_logging_high_availability(self):
        """Audit logging should target high availability."""
        audit = CORE_030_BASELINES[ComponentName.AUDIT_LOGGING.value]
        availability_sla = audit[MetricType.AVAILABILITY_PCT.value]
        
        assert availability_sla.maximum >= 99.0  # At least 99% achievable


class TestComplianceViolation:
    """Test ComplianceViolation tracking."""
    
    def test_violation_creation(self):
        """Violation should record all details."""
        violation = ComplianceViolation(
            component="test",
            metric="latency",
            measured_value=5000,
            sla_target=100,
            sla_maximum=1000
        )
        
        assert violation.component == "test"
        assert violation.measured_value == 5000
        assert violation.severity == "CRITICAL"
    
    def test_violation_auto_severity_critical(self):
        """Violation exceeding maximum gets CRITICAL severity."""
        violation = ComplianceViolation(
            component="test",
            metric="latency",
            measured_value=1500,  # Exceeds maximum of 1000
            sla_target=100,
            sla_maximum=1000
        )
        
        assert violation.severity == "CRITICAL"
    
    def test_violation_auto_severity_warning(self):
        """Violation in warning range gets WARNING severity."""
        violation = ComplianceViolation(
            component="test",
            metric="latency",
            measured_value=600,  # Above midpoint: (100 + (1000-100)/2) = 550
            sla_target=100,
            sla_maximum=1000
        )
        
        assert violation.severity == "WARNING"
    
    def test_violation_auto_severity_info(self):
        """Good performance gets INFO severity."""
        violation = ComplianceViolation(
            component="test",
            metric="latency",
            measured_value=50,  # Within target
            sla_target=100,
            sla_maximum=1000
        )
        
        assert violation.severity == "INFO"
    
    def test_violation_timestamp_set(self):
        """Violation should have timestamp set."""
        before = datetime.utcnow()
        violation = ComplianceViolation(
            component="test",
            metric="latency",
            measured_value=5000,
            sla_target=100,
            sla_maximum=1000
        )
        after = datetime.utcnow()
        
        assert before <= violation.timestamp <= after


class TestPerformanceMonitor:
    """Test PerformanceMonitor functionality."""
    
    def test_get_sla_valid(self):
        """Should retrieve valid SLA."""
        monitor = PerformanceMonitor()
        sla = monitor.get_sla(
            ComponentName.INTENT_ROUTER.value,
            MetricType.RESPONSE_TIME_MS.value
        )
        
        assert sla.component == ComponentName.INTENT_ROUTER.value
        assert sla.metric == MetricType.RESPONSE_TIME_MS.value
    
    def test_get_sla_unknown_component(self):
        """Should raise error for unknown component."""
        monitor = PerformanceMonitor()
        
        with pytest.raises(ValueError, match="Unknown component"):
            monitor.get_sla("unknown_component", "latency")
    
    def test_get_sla_unknown_metric(self):
        """Should raise error for unknown metric."""
        monitor = PerformanceMonitor()
        
        with pytest.raises(ValueError, match="Unknown metric"):
            monitor.get_sla(ComponentName.INTENT_ROUTER.value, "unknown_metric")
    
    def test_check_compliance_compliant(self):
        """Compliant value should return True."""
        monitor = PerformanceMonitor()
        
        result = monitor.check_compliance(
            ComponentName.INTENT_ROUTER.value,
            MetricType.RESPONSE_TIME_MS.value,
            100  # Well within target of 500ms
        )
        
        assert result is True
    
    def test_check_compliance_violation(self):
        """Violating value should return False."""
        monitor = PerformanceMonitor()
        
        result = monitor.check_compliance(
            ComponentName.INTENT_ROUTER.value,
            MetricType.RESPONSE_TIME_MS.value,
            5000  # Exceeds maximum of 2000ms
        )
        
        assert result is False
    
    def test_violation_recorded_on_exceedance(self):
        """Violation should be recorded when SLA exceeded."""
        monitor = PerformanceMonitor()
        
        monitor.check_compliance(
            ComponentName.INTENT_ROUTER.value,
            MetricType.RESPONSE_TIME_MS.value,
            5000  # Exceeds maximum
        )
        
        violations = monitor.get_violations()
        assert len(violations) == 1
        assert violations[0].measured_value == 5000
    
    def test_record_measurement(self):
        """Should record individual measurements."""
        monitor = PerformanceMonitor()
        
        monitor.record_measurement(
            ComponentName.INTENT_ROUTER.value,
            MetricType.RESPONSE_TIME_MS.value,
            250
        )
        
        stats = monitor.get_statistics(
            ComponentName.INTENT_ROUTER.value,
            MetricType.RESPONSE_TIME_MS.value
        )
        
        assert stats["count"] == 1
        assert stats["min"] == 250
        assert stats["max"] == 250
        assert stats["mean"] == 250
    
    def test_get_statistics_multiple_measurements(self):
        """Should calculate statistics from multiple measurements."""
        monitor = PerformanceMonitor()
        
        values = [100, 200, 300, 400, 500]
        for value in values:
            monitor.record_measurement(
                ComponentName.INTENT_ROUTER.value,
                MetricType.RESPONSE_TIME_MS.value,
                value
            )
        
        stats = monitor.get_statistics(
            ComponentName.INTENT_ROUTER.value,
            MetricType.RESPONSE_TIME_MS.value
        )
        
        assert stats["count"] == 5
        assert stats["min"] == 100
        assert stats["max"] == 500
        assert stats["mean"] == 300
        assert stats["p50"] == 300
    
    def test_get_violations_all(self):
        """Should return all violations."""
        monitor = PerformanceMonitor()
        
        monitor.check_compliance(ComponentName.INTENT_ROUTER.value,
                                MetricType.RESPONSE_TIME_MS.value, 5000)
        monitor.check_compliance(ComponentName.AUDIT_LOGGING.value,
                                MetricType.LATENCY_MS.value, 2000)
        
        violations = monitor.get_violations()
        assert len(violations) == 2
    
    def test_get_violations_filtered_by_component(self):
        """Should filter violations by component."""
        monitor = PerformanceMonitor()
        
        monitor.check_compliance(ComponentName.INTENT_ROUTER.value,
                                MetricType.RESPONSE_TIME_MS.value, 5000)
        monitor.check_compliance(ComponentName.AUDIT_LOGGING.value,
                                MetricType.LATENCY_MS.value, 2000)
        
        violations = monitor.get_violations(ComponentName.INTENT_ROUTER.value)
        assert len(violations) == 1
        assert violations[0].component == ComponentName.INTENT_ROUTER.value
    
    def test_clear_violations(self):
        """Should clear violation history."""
        monitor = PerformanceMonitor()
        
        monitor.check_compliance(ComponentName.INTENT_ROUTER.value,
                                MetricType.RESPONSE_TIME_MS.value, 5000)
        
        assert len(monitor.get_violations()) == 1
        
        monitor.clear_violations()
        assert len(monitor.get_violations()) == 0


class TestConvenienceFunctions:
    """Test convenience functions."""
    
    def test_check_sla_function(self):
        """check_sla convenience function should work."""
        # Reset global monitor
        get_monitor().clear_violations()
        
        result = check_sla(
            ComponentName.INTENT_ROUTER.value,
            MetricType.RESPONSE_TIME_MS.value,
            100
        )
        
        assert result is True
    
    def test_record_measurement_function(self):
        """record_measurement convenience function should work."""
        # Reset global monitor
        get_monitor().clear_violations()
        get_monitor().measurements.clear()
        
        record_measurement(
            ComponentName.INTENT_ROUTER.value,
            MetricType.RESPONSE_TIME_MS.value,
            250
        )
        
        monitor = get_monitor()
        stats = monitor.get_statistics(
            ComponentName.INTENT_ROUTER.value,
            MetricType.RESPONSE_TIME_MS.value
        )
        
        assert stats["count"] == 1
        assert stats["mean"] == 250


class TestRealWorldScenarios:
    """Test realistic performance monitoring scenarios."""
    
    def test_intent_router_performance_tracking(self):
        """Track intent router performance across multiple requests."""
        monitor = PerformanceMonitor()
        
        # Simulate 100 requests
        response_times = [
            150, 200, 180, 220, 190, 160, 210, 175, 185, 195,
            200, 220, 190, 170, 210, 195, 180, 200, 185, 210,
            # ... add more simulated times
        ] * 5  # 100 requests
        
        violations_count = 0
        for time in response_times[:100]:  # Use first 100
            monitor.record_measurement(
                ComponentName.INTENT_ROUTER.value,
                MetricType.RESPONSE_TIME_MS.value,
                time
            )
            if not monitor.check_compliance(
                ComponentName.INTENT_ROUTER.value,
                MetricType.RESPONSE_TIME_MS.value,
                time
            ):
                violations_count += 1
        
        stats = monitor.get_statistics(
            ComponentName.INTENT_ROUTER.value,
            MetricType.RESPONSE_TIME_MS.value
        )
        
        # All times should be well within SLA
        assert stats["count"] == 100
        assert stats["max"] < 500  # All within target
        assert violations_count == 0
    
    def test_degraded_performance_detection(self):
        """Detect when performance degrades."""
        monitor = PerformanceMonitor()
        
        # Start with good performance
        for i in range(50):
            monitor.record_measurement(
                ComponentName.INTENT_ROUTER.value,
                MetricType.RESPONSE_TIME_MS.value,
                100 + (i % 50)  # 100-150ms
            )
        
        # Performance degrades
        for i in range(50):
            time = 1500 + (i % 500)  # 1500-2000ms
            monitor.record_measurement(
                ComponentName.INTENT_ROUTER.value,
                MetricType.RESPONSE_TIME_MS.value,
                time
            )
            monitor.check_compliance(
                ComponentName.INTENT_ROUTER.value,
                MetricType.RESPONSE_TIME_MS.value,
                time
            )
        
        # Should have detected violations
        violations = monitor.get_violations()
        assert len(violations) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
