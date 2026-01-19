"""
AC-REM-011-05: Cross-Phase State Consistency Validation Tests

Comprehensive test suite verifying state consistency across all phases
(Comprehension→LENS→Delegation→Execution). Validates state mutations,
carryover, and consistency without data loss or corruption.

CORE-008: Tests created before implementation (TDD).
CORE-011: All functions have type hints.
CORE-012: All methods have Google-style docstrings.
"""

import pytest
from typing import Any, Dict, List
from unittest.mock import Mock, patch
import uuid
import threading

try:
    from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
    from cortex.brain.core.state_manager import StateManager, get_state_manager, OperationState
except (ImportError, ModuleNotFoundError):
    MasterOrchestrator = None
    StateManager = None
    get_state_manager = None
    OperationState = None


@pytest.mark.skipif(
    StateManager is None or MasterOrchestrator is None,
    reason="StateManager or MasterOrchestrator not available"
)
class TestCrossPhaseStateConsistency:
    """AC-REM-011-05: Cross-phase state consistency validation tests."""

    @pytest.fixture
    def state_manager(self) -> Any:
        """Get fresh StateManager instance."""
        if StateManager is None:
            pytest.skip("StateManager not available")
        return StateManager()

    @pytest.fixture
    def master_orchestrator(self) -> Any:
        """Get Master Orchestrator instance."""
        if MasterOrchestrator is None:
            pytest.skip("MasterOrchestrator not available")
        return MasterOrchestrator.instance()

    @pytest.fixture
    def operation_id(self) -> str:
        """Generate unique operation ID."""
        return f"op_{uuid.uuid4().hex[:8]}"

    def test_state_preserved_phase1_to_phase2(self, state_manager: Any, operation_id: str) -> None:
        """Test: Phase 1→Phase 2 state carryover complete."""
        state = state_manager.create_operation(
            operation_id=operation_id,
            user_intent="Test intent",
            priority=1
        )
        assert state.operation_id == operation_id
        assert state.current_phase == 1
        
        phase_1_output = {"analysis": "complete", "intent_type": "TEST"}
        success = state_manager.transition_phase(
            operation_id=operation_id,
            from_phase=1,
            to_phase=2,
            phase_output=phase_1_output
        )
        assert success is True
        
        updated_state = state_manager.get_operation_state(operation_id)
        assert updated_state is not None
        assert updated_state.current_phase == 2
        assert updated_state.get_phase_output(1) == phase_1_output
        assert updated_state.user_intent == "Test intent"

    def test_state_preserved_phase2_to_phase3(self, state_manager: Any, operation_id: str) -> None:
        """Test: Phase 2→Phase 3 state carryover complete."""
        state_manager.create_operation(
            operation_id=operation_id,
            user_intent="Test intent",
            priority=1
        )
        
        phase_1_output = {"analysis": "complete"}
        state_manager.transition_phase(
            operation_id=operation_id,
            from_phase=1,
            to_phase=2,
            phase_output=phase_1_output
        )
        
        phase_2_output = {"routing_decision": "DOMAIN_A"}
        success = state_manager.transition_phase(
            operation_id=operation_id,
            from_phase=2,
            to_phase=3,
            phase_output=phase_2_output
        )
        assert success is True
        
        updated_state = state_manager.get_operation_state(operation_id)
        assert updated_state.current_phase == 3
        assert updated_state.get_phase_output(1) == phase_1_output
        assert updated_state.get_phase_output(2) == phase_2_output

    def test_state_preserved_phase3_to_phase4(self, state_manager: Any, operation_id: str) -> None:
        """Test: Phase 3→Phase 4 state carryover complete."""
        state_manager.create_operation(
            operation_id=operation_id,
            user_intent="Test intent"
        )
        
        state_manager.transition_phase(
            operation_id=operation_id,
            from_phase=1,
            to_phase=2,
            phase_output={"phase": 1}
        )
        
        state_manager.transition_phase(
            operation_id=operation_id,
            from_phase=2,
            to_phase=3,
            phase_output={"phase": 2}
        )
        
        phase_3_output = {"delegation_complete": True}
        success = state_manager.transition_phase(
            operation_id=operation_id,
            from_phase=3,
            to_phase=4,
            phase_output=phase_3_output
        )
        assert success is True
        
        updated_state = state_manager.get_operation_state(operation_id)
        assert updated_state.current_phase == 4

    def test_context_mutations_isolated(self, state_manager: Any, operation_id: str) -> None:
        """Test: Phase mutations don't corrupt sibling states."""
        state_manager.create_operation(
            operation_id=operation_id,
            user_intent="Original intent"
        )
        
        phase_1_output = {
            "data": {"nested": {"value": "original"}},
            "list": [1, 2, 3]
        }
        state_manager.transition_phase(
            operation_id=operation_id,
            from_phase=1,
            to_phase=2,
            phase_output=phase_1_output
        )
        
        context = state_manager.get_context_for_phase(
            operation_id=operation_id,
            target_phase=2
        )
        assert context is not None
        assert context["phase_1_output"] == phase_1_output
        
        if "phase_1_output" in context:
            context["phase_1_output"]["data"]["nested"]["value"] = "modified"
        
        original_state = state_manager.get_operation_state(operation_id)
        assert original_state.get_phase_output(1)["data"]["nested"]["value"] == "original"

    def test_user_intent_carryover(self, state_manager: Any, operation_id: str) -> None:
        """Test: Original user intent preserved across all phases."""
        original_intent = "Build a new feature"
        
        state = state_manager.create_operation(
            operation_id=operation_id,
            user_intent=original_intent,
            priority=2
        )
        assert state.user_intent == original_intent
        
        for phase in range(1, 4):
            state_manager.transition_phase(
                operation_id=operation_id,
                from_phase=phase,
                to_phase=phase + 1,
                phase_output={"phase": phase}
            )
        
        final_state = state_manager.get_operation_state(operation_id)
        assert final_state.user_intent == original_intent
        assert final_state.priority == 2

    def test_intermediate_results_consistency(self, state_manager: Any, operation_id: str) -> None:
        """Test: Intermediate results match between phases."""
        state_manager.create_operation(
            operation_id=operation_id,
            user_intent="Test"
        )
        
        phase_1_output = {"step": "completed", "value": 42}
        state_manager.transition_phase(
            operation_id=operation_id,
            from_phase=1,
            to_phase=2,
            phase_output=phase_1_output
        )
        
        phase_2_output = {"step": "processed", "input_from_phase_1": phase_1_output}
        state_manager.transition_phase(
            operation_id=operation_id,
            from_phase=2,
            to_phase=3,
            phase_output=phase_2_output
        )
        
        state = state_manager.get_operation_state(operation_id)
        assert state.get_phase_output(1) == phase_1_output
        assert state.get_phase_output(2)["input_from_phase_1"] == phase_1_output

    def test_no_state_loss_on_error(self, state_manager: Any, operation_id: str) -> None:
        """Test: State preserved even when phase fails."""
        state_manager.create_operation(
            operation_id=operation_id,
            user_intent="Test"
        )
        
        phase_1_output = {"status": "completed"}
        state_manager.transition_phase(
            operation_id=operation_id,
            from_phase=1,
            to_phase=2,
            phase_output=phase_1_output
        )
        
        success = state_manager.transition_phase(
            operation_id=operation_id,
            from_phase=1,
            to_phase=3,
            phase_output={"status": "error"}
        )
        assert success is False
        
        state = state_manager.get_operation_state(operation_id)
        assert state.current_phase == 2
        assert state.get_phase_output(1) == phase_1_output

    def test_multi_turn_state_isolation(self, state_manager: Any) -> None:
        """Test: Multi-turn sessions don't interfere."""
        op_id_1 = f"op_{uuid.uuid4().hex[:8]}"
        op_id_2 = f"op_{uuid.uuid4().hex[:8]}"
        
        state_manager.create_operation(
            operation_id=op_id_1,
            user_intent="Operation 1"
        )
        
        state_manager.create_operation(
            operation_id=op_id_2,
            user_intent="Operation 2"
        )
        
        state_manager.transition_phase(
            operation_id=op_id_1,
            from_phase=1,
            to_phase=2,
            phase_output={"op": 1}
        )
        
        state_manager.transition_phase(
            operation_id=op_id_2,
            from_phase=1,
            to_phase=3,
            phase_output={"op": 2}
        )
        
        state_1 = state_manager.get_operation_state(op_id_1)
        state_2 = state_manager.get_operation_state(op_id_2)
        
        assert state_1.current_phase == 2
        assert state_2.current_phase == 3
        assert state_1.user_intent == "Operation 1"
        assert state_2.user_intent == "Operation 2"

    def test_state_consistency_under_concurrency(self, state_manager: Any) -> None:
        """Test: Concurrent operations maintain state consistency."""
        op_ids = [f"op_{uuid.uuid4().hex[:8]}" for _ in range(3)]
        results: List[Any] = []
        
        def transition_operation(op_id: str) -> None:
            """Worker function for concurrent transitions."""
            state_manager.create_operation(
                operation_id=op_id,
                user_intent=f"Operation {op_id}"
            )
            
            for phase in range(1, 4):
                success = state_manager.transition_phase(
                    operation_id=op_id,
                    from_phase=phase,
                    to_phase=phase + 1,
                    phase_output={"phase": phase}
                )
                results.append((op_id, phase, success))
        
        threads = [
            threading.Thread(target=transition_operation, args=(op_id,))
            for op_id in op_ids
        ]
        
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()
        
        assert all(success for _, _, success in results)
        
        for op_id in op_ids:
            state = state_manager.get_operation_state(op_id)
            assert state.current_phase == 4

    def test_audit_trail_consistency(self, state_manager: Any, operation_id: str) -> None:
        """Test: Audit trail matches actual state transitions."""
        state_manager.create_operation(
            operation_id=operation_id,
            user_intent="Test"
        )
        
        transitions = [
            (1, 2, {"step": "phase_1_complete"}),
            (2, 3, {"step": "phase_2_complete"}),
            (3, 4, {"step": "phase_3_complete"})
        ]
        
        for from_phase, to_phase, output in transitions:
            state_manager.transition_phase(
                operation_id=operation_id,
                from_phase=from_phase,
                to_phase=to_phase,
                phase_output=output
            )
        
        state = state_manager.get_operation_state(operation_id)
        
        assert state.current_phase == 4
        for i, (from_phase, _, output) in enumerate(transitions, start=1):
            assert state.get_phase_output(from_phase) == output

    def test_rollback_state_recovery(self, state_manager: Any, operation_id: str) -> None:
        """Test: Rollback recovers to consistent prior state."""
        state_manager.create_operation(
            operation_id=operation_id,
            user_intent="Test"
        )
        
        state_manager.transition_phase(
            operation_id=operation_id,
            from_phase=1,
            to_phase=2,
            phase_output={"data": "phase_1"}
        )
        
        state_manager.transition_phase(
            operation_id=operation_id,
            from_phase=2,
            to_phase=3,
            phase_output={"data": "phase_2"}
        )
        
        state = state_manager.get_operation_state(operation_id)
        assert state.current_phase == 3
        
        success = state_manager.rollback_to_phase(
            operation_id=operation_id,
            target_phase=1
        )
        assert success is True
        
        rolled_back = state_manager.get_operation_state(operation_id)
        assert rolled_back.current_phase == 1
        assert rolled_back.user_intent == "Test"

    def test_phase_decision_consistency(self, state_manager: Any, operation_id: str) -> None:
        """Test: Routing decisions consistent across runs."""
        state_manager.create_operation(
            operation_id=operation_id,
            user_intent="Test intent"
        )
        
        decision_output = {"routing": "DOMAIN_A", "confidence": 0.95}
        state_manager.transition_phase(
            operation_id=operation_id,
            from_phase=1,
            to_phase=2,
            phase_output=decision_output
        )
        
        context = state_manager.get_context_for_phase(
            operation_id=operation_id,
            target_phase=2
        )
        
        assert context["phase_1_output"] == decision_output

    def test_confidence_scores_propagation(self, state_manager: Any, operation_id: str) -> None:
        """Test: Confidence scores propagate without modification."""
        state_manager.create_operation(
            operation_id=operation_id,
            user_intent="Test"
        )
        
        phase_1_output = {"confidence": 0.85, "intent": "IMPLEMENT"}
        state_manager.transition_phase(
            operation_id=operation_id,
            from_phase=1,
            to_phase=2,
            phase_output=phase_1_output
        )
        
        context = state_manager.get_context_for_phase(
            operation_id=operation_id,
            target_phase=2
        )
        
        assert context["phase_1_output"]["confidence"] == 0.85

    def test_knowledge_lookup_consistency(self, state_manager: Any, operation_id: str) -> None:
        """Test: Knowledge lookups return same results across phases."""
        state_manager.create_operation(
            operation_id=operation_id,
            user_intent="Test"
        )
        
        knowledge = {"domain": "test", "facts": ["A", "B", "C"]}
        
        state_manager.transition_phase(
            operation_id=operation_id,
            from_phase=1,
            to_phase=2,
            phase_output={"knowledge": knowledge}
        )
        
        context = state_manager.get_context_for_phase(
            operation_id=operation_id,
            target_phase=2
        )
        
        assert context["phase_1_output"]["knowledge"] == knowledge

    def test_execution_context_immutability(self, state_manager: Any, operation_id: str) -> None:
        """Test: Execution context immutable during delegation."""
        state_manager.create_operation(
            operation_id=operation_id,
            user_intent="Test"
        )
        
        execution_context = {"immutable": True, "version": 1}
        state_manager.transition_phase(
            operation_id=operation_id,
            from_phase=1,
            to_phase=2,
            phase_output=execution_context
        )
        
        context = state_manager.get_context_for_phase(
            operation_id=operation_id,
            target_phase=2
        )
        context["phase_1_output"]["immutable"] = False
        
        state = state_manager.get_operation_state(operation_id)
        assert state.get_phase_output(1)["immutable"] is True

    def test_state_snapshot_integrity(self, state_manager: Any, operation_id: str) -> None:
        """Test: State snapshots capture consistent point-in-time."""
        state_manager.create_operation(
            operation_id=operation_id,
            user_intent="Test"
        )
        
        state_manager.transition_phase(
            operation_id=operation_id,
            from_phase=1,
            to_phase=2,
            phase_output={"snapshot_test": True}
        )
        
        stats = state_manager.get_statistics()
        assert stats["active_operations"] >= 1
        assert stats["total_snapshots"] > 0

    def test_cross_phase_timeout_consistency(self, state_manager: Any, operation_id: str) -> None:
        """Test: Timeouts respected consistently across phases."""
        state_manager.create_operation(
            operation_id=operation_id,
            user_intent="Test"
        )
        
        state_manager.update_metadata(
            operation_id=operation_id,
            key="timeout_ms",
            value=5000
        )
        
        state_manager.transition_phase(
            operation_id=operation_id,
            from_phase=1,
            to_phase=2,
            phase_output={"timeout_respected": True}
        )
        
        state = state_manager.get_operation_state(operation_id)
        assert state.metadata["timeout_ms"] == 5000

    def test_error_state_consistency(self, state_manager: Any, operation_id: str) -> None:
        """Test: Error state consistent across phase boundaries."""
        state_manager.create_operation(
            operation_id=operation_id,
            user_intent="Test"
        )
        
        error_output = {"error": "Phase 1 failed", "error_code": "P1_FAIL"}
        state_manager.transition_phase(
            operation_id=operation_id,
            from_phase=1,
            to_phase=2,
            phase_output=error_output
        )
        
        context = state_manager.get_context_for_phase(
            operation_id=operation_id,
            target_phase=2
        )
        
        assert context["phase_1_output"]["error_code"] == "P1_FAIL"

    def test_priority_level_carryover(self, state_manager: Any, operation_id: str) -> None:
        """Test: Priority levels maintained across all phases."""
        priority = 5
        state = state_manager.create_operation(
            operation_id=operation_id,
            user_intent="Test",
            priority=priority
        )
        assert state.priority == priority
        
        for phase in range(1, 4):
            state_manager.transition_phase(
                operation_id=operation_id,
                from_phase=phase,
                to_phase=phase + 1,
                phase_output={"phase": phase}
            )
        
        final_state = state_manager.get_operation_state(operation_id)
        assert final_state.priority == priority

    def test_resource_allocation_consistency(self, state_manager: Any, operation_id: str) -> None:
        """Test: Resource allocations consistent phase-to-phase."""
        state_manager.create_operation(
            operation_id=operation_id,
            user_intent="Test"
        )
        
        state_manager.transition_phase(
            operation_id=operation_id,
            from_phase=1,
            to_phase=2,
            phase_output={
                "resources_allocated": {
                    "cpu": "2", 
                    "memory_mb": 512,
                    "disk_gb": 10
                }
            }
        )
        
        context = state_manager.get_context_for_phase(
            operation_id=operation_id,
            target_phase=2
        )
        
        resources = context["phase_1_output"]["resources_allocated"]
        assert resources["cpu"] == "2"
        assert resources["memory_mb"] == 512


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
