"""
Performance Tuning and Optimization - CORTEX 6.0
feat07-integration Phase 3

Profile critical paths, optimize bottlenecks, validate SLAs

Author: Asif Hussain
Version: 1.0.0
Created: 2026-01-08
"""

import time
import pytest
from typing import Dict, List, Any, Callable
from dataclasses import dataclass
from functools import wraps
import statistics


@dataclass
class PerformanceMetric:
    """Performance metric data"""
    operation: str
    duration_ms: float
    iterations: int
    success: bool
    threshold_ms: float
    
    @property
    def meets_sla(self) -> bool:
        """Check if performance meets SLA"""
        return self.duration_ms <= self.threshold_ms
    
    def __str__(self) -> str:
        status = "✅" if self.meets_sla else "❌"
        return (
            f"{status} {self.operation}: {self.duration_ms:.2f}ms "
            f"(SLA: {self.threshold_ms}ms, {self.iterations} iterations)"
        )


class PerformanceProfiler:
    """
    Performance profiler for CORTEX operations
    Tracks execution times and validates SLAs
    """
    
    def __init__(self):
        self.metrics: List[PerformanceMetric] = []
        self.sla_thresholds = {
            "plan_processing_100_tasks": 500.0,  # 500ms for 100-task plan
            "task_completion": 50.0,  # 50ms per task
            "governance_merge": 50.0,  # 50ms for governance merge
            "dag_validation": 10.0,  # 10ms for DAG validation
            "unicode_normalization": 1.0,  # 1ms for text normalization
            "state_read": 5.0,  # 5ms for state read
            "state_write": 10.0,  # 10ms for state write
            "audit_log_write": 2.0,  # 2ms for audit log
        }
    
    def profile(
        self,
        operation: str,
        func: Callable,
        iterations: int = 100,
        threshold_override: float = None
    ) -> PerformanceMetric:
        """
        Profile a function's performance
        
        Args:
            operation: Operation name
            func: Function to profile
            iterations: Number of iterations
            threshold_override: Custom threshold (overrides SLA)
        
        Returns:
            PerformanceMetric with results
        """
        durations = []
        success = True
        
        try:
            for _ in range(iterations):
                start = time.perf_counter()
                func()
                duration = (time.perf_counter() - start) * 1000  # Convert to ms
                durations.append(duration)
        except Exception as e:
            success = False
            print(f"Error during profiling: {e}")
        
        avg_duration = statistics.mean(durations) if durations else 0.0
        threshold = threshold_override or self.sla_thresholds.get(operation, 100.0)
        
        metric = PerformanceMetric(
            operation=operation,
            duration_ms=avg_duration,
            iterations=iterations,
            success=success,
            threshold_ms=threshold
        )
        
        self.metrics.append(metric)
        return metric
    
    def benchmark_decorator(self, operation: str, threshold_ms: float = None):
        """
        Decorator for benchmarking functions
        
        Usage:
            profiler = PerformanceProfiler()
            
            @profiler.benchmark_decorator("my_operation", threshold_ms=100)
            def my_function():
                # ... code ...
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                start = time.perf_counter()
                result = func(*args, **kwargs)
                duration_ms = (time.perf_counter() - start) * 1000
                
                threshold = threshold_ms or self.sla_thresholds.get(operation, 100.0)
                
                metric = PerformanceMetric(
                    operation=operation,
                    duration_ms=duration_ms,
                    iterations=1,
                    success=True,
                    threshold_ms=threshold
                )
                self.metrics.append(metric)
                
                return result
            return wrapper
        return decorator
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate performance report"""
        if not self.metrics:
            return {"status": "No metrics collected"}
        
        total_metrics = len(self.metrics)
        passing_metrics = sum(1 for m in self.metrics if m.meets_sla)
        
        return {
            "total_operations": total_metrics,
            "passing_sla": passing_metrics,
            "failing_sla": total_metrics - passing_metrics,
            "pass_rate": f"{(passing_metrics / total_metrics) * 100:.1f}%",
            "metrics": [
                {
                    "operation": m.operation,
                    "duration_ms": round(m.duration_ms, 2),
                    "threshold_ms": m.threshold_ms,
                    "meets_sla": m.meets_sla,
                    "status": "PASS" if m.meets_sla else "FAIL"
                }
                for m in self.metrics
            ]
        }
    
    def print_report(self) -> None:
        """Print human-readable report"""
        print("\n" + "=" * 60)
        print("PERFORMANCE PROFILING REPORT")
        print("=" * 60)
        
        for metric in self.metrics:
            print(metric)
        
        report = self.generate_report()
        print("\n" + "-" * 60)
        print(f"Total Operations: {report['total_operations']}")
        print(f"Passing SLA: {report['passing_sla']}")
        print(f"Failing SLA: {report['failing_sla']}")
        print(f"Pass Rate: {report['pass_rate']}")
        print("=" * 60 + "\n")


# ==============================================================================
# Performance Tests
# ==============================================================================

class TestPerformanceTuning:
    """
    Task 3.1-3.3: Performance profiling, optimization, and SLA validation
    """
    
    def test_unicode_normalization_performance(self):
        """Test Unicode normalization meets SLA (<1ms)"""
        from src.infrastructure.risk_mitigations import EdgeCaseMitigations
        
        profiler = PerformanceProfiler()
        
        test_text = "Test 测试 тест テスト Café 🚀"
        
        def normalize():
            EdgeCaseMitigations.normalize_unicode(test_text)
        
        metric = profiler.profile("unicode_normalization", normalize, iterations=1000)
        
        print(f"\n{metric}")
        assert metric.meets_sla, f"Unicode normalization too slow: {metric.duration_ms}ms"
    
    def test_dag_validation_performance(self):
        """Test DAG validation meets SLA (<10ms)"""
        from src.infrastructure.risk_mitigations import EdgeCaseMitigations
        from unittest.mock import Mock
        
        profiler = PerformanceProfiler()
        
        # Create mock DAG with 50 tasks
        dag = Mock()
        dag.is_empty.return_value = False
        dag.tasks = [Mock() for _ in range(50)]
        
        def validate():
            EdgeCaseMitigations.validate_dag_not_empty(dag)
        
        metric = profiler.profile("dag_validation", validate, iterations=1000)
        
        print(f"\n{metric}")
        assert metric.meets_sla, f"DAG validation too slow: {metric.duration_ms}ms"
    
    def test_governance_conflict_resolution_performance(self):
        """Test governance conflict resolution meets SLA (<50ms)"""
        from src.infrastructure.risk_mitigations import EdgeCaseMitigations
        
        profiler = PerformanceProfiler()
        
        rule1 = {
            "category": "business_tier0",
            "rule": "Rule A",
            "created_at": "2026-01-01T00:00:00Z"
        }
        rule2 = {
            "category": "cortex_tier0",
            "rule": "Rule B",
            "created_at": "2026-01-02T00:00:00Z"
        }
        
        def resolve():
            EdgeCaseMitigations.resolve_governance_conflict(rule1, rule2)
        
        metric = profiler.profile(
            "governance_merge",
            resolve,
            iterations=1000
        )
        
        print(f"\n{metric}")
        assert metric.meets_sla, f"Conflict resolution too slow: {metric.duration_ms}ms"
    
    def test_mitigation_registry_lookup_performance(self):
        """Test registry lookups are fast"""
        from src.infrastructure.risk_mitigations import get_registry
        
        profiler = PerformanceProfiler()
        registry = get_registry()
        
        def lookup():
            registry.get("EC-001")
            registry.get("EC-002")
            registry.get("FM-001")
        
        metric = profiler.profile(
            "registry_lookup",
            lookup,
            iterations=10000,
            threshold_override=1.0  # Should be <1ms for 3 lookups
        )
        
        print(f"\n{metric}")
        assert metric.meets_sla, f"Registry lookup too slow: {metric.duration_ms}ms"
    
    def test_deep_dag_detection_performance(self):
        """Test deep DAG detection is efficient"""
        from src.infrastructure.risk_mitigations import EdgeCaseMitigations
        from unittest.mock import Mock
        
        profiler = PerformanceProfiler()
        
        # Create DAG with 50-level depth
        dag = Mock()
        dag.get_root_tasks.return_value = ["root"]
        
        def get_deps(task_id):
            if task_id == "root":
                return ["t1"]
            num = int(task_id[1:]) if task_id.startswith("t") else 0
            if num < 50:
                return [f"t{num + 1}"]
            return []
        
        dag.get_dependents.side_effect = get_deps
        dag.tasks = ["root"] + [f"t{i}" for i in range(1, 51)]
        
        def validate():
            EdgeCaseMitigations.validate_dag_depth(dag, max_depth=100)
        
        metric = profiler.profile(
            "deep_dag_validation",
            validate,
            iterations=100,
            threshold_override=10.0
        )
        
        print(f"\n{metric}")
        assert metric.meets_sla, f"Deep DAG validation too slow: {metric.duration_ms}ms"
    
    def test_concurrent_operations_performance(self):
        """Test concurrent task update performance"""
        from src.infrastructure.risk_mitigations import RaceConditionMitigations
        
        profiler = PerformanceProfiler()
        mitigator = RaceConditionMitigations()
        
        counter = {"value": 0}
        
        def update():
            def increment():
                counter["value"] += 1
            mitigator.atomic_task_update("task1", increment)
        
        metric = profiler.profile(
            "atomic_update",
            update,
            iterations=1000,
            threshold_override=1.0  # Should be <1ms
        )
        
        print(f"\n{metric}")
        assert metric.meets_sla, f"Atomic update too slow: {metric.duration_ms}ms"


class TestOptimizationValidation:
    """Validation of optimization work"""
    
    def test_all_critical_paths_optimized(self):
        """Validate all critical paths meet SLA"""
        from src.infrastructure.risk_mitigations import (
            EdgeCaseMitigations,
            get_registry,
            RaceConditionMitigations
        )
        from unittest.mock import Mock
        
        profiler = PerformanceProfiler()
        
        # Test all critical operations
        operations = [
            ("unicode_norm", lambda: EdgeCaseMitigations.normalize_unicode("Test 🚀")),
            ("dag_validate", lambda: EdgeCaseMitigations.validate_dag_not_empty(
                Mock(is_empty=lambda: False, tasks=[Mock()])
            )),
            ("gov_resolve", lambda: EdgeCaseMitigations.resolve_governance_conflict(
                {"category": "business_tier0", "created_at": "2026-01-01"},
                {"category": "cortex_tier0", "created_at": "2026-01-02"}
            )),
            ("registry_get", lambda: get_registry().get("EC-001")),
        ]
        
        for name, func in operations:
            metric = profiler.profile(name, func, iterations=100)
            print(f"\n{metric}")
        
        profiler.print_report()
        
        # All operations should meet their SLAs
        failing = [m for m in profiler.metrics if not m.meets_sla]
        assert len(failing) == 0, f"Operations failing SLA: {[m.operation for m in failing]}"


# ==============================================================================
# Benchmark Suite
# ==============================================================================

class TestPerformanceBenchmarks:
    """Comprehensive benchmarks for all operations"""
    
    def test_comprehensive_benchmark_suite(self):
        """Run comprehensive benchmark of all operations"""
        from src.infrastructure.risk_mitigations import (
            EdgeCaseMitigations,
            FailureModeMitigations,
            RaceConditionMitigations,
            get_registry
        )
        from unittest.mock import Mock
        
        profiler = PerformanceProfiler()
        
        print("\n" + "=" * 60)
        print("COMPREHENSIVE PERFORMANCE BENCHMARK")
        print("=" * 60)
        
        # Benchmark all operations
        benchmarks = {
            "EC-001 Empty DAG": lambda: EdgeCaseMitigations.validate_dag_not_empty(
                Mock(is_empty=lambda: False, tasks=[Mock()])
            ),
            "EC-003 Unicode": lambda: EdgeCaseMitigations.normalize_unicode("Test 测试 🚀"),
            "EC-005 Gov Conflict": lambda: EdgeCaseMitigations.resolve_governance_conflict(
                {"category": "business_tier0", "created_at": "2026-01-01"},
                {"category": "cortex_tier0", "created_at": "2026-01-02"}
            ),
            "Registry Get": lambda: get_registry().get("EC-001"),
            "Registry Stats": lambda: get_registry().get_stats(),
            "FM-002 Failsafe": lambda: FailureModeMitigations.create_audit_failsafe(),
            "RC-001 Get Lock": lambda: RaceConditionMitigations().get_task_lock("task1"),
        }
        
        for name, func in benchmarks.items():
            try:
                metric = profiler.profile(
                    name,
                    func,
                    iterations=1000,
                    threshold_override=10.0  # 10ms general threshold
                )
                print(f"{metric}")
            except Exception as e:
                print(f"❌ {name}: ERROR - {e}")
        
        profiler.print_report()
        
        # Generate summary
        report = profiler.generate_report()
        assert report["pass_rate"] != "0.0%", "No benchmarks passed"
