"""
Tests for MetricsSchema - Pydantic models for instrumentation metrics.

TDD Phase: RED
Author: Asif Hussain
Created: 2026-02-04
"""

import pytest
from datetime import datetime
from uuid import UUID

# Import will fail until we implement (RED phase)
try:
    from cortex.observability.metrics_schema import (
        TDDMetric,
        DebugMetric,
        CodeGenMetric,
        OrchestratorMetric,
        MetricAggregation,
        EnhancementRecommendation,
    )
    IMPORTS_AVAILABLE = True
except ImportError:
    IMPORTS_AVAILABLE = False


@pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Metrics schema not yet implemented")
class TestTDDMetric:
    """Tests for TDD cycle metrics."""
    
    def test_tdd_metric_creation(self):
        """Test creating a valid TDD metric."""
        metric = TDDMetric(
            cycle_id="550e8400-e29b-41d4-a716-446655440000",
            phase="RED",
            orchestrator="TDDOrchestrator",
            test_file="tests/unit/test_example.py",
            duration_ms=1500,
            success=True,
        )
        assert metric.phase == "RED"
        assert metric.duration_ms == 1500
        assert metric.success is True
        
    def test_tdd_metric_with_failure(self):
        """Test TDD metric with failure reason."""
        metric = TDDMetric(
            cycle_id="550e8400-e29b-41d4-a716-446655440001",
            phase="GREEN",
            orchestrator="TDDOrchestrator",
            test_file="tests/unit/test_example.py",
            duration_ms=5000,
            success=False,
            failure_reason="Test assertion failed: expected True, got False",
            retry_count=2,
        )
        assert metric.success is False
        assert metric.failure_reason is not None
        assert metric.retry_count == 2
        
    def test_tdd_metric_invalid_phase(self):
        """Test TDD metric rejects invalid phase."""
        with pytest.raises(ValueError):
            TDDMetric(
                cycle_id="550e8400-e29b-41d4-a716-446655440002",
                phase="INVALID",  # Should fail validation
                orchestrator="TDDOrchestrator",
                test_file="tests/unit/test_example.py",
                duration_ms=1000,
                success=True,
            )
            
    def test_tdd_metric_serialization(self):
        """Test TDD metric can be serialized to dict."""
        metric = TDDMetric(
            cycle_id="550e8400-e29b-41d4-a716-446655440003",
            phase="REFACTOR",
            orchestrator="TDDOrchestrator",
            test_file="tests/unit/test_example.py",
            duration_ms=800,
            success=True,
        )
        data = metric.model_dump()
        assert data["phase"] == "REFACTOR"
        assert "timestamp" in data


@pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Metrics schema not yet implemented")
class TestDebugMetric:
    """Tests for debugging session metrics."""
    
    def test_debug_metric_creation(self):
        """Test creating a valid debug metric."""
        metric = DebugMetric(
            session_id="660e8400-e29b-41d4-a716-446655440000",
            orchestrator="DebuggingOrchestrator",
            target_file="cortex/orchestrators/core/intent_router.py",
            duration_ms=30000,
            resolved=True,
            resolution_method="log_injection",
            steps_taken=5,
        )
        assert metric.resolved is True
        assert metric.steps_taken == 5
        
    def test_debug_metric_unresolved(self):
        """Test debug metric for unresolved session."""
        metric = DebugMetric(
            session_id="660e8400-e29b-41d4-a716-446655440001",
            orchestrator="DebuggingOrchestrator",
            target_file="cortex/mcp/tools/example.py",
            duration_ms=120000,
            resolved=False,
            steps_taken=15,
        )
        assert metric.resolved is False
        assert metric.resolution_method is None


@pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Metrics schema not yet implemented")
class TestCodeGenMetric:
    """Tests for code generation metrics."""
    
    def test_codegen_metric_creation(self):
        """Test creating a valid code generation metric."""
        metric = CodeGenMetric(
            generation_id="770e8400-e29b-41d4-a716-446655440000",
            template_name="orchestrator_template",
            target_type="orchestrator",
            duration_ms=2000,
            success=True,
            customizations_applied=3,
            manual_edits_needed=False,
        )
        assert metric.template_name == "orchestrator_template"
        assert metric.customizations_applied == 3
        
    def test_codegen_metric_with_manual_edits(self):
        """Test code gen metric requiring manual edits."""
        metric = CodeGenMetric(
            generation_id="770e8400-e29b-41d4-a716-446655440001",
            template_name="test_template",
            target_type="test",
            duration_ms=1500,
            success=True,
            customizations_applied=0,
            manual_edits_needed=True,
        )
        assert metric.manual_edits_needed is True
        
    def test_codegen_metric_invalid_target_type(self):
        """Test code gen metric rejects invalid target type."""
        with pytest.raises(ValueError):
            CodeGenMetric(
                generation_id="770e8400-e29b-41d4-a716-446655440002",
                template_name="invalid_template",
                target_type="invalid_type",  # Should fail validation
                duration_ms=1000,
                success=True,
                customizations_applied=0,
                manual_edits_needed=False,
            )


@pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Metrics schema not yet implemented")
class TestOrchestratorMetric:
    """Tests for orchestrator invocation metrics."""
    
    def test_orchestrator_metric_creation(self):
        """Test creating a valid orchestrator metric."""
        metric = OrchestratorMetric(
            invocation_id="880e8400-e29b-41d4-a716-446655440000",
            orchestrator_name="MasterOrchestrator",
            operation="coordinate_operation",
            duration_ms=500,
            success=True,
        )
        assert metric.orchestrator_name == "MasterOrchestrator"
        assert metric.duration_ms == 500
        
    def test_orchestrator_metric_with_error(self):
        """Test orchestrator metric with error."""
        metric = OrchestratorMetric(
            invocation_id="880e8400-e29b-41d4-a716-446655440001",
            orchestrator_name="IntentRouter",
            operation="route_intent",
            duration_ms=150,
            success=False,
            error_type="ValidationError",
        )
        assert metric.success is False
        assert metric.error_type == "ValidationError"


@pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Metrics schema not yet implemented")
class TestMetricAggregation:
    """Tests for metric aggregation calculations."""
    
    def test_aggregation_from_tdd_metrics(self):
        """Test aggregating TDD metrics."""
        metrics = [
            TDDMetric(
                cycle_id=f"550e8400-e29b-41d4-a716-44665544000{i}",
                phase="GREEN",
                orchestrator="TDDOrchestrator",
                test_file="tests/unit/test_example.py",
                duration_ms=duration,
                success=success,
            )
            for i, (duration, success) in enumerate([
                (1000, True), (2000, True), (1500, False), (3000, True), (5000, True)
            ])
        ]
        
        agg = MetricAggregation.from_tdd_metrics(metrics)
        assert agg.count == 5
        assert agg.avg_duration_ms == 2500  # (1000+2000+1500+3000+5000)/5
        assert agg.success_rate == 0.8  # 4/5
        assert agg.p90_duration_ms >= 3000  # 90th percentile
        
    def test_aggregation_empty_metrics(self):
        """Test aggregation with empty metrics list."""
        agg = MetricAggregation.from_tdd_metrics([])
        assert agg.count == 0
        assert agg.avg_duration_ms == 0
        assert agg.success_rate == 0


@pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Metrics schema not yet implemented")
class TestEnhancementRecommendation:
    """Tests for enhancement recommendation generation."""
    
    def test_recommendation_creation(self):
        """Test creating enhancement recommendation."""
        rec = EnhancementRecommendation(
            priority="P0",
            enhancement="TDD Orchestrator Acceleration",
            evidence={
                "p90_cycle_time": 320,
                "threshold": 300,
                "sample_size": 25,
            },
            effort="M",
            expected_impact="60% cycle time reduction",
        )
        assert rec.priority == "P0"
        assert rec.evidence["p90_cycle_time"] > rec.evidence["threshold"]
        
    def test_recommendation_invalid_priority(self):
        """Test recommendation rejects invalid priority."""
        with pytest.raises(ValueError):
            EnhancementRecommendation(
                priority="P5",  # Invalid priority
                enhancement="Invalid",
                evidence={},
                effort="S",
                expected_impact="None",
            )
