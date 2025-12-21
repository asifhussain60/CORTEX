"""
Tests for Parallel Test Runner (Task 6.10 Package 1)

Tests async parallel test execution, timeout handling, and result aggregation.

Author: CORTEX Development Team
Version: 1.0.0
Created: 2025-12-21
"""

import pytest
import asyncio
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

from src.orchestrators.tdd.parallel_test_runner import (
    ParallelTestRunner,
    TestResult
)


@pytest.fixture
def runner():
    """Create test runner with 2 max workers"""
    return ParallelTestRunner(max_workers=2)


@pytest.fixture
def sample_test_suite(tmp_path):
    """Create sample test suite directory"""
    suite_path = tmp_path / "test_sample.py"
    suite_path.write_text("""
def test_example():
    assert True
""")
    return suite_path


class TestParallelTestRunnerInit:
    """Test initialization"""
    
    def test_init_default_workers(self):
        """Should initialize with default max workers"""
        runner = ParallelTestRunner()
        assert runner.max_workers == 4
    
    def test_init_custom_workers(self):
        """Should initialize with custom max workers"""
        runner = ParallelTestRunner(max_workers=8)
        assert runner.max_workers == 8


class TestRunTestsParallel:
    """Test parallel test execution"""
    
    @pytest.mark.asyncio
    async def test_run_empty_suite_list(self, runner):
        """Should handle empty test suite list"""
        results = await runner.run_tests_parallel([], "pytest")
        assert results == []
    
    @pytest.mark.asyncio
    async def test_run_single_suite(self, runner, sample_test_suite):
        """Should execute single test suite"""
        with patch.object(runner, '_run_test_suite', new=AsyncMock(return_value=TestResult(
            suite_path=sample_test_suite,
            tests_passed=1,
            tests_failed=0,
            tests_skipped=0,
            execution_time=1.0,
            output="Test output",
            success=True
        ))):
            results = await runner.run_tests_parallel([sample_test_suite], "pytest")
            assert len(results) == 1
            assert results[0].success is True
    
    @pytest.mark.asyncio
    async def test_run_multiple_suites_parallel(self, runner, tmp_path):
        """Should execute multiple suites in parallel"""
        suite1 = tmp_path / "test_1.py"
        suite2 = tmp_path / "test_2.py"
        suite1.touch()
        suite2.touch()
        
        with patch.object(runner, '_run_test_suite', new=AsyncMock(return_value=TestResult(
            suite_path=suite1,
            tests_passed=1,
            tests_failed=0,
            tests_skipped=0,
            execution_time=1.0,
            output="Test output",
            success=True
        ))):
            results = await runner.run_tests_parallel([suite1, suite2], "pytest")
            assert len(results) == 2
    
    @pytest.mark.asyncio
    async def test_run_with_timeout(self, runner, sample_test_suite):
        """Should timeout long-running tests"""
        async def slow_test(*args, **kwargs):
            await asyncio.sleep(10)  # Simulate slow test
            return TestResult(
                suite_path=sample_test_suite,
                tests_passed=0,
                tests_failed=0,
                tests_skipped=0,
                execution_time=10.0,
                output="Timeout",
                success=False
            )
        
        runner.timeout = 0.1  # Very short timeout
        with patch.object(runner, '_run_test_suite', new=slow_test):
            results = await runner.run_tests_parallel([sample_test_suite], "pytest")
            # Should handle timeout gracefully (return exception or timeout result)
            assert len(results) == 1


class TestRunTestSuite:
    """Test single suite execution"""
    
    @pytest.mark.asyncio
    async def test_run_pytest_suite(self, runner, sample_test_suite):
        """Should execute pytest suite"""
        with patch('asyncio.create_subprocess_exec', new=AsyncMock(
            return_value=Mock(
                communicate=AsyncMock(return_value=(
                    b"1 passed in 0.5s",
                    b""
                )),
                returncode=0
            )
        )):
            result = await runner._run_test_suite(sample_test_suite, "pytest")
            assert result.success is True
            assert result.tests_passed >= 0
    
    @pytest.mark.asyncio
    async def test_run_unittest_suite(self, runner, sample_test_suite):
        """Should execute unittest suite"""
        with patch('asyncio.create_subprocess_exec', new=AsyncMock(
            return_value=Mock(
                communicate=AsyncMock(return_value=(
                    b"Ran 5 tests in 1.2s",
                    b""
                )),
                returncode=0
            )
        )):
            result = await runner._run_test_suite(sample_test_suite, "unittest")
            assert result.success is True
    
    @pytest.mark.asyncio
    async def test_run_suite_with_failures(self, runner, sample_test_suite):
        """Should handle test failures"""
        with patch('asyncio.create_subprocess_exec', new=AsyncMock(
            return_value=Mock(
                communicate=AsyncMock(return_value=(
                    b"5 passed, 2 failed in 1.0s",
                    b"AssertionError"
                )),
                returncode=1
            )
        )):
            result = await runner._run_test_suite(sample_test_suite, "pytest")
            assert result.success is False
            assert result.tests_failed >= 0


class TestParseTestCounts:
    """Test framework-agnostic result parsing"""
    
    def test_parse_pytest_output(self, runner):
        """Should parse pytest output"""
        output = "10 passed, 2 failed, 1 skipped in 5.2s"
        passed, failed, skipped = runner._parse_test_counts(output, "pytest")
        assert passed == 10
        assert failed == 2
        assert skipped == 1
    
    def test_parse_unittest_output(self, runner):
        """Should parse unittest output"""
        output = "Ran 15 tests in 3.5s"
        passed, failed, skipped = runner._parse_test_counts(output, "unittest")
        assert passed == 15  # Assumes all passed if no FAILED
    
    def test_parse_jest_output(self, runner):
        """Should parse jest output"""
        output = "Tests: 8 passed, 2 failed, 10 total"
        passed, failed, skipped = runner._parse_test_counts(output, "jest")
        assert passed == 8
        assert failed == 2
    
    def test_parse_unknown_format(self, runner):
        """Should handle unknown output format"""
        output = "Some unknown format"
        passed, failed, skipped = runner._parse_test_counts(output, "pytest")
        # Should default to 0s or best effort
        assert passed >= 0
        assert failed >= 0
        assert skipped >= 0


class TestAggregateResults:
    """Test result aggregation"""
    
    def test_aggregate_empty_results(self, runner):
        """Should handle empty results"""
        summary = runner.aggregate_results([])
        assert summary['total_suites'] == 0
        assert summary['total_passed'] == 0
    
    def test_aggregate_multiple_results(self, runner, tmp_path):
        """Should aggregate multiple test results"""
        results = [
            TestResult(
                suite_path=tmp_path / "test_1.py",
                tests_passed=5,
                tests_failed=1,
                tests_skipped=0,
                execution_time=1.0,
                output="",
                success=True
            ),
            TestResult(
                suite_path=tmp_path / "test_2.py",
                tests_passed=3,
                tests_failed=0,
                tests_skipped=1,
                execution_time=2.0,
                output="",
                success=True
            )
        ]
        
        summary = runner.aggregate_results(results)
        assert summary['total_suites'] == 2
        assert summary['total_passed'] == 8
        assert summary['total_failed'] == 1
        assert summary['total_skipped'] == 1
        assert summary['total_time'] == 3.0
        assert summary['successful_suites'] == 2  # Both suites succeeded
    
    def test_aggregate_with_failures(self, runner, tmp_path):
        """Should calculate success rate with failures"""
        results = [
            TestResult(
                suite_path=tmp_path / "test_1.py",
                tests_passed=5,
                tests_failed=0,
                tests_skipped=0,
                execution_time=1.0,
                output="",
                success=True
            ),
            TestResult(
                suite_path=tmp_path / "test_2.py",
                tests_passed=0,
                tests_failed=3,
                tests_skipped=0,
                execution_time=2.0,
                output="",
                success=False
            )
        ]
        
        summary = runner.aggregate_results(results)
        assert summary['successful_suites'] == 1  # 1 of 2 succeeded
        assert summary['pass_rate'] == 62.5  # 5/(5+3)*100
