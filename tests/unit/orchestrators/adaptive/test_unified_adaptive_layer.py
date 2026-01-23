"""Comprehensive test suite for UnifiedAdaptiveLayer.

Tests cover all 6 consolidated components:
- Execution modes (FAST, BALANCED, THOROUGH)
- Strategy selection
- Performance optimization
- Load balancing
- Resource management
- Failover and recovery
"""

import pytest
from datetime import datetime
from cortex.orchestrators.adaptive.unified_adaptive_layer import (
    UnifiedAdaptiveLayer,
    ExecutionMode,
    StrategyType,
    ExecutionMetrics,
    PerformanceProfile,
    FailoverContext,
    ResourceAllocation,
)


class TestUnifiedAdaptiveLayerInitialization:
    """Test initialization and configuration."""
    
    def test_initialization(self):
        """Test UnifiedAdaptiveLayer initialization."""
        adapter = UnifiedAdaptiveLayer()
        assert adapter.get_execution_mode() == ExecutionMode.BALANCED
        assert len(adapter._mode_configs) == 3
        assert len(adapter._strategy_configs) == 3
    
    def test_default_mode_configuration(self):
        """Test default mode configuration."""
        adapter = UnifiedAdaptiveLayer()
        config = adapter.get_mode_config(ExecutionMode.BALANCED)
        assert config.mode == ExecutionMode.BALANCED
        assert config.timeout_seconds == 5.0
        assert config.validation_level == 0.6
        assert config.enable_caching is True
    
    def test_all_modes_configured(self):
        """Test that all execution modes are configured."""
        adapter = UnifiedAdaptiveLayer()
        for mode in ExecutionMode:
            config = adapter.get_mode_config(mode)
            assert config.mode == mode
            assert config.timeout_seconds > 0
            assert 0.0 <= config.validation_level <= 1.0


class TestExecutionModeManagement:
    """Test execution mode switching and configuration."""
    
    def test_set_execution_mode(self):
        """Test setting execution mode."""
        adapter = UnifiedAdaptiveLayer()
        adapter.set_execution_mode(ExecutionMode.FAST)
        assert adapter.get_execution_mode() == ExecutionMode.FAST
    
    def test_mode_transitions(self):
        """Test transitions between modes."""
        adapter = UnifiedAdaptiveLayer()
        for mode in ExecutionMode:
            adapter.set_execution_mode(mode)
            assert adapter.get_execution_mode() == mode
    
    def test_get_mode_config_current_mode(self):
        """Test getting current mode config."""
        adapter = UnifiedAdaptiveLayer()
        adapter.set_execution_mode(ExecutionMode.THOROUGH)
        config = adapter.get_mode_config()
        assert config.mode == ExecutionMode.THOROUGH
        assert config.timeout_seconds == 15.0


class TestTaskExecution:
    """Test task execution with different modes."""
    
    def test_execute_simple_task(self):
        """Test executing a simple task."""
        adapter = UnifiedAdaptiveLayer()
        task = {"name": "test", "input": "test_data"}
        result = adapter.execute_in_mode(task)
        
        assert result["status"] == "success"
        assert result["task"] == task
        assert result["mode"] == "balanced"
    
    def test_execute_with_all_modes(self):
        """Test execution with all modes."""
        adapter = UnifiedAdaptiveLayer()
        task = {"name": "test"}
        
        for mode in ExecutionMode:
            adapter.set_execution_mode(mode)
            result = adapter.execute_in_mode(task)
            assert result["mode"] == mode.value
    
    def test_execute_updates_statistics(self):
        """Test that execution updates statistics."""
        adapter = UnifiedAdaptiveLayer()
        assert adapter._stats["total_executions"] == 0
        
        adapter.execute_in_mode({"test": "task"})
        assert adapter._stats["total_executions"] == 1
        assert adapter._stats["successful_executions"] == 1
    
    def test_execute_invalid_task_raises_error(self):
        """Test that invalid task raises error."""
        adapter = UnifiedAdaptiveLayer()
        adapter.set_execution_mode(ExecutionMode.THOROUGH)
        
        with pytest.raises(ValueError):
            adapter.execute_in_mode(None)
    
    def test_execute_with_retries(self):
        """Test execution with retry configuration."""
        adapter = UnifiedAdaptiveLayer()
        adapter.set_execution_mode(ExecutionMode.BALANCED)
        
        task = {"test": "with_retries"}
        result = adapter.execute_in_mode(task)
        assert result["status"] == "success"


class TestStrategySelection:
    """Test strategy selection based on task characteristics."""
    
    def test_select_strategy_low_complexity(self):
        """Test strategy selection for low complexity tasks."""
        adapter = UnifiedAdaptiveLayer()
        task = {"complexity": "low"}
        strategy = adapter.select_strategy(task)
        assert strategy == StrategyType.FAST
    
    def test_select_strategy_medium_complexity(self):
        """Test strategy selection for medium complexity tasks."""
        adapter = UnifiedAdaptiveLayer()
        task = {"complexity": "medium", "deadline_seconds": 5}
        strategy = adapter.select_strategy(task)
        assert strategy == StrategyType.BALANCED
    
    def test_select_strategy_high_complexity(self):
        """Test strategy selection for high complexity tasks."""
        adapter = UnifiedAdaptiveLayer()
        task = {"complexity": "high", "required_certainty": 0.95}
        strategy = adapter.select_strategy(task)
        assert strategy == StrategyType.THOROUGH
    
    def test_get_strategy_recommendations(self):
        """Test getting strategy recommendations."""
        adapter = UnifiedAdaptiveLayer()
        task = {"complexity": "medium"}
        recommendations = adapter.get_strategy_recommendations(task)
        
        assert len(recommendations) == 3
        assert "FAST" in recommendations
        assert "BALANCED" in recommendations
        assert "THOROUGH" in recommendations
    
    def test_apply_strategy(self):
        """Test applying a strategy to task."""
        adapter = UnifiedAdaptiveLayer()
        task = {"test": "strategy_application"}
        
        result = adapter.apply_strategy(task, StrategyType.FAST)
        assert result["status"] == "success"
        assert "strategy" in result["context"]
        assert result["context"]["strategy"] == "FAST"


class TestComplexityAnalysis:
    """Test task complexity analysis."""
    
    def test_analyze_explicit_complexity(self):
        """Test analysis of explicitly specified complexity."""
        adapter = UnifiedAdaptiveLayer()
        
        assert adapter._analyze_task_complexity({"complexity": "low"}) == "low"
        assert adapter._analyze_task_complexity({"complexity": "medium"}) == "medium"
        assert adapter._analyze_task_complexity({"complexity": "high"}) == "high"
    
    def test_analyze_inferred_complexity(self):
        """Test complexity inference from task characteristics."""
        adapter = UnifiedAdaptiveLayer()
        
        # Large input = high complexity
        large_task = {"inputs": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]}
        assert adapter._analyze_task_complexity(large_task) == "high"
        
        # Medium input = medium complexity
        medium_task = {"inputs": [1, 2, 3, 4, 5, 6, 7]}
        assert adapter._analyze_task_complexity(medium_task) == "medium"
        
        # Small input = low complexity
        small_task = {"inputs": [1, 2]}
        assert adapter._analyze_task_complexity(small_task) == "low"


class TestPerformanceMetrics:
    """Test performance metrics collection and analysis."""
    
    def test_collect_metrics(self):
        """Test collecting execution metrics."""
        adapter = UnifiedAdaptiveLayer()
        adapter.collect_metrics(
            orchestrator="TestOrchestrator",
            task_type="test",
            duration_seconds=1.5,
            memory_mb=256,
            success=True,
        )
        
        assert "TestOrchestrator" in adapter._performance_profiles
        profile = adapter._performance_profiles["TestOrchestrator"]
        assert len(profile.executions) == 1
        assert profile.total_executions == 1
        assert profile.successful_executions == 1
    
    def test_performance_profile_statistics(self):
        """Test performance profile statistics calculation."""
        adapter = UnifiedAdaptiveLayer()
        
        # Collect multiple metrics
        for i in range(3):
            adapter.collect_metrics(
                orchestrator="Orch1",
                task_type="test",
                duration_seconds=1.0 + i,
                memory_mb=100 + i * 50,
                success=True,
            )
        
        profile = adapter._performance_profiles["Orch1"]
        assert profile.total_executions == 3
        assert profile.successful_executions == 3
        assert profile.success_rate == 1.0
        assert profile.average_duration > 1.0
    
    def test_optimize_execution(self):
        """Test optimization suggestions generation."""
        adapter = UnifiedAdaptiveLayer()
        metrics = ExecutionMetrics(
            orchestrator="TestOrch",
            task_type="test",
            duration_seconds=15.0,
            memory_mb=600,
            success=True,
        )
        
        suggestions = adapter.optimize_execution({"test": "task"}, metrics)
        assert "optimizations" in suggestions
        assert len(suggestions["optimizations"]) > 0
    
    def test_get_optimization_suggestions(self):
        """Test getting optimization suggestions for orchestrator."""
        adapter = UnifiedAdaptiveLayer()
        
        # No profile = no suggestions
        suggestions = adapter.get_optimization_suggestions("NoProfile")
        assert suggestions == []
        
        # Profile with high success rate = few suggestions
        adapter.collect_metrics(
            orchestrator="HighPerformer",
            task_type="test",
            duration_seconds=2.0,
            memory_mb=200,
            success=True,
        )
        suggestions = adapter.get_optimization_suggestions("HighPerformer")
        assert len(suggestions) == 0


class TestLoadBalancing:
    """Test load balancing and resource allocation."""
    
    def test_allocate_resources_low_complexity(self):
        """Test resource allocation for low complexity task."""
        adapter = UnifiedAdaptiveLayer()
        task = {"complexity": "low"}
        allocations = adapter.allocate_resources(task)
        
        assert len(allocations) == 1
        assert "memory" in allocations
    
    def test_allocate_resources_high_complexity(self):
        """Test resource allocation for high complexity task."""
        adapter = UnifiedAdaptiveLayer()
        task = {"complexity": "high"}
        allocations = adapter.allocate_resources(task)
        
        assert len(allocations) == 2
        assert "cpu" in allocations
        assert "memory" in allocations
    
    def test_distribute_load(self):
        """Test load distribution across orchestrators."""
        adapter = UnifiedAdaptiveLayer()
        tasks = [{"task": f"t{i}"} for i in range(9)]
        
        distribution = adapter.distribute_load(tasks)
        assert len(distribution) == 3  # 9 tasks / 3 orchestrators
        assert sum(distribution.values()) == 9
    
    def test_get_load_status(self):
        """Test getting load status."""
        adapter = UnifiedAdaptiveLayer()
        tasks = [{"task": f"t{i}"} for i in range(5)]
        adapter.distribute_load(tasks)
        
        status = adapter.get_load_status()
        assert "timestamp" in status
        assert "orchestrator_load" in status
        assert len(status["orchestrator_load"]) > 0


class TestResourceManagement:
    """Test resource lifecycle management."""
    
    def test_track_resource(self):
        """Test resource tracking."""
        adapter = UnifiedAdaptiveLayer()
        allocation = ResourceAllocation(
            resource_id="res1",
            resource_type="Memory",
            quantity=512,
            unit="MB",
        )
        
        adapter.track_resource("res1", allocation)
        assert "res1" in adapter._resource_allocations
    
    def test_release_resource(self):
        """Test resource release."""
        adapter = UnifiedAdaptiveLayer()
        allocation = ResourceAllocation(
            resource_id="res1",
            resource_type="Memory",
            quantity=512,
            unit="MB",
        )
        
        adapter.track_resource("res1", allocation)
        adapter.release_resource("res1")
        
        assert adapter._resource_allocations["res1"].release_at is not None
    
    def test_cleanup_all_resources(self):
        """Test cleanup of all resources."""
        adapter = UnifiedAdaptiveLayer()
        
        # Create multiple resources
        for i in range(3):
            allocation = ResourceAllocation(
                resource_id=f"res{i}",
                resource_type="Memory",
                quantity=512,
                unit="MB",
            )
            adapter.track_resource(f"res{i}", allocation)
        
        cleaned = adapter.cleanup_all_resources()
        assert cleaned == 3


class TestFailoverAndRecovery:
    """Test failover and recovery strategies."""
    
    def test_register_failover_handler(self):
        """Test registering failover handler."""
        adapter = UnifiedAdaptiveLayer()
        
        def handler(context: FailoverContext) -> bool:
            return True
        
        adapter.register_failover_handler(handler)
        assert len(adapter._failover_handlers) == 1
    
    def test_register_recovery_strategy(self):
        """Test registering recovery strategy."""
        adapter = UnifiedAdaptiveLayer()
        
        def strategy(context: FailoverContext):
            return {"recovered": True}
        
        adapter.register_recovery_strategy("timeout", strategy)
        assert "timeout" in adapter._recovery_strategies
    
    def test_trigger_failover(self):
        """Test triggering failover."""
        adapter = UnifiedAdaptiveLayer()
        context = FailoverContext(
            failure_type="timeout",
            failed_component="orchestrator1",
            original_task={"test": "task"},
            error_message="Execution timeout",
        )
        
        adapter.trigger_failover(context)
        assert adapter._stats["failovers_triggered"] == 1
    
    def test_trigger_failover_with_recovery(self):
        """Test failover with recovery strategy."""
        adapter = UnifiedAdaptiveLayer()
        
        def recovery(context: FailoverContext):
            return {"status": "recovered"}
        
        adapter.register_recovery_strategy("timeout", recovery)
        
        context = FailoverContext(
            failure_type="timeout",
            failed_component="orch1",
            original_task={"test": "task"},
            error_message="Timeout occurred",
        )
        
        result = adapter.trigger_failover(context)
        assert result is not None
    
    def test_get_recovery_options(self):
        """Test getting recovery options."""
        adapter = UnifiedAdaptiveLayer()
        
        def strategy(context: FailoverContext):
            return True
        
        adapter.register_recovery_strategy("timeout", strategy)
        adapter.register_failover_handler(lambda ctx: True)
        
        context = FailoverContext(
            failure_type="timeout",
            failed_component="orch1",
            original_task={},
            error_message="Timeout",
        )
        
        options = adapter.get_recovery_options(context)
        assert len(options) > 0
        assert any("recovery strategy" in opt for opt in options)


class TestStatisticsAndMonitoring:
    """Test statistics collection and monitoring."""
    
    def test_get_statistics(self):
        """Test getting execution statistics."""
        adapter = UnifiedAdaptiveLayer()
        adapter.execute_in_mode({"test": "task"})
        
        stats = adapter.get_statistics()
        assert stats["stats"]["total_executions"] == 1
        assert stats["stats"]["successful_executions"] == 1
        assert stats["success_rate"] == 1.0
    
    def test_reset_statistics(self):
        """Test resetting statistics."""
        adapter = UnifiedAdaptiveLayer()
        adapter.execute_in_mode({"test": "task"})
        
        adapter.reset_statistics()
        assert adapter._stats["total_executions"] == 0
        assert adapter._stats["successful_executions"] == 0
    
    def test_health_check(self):
        """Test health check."""
        adapter = UnifiedAdaptiveLayer()
        adapter.execute_in_mode({"test": "task"})
        adapter.set_execution_mode(ExecutionMode.FAST)
        
        health = adapter.health_check()
        assert health["status"] == "healthy"
        assert health["current_mode"] == "fast"
        assert health["total_executions"] == 1
        assert health["success_rate"] == 1.0


class TestIntegration:
    """Integration tests combining multiple components."""
    
    def test_end_to_end_execution_workflow(self):
        """Test complete execution workflow."""
        adapter = UnifiedAdaptiveLayer()
        
        # 1. Analyze task complexity
        task = {"complexity": "medium", "inputs": [1, 2, 3, 4, 5]}
        complexity = adapter._analyze_task_complexity(task)
        assert complexity == "medium"
        
        # 2. Select strategy
        strategy = adapter.select_strategy(task)
        assert strategy in [StrategyType.FAST, StrategyType.BALANCED, StrategyType.THOROUGH]
        
        # 3. Allocate resources
        allocations = adapter.allocate_resources(task)
        assert len(allocations) > 0
        
        # 4. Execute task
        result = adapter.apply_strategy(task, strategy)
        assert result["status"] == "success"
        
        # 5. Collect metrics
        adapter.collect_metrics(
            orchestrator="TestOrch",
            task_type="test",
            duration_seconds=1.5,
            memory_mb=256,
            success=True,
        )
        
        # 6. Verify statistics
        stats = adapter.get_statistics()
        assert stats["stats"]["total_executions"] >= 1
    
    def test_failover_and_recovery_workflow(self):
        """Test failover and recovery workflow."""
        adapter = UnifiedAdaptiveLayer()
        
        # Register recovery strategy
        def recovery(context: FailoverContext):
            return {"status": "recovered", "retry": True}
        
        adapter.register_recovery_strategy("network_error", recovery)
        
        # Trigger failover
        context = FailoverContext(
            failure_type="network_error",
            failed_component="orch1",
            original_task={"test": "failover"},
            error_message="Network timeout",
        )
        
        result = adapter.trigger_failover(context)
        assert result is not None
        assert result["status"] == "recovered"
    
    def test_multi_strategy_comparison(self):
        """Test comparing all strategies."""
        adapter = UnifiedAdaptiveLayer()
        task = {"complexity": "medium"}
        
        recommendations = adapter.get_strategy_recommendations(task)
        assert len(recommendations) == 3
        
        for strategy_key, rec in recommendations.items():
            assert "strategy" in rec
            assert "config" in rec
            assert "estimated_duration" in rec


class TestBackwardCompatibility:
    """Test backward compatibility with existing code."""
    
    def test_execution_mode_enum_compatibility(self):
        """Test ExecutionMode enum backward compatibility."""
        adapter = UnifiedAdaptiveLayer()
        
        # Test all modes exist and work
        for mode in ExecutionMode:
            adapter.set_execution_mode(mode)
            assert adapter.get_execution_mode() == mode
    
    def test_execution_metrics_compatibility(self):
        """Test ExecutionMetrics compatibility."""
        metrics = ExecutionMetrics(
            orchestrator="test",
            task_type="test",
            duration_seconds=1.0,
            memory_mb=256,
            success=True,
        )
        
        assert metrics.orchestrator == "test"
        assert metrics.duration_seconds == 1.0
        assert metrics.memory_mb == 256
        assert metrics.success is True
    
    def test_performance_profile_compatibility(self):
        """Test PerformanceProfile compatibility."""
        profile = PerformanceProfile(orchestrator="test")
        
        metrics = ExecutionMetrics(
            orchestrator="test",
            task_type="test",
            duration_seconds=1.5,
            memory_mb=512,
            success=True,
        )
        
        profile.executions.append(metrics)
        assert profile.total_executions == 1
        assert profile.successful_executions == 1
        assert profile.average_duration == 1.5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
