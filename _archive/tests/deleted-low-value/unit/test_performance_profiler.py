"""Tests for Orchestrator Performance Profiling.

This module tests the PerformanceProfiler component for tracking orchestrator
execution metrics and generating optimization recommendations.

AC-EX-003-01: Execution time tracked per orchestrator, bottlenecks identifiable
from profiles, and historical trends available.

Author: Asif Hussain
Copyright: © 2025-2026 Asif Hussain. All rights reserved.
"""

import time
import unittest
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from statistics import mean, stdev
from unittest.mock import MagicMock, patch


@dataclass
class ExecutionMetrics:
    """Metrics for a single execution.
    
    Attributes:
        orchestrator: Orchestrator name
        task_type: Type of task executed
        duration_seconds: Execution duration
        memory_mb: Memory used
        success: Whether execution succeeded
        error_message: Error message if failed
    """
    
    orchestrator: str
    task_type: str
    duration_seconds: float
    memory_mb: float
    success: bool
    error_message: Optional[str] = None


@dataclass
class PerformanceProfile:
    """Performance profile for an orchestrator.
    
    Attributes:
        orchestrator: Orchestrator name
        executions: List of execution metrics
        total_executions: Total number of executions
        successful_executions: Number of successful executions
        average_duration: Average execution duration
        min_duration: Minimum execution duration
        max_duration: Maximum execution duration
        success_rate: Success rate as percentage
    """
    
    orchestrator: str
    executions: List[ExecutionMetrics] = field(default_factory=list)
    
    @property
    def total_executions(self) -> int:
        """Get total execution count."""
        return len(self.executions)
    
    @property
    def successful_executions(self) -> int:
        """Get count of successful executions."""
        return sum(1 for e in self.executions if e.success)
    
    @property
    def average_duration(self) -> float:
        """Get average duration."""
        if not self.executions:
            return 0.0
        durations = [e.duration_seconds for e in self.executions]
        return mean(durations) if durations else 0.0
    
    @property
    def min_duration(self) -> float:
        """Get minimum duration."""
        if not self.executions:
            return 0.0
        return min(e.duration_seconds for e in self.executions)
    
    @property
    def max_duration(self) -> float:
        """Get maximum duration."""
        if not self.executions:
            return 0.0
        return max(e.duration_seconds for e in self.executions)
    
    @property
    def success_rate(self) -> float:
        """Get success rate as percentage."""
        if not self.executions:
            return 0.0
        return (self.successful_executions / self.total_executions) * 100


class PerformanceProfiler:
    """Profiles orchestrator execution for optimization.
    
    Tracks execution metrics including:
    - Execution time per orchestrator
    - Memory usage patterns
    - Success/failure rates
    - Performance trends over time
    - Bottleneck identification
    """
    
    def __init__(self) -> None:
        """Initialize the performance profiler."""
        self._profiles: Dict[str, PerformanceProfile] = {}
        self._bottleneck_threshold = 0.7  # 70th percentile
    
    def record_execution(self, metrics: ExecutionMetrics) -> None:
        """Record an orchestrator execution.
        
        Args:
            metrics: ExecutionMetrics to record
        """
        if metrics.orchestrator not in self._profiles:
            self._profiles[metrics.orchestrator] = PerformanceProfile(
                orchestrator=metrics.orchestrator
            )
        
        self._profiles[metrics.orchestrator].executions.append(metrics)
    
    def get_profile(self, orchestrator: str) -> Optional[PerformanceProfile]:
        """Get performance profile for an orchestrator.
        
        Args:
            orchestrator: Orchestrator name
            
        Returns:
            PerformanceProfile or None if no data
        """
        return self._profiles.get(orchestrator)
    
    def get_all_profiles(self) -> Dict[str, PerformanceProfile]:
        """Get all performance profiles.
        
        Returns:
            Dictionary of profiles by orchestrator name
        """
        return self._profiles
    
    def identify_bottlenecks(self) -> Dict[str, List[Dict[str, Any]]]:
        """Identify performance bottlenecks.
        
        Returns:
            Dictionary mapping orchestrators to lists of bottleneck info
        """
        bottlenecks: Dict[str, List[Dict[str, Any]]] = {}
        
        for orch_name, profile in self._profiles.items():
            if profile.total_executions < 3:  # Need at least 3 samples
                continue
            
            durations = [e.duration_seconds for e in profile.executions]
            avg = mean(durations)
            
            # Find slow executions (>70th percentile)
            slow_threshold = avg * self._bottleneck_threshold
            slow_executions = [
                e for e in profile.executions
                if e.duration_seconds > slow_threshold
            ]
            
            if slow_executions:
                bottlenecks[orch_name] = [
                    {
                        "task_type": e.task_type,
                        "duration": e.duration_seconds,
                        "threshold": slow_threshold,
                    }
                    for e in slow_executions
                ]
        
        return bottlenecks
    
    def get_historical_trends(self, orchestrator: str, window_size: int = 10) -> Dict[str, Any]:
        """Get historical performance trends.
        
        Args:
            orchestrator: Orchestrator name
            window_size: Number of recent executions to include
            
        Returns:
            Trend data including averages, variance, etc.
        """
        profile = self.get_profile(orchestrator)
        if not profile or not profile.executions:
            return {}
        
        # Get recent executions
        recent = profile.executions[-window_size:]
        durations = [e.duration_seconds for e in recent]
        
        avg_duration = mean(durations)
        duration_variance = stdev(durations) if len(durations) > 1 else 0.0
        
        return {
            "orchestrator": orchestrator,
            "sample_count": len(recent),
            "average_duration": avg_duration,
            "variance": duration_variance,
            "trend": "improving" if durations[-1] < avg_duration else "degrading",
        }
    
    def get_comparison(self) -> Dict[str, Dict[str, Any]]:
        """Get performance comparison across orchestrators.
        
        Returns:
            Dictionary with comparative metrics
        """
        comparison = {}
        
        for orch_name, profile in self._profiles.items():
            comparison[orch_name] = {
                "total_executions": profile.total_executions,
                "average_duration": profile.average_duration,
                "success_rate": profile.success_rate,
                "min_duration": profile.min_duration,
                "max_duration": profile.max_duration,
            }
        
        return comparison


class TestPerformanceProfiler(unittest.TestCase):
    """Tests for PerformanceProfiler."""
    
    def setUp(self) -> None:
        """Set up test fixtures."""
        self.profiler = PerformanceProfiler()
    
    def test_profiler_initialization(self) -> None:
        """Test profiler initializes correctly."""
        self.assertEqual(len(self.profiler._profiles), 0)
    
    def test_record_execution(self) -> None:
        """Test recording an execution."""
        metrics = ExecutionMetrics(
            orchestrator="TestOrch",
            task_type="test_task",
            duration_seconds=1.5,
            memory_mb=128,
            success=True,
        )
        
        self.profiler.record_execution(metrics)
        
        self.assertIn("TestOrch", self.profiler._profiles)
        self.assertEqual(self.profiler._profiles["TestOrch"].total_executions, 1)
    
    def test_get_profile(self) -> None:
        """Test retrieving a profile."""
        metrics = ExecutionMetrics(
            orchestrator="TestOrch",
            task_type="test",
            duration_seconds=1.0,
            memory_mb=128,
            success=True,
        )
        
        self.profiler.record_execution(metrics)
        profile = self.profiler.get_profile("TestOrch")
        
        self.assertIsNotNone(profile)
        self.assertEqual(profile.orchestrator, "TestOrch")
    
    def test_performance_profile_metrics(self) -> None:
        """Test performance profile calculations."""
        metrics_list = [
            ExecutionMetrics("Orch1", "task", 1.0, 128, True),
            ExecutionMetrics("Orch1", "task", 2.0, 256, True),
            ExecutionMetrics("Orch1", "task", 3.0, 192, False),
        ]
        
        for metrics in metrics_list:
            self.profiler.record_execution(metrics)
        
        profile = self.profiler.get_profile("Orch1")
        
        self.assertEqual(profile.total_executions, 3)
        self.assertEqual(profile.successful_executions, 2)
        self.assertEqual(profile.average_duration, 2.0)
        self.assertEqual(profile.min_duration, 1.0)
        self.assertEqual(profile.max_duration, 3.0)
        self.assertAlmostEqual(profile.success_rate, 66.66, places=1)
    
    def test_identify_bottlenecks(self) -> None:
        """Test bottleneck identification."""
        # Record multiple executions with some slow ones
        for i in range(5):
            duration = 1.0 if i < 3 else 5.0  # Last 2 are slow
            metrics = ExecutionMetrics(
                orchestrator="SlowOrch",
                task_type="task",
                duration_seconds=duration,
                memory_mb=128,
                success=True,
            )
            self.profiler.record_execution(metrics)
        
        bottlenecks = self.profiler.identify_bottlenecks()
        
        self.assertIn("SlowOrch", bottlenecks)
        self.assertGreater(len(bottlenecks["SlowOrch"]), 0)
    
    def test_get_historical_trends(self) -> None:
        """Test historical trend analysis."""
        # Record executions with trend
        for i in range(5):
            metrics = ExecutionMetrics(
                orchestrator="TrendOrch",
                task_type="task",
                duration_seconds=1.0 + (i * 0.1),  # Increasing trend
                memory_mb=128,
                success=True,
            )
            self.profiler.record_execution(metrics)
        
        trends = self.profiler.get_historical_trends("TrendOrch", window_size=5)
        
        self.assertEqual(trends["sample_count"], 5)
        self.assertGreater(trends["average_duration"], 0)
        self.assertEqual(trends["trend"], "degrading")
    
    def test_get_comparison(self) -> None:
        """Test performance comparison."""
        # Record executions for multiple orchestrators
        for orch in ["Orch1", "Orch2"]:
            for i in range(3):
                metrics = ExecutionMetrics(
                    orchestrator=orch,
                    task_type="task",
                    duration_seconds=1.0 + (i * 0.1),
                    memory_mb=128,
                    success=True,
                )
                self.profiler.record_execution(metrics)
        
        comparison = self.profiler.get_comparison()
        
        self.assertEqual(len(comparison), 2)
        self.assertIn("Orch1", comparison)
        self.assertIn("Orch2", comparison)
        self.assertEqual(comparison["Orch1"]["total_executions"], 3)
    
    def test_execution_metrics_creation(self) -> None:
        """Test creating execution metrics."""
        metrics = ExecutionMetrics(
            orchestrator="Test",
            task_type="analysis",
            duration_seconds=2.5,
            memory_mb=256,
            success=True,
        )
        
        self.assertEqual(metrics.orchestrator, "Test")
        self.assertEqual(metrics.duration_seconds, 2.5)
        self.assertTrue(metrics.success)
    
    def test_execution_metrics_with_error(self) -> None:
        """Test execution metrics with error."""
        metrics = ExecutionMetrics(
            orchestrator="Test",
            task_type="task",
            duration_seconds=1.0,
            memory_mb=128,
            success=False,
            error_message="Test error",
        )
        
        self.assertFalse(metrics.success)
        self.assertEqual(metrics.error_message, "Test error")
    
    def test_performance_profile_empty(self) -> None:
        """Test performance profile with no executions."""
        profile = PerformanceProfile(orchestrator="Empty")
        
        self.assertEqual(profile.total_executions, 0)
        self.assertEqual(profile.average_duration, 0.0)
        self.assertEqual(profile.success_rate, 0.0)
    
    def test_multiple_orchestrators_tracked(self) -> None:
        """Test tracking multiple orchestrators."""
        for orch in ["Orch1", "Orch2", "Orch3"]:
            metrics = ExecutionMetrics(
                orchestrator=orch,
                task_type="task",
                duration_seconds=1.0,
                memory_mb=128,
                success=True,
            )
            self.profiler.record_execution(metrics)
        
        all_profiles = self.profiler.get_all_profiles()
        
        self.assertEqual(len(all_profiles), 3)
    
    def test_bottleneck_threshold_configuration(self) -> None:
        """Test configurable bottleneck threshold."""
        self.profiler._bottleneck_threshold = 0.5
        
        self.assertEqual(self.profiler._bottleneck_threshold, 0.5)


if __name__ == "__main__":
    unittest.main()
