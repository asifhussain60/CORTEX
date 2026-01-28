"""Test suite for naming violation detector (NAMING-001).

Tests CORE-028 file naming policy enforcement:
- Kebab-case compliance (hyphens, not underscores)
- 25-character limit
- Python module naming (.py files)
"""

import pytest
from pathlib import Path
import tempfile
import shutil
from cortex.tools.naming_violation_detector import (
    NamingViolationDetector,
    ViolationType,
    Violation,
)


@pytest.fixture
def temp_workspace():
    """Create temporary workspace for testing."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def detector(temp_workspace):
    """Create detector instance with temp workspace."""
    return NamingViolationDetector(workspace_root=temp_workspace)


class TestNamingViolationDetector:
    """Test suite for NamingViolationDetector class."""

    def test_detector_initialization(self, temp_workspace):
        """Test detector initializes with workspace root."""
        detector = NamingViolationDetector(workspace_root=temp_workspace)
        assert detector.workspace_root == temp_workspace
        assert detector.violations == []

    def test_detect_underscore_violation(self, detector, temp_workspace):
        """Test detection of underscore naming (should be kebab-case)."""
        # Create file with underscore
        test_file = temp_workspace / "git_history_analyzer.py"
        test_file.touch()
        
        violations = detector.scan_file(test_file)
        
        assert len(violations) == 1
        assert violations[0].type == ViolationType.UNDERSCORE
        assert violations[0].file_path == test_file
        assert "git-history-analyzer.py" in violations[0].suggested_fix

    def test_detect_length_violation(self, detector, temp_workspace):
        """Test detection of 25-character limit violation."""
        # Create file exceeding 25 chars (without .py extension)
        long_name = "very-long-orchestrator-name.py"  # 30 chars total, 27 without .py
        test_file = temp_workspace / long_name
        test_file.touch()
        
        violations = detector.scan_file(test_file)
        
        assert len(violations) == 1
        assert violations[0].type == ViolationType.LENGTH
        assert violations[0].file_path == test_file
        assert len(violations[0].suggested_fix) <= 25 + 3  # +3 for .py

    def test_detect_multiple_violations(self, detector, temp_workspace):
        """Test detection of both underscore and length violations."""
        # Create file with both violations
        test_file = temp_workspace / "very_long_underscore_orchestrator_name.py"  # 40+ chars
        test_file.touch()
        
        violations = detector.scan_file(test_file)
        
        assert len(violations) == 2
        violation_types = {v.type for v in violations}
        assert ViolationType.UNDERSCORE in violation_types
        assert ViolationType.LENGTH in violation_types

    def test_valid_file_no_violations(self, detector, temp_workspace):
        """Test that valid files produce no violations."""
        # Create valid file (kebab-case, under 25 chars)
        test_file = temp_workspace / "lens-orchestrator.py"
        test_file.touch()
        
        violations = detector.scan_file(test_file)
        
        assert len(violations) == 0

    def test_scan_workspace_multiple_files(self, detector, temp_workspace):
        """Test scanning entire workspace with multiple files."""
        # Create mix of valid and invalid files
        (temp_workspace / "valid-file.py").touch()
        (temp_workspace / "invalid_file.py").touch()
        (temp_workspace / "another-valid.py").touch()
        (temp_workspace / "very_long_name_exceeds_limit.py").touch()
        
        all_violations = detector.scan_workspace()
        
        assert len(all_violations) >= 2  # At least 2 violating files
        # Check that violations are grouped by file
        violating_files = {v.file_path for v in all_violations}
        assert any("invalid_file.py" in str(f) for f in violating_files)
        assert any("very_long_name_exceeds_limit.py" in str(f) for f in violating_files)

    def test_ignore_non_python_files(self, detector, temp_workspace):
        """Test that non-.py files are ignored."""
        # Create files with various extensions
        (temp_workspace / "invalid_name.txt").touch()
        (temp_workspace / "invalid_name.yaml").touch()
        (temp_workspace / "invalid_name.md").touch()
        
        all_violations = detector.scan_workspace()
        
        # Should ignore non-Python files
        assert len(all_violations) == 0

    def test_generate_report_json(self, detector, temp_workspace):
        """Test JSON report generation."""
        # Create some violations
        (temp_workspace / "invalid_file.py").touch()
        detector.scan_workspace()
        
        report = detector.generate_report(format="json")
        
        assert isinstance(report, str)
        assert "invalid_file.py" in report
        assert "violations" in report.lower()

    def test_generate_report_text(self, detector, temp_workspace):
        """Test text report generation."""
        # Create some violations
        (temp_workspace / "invalid_file.py").touch()
        detector.scan_workspace()
        
        report = detector.generate_report(format="text")
        
        assert isinstance(report, str)
        assert "invalid_file.py" in report
        assert "CORE-028" in report or "violation" in report.lower()

    def test_suggest_fix_underscore_to_hyphen(self, detector):
        """Test fix suggestion converts underscores to hyphens."""
        suggested = detector.suggest_fix("git_history_analyzer.py")
        assert suggested == "git-history-analyzer.py"

    def test_suggest_fix_length_truncation(self, detector):
        """Test fix suggestion truncates long names."""
        long_name = "very-long-orchestrator-name-exceeds-limit.py"
        suggested = detector.suggest_fix(long_name)
        
        # Should be <= 25 chars (excluding .py)
        name_without_ext = suggested.replace(".py", "")
        assert len(name_without_ext) <= 25

    def test_suggest_fix_combined_violations(self, detector):
        """Test fix suggestion handles both violations."""
        problematic = "very_long_underscore_name_exceeds_limit.py"
        suggested = detector.suggest_fix(problematic)
        
        # Should fix both issues
        assert "_" not in suggested  # No underscores
        name_without_ext = suggested.replace(".py", "")
        assert len(name_without_ext) <= 25  # Within limit
