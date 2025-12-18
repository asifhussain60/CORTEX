"""
Unit tests for PhaseManager (CORTEX 4.0)

Tests phase registration, transitions, status tracking, and error handling.
"""

import pytest
from datetime import datetime
from src.orchestration_4_0.base.phase_manager import (
    PhaseManager,
    Phase,
    PhaseStatus,
    PhaseTransition
)


class TestPhaseRegistration:
    """Test phase registration functionality"""
    
    def test_register_simple_phase(self):
        """Test registering a basic phase"""
        manager = PhaseManager("test_orchestrator")
        
        phase = manager.register_phase(
            name="setup",
            description="Setup phase"
        )
        
        assert phase.name == "setup"
        assert phase.description == "Setup phase"
        assert phase.required is True
        assert phase.status == PhaseStatus.PENDING
        assert len(manager.phases) == 1
    
    def test_register_optional_phase(self):
        """Test registering an optional phase"""
        manager = PhaseManager("test_orchestrator")
        
        phase = manager.register_phase(
            name="optional",
            description="Optional phase",
            required=False
        )
        
        assert phase.required is False
    
    def test_register_phase_with_validation(self):
        """Test registering phase with validation function"""
        manager = PhaseManager("test_orchestrator")
        
        def validate():
            return True
        
        phase = manager.register_phase(
            name="validated",
            description="Phase with validation",
            validation=validate
        )
        
        assert phase.validation is not None
        assert phase.validation() is True
    
    def test_register_phase_with_cleanup(self):
        """Test registering phase with cleanup function"""
        manager = PhaseManager("test_orchestrator")
        cleanup_called = []
        
        def cleanup():
            cleanup_called.append(True)
        
        phase = manager.register_phase(
            name="with_cleanup",
            description="Phase with cleanup",
            cleanup=cleanup
        )
        
        assert phase.cleanup is not None
        phase.cleanup()
        assert cleanup_called == [True]
    
    def test_register_multiple_phases(self):
        """Test registering multiple phases"""
        manager = PhaseManager("test_orchestrator")
        
        manager.register_phase("phase1", "Phase 1")
        manager.register_phase("phase2", "Phase 2")
        manager.register_phase("phase3", "Phase 3")
        
        assert len(manager.phases) == 3
        assert [p.name for p in manager.phases] == ["phase1", "phase2", "phase3"]


class TestPhaseExecution:
    """Test phase execution and transitions"""
    
    def test_start_phase(self):
        """Test starting a phase"""
        manager = PhaseManager("test_orchestrator")
        manager.register_phase("setup", "Setup phase")
        
        manager.start_phase("setup")
        
        phase = manager._get_phase("setup")
        assert phase.status == PhaseStatus.IN_PROGRESS
        assert phase.started_at is not None
        assert manager.current_phase == phase
    
    def test_start_phase_runs_validation(self):
        """Test that validation runs before phase starts"""
        manager = PhaseManager("test_orchestrator")
        validation_called = []
        
        def validate():
            validation_called.append(True)
            return True
        
        manager.register_phase("validated", "Validated phase", validation=validate)
        manager.start_phase("validated")
        
        assert validation_called == [True]
    
    def test_start_phase_validation_failure(self):
        """Test that failed validation prevents phase start"""
        manager = PhaseManager("test_orchestrator")
        
        def validate():
            return False
        
        manager.register_phase("validated", "Validated phase", validation=validate)
        
        with pytest.raises(ValueError, match="Validation failed"):
            manager.start_phase("validated")
    
    def test_complete_phase(self):
        """Test completing a phase"""
        manager = PhaseManager("test_orchestrator")
        manager.register_phase("setup", "Setup phase")
        manager.start_phase("setup")
        
        result = {"data": "test"}
        manager.complete_phase("setup", result)
        
        phase = manager._get_phase("setup")
        assert phase.status == PhaseStatus.COMPLETED
        assert phase.completed_at is not None
        assert phase.result == result
    
    def test_complete_phase_runs_cleanup(self):
        """Test that cleanup runs after phase completes"""
        manager = PhaseManager("test_orchestrator")
        cleanup_called = []
        
        def cleanup():
            cleanup_called.append(True)
        
        manager.register_phase("with_cleanup", "Phase with cleanup", cleanup=cleanup)
        manager.start_phase("with_cleanup")
        manager.complete_phase("with_cleanup")
        
        assert cleanup_called == [True]
    
    def test_fail_phase(self):
        """Test failing a phase"""
        manager = PhaseManager("test_orchestrator")
        manager.register_phase("setup", "Setup phase")
        manager.start_phase("setup")
        
        manager.fail_phase("setup", "Test error")
        
        phase = manager._get_phase("setup")
        assert phase.status == PhaseStatus.FAILED
        assert phase.error == "Test error"
        assert phase.completed_at is not None
    
    def test_skip_phase(self):
        """Test skipping a phase"""
        manager = PhaseManager("test_orchestrator")
        manager.register_phase("optional", "Optional phase")
        
        manager.skip_phase("optional", "Not needed")
        
        phase = manager._get_phase("optional")
        assert phase.status == PhaseStatus.SKIPPED
        assert phase.error == "Not needed"
    
    def test_phase_transition_tracking(self):
        """Test that phase transitions are tracked"""
        manager = PhaseManager("test_orchestrator")
        manager.register_phase("phase1", "Phase 1")
        manager.register_phase("phase2", "Phase 2")
        
        manager.start_phase("phase1")
        manager.complete_phase("phase1")
        manager.start_phase("phase2")
        
        assert len(manager.transitions) == 1
        transition = manager.transitions[0]
        assert transition.from_phase == "phase1"
        assert transition.to_phase == "phase2"
        assert transition.timestamp is not None


class TestPhaseProgress:
    """Test progress tracking functionality"""
    
    def test_get_progress_empty(self):
        """Test progress with no phases"""
        manager = PhaseManager("test_orchestrator")
        progress = manager.get_progress()
        
        assert progress["total_phases"] == 0
        assert progress["completed"] == 0
        assert progress["progress_percent"] == 0
    
    def test_get_progress_all_pending(self):
        """Test progress with all phases pending"""
        manager = PhaseManager("test_orchestrator")
        manager.register_phase("phase1", "Phase 1")
        manager.register_phase("phase2", "Phase 2")
        
        progress = manager.get_progress()
        
        assert progress["total_phases"] == 2
        assert progress["pending"] == 2
        assert progress["completed"] == 0
        assert progress["progress_percent"] == 0
    
    def test_get_progress_partial_completion(self):
        """Test progress with some phases complete"""
        manager = PhaseManager("test_orchestrator")
        manager.register_phase("phase1", "Phase 1")
        manager.register_phase("phase2", "Phase 2")
        manager.register_phase("phase3", "Phase 3")
        
        manager.start_phase("phase1")
        manager.complete_phase("phase1")
        manager.start_phase("phase2")
        
        progress = manager.get_progress()
        
        assert progress["total_phases"] == 3
        assert progress["completed"] == 1
        assert progress["in_progress"] == 1
        assert progress["pending"] == 1
        assert progress["progress_percent"] == pytest.approx(33.33, rel=0.01)
        assert progress["current_phase"] == "phase2"
    
    def test_get_progress_all_complete(self):
        """Test progress with all phases complete"""
        manager = PhaseManager("test_orchestrator")
        manager.register_phase("phase1", "Phase 1")
        manager.register_phase("phase2", "Phase 2")
        
        manager.start_phase("phase1")
        manager.complete_phase("phase1")
        manager.start_phase("phase2")
        manager.complete_phase("phase2")
        
        progress = manager.get_progress()
        
        assert progress["total_phases"] == 2
        assert progress["completed"] == 2
        assert progress["progress_percent"] == 100.0
    
    def test_get_progress_with_failures(self):
        """Test progress tracking with failed phases"""
        manager = PhaseManager("test_orchestrator")
        manager.register_phase("phase1", "Phase 1")
        manager.register_phase("phase2", "Phase 2")
        
        manager.start_phase("phase1")
        manager.fail_phase("phase1", "Error")
        
        progress = manager.get_progress()
        
        assert progress["failed"] == 1
        assert progress["completed"] == 0


class TestPhaseStatus:
    """Test phase status queries"""
    
    def test_get_phase_status(self):
        """Test getting phase status"""
        manager = PhaseManager("test_orchestrator")
        manager.register_phase("setup", "Setup phase")
        
        assert manager.get_phase_status("setup") == PhaseStatus.PENDING
        
        manager.start_phase("setup")
        assert manager.get_phase_status("setup") == PhaseStatus.IN_PROGRESS
        
        manager.complete_phase("setup")
        assert manager.get_phase_status("setup") == PhaseStatus.COMPLETED
    
    def test_get_nonexistent_phase(self):
        """Test getting status of non-existent phase"""
        manager = PhaseManager("test_orchestrator")
        
        with pytest.raises(ValueError, match="Phase not found"):
            manager.get_phase_status("nonexistent")


class TestPhaseReset:
    """Test phase manager reset functionality"""
    
    def test_reset(self):
        """Test resetting all phases"""
        manager = PhaseManager("test_orchestrator")
        manager.register_phase("phase1", "Phase 1")
        manager.register_phase("phase2", "Phase 2")
        
        manager.start_phase("phase1")
        manager.complete_phase("phase1")
        manager.start_phase("phase2")
        
        manager.reset()
        
        # Check all phases reset to pending
        for phase in manager.phases:
            assert phase.status == PhaseStatus.PENDING
            assert phase.started_at is None
            assert phase.completed_at is None
            assert phase.error is None
            assert phase.result is None
        
        # Check state cleared
        assert manager.current_phase is None
        assert len(manager.transitions) == 0


class TestEdgeCases:
    """Test edge cases and error conditions"""
    
    def test_start_already_running_phase(self):
        """Test starting a phase that's already running"""
        manager = PhaseManager("test_orchestrator")
        manager.register_phase("setup", "Setup phase")
        manager.start_phase("setup")
        
        with pytest.raises(ValueError, match="already in progress"):
            manager.start_phase("setup")
    
    def test_start_completed_phase(self):
        """Test starting a phase that's already completed"""
        manager = PhaseManager("test_orchestrator")
        manager.register_phase("setup", "Setup phase")
        manager.start_phase("setup")
        manager.complete_phase("setup")
        
        with pytest.raises(ValueError, match="already completed"):
            manager.start_phase("setup")
    
    def test_complete_not_in_progress_phase(self):
        """Test completing a phase that's not in progress"""
        manager = PhaseManager("test_orchestrator")
        manager.register_phase("setup", "Setup phase")
        
        with pytest.raises(ValueError, match="not in progress"):
            manager.complete_phase("setup")
    
    def test_fail_not_in_progress_phase(self):
        """Test failing a phase that's not in progress"""
        manager = PhaseManager("test_orchestrator")
        manager.register_phase("setup", "Setup phase")
        
        with pytest.raises(ValueError, match="not in progress"):
            manager.fail_phase("setup", "Error")
