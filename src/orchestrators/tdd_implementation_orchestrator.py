"""
TDD Implementation Orchestrator

Orchestrates Test-Driven Development workflow with RED→GREEN→REFACTOR phases
and clean code enforcement. Enforces quality during REFACTOR phase with
duplicate detection, SOLID validation, and holistic code review.

Key Features:
- Phase-based TDD workflow (RED → GREEN → REFACTOR)
- Test-first validation (tests must fail before implementation)
- Minimal implementation guidance (tests pass with simplest code)
- Holistic REFACTOR phase (duplicates, redundancies, SOLID principles)
- Scope-aware quality checks (implementation files only)
- Out-of-scope blocker detection (log, don't fix)
- Git checkpoints at phase boundaries (rollback capability)
- Pattern learning (stores refactoring preferences in Tier 2)
- Real-time metrics (dashboard integration)

Usage:
    from src.orchestrators.tdd_implementation_orchestrator import TDDImplementationOrchestrator
    
    orchestrator = TDDImplementationOrchestrator(project_root="path/to/project")
    
    # Start TDD session
    session = orchestrator.start_session(
        feature_name="User Authentication",
        task_id="FEATURE-001"
    )
    
    # Execute RED phase
    red_result = orchestrator.execute_red_phase(session_id=session["session_id"])
    
    # Execute GREEN phase
    green_result = orchestrator.execute_green_phase(session_id=session["session_id"])
    
    # Execute REFACTOR phase (the innovation)
    refactor_result = orchestrator.execute_refactor_phase(session_id=session["session_id"])

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
Version: 1.0.0 (CORTEX 3.8.2)
"""

import logging
import subprocess
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import uuid
import json

from src.orchestrators.git_checkpoint_orchestrator import GitCheckpointOrchestrator
from src.utils.progress_decorator import with_progress, yield_progress

logger = logging.getLogger(__name__)


class TDDPhase(Enum):
    """TDD workflow phases."""
    NOT_STARTED = "not_started"
    RED = "red"
    GREEN = "green"
    REFACTOR = "refactor"
    COMPLETE = "complete"


class TDDSessionState:
    """State tracker for TDD session."""
    
    def __init__(
        self,
        session_id: str,
        feature_name: str,
        task_id: Optional[str] = None,
        work_item_id: Optional[str] = None
    ):
        self.session_id = session_id
        self.feature_name = feature_name
        self.task_id = task_id
        self.work_item_id = work_item_id
        self.current_phase = TDDPhase.NOT_STARTED
        self.phase_history: List[Dict[str, Any]] = []
        self.checkpoints: List[str] = []
        self.metrics: Dict[str, Any] = {
            "phase_timings": {},
            "duplicates_removed": 0,
            "violations_fixed": 0,
            "coverage_delta": 0.0,
            "refactorings_applied": 0,
            "refactorings_rejected": 0
        }
        self.implementation_scope: List[Path] = []
        self.test_scope: List[Path] = []
        self.blockers: List[Dict[str, Any]] = []
        self.started_at = datetime.now(timezone.utc)
        self.completed_at: Optional[datetime] = None
    
    def transition_to(self, new_phase: TDDPhase, checkpoint_id: Optional[str] = None):
        """
        Transition to new phase with history tracking.
        
        Args:
            new_phase: Phase to transition to
            checkpoint_id: Optional checkpoint ID for rollback
        """
        self.phase_history.append({
            "from_phase": self.current_phase.value,
            "to_phase": new_phase.value,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "checkpoint_id": checkpoint_id
        })
        self.current_phase = new_phase
        
        if checkpoint_id:
            self.checkpoints.append(checkpoint_id)
    
    def can_transition_to(self, target_phase: TDDPhase) -> Tuple[bool, str]:
        """
        Validate if transition to target phase is allowed.
        
        Args:
            target_phase: Phase to validate transition to
            
        Returns:
            Tuple of (allowed, reason)
        """
        current = self.current_phase
        
        # NOT_STARTED -> RED (always allowed)
        if current == TDDPhase.NOT_STARTED and target_phase == TDDPhase.RED:
            return True, "Starting TDD workflow"
        
        # RED -> GREEN (only after RED validated)
        if current == TDDPhase.RED and target_phase == TDDPhase.GREEN:
            return True, "Tests failed, ready for implementation"
        
        # GREEN -> REFACTOR (only after GREEN validated)
        if current == TDDPhase.GREEN and target_phase == TDDPhase.REFACTOR:
            return True, "Tests pass, ready for refactoring"
        
        # REFACTOR -> COMPLETE (only after REFACTOR validated)
        if current == TDDPhase.REFACTOR and target_phase == TDDPhase.COMPLETE:
            return True, "Refactoring complete, TDD cycle finished"
        
        # Invalid transitions
        return False, f"Cannot transition from {current.value} to {target_phase.value}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary for persistence."""
        return {
            "session_id": self.session_id,
            "feature_name": self.feature_name,
            "task_id": self.task_id,
            "work_item_id": self.work_item_id,
            "current_phase": self.current_phase.value,
            "phase_history": self.phase_history,
            "checkpoints": self.checkpoints,
            "metrics": self.metrics,
            "implementation_scope": [str(p) for p in self.implementation_scope],
            "test_scope": [str(p) for p in self.test_scope],
            "blockers": self.blockers,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }


class TDDImplementationOrchestrator:
    """
    Orchestrates TDD workflow with clean code enforcement.
    
    Manages RED→GREEN→REFACTOR cycle with:
    - Test-first validation (RED phase)
    - Minimal implementation (GREEN phase)
    - Holistic refactoring (REFACTOR phase - THE INNOVATION)
    - Git checkpoints at boundaries
    - Pattern learning (Tier 2 integration)
    - Real-time metrics (dashboard integration)
    """
    
    def __init__(
        self,
        project_root: Path,
        cortex_root: Optional[Path] = None
    ):
        """
        Initialize TDD Implementation Orchestrator.
        
        Args:
            project_root: Root directory of project being developed
            cortex_root: Root directory of CORTEX (defaults to auto-detect)
        """
        self.project_root = Path(project_root)
        self.cortex_root = Path(cortex_root) if cortex_root else self._detect_cortex_root()
        
        # Session management
        self.active_sessions: Dict[str, TDDSessionState] = {}
        self.sessions_dir = self.cortex_root / "cortex-brain" / "documents" / "reports" / "tdd-sessions"
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        
        # Integration points
        self.git_checkpoint = GitCheckpointOrchestrator(self.project_root)
        
        # Lazy-load heavy dependencies
        self._code_analyzers = None
        self._brain_protector = None
        self._pattern_library = None
        self._metrics_collector = None
        
        logger.info(f"✅ TDDImplementationOrchestrator initialized for {self.project_root}")
    
    def _detect_cortex_root(self) -> Path:
        """Auto-detect CORTEX root from current file location."""
        current = Path(__file__).resolve()
        # Navigate up to find cortex-brain directory
        for parent in current.parents:
            if (parent / "cortex-brain").exists():
                return parent
        # Fallback to project root
        return self.project_root
    
    def start_session(
        self,
        feature_name: str,
        task_id: Optional[str] = None,
        work_item_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Start a new TDD session.
        
        Args:
            feature_name: Name of feature being implemented
            task_id: Optional task identifier
            work_item_id: Optional ADO work item ID
            
        Returns:
            Dict with session_id and initial state
        """
        session_id = f"tdd-{uuid.uuid4().hex[:8]}"
        
        state = TDDSessionState(
            session_id=session_id,
            feature_name=feature_name,
            task_id=task_id,
            work_item_id=work_item_id
        )
        
        self.active_sessions[session_id] = state
        self._save_session_state(state)
        
        logger.info(f"🚀 Started TDD session {session_id} for '{feature_name}'")
        
        return {
            "success": True,
            "session_id": session_id,
            "feature_name": feature_name,
            "current_phase": state.current_phase.value,
            "message": f"TDD session started for '{feature_name}'"
        }
    
    def get_session(self, session_id: str) -> Optional[TDDSessionState]:
        """
        Get active session state.
        
        Args:
            session_id: Session identifier
            
        Returns:
            TDDSessionState or None if not found
        """
        return self.active_sessions.get(session_id)
    
    def _save_session_state(self, state: TDDSessionState):
        """
        Persist session state to disk.
        
        Args:
            state: Session state to save
        """
        session_file = self.sessions_dir / f"{state.session_id}.json"
        
        try:
            with open(session_file, 'w') as f:
                json.dump(state.to_dict(), f, indent=2)
            logger.debug(f"💾 Saved session state: {state.session_id}")
        except Exception as e:
            logger.error(f"❌ Failed to save session state: {e}")
    
    def _validate_phase_transition(
        self,
        session_id: str,
        target_phase: TDDPhase
    ) -> Tuple[bool, str, Optional[TDDSessionState]]:
        """
        Validate phase transition is allowed.
        
        Args:
            session_id: Session identifier
            target_phase: Target phase to transition to
            
        Returns:
            Tuple of (allowed, reason, state)
        """
        state = self.get_session(session_id)
        
        if not state:
            return False, f"Session {session_id} not found", None
        
        allowed, reason = state.can_transition_to(target_phase)
        return allowed, reason, state
    
    def execute_red_phase(
        self,
        session_id: str,
        test_command: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute RED phase: Verify tests fail before implementation.
        
        Args:
            session_id: TDD session identifier
            test_command: Optional test command (auto-detected if not provided)
            
        Returns:
            Dict with success, message, test results
        """
        # Validate transition
        allowed, reason, state = self._validate_phase_transition(session_id, TDDPhase.RED)
        
        if not allowed:
            return {
                "success": False,
                "phase": "RED",
                "message": f"Cannot start RED phase: {reason}"
            }
        
        logger.info(f"🔴 Executing RED phase for session {session_id}")
        phase_start = datetime.now(timezone.utc)
        
        try:
            # Run tests
            test_result = self._run_tests(test_command)
            
            # Verify at least one test failed
            if test_result["success"] and test_result["tests_passed"] == test_result["tests_total"]:
                # All tests passed - invalid RED phase
                logger.warning(f"⚠️ RED phase violation: All tests passed")
                return {
                    "success": False,
                    "phase": "RED",
                    "message": "RED phase failed: Tests must fail before implementation (test-first discipline)",
                    "test_results": test_result,
                    "challenge": "Brain Protector: Write a failing test first. TDD requires test-first approach."
                }
            
            # Tests failed (expected in RED phase)
            failing_tests = test_result.get("failing_tests", [])
            logger.info(f"✅ RED phase validated: {len(failing_tests)} test(s) failing")
            
            # Create git checkpoint
            checkpoint_result = self.git_checkpoint.create_checkpoint(
                session_id=session_id,
                checkpoint_type="phase-RED",
                message=f"RED phase: {len(failing_tests)} test(s) failing",
                metadata={
                    "task_id": state.task_id,
                    "feature_name": state.feature_name,
                    "work_item_id": state.work_item_id
                }
            )
            
            # Update state
            state.transition_to(TDDPhase.RED, checkpoint_id=checkpoint_result.get("checkpoint_id"))
            phase_duration = (datetime.now(timezone.utc) - phase_start).total_seconds()
            state.metrics["phase_timings"]["RED"] = phase_duration
            self._save_session_state(state)
            
            return {
                "success": True,
                "phase": "RED",
                "message": f"RED phase complete: {len(failing_tests)} test(s) failing as expected",
                "test_results": test_result,
                "failing_tests": failing_tests,
                "checkpoint_id": checkpoint_result.get("checkpoint_id"),
                "phase_duration_seconds": phase_duration
            }
            
        except Exception as e:
            logger.error(f"❌ RED phase failed: {e}")
            return {
                "success": False,
                "phase": "RED",
                "message": f"RED phase error: {str(e)}",
                "error": str(e)
            }
    
    def execute_green_phase(
        self,
        session_id: str,
        test_command: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute GREEN phase: Verify tests pass after minimal implementation.
        
        Args:
            session_id: TDD session identifier
            test_command: Optional test command (auto-detected if not provided)
            
        Returns:
            Dict with success, message, test results, coverage delta
        """
        # Validate transition
        allowed, reason, state = self._validate_phase_transition(session_id, TDDPhase.GREEN)
        
        if not allowed:
            return {
                "success": False,
                "phase": "GREEN",
                "message": f"Cannot start GREEN phase: {reason}"
            }
        
        logger.info(f"🟢 Executing GREEN phase for session {session_id}")
        phase_start = datetime.now(timezone.utc)
        
        try:
            # Run tests with coverage
            test_result = self._run_tests_with_coverage(test_command)
            
            # Verify all tests pass
            if not test_result["success"] or test_result["tests_failed"] > 0:
                # Tests still failing
                failing_tests = test_result.get("failing_tests", [])
                logger.warning(f"⚠️ GREEN phase not ready: {len(failing_tests)} test(s) still failing")
                return {
                    "success": False,
                    "phase": "GREEN",
                    "message": f"GREEN phase incomplete: {len(failing_tests)} test(s) still failing",
                    "test_results": test_result,
                    "failing_tests": failing_tests,
                    "hint": "Implement minimal code to make tests pass"
                }
            
            # All tests pass
            logger.info(f"✅ GREEN phase validated: All {test_result['tests_total']} test(s) passing")
            
            # Calculate coverage delta
            coverage_delta = test_result.get("coverage_percent", 0.0)
            
            # Analyze scope (warn if too many files changed)
            changed_files = self._get_changed_files()
            if len(changed_files) > 5:
                logger.warning(f"⚠️ Scope warning: {len(changed_files)} files changed (minimize implementation)")
            
            # Create git checkpoint
            checkpoint_result = self.git_checkpoint.create_checkpoint(
                session_id=session_id,
                checkpoint_type="phase-GREEN",
                message=f"GREEN phase: All tests passing, coverage {coverage_delta:.1f}%",
                metadata={
                    "task_id": state.task_id,
                    "feature_name": state.feature_name,
                    "work_item_id": state.work_item_id
                }
            )
            
            # Update state
            state.transition_to(TDDPhase.GREEN, checkpoint_id=checkpoint_result.get("checkpoint_id"))
            phase_duration = (datetime.now(timezone.utc) - phase_start).total_seconds()
            state.metrics["phase_timings"]["GREEN"] = phase_duration
            state.metrics["coverage_delta"] = coverage_delta
            state.implementation_scope = changed_files
            self._save_session_state(state)
            
            return {
                "success": True,
                "phase": "GREEN",
                "message": f"GREEN phase complete: All {test_result['tests_total']} test(s) passing",
                "test_results": test_result,
                "coverage_delta": coverage_delta,
                "changed_files": [str(f) for f in changed_files],
                "scope_warning": len(changed_files) > 5,
                "checkpoint_id": checkpoint_result.get("checkpoint_id"),
                "phase_duration_seconds": phase_duration
            }
            
        except Exception as e:
            logger.error(f"❌ GREEN phase failed: {e}")
            return {
                "success": False,
                "phase": "GREEN",
                "message": f"GREEN phase error: {str(e)}",
                "error": str(e)
            }
    
    def execute_refactor_phase(
        self,
        session_id: str,
        auto_apply: bool = False
    ) -> Dict[str, Any]:
        """
        Execute REFACTOR phase: Holistic code quality analysis and cleanup.
        
        THIS IS THE INNOVATION - Enforces clean code/architecture.
        
        Args:
            session_id: TDD session identifier
            auto_apply: If True, apply safe refactorings automatically
            
        Returns:
            Dict with success, message, refactorings, metrics
        """
        # Validate transition
        allowed, reason, state = self._validate_phase_transition(session_id, TDDPhase.REFACTOR)
        
        if not allowed:
            return {
                "success": False,
                "phase": "REFACTOR",
                "message": f"Cannot start REFACTOR phase: {reason}"
            }
        
        logger.info(f"🔵 Executing REFACTOR phase for session {session_id}")
        
        # TODO: Implement in Phase 3
        # - Scope analysis (implementation files only)
        # - Duplicate detection
        # - Redundancy check
        # - SOLID validation
        # - Out-of-scope blocker detection
        # - Apply refactorings (incremental, with re-test)
        # - Store patterns in Tier 2
        # - Create final checkpoint
        
        return {
            "success": False,
            "phase": "REFACTOR",
            "message": "REFACTOR phase implementation pending (Phase 3)",
            "note": "Phase 1 focuses on infrastructure only"
        }
    
    def complete_session(self, session_id: str) -> Dict[str, Any]:
        """
        Complete TDD session and generate summary.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Dict with success, summary, metrics
        """
        state = self.get_session(session_id)
        
        if not state:
            return {
                "success": False,
                "message": f"Session {session_id} not found"
            }
        
        # Validate in REFACTOR or later phase
        if state.current_phase not in [TDDPhase.REFACTOR, TDDPhase.COMPLETE]:
            return {
                "success": False,
                "message": f"Cannot complete session in {state.current_phase.value} phase"
            }
        
        # Mark complete
        state.transition_to(TDDPhase.COMPLETE)
        state.completed_at = datetime.now(timezone.utc)
        self._save_session_state(state)
        
        # Remove from active sessions
        del self.active_sessions[session_id]
        
        logger.info(f"✅ Completed TDD session {session_id}")
        
        return {
            "success": True,
            "session_id": session_id,
            "feature_name": state.feature_name,
            "metrics": state.metrics,
            "phase_history": state.phase_history,
            "duration_seconds": (state.completed_at - state.started_at).total_seconds(),
            "message": f"TDD session complete for '{state.feature_name}'"
        }
    
    def rollback_to_checkpoint(
        self,
        session_id: str,
        checkpoint_id: str
    ) -> Dict[str, Any]:
        """
        Rollback to previous checkpoint.
        
        Args:
            session_id: Session identifier
            checkpoint_id: Checkpoint to rollback to
            
        Returns:
            Dict with success, message
        """
        state = self.get_session(session_id)
        
        if not state:
            return {
                "success": False,
                "message": f"Session {session_id} not found"
            }
        
        if checkpoint_id not in state.checkpoints:
            return {
                "success": False,
                "message": f"Checkpoint {checkpoint_id} not found in session"
            }
        
        try:
            # Rollback via git reset
            result = subprocess.run(
                ["git", "log", "--all", "--grep", f"Checkpoint: {checkpoint_id}", "--format=%H", "-1"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=True
            )
            
            commit_sha = result.stdout.strip()
            if not commit_sha:
                return {
                    "success": False,
                    "message": f"Checkpoint {checkpoint_id} not found in git history"
                }
            
            # Reset to checkpoint
            subprocess.run(
                ["git", "reset", "--hard", commit_sha],
                cwd=self.project_root,
                check=True
            )
            
            logger.info(f"⏮️ Rolled back to checkpoint {checkpoint_id} (commit {commit_sha[:8]})")
            
            return {
                "success": True,
                "message": f"Rolled back to checkpoint {checkpoint_id}",
                "checkpoint_id": checkpoint_id,
                "commit_sha": commit_sha
            }
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Rollback failed: {e}")
            return {
                "success": False,
                "message": f"Rollback failed: {str(e)}",
                "error": str(e)
            }
    
    def _run_tests(self, test_command: Optional[str] = None) -> Dict[str, Any]:
        """
        Run tests without coverage.
        
        Args:
            test_command: Optional test command (auto-detected if not provided)
            
        Returns:
            Dict with test results
        """
        if not test_command:
            test_command = self._detect_test_command()
        
        try:
            result = subprocess.run(
                test_command,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                shell=True
            )
            
            # Parse pytest output
            output = result.stdout + result.stderr
            tests_passed, tests_failed, tests_total = self._parse_test_output(output)
            
            failing_tests = self._extract_failing_tests(output) if tests_failed > 0 else []
            
            return {
                "success": result.returncode == 0,
                "tests_passed": tests_passed,
                "tests_failed": tests_failed,
                "tests_total": tests_total,
                "failing_tests": failing_tests,
                "output": output,
                "command": test_command
            }
            
        except Exception as e:
            logger.error(f"❌ Test execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "command": test_command
            }
    
    def _run_tests_with_coverage(self, test_command: Optional[str] = None) -> Dict[str, Any]:
        """
        Run tests with coverage tracking.
        
        Args:
            test_command: Optional test command (auto-detected if not provided)
            
        Returns:
            Dict with test results and coverage
        """
        if not test_command:
            test_command = self._detect_test_command(with_coverage=True)
        
        try:
            result = subprocess.run(
                test_command,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                shell=True
            )
            
            # Parse pytest output
            output = result.stdout + result.stderr
            tests_passed, tests_failed, tests_total = self._parse_test_output(output)
            failing_tests = self._extract_failing_tests(output) if tests_failed > 0 else []
            coverage_percent = self._extract_coverage(output)
            
            return {
                "success": result.returncode == 0,
                "tests_passed": tests_passed,
                "tests_failed": tests_failed,
                "tests_total": tests_total,
                "failing_tests": failing_tests,
                "coverage_percent": coverage_percent,
                "output": output,
                "command": test_command
            }
            
        except Exception as e:
            logger.error(f"❌ Test execution with coverage failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "command": test_command
            }
    
    def _detect_test_command(self, with_coverage: bool = False) -> str:
        """
        Auto-detect test command based on project structure.
        
        Args:
            with_coverage: Whether to include coverage flags
            
        Returns:
            Test command string
        """
        # Check for pytest
        if (self.project_root / "pytest.ini").exists() or \
           (self.project_root / "setup.py").exists() or \
           (self.project_root / "tests").exists():
            if with_coverage:
                return "pytest --cov --cov-report=term-missing"
            return "pytest"
        
        # Fallback to unittest
        if with_coverage:
            return "python -m coverage run -m unittest discover"
        return "python -m unittest discover"
    
    def _parse_test_output(self, output: str) -> Tuple[int, int, int]:
        """
        Parse test output to extract pass/fail counts.
        
        Args:
            output: Test command output
            
        Returns:
            Tuple of (passed, failed, total)
        """
        import re
        
        # Pytest format: "18 passed in 0.30s" or "5 failed, 13 passed"
        passed_match = re.search(r'(\d+)\s+passed', output)
        failed_match = re.search(r'(\d+)\s+failed', output)
        
        passed = int(passed_match.group(1)) if passed_match else 0
        failed = int(failed_match.group(1)) if failed_match else 0
        total = passed + failed
        
        return passed, failed, total
    
    def _extract_failing_tests(self, output: str) -> List[str]:
        """
        Extract failing test names from output.
        
        Args:
            output: Test command output
            
        Returns:
            List of failing test names
        """
        import re
        
        # Pytest format: "tests/test_file.py::TestClass::test_method FAILED"
        failing_tests = re.findall(r'([\w/]+\.py::[\w:]+)\s+FAILED', output)
        return failing_tests
    
    def _extract_coverage(self, output: str) -> float:
        """
        Extract coverage percentage from output.
        
        Args:
            output: Test command output
            
        Returns:
            Coverage percentage (0.0-100.0)
        """
        import re
        
        # Pytest-cov format: "TOTAL ... 81%" (with various spacing/numbers)
        coverage_match = re.search(r'TOTAL\s+.*?(\d+)%', output)
        if coverage_match:
            return float(coverage_match.group(1))
        
        return 0.0
    
    def _get_changed_files(self) -> List[Path]:
        """
        Get list of changed files since last checkpoint.
        
        Returns:
            List of changed file paths
        """
        try:
            result = subprocess.run(
                ["git", "diff", "--name-only", "HEAD"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=True
            )
            
            files = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    files.append(Path(line))
            
            return files
            
        except subprocess.CalledProcessError:
            return []
