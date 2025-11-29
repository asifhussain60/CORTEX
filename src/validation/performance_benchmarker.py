"""
Performance Benchmarker - Layer 7 Performance Validation

Validates orchestrator performance against defined thresholds:
- Response time: <500ms (typical operations)
- Memory usage: <100MB peak
- CPU usage: <50% average

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import time
import psutil
import tracemalloc
from typing import Dict, Any, Callable, Optional
from dataclasses import dataclass
from pathlib import Path
import json
from datetime import datetime


@dataclass
class PerformanceThresholds:
    """Performance thresholds for validation."""
    response_time_ms: float = 500.0  # Maximum response time in milliseconds
    memory_mb: float = 100.0  # Maximum memory usage in megabytes
    cpu_percent: float = 50.0  # Maximum CPU usage percentage


@dataclass
class PerformanceMetrics:
    """Performance metrics captured during benchmark."""
    response_time_ms: float
    memory_peak_mb: float
    memory_current_mb: float
    cpu_percent: float
    timestamp: datetime
    passed: bool
    violations: list[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        return {
            "response_time_ms": self.response_time_ms,
            "memory_peak_mb": self.memory_peak_mb,
            "memory_current_mb": self.memory_current_mb,
            "cpu_percent": self.cpu_percent,
            "timestamp": self.timestamp.isoformat(),
            "passed": self.passed,
            "violations": self.violations
        }


class PerformanceBenchmarker:
    """
    Performance benchmarking framework for CORTEX orchestrators.
    
    Measures:
    - Response time (execution duration)
    - Memory usage (peak and current)
    - CPU usage (average during execution)
    
    Validates against thresholds and generates reports.
    """
    
    def __init__(
        self,
        thresholds: Optional[PerformanceThresholds] = None,
        report_path: Optional[Path] = None
    ):
        """
        Initialize performance benchmarker.
        
        Args:
            thresholds: Performance thresholds (uses defaults if None)
            report_path: Path to save benchmark reports
        """
        self.thresholds = thresholds or PerformanceThresholds()
        self.report_path = report_path or Path("cortex-brain/documents/reports/performance")
        self.report_path.mkdir(parents=True, exist_ok=True)
    
    def benchmark(
        self,
        func: Callable,
        *args,
        label: str = "operation",
        **kwargs
    ) -> PerformanceMetrics:
        """
        Benchmark a function call and measure performance.
        
        Args:
            func: Function to benchmark
            *args: Positional arguments for function
            label: Label for this benchmark
            **kwargs: Keyword arguments for function
            
        Returns:
            PerformanceMetrics with measured values and validation results
        """
        # Start memory tracking
        tracemalloc.start()
        
        # Get initial CPU and memory state
        process = psutil.Process()
        cpu_before = process.cpu_percent(interval=0.1)
        
        # Execute function and measure time
        start_time = time.perf_counter()
        
        try:
            result = func(*args, **kwargs)
        finally:
            end_time = time.perf_counter()
            
            # Measure final state
            cpu_after = process.cpu_percent(interval=0.1)
            cpu_avg = (cpu_before + cpu_after) / 2
            
            # Get memory metrics
            current_memory, peak_memory = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            
            # Convert to appropriate units
            response_time_ms = (end_time - start_time) * 1000
            memory_peak_mb = peak_memory / (1024 * 1024)
            memory_current_mb = current_memory / (1024 * 1024)
        
        # Validate against thresholds
        violations = []
        
        if response_time_ms > self.thresholds.response_time_ms:
            violations.append(
                f"Response time {response_time_ms:.2f}ms exceeds threshold "
                f"{self.thresholds.response_time_ms}ms"
            )
        
        if memory_peak_mb > self.thresholds.memory_mb:
            violations.append(
                f"Peak memory {memory_peak_mb:.2f}MB exceeds threshold "
                f"{self.thresholds.memory_mb}MB"
            )
        
        if cpu_avg > self.thresholds.cpu_percent:
            violations.append(
                f"CPU usage {cpu_avg:.2f}% exceeds threshold "
                f"{self.thresholds.cpu_percent}%"
            )
        
        # Create metrics object
        metrics = PerformanceMetrics(
            response_time_ms=response_time_ms,
            memory_peak_mb=memory_peak_mb,
            memory_current_mb=memory_current_mb,
            cpu_percent=cpu_avg,
            timestamp=datetime.now(),
            passed=len(violations) == 0,
            violations=violations
        )
        
        # Save report
        self._save_report(label, metrics)
        
        return metrics
    
    def benchmark_orchestrator(
        self,
        orchestrator_class: type,
        operation: str,
        context: Dict[str, Any]
    ) -> PerformanceMetrics:
        """
        Benchmark an orchestrator operation.
        
        Args:
            orchestrator_class: Orchestrator class to benchmark
            operation: Operation method name (e.g., 'execute')
            context: Context dictionary for operation
            
        Returns:
            PerformanceMetrics for the operation
        """
        def run_operation():
            orchestrator = orchestrator_class()
            method = getattr(orchestrator, operation)
            return method(context)
        
        label = f"{orchestrator_class.__name__}.{operation}"
        return self.benchmark(run_operation, label=label)
    
    def _save_report(self, label: str, metrics: PerformanceMetrics):
        """Save benchmark report to file."""
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"benchmark_{label.replace('.', '_')}_{timestamp_str}.json"
        filepath = self.report_path / filename
        
        report = {
            "label": label,
            "metrics": metrics.to_dict(),
            "thresholds": {
                "response_time_ms": self.thresholds.response_time_ms,
                "memory_mb": self.thresholds.memory_mb,
                "cpu_percent": self.thresholds.cpu_percent
            }
        }
        
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)
    
    def generate_summary_report(
        self,
        orchestrator_name: str,
        benchmarks: list[PerformanceMetrics]
    ) -> Dict[str, Any]:
        """
        Generate summary report for multiple benchmarks.
        
        Args:
            orchestrator_name: Name of orchestrator being benchmarked
            benchmarks: List of benchmark metrics
            
        Returns:
            Summary report dictionary
        """
        if not benchmarks:
            return {
                "orchestrator": orchestrator_name,
                "total_benchmarks": 0,
                "all_passed": False
            }
        
        passed_count = sum(1 for b in benchmarks if b.passed)
        avg_response_time = sum(b.response_time_ms for b in benchmarks) / len(benchmarks)
        avg_memory = sum(b.memory_peak_mb for b in benchmarks) / len(benchmarks)
        avg_cpu = sum(b.cpu_percent for b in benchmarks) / len(benchmarks)
        
        all_violations = []
        for benchmark in benchmarks:
            all_violations.extend(benchmark.violations)
        
        summary = {
            "orchestrator": orchestrator_name,
            "total_benchmarks": len(benchmarks),
            "passed": passed_count,
            "failed": len(benchmarks) - passed_count,
            "all_passed": passed_count == len(benchmarks),
            "averages": {
                "response_time_ms": avg_response_time,
                "memory_peak_mb": avg_memory,
                "cpu_percent": avg_cpu
            },
            "thresholds": {
                "response_time_ms": self.thresholds.response_time_ms,
                "memory_mb": self.thresholds.memory_mb,
                "cpu_percent": self.thresholds.cpu_percent
            },
            "violations": all_violations,
            "timestamp": datetime.now().isoformat()
        }
        
        # Save summary report
        filename = f"summary_{orchestrator_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = self.report_path / filename
        
        with open(filepath, 'w') as f:
            json.dump(summary, f, indent=2)
        
        return summary


def validate_orchestrator_performance(
    orchestrator_class: type,
    test_operations: list[tuple[str, Dict[str, Any]]],
    thresholds: Optional[PerformanceThresholds] = None
) -> tuple[bool, Dict[str, Any]]:
    """
    Validate orchestrator performance against thresholds.
    
    Args:
        orchestrator_class: Orchestrator class to validate
        test_operations: List of (operation_name, context) tuples
        thresholds: Custom thresholds (uses defaults if None)
        
    Returns:
        Tuple of (all_passed, summary_report)
    """
    benchmarker = PerformanceBenchmarker(thresholds=thresholds)
    benchmarks = []
    
    for operation, context in test_operations:
        metrics = benchmarker.benchmark_orchestrator(
            orchestrator_class,
            operation,
            context
        )
        benchmarks.append(metrics)
    
    summary = benchmarker.generate_summary_report(
        orchestrator_class.__name__,
        benchmarks
    )
    
    return summary["all_passed"], summary
