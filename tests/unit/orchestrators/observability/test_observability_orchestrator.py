"""ObservabilityOrchestrator tests."""
import pytest
from cortex.orchestrators.observability.observability_orchestrator import ObservabilityOrchestrator

class TestObservabilityOrchestrator:
    @pytest.fixture
    def orch(self) -> ObservabilityOrchestrator:
        return ObservabilityOrchestrator(service_name="test")
    
    def test_record_metric(self, orch: ObservabilityOrchestrator) -> None:
        orch.record_metric("test_counter", 1.0, metric_type="counter")
        metrics = orch.get_metrics()
        assert "test_counter" in metrics
    
    def test_start_span(self, orch: ObservabilityOrchestrator) -> None:
        span = orch.start_span("test_op")
        assert span is not None
    
    def test_end_span(self, orch: ObservabilityOrchestrator) -> None:
        span = orch.start_span("test_op")
        orch.end_span(span)
        assert span.duration_ms > 0
    
    def test_create_alert(self, orch: ObservabilityOrchestrator) -> None:
        alert_id = orch.create_alert("WARNING", "Test", "test")
        assert alert_id
        assert len(orch.get_alerts()) > 0
    
    def test_get_metrics(self, orch: ObservabilityOrchestrator) -> None:
        orch.record_metric("m1", 10.0)
        orch.record_metric("m2", 20.0)
        assert len(orch.get_metrics()) >= 2
