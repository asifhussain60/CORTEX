"""
Tests for BaseOrchestrator adaptive execution integration.

Tests cover:
- Execution mode parameter acceptance
- Safety guardrail integration
- Checkpoint creation/restoration
- Auto-rollback behavior
- Validation gate enforcement
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Import BaseOrchestrator components
from src.orchestrators.base.base_orchestrator import (
    BaseOrchestrator,
    OrchestratorResult,
    OrchestratorStatus,
    ValidationResult
)

# Import adaptive execution components
from src.operations.modules.orchestration.adaptive_execution import (
    ExecutionMode,
    AdaptiveExecutionConfig,
    SafetyGuardrail
)


class TestBaseOrchestratorExecutionMode:
    """Test execution mode parameter handling."""
    
    def test_default_execution_mode_is_supervised(self):
        """BaseOrchestrator defaults to SUPERVISED mode if not specified."""
        config = {"name": "test_orchestrator", "version": "4.0.0"}
        orchestrator = ConcreteOrchestrator(config)
        
        assert orchestrator.execution_mode == ExecutionMode.SUPERVISED
    
    def test_execution_mode_can_be_set_to_autonomous(self):
        """BaseOrchestrator accepts AUTONOMOUS execution mode."""
        config = {
            "name": "test_orchestrator",
            "version": "4.0.0",
            "execution_mode": ExecutionMode.AUTONOMOUS
        }
        orchestrator = ConcreteOrchestrator(config)
        
        assert orchestrator.execution_mode == ExecutionMode.AUTONOMOUS
    
    def test_execution_mode_can_be_set_to_hybrid(self):
        """BaseOrchestrator accepts HYBRID execution mode."""
        config = {
            "name": "test_orchestrator",
            "version": "4.0.0",
            "execution_mode": ExecutionMode.HYBRID
        }
        orchestrator = ConcreteOrchestrator(config)
        
        assert orchestrator.execution_mode == ExecutionMode.HYBRID


class TestBaseOrchestratorSafetyGuardrail:
    """Test safety guardrail integration."""
    
    def test_safety_guardrail_initialized_with_orchestrator(self):
        """BaseOrchestrator initializes SafetyGuardrail on creation."""
        config = {"name": "test_orchestrator", "version": "4.0.0"}
        orchestrator = ConcreteOrchestrator(config)
        
        assert isinstance(orchestrator.safety_guardrail, SafetyGuardrail)
    
    def test_safety_guardrail_uses_adaptive_config(self):
        """SafetyGuardrail is configured with AdaptiveExecutionConfig."""
        config = {
            "name": "test_orchestrator",
            "version": "4.0.0",
            "adaptive_config": {
                "safety_keywords": ["delete", "drop", "truncate"]
            }
        }
        orchestrator = ConcreteOrchestrator(config)
        
        # SafetyGuardrail should have been initialized with custom config
        assert orchestrator.safety_guardrail.config is not None


class TestBaseOrchestratorCheckpointManagement:
    """Test checkpoint creation and restoration."""
    
    def test_create_checkpoint_stores_current_state(self):
        """BaseOrchestrator can create checkpoints of current execution state."""
        config = {"name": "test_orchestrator", "version": "4.0.0"}
        orchestrator = ConcreteOrchestrator(config)
        
        checkpoint = orchestrator.create_checkpoint(phase="test_phase", state={"data": "test"})
        
        assert checkpoint is not None
        assert checkpoint["phase"] == "test_phase"
        assert checkpoint["state"]["data"] == "test"
        assert "timestamp" in checkpoint
    
    def test_restore_checkpoint_recovers_previous_state(self):
        """BaseOrchestrator can restore from checkpoint."""
        config = {"name": "test_orchestrator", "version": "4.0.0"}
        orchestrator = ConcreteOrchestrator(config)
        
        # Create checkpoint
        checkpoint = orchestrator.create_checkpoint(phase="phase1", state={"step": 1})
        
        # Modify state
        orchestrator.current_phase = "phase2"
        
        # Restore checkpoint
        restored = orchestrator.restore_checkpoint(checkpoint["checkpoint_id"])
        
        assert restored is True
        assert orchestrator.current_phase == "phase1"
    
    def test_list_checkpoints_returns_all_saved_checkpoints(self):
        """BaseOrchestrator maintains list of all checkpoints."""
        config = {"name": "test_orchestrator", "version": "4.0.0"}
        orchestrator = ConcreteOrchestrator(config)
        
        # Create multiple checkpoints
        orchestrator.create_checkpoint(phase="phase1", state={"step": 1})
        orchestrator.create_checkpoint(phase="phase2", state={"step": 2})
        
        checkpoints = orchestrator.list_checkpoints()
        
        assert len(checkpoints) == 2
        assert checkpoints[0]["phase"] == "phase1"
        assert checkpoints[1]["phase"] == "phase2"


class TestBaseOrchestratorAutoRollback:
    """Test automatic rollback on failure."""
    
    def test_auto_rollback_enabled_in_autonomous_mode(self):
        """AUTONOMOUS mode enables auto-rollback by default."""
        config = {
            "name": "test_orchestrator",
            "version": "4.0.0",
            "execution_mode": ExecutionMode.AUTONOMOUS
        }
        orchestrator = ConcreteOrchestrator(config)
        
        assert orchestrator.auto_rollback_enabled is True
    
    def test_auto_rollback_disabled_in_supervised_mode(self):
        """SUPERVISED mode disables auto-rollback."""
        config = {
            "name": "test_orchestrator",
            "version": "4.0.0",
            "execution_mode": ExecutionMode.SUPERVISED
        }
        orchestrator = ConcreteOrchestrator(config)
        
        assert orchestrator.auto_rollback_enabled is False
    
    def test_auto_rollback_triggers_on_execution_failure(self):
        """Auto-rollback restores last checkpoint when execution fails."""
        config = {
            "name": "test_orchestrator",
            "version": "4.0.0",
            "execution_mode": ExecutionMode.AUTONOMOUS
        }
        orchestrator = FailingOrchestrator(config)
        
        # Create checkpoint before execution
        orchestrator.create_checkpoint(phase="pre_execution", state={"safe": True})
        
        # Run orchestrator (will fail)
        result = orchestrator.run()
        
        # Should have auto-rolled back
        assert result.data.get("rolled_back") is True
        assert result.data.get("checkpoint_restored") is not None


class TestBaseOrchestratorValidationGates:
    """Test validation gates enforcement."""
    
    def test_validation_gate_blocks_unsafe_action_in_supervised_mode(self):
        """SUPERVISED mode blocks execution if validation fails."""
        config = {
            "name": "test_orchestrator",
            "version": "4.0.0",
            "execution_mode": ExecutionMode.SUPERVISED
        }
        orchestrator = ConcreteOrchestrator(config)
        
        # Try to execute unsafe action
        action = {"type": "delete", "target": "production_db"}
        result = orchestrator.validate_action(action)
        
        assert result.valid is False
        assert "unsafe" in result.errors[0].lower() or "delete" in result.errors[0].lower()
    
    def test_validation_gate_allows_safe_action(self):
        """Validation gate allows safe actions through."""
        config = {"name": "test_orchestrator", "version": "4.0.0"}
        orchestrator = ConcreteOrchestrator(config)
        
        # Try to execute safe action
        action = {"type": "read", "target": "config"}
        result = orchestrator.validate_action(action)
        
        assert result.valid is True


class TestBaseOrchestratorAdaptiveBehavior:
    """Test mode-specific behavior integration."""
    
    def test_supervised_mode_requires_confirmation_per_phase(self):
        """SUPERVISED mode should pause for confirmation at each phase."""
        config = {
            "name": "test_orchestrator",
            "version": "4.0.0",
            "execution_mode": ExecutionMode.SUPERVISED
        }
        orchestrator = MultiPhaseOrchestrator(config)
        
        result = orchestrator.run()
        
        # Should have paused for confirmation (simulated as requires_confirmation flag)
        assert result.data.get("confirmations_required") > 0
    
    def test_autonomous_mode_executes_all_phases_without_confirmation(self):
        """AUTONOMOUS mode executes all phases without pausing."""
        config = {
            "name": "test_orchestrator",
            "version": "4.0.0",
            "execution_mode": ExecutionMode.AUTONOMOUS
        }
        orchestrator = MultiPhaseOrchestrator(config)
        
        result = orchestrator.run()
        
        # Should have executed all phases without confirmation
        assert result.data.get("confirmations_required") == 0
        assert result.data.get("phases_completed") > 1


# ============================================================================
# TEST FIXTURES - Concrete orchestrator implementations for testing
# ============================================================================

class ConcreteOrchestrator(BaseOrchestrator):
    """Concrete orchestrator for testing base functionality."""
    
    def __init__(self, config):
        super().__init__(config)
        self.current_phase = None
    
    def execute(self) -> OrchestratorResult:
        """Simple execution that returns success."""
        return OrchestratorResult(
            status=OrchestratorStatus.COMPLETED,
            success=True,
            message="Execution complete"
        )


class FailingOrchestrator(BaseOrchestrator):
    """Orchestrator that always fails (for rollback testing)."""
    
    def execute(self) -> OrchestratorResult:
        """Execution that raises an exception."""
        raise RuntimeError("Simulated execution failure")


class MultiPhaseOrchestrator(BaseOrchestrator):
    """Orchestrator with multiple phases (for adaptive behavior testing)."""
    
    def execute(self) -> OrchestratorResult:
        """Execute multiple phases based on execution mode."""
        phases_completed = 0
        confirmations_required = 0
        
        # Simulate 3 phases
        for phase in ["phase1", "phase2", "phase3"]:
            if self.execution_mode == ExecutionMode.SUPERVISED:
                # In supervised mode, would require confirmation
                confirmations_required += 1
            
            phases_completed += 1
        
        return OrchestratorResult(
            status=OrchestratorStatus.COMPLETED,
            success=True,
            message=f"Completed {phases_completed} phases",
            data={
                "phases_completed": phases_completed,
                "confirmations_required": confirmations_required
            }
        )
