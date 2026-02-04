"""
Tests for InstrumentationOrchestrator - Coordinate metrics capture and enhancement triggers.

TDD Phase: RED
Author: Asif Hussain
Created: 2026-02-04
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock, AsyncMock

# Import will fail until we implement (RED phase)
try:
    from cortex.orchestrators.support.instrumentation_orchestrator import (
        InstrumentationOrchestrator,
        get_instrumentation_orchestrator,
    )
    from cortex.observability.metrics_schema import (
        TDDMetric,
        DebugMetric,
        EnhancementRecommendation,
    )
    IMPORTS_AVAILABLE = True
except ImportError:
    IMPORTS_AVAILABLE = False


@pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Instrumentation orchestrator not yet implemented")
class TestInstrumentationOrchestrator:
    """Tests for InstrumentationOrchestrator functionality."""
    
    def test_orchestrator_singleton(self):
        """Test orchestrator is singleton."""
        orch1 = get_instrumentation_orchestrator()
        orch2 = get_instrumentation_orchestrator()
        assert orch1 is orch2
        
    def test_orchestrator_initialization(self):
        """Test orchestrator initializes with default thresholds."""
        orch = InstrumentationOrchestrator()
        
        assert orch.thresholds is not None
        assert "tdd_cycle_time_p90" in orch.thresholds
        assert "debugger_failure_rate" in orch.thresholds
        
    def test_record_tdd_cycle(self):
        """Test recording a TDD cycle."""
        orch = InstrumentationOrchestrator()
        
        result = orch.record_tdd_cycle(
            phase="RED",
            orchestrator="TDDOrchestrator",
            test_file="tests/unit/test_example.py",
            duration_ms=1500,
            success=True,
        )
        
        assert result.success is True
        assert result.metric_id is not None
        
    def test_record_debug_session(self):
        """Test recording a debug session."""
        orch = InstrumentationOrchestrator()
        
        result = orch.record_debug_session(
            orchestrator="DebuggingOrchestrator",
            target_file="cortex/orchestrators/core/intent_router.py",
            duration_ms=30000,
            resolved=True,
            resolution_method="log_injection",
            steps_taken=5,
        )
        
        assert result.success is True
        
    def test_record_codegen(self):
        """Test recording code generation."""
        orch = InstrumentationOrchestrator()
        
        result = orch.record_codegen(
            template_name="orchestrator_template",
            target_type="orchestrator",
            duration_ms=2000,
            success=True,
            customizations_applied=3,
            manual_edits_needed=False,
        )
        
        assert result.success is True
        
    def test_record_orchestrator_invocation(self):
        """Test recording orchestrator invocation."""
        orch = InstrumentationOrchestrator()
        
        result = orch.record_orchestrator_invocation(
            orchestrator_name="MasterOrchestrator",
            operation="coordinate_operation",
            duration_ms=500,
            success=True,
        )
        
        assert result.success is True
        
    def test_check_thresholds_no_breach(self):
        """Test checking thresholds when none breached."""
        orch = InstrumentationOrchestrator()
        
        # Record metrics below threshold
        for i in range(10):
            orch.record_tdd_cycle(
                phase="GREEN",
                orchestrator="TDDOrchestrator",
                test_file="tests/unit/test_example.py",
                duration_ms=60000,  # 60s, below 300s threshold
                success=True,
            )
            
        recommendations = orch.check_thresholds()
        
        assert len(recommendations) == 0
        
    def test_check_thresholds_tdd_breach(self):
        """Test checking thresholds when TDD cycle time breached."""
        orch = InstrumentationOrchestrator()
        
        # Record metrics above threshold
        for i in range(15):
            orch.record_tdd_cycle(
                phase="GREEN",
                orchestrator="TDDOrchestrator",
                test_file="tests/unit/test_example.py",
                duration_ms=400000,  # 400s, above 300s threshold
                success=True,
            )
            
        recommendations = orch.check_thresholds()
        
        assert len(recommendations) >= 1
        tdd_rec = next((r for r in recommendations if "TDD" in r.enhancement), None)
        assert tdd_rec is not None
        assert tdd_rec.priority == "P0"
        
    def test_check_thresholds_debug_failure_breach(self):
        """Test checking thresholds when debug failure rate breached."""
        orch = InstrumentationOrchestrator()
        
        # Record metrics with high failure rate (>5%)
        for i in range(20):
            orch.record_debug_session(
                orchestrator="DebuggingOrchestrator",
                target_file="cortex/orchestrators/core/intent_router.py",
                duration_ms=30000,
                resolved=i < 18,  # 2 failures = 10% failure rate
                steps_taken=5,
            )
            
        recommendations = orch.check_thresholds()
        
        debug_rec = next((r for r in recommendations if "Debugger" in r.enhancement), None)
        assert debug_rec is not None
        assert debug_rec.priority == "P0"
        
    def test_get_metrics_summary(self):
        """Test getting metrics summary."""
        from cortex.observability.metrics_collector import MetricsCollector
        
        # Use isolated collector for this test
        collector = MetricsCollector()
        orch = InstrumentationOrchestrator(collector=collector)
        
        # Record various metrics
        orch.record_tdd_cycle(
            phase="RED",
            orchestrator="TDDOrchestrator",
            test_file="tests/unit/test_example.py",
            duration_ms=1500,
            success=True,
        )
        orch.record_debug_session(
            orchestrator="DebuggingOrchestrator",
            target_file="cortex/orchestrators/core/intent_router.py",
            duration_ms=30000,
            resolved=True,
            steps_taken=5,
        )
        
        summary = orch.get_metrics_summary()
        
        assert "tdd" in summary
        assert "debug" in summary
        assert summary["tdd"]["count"] == 1
        assert summary["debug"]["count"] == 1
        
    def test_get_enhancement_recommendations(self):
        """Test getting enhancement recommendations."""
        orch = InstrumentationOrchestrator()
        
        # Record metrics that breach multiple thresholds
        for i in range(20):
            orch.record_tdd_cycle(
                phase="GREEN",
                orchestrator="TDDOrchestrator",
                test_file="tests/unit/test_example.py",
                duration_ms=350000,  # 350s
                success=True,
            )
            
        recommendations = orch.get_enhancement_recommendations()
        
        assert isinstance(recommendations, list)
        if len(recommendations) > 0:
            rec = recommendations[0]
            assert isinstance(rec, EnhancementRecommendation)
            assert rec.evidence is not None
            
    def test_export_metrics_report(self):
        """Test exporting metrics report."""
        orch = InstrumentationOrchestrator()
        
        # Record some metrics
        orch.record_tdd_cycle(
            phase="RED",
            orchestrator="TDDOrchestrator",
            test_file="tests/unit/test_example.py",
            duration_ms=1500,
            success=True,
        )
        
        report = orch.export_metrics_report(format="yaml")
        
        assert "tdd_metrics" in report or "metrics" in report
        
    def test_clear_metrics(self):
        """Test clearing all metrics."""
        from cortex.observability.metrics_collector import MetricsCollector
        
        # Use isolated collector for this test
        collector = MetricsCollector()
        orch = InstrumentationOrchestrator(collector=collector)
        
        orch.record_tdd_cycle(
            phase="RED",
            orchestrator="TDDOrchestrator",
            test_file="tests/unit/test_example.py",
            duration_ms=1500,
            success=True,
        )
        
        summary = orch.get_metrics_summary()
        assert summary["tdd"]["count"] == 1
        
        orch.clear_metrics()
        
        summary = orch.get_metrics_summary()
        assert summary["tdd"]["count"] == 0


@pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Instrumentation orchestrator not yet implemented")
class TestInstrumentationOrchestratorAsync:
    """Tests for async InstrumentationOrchestrator methods."""
    
    @pytest.mark.asyncio
    async def test_async_record_tdd_cycle(self):
        """Test async recording of TDD cycle."""
        orch = InstrumentationOrchestrator()
        
        result = await orch.async_record_tdd_cycle(
            phase="GREEN",
            orchestrator="TDDOrchestrator",
            test_file="tests/unit/test_example.py",
            duration_ms=2000,
            success=True,
        )
        
        assert result.success is True
        
    @pytest.mark.asyncio
    async def test_async_check_thresholds(self):
        """Test async threshold checking."""
        orch = InstrumentationOrchestrator()
        
        recommendations = await orch.async_check_thresholds()
        
        assert isinstance(recommendations, list)


@pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Instrumentation orchestrator not yet implemented")
class TestThresholdConfiguration:
    """Tests for threshold configuration."""
    
    def test_custom_thresholds(self):
        """Test setting custom thresholds."""
        orch = InstrumentationOrchestrator(
            thresholds={
                "tdd_cycle_time_p90": 600,  # 10 min instead of 5 min
                "debugger_failure_rate": 0.10,  # 10% instead of 5%
            }
        )
        
        assert orch.thresholds["tdd_cycle_time_p90"] == 600
        assert orch.thresholds["debugger_failure_rate"] == 0.10
        
    def test_update_thresholds(self):
        """Test updating thresholds at runtime."""
        orch = InstrumentationOrchestrator()
        
        orch.update_threshold("tdd_cycle_time_p90", 400)
        
        assert orch.thresholds["tdd_cycle_time_p90"] == 400
        
    def test_invalid_threshold_name(self):
        """Test updating invalid threshold raises error."""
        orch = InstrumentationOrchestrator()
        
        with pytest.raises(KeyError):
            orch.update_threshold("invalid_threshold", 100)
