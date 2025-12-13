"""
Performance Profiling Orchestrator.

Provides execution profiling, bottleneck detection, and regression analysis.
"""

import cProfile
import io
import pstats
import time
from dataclasses import dataclass, field
from typing import Callable, Dict, Any, List, Optional, Tuple
from functools import wraps


@dataclass
class ProfileResult:
    """Result of a profiling execution."""
    function_name: str
    execution_time: float
    call_count: int
    return_value: Any = None
    runs: int = 1
    avg_execution_time: float = 0.0
    min_execution_time: float = 0.0
    max_execution_time: float = 0.0
    
    def __post_init__(self):
        """Calculate averages after initialization."""
        if self.runs == 1:
            self.avg_execution_time = self.execution_time
            self.min_execution_time = self.execution_time
            self.max_execution_time = self.execution_time


@dataclass
class BottleneckReport:
    """Report of identified performance bottlenecks."""
    hotspots: List[Dict[str, Any]] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    total_time: float = 0.0


@dataclass
class RegressionReport:
    """Report of performance regression analysis."""
    has_regression: bool = False
    degraded_functions: List[str] = field(default_factory=list)
    percentage_change: Dict[str, float] = field(default_factory=dict)
    threshold: float = 0.10


class PerformanceProfilingOrchestrator:
    """
    Orchestrator for performance profiling and analysis.
    
    Features:
    - Execution profiling with cProfile
    - Bottleneck identification
    - Regression detection
    - Performance comparison
    """
    
    def __init__(self):
        """Initialize the orchestrator."""
        self.profiler = None
        self.profile_history: Dict[str, List[float]] = {}
    
    def profile_execution(
        self, 
        func: Callable, 
        args: Tuple = (), 
        kwargs: Optional[Dict] = None,
        runs: int = 1
    ) -> ProfileResult:
        """
        Profile function execution.
        
        Args:
            func: Function to profile
            args: Positional arguments
            kwargs: Keyword arguments
            runs: Number of runs for averaging
            
        Returns:
            ProfileResult with timing data
        """
        if kwargs is None:
            kwargs = {}
        
        execution_times = []
        return_value = None
        
        for _ in range(runs):
            start_time = time.perf_counter()
            return_value = func(*args, **kwargs)
            end_time = time.perf_counter()
            execution_times.append(end_time - start_time)
        
        total_time = sum(execution_times)
        
        result = ProfileResult(
            function_name=func.__name__,
            execution_time=total_time,
            call_count=runs,
            return_value=return_value,
            runs=runs,
            avg_execution_time=total_time / runs,
            min_execution_time=min(execution_times),
            max_execution_time=max(execution_times)
        )
        
        # Store in history
        if func.__name__ not in self.profile_history:
            self.profile_history[func.__name__] = []
        self.profile_history[func.__name__].extend(execution_times)
        
        return result
    
    def generate_profile_data(self, result: ProfileResult) -> Dict[str, Dict[str, Any]]:
        """
        Generate profile data dictionary from ProfileResult.
        
        Args:
            result: ProfileResult instance
            
        Returns:
            Dictionary with profile data
        """
        return {
            result.function_name: {
                'time': result.avg_execution_time,
                'calls': result.call_count
            }
        }
    
    def identify_bottlenecks(
        self, 
        profile_data: Dict[str, Dict[str, Any]], 
        threshold: float = 0.0
    ) -> BottleneckReport:
        """
        Identify performance bottlenecks.
        
        Args:
            profile_data: Dictionary of function profiling data
            threshold: Minimum time threshold for bottlenecks
            
        Returns:
            BottleneckReport with hotspots and recommendations
        """
        hotspots = []
        total_time = 0.0
        
        # Collect and sort by time
        for func_name, data in profile_data.items():
            func_time = data.get('time', 0.0)
            calls = data.get('calls', 0)
            
            if func_time >= threshold:
                hotspots.append({
                    'function': func_name,
                    'time': func_time,
                    'calls': calls,
                    'time_per_call': func_time / calls if calls > 0 else 0.0
                })
                total_time += func_time
        
        # Sort by total time descending
        hotspots.sort(key=lambda x: x['time'], reverse=True)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(hotspots)
        
        return BottleneckReport(
            hotspots=hotspots,
            recommendations=recommendations,
            total_time=total_time
        )
    
    def _generate_recommendations(self, hotspots: List[Dict[str, Any]]) -> List[str]:
        """
        Generate optimization recommendations based on hotspots.
        
        Args:
            hotspots: List of hotspot dictionaries
            
        Returns:
            List of recommendation strings
        """
        recommendations = []
        
        if not hotspots:
            return recommendations
        
        for hotspot in hotspots[:3]:  # Top 3 hotspots
            func_name = hotspot['function']
            calls = hotspot['calls']
            func_time = hotspot['time']
            
            if calls > 100:
                recommendations.append(
                    f"Optimize '{func_name}' - called {calls} times"
                )
            elif func_time > 0.5:
                recommendations.append(
                    f"Optimize '{func_name}' - takes {func_time:.3f}s"
                )
            else:
                recommendations.append(
                    f"Consider optimizing '{func_name}' for better performance"
                )
        
        if hotspots:
            recommendations.append(
                "Review top functions for caching opportunities or algorithmic improvements"
            )
        
        return recommendations
    
    def detect_regression(
        self, 
        baseline: Dict[str, float], 
        current: Dict[str, float],
        threshold: float = 0.10
    ) -> RegressionReport:
        """
        Detect performance regressions.
        
        Args:
            baseline: Baseline performance metrics (function -> time)
            current: Current performance metrics (function -> time)
            threshold: Regression threshold (0.10 = 10% slower)
            
        Returns:
            RegressionReport with regression details
        """
        degraded_functions = []
        percentage_change = {}
        
        for func_name in baseline.keys():
            if func_name in current:
                baseline_time = baseline[func_name]
                current_time = current[func_name]
                
                if baseline_time > 0:
                    change = (current_time - baseline_time) / baseline_time
                    percentage_change[func_name] = change
                    
                    if change > threshold:
                        degraded_functions.append(func_name)
        
        return RegressionReport(
            has_regression=len(degraded_functions) > 0,
            degraded_functions=degraded_functions,
            percentage_change=percentage_change,
            threshold=threshold
        )
