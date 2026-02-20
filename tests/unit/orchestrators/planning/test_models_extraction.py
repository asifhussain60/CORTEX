"""
Tests for Planning Orchestrator Models (Wave 8 Stage 3)

Tests ROICompositeScorer, DependencyResolver, and ParallelismCalculator.
"""

import pytest
from cortex.orchestrators.domain.roi_composite_scorer import ROICompositeScorer
from cortex.orchestrators.domain.dependency_resolver import DependencyResolver
from cortex.orchestrators.domain.parallelism_calculator import ParallelismCalculator
from cortex.orchestrators.domain.roi_composite_scorer import (
    ROIWeights,
    PhaseMetrics,
    PriorityTier,
)
from cortex.orchestrators.domain.dependency_resolver import (
    DependencyGraph,
    ResolutionStatus,
)


# =============================================================================
# ROI Composite Scorer Tests
# =============================================================================

class TestROICompositeScorer:
    """Tests for ROI scoring algorithm"""
    
    def test_scorer_instantiation(self):
        """Test: Scorer can be instantiated with default weights"""
        scorer = ROICompositeScorer()
        
        assert scorer.weights.architectural_impact == 0.35
        assert scorer.weights.efficiency_gain == 0.25
        assert scorer.weights.accuracy_improvement == 0.20
        assert scorer.weights.effort_cost == 0.15
        assert scorer.weights.blocking_severity == 0.05
    
    def test_roi_calculation_formula(self):
        """Test: ROI score calculated correctly per phase-25 spec"""
        scorer = ROICompositeScorer()
        metrics = PhaseMetrics(
            architectural_impact=0.9,
            efficiency_gain=0.95,
            accuracy_improvement=0.4,
            effort_cost=0.3,
            blocking_severity=1.0
        )
        
        roi_score = scorer.calculate(metrics)
        
        # Expected: (0.9*0.35) + (0.95*0.25) + (0.4*0.2) + ((1-0.3)*0.15) + (1.0*0.05)
        expected = 0.315 + 0.2375 + 0.08 + 0.105 + 0.05
        assert abs(roi_score - expected) < 0.001
    
    def test_roi_effort_inversion(self):
        """Test: Effort cost is inverted (low effort = high score)"""
        scorer = ROICompositeScorer()
        
        # High effort (0.9) should reduce score
        high_effort = PhaseMetrics(
            architectural_impact=0.5,
            efficiency_gain=0.5,
            accuracy_improvement=0.5,
            effort_cost=0.9,  # High effort
            blocking_severity=0.5
        )
        
        # Low effort (0.1) should increase score
        low_effort = PhaseMetrics(
            architectural_impact=0.5,
            efficiency_gain=0.5,
            accuracy_improvement=0.5,
            effort_cost=0.1,  # Low effort
            blocking_severity=0.5
        )
        
        high_effort_score = scorer.calculate(high_effort)
        low_effort_score = scorer.calculate(low_effort)
        
        assert low_effort_score > high_effort_score
    
    def test_priority_tier_high(self):
        """Test: ROI >= 0.75 returns HIGH priority"""
        scorer = ROICompositeScorer()
        metrics = PhaseMetrics(
            architectural_impact=0.9,
            efficiency_gain=0.9,
            accuracy_improvement=0.8,
            effort_cost=0.2,
            blocking_severity=0.9
        )
        
        tier = scorer.get_priority_tier(metrics)
        
        assert tier == PriorityTier.HIGH
    
    def test_priority_tier_medium(self):
        """Test: 0.60 <= ROI < 0.75 returns MEDIUM priority"""
        scorer = ROICompositeScorer()
        metrics = PhaseMetrics(
            architectural_impact=0.6,
            efficiency_gain=0.7,
            accuracy_improvement=0.6,
            effort_cost=0.3,
            blocking_severity=0.5
        )
        
        tier = scorer.get_priority_tier(metrics)
        
        assert tier == PriorityTier.MEDIUM
    
    def test_priority_tier_low(self):
        """Test: 0.40 <= ROI < 0.60 returns LOW priority"""
        scorer = ROICompositeScorer()
        metrics = PhaseMetrics(
            architectural_impact=0.4,
            efficiency_gain=0.5,
            accuracy_improvement=0.4,
            effort_cost=0.5,
            blocking_severity=0.3
        )
        
        tier = scorer.get_priority_tier(metrics)
        
        assert tier == PriorityTier.LOW
    
    def test_priority_tier_defer(self):
        """Test: ROI < 0.40 returns DEFER priority"""
        scorer = ROICompositeScorer()
        metrics = PhaseMetrics(
            architectural_impact=0.2,
            efficiency_gain=0.3,
            accuracy_improvement=0.2,
            effort_cost=0.8,  # High effort
            blocking_severity=0.1
        )
        
        tier = scorer.get_priority_tier(metrics)
        
        assert tier == PriorityTier.DEFER
    
    def test_metrics_validation_range(self):
        """Test: PhaseMetrics validates 0.0-1.0 range"""
        with pytest.raises(ValueError, match="must be in \\[0.0, 1.0\\]"):
            PhaseMetrics(
                architectural_impact=1.5,  # Invalid
                efficiency_gain=0.5,
                accuracy_improvement=0.5,
                effort_cost=0.5,
                blocking_severity=0.5
            )
    
    def test_custom_weights(self):
        """Test: Scorer accepts custom weights"""
        custom_weights = ROIWeights(
            architectural_impact=0.5,
            efficiency_gain=0.3,
            accuracy_improvement=0.1,
            effort_cost=0.05,
            blocking_severity=0.05
        )
        
        scorer = ROICompositeScorer(weights=custom_weights)
        
        assert scorer.weights.architectural_impact == 0.5


# =============================================================================
# Dependency Resolver Tests
# =============================================================================

class TestDependencyResolver:
    """Tests for dependency resolution algorithm"""
    
    def test_resolver_simple_chain(self):
        """Test: Resolver handles simple dependency chain"""
        graph = DependencyGraph.from_dict({
            "A": [],
            "B": ["A"],
            "C": ["B"]
        })
        
        resolver = DependencyResolver()
        result = resolver.resolve(graph)
        
        assert result.is_success
        assert result.execution_order == ["A", "B", "C"]
    
    def test_resolver_parallel_branches(self):
        """Test: Resolver handles parallel branches"""
        graph = DependencyGraph.from_dict({
            "A": [],
            "B": [],
            "C": ["A"],
            "D": ["B"]
        })
        
        resolver = DependencyResolver()
        result = resolver.resolve(graph)
        
        assert result.is_success
        # A and B should come before C and D
        assert result.execution_order.index("A") < result.execution_order.index("C")
        assert result.execution_order.index("B") < result.execution_order.index("D")
    
    def test_resolver_detects_circular_dependency(self):
        """Test: Resolver detects circular dependencies"""
        graph = DependencyGraph.from_dict({
            "A": ["B"],
            "B": ["C"],
            "C": ["A"]  # Circular
        })
        
        resolver = DependencyResolver()
        result = resolver.resolve(graph)
        
        assert not result.is_success
        assert result.status == ResolutionStatus.CIRCULAR_DEPENDENCY
        assert result.circular_path is not None
        assert len(result.circular_path) > 0
    
    def test_resolver_complex_dag(self):
        """Test: Resolver handles complex DAG"""
        graph = DependencyGraph.from_dict({
            "A": [],
            "B": [],
            "C": ["A"],
            "D": ["A"],
            "E": ["B", "C"],
            "F": ["D", "E"]
        })
        
        resolver = DependencyResolver()
        result = resolver.resolve(graph)
        
        assert result.is_success
        assert len(result.execution_order) == 6
        
        # Verify dependencies are respected
        order = result.execution_order
        assert order.index("A") < order.index("C")
        assert order.index("A") < order.index("D")
        assert order.index("B") < order.index("E")
        assert order.index("C") < order.index("E")
        assert order.index("D") < order.index("F")
        assert order.index("E") < order.index("F")
    
    def test_transitive_dependencies(self):
        """Test: Get transitive dependencies of a phase"""
        graph = DependencyGraph.from_dict({
            "A": [],
            "B": ["A"],
            "C": ["B"],
            "D": ["C"]
        })
        
        resolver = DependencyResolver()
        transitive = resolver.get_transitive_dependencies(graph, "D")
        
        assert transitive == {"A", "B", "C"}
    
    def test_empty_graph(self):
        """Test: Resolver handles empty graph"""
        graph = DependencyGraph(phases=set(), dependencies={})
        
        resolver = DependencyResolver()
        result = resolver.resolve(graph)
        
        assert result.is_success
        assert result.execution_order == []


# =============================================================================
# Parallelism Calculator Tests
# =============================================================================

class TestParallelismCalculator:
    """Tests for parallelism calculation algorithm"""
    
    def test_calculator_simple_parallel(self):
        """Test: Calculator identifies parallel phases"""
        graph = DependencyGraph.from_dict({
            "A": [],
            "B": [],
            "C": []
        })
        
        calculator = ParallelismCalculator()
        plan = calculator.calculate(graph)
        
        assert plan.total_phases == 3
        assert plan.total_levels == 1
        assert plan.max_parallelism == 3
        assert len(plan.levels) == 1
        assert set(plan.levels[0].phases) == {"A", "B", "C"}
    
    def test_calculator_sequential(self):
        """Test: Calculator handles sequential dependencies"""
        graph = DependencyGraph.from_dict({
            "A": [],
            "B": ["A"],
            "C": ["B"]
        })
        
        calculator = ParallelismCalculator()
        plan = calculator.calculate(graph)
        
        assert plan.total_phases == 3
        assert plan.total_levels == 3
        assert plan.max_parallelism == 1
        assert plan.levels[0].phases == ["A"]
        assert plan.levels[1].phases == ["B"]
        assert plan.levels[2].phases == ["C"]
    
    def test_calculator_mixed_parallel_sequential(self):
        """Test: Calculator handles mixed parallel/sequential"""
        graph = DependencyGraph.from_dict({
            "A": [],
            "B": [],
            "C": ["A"],
            "D": ["A"],
            "E": ["B", "C"]
        })
        
        calculator = ParallelismCalculator()
        plan = calculator.calculate(graph)
        
        # Level 0: A, B (parallel)
        # Level 1: C, D (parallel, depend on A)
        # Level 2: E (depends on B and C)
        assert plan.total_levels == 3
        assert set(plan.levels[0].phases) == {"A", "B"}
        assert set(plan.levels[1].phases) == {"C", "D"}
        assert plan.levels[2].phases == ["E"]
    
    def test_calculator_speedup_potential(self):
        """Test: Calculator computes speedup potential"""
        graph = DependencyGraph.from_dict({
            "A": [],
            "B": [],
            "C": ["A", "B"]
        })
        
        calculator = ParallelismCalculator()
        plan = calculator.calculate(graph)
        
        # 3 phases / 2 levels = 1.5x speedup
        assert abs(plan.speedup_potential - 1.5) < 0.01
    
    def test_calculator_execution_time_estimation(self):
        """Test: Calculator estimates execution time"""
        graph = DependencyGraph.from_dict({
            "A": [],
            "B": [],
            "C": ["A", "B"]
        })
        
        calculator = ParallelismCalculator()
        plan = calculator.calculate(graph)
        
        phase_durations = {
            "A": 2.0,  # 2 hours
            "B": 3.0,  # 3 hours
            "C": 1.0   # 1 hour
        }
        
        # Level 0: max(A=2, B=3) = 3 hours
        # Level 1: C = 1 hour
        # Total: 4 hours
        estimated_time = calculator.estimate_execution_time(plan, phase_durations)
        
        assert abs(estimated_time - 4.0) < 0.01
    
    def test_calculator_sequential_vs_parallel_comparison(self):
        """Test: Calculator compares sequential vs parallel"""
        graph = DependencyGraph.from_dict({
            "A": [],
            "B": [],
            "C": ["A", "B"]
        })
        
        calculator = ParallelismCalculator()
        plan = calculator.calculate(graph)
        
        phase_durations = {
            "A": 2.0,
            "B": 3.0,
            "C": 1.0
        }
        
        comparison = calculator.compare_sequential_vs_parallel(plan, phase_durations)
        
        # Sequential: 2 + 3 + 1 = 6 hours
        # Parallel: max(2, 3) + 1 = 4 hours
        # Speedup: 6 / 4 = 1.5x
        assert abs(comparison["sequential_time"] - 6.0) < 0.01
        assert abs(comparison["parallel_time"] - 4.0) < 0.01
        assert abs(comparison["speedup"] - 1.5) < 0.01
        assert abs(comparison["time_saved"] - 2.0) < 0.01
    
    def test_calculator_raises_on_circular_dependency(self):
        """Test: Calculator raises error on circular dependencies"""
        graph = DependencyGraph.from_dict({
            "A": ["B"],
            "B": ["A"]
        })
        
        calculator = ParallelismCalculator()
        
        with pytest.raises(ValueError, match="Circular dependency"):
            calculator.calculate(graph)
