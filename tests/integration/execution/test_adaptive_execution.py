"""
Tests for Adaptive Execution Engine and related components.

This module provides comprehensive tests for the adaptive execution system,
including the AdaptiveExecutionEngine, PerformanceMetricsCollector,
StrategySelector, and FeedbackLoop.
"""

import pytest
from datetime import datetime, timedelta
from typing import Dict, List, Any
from unittest.mock import Mock, patch

from cortex.execution.adaptive_execution_engine import (
    AdaptiveExecutionEngine,
    ExecutionStrategy,
    ExecutionContext,
)
from cortex.execution.performance_metrics import (
    PerformanceMetricsCollector,
    PerformanceMetrics,
)
from cortex.execution.strategy_selector import StrategySelector
from cortex.execution.feedback_loop import FeedbackLoop


class TestAdaptiveExecutionEngine:
    """Tests for AdaptiveExecutionEngine learning and adaptation."""

    def test_engine_initializes_correctly(self) -> None:
        """Test AdaptiveExecutionEngine initialization."""
        engine = AdaptiveExecutionEngine()
        assert engine is not None
        assert engine.execution_history == []
        assert engine.current_strategy == ExecutionStrategy.SEQUENTIAL

    def test_engine_learns_from_execution_history(self) -> None:
        """Test engine learns from execution patterns."""
        engine = AdaptiveExecutionEngine()
        
        # Record successful sequential executions
        for i in range(5):
            context = ExecutionContext(
                task_id=f"task_{i}",
                strategy=ExecutionStrategy.SEQUENTIAL,
                duration=1.5,
                success=True,
                timestamp=datetime.now(),
            )
            engine.record_execution(context)
        
        assert len(engine.execution_history) == 5
        assert all(c.success for c in engine.execution_history)

    def test_engine_adapts_strategy_based_on_patterns(self) -> None:
        """Test engine adapts strategy based on performance patterns."""
        engine = AdaptiveExecutionEngine()
        
        # Record slower sequential executions
        for i in range(3):
            context = ExecutionContext(
                task_id=f"seq_{i}",
                strategy=ExecutionStrategy.SEQUENTIAL,
                duration=5.0,
                success=True,
                timestamp=datetime.now(),
            )
            engine.record_execution(context)
        
        # Record faster parallel executions
        for i in range(3):
            context = ExecutionContext(
                task_id=f"par_{i}",
                strategy=ExecutionStrategy.PARALLEL,
                duration=2.0,
                success=True,
                timestamp=datetime.now(),
            )
            engine.record_execution(context)
        
        # Engine should learn that parallel is faster
        adapted_strategy = engine.recommend_strategy()
        assert adapted_strategy == ExecutionStrategy.PARALLEL

    def test_engine_handles_failed_executions(self) -> None:
        """Test engine records and learns from failed executions."""
        engine = AdaptiveExecutionEngine()
        
        # Record failed execution
        context = ExecutionContext(
            task_id="failing_task",
            strategy=ExecutionStrategy.PARALLEL,
            duration=3.0,
            success=False,
            timestamp=datetime.now(),
        )
        engine.record_execution(context)
        
        assert len(engine.execution_history) == 1
        assert not engine.execution_history[0].success

    def test_engine_retrieves_execution_statistics(self) -> None:
        """Test engine provides execution statistics."""
        engine = AdaptiveExecutionEngine()
        
        # Record mixed executions
        for i in range(3):
            context = ExecutionContext(
                task_id=f"task_{i}",
                strategy=ExecutionStrategy.SEQUENTIAL,
                duration=2.0 + i,
                success=i < 2,
                timestamp=datetime.now(),
            )
            engine.record_execution(context)
        
        stats = engine.get_statistics()
        assert stats["total_executions"] == 3
        assert stats["successful_executions"] == 2
        assert stats["failed_executions"] == 1
        assert stats["avg_duration"] > 2.0


class TestPerformanceMetricsCollector:
    """Tests for PerformanceMetricsCollector."""

    def test_collector_initializes_correctly(self) -> None:
        """Test PerformanceMetricsCollector initialization."""
        collector = PerformanceMetricsCollector()
        assert collector is not None
        assert len(collector.metrics_history) == 0

    def test_collector_records_latency_metrics(self) -> None:
        """Test collector records p50, p95, p99 latencies."""
        collector = PerformanceMetricsCollector()
        
        # Record latencies
        latencies = [1.0, 2.0, 3.0, 4.0, 5.0]
        for lat in latencies:
            collector.record_latency(lat)
        
        metrics = collector.compute_metrics()
        assert metrics.p50_latency > 0
        assert metrics.p95_latency >= metrics.p50_latency
        assert metrics.p99_latency >= metrics.p95_latency

    def test_collector_computes_error_rates(self) -> None:
        """Test collector computes error rates correctly."""
        collector = PerformanceMetricsCollector()
        
        # Record 10 operations: 8 successful, 2 failed
        for i in range(8):
            collector.record_success()
        for i in range(2):
            collector.record_error()
        
        metrics = collector.compute_metrics()
        assert metrics.error_rate == 0.2
        assert metrics.success_rate == 0.8

    def test_collector_computes_success_percentage(self) -> None:
        """Test collector computes success percentage."""
        collector = PerformanceMetricsCollector()
        
        # Record 100 operations: 85 successful
        for i in range(85):
            collector.record_success()
        for i in range(15):
            collector.record_error()
        
        metrics = collector.compute_metrics()
        assert metrics.success_percentage == 85.0

    def test_collector_aggregates_metrics_over_time(self) -> None:
        """Test collector aggregates metrics correctly."""
        collector = PerformanceMetricsCollector()
        
        # Record metrics for first period
        for i in range(5):
            collector.record_latency(2.0)
            collector.record_success()
        
        first_metrics = collector.compute_metrics()
        
        # Record metrics for second period
        for i in range(5):
            collector.record_latency(3.0)
            collector.record_success()
        
        second_metrics = collector.compute_metrics()
        assert second_metrics.p50_latency >= first_metrics.p50_latency


class TestStrategySelector:
    """Tests for StrategySelector."""

    def test_selector_initializes_correctly(self) -> None:
        """Test StrategySelector initialization."""
        selector = StrategySelector()
        assert selector is not None
        assert selector.default_strategy == ExecutionStrategy.SEQUENTIAL

    def test_selector_recommends_based_on_metrics(self) -> None:
        """Test selector recommends strategy based on metrics."""
        selector = StrategySelector()
        metrics = PerformanceMetrics(
            p50_latency=2.0,
            p95_latency=3.0,
            p99_latency=5.0,
            error_rate=0.1,
            success_rate=0.9,
            success_percentage=90.0,
            total_operations=100,
        )
        
        recommendation = selector.recommend(metrics)
        assert recommendation in [
            ExecutionStrategy.SEQUENTIAL,
            ExecutionStrategy.PARALLEL,
            ExecutionStrategy.ASYNC,
        ]

    def test_selector_favors_parallel_for_low_error_rates(self) -> None:
        """Test selector favors parallel execution for reliable systems."""
        selector = StrategySelector()
        metrics = PerformanceMetrics(
            p50_latency=3.0,
            p95_latency=4.0,
            p99_latency=5.0,
            error_rate=0.01,
            success_rate=0.99,
            success_percentage=99.0,
            total_operations=1000,
        )
        
        recommendation = selector.recommend(metrics)
        assert recommendation == ExecutionStrategy.PARALLEL

    def test_selector_recommends_async_for_long_operations(self) -> None:
        """Test selector recommends async for long-running operations."""
        selector = StrategySelector()
        metrics = PerformanceMetrics(
            p50_latency=10.0,
            p95_latency=20.0,
            p99_latency=30.0,
            error_rate=0.05,
            success_rate=0.95,
            success_percentage=95.0,
            total_operations=500,
        )
        
        recommendation = selector.recommend(metrics)
        assert recommendation in [ExecutionStrategy.ASYNC, ExecutionStrategy.PARALLEL]

    def test_selector_recommends_sequential_for_high_error_rates(self) -> None:
        """Test selector recommends sequential for unreliable systems."""
        selector = StrategySelector()
        metrics = PerformanceMetrics(
            p50_latency=1.0,
            p95_latency=2.0,
            p99_latency=3.0,
            error_rate=0.3,
            success_rate=0.7,
            success_percentage=70.0,
            total_operations=100,
        )
        
        recommendation = selector.recommend(metrics)
        assert recommendation == ExecutionStrategy.SEQUENTIAL


class TestFeedbackLoop:
    """Tests for FeedbackLoop."""

    def test_feedback_loop_initializes_correctly(self) -> None:
        """Test FeedbackLoop initialization."""
        loop = FeedbackLoop()
        assert loop is not None
        assert len(loop.feedback_history) == 0

    def test_feedback_loop_records_outcomes(self) -> None:
        """Test feedback loop records execution outcomes."""
        loop = FeedbackLoop()
        
        outcome = {
            "strategy": ExecutionStrategy.PARALLEL,
            "duration": 2.5,
            "success": True,
            "improvement": 0.15,
        }
        loop.record_outcome(outcome)
        
        assert len(loop.feedback_history) == 1
        assert loop.feedback_history[0] == outcome

    def test_feedback_loop_computes_improvement_over_time(self) -> None:
        """Test feedback loop computes improvement metrics."""
        loop = FeedbackLoop()
        
        # Record initial outcomes
        for i in range(3):
            outcome = {
                "strategy": ExecutionStrategy.SEQUENTIAL,
                "duration": 5.0,
                "success": True,
                "improvement": 0.0,
            }
            loop.record_outcome(outcome)
        
        # Record improved outcomes
        for i in range(3):
            outcome = {
                "strategy": ExecutionStrategy.PARALLEL,
                "duration": 2.0,
                "success": True,
                "improvement": 0.6,
            }
            loop.record_outcome(outcome)
        
        improvement = loop.get_cumulative_improvement()
        assert improvement > 0

    def test_feedback_loop_suggests_strategy_updates(self) -> None:
        """Test feedback loop suggests strategy updates."""
        loop = FeedbackLoop()
        
        # Record many successful parallel executions
        for i in range(10):
            outcome = {
                "strategy": ExecutionStrategy.PARALLEL,
                "duration": 1.5,
                "success": True,
                "improvement": 0.5,
            }
            loop.record_outcome(outcome)
        
        suggestion = loop.get_strategy_suggestion()
        assert suggestion is not None
        assert suggestion.recommended_strategy == ExecutionStrategy.PARALLEL

    def test_feedback_loop_adapts_to_failures(self) -> None:
        """Test feedback loop adapts to execution failures."""
        loop = FeedbackLoop()
        
        # Record failures with parallel strategy
        for i in range(5):
            outcome = {
                "strategy": ExecutionStrategy.PARALLEL,
                "duration": 3.0,
                "success": False,
                "improvement": -0.3,
            }
            loop.record_outcome(outcome)
        
        suggestion = loop.get_strategy_suggestion()
        if suggestion:
            # Should suggest moving away from parallel after failures
            assert suggestion.recommended_strategy != ExecutionStrategy.PARALLEL


class TestAdaptiveExecutionIntegration:
    """Integration tests for the adaptive execution system."""

    def test_end_to_end_execution_flow(self) -> None:
        """Test complete adaptive execution flow."""
        engine = AdaptiveExecutionEngine()
        collector = PerformanceMetricsCollector()
        selector = StrategySelector()
        feedback = FeedbackLoop()
        
        # Simulate execution cycle
        for i in range(5):
            # Record execution
            context = ExecutionContext(
                task_id=f"task_{i}",
                strategy=ExecutionStrategy.SEQUENTIAL,
                duration=2.5,
                success=True,
                timestamp=datetime.now(),
            )
            engine.record_execution(context)
            collector.record_latency(2.5)
            collector.record_success()
            
            # Get metrics and recommendations
            metrics = collector.compute_metrics()
            strategy = selector.recommend(metrics)
            
            # Record feedback
            outcome = {
                "strategy": strategy,
                "duration": 2.5,
                "success": True,
                "improvement": 0.1,
            }
            feedback.record_outcome(outcome)
        
        # Verify system state
        stats = engine.get_statistics()
        assert stats["total_executions"] == 5
        assert stats["successful_executions"] == 5
        
        improvement = feedback.get_cumulative_improvement()
        assert improvement >= 0

    def test_adaptive_system_handles_performance_changes(self) -> None:
        """Test system adapts to changing performance characteristics."""
        engine = AdaptiveExecutionEngine()
        
        # Phase 1: Fast sequential execution
        for i in range(3):
            context = ExecutionContext(
                task_id=f"seq_{i}",
                strategy=ExecutionStrategy.SEQUENTIAL,
                duration=1.0,
                success=True,
                timestamp=datetime.now(),
            )
            engine.record_execution(context)
        
        strategy_1 = engine.recommend_strategy()
        
        # Phase 2: Slow sequential, fast parallel
        for i in range(3):
            context = ExecutionContext(
                task_id=f"seq_slow_{i}",
                strategy=ExecutionStrategy.SEQUENTIAL,
                duration=5.0,
                success=True,
                timestamp=datetime.now(),
            )
            engine.record_execution(context)
            
            context = ExecutionContext(
                task_id=f"par_fast_{i}",
                strategy=ExecutionStrategy.PARALLEL,
                duration=1.5,
                success=True,
                timestamp=datetime.now(),
            )
            engine.record_execution(context)
        
        strategy_2 = engine.recommend_strategy()
        
        # Strategy should adapt to new patterns
        assert strategy_2 in [
            ExecutionStrategy.PARALLEL,
            ExecutionStrategy.ASYNC,
        ]

    def test_full_workflow_with_metrics_aggregation(self) -> None:
        """Test full workflow with metrics aggregation."""
        collector = PerformanceMetricsCollector()
        
        # Record diverse metrics
        latencies = [1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 10.0]
        for lat in latencies:
            collector.record_latency(lat)
        
        # Record 90% success rate
        for i in range(90):
            collector.record_success()
        for i in range(10):
            collector.record_error()
        
        metrics = collector.compute_metrics()
        assert metrics.success_percentage == 90.0
        assert metrics.p50_latency > 0
        assert metrics.p95_latency >= metrics.p50_latency
        assert metrics.p99_latency >= metrics.p95_latency or metrics.p99_latency == metrics.p95_latency
