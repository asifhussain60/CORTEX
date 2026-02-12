"""
Tests for Cross-Reference Validator (ENH-068)
WAVE-O Stage 1: Data Integrity Validation

AC-WAVE-O-001: Cross-reference validation across registry files
"""
import pytest
from pathlib import Path
from datetime import datetime
from typing import List

from cortex.validation.cross_reference_validator import (
    CrossReferenceValidator,
    ContradictionReport,
    ContradictionType,
    ContradictionSeverity,
)


class TestCrossReferenceValidator:
    """Test suite for cross-reference validator"""
    
    @pytest.fixture
    def validator(self):
        """Create validator instance"""
        return CrossReferenceValidator()
    
    @pytest.fixture
    def sample_registry_data(self, tmp_path):
        """Create sample registry YAML files"""
        registry_path = tmp_path / "registry"
        registry_path.mkdir()
        
        # Wave file with valid data
        wave_file = registry_path / "wave-test.yaml"
        wave_file.write_text("""
wave_id: WAVE-TEST
status: complete
completion_date: "2026-02-12"
last_updated: "2026-02-12T23:59:59Z"
tests_total: 100
tests_passing: 100
dependencies: []
""")
        
        return registry_path


class TestTimestampValidation:
    """Test timestamp consistency validation"""
    
    @pytest.fixture
    def validator(self):
        return CrossReferenceValidator()
    
    def test_detect_completion_after_last_updated(self, validator, tmp_path):
        """Should detect completion_date > last_updated contradiction"""
        registry_path = tmp_path / "registry"
        registry_path.mkdir()
        
        file_path = registry_path / "invalid-timestamps.yaml"
        file_path.write_text("""
wave_id: WAVE-INVALID
status: complete
completion_date: "2026-02-15"
last_updated: "2026-02-12T00:00:00Z"
""")
        
        reports = validator.validate_registry(registry_path)
        
        timestamp_reports = [r for r in reports if r.contradiction_type == ContradictionType.TIMESTAMP]
        assert len(timestamp_reports) > 0
        assert any("completion_date" in r.details.lower() for r in timestamp_reports)
    
    def test_valid_timestamps_no_contradiction(self, validator, tmp_path):
        """Should pass when timestamps are consistent"""
        registry_path = tmp_path / "registry"
        registry_path.mkdir()
        
        file_path = registry_path / "valid-timestamps.yaml"
        file_path.write_text("""
wave_id: WAVE-VALID
status: complete
completion_date: "2026-02-12"
last_updated: "2026-02-12T23:59:59Z"
""")
        
        reports = validator.validate_registry(registry_path)
        
        timestamp_reports = [r for r in reports if r.contradiction_type == ContradictionType.TIMESTAMP]
        assert len(timestamp_reports) == 0


class TestMetricValidation:
    """Test metric accuracy validation"""
    
    @pytest.fixture
    def validator(self):
        return CrossReferenceValidator()
    
    def test_detect_tests_passing_exceeds_total(self, validator, tmp_path):
        """Should detect tests_passing > tests_total"""
        registry_path = tmp_path / "registry"
        registry_path.mkdir()
        
        file_path = registry_path / "invalid-metrics.yaml"
        file_path.write_text("""
wave_id: WAVE-METRIC-ERROR
tests_total: 100
tests_passing: 120
""")
        
        reports = validator.validate_registry(registry_path)
        
        metric_reports = [r for r in reports if r.contradiction_type == ContradictionType.METRIC]
        assert len(metric_reports) > 0
        assert any("tests_passing" in r.details.lower() for r in metric_reports)
    
    def test_valid_metrics_no_contradiction(self, validator, tmp_path):
        """Should pass when metrics are valid"""
        registry_path = tmp_path / "registry"
        registry_path.mkdir()
        
        file_path = registry_path / "valid-metrics.yaml"
        file_path.write_text("""
wave_id: WAVE-VALID-METRICS
tests_total: 100
tests_passing: 95
""")
        
        reports = validator.validate_registry(registry_path)
        
        metric_reports = [r for r in reports if r.contradiction_type == ContradictionType.METRIC]
        assert len(metric_reports) == 0
    
    def test_detect_negative_metrics(self, validator, tmp_path):
        """Should detect negative metric values"""
        registry_path = tmp_path / "registry"
        registry_path.mkdir()
        
        file_path = registry_path / "negative-metrics.yaml"
        file_path.write_text("""
wave_id: WAVE-NEGATIVE
tests_total: -10
tests_passing: 5
""")
        
        reports = validator.validate_registry(registry_path)
        
        metric_reports = [r for r in reports if r.contradiction_type == ContradictionType.METRIC]
        assert len(metric_reports) > 0


class TestDependencyValidation:
    """Test dependency graph validation"""
    
    @pytest.fixture
    def validator(self):
        return CrossReferenceValidator()
    
    def test_detect_circular_dependency(self, validator, tmp_path):
        """Should detect circular dependencies"""
        registry_path = tmp_path / "registry"
        registry_path.mkdir()
        
        wave_a = registry_path / "wave-a.yaml"
        wave_a.write_text("""
wave_id: WAVE-A
dependencies: ["WAVE-B"]
""")
        
        wave_b = registry_path / "wave-b.yaml"
        wave_b.write_text("""
wave_id: WAVE-B
dependencies: ["WAVE-A"]
""")
        
        reports = validator.validate_registry(registry_path)
        
        dep_reports = [r for r in reports if r.contradiction_type == ContradictionType.DEPENDENCY]
        assert len(dep_reports) > 0
        assert any("circular" in r.details.lower() for r in dep_reports)
    
    def test_detect_missing_dependency(self, validator, tmp_path):
        """Should detect references to non-existent dependencies"""
        registry_path = tmp_path / "registry"
        registry_path.mkdir()
        
        wave_file = registry_path / "wave-orphan.yaml"
        wave_file.write_text("""
wave_id: WAVE-ORPHAN
dependencies: ["WAVE-NONEXISTENT"]
""")
        
        reports = validator.validate_registry(registry_path)
        
        dep_reports = [r for r in reports if r.contradiction_type == ContradictionType.DEPENDENCY]
        assert len(dep_reports) > 0
        assert any("WAVE-NONEXISTENT" in r.details for r in dep_reports)
    
    def test_valid_dependencies_no_contradiction(self, validator, tmp_path):
        """Should pass when dependencies are valid"""
        registry_path = tmp_path / "registry"
        registry_path.mkdir()
        
        wave_a = registry_path / "wave-a.yaml"
        wave_a.write_text("""
wave_id: WAVE-A
dependencies: []
""")
        
        wave_b = registry_path / "wave-b.yaml"
        wave_b.write_text("""
wave_id: WAVE-B
dependencies: ["WAVE-A"]
""")
        
        reports = validator.validate_registry(registry_path)
        
        dep_reports = [r for r in reports if r.contradiction_type == ContradictionType.DEPENDENCY]
        assert len(dep_reports) == 0


class TestStatusValidation:
    """Test status consistency validation"""
    
    @pytest.fixture
    def validator(self):
        return CrossReferenceValidator()
    
    def test_detect_complete_without_completion_date(self, validator, tmp_path):
        """Should detect status=complete without completion_date"""
        registry_path = tmp_path / "registry"
        registry_path.mkdir()
        
        file_path = registry_path / "incomplete-completion.yaml"
        file_path.write_text("""
wave_id: WAVE-INCOMPLETE
status: complete
completion_date: null
""")
        
        reports = validator.validate_registry(registry_path)
        
        status_reports = [r for r in reports if r.contradiction_type == ContradictionType.STATUS]
        assert len(status_reports) > 0
        assert any("completion_date" in r.details.lower() for r in status_reports)
    
    def test_detect_pending_with_completion_date(self, validator, tmp_path):
        """Should detect status=pending with completion_date"""
        registry_path = tmp_path / "registry"
        registry_path.mkdir()
        
        file_path = registry_path / "premature-completion.yaml"
        file_path.write_text("""
wave_id: WAVE-PREMATURE
status: pending
completion_date: "2026-02-12"
""")
        
        reports = validator.validate_registry(registry_path)
        
        status_reports = [r for r in reports if r.contradiction_type == ContradictionType.STATUS]
        assert len(status_reports) > 0
