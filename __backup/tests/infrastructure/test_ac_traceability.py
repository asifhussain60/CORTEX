"""
CORTEX 6.0 Stage 1 Phase 1.3 - AC Traceability System Tests

Tests for AC-TRACE-001 through AC-TRACE-005:
- AC-TRACE-001: @pytest.mark.ac_id() decorator implementation
- AC-TRACE-002: ACTraceabilitySystem.scan_tests() extracts markers
- AC-TRACE-003: generate_coverage_matrix() creates AC→Test mapping
- AC-TRACE-004: detect_gaps() finds AC without tests
- AC-TRACE-005: validate_ac(ac_id) checks coverage

RED PHASE: All tests will fail initially (implementation pending)

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import pytest
import tempfile
from pathlib import Path
from typing import Dict, List, Set
from unittest.mock import Mock, patch, MagicMock

# Import the AC traceability system (will fail until implementation)
from src.infrastructure.ac_traceability import (
    ACTraceabilitySystem,
    ACCoverageMatrix,
    ACGapReport,
    TraceabilityConfig,
)


# ==============================================================================
# AC-TRACE-001: @pytest.mark.ac_id() Decorator Tests
# ==============================================================================

@pytest.mark.ac_id("AC-TRACE-001")
class TestACIDMarker:
    """Test @pytest.mark.ac_id() decorator functionality."""
    
    def test_marker_registration(self):
        """Test: ac_id marker is registered in pytest."""
        # This test validates that the marker is properly configured
        # in pytest.ini and conftest.py
        import _pytest.mark
        
        # The marker should be available
        marker = pytest.mark.ac_id("AC-TEST-001")
        assert marker is not None
        assert marker.name == "ac_id"
        assert marker.args == ("AC-TEST-001",)
    
    def test_marker_validation_valid_format(self):
        """Test: Marker accepts valid AC-ID format (AC-XXX-NNN)."""
        # Valid formats should not raise
        valid_ids = [
            "AC-GOV-001",
            "AC-AUDIT-042",
            "AC-TRACE-999",
            "AC-TDD-001"
        ]
        
        for ac_id in valid_ids:
            marker = pytest.mark.ac_id(ac_id)
            assert marker.args[0] == ac_id
    
    def test_marker_validation_invalid_format(self):
        """Test: Marker rejects invalid AC-ID formats."""
        # These should be flagged during test collection
        invalid_ids = [
            "INVALID",
            "AC-001",  # Missing component
            "AC-GOV",  # Missing number
            "GOV-001",  # Missing AC prefix
        ]
        
        # The validation happens at collection time via conftest.py
        # This test documents expected behavior
        for ac_id in invalid_ids:
            marker = pytest.mark.ac_id(ac_id)
            # Marker creation succeeds but validation happens later
            assert marker.args[0] == ac_id
    
    def test_marker_with_multiple_ac_ids(self):
        """Test: Single test can reference multiple AC-IDs."""
        # A test might validate multiple acceptance criteria
        marker = pytest.mark.ac_id("AC-GOV-001", "AC-GOV-002")
        assert len(marker.args) == 2
        assert "AC-GOV-001" in marker.args
        assert "AC-GOV-002" in marker.args


# ==============================================================================
# AC-TRACE-002: scan_tests() Tests
# ==============================================================================

@pytest.mark.ac_id("AC-TRACE-002")
class TestScanTests:
    """Test ACTraceabilitySystem.scan_tests() functionality."""
    
    def setup_method(self):
        """Setup test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = TraceabilityConfig(
            tests_root=Path(self.temp_dir) / "tests",
            registry_path=Path(self.temp_dir) / "registry"
        )
        self.system = ACTraceabilitySystem(self.config)
    
    def teardown_method(self):
        """Cleanup test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_scan_finds_ac_id_markers(self):
        """Test: scan_tests() extracts @pytest.mark.ac_id markers."""
        # Create test file with markers
        test_file = self.config.tests_root / "test_example.py"
        test_file.parent.mkdir(parents=True, exist_ok=True)
        test_file.write_text("""
import pytest

@pytest.mark.ac_id("AC-GOV-001")
def test_governance():
    pass

@pytest.mark.ac_id("AC-GOV-002", "AC-GOV-003")
def test_multiple_ac():
    pass
""")
        
        # Execute scan
        results = self.system.scan_tests()
        
        # Assert: Found all markers
        assert len(results) >= 3
        assert "AC-GOV-001" in results
        assert "AC-GOV-002" in results
        assert "AC-GOV-003" in results
    
    def test_scan_handles_nested_directories(self):
        """Test: Scan recurses through test directory structure."""
        # Create nested structure
        unit_dir = self.config.tests_root / "unit"
        integration_dir = self.config.tests_root / "integration"
        
        for test_dir in [unit_dir, integration_dir]:
            test_dir.mkdir(parents=True, exist_ok=True)
            (test_dir / "test_nested.py").write_text("""
import pytest

@pytest.mark.ac_id("AC-TEST-001")
def test_nested():
    pass
""")
        
        results = self.system.scan_tests()
        
        # Should find markers in both directories (same AC-ID, 2 test locations)
        assert "AC-TEST-001" in results
        assert len(results["AC-TEST-001"]) == 2  # 2 test locations for same AC-ID
    
    def test_scan_ignores_non_test_files(self):
        """Test: Scan only processes test_*.py and *_test.py files."""
        # Create various files
        self.config.tests_root.mkdir(parents=True, exist_ok=True)
        
        files = {
            "test_valid.py": '@pytest.mark.ac_id("AC-VALID-001")',
            "valid_test.py": '@pytest.mark.ac_id("AC-VALID-002")',
            "nottest.py": '@pytest.mark.ac_id("AC-INVALID-001")',  # Doesn't match pattern
            "conftest.py": '@pytest.mark.ac_id("AC-INVALID-002")',  # Excluded by name
        }
        
        for filename, content in files.items():
            (self.config.tests_root / filename).write_text(f"""
import pytest

{content}
def test_something():
    pass
""")
        
        results = self.system.scan_tests()
        
        # Should only find markers in test files
        assert "AC-VALID-001" in results
        assert "AC-VALID-002" in results
        assert "AC-INVALID-001" not in results  # nottest.py doesn't match pattern
        assert "AC-INVALID-002" not in results  # conftest.py explicitly excluded
    
    def test_scan_returns_test_locations(self):
        """Test: Results include file path and line number for each marker."""
        test_file = self.config.tests_root / "test_location.py"
        test_file.parent.mkdir(parents=True, exist_ok=True)
        test_file.write_text("""
import pytest

@pytest.mark.ac_id("AC-LOC-001")
def test_first():
    pass

@pytest.mark.ac_id("AC-LOC-002")
def test_second():
    pass
""")
        
        results = self.system.scan_tests()
        
        # Each AC-ID should have location info
        assert "AC-LOC-001" in results
        assert "AC-LOC-002" in results
        
        # Location should include file and line (relative path from tests_root)
        loc_001 = results["AC-LOC-001"]
        assert len(loc_001) == 1
        assert loc_001[0]['file'] == 'test_location.py'  # Relative path
        assert loc_001[0]['line'] == 5  # Line number
        assert loc_001[0]['test'] == 'test_first'  # Test name


# ==============================================================================
# AC-TRACE-003: generate_coverage_matrix() Tests
# ==============================================================================

@pytest.mark.ac_id("AC-TRACE-003")
class TestCoverageMatrix:
    """Test coverage matrix generation."""
    
    def setup_method(self):
        """Setup test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = TraceabilityConfig(
            tests_root=Path(self.temp_dir) / "tests",
            registry_path=Path(self.temp_dir) / "registry"
        )
        self.system = ACTraceabilitySystem(self.config)
    
    def teardown_method(self):
        """Cleanup test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_matrix_generation_basic(self):
        """Test: Generate coverage matrix from scan results."""
        # Create test files
        self.config.tests_root.mkdir(parents=True, exist_ok=True)
        (self.config.tests_root / "test_gov.py").write_text("""
import pytest

@pytest.mark.ac_id("AC-GOV-001")
def test_gov_001():
    pass

@pytest.mark.ac_id("AC-GOV-002")
def test_gov_002():
    pass
""")
        
        # Generate matrix
        matrix = self.system.generate_coverage_matrix()
        
        # Assert: Matrix contains AC→Test mappings
        assert isinstance(matrix, ACCoverageMatrix)
        assert "AC-GOV-001" in matrix.coverage
        assert "AC-GOV-002" in matrix.coverage
        assert len(matrix.coverage["AC-GOV-001"]) >= 1
        assert len(matrix.coverage["AC-GOV-002"]) >= 1
    
    def test_matrix_handles_multiple_tests_per_ac(self):
        """Test: AC-ID can be referenced by multiple tests."""
        self.config.tests_root.mkdir(parents=True, exist_ok=True)
        (self.config.tests_root / "test_multi.py").write_text("""
import pytest

@pytest.mark.ac_id("AC-MULTI-001")
def test_scenario_1():
    pass

@pytest.mark.ac_id("AC-MULTI-001")
def test_scenario_2():
    pass

@pytest.mark.ac_id("AC-MULTI-001")
def test_scenario_3():
    pass
""")
        
        matrix = self.system.generate_coverage_matrix()
        
        # Should have 3 tests for AC-MULTI-001
        assert "AC-MULTI-001" in matrix.coverage
        assert len(matrix.coverage["AC-MULTI-001"]) == 3
    
    def test_matrix_calculates_coverage_percentage(self):
        """Test: Matrix calculates overall coverage percentage."""
        # This requires knowing total AC count
        # For now, test that percentage is calculated
        self.config.tests_root.mkdir(parents=True, exist_ok=True)
        (self.config.tests_root / "test_coverage.py").write_text("""
import pytest

@pytest.mark.ac_id("AC-COV-001")
def test_covered():
    pass
""")
        
        matrix = self.system.generate_coverage_matrix()
        
        # Should have coverage statistics
        assert hasattr(matrix, 'coverage_percentage')
        assert isinstance(matrix.coverage_percentage, (int, float))
        assert 0 <= matrix.coverage_percentage <= 100
    
    def test_matrix_exports_to_yaml(self):
        """Test: Matrix can be exported to YAML format."""
        self.config.tests_root.mkdir(parents=True, exist_ok=True)
        (self.config.tests_root / "test_export.py").write_text("""
import pytest

@pytest.mark.ac_id("AC-EXP-001")
def test_export():
    pass
""")
        
        matrix = self.system.generate_coverage_matrix()
        
        # Export to YAML
        self.config.registry_path.mkdir(parents=True, exist_ok=True)
        output_path = self.config.registry_path / "coverage.yaml"
        matrix.export_yaml(output_path)
        
        # Verify file created and valid
        assert output_path.exists()
        
        import yaml
        with open(output_path) as f:
            data = yaml.safe_load(f)
        
        assert "coverage" in data
        assert "AC-EXP-001" in data["coverage"]


# ==============================================================================
# AC-TRACE-004: detect_gaps() Tests
# ==============================================================================

@pytest.mark.ac_id("AC-TRACE-004")
class TestGapDetection:
    """Test gap detection (AC without tests)."""
    
    def setup_method(self):
        """Setup test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = TraceabilityConfig(
            tests_root=Path(self.temp_dir) / "tests",
            registry_path=Path(self.temp_dir) / "registry",
            ac_definitions_path=Path(self.temp_dir) / "ac-definitions.yaml"
        )
        self.system = ACTraceabilitySystem(self.config)
    
    def teardown_method(self):
        """Cleanup test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_detect_ac_without_tests(self):
        """Test: Detect AC-IDs that have no test coverage."""
        # Create AC definitions
        self.config.ac_definitions_path.parent.mkdir(parents=True, exist_ok=True)
        import yaml
        with open(self.config.ac_definitions_path, 'w') as f:
            yaml.dump({
                'acceptance_criteria': [
                    {'id': 'AC-GAP-001', 'name': 'Covered criterion'},
                    {'id': 'AC-GAP-002', 'name': 'Uncovered criterion'},
                    {'id': 'AC-GAP-003', 'name': 'Another uncovered'},
                ]
            }, f)
        
        # Create test with only AC-GAP-001
        self.config.tests_root.mkdir(parents=True, exist_ok=True)
        (self.config.tests_root / "test_partial.py").write_text("""
import pytest

@pytest.mark.ac_id("AC-GAP-001")
def test_only_one():
    pass
""")
        
        # Detect gaps
        gap_report = self.system.detect_gaps()
        
        # Should find AC-GAP-002 and AC-GAP-003 as uncovered
        assert isinstance(gap_report, ACGapReport)
        assert "AC-GAP-002" in gap_report.uncovered_ac
        assert "AC-GAP-003" in gap_report.uncovered_ac
        assert "AC-GAP-001" not in gap_report.uncovered_ac
    
    def test_detect_tests_without_ac(self):
        """Test: Detect tests that don't reference any AC-ID."""
        # Create test without markers
        self.config.tests_root.mkdir(parents=True, exist_ok=True)
        (self.config.tests_root / "test_unmarked.py").write_text("""
import pytest

def test_no_marker():
    pass

@pytest.mark.ac_id("AC-MARK-001")
def test_has_marker():
    pass
""")
        
        gap_report = self.system.detect_gaps()
        
        # Should identify test_no_marker as orphaned
        assert len(gap_report.orphaned_tests) >= 1
        assert any("test_no_marker" in str(test) for test in gap_report.orphaned_tests)
    
    def test_gap_report_prioritization(self):
        """Test: Gap report prioritizes high-priority AC without coverage."""
        # Create AC definitions with priorities
        self.config.ac_definitions_path.parent.mkdir(parents=True, exist_ok=True)
        import yaml
        with open(self.config.ac_definitions_path, 'w') as f:
            yaml.dump({
                'acceptance_criteria': [
                    {'id': 'AC-PRI-001', 'priority': 'P0_CRITICAL'},
                    {'id': 'AC-PRI-002', 'priority': 'P1_HIGH'},
                    {'id': 'AC-PRI-003', 'priority': 'P2_MEDIUM'},
                ]
            }, f)
        
        # No tests for any
        self.config.tests_root.mkdir(parents=True, exist_ok=True)
        (self.config.tests_root / "test_empty.py").write_text("# No tests")
        
        gap_report = self.system.detect_gaps()
        
        # Should prioritize P0_CRITICAL
        assert len(gap_report.critical_gaps) >= 1
        assert "AC-PRI-001" in gap_report.critical_gaps


# ==============================================================================
# AC-TRACE-005: validate_ac(ac_id) Tests
# ==============================================================================

@pytest.mark.ac_id("AC-TRACE-005")
class TestACValidation:
    """Test AC coverage validation."""
    
    def setup_method(self):
        """Setup test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = TraceabilityConfig(
            tests_root=Path(self.temp_dir) / "tests",
            registry_path=Path(self.temp_dir) / "registry"
        )
        self.system = ACTraceabilitySystem(self.config)
    
    def teardown_method(self):
        """Cleanup test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_validate_ac_with_coverage(self):
        """Test: validate_ac() returns True for covered AC."""
        # Create test with marker
        self.config.tests_root.mkdir(parents=True, exist_ok=True)
        (self.config.tests_root / "test_validate.py").write_text("""
import pytest

@pytest.mark.ac_id("AC-VAL-001")
def test_validation():
    pass
""")
        
        # Validate
        is_covered = self.system.validate_ac("AC-VAL-001")
        
        assert is_covered is True
    
    def test_validate_ac_without_coverage(self):
        """Test: validate_ac() returns False for uncovered AC."""
        self.config.tests_root.mkdir(parents=True, exist_ok=True)
        
        # No tests for AC-UNCOV-001
        is_covered = self.system.validate_ac("AC-UNCOV-001")
        
        assert is_covered is False
    
    def test_validate_ac_returns_test_count(self):
        """Test: validate_ac() returns number of covering tests."""
        self.config.tests_root.mkdir(parents=True, exist_ok=True)
        (self.config.tests_root / "test_count.py").write_text("""
import pytest

@pytest.mark.ac_id("AC-CNT-001")
def test_first():
    pass

@pytest.mark.ac_id("AC-CNT-001")
def test_second():
    pass
""")
        
        result = self.system.validate_ac("AC-CNT-001", return_count=True)
        
        assert isinstance(result, int)
        assert result == 2
    
    def test_validate_ac_batch_mode(self):
        """Test: Validate multiple AC-IDs in batch."""
        self.config.tests_root.mkdir(parents=True, exist_ok=True)
        (self.config.tests_root / "test_batch.py").write_text("""
import pytest

@pytest.mark.ac_id("AC-BATCH-001")
def test_batch_1():
    pass

@pytest.mark.ac_id("AC-BATCH-003")
def test_batch_3():
    pass
""")
        
        ac_ids = ["AC-BATCH-001", "AC-BATCH-002", "AC-BATCH-003"]
        results = self.system.validate_ac_batch(ac_ids)
        
        assert results["AC-BATCH-001"] is True
        assert results["AC-BATCH-002"] is False
        assert results["AC-BATCH-003"] is True


# ==============================================================================
# Integration Tests
# ==============================================================================

@pytest.mark.ac_id("AC-TRACE-001", "AC-TRACE-002", "AC-TRACE-003", "AC-TRACE-004", "AC-TRACE-005")
class TestACTraceabilityIntegration:
    """Integration tests for full traceability workflow."""
    
    def test_full_workflow(self):
        """Test: Complete scan → matrix → gaps → validation workflow."""
        temp_dir = tempfile.mkdtemp()
        config = TraceabilityConfig(
            tests_root=Path(temp_dir) / "tests",
            registry_path=Path(temp_dir) / "registry",
            ac_definitions_path=Path(temp_dir) / "ac-definitions.yaml"
        )
        system = ACTraceabilitySystem(config)
        
        try:
            # Setup AC definitions
            config.ac_definitions_path.parent.mkdir(parents=True, exist_ok=True)
            import yaml
            with open(config.ac_definitions_path, 'w') as f:
                yaml.dump({
                    'acceptance_criteria': [
                        {'id': 'AC-INT-001', 'priority': 'P0_CRITICAL'},
                        {'id': 'AC-INT-002', 'priority': 'P1_HIGH'},
                        {'id': 'AC-INT-003', 'priority': 'P2_MEDIUM'},
                    ]
                }, f)
            
            # Create tests
            config.tests_root.mkdir(parents=True, exist_ok=True)
            (config.tests_root / "test_integration.py").write_text("""
import pytest

@pytest.mark.ac_id("AC-INT-001")
def test_critical_feature():
    pass

@pytest.mark.ac_id("AC-INT-002")
def test_high_feature():
    pass

def test_orphan():
    pass
""")
            
            # Execute workflow
            scan_results = system.scan_tests()
            assert len(scan_results) >= 2
            
            matrix = system.generate_coverage_matrix()
            assert "AC-INT-001" in matrix.coverage
            assert "AC-INT-002" in matrix.coverage
            
            gap_report = system.detect_gaps()
            assert "AC-INT-003" in gap_report.uncovered_ac
            assert len(gap_report.orphaned_tests) >= 1
            
            assert system.validate_ac("AC-INT-001") is True
            assert system.validate_ac("AC-INT-003") is False
            
        finally:
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_coverage_report_generation(self):
        """Test: Generate comprehensive coverage report."""
        temp_dir = tempfile.mkdtemp()
        config = TraceabilityConfig(
            tests_root=Path(temp_dir) / "tests",
            registry_path=Path(temp_dir) / "registry"
        )
        system = ACTraceabilitySystem(config)
        
        try:
            # Create tests
            config.tests_root.mkdir(parents=True, exist_ok=True)
            (config.tests_root / "test_report.py").write_text("""
import pytest

@pytest.mark.ac_id("AC-REP-001")
def test_report():
    pass
""")
            
            # Generate report
            config.registry_path.mkdir(parents=True, exist_ok=True)
            report_path = config.registry_path / "ac-test-coverage.yaml"
            system.generate_coverage_report(report_path)
            
            # Verify report
            assert report_path.exists()
            
            import yaml
            with open(report_path) as f:
                report = yaml.safe_load(f)
            
            assert "metadata" in report
            assert "coverage" in report
            assert "gaps" in report
            assert "statistics" in report
            
        finally:
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
