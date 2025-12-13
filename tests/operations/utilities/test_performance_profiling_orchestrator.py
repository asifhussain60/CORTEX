"""
Tests for Performance Profiling Orchestrator.

Tests execution profiling, bottleneck detection, and regression analysis.
"""

import pytest
import time
from pathlib import Path
from typing import Dict, Any, List
from src.operations.utilities.performance_profiling_orchestrator import (
    PerformanceProfilingOrchestrator,
    ProfileResult,
    BottleneckReport,
    RegressionReport
)


@pytest.fixture
def orchestrator():
    """Create orchestrator instance."""
    return PerformanceProfilingOrchestrator()


@pytest.fixture
def sample_function():
    """Sample function for profiling."""
    def slow_function():
        total = 0
        for i in range(1000):
            total += i
        time.sleep(0.01)
        return total
    return slow_function


@pytest.fixture
def fast_function():
    """Fast function for comparison."""
    def quick_function():
        return sum(range(100))
    return quick_function


class TestExecutionProfiling:
    """Test execution profiling capabilities."""

    def test_profile_execution_basic(self, orchestrator, sample_function):
        """Test basic execution profiling."""
        result = orchestrator.profile_execution(sample_function)
        
        assert isinstance(result, ProfileResult)
        assert result.execution_time > 0
        assert result.function_name == "slow_function"
        assert result.call_count > 0

    def test_profile_execution_with_args(self, orchestrator):
        """Test profiling with function arguments."""
        def func_with_args(x, y):
            return x + y
        
        result = orchestrator.profile_execution(func_with_args, args=(5, 3))
        
        assert result.return_value == 8
        assert result.execution_time > 0

    def test_profile_execution_multiple_runs(self, orchestrator, fast_function):
        """Test profiling with multiple runs for averaging."""
        result = orchestrator.profile_execution(
            fast_function, 
            runs=10
        )
        
        assert result.avg_execution_time > 0
        assert result.min_execution_time > 0
        assert result.max_execution_time > 0
        assert result.runs == 10


class TestBottleneckDetection:
    """Test bottleneck identification."""

    def test_identify_bottlenecks_basic(self, orchestrator):
        """Test basic bottleneck detection."""
        profile_data = {
            'function_a': {'time': 0.5, 'calls': 10},
            'function_b': {'time': 0.1, 'calls': 5},
            'function_c': {'time': 1.2, 'calls': 3}
        }
        
        bottlenecks = orchestrator.identify_bottlenecks(profile_data)
        
        assert isinstance(bottlenecks, BottleneckReport)
        assert len(bottlenecks.hotspots) > 0
        assert bottlenecks.hotspots[0]['function'] == 'function_c'

    def test_identify_bottlenecks_with_threshold(self, orchestrator):
        """Test bottleneck detection with time threshold."""
        profile_data = {
            'fast_func': {'time': 0.01, 'calls': 100},
            'slow_func': {'time': 0.5, 'calls': 10}
        }
        
        bottlenecks = orchestrator.identify_bottlenecks(
            profile_data, 
            threshold=0.1
        )
        
        assert len(bottlenecks.hotspots) == 1
        assert bottlenecks.hotspots[0]['function'] == 'slow_func'

    def test_identify_bottlenecks_recommendations(self, orchestrator):
        """Test bottleneck detection includes recommendations."""
        profile_data = {
            'recursive_func': {'time': 1.0, 'calls': 1000},
            'io_func': {'time': 0.8, 'calls': 5}
        }
        
        bottlenecks = orchestrator.identify_bottlenecks(profile_data)
        
        assert len(bottlenecks.recommendations) > 0
        assert any('optimize' in r.lower() for r in bottlenecks.recommendations)


class TestRegressionDetection:
    """Test performance regression analysis."""

    def test_detect_regression_no_regression(self, orchestrator):
        """Test no regression detected when performance improves."""
        baseline = {'function_a': 0.5, 'function_b': 0.3}
        current = {'function_a': 0.4, 'function_b': 0.25}
        
        regression = orchestrator.detect_regression(baseline, current)
        
        assert isinstance(regression, RegressionReport)
        assert not regression.has_regression

    def test_detect_regression_with_regression(self, orchestrator):
        """Test regression detection when performance degrades."""
        baseline = {'function_a': 0.5, 'function_b': 0.3}
        current = {'function_a': 0.8, 'function_b': 0.35}
        
        regression = orchestrator.detect_regression(baseline, current)
        
        assert regression.has_regression
        assert len(regression.degraded_functions) > 0
        assert 'function_a' in regression.degraded_functions

    def test_detect_regression_threshold(self, orchestrator):
        """Test regression detection with custom threshold."""
        baseline = {'function_a': 1.0}
        current = {'function_a': 1.05}  # 5% slower
        
        # Should not trigger with 10% threshold
        regression = orchestrator.detect_regression(
            baseline, 
            current, 
            threshold=0.10
        )
        assert not regression.has_regression
        
        # Should trigger with 3% threshold
        regression = orchestrator.detect_regression(
            baseline, 
            current, 
            threshold=0.03
        )
        assert regression.has_regression

    def test_detect_regression_report_details(self, orchestrator):
        """Test regression report includes detailed metrics."""
        baseline = {'function_a': 0.5, 'function_b': 0.3}
        current = {'function_a': 0.8, 'function_b': 0.25}
        
        regression = orchestrator.detect_regression(baseline, current)
        
        assert hasattr(regression, 'percentage_change')
        assert 'function_a' in regression.percentage_change
        assert regression.percentage_change['function_a'] > 0


class TestIntegration:
    """Test integrated profiling workflows."""

    def test_full_profiling_workflow(self, orchestrator, sample_function):
        """Test complete profiling workflow."""
        # Profile execution
        result = orchestrator.profile_execution(sample_function, runs=5)
        
        # Generate profile data
        profile_data = orchestrator.generate_profile_data(result)
        
        # Identify bottlenecks
        bottlenecks = orchestrator.identify_bottlenecks(profile_data)
        
        assert result.avg_execution_time > 0
        assert len(bottlenecks.hotspots) >= 0
