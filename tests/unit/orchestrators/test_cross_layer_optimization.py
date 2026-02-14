# AC_START: AC-WAVE-4-S2-001
"""
Test suite for ENH-087 Track 3: Cross-Layer Optimization.

Tests cross-orchestrator coordination, latency optimization (<100ms),
and resource pooling strategies.

Module: tests/unit/orchestrators/test_cross_layer_optimization.py
Authority: WAVE-4 Stage 2 - ENH-087 Track 3
Coverage Target: ≥98%
"""

import pytest
import time
from typing import Dict, Any, List
from dataclasses import dataclass

# Import modules to test (will be created)
from cortex.orchestrators.optimization.cross_layer_optimizer import (
    CrossLayerOptimizer,
    CoordinationResult,
    LatencyMeasurement,
    ResourcePool,
    OptimizationConfig,
)


class TestCoordinationImprovement:
    """Test suite for cross-orchestrator coordination (10 tests)."""

    def test_coordinator_initialization(self):
        """Coordinator should initialize with default config."""
        optimizer = CrossLayerOptimizer()
        
        assert optimizer is not None
        assert optimizer.config is not None

    def test_coordinate_single_orchestrator(self):
        """Coordination should handle single orchestrator."""
        optimizer = CrossLayerOptimizer()
        
        result = optimizer.coordinate(
            orchestrators=["TDDOrchestrator"],
            operation="implement_feature"
        )
        
        assert result.success
        assert len(result.coordination_plan) == 1

    def test_coordinate_multiple_orchestrators(self):
        """Coordination should sequence multiple orchestrators."""
        optimizer = CrossLayerOptimizer()
        
        result = optimizer.coordinate(
            orchestrators=["IntentRouter", "TDDOrchestrator", "RefactoringOrchestrator"],
            operation="implement_and_refactor"
        )
        
        assert result.success
        assert len(result.coordination_plan) == 3
        assert result.optimization_applied

    def test_coordinate_with_dependencies(self):
        """Coordination should respect orchestrator dependencies."""
        optimizer = CrossLayerOptimizer()
        
        result = optimizer.coordinate(
            orchestrators=["LENSSynthesis", "IntentRouter", "TDDOrchestrator"],
            operation="implement_with_analysis",
            dependencies={
                "IntentRouter": ["LENSSynthesis"],
                "TDDOrchestrator": ["IntentRouter"]
            }
        )
        
        assert result.success
        # Should be ordered: LENS -> IntentRouter -> TDD
        assert result.coordination_plan[0] == "LENSSynthesis"
        assert result.coordination_plan[1] == "IntentRouter"

    def test_coordinate_parallel_execution(self):
        """Coordination should identify parallelizable work."""
        optimizer = CrossLayerOptimizer()
        
        result = optimizer.coordinate(
            orchestrators=["RefactoringOrchestrator", "SecurityOrchestrator"],
            operation="parallel_analysis",
            allow_parallel=True
        )
        
        assert result.success
        assert result.parallel_groups is not None
        assert len(result.parallel_groups) > 0

    def test_coordinate_cyclic_dependency_detection(self):
        """Coordination should detect cyclic dependencies."""
        optimizer = CrossLayerOptimizer()
        
        result = optimizer.coordinate(
            orchestrators=["OrchestratorA", "OrchestratorB"],
            operation="cyclic_test",
            dependencies={
                "OrchestratorA": ["OrchestratorB"],
                "OrchestratorB": ["OrchestratorA"]
            }
        )
        
        assert not result.success
        assert "cyclic" in result.error_message.lower()

    def test_coordinate_optimization_metrics(self):
        """Coordination should provide optimization metrics."""
        optimizer = CrossLayerOptimizer()
        
        result = optimizer.coordinate(
            orchestrators=["MasterOrchestrator", "IntentRouter"],
            operation="routing"
        )
        
        assert result.success
        assert "metrics" in result.metadata
        assert result.metadata["metrics"]["coordination_time_ms"] is not None

    def test_coordinate_caching_strategy(self):
        """Coordination should cache frequently used plans."""
        optimizer = CrossLayerOptimizer()
        
        # First call
        result1 = optimizer.coordinate(
            orchestrators=["TDDOrchestrator"],
            operation="implement"
        )
        
        # Second identical call (should be cached)
        result2 = optimizer.coordinate(
            orchestrators=["TDDOrchestrator"],
            operation="implement"
        )
        
        assert result1.success and result2.success
        assert result2.from_cache

    def test_coordinate_failure_handling(self):
        """Coordination should handle orchestrator failures gracefully."""
        optimizer = CrossLayerOptimizer()
        
        result = optimizer.coordinate(
            orchestrators=["NonExistentOrchestrator"],
            operation="test"
        )
        
        assert not result.success
        assert result.error_message is not None

    def test_coordinate_empty_orchestrators(self):
        """Coordination should handle empty orchestrator list."""
        optimizer = CrossLayerOptimizer()
        
        result = optimizer.coordinate(
            orchestrators=[],
            operation="empty_test"
        )
        
        assert not result.success
        assert "empty" in result.error_message.lower() or "no orchestrators" in result.error_message.lower()


class TestLatencyOptimization:
    """Test suite for latency optimization (12 tests)."""

    def test_measure_latency_simple_operation(self):
        """Latency measurement for simple operation."""
        optimizer = CrossLayerOptimizer()
        
        measurement = optimizer.measure_latency(
            operation_name="simple_routing",
            operation_fn=lambda: time.sleep(0.01)
        )
        
        assert measurement.success
        assert measurement.latency_ms >= 10  # At least 10ms
        assert measurement.latency_ms < 100  # Less than 100ms

    def test_measure_latency_target_achievement(self):
        """Latency measurement should compare against target."""
        optimizer = CrossLayerOptimizer(
            config=OptimizationConfig(latency_target_ms=50)
        )
        
        # Fast operation (should meet target)
        measurement = optimizer.measure_latency(
            operation_name="fast_op",
            operation_fn=lambda: time.sleep(0.01)
        )
        
        assert measurement.success
        assert measurement.meets_target

    def test_measure_latency_target_miss(self):
        """Latency measurement should detect target misses."""
        optimizer = CrossLayerOptimizer(
            config=OptimizationConfig(latency_target_ms=10)
        )
        
        # Slow operation (should miss target)
        measurement = optimizer.measure_latency(
            operation_name="slow_op",
            operation_fn=lambda: time.sleep(0.02)
        )
        
        assert measurement.success
        assert not measurement.meets_target

    def test_optimize_latency_caching(self):
        """Latency optimization through result caching."""
        optimizer = CrossLayerOptimizer()
        
        call_count = 0
        def expensive_operation():
            nonlocal call_count
            call_count += 1
            time.sleep(0.01)
            return "result"
        
        # First call (no cache)
        result1 = optimizer.optimize_latency(
            operation_name="expensive",
            operation_fn=expensive_operation,
            enable_cache=True
        )
        
        # Second call (should use cache)
        result2 = optimizer.optimize_latency(
            operation_name="expensive",
            operation_fn=expensive_operation,
            enable_cache=True
        )
        
        assert result1 == result2
        assert call_count == 1  # Function called only once

    def test_optimize_latency_parallelization(self):
        """Latency optimization through parallelization."""
        optimizer = CrossLayerOptimizer()
        
        operations = [
            lambda: time.sleep(0.01),
            lambda: time.sleep(0.01),
            lambda: time.sleep(0.01),
        ]
        
        start = time.time()
        results = optimizer.optimize_latency_parallel(operations)
        duration = time.time() - start
        
        # Parallel execution should be faster than sequential (3 * 10ms = 30ms)
        assert len(results) == 3
        assert duration < 0.05  # Should complete in < 50ms (parallel overhead)

    def test_optimize_latency_timeout_handling(self):
        """Latency optimization should enforce timeouts."""
        optimizer = CrossLayerOptimizer(
            config=OptimizationConfig(timeout_ms=50)
        )
        
        def slow_operation():
            time.sleep(0.1)  # 100ms (exceeds timeout)
            return "result"
        
        result = optimizer.optimize_latency(
            operation_name="timeout_test",
            operation_fn=slow_operation
        )
        
        assert result is None or "timeout" in str(result).lower()

    def test_latency_profiling(self):
        """Latency profiler should track operation times."""
        optimizer = CrossLayerOptimizer()
        
        # Perform several operations
        for i in range(3):
            optimizer.measure_latency(
                operation_name=f"op_{i}",
                operation_fn=lambda: time.sleep(0.001 * (i + 1))
            )
        
        profile = optimizer.get_latency_profile()
        
        assert len(profile) == 3
        assert all("latency_ms" in op for op in profile)

    def test_latency_percentile_calculation(self):
        """Latency optimizer should calculate percentiles."""
        optimizer = CrossLayerOptimizer()
        
        # Generate measurements
        for i in range(10):
            optimizer.measure_latency(
                operation_name="test_op",
                operation_fn=lambda i=i: time.sleep(0.001 * i)
            )
        
        stats = optimizer.get_latency_stats("test_op")
        
        assert "p50" in stats
        assert "p95" in stats
        assert "p99" in stats

    def test_latency_regression_detection(self):
        """Latency optimizer should detect regressions."""
        optimizer = CrossLayerOptimizer()
        
        # Establish baseline
        for _ in range(5):
            optimizer.measure_latency(
                operation_name="stable_op",
                operation_fn=lambda: time.sleep(0.01)
            )
        
        # Introduce regression
        regression_detected = optimizer.detect_regression(
            operation_name="stable_op",
            new_latency_ms=50  # Significantly slower
        )
        
        assert regression_detected

    def test_latency_optimization_recommendation(self):
        """Latency optimizer should provide recommendations."""
        optimizer = CrossLayerOptimizer()
        
        # Slow operation
        optimizer.measure_latency(
            operation_name="slow_routing",
            operation_fn=lambda: time.sleep(0.15)
        )
        
        recommendations = optimizer.get_optimization_recommendations("slow_routing")
        
        assert len(recommendations) > 0
        assert any("cache" in rec.lower() or "parallel" in rec.lower() for rec in recommendations)

    def test_latency_monitoring_integration(self):
        """Latency optimizer should integrate with monitoring."""
        optimizer = CrossLayerOptimizer()
        
        measurement = optimizer.measure_latency(
            operation_name="monitored_op",
            operation_fn=lambda: "result",
            enable_monitoring=True
        )
        
        assert measurement.success
        assert "monitoring_id" in measurement.metadata

    def test_latency_comparison_baseline(self):
        """Latency optimizer should compare against baseline."""
        optimizer = CrossLayerOptimizer()
        
        # Set baseline
        optimizer.set_baseline("operation_x", baseline_ms=20)
        
        # Measure current
        measurement = optimizer.measure_latency(
            operation_name="operation_x",
            operation_fn=lambda: time.sleep(0.015)
        )
        
        assert measurement.success
        assert measurement.vs_baseline is not None


class TestResourcePooling:
    """Test suite for resource pooling (8 tests)."""

    def test_resource_pool_initialization(self):
        """Resource pool should initialize with config."""
        optimizer = CrossLayerOptimizer()
        
        pool = optimizer.create_resource_pool(
            resource_type="orchestrator_instances",
            pool_size=5
        )
        
        assert pool is not None
        assert pool.size == 5

    def test_resource_pool_acquire_release(self):
        """Resource pool should support acquire/release."""
        optimizer = CrossLayerOptimizer()
        
        pool = optimizer.create_resource_pool(
            resource_type="connections",
            pool_size=3
        )
        
        # Acquire resource
        resource = pool.acquire()
        assert resource is not None
        
        # Release resource
        success = pool.release(resource)
        assert success

    def test_resource_pool_exhaustion(self):
        """Resource pool should handle exhaustion."""
        optimizer = CrossLayerOptimizer()
        
        pool = optimizer.create_resource_pool(
            resource_type="workers",
            pool_size=2
        )
        
        # Acquire all resources
        r1 = pool.acquire()
        r2 = pool.acquire()
        
        # Try to acquire when exhausted
        r3 = pool.acquire(block=False)
        
        assert r1 is not None
        assert r2 is not None
        assert r3 is None

    def test_resource_pool_metrics(self):
        """Resource pool should track metrics."""
        optimizer = CrossLayerOptimizer()
        
        pool = optimizer.create_resource_pool(
            resource_type="cache_entries",
            pool_size=10
        )
        
        # Perform operations
        r1 = pool.acquire()
        r2 = pool.acquire()
        pool.release(r1)
        
        metrics = pool.get_metrics()
        
        assert "total_acquires" in metrics
        assert "total_releases" in metrics
        assert "current_usage" in metrics

    def test_resource_pool_cleanup(self):
        """Resource pool should support cleanup."""
        optimizer = CrossLayerOptimizer()
        
        pool = optimizer.create_resource_pool(
            resource_type="temp_objects",
            pool_size=5
        )
        
        # Acquire some resources
        r1 = pool.acquire()
        r2 = pool.acquire()
        
        # Cleanup pool
        pool.cleanup()
        
        assert pool.size == 0

    def test_resource_pool_reuse_rate(self):
        """Resource pool should maximize reuse."""
        optimizer = CrossLayerOptimizer()
        
        pool = optimizer.create_resource_pool(
            resource_type="analyzers",
            pool_size=3
        )
        
        # Acquire and release multiple times
        for _ in range(10):
            r = pool.acquire()
            pool.release(r)
        
        metrics = pool.get_metrics()
        reuse_rate = metrics["total_acquires"] / pool.size
        
        assert reuse_rate > 1  # Each resource used multiple times

    def test_resource_pool_health_check(self):
        """Resource pool should support health checks."""
        optimizer = CrossLayerOptimizer()
        
        pool = optimizer.create_resource_pool(
            resource_type="services",
            pool_size=5
        )
        
        health = pool.health_check()
        
        assert "healthy_count" in health
        assert "unhealthy_count" in health

    def test_resource_pool_dynamic_sizing(self):
        """Resource pool should support dynamic resizing."""
        optimizer = CrossLayerOptimizer()
        
        pool = optimizer.create_resource_pool(
            resource_type="buffers",
            pool_size=3,
            allow_dynamic=True
        )
        
        # Trigger expansion
        pool.resize(new_size=5)
        
        assert pool.size == 5


# AC_COMPLETE: AC-WAVE-4-S2-001 (30 tests - RED phase complete)
