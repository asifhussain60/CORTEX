"""
Tests for Health Metrics

Tests for AC-METRICS-001 through AC-METRICS-005:
- Validation success rate tracking
- Semantic accuracy tracking
- Cross-reference success rate
- Phase alignment rate
- Anomaly detection
"""

import pytest
import time
from datetime import datetime, timedelta
from src.core.health_metrics import (
    HealthMetrics,
    MetricEntry,
    MetricSummary,
    MetricType
)


class TestValidationSuccessRateTracking:
    """Tests for AC-METRICS-001: Validation success rate tracking"""

    def test_record_validation_success(self):
        """Test recording successful validation"""
        metrics = HealthMetrics.instance()
        metrics.reset_metrics()
        
        metrics.record_validation_success(component="InputValidator")
        
        assert metrics.get_metrics_count() == 1
        entry = metrics.get_all_metrics()[0]
        assert entry["metric_type"] == "validation_success"
        assert entry["value"] == 1.0

    def test_record_validation_failure(self):
        """Test recording failed validation"""
        metrics = HealthMetrics.instance()
        metrics.reset_metrics()
        
        metrics.record_validation_failure(component="InputValidator")
        
        assert metrics.get_metrics_count() == 1
        entry = metrics.get_all_metrics()[0]
        assert entry["metric_type"] == "validation_failure"
        assert entry["value"] == 0.0

    def test_validation_success_rate_all_pass(self):
        """Test success rate when all validations pass"""
        metrics = HealthMetrics.instance()
        metrics.reset_metrics()
        
        for _ in range(10):
            metrics.record_validation_success()
        
        success_rate = metrics.get_validation_success_rate()
        assert success_rate == 100.0

    def test_validation_success_rate_all_fail(self):
        """Test success rate when all validations fail"""
        metrics = HealthMetrics.instance()
        metrics.reset_metrics()
        
        for _ in range(10):
            metrics.record_validation_failure()
        
        success_rate = metrics.get_validation_success_rate()
        assert success_rate == 0.0

    def test_validation_success_rate_mixed(self):
        """Test success rate with mixed pass/fail"""
        metrics = HealthMetrics.instance()
        metrics.reset_metrics()
        
        for _ in range(7):
            metrics.record_validation_success()
        for _ in range(3):
            metrics.record_validation_failure()
        
        success_rate = metrics.get_validation_success_rate()
        assert success_rate == 70.0

    def test_validation_success_rate_empty(self):
        """Test success rate with no data"""
        metrics = HealthMetrics.instance()
        metrics.reset_metrics()
        
        success_rate = metrics.get_validation_success_rate()
        assert success_rate == 0.0

    def test_validation_success_rate_by_component(self):
        """Test success rate filtering by component"""
        metrics = HealthMetrics.instance()
        metrics.reset_metrics()
        
        metrics.record_validation_success(component="ValidatorA")
        metrics.record_validation_success(component="ValidatorA")
        metrics.record_validation_failure(component="ValidatorB")
        metrics.record_validation_failure(component="ValidatorB")
        
        rate_a = metrics.get_validation_success_rate(component="ValidatorA")
        rate_b = metrics.get_validation_success_rate(component="ValidatorB")
        
        assert rate_a == 100.0
        assert rate_b == 0.0


class TestSemanticAccuracyTracking:
    """Tests for AC-METRICS-002: Semantic accuracy tracking"""

    def test_record_semantic_accuracy(self):
        """Test recording semantic accuracy"""
        metrics = HealthMetrics.instance()
        metrics.reset_metrics()
        
        metrics.record_semantic_accuracy(accuracy_score=0.95)
        
        assert metrics.get_metrics_count() == 1
        entry = metrics.get_all_metrics()[0]
        assert entry["metric_type"] == "semantic_accuracy"
        assert entry["value"] == 0.95

    def test_semantic_accuracy_invalid_score_low(self):
        """Test that invalid accuracy scores are rejected (< 0.0)"""
        metrics = HealthMetrics.instance()
        
        with pytest.raises(ValueError):
            metrics.record_semantic_accuracy(accuracy_score=-0.1)

    def test_semantic_accuracy_invalid_score_high(self):
        """Test that invalid accuracy scores are rejected (> 1.0)"""
        metrics = HealthMetrics.instance()
        
        with pytest.raises(ValueError):
            metrics.record_semantic_accuracy(accuracy_score=1.1)

    def test_semantic_accuracy_valid_boundaries(self):
        """Test that valid boundaries are accepted"""
        metrics = HealthMetrics.instance()
        metrics.reset_metrics()
        
        metrics.record_semantic_accuracy(accuracy_score=0.0)
        metrics.record_semantic_accuracy(accuracy_score=1.0)
        metrics.record_semantic_accuracy(accuracy_score=0.5)
        
        assert metrics.get_metrics_count() == 3

    def test_get_semantic_accuracy_mean(self):
        """Test getting mean semantic accuracy"""
        metrics = HealthMetrics.instance()
        metrics.reset_metrics()
        
        metrics.record_semantic_accuracy(0.8)
        metrics.record_semantic_accuracy(0.9)
        metrics.record_semantic_accuracy(0.7)
        
        accuracy = metrics.get_semantic_accuracy()
        assert accuracy == pytest.approx(0.8)  # Mean of 0.8, 0.9, 0.7

    def test_get_semantic_accuracy_no_data(self):
        """Test getting accuracy with no data"""
        metrics = HealthMetrics.instance()
        metrics.reset_metrics()
        
        accuracy = metrics.get_semantic_accuracy()
        assert accuracy is None

    def test_get_semantic_accuracy_by_component(self):
        """Test getting accuracy by component"""
        metrics = HealthMetrics.instance()
        metrics.reset_metrics()
        
        metrics.record_semantic_accuracy(0.9, component="ValidatorA")
        metrics.record_semantic_accuracy(0.9, component="ValidatorA")
        metrics.record_semantic_accuracy(0.5, component="ValidatorB")
        
        accuracy_a = metrics.get_semantic_accuracy(component="ValidatorA")
        accuracy_b = metrics.get_semantic_accuracy(component="ValidatorB")
        
        assert accuracy_a == pytest.approx(0.9)
        assert accuracy_b == pytest.approx(0.5)


class TestCrossReferenceTracking:
    """Tests for AC-METRICS-003: Cross-reference success rate"""

    def test_record_cross_reference_success(self):
        """Test recording successful cross-reference check"""
        metrics = HealthMetrics.instance()
        metrics.reset_metrics()
        
        metrics.record_cross_reference_check(success=True)
        
        assert metrics.get_metrics_count() == 1

    def test_record_cross_reference_failure(self):
        """Test recording failed cross-reference check"""
        metrics = HealthMetrics.instance()
        metrics.reset_metrics()
        
        metrics.record_cross_reference_check(success=False)
        
        assert metrics.get_metrics_count() == 1

    def test_cross_reference_success_rate(self):
        """Test cross-reference success rate calculation"""
        metrics = HealthMetrics.instance()
        metrics.reset_metrics()
        
        for _ in range(8):
            metrics.record_cross_reference_check(success=True)
        for _ in range(2):
            metrics.record_cross_reference_check(success=False)
        
        success_rate = metrics.get_cross_reference_success_rate()
        assert success_rate == 80.0


class TestPhaseAlignmentTracking:
    """Tests for AC-METRICS-004: Phase alignment enforcement"""

    def test_record_phase_alignment_aligned(self):
        """Test recording aligned phase check"""
        metrics = HealthMetrics.instance()
        metrics.reset_metrics()
        
        metrics.record_phase_alignment_check(aligned=True, phase="PHASE-02")
        
        assert metrics.get_metrics_count() == 1

    def test_record_phase_alignment_not_aligned(self):
        """Test recording misaligned phase check"""
        metrics = HealthMetrics.instance()
        metrics.reset_metrics()
        
        metrics.record_phase_alignment_check(aligned=False, phase="PHASE-03")
        
        assert metrics.get_metrics_count() == 1

    def test_phase_alignment_rate(self):
        """Test phase alignment rate calculation"""
        metrics = HealthMetrics.instance()
        metrics.reset_metrics()
        
        for _ in range(6):
            metrics.record_phase_alignment_check(aligned=True, phase="PHASE-02")
        for _ in range(4):
            metrics.record_phase_alignment_check(aligned=False, phase="PHASE-02")
        
        alignment_rate = metrics.get_phase_alignment_rate()
        assert alignment_rate == 60.0


class TestAnomalyDetection:
    """Tests for AC-METRICS-005: Anomaly detection"""

    def test_detect_anomalies_with_outliers(self):
        """Test anomaly detection with outliers"""
        metrics = HealthMetrics.instance()
        metrics.reset_metrics()
        
        # Record normal values
        for _ in range(5):
            metrics.record_semantic_accuracy(0.9, component="Validator")
        
        # Record outlier
        metrics.record_semantic_accuracy(0.1, component="Validator")
        
        anomalies = metrics.detect_anomalies(
            metric_type=MetricType.SEMANTIC_ACCURACY,
            threshold_std_dev=1.0
        )
        
        # Should detect the outlier
        assert len(anomalies) > 0

    def test_detect_anomalies_no_outliers(self):
        """Test anomaly detection with no outliers"""
        metrics = HealthMetrics.instance()
        metrics.reset_metrics()
        
        # Record consistent values
        for _ in range(5):
            metrics.record_semantic_accuracy(0.9, component="Validator")
        
        anomalies = metrics.detect_anomalies(
            metric_type=MetricType.SEMANTIC_ACCURACY
        )
        
        # Should not detect anomalies
        assert len(anomalies) == 0

    def test_detect_anomalies_insufficient_data(self):
        """Test anomaly detection with insufficient data"""
        metrics = HealthMetrics.instance()
        metrics.reset_metrics()
        
        # Record only 2 points (need at least 3)
        metrics.record_semantic_accuracy(0.9)
        metrics.record_semantic_accuracy(0.8)
        
        anomalies = metrics.detect_anomalies()
        
        # Should not detect (insufficient data)
        assert len(anomalies) == 0


class TestMetricEntry:
    """Tests for MetricEntry dataclass"""

    def test_metric_entry_creation(self):
        """Test creating a metric entry"""
        now = datetime.now()
        entry = MetricEntry(
            timestamp=now,
            metric_type=MetricType.VALIDATION_SUCCESS,
            component="Validator",
            value=1.0
        )
        
        assert entry.timestamp == now
        assert entry.metric_type == MetricType.VALIDATION_SUCCESS
        assert entry.component == "Validator"
        assert entry.value == 1.0

    def test_metric_entry_with_metadata(self):
        """Test metric entry with metadata"""
        entry = MetricEntry(
            timestamp=datetime.now(),
            metric_type=MetricType.VALIDATION_SUCCESS,
            component="Validator",
            value=1.0,
            metadata={"ac_id": "AC-AR-006-01"}
        )
        
        assert entry.metadata["ac_id"] == "AC-AR-006-01"

    def test_metric_entry_to_dict(self):
        """Test converting metric entry to dictionary"""
        entry = MetricEntry(
            timestamp=datetime.now(),
            metric_type=MetricType.VALIDATION_SUCCESS,
            component="Validator",
            value=1.0
        )
        
        entry_dict = entry.to_dict()
        assert entry_dict["component"] == "Validator"
        assert entry_dict["value"] == 1.0
        assert "timestamp" in entry_dict


class TestMetricSummary:
    """Tests for MetricSummary dataclass"""

    def test_metric_summary_creation(self):
        """Test creating a metric summary"""
        now = datetime.now()
        summary = MetricSummary(
            metric_type=MetricType.VALIDATION_SUCCESS,
            component="Validator",
            count=10,
            mean=0.95,
            min=0.8,
            max=1.0,
            median=0.95,
            std_dev=0.05,
            period_start=now,
            period_end=now
        )
        
        assert summary.component == "Validator"
        assert summary.count == 10
        assert summary.mean == 0.95

    def test_metric_summary_to_dict(self):
        """Test converting summary to dictionary"""
        summary = MetricSummary(
            metric_type=MetricType.VALIDATION_SUCCESS,
            component="Validator",
            count=10,
            mean=0.95,
            min=0.8,
            max=1.0,
            median=0.95,
            std_dev=0.05,
            period_start=datetime.now(),
            period_end=datetime.now()
        )
        
        summary_dict = summary.to_dict()
        assert summary_dict["count"] == 10
        assert summary_dict["mean"] == 0.95


class TestHealthMetricsSingleton:
    """Tests for HealthMetrics singleton pattern"""

    def test_singleton_instance(self):
        """Test that HealthMetrics is a singleton"""
        metrics1 = HealthMetrics.instance()
        metrics2 = HealthMetrics.instance()
        
        assert metrics1 is metrics2

    def test_singleton_state_persistence(self):
        """Test that singleton maintains state"""
        metrics = HealthMetrics.instance()
        metrics.reset_metrics()
        
        metrics.record_validation_success()
        count1 = metrics.get_metrics_count()
        
        metrics2 = HealthMetrics.instance()
        count2 = metrics2.get_metrics_count()
        
        assert count1 == count2 == 1


class TestMetricsRetention:
    """Tests for metrics retention and cleanup"""

    def test_clear_old_metrics(self):
        """Test clearing old metrics"""
        metrics = HealthMetrics.instance()
        # Don't reset - let's test with current state first
        initial_before = metrics.get_metrics_count()
        
        # Record some new metrics
        metrics.record_validation_success()
        metrics.record_validation_success()
        
        count_after_add = metrics.get_metrics_count()
        assert count_after_add == initial_before + 2
        
        # Clear with 0 hour retention (removes all)
        removed = metrics.clear_old_metrics(hours=0)
        
        assert removed == count_after_add
        assert metrics.get_metrics_count() == 0

    def test_reset_metrics(self):
        """Test resetting all metrics"""
        metrics = HealthMetrics.instance()
        
        metrics.record_validation_success()
        metrics.record_validation_success()
        assert metrics.get_metrics_count() >= 2
        
        metrics.reset_metrics()
        assert metrics.get_metrics_count() == 0


class TestGetMetricSummary:
    """Tests for getting metric summaries"""

    def test_get_metric_summary(self):
        """Test getting metric summary statistics"""
        metrics = HealthMetrics.instance()
        metrics.reset_metrics()
        
        metrics.record_semantic_accuracy(0.8)
        metrics.record_semantic_accuracy(0.9)
        metrics.record_semantic_accuracy(0.85)
        
        summary = metrics.get_metric_summary(
            MetricType.SEMANTIC_ACCURACY
        )
        
        assert summary is not None
        assert summary.count == 3
        assert summary.mean == pytest.approx(0.85)
        assert summary.min == 0.8
        assert summary.max == 0.9

    def test_get_metric_summary_no_data(self):
        """Test getting summary with no data"""
        metrics = HealthMetrics.instance()
        metrics.reset_metrics()
        
        summary = metrics.get_metric_summary(
            MetricType.SEMANTIC_ACCURACY
        )
        
        assert summary is None


class TestComprehensiveMetricsTracking:
    """Integration tests for health metrics"""

    def test_complete_metrics_workflow(self):
        """Test complete metrics workflow"""
        metrics = HealthMetrics.instance()
        metrics.reset_metrics()
        
        # Record various metrics
        for _ in range(8):
            metrics.record_validation_success(component="InputValidator")
        for _ in range(2):
            metrics.record_validation_failure(component="InputValidator")
        
        for _ in range(5):
            metrics.record_semantic_accuracy(0.92)
        
        metrics.record_cross_reference_check(True)
        metrics.record_phase_alignment_check(True, "PHASE-02")
        
        # Verify counts
        assert metrics.get_metrics_count() >= 15
        
        # Verify rates (only count InputValidator validations)
        validation_rate = metrics.get_validation_success_rate(component="InputValidator")
        assert validation_rate == 80.0
        
        semantic_acc = metrics.get_semantic_accuracy()
        assert semantic_acc == pytest.approx(0.92)

    def test_metrics_by_time_window(self):
        """Test metrics with different time windows"""
        metrics = HealthMetrics.instance()
        metrics.reset_metrics()
        
        # Record recent metrics
        metrics.record_validation_success()
        
        # Get rate with 1 hour window (should include recent)
        rate_1h = metrics.get_validation_success_rate(hours=1)
        assert rate_1h == 100.0
        
        # Get rate with 0 hour window (should be empty)
        rate_0h = metrics.get_validation_success_rate(hours=0)
        assert rate_0h == 0.0
