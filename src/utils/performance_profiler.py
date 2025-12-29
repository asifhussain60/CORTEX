"""
CORTEX Performance Profiler

Profile startup time, identify slow initialization paths, and measure performance.
Part of Phase 3 optimization using proven patterns from Phase 0.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import time
import functools
from typing import Dict, List, Callable, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class ProfilerEntry:
    """Single profiler measurement entry."""
    name: str
    duration_ms: float
    timestamp: datetime
    parent: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class PerformanceProfiler:
    """
    Performance profiler for CORTEX startup and operation profiling.
    
    Features:
    - Context manager for easy timing
    - Decorator for function timing
    - Hierarchical timing (parent-child relationships)
    - Statistics aggregation
    - Performance report generation
    
    Example:
        >>> profiler = PerformanceProfiler()
        >>> 
        >>> # Context manager
        >>> with profiler.measure("load_config"):
        ...     config = load_yaml("config.yaml")
        >>> 
        >>> # Decorator
        >>> @profiler.profile
        ... def initialize_brain():
        ...     pass
        >>> 
        >>> # Report
        >>> profiler.print_report()
    """
    
    def __init__(self, enabled: bool = True):
        """
        Initialize profiler.
        
        Args:
            enabled: Whether profiling is enabled (can be disabled in production)
        """
        self.enabled = enabled
        self.entries: List[ProfilerEntry] = []
        self._context_stack: List[str] = []
    
    def measure(self, name: str, metadata: Optional[Dict[str, Any]] = None):
        """
        Context manager for measuring operation duration.
        
        Args:
            name: Operation name
            metadata: Optional metadata to attach
        
        Example:
            >>> profiler = PerformanceProfiler()
            >>> with profiler.measure("database_init"):
            ...     db.connect()
        """
        return _ProfilerContext(self, name, metadata or {})
    
    def profile(self, func: Callable) -> Callable:
        """
        Decorator for profiling functions.
        
        Args:
            func: Function to profile
        
        Returns:
            Wrapped function with profiling
        
        Example:
            >>> profiler = PerformanceProfiler()
            >>> 
            >>> @profiler.profile
            ... def slow_function():
            ...     time.sleep(0.1)
            >>> 
            >>> slow_function()  # Automatically profiled
        """
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if not self.enabled:
                return func(*args, **kwargs)
            
            func_name = f"{func.__module__}.{func.__qualname__}"
            
            with self.measure(func_name):
                return func(*args, **kwargs)
        
        return wrapper
    
    def record(
        self, 
        name: str, 
        duration_ms: float, 
        parent: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Manually record a measurement.
        
        Args:
            name: Operation name
            duration_ms: Duration in milliseconds
            parent: Optional parent operation name
            metadata: Optional metadata
        """
        if not self.enabled:
            return
        
        entry = ProfilerEntry(
            name=name,
            duration_ms=duration_ms,
            timestamp=datetime.now(),
            parent=parent,
            metadata=metadata or {}
        )
        
        self.entries.append(entry)
        logger.debug(f"Profile: {name} took {duration_ms:.2f}ms")
    
    def get_stats(self, operation_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get performance statistics.
        
        Args:
            operation_name: Optional filter by operation name
        
        Returns:
            Dict with statistics:
            - count: Number of measurements
            - total_ms: Total duration
            - avg_ms: Average duration
            - min_ms: Minimum duration
            - max_ms: Maximum duration
        """
        if operation_name:
            entries = [e for e in self.entries if e.name == operation_name]
        else:
            entries = self.entries
        
        if not entries:
            return {
                'count': 0,
                'total_ms': 0.0,
                'avg_ms': 0.0,
                'min_ms': 0.0,
                'max_ms': 0.0
            }
        
        durations = [e.duration_ms for e in entries]
        
        return {
            'count': len(durations),
            'total_ms': sum(durations),
            'avg_ms': sum(durations) / len(durations),
            'min_ms': min(durations),
            'max_ms': max(durations)
        }
    
    def get_all_operations(self) -> List[str]:
        """Get list of all profiled operation names."""
        return sorted(set(e.name for e in self.entries))
    
    def get_slow_operations(self, threshold_ms: float = 100.0) -> List[Dict[str, Any]]:
        """
        Get operations slower than threshold.
        
        Args:
            threshold_ms: Threshold in milliseconds
        
        Returns:
            List of slow operations with details
        """
        slow_ops = []
        
        for operation in self.get_all_operations():
            stats = self.get_stats(operation)
            if stats['avg_ms'] >= threshold_ms:
                slow_ops.append({
                    'operation': operation,
                    **stats
                })
        
        return sorted(slow_ops, key=lambda x: x['avg_ms'], reverse=True)
    
    def print_report(self, top_n: int = 20):
        """
        Print performance report to console.
        
        Args:
            top_n: Number of top operations to show
        """
        print("\n" + "=" * 80)
        print("CORTEX PERFORMANCE PROFILE REPORT")
        print("=" * 80)
        print()
        
        # Overall stats
        total_entries = len(self.entries)
        total_time_ms = sum(e.duration_ms for e in self.entries)
        
        print(f"Total Measurements: {total_entries}")
        print(f"Total Time: {total_time_ms:.2f}ms ({total_time_ms/1000:.2f}s)")
        print()
        
        # Top operations by average time
        print(f"TOP {top_n} OPERATIONS (by average time)")
        print("-" * 80)
        print(f"{'Operation':<50} {'Count':>6} {'Avg (ms)':>10} {'Total (ms)':>12}")
        print("-" * 80)
        
        operations = []
        for op_name in self.get_all_operations():
            stats = self.get_stats(op_name)
            operations.append({
                'name': op_name,
                **stats
            })
        
        # Sort by average time
        operations.sort(key=lambda x: x['avg_ms'], reverse=True)
        
        for op in operations[:top_n]:
            name_short = op['name'][:49]
            print(f"{name_short:<50} {op['count']:>6} {op['avg_ms']:>10.2f} {op['total_ms']:>12.2f}")
        
        print()
        
        # Slow operations (>100ms)
        slow_ops = self.get_slow_operations(threshold_ms=100.0)
        if slow_ops:
            print(f"SLOW OPERATIONS (>100ms average)")
            print("-" * 80)
            for op in slow_ops:
                print(f"  • {op['operation']}: {op['avg_ms']:.2f}ms avg")
        else:
            print("✅ No slow operations detected (all <100ms)")
        
        print()
        print("=" * 80)
    
    def export_report(self, output_file: str):
        """
        Export performance report to markdown file.
        
        Args:
            output_file: Output file path
        """
        from pathlib import Path
        
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            f.write("# CORTEX Performance Profile Report\n\n")
            f.write(f"**Generated:** {datetime.now().isoformat()}\n\n")
            
            # Overall stats
            total_entries = len(self.entries)
            total_time_ms = sum(e.duration_ms for e in self.entries)
            
            f.write("## Summary\n\n")
            f.write(f"- **Total Measurements:** {total_entries}\n")
            f.write(f"- **Total Time:** {total_time_ms:.2f}ms ({total_time_ms/1000:.2f}s)\n")
            f.write("\n")
            
            # All operations table
            f.write("## All Operations\n\n")
            f.write("| Operation | Count | Avg (ms) | Min (ms) | Max (ms) | Total (ms) |\n")
            f.write("|-----------|-------|----------|----------|----------|------------|\n")
            
            operations = []
            for op_name in self.get_all_operations():
                stats = self.get_stats(op_name)
                operations.append({'name': op_name, **stats})
            
            operations.sort(key=lambda x: x['avg_ms'], reverse=True)
            
            for op in operations:
                f.write(f"| {op['name']} | {op['count']} | {op['avg_ms']:.2f} | "
                       f"{op['min_ms']:.2f} | {op['max_ms']:.2f} | {op['total_ms']:.2f} |\n")
            
            f.write("\n")
            
            # Slow operations
            slow_ops = self.get_slow_operations(threshold_ms=100.0)
            if slow_ops:
                f.write("## Slow Operations (>100ms)\n\n")
                for op in slow_ops:
                    f.write(f"- **{op['operation']}**: {op['avg_ms']:.2f}ms avg "
                           f"({op['count']} calls, {op['total_ms']:.2f}ms total)\n")
            else:
                f.write("## Slow Operations\n\n")
                f.write("✅ No slow operations detected (all <100ms)\n")
            
            f.write("\n---\n\n")
            f.write("**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.\n")
        
        logger.info(f"Performance report exported to: {output_path}")
    
    def clear(self):
        """Clear all profiling data."""
        self.entries.clear()
        self._context_stack.clear()
    
    def enable(self):
        """Enable profiling."""
        self.enabled = True
    
    def disable(self):
        """Disable profiling."""
        self.enabled = False


class _ProfilerContext:
    """Context manager for profiler measurements."""
    
    def __init__(self, profiler: PerformanceProfiler, name: str, metadata: Dict[str, Any]):
        self.profiler = profiler
        self.name = name
        self.metadata = metadata
        self.start_time = 0.0
    
    def __enter__(self):
        if not self.profiler.enabled:
            return self
        
        self.start_time = time.perf_counter()
        
        # Track parent context
        parent = self.profiler._context_stack[-1] if self.profiler._context_stack else None
        self.metadata['parent'] = parent
        self.profiler._context_stack.append(self.name)
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self.profiler.enabled:
            return False
        
        duration_ms = (time.perf_counter() - self.start_time) * 1000
        
        self.profiler.record(
            name=self.name,
            duration_ms=duration_ms,
            parent=self.metadata.get('parent'),
            metadata=self.metadata
        )
        
        # Pop context stack
        if self.profiler._context_stack and self.profiler._context_stack[-1] == self.name:
            self.profiler._context_stack.pop()
        
        return False


# Global singleton profiler
_global_profiler: Optional[PerformanceProfiler] = None


def get_global_profiler() -> PerformanceProfiler:
    """
    Get global profiler instance.
    
    Returns:
        Global PerformanceProfiler instance
    """
    global _global_profiler
    if _global_profiler is None:
        _global_profiler = PerformanceProfiler()
    return _global_profiler


def profile(func: Callable) -> Callable:
    """
    Convenience decorator using global profiler.
    
    Example:
        >>> from src.utils.performance_profiler import profile
        >>> 
        >>> @profile
        ... def slow_function():
        ...     time.sleep(0.1)
    """
    profiler = get_global_profiler()
    return profiler.profile(func)


def measure(name: str, metadata: Optional[Dict[str, Any]] = None):
    """
    Convenience context manager using global profiler.
    
    Example:
        >>> from src.utils.performance_profiler import measure
        >>> 
        >>> with measure("database_query"):
        ...     db.execute("SELECT * FROM users")
    """
    profiler = get_global_profiler()
    return profiler.measure(name, metadata)
