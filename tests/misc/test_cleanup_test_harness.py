"""
Unit tests for CleanupTestHarness

Tests baseline capture, category validation, rollback mechanism, and failure detection.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
Version: 3.2.1
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import json

from src.operations.modules.cleanup.cleanup_test_harness import (
    CleanupTestHarness,
    TestBaseline,
    ValidationResult
)


@pytest.fixture
def temp_workspace(tmp_path):
    """Create a temporary workspace for testing"""
    workspace = tmp_path / "test_workspace"
    workspace.mkdir()
    
    # Create basic structure
    (workspace / "src").mkdir()
    (workspace / "tests").mkdir()
    (workspace / "tests" / "test_example.py").write_text("""
def test_passing():
    assert True

def test_another():
    assert 1 + 1 == 2
""")
    
    return workspace


@pytest.fixture
def mock_harness(temp_workspace):
    """Create a test harness with mocked test execution"""
    harness = CleanupTestHarness(
        workspace_root=temp_workspace,
        test_command="echo 'test output'",
        coverage_command="echo 'coverage output'"
    )
    return harness


class TestTestBaseline:
    """Test TestBaseline dataclass"""
    
    def test_baseline_creation(self):
        """Test creating a baseline"""
        baseline = TestBaseline(
            timestamp="2025-11-30T10:00:00",
            total_tests=10,
            passed_tests=9,
            failed_tests=1,
            skipped_tests=0,
            coverage_percent=85.5,
            test_duration=2.5
        )
        
        assert baseline.total_tests == 10
        assert baseline.passed_tests == 9
        assert baseline.failed_tests == 1
        assert baseline.coverage_percent == 85.5
    
    def test_baseline_to_dict(self):
        """Test converting baseline to dictionary"""
        baseline = TestBaseline(
            timestamp="2025-11-30T10:00:00",
            total_tests=10,
            passed_tests=10,
            failed_tests=0,
            skipped_tests=0,
            coverage_percent=90.0,
            test_duration=1.5
        )
        
        data = baseline.to_dict()
        
        assert data['total_tests'] == 10
        assert data['passed_tests'] == 10
        assert data['coverage_percent'] == 90.0
        assert 'timestamp' in data
    
    def test_baseline_from_dict(self):
        """Test creating baseline from dictionary"""
        data = {
            'timestamp': "2025-11-30T10:00:00",
            'total_tests': 10,
            'passed_tests': 10,
            'failed_tests': 0,
            'skipped_tests': 0,
            'coverage_percent': 90.0,
            'test_duration': 1.5,
            'test_details': {}
        }
        
        baseline = TestBaseline.from_dict(data)
        
        assert baseline.total_tests == 10
        assert baseline.passed_tests == 10
        assert baseline.coverage_percent == 90.0


class TestValidationResult:
    """Test ValidationResult dataclass"""
    
    def test_validation_result_success(self):
        """Test successful validation result"""
        baseline = TestBaseline(
            timestamp="2025-11-30T10:00:00",
            total_tests=10,
            passed_tests=10,
            failed_tests=0,
            skipped_tests=0,
            coverage_percent=90.0,
            test_duration=1.5
        )
        
        result = ValidationResult(
            success=True,
            baseline=baseline,
            current=baseline,
            issues=[],
            warnings=[]
        )
        
        assert result.success
        assert not result.has_failures()
        assert len(result.issues) == 0
    
    def test_validation_result_failure(self):
        """Test failed validation result"""
        baseline = TestBaseline(
            timestamp="2025-11-30T10:00:00",
            total_tests=10,
            passed_tests=10,
            failed_tests=0,
            skipped_tests=0,
            coverage_percent=90.0,
            test_duration=1.5
        )
        
        current = TestBaseline(
            timestamp="2025-11-30T10:05:00",
            total_tests=10,
            passed_tests=8,
            failed_tests=2,
            skipped_tests=0,
            coverage_percent=85.0,
            test_duration=1.8
        )
        
        result = ValidationResult(
            success=False,
            baseline=baseline,
            current=current,
            issues=["New test failures: 0 → 2"],
            warnings=["Coverage decreased: 90.0% → 85.0%"]
        )
        
        assert not result.success
        assert result.has_failures()
        assert len(result.issues) == 1
        assert len(result.warnings) == 1


class TestCleanupTestHarness:
    """Test CleanupTestHarness class"""
    
    def test_harness_initialization(self, temp_workspace):
        """Test harness initialization"""
        harness = CleanupTestHarness(
            workspace_root=temp_workspace,
            test_command="pytest",
            coverage_command="pytest --cov"
        )
        
        assert harness.workspace_root == temp_workspace
        assert harness.test_command == "pytest"
        assert harness.coverage_command == "pytest --cov"
        assert harness.backup_dir.exists()
        assert harness.baseline is None
    
    @patch('subprocess.run')
    def test_capture_baseline_success(self, mock_run, mock_harness, temp_workspace):
        """Test successful baseline capture"""
        # Mock subprocess output
        mock_result = Mock()
        mock_result.stdout = "5 passed in 1.23s"
        mock_result.returncode = 0
        mock_run.return_value = mock_result
        
        # Mock coverage report
        coverage_data = {'totals': {'percent_covered': 85.5}}
        coverage_file = temp_workspace / "coverage.json"
        coverage_file.write_text(json.dumps(coverage_data))
        
        baseline = mock_harness.capture_baseline()
        
        assert baseline is not None
        assert baseline.passed_tests == 5
        assert baseline.total_tests == 5
        assert baseline.coverage_percent == 85.5
        assert mock_harness.baseline == baseline
    
    @patch('subprocess.run')
    def test_capture_baseline_with_failures(self, mock_run, mock_harness, temp_workspace):
        """Test baseline capture with failing tests"""
        mock_result = Mock()
        mock_result.stdout = "3 passed, 2 failed in 2.45s"
        mock_result.returncode = 1
        mock_run.return_value = mock_result
        
        coverage_data = {'totals': {'percent_covered': 80.0}}
        coverage_file = temp_workspace / "coverage.json"
        coverage_file.write_text(json.dumps(coverage_data))
        
        baseline = mock_harness.capture_baseline()
        
        assert baseline.passed_tests == 3
        assert baseline.failed_tests == 2
        assert baseline.total_tests == 5
    
    @patch('subprocess.run')
    def test_validate_category_success(self, mock_run, mock_harness, temp_workspace):
        """Test successful category validation"""
        # Set up baseline
        mock_result = Mock()
        mock_result.stdout = "5 passed in 1.23s"
        mock_result.returncode = 0
        mock_run.return_value = mock_result
        
        coverage_data = {'totals': {'percent_covered': 85.0}}
        (temp_workspace / "coverage.json").write_text(json.dumps(coverage_data))
        
        mock_harness.capture_baseline()
        
        # Validate category (same results)
        validation = mock_harness.validate_category("redundant")
        
        assert validation.success
        assert not validation.has_failures()
        assert len(validation.issues) == 0
    
    @patch('subprocess.run')
    def test_validate_category_with_failures(self, mock_run, mock_harness, temp_workspace):
        """Test category validation with test failures"""
        # Set up baseline (all passing)
        mock_result_baseline = Mock()
        mock_result_baseline.stdout = "5 passed in 1.23s"
        mock_result_baseline.returncode = 0
        
        coverage_data_baseline = {'totals': {'percent_covered': 85.0}}
        (temp_workspace / "coverage.json").write_text(json.dumps(coverage_data_baseline))
        
        mock_run.return_value = mock_result_baseline
        mock_harness.capture_baseline()
        
        # Now mock failed validation
        mock_result_validation = Mock()
        mock_result_validation.stdout = "3 passed, 2 failed in 1.45s"
        mock_result_validation.returncode = 1
        mock_run.return_value = mock_result_validation
        
        coverage_data_validation = {'totals': {'percent_covered': 80.0}}
        (temp_workspace / "coverage.json").write_text(json.dumps(coverage_data_validation))
        
        validation = mock_harness.validate_category("redundant")
        
        assert not validation.success
        assert validation.has_failures()
        assert len(validation.issues) > 0
        assert any("new failures" in issue.lower() for issue in validation.issues)
    
    def test_backup_files(self, mock_harness, temp_workspace):
        """Test file backup functionality"""
        # Create test files
        test_file1 = temp_workspace / "test1.txt"
        test_file2 = temp_workspace / "test2.txt"
        test_file1.write_text("content 1")
        test_file2.write_text("content 2")
        
        mock_harness.current_category = "test_category"
        
        backup_path = mock_harness.backup_files([test_file1, test_file2])
        
        assert backup_path.exists()
        assert (backup_path / "test1.txt").exists()
        assert (backup_path / "test2.txt").exists()
        assert (backup_path / "test1.txt").read_text() == "content 1"
    
    def test_rollback_category(self, mock_harness, temp_workspace):
        """Test category rollback functionality"""
        # Create and backup files
        test_file = temp_workspace / "test.txt"
        test_file.write_text("original content")
        
        mock_harness.current_category = "test_category"
        backup_path = mock_harness.backup_files([test_file])
        
        # Modify file
        test_file.write_text("modified content")
        
        # Rollback
        success = mock_harness.rollback_category(backup_path)
        
        assert success
        assert test_file.read_text() == "original content"
    
    @patch('subprocess.run')
    def test_generate_validation_report(self, mock_run, mock_harness, temp_workspace):
        """Test validation report generation"""
        # Set up baseline and validation
        mock_result = Mock()
        mock_result.stdout = "5 passed in 1.23s"
        mock_result.returncode = 0
        mock_run.return_value = mock_result
        
        coverage_data = {'totals': {'percent_covered': 85.0}}
        (temp_workspace / "coverage.json").write_text(json.dumps(coverage_data))
        
        mock_harness.capture_baseline()
        mock_harness.validate_category("test_category")
        
        report = mock_harness.generate_validation_report()
        
        assert "Cleanup Test Validation Report" in report
        assert "Baseline" in report
        assert "Validation History" in report
        assert "test_category" in report.lower() or "validation 1" in report.lower()
    
    def test_parse_pytest_output_simple(self, mock_harness):
        """Test parsing simple pytest output"""
        output = "5 passed in 1.23s"
        stats = mock_harness._parse_pytest_output(output)
        
        assert stats['passed'] == 5
        assert stats['total'] == 5
        assert stats['duration'] == 1.23
    
    def test_parse_pytest_output_with_failures(self, mock_harness):
        """Test parsing pytest output with failures"""
        output = "3 passed, 2 failed in 2.45s"
        stats = mock_harness._parse_pytest_output(output)
        
        assert stats['passed'] == 3
        assert stats['failed'] == 2
        assert stats['total'] == 5
        assert stats['duration'] == 2.45
    
    def test_parse_pytest_output_with_skipped(self, mock_harness):
        """Test parsing pytest output with skipped tests"""
        output = "10 passed, 3 skipped in 3.21s"
        stats = mock_harness._parse_pytest_output(output)
        
        assert stats['passed'] == 10
        assert stats['skipped'] == 3
        assert stats['total'] == 13
    
    def test_compare_with_baseline_success(self, mock_harness):
        """Test baseline comparison with successful validation"""
        baseline = TestBaseline(
            timestamp="2025-11-30T10:00:00",
            total_tests=10,
            passed_tests=10,
            failed_tests=0,
            skipped_tests=0,
            coverage_percent=90.0,
            test_duration=1.5
        )
        mock_harness.baseline = baseline
        
        current = TestBaseline(
            timestamp="2025-11-30T10:05:00",
            total_tests=10,
            passed_tests=10,
            failed_tests=0,
            skipped_tests=0,
            coverage_percent=90.5,
            test_duration=1.6
        )
        
        result = mock_harness._compare_with_baseline(current)
        
        assert result.success
        assert len(result.issues) == 0
    
    def test_compare_with_baseline_new_failures(self, mock_harness):
        """Test baseline comparison with new test failures"""
        baseline = TestBaseline(
            timestamp="2025-11-30T10:00:00",
            total_tests=10,
            passed_tests=10,
            failed_tests=0,
            skipped_tests=0,
            coverage_percent=90.0,
            test_duration=1.5
        )
        mock_harness.baseline = baseline
        
        current = TestBaseline(
            timestamp="2025-11-30T10:05:00",
            total_tests=10,
            passed_tests=8,
            failed_tests=2,
            skipped_tests=0,
            coverage_percent=88.0,
            test_duration=1.8
        )
        
        result = mock_harness._compare_with_baseline(current)
        
        assert not result.success
        assert len(result.issues) > 0
        assert any("new failures" in issue.lower() for issue in result.issues)
    
    def test_compare_with_baseline_test_loss(self, mock_harness):
        """Test baseline comparison with lost tests"""
        baseline = TestBaseline(
            timestamp="2025-11-30T10:00:00",
            total_tests=10,
            passed_tests=10,
            failed_tests=0,
            skipped_tests=0,
            coverage_percent=90.0,
            test_duration=1.5
        )
        mock_harness.baseline = baseline
        
        current = TestBaseline(
            timestamp="2025-11-30T10:05:00",
            total_tests=8,
            passed_tests=8,
            failed_tests=0,
            skipped_tests=0,
            coverage_percent=88.0,
            test_duration=1.2
        )
        
        result = mock_harness._compare_with_baseline(current)
        
        assert not result.success
        assert len(result.issues) > 0
        assert any("test count decreased" in issue.lower() for issue in result.issues)
    
    def test_compare_with_baseline_coverage_drop(self, mock_harness):
        """Test baseline comparison with significant coverage drop"""
        baseline = TestBaseline(
            timestamp="2025-11-30T10:00:00",
            total_tests=10,
            passed_tests=10,
            failed_tests=0,
            skipped_tests=0,
            coverage_percent=90.0,
            test_duration=1.5
        )
        mock_harness.baseline = baseline
        
        current = TestBaseline(
            timestamp="2025-11-30T10:05:00",
            total_tests=10,
            passed_tests=10,
            failed_tests=0,
            skipped_tests=0,
            coverage_percent=85.0,  # 5% drop
            test_duration=1.6
        )
        
        result = mock_harness._compare_with_baseline(current)
        
        assert result.success  # Still success (only warnings)
        assert len(result.warnings) > 0
        assert any("coverage decreased" in warning.lower() for warning in result.warnings)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
