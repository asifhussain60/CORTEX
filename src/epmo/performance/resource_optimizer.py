"""
CORTEX 3.0 Resource Optimizer
==============================

Intelligent resource management and optimization for production-scale
documentation generation with memory management and performance tuning.
"""

import gc
import sys
import threading
import time
import psutil
import os
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
import logging
import weakref
from concurrent.futures import ThreadPoolExecutor
import tracemalloc


logger = logging.getLogger(__name__)


class OptimizationLevel(Enum):
    """Resource optimization levels."""
    CONSERVATIVE = "conservative"
    BALANCED = "balanced"
    AGGRESSIVE = "aggressive"
    CUSTOM = "custom"


class ResourceType(Enum):
    """Types of resources to optimize."""
    MEMORY = "memory"
    CPU = "cpu"
    DISK_IO = "disk_io"
    NETWORK = "network"
    THREADS = "threads"


@dataclass
class ResourceLimits:
    """Resource usage limits."""
    max_memory_mb: Optional[float] = None
    max_cpu_percent: Optional[float] = None
    max_threads: Optional[int] = None
    max_open_files: Optional[int] = None
    max_cache_size_mb: Optional[float] = None
    gc_threshold_mb: Optional[float] = None


@dataclass
class OptimizationResult:
    """Result of resource optimization."""
    optimization_type: str
    resources_freed_mb: float = 0.0
    execution_time_ms: float = 0.0
    items_processed: int = 0
    performance_gain: float = 0.0
    recommendations: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class ResourceProfile:
    """Resource usage profile for different operations."""
    operation_type: str
    baseline_memory_mb: float = 0.0
    peak_memory_mb: float = 0.0
    avg_cpu_percent: float = 0.0
    execution_time_ms: float = 0.0
    thread_count: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    
    @property
    def memory_efficiency(self) -> float:
        """Calculate memory efficiency score."""
        if self.peak_memory_mb == 0:
            return 1.0
        return min(1.0, self.baseline_memory_mb / self.peak_memory_mb)
    
    @property
    def cache_efficiency(self) -> float:
        """Calculate cache efficiency score."""
        total_requests = self.cache_hits + self.cache_misses
        if total_requests == 0:
            return 0.0
        return self.cache_hits / total_requests


class ResourceOptimizer:
    """
    Intelligent resource optimizer for production documentation generation
    with memory management, performance tuning, and resource monitoring.
    """
    
    def __init__(
        self,
        optimization_level: OptimizationLevel = OptimizationLevel.BALANCED,
        resource_limits: Optional[ResourceLimits] = None,
        auto_optimize: bool = True,
        monitoring_interval: float = 30.0
    ):
        self.optimization_level = optimization_level
        self.resource_limits = resource_limits or self._get_default_limits()
        self.auto_optimize = auto_optimize
        self.monitoring_interval = monitoring_interval
        
        # Resource tracking
        self._process = psutil.Process()
        self._optimization_history: List[OptimizationResult] = []
        self._resource_profiles: Dict[str, ResourceProfile] = {}
        self._lock = threading.RLock()
        
        # Object tracking for memory optimization
        self._tracked_objects: weakref.WeakSet = weakref.WeakSet()
        self._large_objects: List[weakref.ref] = []
        
        # Monitoring state
        self._monitoring = False
        self._monitor_thread: Optional[threading.Thread] = None
        
        # Memory tracking
        self._memory_snapshots: List[float] = []
        self._gc_stats: Dict[str, int] = {}
        
        # Performance callbacks
        self._optimization_callbacks: List[Callable[[OptimizationResult], None]] = []
        
        # Enable memory tracking if aggressive optimization
        if optimization_level == OptimizationLevel.AGGRESSIVE:
            tracemalloc.start()
    
    def start_monitoring(self) -> None:
        """Start resource monitoring and auto-optimization."""
        if self._monitoring:
            return
        
        self._monitoring = True
        self._monitor_thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=True
        )
        self._monitor_thread.start()
        
        logger.info("Resource monitoring started")
    
    def stop_monitoring(self) -> None:
        """Stop resource monitoring."""
        self._monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5.0)
        
        logger.info("Resource monitoring stopped")
    
    def optimize_memory(self, force_gc: bool = False) -> OptimizationResult:
        """
        Perform memory optimization with garbage collection and cache cleanup.
        
        Args:
            force_gc: Force aggressive garbage collection
            
        Returns:
            Optimization result with freed memory information
        """
        start_time = time.time()
        start_memory = self._get_memory_usage()
        
        result = OptimizationResult(optimization_type="memory")
        
        try:
            # Track objects before optimization
            initial_objects = len(gc.get_objects())
            
            # 1. Standard garbage collection
            if force_gc or self.optimization_level in [OptimizationLevel.AGGRESSIVE, OptimizationLevel.BALANCED]:
                collected = []
                for generation in range(3):
                    collected.append(gc.collect(generation))
                
                result.items_processed = sum(collected)
                logger.debug(f"GC collected: {collected}")
            
            # 2. Clean up weak references to deleted objects
            self._cleanup_weak_references()
            
            # 3. Clear internal caches if memory pressure is high
            current_memory = self._get_memory_usage()
            if (self.resource_limits.max_memory_mb and 
                current_memory > self.resource_limits.max_memory_mb * 0.8):
                self._clear_internal_caches()
            
            # 4. Optimize large objects if aggressive mode
            if self.optimization_level == OptimizationLevel.AGGRESSIVE:
                self._optimize_large_objects()
            
            # 5. System-specific optimizations
            if sys.platform.startswith('linux'):
                self._linux_memory_optimization()
            
            # Calculate results
            end_memory = self._get_memory_usage()
            result.resources_freed_mb = start_memory - end_memory
            result.execution_time_ms = (time.time() - start_time) * 1000
            
            # Performance analysis
            if result.resources_freed_mb > 0:
                result.performance_gain = result.resources_freed_mb / start_memory
                result.recommendations.append(
                    f"Freed {result.resources_freed_mb:.1f}MB memory"
                )
            
            # Memory efficiency warnings
            if current_memory > self.resource_limits.max_memory_mb * 0.9:
                result.warnings.append("Memory usage approaching limit")
            
            final_objects = len(gc.get_objects())
            if initial_objects - final_objects > 1000:
                result.recommendations.append(
                    f"Cleaned up {initial_objects - final_objects} objects"
                )
        
        except Exception as e:
            result.warnings.append(f"Memory optimization error: {e}")
            logger.error(f"Memory optimization failed: {e}")
        
        self._record_optimization(result)
        return result
    
    def optimize_cpu(self) -> OptimizationResult:
        """
        Perform CPU optimization by adjusting thread pools and process priority.
        
        Returns:
            Optimization result with CPU optimization details
        """
        start_time = time.time()
        result = OptimizationResult(optimization_type="cpu")
        
        try:
            # Get current CPU usage
            cpu_percent = psutil.cpu_percent(interval=1.0)
            cpu_count = psutil.cpu_count()
            
            # 1. Optimize thread pool sizes
            if hasattr(ThreadPoolExecutor, '_threads'):
                active_threads = threading.active_count()
                optimal_threads = min(cpu_count * 2, active_threads)
                
                if active_threads > optimal_threads:
                    result.recommendations.append(
                        f"Consider reducing thread count from {active_threads} to {optimal_threads}"
                    )
            
            # 2. Adjust process priority if high CPU usage
            if cpu_percent > 80.0:
                try:
                    current_priority = self._process.nice()
                    if current_priority <= 0:  # Can increase niceness (lower priority)
                        new_priority = min(5, current_priority + 2)
                        self._process.nice(new_priority)
                        result.recommendations.append(
                            f"Adjusted process priority from {current_priority} to {new_priority}"
                        )
                except (psutil.AccessDenied, psutil.NoSuchProcess):
                    result.warnings.append("Cannot adjust process priority")
            
            # 3. CPU affinity optimization (Linux/Windows)
            if self.optimization_level == OptimizationLevel.AGGRESSIVE:
                try:
                    available_cpus = self._process.cpu_affinity()
                    if len(available_cpus) > 2:
                        # Use subset of CPUs for better cache locality
                        optimal_cpus = available_cpus[:max(2, len(available_cpus) // 2)]
                        self._process.cpu_affinity(optimal_cpus)
                        result.recommendations.append(
                            f"Set CPU affinity to {len(optimal_cpus)} cores"
                        )
                except (psutil.AccessDenied, AttributeError):
                    pass  # Not supported on all platforms
            
            result.execution_time_ms = (time.time() - start_time) * 1000
            result.performance_gain = max(0, (80.0 - cpu_percent) / 80.0)
        
        except Exception as e:
            result.warnings.append(f"CPU optimization error: {e}")
            logger.error(f"CPU optimization failed: {e}")
        
        self._record_optimization(result)
        return result
    
    def optimize_io(self) -> OptimizationResult:
        """
        Optimize I/O operations including file handles and disk access.
        
        Returns:
            Optimization result with I/O optimization details
        """
        start_time = time.time()
        result = OptimizationResult(optimization_type="io")
        
        try:
            # 1. Check and cleanup file handles
            open_files = self._process.open_files()
            if len(open_files) > 100:  # Arbitrary threshold
                result.warnings.append(
                    f"High number of open files: {len(open_files)}"
                )
                result.recommendations.append(
                    "Consider implementing file handle pooling"
                )
            
            # 2. Optimize file descriptor limits
            try:
                import resource
                soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
                if soft < 1024:
                    new_soft = min(hard, 2048)
                    resource.setrlimit(resource.RLIMIT_NOFILE, (new_soft, hard))
                    result.recommendations.append(
                        f"Increased file descriptor limit to {new_soft}"
                    )
            except (ImportError, OSError, ValueError):
                pass  # Not available on all platforms
            
            # 3. Buffer optimization recommendations
            if self.optimization_level == OptimizationLevel.AGGRESSIVE:
                result.recommendations.extend([
                    "Use larger buffer sizes for file operations",
                    "Implement read-ahead for sequential file access",
                    "Consider using memory-mapped files for large datasets"
                ])
            
            result.execution_time_ms = (time.time() - start_time) * 1000
        
        except Exception as e:
            result.warnings.append(f"I/O optimization error: {e}")
            logger.error(f"I/O optimization failed: {e}")
        
        self._record_optimization(result)
        return result
    
    def profile_operation(
        self,
        operation_name: str,
        operation_func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """
        Profile a specific operation and store resource usage patterns.
        
        Args:
            operation_name: Name of the operation to profile
            operation_func: Function to profile
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
        """
        # Start profiling
        start_time = time.time()
        start_memory = self._get_memory_usage()
        start_threads = threading.active_count()
        
        # Memory snapshot
        if tracemalloc.is_tracing():
            snapshot_start = tracemalloc.take_snapshot()
        else:
            snapshot_start = None
        
        try:
            # Execute operation
            result = operation_func(*args, **kwargs)
            
            # End profiling
            end_time = time.time()
            end_memory = self._get_memory_usage()
            peak_memory = max(start_memory, end_memory)
            
            # Create resource profile
            profile = ResourceProfile(
                operation_type=operation_name,
                baseline_memory_mb=start_memory,
                peak_memory_mb=peak_memory,
                execution_time_ms=(end_time - start_time) * 1000,
                thread_count=max(start_threads, threading.active_count())
            )
            
            # Memory growth analysis
            if snapshot_start and tracemalloc.is_tracing():
                snapshot_end = tracemalloc.take_snapshot()
                top_stats = snapshot_end.compare_to(snapshot_start, 'lineno')
                
                if top_stats:
                    memory_growth = sum(stat.size_diff for stat in top_stats[:10])
                    profile.peak_memory_mb += memory_growth / (1024 * 1024)
            
            # Store profile
            with self._lock:
                self._resource_profiles[operation_name] = profile
            
            logger.debug(
                f"Operation {operation_name}: "
                f"{profile.execution_time_ms:.1f}ms, "
                f"{profile.peak_memory_mb:.1f}MB peak"
            )
            
            return result
        
        except Exception as e:
            logger.error(f"Operation profiling failed for {operation_name}: {e}")
            raise
    
    def get_optimization_recommendations(self) -> List[str]:
        """Get intelligent optimization recommendations based on profiling data."""
        recommendations = []
        
        with self._lock:
            # Analyze resource profiles
            if self._resource_profiles:
                # Memory-intensive operations
                memory_heavy = [
                    name for name, profile in self._resource_profiles.items()
                    if profile.peak_memory_mb > 100  # 100MB threshold
                ]
                
                if memory_heavy:
                    recommendations.append(
                        f"Consider memory optimization for: {', '.join(memory_heavy)}"
                    )
                
                # Slow operations
                slow_operations = [
                    name for name, profile in self._resource_profiles.items()
                    if profile.execution_time_ms > 5000  # 5 second threshold
                ]
                
                if slow_operations:
                    recommendations.append(
                        f"Consider performance optimization for: {', '.join(slow_operations)}"
                    )
                
                # Low cache efficiency
                low_cache = [
                    name for name, profile in self._resource_profiles.items()
                    if profile.cache_efficiency < 0.5 and profile.cache_hits + profile.cache_misses > 0
                ]
                
                if low_cache:
                    recommendations.append(
                        f"Consider cache optimization for: {', '.join(low_cache)}"
                    )
            
            # General recommendations based on optimization history
            if self._optimization_history:
                memory_optimizations = [
                    opt for opt in self._optimization_history
                    if opt.optimization_type == "memory"
                ]
                
                if memory_optimizations:
                    avg_freed = sum(opt.resources_freed_mb for opt in memory_optimizations) / len(memory_optimizations)
                    if avg_freed > 50:  # 50MB average
                        recommendations.append(
                            "Frequent memory optimization needed - consider reducing memory footprint"
                        )
        
        # Current resource status recommendations
        current_memory = self._get_memory_usage()
        if (self.resource_limits.max_memory_mb and 
            current_memory > self.resource_limits.max_memory_mb * 0.8):
            recommendations.append("Memory usage high - consider immediate optimization")
        
        if not recommendations:
            recommendations.append("Resource usage is optimal")
        
        return recommendations
    
    def get_resource_summary(self) -> Dict[str, Any]:
        """Get comprehensive resource usage summary."""
        current_memory = self._get_memory_usage()
        
        summary = {
            'current_memory_mb': current_memory,
            'memory_limit_mb': self.resource_limits.max_memory_mb,
            'memory_utilization': (
                current_memory / self.resource_limits.max_memory_mb
                if self.resource_limits.max_memory_mb else 0.0
            ),
            'optimization_level': self.optimization_level.value,
            'total_optimizations': len(self._optimization_history),
            'profiles_count': len(self._resource_profiles),
            'recommendations': self.get_optimization_recommendations()
        }
        
        # Recent optimization results
        if self._optimization_history:
            recent = self._optimization_history[-5:]  # Last 5 optimizations
            summary['recent_optimizations'] = [
                {
                    'type': opt.optimization_type,
                    'freed_mb': opt.resources_freed_mb,
                    'duration_ms': opt.execution_time_ms,
                    'performance_gain': opt.performance_gain
                }
                for opt in recent
            ]
        
        return summary
    
    def add_optimization_callback(
        self,
        callback: Callable[[OptimizationResult], None]
    ) -> None:
        """Add callback for optimization events."""
        self._optimization_callbacks.append(callback)
    
    def _get_default_limits(self) -> ResourceLimits:
        """Get default resource limits based on system capabilities."""
        system_memory = psutil.virtual_memory().total / (1024 * 1024)  # MB
        
        return ResourceLimits(
            max_memory_mb=system_memory * 0.8,  # 80% of system memory
            max_cpu_percent=80.0,
            max_threads=psutil.cpu_count() * 4,
            max_open_files=1024,
            max_cache_size_mb=system_memory * 0.2,  # 20% for cache
            gc_threshold_mb=100.0  # Trigger GC at 100MB growth
        )
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        try:
            return self._process.memory_info().rss / (1024 * 1024)
        except psutil.NoSuchProcess:
            return 0.0
    
    def _cleanup_weak_references(self) -> None:
        """Clean up weak references to deleted objects."""
        self._large_objects = [ref for ref in self._large_objects if ref() is not None]
    
    def _clear_internal_caches(self) -> None:
        """Clear internal Python caches."""
        # Clear type cache
        if hasattr(sys, '_clear_type_cache'):
            sys._clear_type_cache()
        
        # Clear import cache
        if hasattr(sys, 'modules'):
            # Don't clear sys.modules, but clear __pycache__
            for module in sys.modules.values():
                if hasattr(module, '__pycache__'):
                    if hasattr(module.__pycache__, 'clear'):
                        module.__pycache__.clear()
    
    def _optimize_large_objects(self) -> None:
        """Optimize handling of large objects."""
        # This is a placeholder for more sophisticated large object optimization
        # In practice, you might implement object pooling, compression, etc.
        pass
    
    def _linux_memory_optimization(self) -> None:
        """Linux-specific memory optimizations."""
        try:
            # Advise the kernel about memory usage patterns
            import madvise
            # This would require a custom madvise module
            # madvise.madvise_dontneed() for unused memory regions
        except ImportError:
            pass
    
    def _record_optimization(self, result: OptimizationResult) -> None:
        """Record optimization result and notify callbacks."""
        with self._lock:
            self._optimization_history.append(result)
            
            # Keep only recent history
            if len(self._optimization_history) > 100:
                self._optimization_history = self._optimization_history[-50:]
        
        # Notify callbacks
        for callback in self._optimization_callbacks:
            try:
                callback(result)
            except Exception as e:
                logger.warning(f"Optimization callback error: {e}")
    
    def _monitoring_loop(self) -> None:
        """Main resource monitoring loop."""
        logger.info("Resource monitoring loop started")
        
        while self._monitoring:
            try:
                current_memory = self._get_memory_usage()
                
                # Auto-optimize if thresholds exceeded
                if self.auto_optimize:
                    if (self.resource_limits.gc_threshold_mb and 
                        len(self._memory_snapshots) > 0 and
                        current_memory - self._memory_snapshots[-1] > self.resource_limits.gc_threshold_mb):
                        self.optimize_memory()
                    
                    if (self.resource_limits.max_memory_mb and 
                        current_memory > self.resource_limits.max_memory_mb * 0.9):
                        self.optimize_memory(force_gc=True)
                
                # Update memory snapshots
                self._memory_snapshots.append(current_memory)
                if len(self._memory_snapshots) > 100:
                    self._memory_snapshots = self._memory_snapshots[-50:]
                
                time.sleep(self.monitoring_interval)
            
            except Exception as e:
                logger.error(f"Resource monitoring error: {e}")
                time.sleep(self.monitoring_interval)
        
        logger.info("Resource monitoring loop stopped")


# Global optimizer instance
default_optimizer = ResourceOptimizer()