"""
State Manager - Cross-orchestrator state coordination.

Manages state lifecycle, transitions, and persistence for CORTEX orchestrators.

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import json
import logging
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, Any, Optional, List


class StateType(str, Enum):
    """Types of states managed by StateManager."""
    PLANNING = "planning"
    EXECUTION = "execution"
    VALIDATION = "validation"
    COORDINATION = "coordination"


class TransitionType(str, Enum):
    """Types of state transitions."""
    STATUS_CHANGE = "status_change"
    PHASE_CHANGE = "phase_change"
    DATA_UPDATE = "data_update"
    ERROR = "error"


@dataclass
class StateTransition:
    """Record of a state transition."""
    state_id: str
    transition_type: TransitionType
    from_value: Any
    to_value: Any
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "state_id": self.state_id,
            "transition_type": self.transition_type.value,
            "from_value": str(self.from_value),
            "to_value": str(self.to_value),
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata or {}
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StateTransition":
        """Create from dictionary."""
        return cls(
            state_id=data["state_id"],
            transition_type=TransitionType(data["transition_type"]),
            from_value=data["from_value"],
            to_value=data["to_value"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            metadata=data.get("metadata")
        )


class StateValidationError(Exception):
    """Raised when state validation fails."""
    pass


class StateManager:
    """
    Manages cross-orchestrator state coordination.
    
    Provides:
    - State creation, retrieval, update, deletion
    - State transition tracking
    - State persistence and loading
    - State validation
    - Metrics collection
    """
    
    def __init__(self, state_file: Optional[str] = None):
        """
        Initialize StateManager.
        
        Args:
            state_file: Path to state persistence file
        """
        self.logger = logging.getLogger("cortex.orchestrators.state_manager")
        self.state_file = Path(state_file) if state_file else None
        self.states: Dict[str, Dict[str, Any]] = {}
        self.transitions: Dict[str, List[StateTransition]] = {}
        
        # Load existing state if file exists
        if self.state_file and self.state_file.exists():
            self.load()
        
        self.logger.info("StateManager initialized")
    
    def create_state(
        self, 
        state_id: str, 
        state_type: StateType, 
        data: Dict[str, Any]
    ) -> bool:
        """
        Create new state.
        
        Args:
            state_id: Unique state identifier
            state_type: Type of state
            data: State data
            
        Returns:
            True if created successfully
            
        Raises:
            StateValidationError: If state already exists
        """
        if state_id in self.states:
            raise StateValidationError(f"State {state_id} already exists")
        
        self.states[state_id] = {
            "type": state_type,
            "data": data,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        self.logger.debug(f"Created state: {state_id} (type: {state_type})")
        return True
    
    def get_state(self, state_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve state by ID.
        
        Args:
            state_id: State identifier
            
        Returns:
            State data or None if not found
        """
        return self.states.get(state_id)
    
    def update_state(self, state_id: str, data: Dict[str, Any]) -> bool:
        """
        Update existing state.
        
        Args:
            state_id: State identifier
            data: New state data
            
        Returns:
            True if updated successfully
            
        Raises:
            StateValidationError: If state not found
        """
        if state_id not in self.states:
            raise StateValidationError(f"State {state_id} not found")
        
        self.states[state_id]["data"] = data
        self.states[state_id]["updated_at"] = datetime.now().isoformat()
        
        self.logger.debug(f"Updated state: {state_id}")
        return True
    
    def delete_state(self, state_id: str) -> bool:
        """
        Delete state.
        
        Args:
            state_id: State identifier
            
        Returns:
            True if deleted successfully
        """
        if state_id in self.states:
            del self.states[state_id]
            if state_id in self.transitions:
                del self.transitions[state_id]
            self.logger.debug(f"Deleted state: {state_id}")
            return True
        return False
    
    def list_states(
        self, 
        state_type: Optional[StateType] = None
    ) -> List[Dict[str, Any]]:
        """
        List all states, optionally filtered by type.
        
        Args:
            state_type: Optional type filter
            
        Returns:
            List of states
        """
        states = []
        for state_id, state_data in self.states.items():
            if state_type is None or state_data["type"] == state_type:
                states.append({
                    "state_id": state_id,
                    **state_data
                })
        return states
    
    def record_transition(self, transition: StateTransition) -> bool:
        """
        Record state transition.
        
        Args:
            transition: Transition to record
            
        Returns:
            True if recorded successfully
        """
        state_id = transition.state_id
        if state_id not in self.transitions:
            self.transitions[state_id] = []
        
        self.transitions[state_id].append(transition)
        self.logger.debug(
            f"Recorded transition for {state_id}: "
            f"{transition.from_value} -> {transition.to_value}"
        )
        return True
    
    def get_transition_history(
        self, 
        state_id: str
    ) -> List[StateTransition]:
        """
        Get transition history for state.
        
        Args:
            state_id: State identifier
            
        Returns:
            List of transitions in chronological order
        """
        transitions = self.transitions.get(state_id, [])
        # Sort by timestamp
        return sorted(transitions, key=lambda t: t.timestamp)
    
    def validate_state(self, state_id: str) -> bool:
        """
        Validate state integrity.
        
        Args:
            state_id: State identifier
            
        Returns:
            True if valid
        """
        state = self.get_state(state_id)
        if not state:
            return False
        
        # Basic validation: must have type and data
        required_fields = ["type", "data", "created_at", "updated_at"]
        return all(field in state for field in required_fields)
    
    def persist(self) -> bool:
        """
        Persist states to disk.
        
        Returns:
            True if persisted successfully
        """
        if not self.state_file:
            self.logger.warning("No state file configured, skipping persist")
            return False
        
        try:
            # Convert to serializable format
            data = {
                "states": self.states,
                "transitions": {
                    state_id: [t.to_dict() for t in transitions]
                    for state_id, transitions in self.transitions.items()
                }
            }
            
            # Ensure parent directory exists
            self.state_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Write to file
            with open(self.state_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            self.logger.info(f"Persisted {len(self.states)} states to {self.state_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to persist state: {e}")
            return False
    
    def load(self) -> bool:
        """
        Load states from disk.
        
        Returns:
            True if loaded successfully
        """
        if not self.state_file or not self.state_file.exists():
            self.logger.warning("State file not found, starting fresh")
            return False
        
        try:
            with open(self.state_file, 'r') as f:
                data = json.load(f)
            
            self.states = data.get("states", {})
            
            # Reconstruct transitions
            self.transitions = {}
            for state_id, transition_dicts in data.get("transitions", {}).items():
                self.transitions[state_id] = [
                    StateTransition.from_dict(t) for t in transition_dicts
                ]
            
            self.logger.info(f"Loaded {len(self.states)} states from {self.state_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load state: {e}")
            return False
    
    def clear(self) -> bool:
        """
        Clear all states.
        
        Returns:
            True if cleared successfully
        """
        self.states = {}
        self.transitions = {}
        self.logger.info("Cleared all states")
        return True
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get state metrics.
        
        Returns:
            Dictionary of metrics
        """
        metrics = {
            "total_states": len(self.states),
            "by_type": {},
            "total_transitions": sum(len(t) for t in self.transitions.values())
        }
        
        # Count states by type
        for state in self.states.values():
            state_type = state["type"]
            if state_type not in metrics["by_type"]:
                metrics["by_type"][state_type] = 0
            metrics["by_type"][state_type] += 1
        
        return metrics
