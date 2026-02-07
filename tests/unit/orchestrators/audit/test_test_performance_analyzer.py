"""
Tests for TestPerformanceAnalyzer - P1-028 AUDIT check.

AC_START: AC-ENH053-003
Description: TDD for test suite performance analysis
Author: Asif Hussain
Date: 2026-02-07
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch
from cortex.orchestrators.audit.test_performance_analyzer import (
    TestPerformanceAnalyzer,
    TestPerformanceResult,
    SlowTest,
)


class TestTestPerformanceAnalyzer:
    """Test suite performance regression detection."""

    @pytest.fixture
    def analyzer(self):
        """Create TestPerformanceAnalyzer instance."""
        return TestPerformanceAnalyzer()

    @pytest.fixture
    def sample_repo_path(self, tmp_path):
        """Create sample repository."""
        repo_path = tmp_path / "sample_repo"
        repo_path.mkdir()
        (repo_path / "tests").mkdir()
        return repo_path

    def test_analyzer_initialization(self, analyzer):
        """Test analyzer initializes correctly."""
        assert analyzer is not None
        assert hasattr(analyzer, "analyze")

    @patch("subprocess.run")
    def test_run_pytest_with_durations(self, mock_run, analyzer, sample_repo_path):
        """Test running pytest with --durations flag."""
        mock_run.return_value = Mock(
            stdout=(
                "===== slowest 10 durations =====\n"
                "12.34s call     tests/test_slow.py::test_one\n"
                "5.67s call      tests/test_slow.py::test_two\n"
                "===== 100 passed in 120.45s =====\n"
            ),
            returncode=0,
        )
        
        result = analyzer.analyze(sample_repo_path)
        
        assert result.total_time == 120.45
        assert len(result.slow_tests) == 1  # Only one test above 10s threshold
        assert result.slow_tests[0].duration == 12.34

    @patch("subprocess.run")
    def test_parse_total_time(self, mock_run, analyzer):
        """Test parsing total execution time from pytest output."""
        output = "===== 1483 passed in 145.67s ====="
        
        total_time = analyzer._parse_total_time(output)
        
        assert total_time == 145.67

    @patch("subprocess.run")
    def test_parse_slow_tests(self, mock_run, analyzer):
        """Test parsing slow tests from pytest --durations output."""
        output = (
            "===== slowest 10 durations =====\n"
            "15.23s call     tests/integration/test_api.py::test_endpoint\n"
            "8.45s call      tests/unit/test_heavy.py::test_computation\n"
            "2.11s call      tests/unit/test_fast.py::test_quick\n"
        )
        
        slow_tests = analyzer._parse_slow_tests(output, threshold=5.0)
        
        assert len(slow_tests) == 2
        assert slow_tests[0].test_name == "tests/integration/test_api.py::test_endpoint"
        assert slow_tests[0].duration == 15.23
        assert slow_tests[1].duration == 8.45

    def test_load_baseline(self, analyzer, sample_repo_path):
        """Test loading performance baseline."""
        baseline_dir = sample_repo_path / ".cortex" / "metrics"
        baseline_dir.mkdir(parents=True)
        baseline_file = baseline_dir / "test_performance_baseline.json"
        baseline_file.write_text('{"total_time": 100.0, "slow_tests": []}')
        
        baseline = analyzer._load_baseline(sample_repo_path)
        
        assert baseline is not None
        assert baseline["total_time"] == 100.0

    def test_load_baseline_missing(self, analyzer, sample_repo_path):
        """Test loading baseline when file doesn't exist."""
        baseline = analyzer._load_baseline(sample_repo_path)
        assert baseline is None

    def test_save_baseline(self, analyzer, sample_repo_path):
        """Test saving performance baseline."""
        result = TestPerformanceResult(
            total_time=120.5,
            slow_tests=[SlowTest("tests/test_slow.py::test_one", 12.34)],
            regression_percent=0.0,
            severity="P2",
        )
        
        analyzer._save_baseline(sample_repo_path, result)
        
        baseline_file = sample_repo_path / ".cortex" / "metrics" / "test_performance_baseline.json"
        assert baseline_file.exists()

    @patch("subprocess.run")
    def test_analyze_no_regression(self, mock_run, analyzer, sample_repo_path):
        """Test analysis with no performance regression."""
        # Setup baseline
        baseline_dir = sample_repo_path / ".cortex" / "metrics"
        baseline_dir.mkdir(parents=True)
        baseline_file = baseline_dir / "test_performance_baseline.json"
        baseline_file.write_text('{"total_time": 100.0, "slow_tests": []}')
        
        mock_run.return_value = Mock(
            stdout="===== 100 passed in 95.5s =====\n",
            returncode=0,
        )
        
        result = analyzer.analyze(sample_repo_path)
        
        assert result.total_time == 95.5
        assert result.regression_percent < 0  # Improvement
        assert result.severity == "P2"

    @patch("subprocess.run")
    def test_analyze_with_regression(self, mock_run, analyzer, sample_repo_path):
        """Test analysis with performance regression detected."""
        # Setup baseline
        baseline_dir = sample_repo_path / ".cortex" / "metrics"
        baseline_dir.mkdir(parents=True)
        baseline_file = baseline_dir / "test_performance_baseline.json"
        baseline_file.write_text('{"total_time": 100.0, "slow_tests": []}')
        
        mock_run.return_value = Mock(
            stdout=(
                "===== slowest 10 durations =====\n"
                "125.67s call    tests/test_very_slow.py::test_timeout\n"
                "===== 100 passed in 250.0s =====\n"
            ),
            returncode=0,
        )
        
        result = analyzer.analyze(sample_repo_path)
        
        assert result.total_time == 250.0
        assert result.regression_percent == 150.0  # 150% increase
        assert result.severity == "P1"  # 250s is >120s but <300s

    @patch("subprocess.run")
    def test_pytest_timeout_handling(self, mock_run, analyzer, sample_repo_path):
        """Test handling pytest timeout."""
        mock_run.side_effect = Exception("Command timed out")
        
        result = analyzer.analyze(sample_repo_path)
        
        assert result.total_time == 0.0
        assert result.severity == "P0"
        assert len(result.slow_tests) == 0


class TestTestPerformanceResult:
    """Test TestPerformanceResult model."""

    def test_result_initialization(self):
        """Test result model initialization."""
        result = TestPerformanceResult(
            total_time=120.5,
            slow_tests=[SlowTest("tests/test_slow.py::test_one", 12.34)],
            regression_percent=20.0,
            severity="P1",
        )
        
        assert result.total_time == 120.5
        assert len(result.slow_tests) == 1
        assert result.regression_percent == 20.0
        assert result.severity == "P1"

    def test_to_dict(self):
        """Test converting result to dictionary."""
        result = TestPerformanceResult(
            total_time=120.5,
            slow_tests=[SlowTest("tests/test_slow.py::test_one", 12.34)],
            regression_percent=20.0,
            severity="P1",
        )
        
        data = result.to_dict()
        
        assert data["total_time"] == 120.5
        assert len(data["slow_tests"]) == 1
        assert data["slow_tests"][0]["test_name"] == "tests/test_slow.py::test_one"
        assert data["regression_percent"] == 20.0


# AC_COMPLETE: AC-ENH053-003 ✅ 10/10 tests defined (RED phase)
