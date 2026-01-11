"""
Unit tests for Orchestrator Lifecycle Management
================================================
Tests lifecycle states, transitions, and health checks for orchestrators.

Author: GitHub Copilot (for CORTEX)
Created: 2026-01-08
Feature: feat04-core-orchestration
Task: 1.4
TDD Phase: RED
"""

import pytest
import time
from datetime import datetime
from pathlib import Path
from src.orchestrators.middleware.orchestrator_lifecycle import (
    OrchestratorLifecycle,
    LifecycleState,
    LifecycleTransition,
    LifecycleError,
    HealthStatus,
    HealthCheck
)


class TestLifecycleStates:
    """Test lifecycle state management"""
    
    @pytest.fixture
    def lifecycle(self):
        """Create lifecycle manager"""
        return OrchestratorLifecycle(orchestrator_id="test-orchestrator")
    
    @pytest.mark.ac_id("AC-LIFECYCLE-001")
    def test_initial_state_is_initialized(self, lifecycle):
        """Should start in INITIALIZED state"""
        assert lifecycle.current_state == LifecycleState.INITIALIZED
        assert lifecycle.previous_state is None
    
    def test_transition_to_ready(self, lifecycle):
        """Should transition from INITIALIZED to READY"""
        lifecycle.transition_to(LifecycleState.READY)
        
        assert lifecycle.current_state == LifecycleState.READY
        assert lifecycle.previous_state == LifecycleState.INITIALIZED
    
    def test_transition_to_running(self, lifecycle):
        """Should transition through READY to RUNNING"""
        lifecycle.transition_to(LifecycleState.READY)
        lifecycle.transition_to(LifecycleState.RUNNING)
        
        assert lifecycle.current_state == LifecycleState.RUNNING
        assert lifecycle.previous_state == LifecycleState.READY
    
    def test_transition_to_paused(self, lifecycle):
        """Should pause from RUNNING state"""
        lifecycle.transition_to(LifecycleState.READY)
        lifecycle.transition_to(LifecycleState.RUNNING)
        lifecycle.transition_to(LifecycleState.PAUSED)
        
        assert lifecycle.current_state == LifecycleState.PAUSED
    
    def test_transition_to_stopped(self, lifecycle):
        """Should stop from any state"""
        lifecycle.transition_to(LifecycleState.READY)
        lifecycle.transition_to(LifecycleState.RUNNING)
        lifecycle.transition_to(LifecycleState.STOPPED)
        
        assert lifecycle.current_state == LifecycleState.STOPPED
    
    def test_transition_to_error(self, lifecycle):
        """Should transition to ERROR from any state"""
        lifecycle.transition_to(LifecycleState.READY)
        lifecycle.transition_to(LifecycleState.ERROR, error="Test error")
        
        assert lifecycle.current_state == LifecycleState.ERROR
        assert lifecycle.last_error == "Test error"


class TestInvalidTransitions:
    """Test invalid state transitions"""
    
    @pytest.fixture
    def lifecycle(self):
        return OrchestratorLifecycle(orchestrator_id="test-orchestrator")
    
    @pytest.mark.ac_id("AC-LIFECYCLE-002")
    def test_cannot_run_without_ready(self, lifecycle):
        """Should not transition to RUNNING without being READY"""
        with pytest.raises(LifecycleError) as exc_info:
            lifecycle.transition_to(LifecycleState.RUNNING)
        
        assert "invalid transition" in str(exc_info.value).lower()
    
    def test_cannot_pause_without_running(self, lifecycle):
        """Should not pause unless RUNNING"""
        lifecycle.transition_to(LifecycleState.READY)
        
        with pytest.raises(LifecycleError):
            lifecycle.transition_to(LifecycleState.PAUSED)
    
    def test_cannot_resume_without_paused(self, lifecycle):
        """Should not resume unless PAUSED"""
        with pytest.raises(LifecycleError):
            lifecycle.resume()


class TestLifecycleCallbacks:
    """Test lifecycle event callbacks"""
    
    @pytest.fixture
    def lifecycle(self):
        return OrchestratorLifecycle(orchestrator_id="test-orchestrator")
    
    def test_on_state_change_callback(self, lifecycle):
        """Should invoke callback on state change"""
        callback_invoked = []
        
        def callback(old_state, new_state):
            callback_invoked.append((old_state, new_state))
        
        lifecycle.on_state_change(callback)
        lifecycle.transition_to(LifecycleState.READY)
        
        assert len(callback_invoked) == 1
        assert callback_invoked[0] == (LifecycleState.INITIALIZED, LifecycleState.READY)
    
    def test_on_error_callback(self, lifecycle):
        """Should invoke callback on error"""
        error_captured = []
        
        def callback(error_msg):
            error_captured.append(error_msg)
        
        lifecycle.on_error(callback)
        lifecycle.transition_to(LifecycleState.ERROR, error="Test error")
        
        assert len(error_captured) == 1
        assert error_captured[0] == "Test error"
    
    def test_multiple_callbacks(self, lifecycle):
        """Should support multiple callbacks"""
        calls = []
        
        lifecycle.on_state_change(lambda old, new: calls.append(1))
        lifecycle.on_state_change(lambda old, new: calls.append(2))
        
        lifecycle.transition_to(LifecycleState.READY)
        
        assert calls == [1, 2]


class TestHealthChecks:
    """Test health check functionality"""
    
    @pytest.fixture
    def lifecycle(self):
        return OrchestratorLifecycle(orchestrator_id="test-orchestrator")
    
    def test_register_health_check(self, lifecycle):
        """Should register health check"""
        def check():
            return HealthStatus.HEALTHY
        
        lifecycle.register_health_check("test_check", check)
        
        health = lifecycle.get_health()
        assert "test_check" in health.checks
        assert health.checks["test_check"] == HealthStatus.HEALTHY
    
    def test_unhealthy_check_detection(self, lifecycle):
        """Should detect unhealthy checks"""
        def unhealthy_check():
            return HealthStatus.UNHEALTHY
        
        lifecycle.register_health_check("failing_check", unhealthy_check)
        
        health = lifecycle.get_health()
        assert health.overall_status == HealthStatus.UNHEALTHY
    
    def test_degraded_check_detection(self, lifecycle):
        """Should detect degraded status"""
        lifecycle.register_health_check("check1", lambda: HealthStatus.HEALTHY)
        lifecycle.register_health_check("check2", lambda: HealthStatus.DEGRADED)
        
        health = lifecycle.get_health()
        assert health.overall_status == HealthStatus.DEGRADED
    
    def test_health_check_exception_handling(self, lifecycle):
        """Should handle exceptions in health checks"""
        def failing_check():
            raise Exception("Check failed")
        
        lifecycle.register_health_check("exception_check", failing_check)
        
        health = lifecycle.get_health()
        assert health.checks["exception_check"] == HealthStatus.UNHEALTHY


class TestLifecycleTimestamps:
    """Test lifecycle timestamp tracking"""
    
    @pytest.fixture
    def lifecycle(self):
        return OrchestratorLifecycle(orchestrator_id="test-orchestrator")
    
    @pytest.mark.ac_id("AC-LIFECYCLE-003")
    def test_tracks_state_entry_time(self, lifecycle):
        """Should track when state was entered"""
        before = datetime.now()
        lifecycle.transition_to(LifecycleState.READY)
        after = datetime.now()
        
        entry_time = lifecycle.get_state_entry_time(LifecycleState.READY)
        
        assert entry_time is not None
        assert before <= entry_time <= after
    
    def test_tracks_time_in_state(self, lifecycle):
        """Should track duration in current state"""
        lifecycle.transition_to(LifecycleState.READY)
        time.sleep(0.1)
        
        duration = lifecycle.get_time_in_current_state()
        
        assert duration >= 0.1
    
    def test_tracks_total_uptime(self, lifecycle):
        """Should track total uptime"""
        lifecycle.transition_to(LifecycleState.READY)
        lifecycle.transition_to(LifecycleState.RUNNING)
        time.sleep(0.1)
        
        uptime = lifecycle.get_uptime()
        
        assert uptime >= 0.1


class TestLifecycleHistory:
    """Test lifecycle history tracking"""
    
    @pytest.fixture
    def lifecycle(self):
        return OrchestratorLifecycle(orchestrator_id="test-orchestrator")
    
    def test_records_transition_history(self, lifecycle):
        """Should record all transitions"""
        lifecycle.transition_to(LifecycleState.READY)
        lifecycle.transition_to(LifecycleState.RUNNING)
        lifecycle.transition_to(LifecycleState.PAUSED)
        
        history = lifecycle.get_history()
        
        assert len(history) == 3
        assert history[0].from_state == LifecycleState.INITIALIZED
        assert history[0].to_state == LifecycleState.READY
        assert history[2].to_state == LifecycleState.PAUSED
    
    def test_history_includes_timestamps(self, lifecycle):
        """Should include timestamps in history"""
        lifecycle.transition_to(LifecycleState.READY)
        
        history = lifecycle.get_history()
        
        assert history[0].timestamp is not None
        assert isinstance(history[0].timestamp, datetime)
    
    def test_history_includes_error_info(self, lifecycle):
        """Should include error information in history"""
        lifecycle.transition_to(LifecycleState.ERROR, error="Test error")
        
        history = lifecycle.get_history()
        error_entry = [h for h in history if h.to_state == LifecycleState.ERROR][0]
        
        assert error_entry.error == "Test error"


class TestLifecycleAuditLogging:
    """Test audit log integration"""
    
    @pytest.fixture
    def lifecycle(self):
        return OrchestratorLifecycle(orchestrator_id="test-orchestrator")
    
    def test_logs_state_transitions(self, lifecycle):
        """Should log all state transitions"""
        lifecycle.transition_to(LifecycleState.READY)
        
        # Check audit log was called
        assert lifecycle.last_audit_entry is not None
        assert "→" in lifecycle.last_audit_entry
        assert "ready" in lifecycle.last_audit_entry.lower()
    
    def test_logs_errors_with_context(self, lifecycle):
        """Should log errors with full context"""
        lifecycle.transition_to(LifecycleState.ERROR, error="Critical failure")
        
        assert lifecycle.last_audit_entry is not None
        assert "error" in lifecycle.last_audit_entry.lower()
        assert "Critical failure" in lifecycle.last_audit_entry


class TestLifecycleStateMachine:
    """Test state machine validation"""
    
    @pytest.fixture
    def lifecycle(self):
        return OrchestratorLifecycle(orchestrator_id="test-orchestrator")
    
    def test_valid_transitions_defined(self, lifecycle):
        """Should have valid transitions defined"""
        valid_transitions = lifecycle.get_valid_transitions(LifecycleState.READY)
        
        assert LifecycleState.RUNNING in valid_transitions
        assert LifecycleState.STOPPED in valid_transitions
        assert LifecycleState.ERROR in valid_transitions
    
    def test_can_transition_check(self, lifecycle):
        """Should check if transition is valid"""
        assert lifecycle.can_transition_to(LifecycleState.READY) is True
        assert lifecycle.can_transition_to(LifecycleState.RUNNING) is False
    
    def test_get_next_allowed_states(self, lifecycle):
        """Should return list of allowed next states"""
        lifecycle.transition_to(LifecycleState.READY)
        
        allowed = lifecycle.get_next_allowed_states()
        
        assert LifecycleState.RUNNING in allowed
        assert LifecycleState.PAUSED not in allowed
