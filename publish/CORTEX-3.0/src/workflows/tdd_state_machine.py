"""
TDD Workflow State Machine - Phase 2 Milestone 2.1

Orchestrates RED→GREEN→REFACTOR cycle with state management,
transition validation, and cycle metrics.

Author: Asif Hussain
Created: 2025-11-23
Phase: TDD Mastery Phase 2
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime
import json


class TDDState(Enum):
    """TDD workflow states."""
    IDLE = "idle"
    RED = "red"  # Tests written, failing
    GREEN = "green"  # Tests passing with minimal code
    REFACTOR = "refactor"  # Improving code while maintaining tests
    DONE = "done"  # Feature complete
    ERROR = "error"  # Unexpected error occurred


@dataclass
class TDDCycleMetrics:
    """Metrics for a single TDD cycle."""
    cycle_number: int
    red_duration: float = 0.0  # seconds in RED phase
    green_duration: float = 0.0  # seconds in GREEN phase
    refactor_duration: float = 0.0  # seconds in REFACTOR phase
    total_duration: float = 0.0
    tests_written: int = 0
    tests_passing: int = 0
    code_lines_added: int = 0
    code_lines_refactored: int = 0
    refactoring_iterations: int = 0
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None


@dataclass
class TDDSession:
    """Complete TDD session with all cycles."""
    feature_name: str
    session_id: str
    cycles: List[TDDCycleMetrics] = field(default_factory=list)
    current_state: TDDState = TDDState.IDLE
    current_cycle: Optional[TDDCycleMetrics] = None
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize session to dictionary."""
        return {
            "feature_name": self.feature_name,
            "session_id": self.session_id,
            "cycles": [self._cycle_to_dict(c) for c in self.cycles],
            "current_state": self.current_state.value,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }
    
    def _cycle_to_dict(self, cycle: TDDCycleMetrics) -> Dict[str, Any]:
        """Convert cycle to dictionary."""
        return {
            "cycle_number": cycle.cycle_number,
            "red_duration": cycle.red_duration,
            "green_duration": cycle.green_duration,
            "refactor_duration": cycle.refactor_duration,
            "total_duration": cycle.total_duration,
            "tests_written": cycle.tests_written,
            "tests_passing": cycle.tests_passing,
            "code_lines_added": cycle.code_lines_added,
            "code_lines_refactored": cycle.code_lines_refactored,
            "refactoring_iterations": cycle.refactoring_iterations,
            "started_at": cycle.started_at.isoformat(),
            "completed_at": cycle.completed_at.isoformat() if cycle.completed_at else None,
        }


class TDDStateMachine:
    """
    TDD Workflow State Machine.
    
    Manages transitions between RED→GREEN→REFACTOR states,
    validates transitions, tracks metrics, and provides
    cycle analytics.
    """
    
    # Valid state transitions
    VALID_TRANSITIONS = {
        TDDState.IDLE: [TDDState.RED],
        TDDState.RED: [TDDState.GREEN, TDDState.ERROR],
        TDDState.GREEN: [TDDState.REFACTOR, TDDState.RED, TDDState.DONE],
        TDDState.REFACTOR: [TDDState.GREEN, TDDState.RED],
        TDDState.DONE: [TDDState.RED],  # Start new cycle
        TDDState.ERROR: [TDDState.RED],  # Recover from error
    }
    
    def __init__(self, feature_name: str, session_id: str):
        """
        Initialize TDD state machine.
        
        Args:
            feature_name: Name of feature being developed
            session_id: Unique session identifier
        """
        self.session = TDDSession(
            feature_name=feature_name,
            session_id=session_id
        )
        self.phase_start_time: Optional[datetime] = None
    
    def start_red_phase(self) -> bool:
        """
        Start RED phase (write failing tests).
        
        Returns:
            True if transition successful, False otherwise
        """
        if not self._can_transition(TDDState.RED):
            return False
        
        # Start new cycle
        cycle_number = len(self.session.cycles) + 1
        self.session.current_cycle = TDDCycleMetrics(cycle_number=cycle_number)
        
        self.session.current_state = TDDState.RED
        self.phase_start_time = datetime.now()
        
        return True
    
    def complete_red_phase(self, tests_written: int) -> bool:
        """
        Complete RED phase (tests written and verified failing).
        
        Args:
            tests_written: Number of tests written
            
        Returns:
            True if phase completed successfully
        """
        if self.session.current_state != TDDState.RED:
            return False
        
        # Record RED phase metrics
        if self.session.current_cycle and self.phase_start_time:
            duration = (datetime.now() - self.phase_start_time).total_seconds()
            self.session.current_cycle.red_duration = duration
            self.session.current_cycle.tests_written = tests_written
        
        return True
    
    def start_green_phase(self) -> bool:
        """
        Start GREEN phase (write minimal code to pass tests).
        
        Returns:
            True if transition successful
        """
        if not self._can_transition(TDDState.GREEN):
            return False
        
        self.session.current_state = TDDState.GREEN
        self.phase_start_time = datetime.now()
        
        return True
    
    def complete_green_phase(self, tests_passing: int, code_lines_added: int) -> bool:
        """
        Complete GREEN phase (all tests passing).
        
        Args:
            tests_passing: Number of tests now passing
            code_lines_added: Lines of code added to make tests pass
            
        Returns:
            True if phase completed successfully
        """
        if self.session.current_state != TDDState.GREEN:
            return False
        
        # Record GREEN phase metrics
        if self.session.current_cycle and self.phase_start_time:
            duration = (datetime.now() - self.phase_start_time).total_seconds()
            self.session.current_cycle.green_duration = duration
            self.session.current_cycle.tests_passing = tests_passing
            self.session.current_cycle.code_lines_added = code_lines_added
        
        return True
    
    def start_refactor_phase(self) -> bool:
        """
        Start REFACTOR phase (improve code while maintaining tests).
        
        Returns:
            True if transition successful
        """
        if not self._can_transition(TDDState.REFACTOR):
            return False
        
        self.session.current_state = TDDState.REFACTOR
        self.phase_start_time = datetime.now()
        
        return True
    
    def complete_refactor_phase(self, code_lines_refactored: int, iterations: int = 1) -> bool:
        """
        Complete REFACTOR phase (code improved, tests still passing).
        
        Args:
            code_lines_refactored: Lines of code refactored
            iterations: Number of refactoring iterations performed
            
        Returns:
            True if phase completed successfully
        """
        if self.session.current_state != TDDState.REFACTOR:
            return False
        
        # Record REFACTOR phase metrics
        if self.session.current_cycle and self.phase_start_time:
            duration = (datetime.now() - self.phase_start_time).total_seconds()
            self.session.current_cycle.refactor_duration = duration
            self.session.current_cycle.code_lines_refactored = code_lines_refactored
            self.session.current_cycle.refactoring_iterations = iterations
        
        return True
    
    def complete_cycle(self) -> bool:
        """
        Complete current TDD cycle.
        
        Finalizes cycle metrics and adds to session history.
        
        Returns:
            True if cycle completed successfully
        """
        if not self.session.current_cycle:
            return False
        
        # Finalize cycle
        self.session.current_cycle.completed_at = datetime.now()
        self.session.current_cycle.total_duration = (
            self.session.current_cycle.red_duration +
            self.session.current_cycle.green_duration +
            self.session.current_cycle.refactor_duration
        )
        
        # Add to cycle history
        self.session.cycles.append(self.session.current_cycle)
        self.session.current_cycle = None
        
        # Transition to GREEN (ready for next feature or DONE)
        self.session.current_state = TDDState.GREEN
        
        return True
    
    def mark_done(self) -> bool:
        """
        Mark feature as complete.
        
        Returns:
            True if successfully marked done
        """
        if not self._can_transition(TDDState.DONE):
            return False
        
        self.session.current_state = TDDState.DONE
        self.session.completed_at = datetime.now()
        
        return True
    
    def handle_error(self, error_message: str) -> bool:
        """
        Handle error during TDD workflow.
        
        Args:
            error_message: Description of error
            
        Returns:
            True if error handled successfully
        """
        self.session.current_state = TDDState.ERROR
        # TODO: Log error details
        return True
    
    def _can_transition(self, target_state: TDDState) -> bool:
        """
        Check if transition to target state is valid.
        
        Args:
            target_state: Desired state
            
        Returns:
            True if transition is valid
        """
        current = self.session.current_state
        valid_targets = self.VALID_TRANSITIONS.get(current, [])
        return target_state in valid_targets
    
    def get_current_state(self) -> TDDState:
        """Get current workflow state."""
        return self.session.current_state
    
    def get_cycle_metrics(self) -> List[TDDCycleMetrics]:
        """Get all completed cycle metrics."""
        return self.session.cycles
    
    def get_session_summary(self) -> Dict[str, Any]:
        """
        Get summary of TDD session.
        
        Returns:
            Dictionary with session statistics
        """
        total_cycles = len(self.session.cycles)
        
        if total_cycles == 0:
            return {
                "feature_name": self.session.feature_name,
                "total_cycles": 0,
                "current_state": self.session.current_state.value,
            }
        
        # Calculate aggregate metrics
        total_tests = sum(c.tests_written for c in self.session.cycles)
        total_passing = sum(c.tests_passing for c in self.session.cycles)
        total_duration = sum(c.total_duration for c in self.session.cycles)
        total_code_added = sum(c.code_lines_added for c in self.session.cycles)
        total_code_refactored = sum(c.code_lines_refactored for c in self.session.cycles)
        
        avg_cycle_duration = total_duration / total_cycles
        
        return {
            "feature_name": self.session.feature_name,
            "session_id": self.session.session_id,
            "current_state": self.session.current_state.value,
            "total_cycles": total_cycles,
            "total_tests_written": total_tests,
            "total_tests_passing": total_passing,
            "test_pass_rate": (total_passing / total_tests * 100) if total_tests > 0 else 0,
            "total_duration_seconds": total_duration,
            "average_cycle_duration": avg_cycle_duration,
            "total_code_lines_added": total_code_added,
            "total_code_lines_refactored": total_code_refactored,
            "started_at": self.session.started_at.isoformat(),
            "completed_at": self.session.completed_at.isoformat() if self.session.completed_at else None,
        }
    
    def save_session(self, filepath: str) -> bool:
        """
        Save session to JSON file.
        
        Args:
            filepath: Path to save file
            
        Returns:
            True if saved successfully
        """
        try:
            with open(filepath, 'w') as f:
                json.dump(self.session.to_dict(), f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving session: {e}")
            return False
    
    @classmethod
    def load_session(cls, filepath: str) -> Optional['TDDStateMachine']:
        """
        Load session from JSON file.
        
        Args:
            filepath: Path to session file
            
        Returns:
            TDDStateMachine instance or None if load failed
        """
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            # Reconstruct state machine
            machine = cls(
                feature_name=data["feature_name"],
                session_id=data["session_id"]
            )
            
            # Restore state
            machine.session.current_state = TDDState(data["current_state"])
            machine.session.started_at = datetime.fromisoformat(data["started_at"])
            
            if data["completed_at"]:
                machine.session.completed_at = datetime.fromisoformat(data["completed_at"])
            
            # Restore cycles
            for cycle_data in data["cycles"]:
                cycle = TDDCycleMetrics(
                    cycle_number=cycle_data["cycle_number"],
                    red_duration=cycle_data["red_duration"],
                    green_duration=cycle_data["green_duration"],
                    refactor_duration=cycle_data["refactor_duration"],
                    total_duration=cycle_data["total_duration"],
                    tests_written=cycle_data["tests_written"],
                    tests_passing=cycle_data["tests_passing"],
                    code_lines_added=cycle_data["code_lines_added"],
                    code_lines_refactored=cycle_data["code_lines_refactored"],
                    refactoring_iterations=cycle_data["refactoring_iterations"],
                    started_at=datetime.fromisoformat(cycle_data["started_at"]),
                )
                
                if cycle_data["completed_at"]:
                    cycle.completed_at = datetime.fromisoformat(cycle_data["completed_at"])
                
                machine.session.cycles.append(cycle)
            
            return machine
            
        except Exception as e:
            print(f"Error loading session: {e}")
            return None
