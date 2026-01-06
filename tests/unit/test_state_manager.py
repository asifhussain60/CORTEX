"""
Unit tests for StateManager.

Test-first approach per CORTEX SKULL rules.

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import pytest
from datetime import datetime
from typing import Dict, Any
from src.orchestrators.state_manager import (
    StateManager,
    StateTransition,
    StateValidationError,
    StateType,
    TransitionType
)


class TestStateManager:
    """Test suite for StateManager."""
    
    @pytest.fixture
    def state_manager(self, tmp_path):
        """Create StateManager instance."""
        state_file = tmp_path / "state.json"
        return StateManager(state_file=str(state_file))
    
    def test_initialization(self, state_manager):
        """Test StateManager initializes correctly."""
        assert state_manager is not None
        assert hasattr(state_manager, 'state_file')
        assert hasattr(state_manager, 'states')
    
    def test_create_state(self, state_manager):
        """Test creating new state."""
        state_id = "plan_123"
        state_type = StateType.PLANNING
        data = {"plan_name": "test_plan", "status": "draft"}
        
        result = state_manager.create_state(state_id, state_type, data)
        
        assert result is True
        assert state_id in state_manager.states
        assert state_manager.states[state_id]["type"] == state_type
        assert state_manager.states[state_id]["data"] == data
    
    def test_create_duplicate_state_fails(self, state_manager):
        """Test creating duplicate state raises error."""
        state_id = "plan_123"
        state_manager.create_state(state_id, StateType.PLANNING, {})
        
        with pytest.raises(StateValidationError, match="already exists"):
            state_manager.create_state(state_id, StateType.PLANNING, {})
    
    def test_get_state(self, state_manager):
        """Test retrieving state."""
        state_id = "plan_123"
        data = {"status": "active"}
        state_manager.create_state(state_id, StateType.PLANNING, data)
        
        result = state_manager.get_state(state_id)
        
        assert result is not None
        assert result["data"] == data
        assert result["type"] == StateType.PLANNING
    
    def test_get_nonexistent_state_returns_none(self, state_manager):
        """Test getting non-existent state returns None."""
        result = state_manager.get_state("nonexistent")
        assert result is None
    
    def test_update_state(self, state_manager):
        """Test updating existing state."""
        state_id = "plan_123"
        state_manager.create_state(state_id, StateType.PLANNING, {"status": "draft"})
        
        new_data = {"status": "in_progress", "phase": 1}
        result = state_manager.update_state(state_id, new_data)
        
        assert result is True
        state = state_manager.get_state(state_id)
        assert state["data"] == new_data
    
    def test_update_nonexistent_state_fails(self, state_manager):
        """Test updating non-existent state raises error."""
        with pytest.raises(StateValidationError, match="not found"):
            state_manager.update_state("nonexistent", {})
    
    def test_delete_state(self, state_manager):
        """Test deleting state."""
        state_id = "plan_123"
        state_manager.create_state(state_id, StateType.PLANNING, {})
        
        result = state_manager.delete_state(state_id)
        
        assert result is True
        assert state_manager.get_state(state_id) is None
    
    def test_list_states_by_type(self, state_manager):
        """Test listing states filtered by type."""
        state_manager.create_state("plan_1", StateType.PLANNING, {})
        state_manager.create_state("exec_1", StateType.EXECUTION, {})
        state_manager.create_state("plan_2", StateType.PLANNING, {})
        
        planning_states = state_manager.list_states(state_type=StateType.PLANNING)
        
        assert len(planning_states) == 2
        assert all(s["type"] == StateType.PLANNING for s in planning_states)
    
    def test_record_transition(self, state_manager):
        """Test recording state transition."""
        state_id = "plan_123"
        state_manager.create_state(state_id, StateType.PLANNING, {"status": "draft"})
        
        transition = StateTransition(
            state_id=state_id,
            transition_type=TransitionType.STATUS_CHANGE,
            from_value="draft",
            to_value="in_progress",
            timestamp=datetime.now()
        )
        
        result = state_manager.record_transition(transition)
        
        assert result is True
        history = state_manager.get_transition_history(state_id)
        assert len(history) == 1
        assert history[0].from_value == "draft"
        assert history[0].to_value == "in_progress"
    
    def test_transition_history_ordering(self, state_manager):
        """Test transition history is ordered chronologically."""
        state_id = "plan_123"
        state_manager.create_state(state_id, StateType.PLANNING, {})
        
        # Record multiple transitions
        for i in range(3):
            transition = StateTransition(
                state_id=state_id,
                transition_type=TransitionType.STATUS_CHANGE,
                from_value=f"status_{i}",
                to_value=f"status_{i+1}",
                timestamp=datetime.now()
            )
            state_manager.record_transition(transition)
        
        history = state_manager.get_transition_history(state_id)
        
        assert len(history) == 3
        # Should be in chronological order
        for i in range(len(history) - 1):
            assert history[i].timestamp <= history[i+1].timestamp
    
    def test_validate_state(self, state_manager):
        """Test state validation."""
        state_id = "plan_123"
        state_manager.create_state(state_id, StateType.PLANNING, {"status": "draft"})
        
        is_valid = state_manager.validate_state(state_id)
        
        assert is_valid is True
    
    def test_persist_state(self, state_manager, tmp_path):
        """Test persisting state to disk."""
        state_id = "plan_123"
        state_manager.create_state(state_id, StateType.PLANNING, {"status": "active"})
        
        result = state_manager.persist()
        
        assert result is True
        # Verify file was created
        assert (tmp_path / "state.json").exists()
    
    def test_load_state(self, tmp_path):
        """Test loading state from disk."""
        # Create and persist state
        state_file = tmp_path / "state.json"
        manager1 = StateManager(state_file=str(state_file))
        manager1.create_state("plan_123", StateType.PLANNING, {"status": "active"})
        manager1.persist()
        
        # Load in new instance
        manager2 = StateManager(state_file=str(state_file))
        manager2.load()
        
        state = manager2.get_state("plan_123")
        assert state is not None
        assert state["data"]["status"] == "active"
    
    def test_clear_states(self, state_manager):
        """Test clearing all states."""
        state_manager.create_state("plan_1", StateType.PLANNING, {})
        state_manager.create_state("plan_2", StateType.PLANNING, {})
        
        result = state_manager.clear()
        
        assert result is True
        assert len(state_manager.states) == 0
    
    def test_get_metrics(self, state_manager):
        """Test retrieving state metrics."""
        state_manager.create_state("plan_1", StateType.PLANNING, {})
        state_manager.create_state("exec_1", StateType.EXECUTION, {})
        
        metrics = state_manager.get_metrics()
        
        assert metrics["total_states"] == 2
        assert StateType.PLANNING in metrics["by_type"]
        assert StateType.EXECUTION in metrics["by_type"]
