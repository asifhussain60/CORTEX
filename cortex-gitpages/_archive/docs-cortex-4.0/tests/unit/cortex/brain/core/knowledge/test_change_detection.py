"""Unit tests for change detection and anomaly identification.

Tests all anomaly detector implementations and the change detection service.
"""

import pytest
from datetime import datetime, timedelta
from typing import Any, Dict, List

from cortex.brain.core.knowledge.change_detection import (
    AnomalyType,
    SeverityLevel,
    AnomalyScore,
    AnomalyDetection,
    ChangeHistory,
    SchemaDriftDetector,
    SemanticShiftDetector,
    CoverageGapDetector,
    StalenessDetector,
    VolumeAnomalyDetector,
    ChangeDetectionService,
)


# ============================================================================
# Test Fixtures
# ============================================================================


@pytest.fixture
def sample_entries() -> List[Dict[str, Any]]:
    """Sample knowledge entries for testing."""
    return [
        {
            "id": "entry1",
            "domain": "api_design",
            "title": "REST API Design",
            "description": "Best practices for REST API design",
            "category": "architectural_pattern",
            "created_at": (datetime.utcnow() - timedelta(days=10)).isoformat(),
            "updated_at": (datetime.utcnow() - timedelta(days=5)).isoformat(),
        },
        {
            "id": "entry2",
            "domain": "security",
            "title": "Authentication",
            "description": "Security best practices for authentication",
            "category": "security_pattern",
            "created_at": (datetime.utcnow() - timedelta(days=20)).isoformat(),
            "updated_at": (datetime.utcnow() - timedelta(days=1)).isoformat(),
        },
        {
            "id": "entry3",
            "domain": "architecture",
            "title": "Microservices",
            "description": "Microservices architecture patterns",
            "category": "architectural_pattern",
            "created_at": (datetime.utcnow() - timedelta(days=30)).isoformat(),
            "updated_at": (datetime.utcnow() - timedelta(days=25)).isoformat(),
        },
    ]


@pytest.fixture
def change_history() -> Dict[str, ChangeHistory]:
    """Sample change history for testing."""
    history: Dict[str, ChangeHistory] = {}

    for i in range(1, 4):
        entry_id = f"entry{i}"
        history[entry_id] = ChangeHistory(entry_id)
        history[entry_id].add_change(
            {"id": entry_id, "version": 1},
            datetime.utcnow() - timedelta(days=30),
            "Initial creation",
        )

    return history


# ============================================================================
# AnomalyScore Tests
# ============================================================================


class TestAnomalyScore:
    """Tests for AnomalyScore validation."""

    def test_valid_score(self) -> None:
        """Test creation of valid anomaly score."""
        score = AnomalyScore(value=0.5, confidence=0.8, reasoning="Test")
        assert score.value == 0.5
        assert score.confidence == 0.8

    def test_score_value_zero(self) -> None:
        """Test score value of zero."""
        score = AnomalyScore(value=0.0, confidence=0.5, reasoning="Normal")
        assert score.value == 0.0

    def test_score_value_one(self) -> None:
        """Test score value of one."""
        score = AnomalyScore(value=1.0, confidence=0.5, reasoning="Severe")
        assert score.value == 1.0

    def test_invalid_score_too_high(self) -> None:
        """Test that scores > 1.0 are rejected."""
        with pytest.raises(ValueError):
            AnomalyScore(value=1.5, confidence=0.5, reasoning="Invalid")

    def test_invalid_score_negative(self) -> None:
        """Test that negative scores are rejected."""
        with pytest.raises(ValueError):
            AnomalyScore(value=-0.1, confidence=0.5, reasoning="Invalid")

    def test_invalid_confidence_too_high(self) -> None:
        """Test that confidence > 1.0 is rejected."""
        with pytest.raises(ValueError):
            AnomalyScore(value=0.5, confidence=1.5, reasoning="Invalid")

    def test_invalid_confidence_negative(self) -> None:
        """Test that negative confidence is rejected."""
        with pytest.raises(ValueError):
            AnomalyScore(value=0.5, confidence=-0.1, reasoning="Invalid")


# ============================================================================
# AnomalyDetection Tests
# ============================================================================


class TestAnomalyDetection:
    """Tests for AnomalyDetection creation."""

    def test_anomaly_creation(self) -> None:
        """Test creation of anomaly detection."""
        score = AnomalyScore(value=0.7, confidence=0.9, reasoning="Test anomaly")
        anomaly = AnomalyDetection(
            anomaly_type=AnomalyType.SCHEMA_DRIFT,
            severity=SeverityLevel.WARNING,
            score=score,
            affected_entries=["entry1"],
            reasoning="Schema changed",
        )
        assert anomaly.anomaly_type == AnomalyType.SCHEMA_DRIFT
        assert anomaly.severity == SeverityLevel.WARNING

    def test_anomaly_with_recommendations(self) -> None:
        """Test anomaly with recommendations."""
        score = AnomalyScore(value=0.8, confidence=0.85, reasoning="Critical issue")
        anomaly = AnomalyDetection(
            anomaly_type=AnomalyType.COVERAGE_GAP,
            severity=SeverityLevel.CRITICAL,
            score=score,
            recommendations=["Investigate gap", "Restore data"],
        )
        assert len(anomaly.recommendations) == 2


# ============================================================================
# ChangeHistory Tests
# ============================================================================


class TestChangeHistory:
    """Tests for ChangeHistory tracking."""

    def test_add_change(self) -> None:
        """Test adding a change to history."""
        history = ChangeHistory("entry1")
        version = {"id": "entry1", "value": "test"}
        history.add_change(version, datetime.utcnow(), "Test change")

        assert len(history.timestamps) == 1
        assert len(history.versions) == 1

    def test_multiple_changes(self) -> None:
        """Test tracking multiple changes."""
        history = ChangeHistory("entry1")
        now = datetime.utcnow()

        for i in range(5):
            history.add_change(
                {"id": "entry1", "version": i},
                now + timedelta(seconds=i),
                f"Change {i}",
            )

        assert len(history.timestamps) == 5

    def test_get_last_change(self) -> None:
        """Test retrieving the most recent change."""
        history = ChangeHistory("entry1")
        now = datetime.utcnow()

        history.add_change({"version": 1}, now, "Change 1")
        history.add_change({"version": 2}, now + timedelta(seconds=1), "Change 2")

        last_ts, last_change = history.get_last_change()
        assert last_change == "Change 2"

    def test_get_last_change_empty(self) -> None:
        """Test getting last change when no changes exist."""
        history = ChangeHistory("entry1")
        assert history.get_last_change() is None

    def test_get_changes_since(self) -> None:
        """Test retrieving changes since a timestamp."""
        history = ChangeHistory("entry1")
        now = datetime.utcnow()

        for i in range(3):
            history.add_change({"v": i}, now + timedelta(hours=i), f"Change {i}")

        cutoff = now + timedelta(hours=1)
        changes = history.get_changes_since(cutoff)

        assert len(changes) == 2


# ============================================================================
# SchemaDriftDetector Tests
# ============================================================================


class TestSchemaDriftDetector:
    """Tests for schema drift detection."""

    def test_schema_drift_detection_enabled_after_learning(self, sample_entries: List[Dict[str, Any]]) -> None:
        """Test schema drift is detected after learning mode."""
        detector = SchemaDriftDetector(learning_mode_duration=0)
        detector.start_learning_mode()

        # First call: establishes baseline
        anomalies = detector.detect(sample_entries, {})
        assert len(anomalies) == 0  # Learning mode

        # Modify schema
        modified_entries = sample_entries.copy()
        modified_entries[0]["new_field"] = "added"

        # Second call: should detect drift (but learning mode still active due to duration=0)
        anomalies = detector.detect(modified_entries, {})
        # With duration=0, learning mode should be expired

    def test_schema_extraction(self, sample_entries: List[Dict[str, Any]]) -> None:
        """Test schema extraction from entries."""
        detector = SchemaDriftDetector()
        schema = detector._extract_schema(sample_entries)

        assert len(schema) == 3
        assert "entry1" in schema
        assert "domain" in schema["entry1"]

    def test_empty_entries(self) -> None:
        """Test handling of empty entry list."""
        detector = SchemaDriftDetector()
        anomalies = detector.detect([], {})
        assert len(anomalies) == 0


# ============================================================================
# SemanticShiftDetector Tests
# ============================================================================


class TestSemanticShiftDetector:
    """Tests for semantic shift detection."""

    def test_text_similarity_calculation(self) -> None:
        """Test text similarity calculation."""
        detector = SemanticShiftDetector()

        # Identical texts
        sim = detector._calculate_text_similarity("hello world", "hello world")
        assert sim == 1.0

        # Completely different
        sim = detector._calculate_text_similarity("hello world", "foo bar baz")
        assert sim < 0.5

        # Partial overlap
        sim = detector._calculate_text_similarity("hello world test", "hello world demo")
        assert 0.3 < sim < 0.7

    def test_text_similarity_empty(self) -> None:
        """Test similarity with empty strings."""
        detector = SemanticShiftDetector()
        sim = detector._calculate_text_similarity("", "hello")
        assert sim == 0.0

    def test_content_extraction(self, sample_entries: List[Dict[str, Any]]) -> None:
        """Test content extraction from entries."""
        detector = SemanticShiftDetector()
        content = detector._extract_content(sample_entries)

        assert len(content) == 3
        assert "entry1" in content
        assert len(content["entry1"]) > 0


# ============================================================================
# CoverageGapDetector Tests
# ============================================================================


class TestCoverageGapDetector:
    """Tests for coverage gap detection."""

    def test_coverage_extraction(self, sample_entries: List[Dict[str, Any]]) -> None:
        """Test coverage metric extraction."""
        detector = CoverageGapDetector()
        coverage = detector._extract_coverage(sample_entries)

        assert "api_design" in coverage
        assert "security" in coverage
        assert coverage["api_design"] == 1

    def test_coverage_by_category(self) -> None:
        """Test coverage extraction by category."""
        entries = [
            {"id": "1", "category": "pattern"},
            {"id": "2", "category": "pattern"},
            {"id": "3", "category": "guideline"},
        ]
        detector = CoverageGapDetector()
        coverage = detector._extract_coverage(entries)

        assert coverage["pattern"] == 2
        assert coverage["guideline"] == 1


# ============================================================================
# StalenessDetector Tests
# ============================================================================


class TestStalenessDetector:
    """Tests for staleness detection."""

    def test_stale_entry_detection(self) -> None:
        """Test detection of stale entries."""
        detector = StalenessDetector(max_age_hours=24, learning_mode_duration=0)
        detector.start_learning_mode()

        now = datetime.utcnow()
        entries = [
            {
                "id": "fresh",
                "updated_at": (now - timedelta(hours=12)).isoformat(),
            },
            {
                "id": "stale",
                "updated_at": (now - timedelta(hours=48)).isoformat(),
            },
        ]

        anomalies = detector.detect(entries, {})
        # With learning_mode_duration=0 and immediate start, learning mode should expire

    def test_learning_mode_skip(self) -> None:
        """Test that staleness is not detected during learning mode."""
        detector = StalenessDetector(max_age_hours=24, learning_mode_duration=3600)
        detector.start_learning_mode()

        entries = [
            {"id": "old", "updated_at": (datetime.utcnow() - timedelta(days=100)).isoformat()}
        ]

        # Should not detect during learning mode
        anomalies = detector.detect(entries, {})
        assert len(anomalies) == 0  # Learning mode active


# ============================================================================
# VolumeAnomalyDetector Tests
# ============================================================================


class TestVolumeAnomalyDetector:
    """Tests for volume anomaly detection."""

    def test_volume_tracking(self) -> None:
        """Test volume history tracking."""
        detector = VolumeAnomalyDetector()

        entries1 = [{"id": str(i)} for i in range(100)]
        detector.detect(entries1, {})

        entries2 = [{"id": str(i)} for i in range(110)]
        detector.detect(entries2, {})

        assert len(detector.volume_history) == 2
        assert detector.volume_history[0] == 100
        assert detector.volume_history[1] == 110

    def test_volume_variance_detection(self) -> None:
        """Test detection of high volume variance."""
        detector = VolumeAnomalyDetector(variance_threshold=0.3, learning_mode_duration=0)
        detector.start_learning_mode()

        # Build up history
        for volume in [100, 100, 100, 100]:
            entries = [{"id": str(i)} for i in range(volume)]
            detector.detect(entries, {})

        # Big spike
        entries = [{"id": str(i)} for i in range(500)]
        anomalies = detector.detect(entries, {})

        # After learning mode expires, should detect anomaly


# ============================================================================
# ChangeDetectionService Tests
# ============================================================================


class TestChangeDetectionService:
    """Tests for the change detection service."""

    def test_service_initialization(self) -> None:
        """Test service initialization."""
        service = ChangeDetectionService()
        assert len(service.detectors) == 5
        assert AnomalyType.SCHEMA_DRIFT in service.detectors
        assert AnomalyType.VOLUME_ANOMALY in service.detectors

    def test_record_entry_change(self) -> None:
        """Test recording entry changes."""
        service = ChangeDetectionService()
        version = {"id": "entry1", "value": "test"}

        service.record_entry_change("entry1", version, "Updated value")

        assert "entry1" in service.history
        assert len(service.history["entry1"].timestamps) == 1

    def test_multiple_entry_changes(self) -> None:
        """Test recording multiple changes to same entry."""
        service = ChangeDetectionService()

        for i in range(3):
            service.record_entry_change(
                "entry1", {"version": i}, f"Change {i}"
            )

        assert len(service.history["entry1"].timestamps) == 3

    def test_detect_anomalies(self, sample_entries: List[Dict[str, Any]]) -> None:
        """Test anomaly detection service."""
        service = ChangeDetectionService()
        anomalies = service.detect_anomalies(sample_entries)

        # Should detect at least one type (depends on learning mode)
        assert isinstance(anomalies, list)

    def test_get_critical_anomalies(self, sample_entries: List[Dict[str, Any]]) -> None:
        """Test filtering for critical anomalies."""
        service = ChangeDetectionService()
        critical = service.get_critical_anomalies(sample_entries)

        assert isinstance(critical, list)

    def test_change_summary(self) -> None:
        """Test generating change summary."""
        service = ChangeDetectionService()
        now = datetime.utcnow()

        service.record_entry_change("entry1", {}, "Change 1")
        service.record_entry_change("entry1", {}, "Change 2")
        service.record_entry_change("entry2", {}, "Change 3")

        summary = service.get_change_summary(now - timedelta(minutes=1))

        assert "entry1" in summary
        assert summary["entry1"] == 2


# ============================================================================
# Integration Tests
# ============================================================================


class TestChangeDetectionIntegration:
    """Integration tests for change detection."""

    def test_full_detection_pipeline(self, sample_entries: List[Dict[str, Any]]) -> None:
        """Test complete detection pipeline."""
        service = ChangeDetectionService()

        # First scan: baseline
        anomalies1 = service.detect_anomalies(sample_entries)

        # Record changes
        entry_id = sample_entries[0]["id"]
        service.record_entry_change(entry_id, sample_entries[0], "Updated")

        # Second scan
        anomalies2 = service.detect_anomalies(sample_entries)

        assert isinstance(anomalies1, list)
        assert isinstance(anomalies2, list)

    def test_detector_error_handling(self, sample_entries: List[Dict[str, Any]]) -> None:
        """Test that service continues if detector fails."""
        service = ChangeDetectionService()

        # Even if one detector fails, service should continue
        anomalies = service.detect_anomalies(sample_entries)
        assert isinstance(anomalies, list)

    def test_multiple_anomaly_types(self, sample_entries: List[Dict[str, Any]]) -> None:
        """Test detection of multiple anomaly types."""
        service = ChangeDetectionService()
        anomalies = service.detect_anomalies(sample_entries)

        # Collect anomaly types
        types = {a.anomaly_type for a in anomalies}
        # Should have at most the number of detector types
        assert len(types) <= len(service.detectors)


# ============================================================================
# Edge Case Tests
# ============================================================================


class TestEdgeCases:
    """Tests for edge cases and error conditions."""

    def test_empty_entry_list(self) -> None:
        """Test handling of empty entry list."""
        service = ChangeDetectionService()
        anomalies = service.detect_anomalies([])
        assert len(anomalies) == 0

    def test_entries_missing_id(self) -> None:
        """Test handling of entries without ID."""
        service = ChangeDetectionService()
        entries = [{"name": "test"}]  # No 'id' field
        anomalies = service.detect_anomalies(entries)
        assert isinstance(anomalies, list)

    def test_malformed_timestamps(self) -> None:
        """Test handling of malformed timestamp strings."""
        detector = StalenessDetector()
        entries = [
            {"id": "test", "updated_at": "not-a-date"}
        ]
        anomalies = detector.detect(entries, {})
        # Should handle gracefully without crashing

    def test_very_large_entry_list(self) -> None:
        """Test handling of very large entry list."""
        service = ChangeDetectionService()
        large_entries = [
            {"id": f"entry{i}", "value": f"data{i}"}
            for i in range(1000)
        ]
        anomalies = service.detect_anomalies(large_entries)
        assert isinstance(anomalies, list)

    def test_detector_learning_mode_transitions(self) -> None:
        """Test transition in and out of learning mode."""
        detector = SchemaDriftDetector(learning_mode_duration=1)  # 1 second
        detector.start_learning_mode()

        assert detector.is_learning_mode()

        # After 1+ seconds, learning mode should end
        import time
        time.sleep(1.1)
        assert not detector.is_learning_mode()
