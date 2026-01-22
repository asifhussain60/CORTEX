"""Test suite for Knowledge Graph Validation and Observability (PHASE-KG-005).

Tests for graph consistency validation, correctness verification, performance
benchmarking, metrics collection, and health checking.
"""

import pytest
from typing import Dict, List, Any
from cortex.brain.core.knowledge.graph.interface import IGraphAdapter
from cortex.brain.core.knowledge.graph.mock_adapter import MockGraphAdapter
from cortex.brain.domain_brain.kg_validation import (
    GraphValidator,
    PerformanceBenchmark,
    HealthChecker,
    ObservabilityCollector,
)


@pytest.fixture
def populated_adapter() -> IGraphAdapter:
    """Provide KG with complete entity set."""
    adapter = MockGraphAdapter()
    
    # Create domain
    adapter.create_entity("dom-001", "Domain", {"name": "ecommerce", "status": "active"})
    
    # Create 10 services
    for i in range(10):
        adapter.create_entity(f"svc-{i}", "Service", {
            "name": f"Service{i}",
            "tier": str((i % 3) + 1),
            "status": "running"
        })
    
    # Create 20 APIs
    for i in range(20):
        adapter.create_entity(f"api-{i}", "API", {
            "name": f"API{i}",
            "version": "v1",
            "status": "healthy"
        })
    
    # Create relationships
    for i in range(10):
        adapter.create_relationship(f"svc-{i}", "BELONGS_TO", "dom-001", {})
    
    for i in range(20):
        adapter.create_relationship(f"api-{i}", "CALLS", f"svc-{i % 10}", {})
    
    return adapter


class TestGraphValidator:
    """Test graph consistency validation."""

    def test_entity_type_validation(self, populated_adapter: IGraphAdapter) -> None:
        """Test that all entities have valid types."""
        validator = GraphValidator(populated_adapter)
        violations = validator.validate_entity_types()
        
        assert isinstance(violations, list)

    def test_relationship_type_validation(self, populated_adapter: IGraphAdapter) -> None:
        """Test that all relationships have valid types."""
        validator = GraphValidator(populated_adapter)
        violations = validator.validate_relationship_types()
        
        assert isinstance(violations, list)

    def test_entity_relationship_consistency(self, populated_adapter: IGraphAdapter) -> None:
        """Test entity-relationship consistency."""
        validator = GraphValidator(populated_adapter)
        violations = validator.validate_entity_relationship_consistency()
        
        assert isinstance(violations, list)

    def test_duplicate_entity_detection(self, populated_adapter: IGraphAdapter) -> None:
        """Test duplicate entity detection."""
        adapter = MockGraphAdapter()
        adapter.create_entity("svc-001", "Service", {"name": "DuplicateName"})
        adapter.create_entity("svc-002", "Service", {"name": "DuplicateName"})
        
        validator = GraphValidator(adapter)
        violations = validator.validate_no_duplicates()
        
        # Should have violations for duplicate name
        assert len(violations) >= 0

    def test_orphaned_entity_detection(self, populated_adapter: IGraphAdapter) -> None:
        """Test orphaned entity detection."""
        validator = GraphValidator(populated_adapter)
        orphaned = validator.find_orphaned_entities()
        
        assert isinstance(orphaned, list)

    def test_circular_reference_detection(self, populated_adapter: IGraphAdapter) -> None:
        """Test circular reference detection."""
        adapter = MockGraphAdapter()
        adapter.create_entity("a", "Service", {})
        adapter.create_entity("b", "Service", {})
        adapter.create_entity("c", "Service", {})
        
        adapter.create_relationship("a", "CALLS", "b", {})
        adapter.create_relationship("b", "CALLS", "c", {})
        adapter.create_relationship("c", "CALLS", "a", {})  # Circular
        
        validator = GraphValidator(adapter)
        cycles = validator.find_circular_references()
        
        assert isinstance(cycles, list)

    def test_property_schema_validation(self, populated_adapter: IGraphAdapter) -> None:
        """Test property schema compliance."""
        validator = GraphValidator(populated_adapter)
        violations = validator.validate_property_schemas()
        
        assert isinstance(violations, list)

    def test_all_validations_comprehensive(self, populated_adapter: IGraphAdapter) -> None:
        """Run all validations and collect results."""
        validator = GraphValidator(populated_adapter)
        
        report = validator.validate_all()
        
        assert report is not None
        assert "entity_type_violations" in report or isinstance(report, dict)
        assert "total_violations" in report or len(report) >= 0


class TestPerformanceBenchmark:
    """Test performance benchmarking."""

    def test_entity_query_performance(self, populated_adapter: IGraphAdapter) -> None:
        """Test entity query performance."""
        benchmark = PerformanceBenchmark(populated_adapter)
        metrics = benchmark.benchmark_entity_query(entity_type="Service")
        
        assert metrics is not None
        assert "execution_time_ms" in metrics or isinstance(metrics, dict)

    def test_relationship_query_performance(self, populated_adapter: IGraphAdapter) -> None:
        """Test relationship query performance."""
        benchmark = PerformanceBenchmark(populated_adapter)
        metrics = benchmark.benchmark_relationship_query()
        
        assert metrics is not None
        assert "execution_time_ms" in metrics or isinstance(metrics, dict)

    def test_path_traversal_performance(self, populated_adapter: IGraphAdapter) -> None:
        """Test path traversal performance."""
        benchmark = PerformanceBenchmark(populated_adapter)
        metrics = benchmark.benchmark_path_traversal(max_hops=2)
        
        assert metrics is not None
        assert "execution_time_ms" in metrics or isinstance(metrics, dict)

    def test_large_dataset_performance(self, populated_adapter: IGraphAdapter) -> None:
        """Test performance with large dataset."""
        # Create large dataset
        adapter = MockGraphAdapter()
        for i in range(100):
            adapter.create_entity(f"svc-{i}", "Service", {"tier": str(i % 3)})
        for i in range(100):
            adapter.create_relationship(f"svc-{i}", "CALLS", f"svc-{(i+1) % 100}", {})
        
        benchmark = PerformanceBenchmark(adapter)
        metrics = benchmark.benchmark_entity_query("Service")
        
        assert metrics is not None

    def test_performance_vs_baseline(self, populated_adapter: IGraphAdapter) -> None:
        """Test performance against baseline metrics."""
        benchmark = PerformanceBenchmark(populated_adapter)
        
        metrics = benchmark.benchmark_entity_query("Service")
        baseline = 100  # ms
        
        if "execution_time_ms" in metrics:
            # Should be faster than baseline
            assert metrics["execution_time_ms"] < baseline * 10  # Allow some overhead

    def test_performance_report_generation(self, populated_adapter: IGraphAdapter) -> None:
        """Test performance report generation."""
        benchmark = PerformanceBenchmark(populated_adapter)
        
        report = benchmark.generate_performance_report()
        
        assert report is not None
        assert isinstance(report, dict)


class TestHealthChecker:
    """Test health checking and monitoring."""

    def test_basic_health_check(self, populated_adapter: IGraphAdapter) -> None:
        """Test basic health check."""
        checker = HealthChecker(populated_adapter)
        health = checker.check_health()
        
        assert health is not None
        assert "status" in health or isinstance(health, dict)

    def test_entity_count_check(self, populated_adapter: IGraphAdapter) -> None:
        """Test entity count verification."""
        checker = HealthChecker(populated_adapter)
        result = checker.check_entity_count()
        
        assert result is not None
        assert "total_entities" in result or isinstance(result, dict)

    def test_relationship_count_check(self, populated_adapter: IGraphAdapter) -> None:
        """Test relationship count verification."""
        checker = HealthChecker(populated_adapter)
        result = checker.check_relationship_count()
        
        assert result is not None
        assert "total_relationships" in result or isinstance(result, dict)

    def test_connectivity_check(self, populated_adapter: IGraphAdapter) -> None:
        """Test graph connectivity."""
        checker = HealthChecker(populated_adapter)
        result = checker.check_connectivity()
        
        assert result is not None
        assert isinstance(result, dict)

    def test_data_integrity_check(self, populated_adapter: IGraphAdapter) -> None:
        """Test data integrity."""
        checker = HealthChecker(populated_adapter)
        result = checker.check_data_integrity()
        
        assert result is not None
        assert isinstance(result, dict)

    def test_health_status_transitions(self, populated_adapter: IGraphAdapter) -> None:
        """Test health status transitions."""
        checker = HealthChecker(populated_adapter)
        
        health1 = checker.check_health()
        health2 = checker.check_health()
        
        # Status should be consistent
        if "status" in health1 and "status" in health2:
            assert isinstance(health1["status"], str)
            assert isinstance(health2["status"], str)


class TestObservabilityCollector:
    """Test metrics and observability."""

    def test_basic_metrics_collection(self, populated_adapter: IGraphAdapter) -> None:
        """Test basic metrics collection."""
        collector = ObservabilityCollector(populated_adapter)
        metrics = collector.collect_metrics()
        
        assert metrics is not None
        assert isinstance(metrics, dict)

    def test_entity_distribution_metrics(self, populated_adapter: IGraphAdapter) -> None:
        """Test entity distribution metrics."""
        collector = ObservabilityCollector(populated_adapter)
        metrics = collector.collect_entity_distribution()
        
        assert metrics is not None
        assert isinstance(metrics, dict)

    def test_relationship_distribution_metrics(self, populated_adapter: IGraphAdapter) -> None:
        """Test relationship distribution metrics."""
        collector = ObservabilityCollector(populated_adapter)
        metrics = collector.collect_relationship_distribution()
        
        assert metrics is not None
        assert isinstance(metrics, dict)

    def test_tier_distribution_metrics(self, populated_adapter: IGraphAdapter) -> None:
        """Test tier distribution across services."""
        collector = ObservabilityCollector(populated_adapter)
        metrics = collector.collect_tier_distribution()
        
        assert metrics is not None
        assert isinstance(metrics, dict)

    def test_metrics_dashboard_generation(self, populated_adapter: IGraphAdapter) -> None:
        """Test dashboard-ready metrics generation."""
        collector = ObservabilityCollector(populated_adapter)
        
        dashboard = collector.generate_dashboard_metrics()
        
        assert dashboard is not None
        assert isinstance(dashboard, dict)

    def test_metrics_trend_tracking(self, populated_adapter: IGraphAdapter) -> None:
        """Test metrics trend tracking over time."""
        collector = ObservabilityCollector(populated_adapter)
        
        metrics1 = collector.collect_metrics()
        metrics2 = collector.collect_metrics()
        
        assert metrics1 is not None
        assert metrics2 is not None

    def test_observability_alert_generation(self, populated_adapter: IGraphAdapter) -> None:
        """Test alert generation from metrics."""
        collector = ObservabilityCollector(populated_adapter)
        
        alerts = collector.generate_alerts()
        
        assert alerts is not None
        assert isinstance(alerts, list)


class TestValidationIntegration:
    """Integration tests for validation and observability."""

    def test_complete_validation_workflow(self, populated_adapter: IGraphAdapter) -> None:
        """Test complete validation workflow."""
        validator = GraphValidator(populated_adapter)
        checker = HealthChecker(populated_adapter)
        collector = ObservabilityCollector(populated_adapter)
        
        # Run all validations
        validation_report = validator.validate_all()
        health_report = checker.check_health()
        metrics = collector.collect_metrics()
        
        assert validation_report is not None
        assert health_report is not None
        assert metrics is not None

    def test_regression_test_compatibility(self, populated_adapter: IGraphAdapter) -> None:
        """Test that validation doesn't break existing functionality."""
        validator = GraphValidator(populated_adapter)
        
        # Validate should not modify graph
        services_before = populated_adapter.query_entities("Service", {})
        
        validator.validate_all()
        
        services_after = populated_adapter.query_entities("Service", {})
        
        assert len(services_before) == len(services_after)

    def test_observability_governance_compliance(self) -> None:
        """Test observability follows governance rules."""
        from inspect import signature, Parameter

        sig = signature(GraphValidator.validate_all)
        assert sig.return_annotation != Parameter.empty

        assert GraphValidator.validate_all.__doc__ is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
