"""
TDD Workflow State Machine - Phase 2 Milestone 2.1

Orchestrates RED→GREEN→REFACTOR cycle with state management,
transition validation, and cycle metrics.

Author: Asif Hussain
Created: 2025-11-23
Phase: TDD Mastery Phase 2
Updated: 2025-11-24 - Phase 4 TDD Mastery Integration (Debug + Feedback)
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime
import json
import sys
from pathlib import Path

# Phase 4 - TDD Mastery Integration: Add agent imports
src_path = Path(__file__).parent.parent
cortex_brain_path = src_path.parent / "cortex-brain"
if str(cortex_brain_path) not in sys.path:
    sys.path.insert(0, str(cortex_brain_path))

try:
    from agents.debug_agent import DebugAgent
    from agents.debug_session_manager import DebugSessionManager
    from agents.feedback_agent import FeedbackAgent
except ImportError:
    # Fallback if agents not available
    DebugAgent = None
    DebugSessionManager = None
    FeedbackAgent = None


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
    
    def __init__(
        self, 
        feature_name: str, 
        session_id: str,
        storage_path: str = "cortex-brain/tier1",
        enable_debug: bool = True,
        enable_feedback: bool = True,
        feedback_threshold: int = 3
    ):
        """
        Initialize TDD state machine.
        
        Args:
            feature_name: Name of feature being developed
            session_id: Unique session identifier
            storage_path: Path for debug and feedback data storage
            enable_debug: Enable auto-debug on test failures
            enable_feedback: Enable auto-feedback on persistent failures
            feedback_threshold: RED cycles before triggering feedback
        """
        self.session = TDDSession(
            feature_name=feature_name,
            session_id=session_id
        )
        self.phase_start_time: Optional[datetime] = None
        
        # Phase 4 - TDD Mastery Integration: Debug and feedback agents
        self.storage_path = storage_path
        self.enable_debug = enable_debug
        self.enable_feedback = enable_feedback
        self.feedback_threshold = feedback_threshold
        self.red_state_count = 0
        self.active_debug_session: Optional[str] = None
        self.debug_data_cache: Dict[str, Any] = {}
        
        # Initialize debug system
        self.debug_manager: Optional[Any] = None
        self.debug_agent: Optional[Any] = None
        if enable_debug and DebugSessionManager and DebugAgent:
            try:
                self.debug_manager = DebugSessionManager(storage_path=storage_path)
                self.debug_agent = DebugAgent(self.debug_manager)
            except Exception as e:
                print(f"⚠️  Debug system initialization failed: {e}")
                self.debug_manager = None
                self.debug_agent = None
        
        # Initialize feedback system
        self.feedback_agent: Optional[Any] = None
        if enable_feedback and FeedbackAgent:
            try:
                brain_path = Path(storage_path).parent
                self.feedback_agent = FeedbackAgent(brain_path=str(brain_path))
            except Exception as e:
                print(f"⚠️  Feedback system initialization failed: {e}")
                self.feedback_agent = None
    
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
    
    # Phase 4 - TDD Mastery Integration: Debug and feedback helper methods
    
    def _extract_failing_modules(self, test_results: Dict[str, Any]) -> List[str]:
        """Extract module names from test failures."""
        failing_modules = []
        failures = test_results.get("failures", [])
        
        # Handle None or invalid failures
        if failures is None:
            return failing_modules
        
        for failure in failures:
            if isinstance(failure, dict):
                module = failure.get("module") or failure.get("file")
                if module and module not in failing_modules:
                    failing_modules.append(module)
            elif isinstance(failure, str):
                # Extract module from string representation
                if "/" in failure or "\\" in failure:
                    module = failure.split("/")[-1].split("\\")[-1]
                    if module not in failing_modules:
                        failing_modules.append(module)
        
        return failing_modules
    
    def _trigger_debug_session(self, test_results: Dict[str, Any]):
        """Auto-trigger debug session on test failures."""
        if not self.debug_agent or not self.enable_debug:
            return
        
        failing_modules = self._extract_failing_modules(test_results)
        if not failing_modules:
            return
        
        try:
            self.active_debug_session = self.debug_agent.start_debug_session(
                target=failing_modules[0],
                session_metadata={
                    "tdd_session_id": self.session.session_id,
                    "test_results": test_results,
                    "state": "RED",
                    "cycle_number": len(self.session.cycles) + 1
                }
            )
            print(f"🔍 Debug session started: {self.active_debug_session}")
            print(f"   Instrumenting: {failing_modules[0]}")
        except Exception as e:
            print(f"⚠️  Debug session failed to start: {e}")
    
    def _stop_debug_session_and_capture(self):
        """Stop debug session and capture data for refactoring."""
        if not self.active_debug_session or not self.debug_agent:
            return
        
        try:
            debug_data = self.debug_agent.stop_debug_session(
                session_id=self.active_debug_session
            )
            self.debug_data_cache = debug_data
            self.active_debug_session = None
            print(f"✅ Debug session stopped, data captured for refactoring")
        except Exception as e:
            print(f"⚠️  Debug session stop failed: {e}")
    
    def _trigger_feedback_collection(self, test_results: Dict[str, Any]):
        """Auto-collect feedback for persistent failures."""
        if not self.feedback_agent or not self.enable_feedback:
            return
        
        try:
            failure_summary = self._format_failure_summary(test_results)
            
            feedback_report = self.feedback_agent.create_feedback_report(
                user_input=f"Persistent TDD test failures after {self.red_state_count} RED cycles:\n{failure_summary}",
                feedback_type="bug",
                severity="high" if self.red_state_count >= 5 else "medium",
                context={
                    "tdd_session_id": self.session.session_id,
                    "feature_name": self.session.feature_name,
                    "test_results": test_results,
                    "red_state_count": self.red_state_count,
                    "debug_session_id": self.active_debug_session,
                    "cycle_number": len(self.session.cycles) + 1
                },
                auto_upload=True
            )
            
            print(f"📢 Feedback report created: {feedback_report.get('file_path', 'N/A')}")
            if feedback_report.get("gist_url"):
                print(f"   Gist URL: {feedback_report['gist_url']}")
        except Exception as e:
            print(f"⚠️  Feedback collection failed: {e}")
    
    def _format_failure_summary(self, test_results: Dict[str, Any]) -> str:
        """Format test failures into readable summary."""
        failures = test_results.get("failures", [])
        if not failures:
            return "No failure details available"
        
        summary = []
        for i, failure in enumerate(failures[:5], 1):  # Limit to first 5
            if isinstance(failure, dict):
                test_name = failure.get("test", "Unknown")
                error = failure.get("error", "No error message")
                summary.append(f"{i}. {test_name}: {error}")
            elif isinstance(failure, str):
                summary.append(f"{i}. {failure}")
        
        if len(failures) > 5:
            summary.append(f"... and {len(failures) - 5} more failures")
        
        return "\n".join(summary)
    
    def get_debug_data(self) -> Dict[str, Any]:
        """Get cached debug data for refactoring analysis."""
        return self.debug_data_cache.copy()
    
    def transition_to_red_with_debug(self, test_results: Dict[str, Any]) -> bool:
        """Transition to RED state with auto-debug trigger."""
        # Increment RED count first (tracks persistent failures even if already in RED)
        self.red_state_count += 1
        
        # Attempt state transition (may fail if already in RED)
        success = self.start_red_phase()
        
        # Auto-trigger debug on failures (regardless of state transition success)
        if test_results.get("failures"):
            self._trigger_debug_session(test_results)
        
        # Persistent failure feedback collection
        if self.red_state_count >= self.feedback_threshold:
            self._trigger_feedback_collection(test_results)
        
        return success or self.session.current_state == TDDState.RED  # True if in RED state
    
    def transition_to_green_with_debug_capture(
        self, 
        tests_passing: int, 
        code_lines_added: int
    ) -> bool:
        """Transition to GREEN state and capture debug data."""
        if not self.start_green_phase():
            return False
        
        # Reset RED state count on successful GREEN
        self.red_state_count = 0
        
        # Stop debug session and capture data
        self._stop_debug_session_and_capture()
        
        # Complete GREEN phase with metrics
        return self.complete_green_phase(tests_passing, code_lines_added)
