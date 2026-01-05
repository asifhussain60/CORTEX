"""
Test suite for orchestrator integration layer.

Tests cover:
- AuditedOrchestrator base class functionality
- Audit operation context manager
- Error recovery integration
- Handoff logging
- State transition tracking
- Performance metric logging
- Health check system
"""

import asyncio
import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch

from src.logging.integration import AuditedOrchestrator, OrchestratorHealthCheck
from src.logging.audit_logger import AuditLogger, LogLevel
from src.logging.self_healing_engine import SelfHealingEngine


class TestAuditedOrchestrator:
    """Test AuditedOrchestrator base class."""
    
    @pytest.fixture
    def temp_log_dir(self):
        """Create temporary log directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
    
    @pytest.fixture
    def audit_logger(self, temp_log_dir):
        """Create audit logger instance."""
        return AuditLogger({"log_dir": str(temp_log_dir)})
    
    @pytest.fixture
    def self_healing_engine(self, audit_logger):
        """Create self-healing engine instance."""
        return SelfHealingEngine(
            audit_logger=audit_logger,
            analysis_interval=1.0,
            auto_recovery_enabled=True
        )
    
    @pytest.fixture
    def audited_orchestrator(self, audit_logger, self_healing_engine):
        """Create audited orchestrator instance."""
        return AuditedOrchestrator(
            orchestrator_name="test_orchestrator",
            audit_logger=audit_logger,
            self_healing_engine=self_healing_engine,
            enable_recovery=True
        )
    
    def test_orchestrator_initialization(self, audited_orchestrator):
        """Test orchestrator initializes correctly."""
        assert audited_orchestrator.orchestrator_name == "test_orchestrator"
        assert audited_orchestrator.enable_recovery is True
        assert audited_orchestrator.audit_logger is not None
        assert audited_orchestrator.self_healing_engine is not None
    
    def test_orchestrator_initialization_without_logger(self):
        """Test orchestrator creates default logger if none provided."""
        orch = AuditedOrchestrator(orchestrator_name="test")
        assert orch.audit_logger is not None
        assert orch.orchestrator_name == "test"
    
    def test_set_session_context(self, audited_orchestrator):
        """Test session context setting."""
        session_id = "test-session-123"
        correlation_id = "test-correlation-456"
        
        audited_orchestrator.set_session_context(session_id, correlation_id)
        
        assert audited_orchestrator.current_session_id == session_id
        assert audited_orchestrator.current_correlation_id == correlation_id
    
    def test_set_session_context_auto_correlation(self, audited_orchestrator):
        """Test auto-generation of correlation ID."""
        session_id = "test-session-123"
        
        audited_orchestrator.set_session_context(session_id)
        
        assert audited_orchestrator.current_session_id == session_id
        assert audited_orchestrator.current_correlation_id is not None
        assert len(audited_orchestrator.current_correlation_id) > 0
    
    @pytest.mark.asyncio
    async def test_audit_operation_success(self, audited_orchestrator):
        """Test successful operation auditing."""
        operation_completed = False
        
        async with audited_orchestrator.audit_operation("test_operation"):
            operation_completed = True
            await asyncio.sleep(0.01)  # Simulate work
        
        assert operation_completed is True
        
        # Check that events were logged
        events = audited_orchestrator.audit_logger._event_cache
        assert len(events) >= 2  # Start and complete events
        
        # Verify start event
        start_event = next((e for e in events if "started" in e["event"]), None)
        assert start_event is not None
        assert start_event["orchestrator"] == "test_orchestrator"
        
        # Verify complete event
        complete_event = next((e for e in events if "completed" in e["event"]), None)
        assert complete_event is not None
        assert "duration_ms" in complete_event["data"]
    
    @pytest.mark.asyncio
    async def test_audit_operation_with_context(self, audited_orchestrator):
        """Test operation auditing with context data."""
        context_data = {"user_id": "123", "request_type": "test"}
        
        async with audited_orchestrator.audit_operation("test_operation", context=context_data):
            await asyncio.sleep(0.01)
        
        events = audited_orchestrator.audit_logger._event_cache
        start_event = next((e for e in events if "started" in e["event"]), None)
        
        assert start_event is not None
        assert start_event["data"]["context"] == context_data
    
    @pytest.mark.asyncio
    async def test_audit_operation_error(self, audited_orchestrator):
        """Test error logging in audited operation."""
        with pytest.raises(ValueError):
            async with audited_orchestrator.audit_operation("test_operation"):
                raise ValueError("Test error")
        
        events = audited_orchestrator.audit_logger._event_cache
        error_event = next((e for e in events if "failed" in e["event"]), None)
        
        assert error_event is not None
        assert error_event["level"] == "ERROR"
        assert "Test error" in error_event["data"]["error"]
        assert error_event["data"]["error_type"] == "ValueError"
    
    @pytest.mark.asyncio
    async def test_log_handoff(self, audited_orchestrator):
        """Test orchestrator handoff logging."""
        handoff_data = {"plan_id": "123", "phase": "execution"}
        
        await audited_orchestrator.log_handoff(
            target_orchestrator="planning_v5",
            handoff_data=handoff_data
        )
        
        events = audited_orchestrator.audit_logger._event_cache
        handoff_event = next((e for e in events if e["event"] == "orchestrator_handoff"), None)
        
        assert handoff_event is not None
        assert handoff_event["data"]["source"] == "test_orchestrator"
        assert handoff_event["data"]["target"] == "planning_v5"
        assert handoff_event["data"]["handoff_data"] == handoff_data
    
    @pytest.mark.asyncio
    async def test_log_state_transition(self, audited_orchestrator):
        """Test state transition logging."""
        await audited_orchestrator.log_state_transition(
            from_state="initializing",
            to_state="executing",
            context={"step": 1}
        )
        
        events = audited_orchestrator.audit_logger._event_cache
        transition_event = next((e for e in events if e["event"] == "state_transition"), None)
        
        assert transition_event is not None
        assert transition_event["data"]["from_state"] == "initializing"
        assert transition_event["data"]["to_state"] == "executing"
        assert transition_event["data"]["context"]["step"] == 1
    
    @pytest.mark.asyncio
    async def test_log_performance_metric(self, audited_orchestrator):
        """Test performance metric logging."""
        await audited_orchestrator.log_performance_metric(
            metric_name="response_time",
            value=123.45,
            unit="ms"
        )
        
        events = audited_orchestrator.audit_logger._event_cache
        metric_event = next((e for e in events if e["event"] == "performance_metric"), None)
        
        assert metric_event is not None
        assert metric_event["data"]["metric"] == "response_time"
        assert metric_event["data"]["value"] == 123.45
        assert metric_event["data"]["unit"] == "ms"


class TestOrchestratorHealthCheck:
    """Test OrchestratorHealthCheck system."""
    
    @pytest.fixture
    def temp_log_dir(self):
        """Create temporary log directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
    
    @pytest.fixture
    def audit_logger(self, temp_log_dir):
        """Create audit logger instance."""
        return AuditLogger({"log_dir": str(temp_log_dir)})
    
    @pytest.fixture
    def health_check(self, audit_logger):
        """Create health check instance."""
        return OrchestratorHealthCheck(audit_logger=audit_logger)
    
    @pytest.mark.asyncio
    async def test_check_orchestrator_health(self, health_check):
        """Test individual orchestrator health check."""
        health_status = await health_check.check_orchestrator_health("planning_v5")
        
        assert health_status["orchestrator"] == "planning_v5"
        assert health_status["status"] == "healthy"
        assert "last_check" in health_status
        assert "error_rate" in health_status
        assert "avg_response_time_ms" in health_status
    
    @pytest.mark.asyncio
    async def test_get_system_health(self, health_check):
        """Test system-wide health check."""
        system_health = await health_check.get_system_health()
        
        assert system_health["status"] == "healthy"
        assert "timestamp" in system_health
        assert "orchestrators_checked" in system_health
        assert "total_errors" in system_health
        assert system_health["self_healing_enabled"] is True


class TestIntegrationScenarios:
    """Test realistic integration scenarios."""
    
    @pytest.fixture
    def temp_log_dir(self):
        """Create temporary log directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
    
    @pytest.fixture
    def full_stack(self, temp_log_dir):
        """Create full integration stack."""
        audit_logger = AuditLogger({"log_dir": str(temp_log_dir)})
        self_healing_engine = SelfHealingEngine(
            audit_logger=audit_logger,
            analysis_interval=1.0
        )
        orchestrator = AuditedOrchestrator(
            orchestrator_name="integration_test",
            audit_logger=audit_logger,
            self_healing_engine=self_healing_engine
        )
        health_check = OrchestratorHealthCheck(audit_logger=audit_logger)
        
        return {
            "orchestrator": orchestrator,
            "health_check": health_check,
            "audit_logger": audit_logger,
            "self_healing_engine": self_healing_engine
        }
    
    @pytest.mark.asyncio
    async def test_end_to_end_workflow(self, full_stack):
        """Test complete workflow with multiple operations."""
        orch = full_stack["orchestrator"]
        health_check = full_stack["health_check"]
        
        # Set session context
        orch.set_session_context("session-123", "corr-456")
        
        # Execute operation 1
        async with orch.audit_operation("operation_1"):
            await asyncio.sleep(0.01)
        
        # Log handoff
        await orch.log_handoff("target_orch", {"data": "test"})
        
        # Execute operation 2
        async with orch.audit_operation("operation_2"):
            await orch.log_state_transition("state_1", "state_2")
            await asyncio.sleep(0.01)
        
        # Log performance metric
        await orch.log_performance_metric("latency", 50.5)
        
        # Check health
        health = await health_check.check_orchestrator_health("integration_test")
        
        # Verify all events logged
        events = orch.audit_logger._event_cache
        assert len(events) >= 7  # 2 ops * 2 events + handoff + transition + metric
        
        # Verify health check works
        assert health["status"] == "healthy"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
