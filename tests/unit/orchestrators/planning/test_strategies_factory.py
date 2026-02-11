"""
Wave 8 Stage 1: Strategy Factory and Composition Tests (REFACTOR Phase)

Tests for StrategyFactory, StrategyComposer, and MetricsCollector utilities.
"""

import pytest
from cortex.orchestrators.planning.strategies.base import ExecutionContext, ExecutionResult
from cortex.orchestrators.planning.strategies.factory import (
    StrategyFactory,
    StrategyComposer,
    MetricsCollector,
)
from cortex.orchestrators.planning.strategies import (
    PhaseExecutionStrategy,
    WaveOrchestrationStrategy,
    TrackParallelizationStrategy,
)


class TestStrategyFactory:
    """Tests for StrategyFactory."""

    def test_factory_create_phase_strategy(self):
        """Factory can create phase strategy."""
        strategy = StrategyFactory.create("phase")
        assert isinstance(strategy, PhaseExecutionStrategy)

    def test_factory_create_wave_strategy(self):
        """Factory can create wave strategy."""
        strategy = StrategyFactory.create("wave")
        assert isinstance(strategy, WaveOrchestrationStrategy)

    def test_factory_create_track_strategy(self):
        """Factory can create track strategy."""
        strategy = StrategyFactory.create("track")
        assert isinstance(strategy, TrackParallelizationStrategy)

    def test_factory_invalid_strategy_type(self):
        """Factory raises error for unknown strategy type."""
        with pytest.raises(ValueError):
            StrategyFactory.create("unknown")

    def test_factory_get_available_types(self):
        """Factory lists available strategy types."""
        types = StrategyFactory.get_available_types()
        assert "phase" in types
        assert "wave" in types
        assert "track" in types

    def test_factory_register_custom_strategy(self):
        """Factory can register custom strategy type."""
        from cortex.orchestrators.planning.strategies.base import ExecutionStrategy

        class CustomStrategy(ExecutionStrategy):
            def execute(self, context):
                return ExecutionResult(success=True)

            def validate(self):
                from cortex.orchestrators.planning.strategies.base import ValidationResult
                return ValidationResult(passed=True)

        StrategyFactory.register("custom", CustomStrategy)
        strategy = StrategyFactory.create("custom")
        assert isinstance(strategy, CustomStrategy)

    def test_factory_register_invalid_strategy(self):
        """Factory rejects non-strategy classes."""
        class InvalidStrategy:
            pass

        with pytest.raises(TypeError):
            StrategyFactory.register("invalid", InvalidStrategy)


class TestStrategyComposer:
    """Tests for StrategyComposer."""

    def test_composer_instantiation(self):
        """StrategyComposer can be instantiated."""
        composer = StrategyComposer()
        assert composer is not None

    def test_composer_add_strategy(self):
        """Composer can add strategies."""
        composer = StrategyComposer()
        phase = PhaseExecutionStrategy()
        result = composer.add_strategy("phase", phase)
        assert result is composer  # Check fluent interface

    def test_composer_add_multiple_strategies(self):
        """Composer can add multiple strategies."""
        composer = StrategyComposer()
        phase = PhaseExecutionStrategy()
        wave = WaveOrchestrationStrategy()
        track = TrackParallelizationStrategy()

        composer.add_strategy("phase", phase, order=3)
        composer.add_strategy("wave", wave, order=2)
        composer.add_strategy("track", track, order=1)

        types = list(s[1] for s in composer._execution_order)
        assert types == ["track", "wave", "phase"]  # Sorted by order

    def test_composer_execute_hierarchy(self):
        """Composer executes strategy hierarchy."""
        composer = StrategyComposer()
        phase = PhaseExecutionStrategy()
        wave = WaveOrchestrationStrategy()
        
        composer.add_strategy("phase", phase, order=2)
        composer.add_strategy("wave", wave, order=1)
        
        context = ExecutionContext(
            strategy_type="wave",
            wave_id="WAVE-8",
            data={"phases": ["P1", "P2"]}
        )
        
        result = composer.execute_hierarchy(context)
        assert hasattr(result, 'success')

    def test_composer_execute_with_no_strategies(self):
        """Composer fails gracefully with no strategies."""
        composer = StrategyComposer()
        context = ExecutionContext(strategy_type="wave")
        
        result = composer.execute_hierarchy(context)
        assert result.success is False


class TestMetricsCollector:
    """Tests for MetricsCollector."""

    def test_collector_instantiation(self):
        """MetricsCollector can be instantiated."""
        collector = MetricsCollector()
        assert collector is not None

    def test_collector_collect_from_strategy(self):
        """Collector can collect metrics from strategy."""
        collector = MetricsCollector()
        strategy = PhaseExecutionStrategy()
        
        # Execute strategy first to generate metrics
        context = ExecutionContext(
            strategy_type="phase",
            phase_id="P1",
            data={"tasks": ["task1"]}
        )
        strategy.execute(context)
        
        # Collect metrics
        collector.collect_from_strategy("phase", strategy)
        
        assert "phase" in collector._metrics

    def test_collector_get_aggregate_metrics(self):
        """Collector aggregates metrics from all strategies."""
        collector = MetricsCollector()
        
        # Collect from multiple strategies
        phase = PhaseExecutionStrategy()
        wave = WaveOrchestrationStrategy()
        
        context1 = ExecutionContext(
            strategy_type="phase",
            phase_id="P1",
            data={"tasks": ["task1"]}
        )
        phase.execute(context1)
        
        context2 = ExecutionContext(
            strategy_type="wave",
            wave_id="W1",
            data={"phases": ["P1"]}
        )
        wave.execute(context2)
        
        collector.collect_from_strategy("phase", phase)
        collector.collect_from_strategy("wave", wave)
        
        metrics = collector.get_aggregate_metrics()
        
        assert "strategies" in metrics
        assert "total_events" in metrics
        assert metrics["strategies"]["phase"] is not None
        assert metrics["strategies"]["wave"] is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
