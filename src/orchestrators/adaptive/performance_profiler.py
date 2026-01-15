"""Orchestrator Performance Profiling Module.

This module implements performance profiling for orchestrator execution tracking,
bottleneck identification, and trend analysis.

AC-EX-003-01: Execution time tracked per orchestrator, bottlenecks identifiable
from profiles, and historical trends available.

Author: Asif Hussain
Copyright: © 2025-2026 Asif Hussain. All rights reserved.
"""

from dataclasses import dataclass, field
from statistics import mean, stdev
from typing import Any, Dict, List, Optional


@dataclass
class ExecutionMetrics:
    """Metrics for a single orchestrator execution.
    
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
    
    Properties:
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
        """Get average execution duration."""
        if not self.executions:
            return 0.0
        durations = [e.duration_seconds for e in self.executions]
        return mean(durations) if durations else 0.0
    
    @property
    def min_duration(self) -> float:
        """Get minimum execution duration."""
        if not self.executions:
            return 0.0
        return min(e.duration_seconds for e in self.executions)
    
    @property
    def max_duration(self) -> float:
        """Get maximum execution duration."""
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
    
    Example:
        >>> profiler = PerformanceProfiler()
        >>> metrics = ExecutionMetrics("Orch1", "task", 1.5, 128, True)
        >>> profiler.record_execution(metrics)
        >>> profile = profiler.get_profile("Orch1")
        >>> bottlenecks = profiler.identify_bottlenecks()
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
        """Identify performance bottlenecks across orchestrators.
        
        Identifies slow executions (above the bottleneck threshold) for each
        orchestrator with sufficient execution history.
        
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
        """Get historical performance trends for an orchestrator.
        
        Analyzes recent execution performance to identify trends such as
        improving or degrading performance.
        
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
            Dictionary with comparative metrics for each orchestrator
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
