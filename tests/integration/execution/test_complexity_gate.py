"""Tests for complexity gate implementation (arch-023-complexity).

Covers complexity metrics, calculation, gate logic, and reporting.
"""

import pytest
from cortex.execution.complexity_metrics import ComplexityMetrics
from cortex.execution.complexity_calculator import ComplexityCalculator, ComplexityScore
from cortex.execution.complexity_gate import ComplexityGate, GateDecision


class TestComplexityMetrics:
    """Test complexity metrics collection."""

    def test_collect_basic_metrics(self) -> None:
        """Test collecting basic operation metrics."""
        metrics = ComplexityMetrics()
        collected = metrics.collect(
            operation_type="api_call",
            data_size_mb=10,
            dependency_count=3
        )
        assert collected is not None
        assert collected.get("operation_type") == "api_call"
        assert collected.get("data_size_mb") == 10
        assert collected.get("dependency_count") == 3

    def test_calculate_metric_factors(self) -> None:
        """Test calculating metric factors for complexity."""
        metrics = ComplexityMetrics()
        factors = metrics.calculate_factors(
            operation_type="database_query",
            data_size_mb=100,
            dependency_count=5
        )
        assert isinstance(factors, dict)
        assert len(factors) > 0

    def test_operation_type_factor(self) -> None:
        """Test operation type contributes to complexity factor."""
        metrics = ComplexityMetrics()
        
        simple_factor = metrics.get_operation_factor("read")
        complex_factor = metrics.get_operation_factor("distributed_transaction")
        
        assert complex_factor > simple_factor

    def test_data_size_factor(self) -> None:
        """Test data size contributes to complexity factor."""
        metrics = ComplexityMetrics()
        
        small = metrics.get_data_size_factor(1)
        large = metrics.get_data_size_factor(1000)
        
        assert large > small

    def test_dependency_factor(self) -> None:
        """Test dependency count contributes to complexity factor."""
        metrics = ComplexityMetrics()
        
        few_deps = metrics.get_dependency_factor(1)
        many_deps = metrics.get_dependency_factor(10)
        
        assert many_deps > few_deps


class TestComplexityCalculator:
    """Test complexity score calculation."""

    def test_calculate_simple_operation(self) -> None:
        """Test calculating complexity for simple operation."""
        calculator = ComplexityCalculator()
        score = calculator.calculate(
            operation_type="read",
            data_size_mb=1,
            dependency_count=1,
            parallel_tasks=1
        )
        assert score.score < 30
        assert score.category == "simple"

    def test_calculate_moderate_operation(self) -> None:
        """Test calculating complexity for moderate operation."""
        calculator = ComplexityCalculator()
        score = calculator.calculate(
            operation_type="api_orchestration",
            data_size_mb=50,
            dependency_count=5,
            parallel_tasks=3
        )
        assert 30 <= score.score < 70
        assert score.category == "moderate"

    def test_calculate_complex_operation(self) -> None:
        """Test calculating complexity for complex operation."""
        calculator = ComplexityCalculator()
        score = calculator.calculate(
            operation_type="distributed_transaction",
            data_size_mb=500,
            dependency_count=15,
            parallel_tasks=20,
            retry_count=5
        )
        assert score.score >= 70
        assert score.category == "complex"

    def test_score_reproducibility(self) -> None:
        """Test that same inputs produce same scores."""
        calculator = ComplexityCalculator()
        
        score1 = calculator.calculate(
            operation_type="api_call",
            data_size_mb=10,
            dependency_count=2
        )
        score2 = calculator.calculate(
            operation_type="api_call",
            data_size_mb=10,
            dependency_count=2
        )
        
        assert score1.score == score2.score

    def test_score_factors_documented(self) -> None:
        """Test that score includes factor breakdowns."""
        calculator = ComplexityCalculator()
        score = calculator.calculate(
            operation_type="database_query",
            data_size_mb=100,
            dependency_count=3
        )
        
        assert score.factors is not None
        assert len(score.factors) > 0


class TestComplexityGate:
    """Test complexity gate decision logic."""

    def test_gate_allows_simple_operations(self) -> None:
        """Test gate allows simple operations."""
        gate = ComplexityGate(
            simple_threshold=30,
            moderate_threshold=70
        )
        
        score = ComplexityScore(score=20, category="simple")
        decision = gate.evaluate(score)
        
        assert decision.allowed is True
        assert decision.action == "allow"

    def test_gate_warns_moderate_operations(self) -> None:
        """Test gate warns on moderate complexity."""
        gate = ComplexityGate(
            simple_threshold=30,
            moderate_threshold=70
        )
        
        score = ComplexityScore(score=50, category="moderate")
        decision = gate.evaluate(score)
        
        assert decision.action in ("warn", "allow")
        assert decision.complexity_level == "moderate"

    def test_gate_blocks_complex_operations(self) -> None:
        """Test gate blocks complex operations by default."""
        gate = ComplexityGate(
            simple_threshold=30,
            moderate_threshold=70,
            allow_complex=False
        )
        
        score = ComplexityScore(score=80, category="complex")
        decision = gate.evaluate(score)
        
        assert decision.allowed is False
        assert decision.action == "block"

    def test_gate_allows_complex_with_override(self) -> None:
        """Test gate can allow complex with override."""
        gate = ComplexityGate(
            simple_threshold=30,
            moderate_threshold=70,
            allow_complex=True
        )
        
        score = ComplexityScore(score=85, category="complex")
        decision = gate.evaluate(score, allow_override=True)
        
        assert decision.allowed is True

    def test_gate_considers_resource_availability(self) -> None:
        """Test gate considers available resources."""
        gate = ComplexityGate()
        
        score = ComplexityScore(score=75, category="complex")
        
        # With resources available
        decision_with_resources = gate.evaluate(
            score,
            available_resources=1000
        )
        
        # Without resources
        decision_without_resources = gate.evaluate(
            score,
            available_resources=10
        )
        
        # With more resources, should be more permissive
        assert isinstance(decision_with_resources, GateDecision)
        assert isinstance(decision_without_resources, GateDecision)

    def test_gate_decision_includes_reason(self) -> None:
        """Test gate decision includes explanation."""
        gate = ComplexityGate()
        score = ComplexityScore(score=85, category="complex")
        decision = gate.evaluate(score)
        
        assert decision.reason is not None
        assert len(decision.reason) > 0


class TestComplexityReporting:
    """Test complexity analysis and reporting."""

    def test_report_complexity_distribution(self) -> None:
        """Test generating complexity distribution report."""
        from cortex.execution.complexity_gate import ComplexityReporter
        
        reporter = ComplexityReporter()
        scores = [
            ComplexityScore(score=10, category="simple"),
            ComplexityScore(score=15, category="simple"),
            ComplexityScore(score=50, category="moderate"),
            ComplexityScore(score=75, category="complex"),
            ComplexityScore(score=85, category="complex")
        ]
        
        report = reporter.distribution_report(scores)
        
        assert report.get("total_operations", 0) == 5
        assert report.get("simple_count", 0) == 2
        assert report.get("moderate_count", 0) == 1
        assert report.get("complex_count", 0) == 2

    def test_report_high_complexity_operations(self) -> None:
        """Test identifying high-complexity operations."""
        from cortex.execution.complexity_gate import ComplexityReporter
        
        reporter = ComplexityReporter()
        scores = [
            ComplexityScore(score=20, category="simple"),
            ComplexityScore(score=80, category="complex"),
            ComplexityScore(score=90, category="complex"),
            ComplexityScore(score=60, category="moderate")
        ]
        
        high_complexity = reporter.identify_high_complexity(scores, threshold=75)
        
        assert len(high_complexity) == 2
        assert all(s.score >= 75 for s in high_complexity)

    def test_report_average_complexity(self) -> None:
        """Test calculating average complexity."""
        from cortex.execution.complexity_gate import ComplexityReporter
        
        reporter = ComplexityReporter()
        scores = [
            ComplexityScore(score=20, category="simple"),
            ComplexityScore(score=50, category="moderate"),
            ComplexityScore(score=80, category="complex")
        ]
        
        avg = reporter.average_complexity(scores)
        
        assert avg == 50


class TestBusinessRules:
    """Test complexity business rules."""

    def test_load_business_rules(self) -> None:
        """Test loading complexity business rules."""
        from cortex.execution.complexity_gate import RuleEngine
        
        engine = RuleEngine()
        rules = engine.load_rules()
        
        assert rules is not None
        assert len(rules) > 0

    def test_apply_custom_rules(self) -> None:
        """Test applying custom business rules."""
        from cortex.execution.complexity_gate import RuleEngine
        
        engine = RuleEngine()
        
        custom_rule = {
            "name": "high_priority_operations",
            "condition": "operation_type == 'critical'",
            "adjustment": -10  # Reduce complexity score
        }
        
        engine.add_rule(custom_rule)
        rules = engine.get_rules()
        
        assert any(r.get("name") == "high_priority_operations" for r in rules)

    def test_rules_can_adjust_scores(self) -> None:
        """Test that rules can adjust complexity scores."""
        from cortex.execution.complexity_gate import RuleEngine
        
        engine = RuleEngine()
        
        base_score = 75
        adjusted = engine.apply_adjustments(base_score, operation_type="monitoring")
        
        # Different operation types should have different adjustments
        assert isinstance(adjusted, (int, float))


class TestIntegration:
    """Integration tests for complexity gate system."""

    def test_end_to_end_complexity_evaluation(self) -> None:
        """Test complete workflow: metrics → calculation → gating."""
        calculator = ComplexityCalculator()
        gate = ComplexityGate()
        
        # Calculate complexity
        score = calculator.calculate(
            operation_type="api_orchestration",
            data_size_mb=50,
            dependency_count=5,
            parallel_tasks=3
        )
        
        # Evaluate gate decision
        decision = gate.evaluate(score)
        
        assert score.score > 0
        assert decision.action in ("allow", "warn", "block")

    def test_metrics_calculator_gate_integration(self) -> None:
        """Test full integration of metrics collection through gating."""
        metrics = ComplexityMetrics()
        calculator = ComplexityCalculator()
        gate = ComplexityGate()
        
        # Collect metrics
        collected = metrics.collect(
            operation_type="database_transaction",
            data_size_mb=100,
            dependency_count=10
        )
        
        # Calculate score
        score = calculator.calculate(**collected)
        
        # Make gate decision
        decision = gate.evaluate(score)
        
        assert collected is not None
        assert score.score > 0
        assert decision is not None
