"""
WAVE-O Stage 2 Tests: Contradiction Resolver (ENH-068)
RED Phase - 8 tests for automated resolution strategies
"""

import pytest
from pathlib import Path
from datetime import datetime
from cortex.governance.validation.contradiction_resolver import (
    ContradictionResolver,
    ResolutionStrategy,
    Resolution,
    ResolutionStatus
)
from cortex.governance.validation.cross_reference_validator import (
    ContradictionReport,
    ContradictionType,
    ContradictionSeverity
)


class TestResolutionStrategies:
    """Test automated resolution strategy selection"""
    
    @pytest.fixture
    def resolver(self):
        """Create resolver instance"""
        return ContradictionResolver()
    
    def test_timestamp_auto_resolution(self, resolver):
        """Test automatic resolution of timestamp contradictions"""
        report = ContradictionReport(
            file_path=Path("test.yaml"),
            contradiction_type=ContradictionType.TIMESTAMP,
            severity=ContradictionSeverity.HIGH,
            details="completion_date (2026-02-15) is after last_updated (2026-02-12)",
            suggested_fix="Update last_updated to be >= completion_date",
            confidence=0.95
        )
        
        resolution = resolver.resolve(report, strategy=ResolutionStrategy.AUTOMATIC)
        
        assert resolution.status == ResolutionStatus.RESOLVED
        assert resolution.resolution_type == ResolutionStrategy.AUTOMATIC
        assert "last_updated" in resolution.changes
        assert resolution.confidence >= 0.9
    
    def test_metric_auto_resolution(self, resolver):
        """Test automatic resolution of metric contradictions"""
        report = ContradictionReport(
            file_path=Path("test.yaml"),
            contradiction_type=ContradictionType.METRIC,
            severity=ContradictionSeverity.MEDIUM,
            details="tests_passing (150) exceeds tests_total (100)",
            suggested_fix="Verify tests_total count",
            confidence=0.85
        )
        
        resolution = resolver.resolve(report, strategy=ResolutionStrategy.AUTOMATIC)
        
        assert resolution.status in [ResolutionStatus.RESOLVED, ResolutionStatus.MANUAL_REVIEW_REQUIRED]
        if resolution.status == ResolutionStatus.RESOLVED:
            assert "tests_total" in resolution.changes or "tests_passing" in resolution.changes
    
    def test_manual_override(self, resolver):
        """Test manual resolution override capability"""
        report = ContradictionReport(
            file_path=Path("test.yaml"),
            contradiction_type=ContradictionType.DEPENDENCY,
            severity=ContradictionSeverity.CRITICAL,
            details="Circular dependency detected: A → B → C → A",
            suggested_fix="Break circular dependency",
            confidence=1.0
        )
        
        # Manual override with specific changes
        manual_changes = {"dependencies": ["A", "B"]}  # Remove C to break cycle
        resolution = resolver.resolve(
            report, 
            strategy=ResolutionStrategy.MANUAL_OVERRIDE,
            manual_changes=manual_changes
        )
        
        assert resolution.status == ResolutionStatus.RESOLVED
        assert resolution.resolution_type == ResolutionStrategy.MANUAL_OVERRIDE
        assert resolution.changes == manual_changes


class TestResolutionHistory:
    """Test resolution history tracking"""
    
    @pytest.fixture
    def resolver(self):
        """Create resolver instance"""
        return ContradictionResolver()
    
    def test_history_tracking(self, resolver):
        """Test that resolutions are tracked in history"""
        report = ContradictionReport(
            file_path=Path("test.yaml"),
            contradiction_type=ContradictionType.STATUS,
            severity=ContradictionSeverity.LOW,
            details="Status 'complete' but no completion_date",
            suggested_fix="Add completion_date or change status",
            confidence=0.8
        )
        
        resolution = resolver.resolve(report)
        
        # Check history
        history = resolver.get_history(file_path=Path("test.yaml"))
        assert len(history) == 1
        assert history[0].report == report
        assert history[0] == resolution
    
    def test_multiple_resolutions_history(self, resolver):
        """Test multiple resolutions tracked correctly"""
        reports = [
            ContradictionReport(
                file_path=Path("test.yaml"),
                contradiction_type=ContradictionType.TIMESTAMP,
                severity=ContradictionSeverity.HIGH,
                details="Timestamp issue 1",
                suggested_fix="Fix timestamp",
                confidence=0.9
            ),
            ContradictionReport(
                file_path=Path("test.yaml"),
                contradiction_type=ContradictionType.METRIC,
                severity=ContradictionSeverity.MEDIUM,
                details="Metric issue 1",
                suggested_fix="Fix metric",
                confidence=0.85
            )
        ]
        
        for report in reports:
            resolver.resolve(report)
        
        history = resolver.get_history(file_path=Path("test.yaml"))
        assert len(history) == 2
        assert {h.report.contradiction_type for h in history} == {ContradictionType.TIMESTAMP, ContradictionType.METRIC}


class TestRollback:
    """Test resolution rollback capability"""
    
    @pytest.fixture
    def resolver(self):
        """Create resolver instance"""
        return ContradictionResolver()
    
    def test_rollback_resolution(self, resolver):
        """Test rolling back a resolution"""
        report = ContradictionReport(
            file_path=Path("test.yaml"),
            contradiction_type=ContradictionType.TIMESTAMP,
            severity=ContradictionSeverity.HIGH,
            details="Timestamp contradiction",
            suggested_fix="Update timestamp",
            confidence=0.95
        )
        
        # Resolve
        resolution = resolver.resolve(report)
        resolution_id = resolution.resolution_id
        
        # Rollback
        rollback_result = resolver.rollback(resolution_id)
        
        assert rollback_result is True
        # Resolution should be marked as rolled back in history
        history = resolver.get_history(file_path=Path("test.yaml"))
        assert any(h.resolution_id == resolution_id and h.status == ResolutionStatus.ROLLED_BACK for h in history)
    
    def test_rollback_nonexistent_resolution(self, resolver):
        """Test rolling back non-existent resolution fails gracefully"""
        result = resolver.rollback("nonexistent-resolution-id")
        assert result is False


class TestConfidenceScoring:
    """Test confidence-based resolution decisions"""
    
    @pytest.fixture
    def resolver(self):
        """Create resolver instance"""
        return ContradictionResolver()
    
    def test_high_confidence_auto_resolve(self, resolver):
        """Test high-confidence contradictions resolved automatically"""
        report = ContradictionReport(
            file_path=Path("test.yaml"),
            contradiction_type=ContradictionType.TIMESTAMP,
            severity=ContradictionSeverity.HIGH,
            details="Completion date after last_updated",
            suggested_fix="Update last_updated",
            confidence=0.98  # Very high confidence
        )
        
        resolution = resolver.resolve(report, strategy=ResolutionStrategy.AUTOMATIC)
        
        # High confidence should result in automatic resolution
        assert resolution.status == ResolutionStatus.RESOLVED
        assert resolution.confidence >= 0.95
    
    def test_low_confidence_manual_review(self, resolver):
        """Test low-confidence contradictions require manual review"""
        report = ContradictionReport(
            file_path=Path("test.yaml"),
            contradiction_type=ContradictionType.METRIC,
            severity=ContradictionSeverity.MEDIUM,
            details="Ambiguous metric discrepancy",
            suggested_fix="Unclear fix required",
            confidence=0.55  # Low confidence
        )
        
        resolution = resolver.resolve(report, strategy=ResolutionStrategy.AUTOMATIC)
        
        # Low confidence should require manual review
        assert resolution.status == ResolutionStatus.MANUAL_REVIEW_REQUIRED
        assert resolution.confidence < 0.7
