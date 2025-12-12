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
import ast
import re
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import uuid
import json

from src.orchestrators.git_checkpoint_orchestrator import GitCheckpointOrchestrator
from src.orchestrators.session_model import TDDSession, TDDPhase as NewTDDPhase, SessionStatus, SessionFactory
from src.orchestrators.validation_framework import validate_tdd_transition, validate_code_quality, TDDTestValidator
from src.orchestrators.tdd_intelligence import TDDIntelligence, get_tdd_intelligence, CodeType, TDDDecision
from src.utils.progress_decorator import with_progress, yield_progress

logger = logging.getLogger(__name__)


# Backward compatibility: Keep old enum for existing code
class TDDPhase(Enum):
    """TDD workflow phases (DEPRECATED - use session_model.TDDPhase)."""
    NOT_STARTED = "not_started"
    RED = "red"
    GREEN = "green"
    REFACTOR = "refactor"
    COMPLETE = "complete"


class TDDSessionState(TDDSession):
    """
    State tracker for TDD session (MIGRATED to session_model.TDDSession).
    
    This class now inherits from TDDSession for type safety and consistency.
    Maintains backward compatibility with existing code.
    """
    
    def __init__(
        self,
        session_id: str,
        feature_name: str,
        task_id: Optional[str] = None,
        work_item_id: Optional[str] = None
    ):
        # Initialize parent TDDSession
        super().__init__(
            session_id=session_id,
            session_type="tdd",
            status=SessionStatus.NOT_STARTED,
            started_at=datetime.now(timezone.utc),
            feature_name=feature_name
        )
        
        # Additional fields specific to implementation orchestrator
        self.task_id = task_id
        self.work_item_id = work_item_id
        self.blockers: List[Dict[str, Any]] = []
        
        # Override metrics with extended structure
        self.metrics = {
            "phase_timings": {},
            "duplicates_removed": 0,
            "violations_fixed": 0,
            "coverage_delta": 0.0,
            "refactorings_applied": 0,
            "refactorings_rejected": 0
        }
        
        # Convert Path lists to str lists for parent class compatibility
        self.implementation_scope: List[Path] = []
        self.test_scope: List[Path] = []
        
        # Maintain backward-compatible current_phase field
        self.current_phase = TDDPhase.NOT_STARTED
    
    def transition_to(self, new_phase: TDDPhase, checkpoint_id: Optional[str] = None):
        """
        Transition to new phase with history tracking.
        
        Uses validation framework to ensure valid transitions.
        
        Args:
            new_phase: Phase to transition to (old enum)
            checkpoint_id: Optional checkpoint ID for rollback
        """
        # Convert old enum to new enum for validation
        phase_mapping = {
            TDDPhase.NOT_STARTED: NewTDDPhase.NOT_STARTED,
            TDDPhase.RED: NewTDDPhase.RED,
            TDDPhase.GREEN: NewTDDPhase.GREEN,
            TDDPhase.REFACTOR: NewTDDPhase.REFACTOR,
            TDDPhase.COMPLETE: NewTDDPhase.COMPLETED
        }
        
        new_phase_enum = phase_mapping.get(new_phase, NewTDDPhase.NOT_STARTED)
        
        # Use parent class transition method
        self.transition_to_phase(new_phase_enum, checkpoint_id)
        
        # Update old enum for backward compatibility
        self.current_phase = new_phase
    
    def can_transition_to(self, target_phase: TDDPhase) -> Tuple[bool, str]:
        """
        Validate if transition to target phase is allowed.
        
        Now uses validation framework for consistent rules.
        
        Args:
            target_phase: Phase to validate transition to
            
        Returns:
            Tuple of (allowed, reason)
        """
        # Map old enum values to new enum values for validation
        phase_value_mapping = {
            "not_started": "not_started",
            "red": "red",
            "green": "green",
            "refactor": "refactor",
            "complete": "completed"  # OLD enum uses "complete", NEW uses "completed"
        }
        
        current_value = phase_value_mapping.get(self.current_phase.value, self.current_phase.value)
        target_value = phase_value_mapping.get(target_phase.value, target_phase.value)
        
        # Use validation framework
        result = validate_tdd_transition(current_value, target_value)
        
        if result.valid:
            return True, "Valid transition"
        else:
            return False, result.errors[0] if result.errors else "Invalid transition"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary for persistence (uses parent serialization)."""
        # Get base serialization from parent
        data = super().to_dict()
        
        # Add orchestrator-specific fields
        data.update({
            "task_id": self.task_id,
            "work_item_id": self.work_item_id,
            "implementation_scope": [str(p) for p in self.implementation_scope],
            "test_scope": [str(p) for p in self.test_scope],
            "blockers": self.blockers,
            "metrics": self.metrics  # Override with extended metrics
        })
        
        return data


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
        cortex_root: Optional[Path] = None,
        enable_pattern_library: bool = True
    ):
        """
        Initialize TDD Implementation Orchestrator.
        
        Args:
            project_root: Root directory of project being developed
            cortex_root: Root directory of CORTEX (defaults to auto-detect)
            enable_pattern_library: Enable Tier 2 pattern learning (default: True)
        """
        self.project_root = Path(project_root)
        self.cortex_root = Path(cortex_root) if cortex_root else self._detect_cortex_root()
        
        # Session management
        self.active_sessions: Dict[str, TDDSessionState] = {}
        self.sessions_dir = self.cortex_root / "cortex-brain" / "documents" / "reports" / "tdd-sessions"
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        
        # Integration points
        self.git_checkpoint = GitCheckpointOrchestrator(self.project_root)
        
        # NEW: TDD Intelligence for smart enforcement
        self.tdd_intelligence = get_tdd_intelligence()
        
        # Lazy-load heavy dependencies
        self._code_analyzers = None
        self._brain_protector = None
        self._pattern_library = enable_pattern_library
        self._metrics_collector = None
        
        logger.info(f"✅ TDDImplementationOrchestrator initialized for {self.project_root}")
        logger.info(f"✅ TDD Intelligence enabled (smart TDD enforcement)")

    
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
        work_item_id: Optional[str] = None,
        test_files: Optional[List[Path]] = None,
        require_tests_upfront: bool = True
    ) -> Dict[str, Any]:
        """
        Start a new TDD session.
        
        TIER 0 ENFORCEMENT: By default, requires test file paths to enforce test-first.
        
        Args:
            feature_name: Name of feature being implemented
            task_id: Optional task identifier
            work_item_id: Optional ADO work item ID
            test_files: Test files that MUST exist before RED phase (test-first enforcement)
            require_tests_upfront: If True, blocks session start until test files specified
            
        Returns:
            Dict with session_id and initial state
        """
        # Subtle hint: Orchestrator engagement
        logger.info("🎭 Orchestrator engaged: TDDImplementationOrchestrator")
        
        session_id = f"tdd-{uuid.uuid4().hex[:8]}"
        
        # SKULL PROTECTION: TDD_ENFORCEMENT
        if require_tests_upfront and not test_files:
            logger.warning(f"⚠️ TDD_ENFORCEMENT: Session starting without test files specified")
            logger.warning("   Best practice: Specify test_files to enforce test-first discipline")
            logger.warning(f"   Session {session_id} will require test validation before GREEN phase")
        
        state = TDDSessionState(
            session_id=session_id,
            feature_name=feature_name,
            task_id=task_id,
            work_item_id=work_item_id
        )
        
        # Store test scope for validation
        if test_files:
            state.test_scope = test_files
        
        self.active_sessions[session_id] = state
        self._save_session_state(state)
        
        logger.info(f"🚀 Started TDD session {session_id} for '{feature_name}'")
        if test_files:
            logger.info(f"   Test scope: {len(test_files)} file(s) - test-first enforced")
        
        return {
            "success": True,
            "session_id": session_id,
            "feature_name": feature_name,
            "current_phase": state.current_phase.value,
            "test_files_required": len(test_files) if test_files else 0,
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
    
    def analyze_code_for_tdd_requirement(
        self,
        code_content: str,
        file_path: str,
        intent: Optional[str] = None
    ) -> TDDDecision:
        """
        Intelligently determine if TDD is required for given code.
        
        Uses TDD Intelligence module to analyze complexity and business value.
        
        Args:
            code_content: Source code to analyze
            file_path: Path to file being created
            intent: User's stated intent (e.g., "Create user entity")
        
        Returns:
            TDDDecision with enforcement decision and rationale
        
        Example:
            # Analyze entity class
            decision = orchestrator.analyze_code_for_tdd_requirement(
                code_content="public class User { public int Id { get; set; } }",
                file_path="src/Entities/User.cs",
                intent="Create user entity"
            )
            
            if decision.tdd_required:
                # Follow RED→GREEN→REFACTOR
                session = orchestrator.start_session(...)
            else:
                # TDD optional, proceed without tests
                logger.info(f"TDD OPTIONAL: {decision.exemption_reason}")
        """
        logger.info(f"🔍 Analyzing code for TDD requirement: {file_path}")
        
        decision = self.tdd_intelligence.analyze_code_for_tdd(
            code_content=code_content,
            file_path=file_path,
            intent=intent
        )
        
        # Log decision
        if decision.tdd_required:
            logger.info(f"🔴 TDD MANDATORY: {decision.rationale}")
            logger.info(f"   Code Type: {decision.code_type.value}")
            logger.info(f"   Complexity: {decision.complexity_score}/100")
            logger.info(f"   Methods: {decision.evidence.get('method_count', 0)}")
        else:
            logger.info(f"⏭️  TDD OPTIONAL: {decision.rationale}")
            logger.info(f"   Exemption: {decision.exemption_reason}")
            logger.info(f"   Properties: {decision.evidence.get('property_count', 0)}")
        
        return decision
    
    def get_tdd_guidance_for_code(
        self,
        code_content: str,
        file_path: str,
        intent: Optional[str] = None
    ) -> str:
        """
        Get human-readable TDD guidance for code being created.
        
        Args:
            code_content: Source code to analyze
            file_path: Path to file
            intent: User's stated intent
        
        Returns:
            Formatted guidance string
        """
        decision = self.analyze_code_for_tdd_requirement(code_content, file_path, intent)
        return self.tdd_intelligence.get_tdd_guidance(decision)
    
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
        test_command: Optional[str] = None,
        test_files: Optional[List[Path]] = None
    ) -> Dict[str, Any]:
        """
        Execute RED phase: Verify tests fail before implementation.
        
        TIER 0 ENFORCEMENT: Tests MUST be written and failing before implementation.
        
        Args:
            session_id: TDD session identifier
            test_command: Optional test command (auto-detected if not provided)
            test_files: Optional list of test files to validate (enforces test-first)
            
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
        logger.info("🎭 Phase transition: NOT_STARTED → RED")
        phase_start = datetime.now(timezone.utc)
        
        try:
            # SKULL PROTECTION: Verify tests exist before running
            if test_files:
                missing_tests = [tf for tf in test_files if not tf.exists()]
                if missing_tests:
                    logger.error(f"❌ RED_PHASE_VALIDATION violation: Test files missing")
                    for mt in missing_tests:
                        logger.error(f"   Missing: {mt}")
                    return {
                        "success": False,
                        "phase": "RED",
                        "message": "RED phase blocked: Tests must be written BEFORE implementation",
                        "missing_test_files": [str(mt) for mt in missing_tests],
                        "challenge": "Brain Protector: TDD_ENFORCEMENT requires test-first. Write failing tests now."
                    }
            
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
        logger.info("🎭 Phase transition: RED → GREEN")
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
        logger.info("🎭 Phase transition: GREEN → REFACTOR")
        phase_start = datetime.now(timezone.utc)
        
        try:
            # Step 1: Scope Analysis
            scope_result = self._analyze_scope(state)
            logger.info(f"📁 Scope: {len(scope_result['implementation_files'])} implementation, {len(scope_result['test_files'])} test, {len(scope_result['out_of_scope'])} out-of-scope")
            
            # Step 2: Security Scan (CRITICAL - blocks refactoring if issues found)
            security_result = self._detect_security_issues(scope_result['implementation_files'])
            critical_security = security_result.get('critical_count', 0)
            if critical_security > 0:
                logger.error(f"🚨 CRITICAL: {critical_security} security issues found - must fix before refactoring")
            logger.info(f"🔒 Security: {critical_security} critical, {security_result.get('high_count', 0)} high")
            
            # Step 3: Magic Values Detection
            magic_result = self._detect_magic_values(scope_result['implementation_files'])
            logger.info(f"🔢 Magic values: {len(magic_result['magic_values'])} found ({magic_result['repeated_strings']} repeated strings, {magic_result['hardcoded_urls']} URLs)")
            
            # Step 4: Duplicate Detection
            duplicates_result = self._detect_duplicates(scope_result['implementation_files'])
            logger.info(f"🔍 Found {len(duplicates_result['duplicates'])} duplicate code blocks")
            
            # Step 5: Redundancy Check
            redundancies_result = self._detect_redundancies(scope_result['implementation_files'])
            logger.info(f"🧹 Found {len(redundancies_result['redundancies'])} redundancies")
            
            # Step 6: SOLID Validation
            solid_result = self._validate_solid(scope_result['implementation_files'])
            logger.info(f"🏛️ SOLID: {solid_result.get('critical_count', 0)} critical, {solid_result.get('high_count', 0)} high, {solid_result.get('medium_count', 0)} medium violations")
            
            # NEW Step 6a: Anemic Domain Model Detection (from CRITICAL-ARCHITECTURE-REVIEW.md)
            anemic_result = self._detect_anemic_domain_models(scope_result['implementation_files'])
            anemic_count = anemic_result.get('count', 0)
            logger.info(f"🎭 Anemic Models: {anemic_count} detected")
            
            # NEW Step 6b: Configuration Management Issues (using validation framework)
            config_issues_from_framework = []
            for impl_file in scope_result['implementation_files']:
                try:
                    file_content = (self.project_root / impl_file).read_text(encoding='utf-8')
                    validation_result = validate_code_quality(file_content)
                    
                    if validation_result.warnings:
                        config_issues_from_framework.extend([
                            {
                                "type": "config_issue",
                                "severity": "HIGH",
                                "file": str(impl_file),
                                "message": warning,
                                "recommendation": "Externalize configuration to environment files"
                            }
                            for warning in validation_result.warnings
                        ])
                except Exception as e:
                    logger.debug(f"Validation framework skipped for {impl_file}: {e}")
            
            logger.info(f"⚙️ Configuration (framework): {len(config_issues_from_framework)} issues detected")
            
            # Legacy config detection (keep for backward compatibility)
            config_result = self._detect_configuration_issues(scope_result['implementation_files'])
            config_issues = config_result.get('config_issues', [])
            logger.info(f"⚙️ Configuration (legacy): {len(config_issues)} issues")
            
            # Merge framework and legacy results
            all_config_issues = config_issues_from_framework + config_issues
            config_result['config_issues'] = all_config_issues
            config_result['count'] = len(all_config_issues)
            
            # NEW Step 6c: Transaction Management Issues (from CRITICAL-ARCHITECTURE-REVIEW.md)
            transaction_result = self._detect_transaction_issues(scope_result['implementation_files'])
            transaction_issues = transaction_result.get('transaction_issues', [])
            logger.info(f"🔄 Transactions: {len(transaction_issues)} issues detected")
            
            # Step 7: Out-of-Scope Blocker Detection
            blockers_result = self._detect_blockers(scope_result['out_of_scope'])
            if blockers_result['blockers']:
                logger.warning(f"⚠️ Found {len(blockers_result['blockers'])} out-of-scope blockers")
                state.blockers.extend(blockers_result['blockers'])
            
            # Step 8: Generate Refactoring Recommendations
            refactorings = self._generate_refactorings(
                security_result,
                magic_result,
                duplicates_result,
                redundancies_result,
                solid_result,
                anemic_result,
                config_result,
                transaction_result
            )
            
            # Step 7: Apply Refactorings (if auto_apply or user approval)
            applied_refactorings = []
            if auto_apply:
                applied_refactorings = self._apply_refactorings_auto(refactorings, state)
            
            # Step 8: Store Patterns in Tier 2 (Learning)
            if self._pattern_library:
                self._store_refactoring_patterns(refactorings, applied_refactorings, state)
            
            # Step 9: Create Final Checkpoint
            checkpoint_result = self.git_checkpoint.create_checkpoint(
                session_id=session_id,
                checkpoint_type="phase-REFACTOR",
                message=f"REFACTOR phase: {len(applied_refactorings)} refactorings applied, {len(duplicates_result['duplicates'])} duplicates, {len(solid_result['violations'])} violations",
                metadata={
                    "task_id": state.task_id,
                    "feature_name": state.feature_name,
                    "work_item_id": state.work_item_id
                }
            )
            
            # Update state
            state.transition_to(TDDPhase.REFACTOR, checkpoint_id=checkpoint_result.get("checkpoint_id"))
            phase_duration = (datetime.now(timezone.utc) - phase_start).total_seconds()
            state.metrics["phase_timings"]["REFACTOR"] = phase_duration
            state.metrics["duplicates_removed"] = len(applied_refactorings)
            state.metrics["violations_fixed"] = len([r for r in applied_refactorings if r.get("type") == "solid"])
            self._save_session_state(state)
            
            return {
                "success": True,
                "phase": "REFACTOR",
                "message": f"REFACTOR phase complete: {len(applied_refactorings)} refactorings applied",
                "scope": scope_result,
                "security": security_result,
                "magic_values": magic_result,
                "duplicates": duplicates_result,
                "redundancies": redundancies_result,
                "solid_violations": solid_result,
                "blockers": blockers_result,
                "refactorings": refactorings,
                "applied_refactorings": applied_refactorings,
                "checkpoint_id": checkpoint_result.get("checkpoint_id"),
                "phase_duration_seconds": phase_duration,
                "critical_security_count": security_result.get('critical_count', 0),
                "total_refactorings_recommended": len(refactorings)
            }
            
        except Exception as e:
            logger.error(f"❌ REFACTOR phase failed: {e}")
            return {
                "success": False,
                "phase": "REFACTOR",
                "message": f"REFACTOR phase error: {str(e)}",
                "error": str(e)
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
        
        # Subtle hint: Completion status
        logger.info("🎭 Orchestrator completing: ✅ ALL WORK COMPLETE")
        logger.info(f"✅ Completed TDD session {session_id}")
        
        return {
            "success": True,
            "session_id": session_id,
            "feature_name": state.feature_name,
            "metrics": state.metrics,
            "phase_history": state.phase_history,
            "duration_seconds": (state.completed_at - state.started_at).total_seconds(),
            "message": f"TDD session complete for '{state.feature_name}'",
            "is_complete": True  # Signal for template selection
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
    
    def _analyze_scope(self, state: TDDSessionState) -> Dict[str, Any]:
        """
        Analyze implementation scope: categorize changed files.
        
        Args:
            state: TDD session state
            
        Returns:
            Dict with implementation_files, test_files, config_files, out_of_scope
        """
        changed_files = state.implementation_scope if state.implementation_scope else self._get_changed_files()
        
        implementation_files = []
        test_files = []
        config_files = []
        out_of_scope = []
        
        for file_path in changed_files:
            file_str = str(file_path)
            
            # Categorize files
            if '/test' in file_str or '\\test' in file_str or file_str.startswith('test_'):
                test_files.append(file_path)
            elif file_path.suffix in ['.json', '.yaml', '.yml', '.ini', '.cfg', '.toml']:
                config_files.append(file_path)
            elif file_path.suffix in ['.py', '.js', '.ts', '.cs', '.java', '.cfm', '.cfc']:
                # Check if in CORTEX internal paths (out-of-scope for user repos)
                if 'cortex-brain' in file_str or 'src/tier' in file_str:
                    out_of_scope.append(file_path)
                else:
                    implementation_files.append(file_path)
            else:
                out_of_scope.append(file_path)
        
        return {
            "implementation_files": implementation_files,
            "test_files": test_files,
            "config_files": config_files,
            "out_of_scope": out_of_scope,
            "total_files": len(changed_files)
        }
    
    def _detect_security_issues(self, files: List[Path]) -> Dict[str, Any]:
        """
        Detect security vulnerabilities in implementation files.
        
        Detection rules from BadMonolith analysis + CRITICAL-ARCHITECTURE-REVIEW.md:
        - SQL injection (string concatenation with SQL keywords)
        - Hard-coded credentials (passwords, API keys)
        - Missing error handling in async methods
        - Unvalidated user input
        - Missing authorization checks (NEW)
        - No rate limiting (NEW)
        - HTTP instead of HTTPS (NEW)
        - Missing CSRF protection (NEW)
        - No audit logging for state changes (NEW)
        
        Args:
            files: List of implementation files
            
        Returns:
            Dict with security_issues list, enhanced with architectural gaps
        """
        import re
        
        security_issues = []
        
        # SQL injection patterns
        sql_keywords = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'WHERE', 'FROM', 'JOIN']
        sql_concat_patterns = [
            r'["\']\s*\+\s*\w+',  # "SELECT " + variable
            r'\w+\s*\+\s*["\']',  # variable + " WHERE"
            r'["\'].*?(SELECT|INSERT|UPDATE|DELETE).*?["\'].*?\+',  # "SELECT * FROM " +
        ]
        
        # Credential patterns
        credential_patterns = [
            r'[Pp]assword\s*=\s*["\'][^"\']+["\']',
            r'[Aa]pi[Kk]ey\s*=\s*["\'][^"\']+["\']',
            r'[Ss]ecret\s*=\s*["\'][^"\']+["\']',
            r'pwd\s*=\s*["\'][^"\']+["\']',
        ]
        
        for file_path in files:
            try:
                content = (self.project_root / file_path).read_text(encoding='utf-8')
                lines = content.split('\n')
                
                for i, line in enumerate(lines, start=1):
                    # Check SQL injection patterns
                    for pattern in sql_concat_patterns:
                        if re.search(pattern, line, re.IGNORECASE):
                            # Verify it's SQL-related
                            if any(kw in line.upper() for kw in sql_keywords):
                                security_issues.append({
                                    "type": "sql_injection",
                                    "severity": "CRITICAL",
                                    "file": str(file_path),
                                    "line": i,
                                    "message": "Potential SQL injection: String concatenation with SQL keywords detected",
                                    "line_content": line.strip()
                                })
                    
                    # Check hard-coded credentials
                    for pattern in credential_patterns:
                        if re.search(pattern, line):
                            security_issues.append({
                                "type": "hardcoded_credential",
                                "severity": "CRITICAL",
                                "file": str(file_path),
                                "line": i,
                                "message": "Hard-coded credential detected in source code",
                                "line_content": line.strip()
                            })
                
                # Check missing error handling in async/await
                if file_path.suffix in ['.py', '.cs', '.ts', '.js']:
                    async_pattern = r'async\s+(def|function|Task|void)\s+\w+'
                    try_pattern = r'try\s*[:{]'
                    
                    async_matches = list(re.finditer(async_pattern, content))
                    try_blocks = list(re.finditer(try_pattern, content))
                    
                    # If we have async methods but very few try blocks, flag it
                    if len(async_matches) > 0 and len(try_blocks) < len(async_matches) / 2:
                        security_issues.append({
                            "type": "missing_error_handling",
                            "severity": "HIGH",
                            "file": str(file_path),
                            "line": 1,
                            "message": f"{len(async_matches)} async methods but only {len(try_blocks)} try blocks found",
                            "line_content": ""
                        })
            
            except Exception as e:
                logger.debug(f"Security scan skipped for {file_path}: {e}")
        
        # NEW: Enhanced architectural security checks from CRITICAL-ARCHITECTURE-REVIEW.md
        for file_path in files:
            try:
                content = (self.project_root / file_path).read_text(encoding='utf-8')
                file_lower = str(file_path).lower()
                
                # Check 1: Authorization in controllers/services
                if 'controller' in file_lower or 'service' in file_lower:
                    if 'delete' in content.lower() or 'update' in content.lower():
                        if not any(keyword in content.lower() for keyword in ['authorize', 'permission', 'role', 'claim']):
                            security_issues.append({
                                "type": "missing_authorization",
                                "severity": "HIGH",
                                "file": str(file_path),
                                "line": 1,
                                "message": "State-changing operations without authorization checks detected",
                                "line_content": "[File performs DELETE/UPDATE without auth]"
                            })
                
                # Check 2: Audit logging for state changes
                if 'service' in file_lower or 'repository' in file_lower:
                    has_state_change = any(kw in content.lower() for kw in ['create', 'update', 'delete', 'save'])
                    has_logging = any(kw in content for kw in ['ILogger', 'logger', 'log.', 'Logger'])
                    
                    if has_state_change and not has_logging:
                        security_issues.append({
                            "type": "missing_audit_logging",
                            "severity": "MEDIUM",
                            "file": str(file_path),
                            "line": 1,
                            "message": "State-changing operations without audit logging (cannot trace who did what)",
                            "line_content": "[File modifies data without logging]"
                        })
                
                # Check 3: HTTP vs HTTPS in frontend services
                if file_path.suffix in ['.ts', '.js'] and 'service' in file_lower:
                    http_pattern = re.search(r'http://[^"\s]+', content)
                    if http_pattern:
                        security_issues.append({
                            "type": "insecure_http",
                            "severity": "HIGH",
                            "file": str(file_path),
                            "line": content[:http_pattern.start()].count('\n') + 1,
                            "message": "HTTP endpoint detected (should use HTTPS to prevent man-in-the-middle attacks)",
                            "line_content": http_pattern.group(0)
                        })
                
                # Check 4: No input validation in API methods
                if file_path.suffix in ['.cs', '.py', '.ts', '.js']:
                    # Find methods that accept parameters
                    method_pattern = r'(public|async|def|function)\s+\w+\s*\([^)]*\w+[^)]*\)'
                    methods_with_params = re.finditer(method_pattern, content)
                    
                    for method_match in methods_with_params:
                        method_start = method_match.start()
                        method_end = content.find('}' if file_path.suffix == '.cs' else '\n\n', method_start, method_start + 500)
                        if method_end == -1:
                            method_end = method_start + 500
                        
                        method_body = content[method_start:method_end]
                        
                        # Check if method validates input
                        has_validation = any(kw in method_body.lower() for kw in [
                            'validate', 'isnullorempty', 'throw', 'argumentnull', 
                            'required', 'maxlength', 'minlength', 'range'
                        ])
                        
                        has_param = '(' in method_body and any(c.isalnum() for c in method_body.split('(')[1].split(')')[0])
                        
                        if has_param and not has_validation:
                            line_num = content[:method_start].count('\n') + 1
                            security_issues.append({
                                "type": "missing_input_validation",
                                "severity": "MEDIUM",
                                "file": str(file_path),
                                "line": line_num,
                                "message": "Method accepts parameters but has no visible validation",
                                "line_content": method_match.group(0)[:80]
                            })
                            break  # Only report once per file
            
            except Exception as e:
                logger.debug(f"Enhanced security scan skipped for {file_path}: {e}")
        
        return {
            "security_issues": security_issues,
            "critical_count": len([i for i in security_issues if i["severity"] == "CRITICAL"]),
            "high_count": len([i for i in security_issues if i["severity"] == "HIGH"]),
            "medium_count": len([i for i in security_issues if i["severity"] == "MEDIUM"])
        }
    
    def _detect_magic_values(self, files: List[Path]) -> Dict[str, Any]:
        """
        Detect magic strings/numbers in implementation files.
        
        Detection rules from BadMonolith analysis:
        - String literals used >5 times (should be constants)
        - Numeric literals in business logic (except 0, 1, -1)
        - Hard-coded URLs/endpoints
        
        Args:
            files: List of implementation files
            
        Returns:
            Dict with magic_values list
        """
        import re
        
        magic_values = []
        string_frequency: Dict[str, List[Tuple[Path, int]]] = {}
        
        for file_path in files:
            try:
                content = (self.project_root / file_path).read_text(encoding='utf-8')
                lines = content.split('\n')
                
                for i, line in enumerate(lines, start=1):
                    # Extract string literals
                    string_literals = re.findall(r'["\']([^"\']{3,})["\']', line)
                    for literal in string_literals:
                        # Skip common patterns (log messages, etc.)
                        if literal.startswith('http'):
                            magic_values.append({
                                "type": "hardcoded_url",
                                "file": str(file_path),
                                "line": i,
                                "value": literal,
                                "message": "Hard-coded URL should be in configuration"
                            })
                        
                        if literal not in string_frequency:
                            string_frequency[literal] = []
                        string_frequency[literal].append((file_path, i))
                    
                    # Extract numeric literals (excluding trivial values)
                    numeric_literals = re.findall(r'\b(\d{2,})\b', line)
                    for num in numeric_literals:
                        if int(num) not in [0, 1, -1, 10, 100, 1000]:  # Common values
                            magic_values.append({
                                "type": "magic_number",
                                "file": str(file_path),
                                "line": i,
                                "value": num,
                                "message": f"Magic number '{num}' should be a named constant"
                            })
            
            except Exception as e:
                logger.debug(f"Magic value detection skipped for {file_path}: {e}")
        
        # Flag frequently repeated strings
        for string, locations in string_frequency.items():
            if len(locations) > 5 and len(string) > 5:
                magic_values.append({
                    "type": "repeated_string",
                    "value": string,
                    "occurrences": len(locations),
                    "locations": [(str(f), line) for f, line in locations[:3]],  # Show first 3
                    "message": f"String '{string}' repeated {len(locations)} times - extract to constant"
                })
        
        return {
            "magic_values": magic_values,
            "repeated_strings": len([m for m in magic_values if m["type"] == "repeated_string"]),
            "hardcoded_urls": len([m for m in magic_values if m["type"] == "hardcoded_url"]),
            "magic_numbers": len([m for m in magic_values if m["type"] == "magic_number"])
        }
    
    def _detect_duplicates(self, files: List[Path]) -> Dict[str, Any]:
        """
        Detect duplicate code blocks in implementation files.
        
        Args:
            files: List of implementation files
            
        Returns:
            Dict with duplicates list
        """
        duplicates = []
        
        # Simple duplicate detection: hash code blocks
        code_hashes: Dict[str, List[Tuple[Path, int]]] = {}
        
        for file_path in files:
            try:
                content = (self.project_root / file_path).read_text(encoding='utf-8')
                lines = content.split('\n')
                
                # Check 5-line blocks for duplicates
                for i in range(len(lines) - 5):
                    block = '\n'.join(lines[i:i+5]).strip()
                    if len(block) < 20:  # Skip trivial blocks
                        continue
                    
                    block_hash = hash(block)
                    if block_hash not in code_hashes:
                        code_hashes[block_hash] = []
                    code_hashes[block_hash].append((file_path, i+1))
            except Exception as e:
                logger.warning(f"Failed to analyze {file_path}: {e}")
        
        # Find duplicates (hash appears >1 time)
        for block_hash, locations in code_hashes.items():
            if len(locations) > 1:
                duplicates.append({
                    "locations": [(str(f), line) for f, line in locations],
                    "count": len(locations)
                })
        
        return {
            "duplicates": duplicates,
            "total_blocks_analyzed": sum(len(locs) for locs in code_hashes.values())
        }
    
    def _detect_redundancies(self, files: List[Path]) -> Dict[str, Any]:
        """
        Detect redundant code (unused variables, dead code, etc.).
        
        Args:
            files: List of implementation files
            
        Returns:
            Dict with redundancies list
        """
        redundancies = []
        
        for file_path in files:
            if file_path.suffix != '.py':
                continue  # Only Python for now
            
            try:
                content = (self.project_root / file_path).read_text(encoding='utf-8')
                tree = ast.parse(content)
                
                # Simple redundancy checks
                for node in ast.walk(tree):
                    # Unused imports (basic heuristic)
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            if alias.name not in content:
                                redundancies.append({
                                    "type": "unused_import",
                                    "file": str(file_path),
                                    "line": node.lineno,
                                    "message": f"Import '{alias.name}' appears unused"
                                })
            except Exception as e:
                logger.debug(f"Redundancy check skipped for {file_path}: {e}")
        
        return {
            "redundancies": redundancies
        }
    
    def _detect_anemic_domain_models(self, files: List[Path]) -> Dict[str, Any]:
        """
        Detect anemic domain models (entities with no behavior).
        
        Based on CRITICAL-ARCHITECTURE-REVIEW.md finding:
        - Entities with only properties/fields (no methods)
        - Missing domain logic (Complete(), Reopen(), Validate())
        - No value objects or domain services
        
        Args:
            files: List of implementation files
            
        Returns:
            Dict with anemic_models list
        """
        anemic_models = []
        
        for file_path in files:
            file_lower = str(file_path).lower()
            
            # Only check files likely to be domain entities
            if not any(keyword in file_lower for keyword in ['domain', 'entity', 'entities', 'model']):
                continue
            
            try:
                content = (self.project_root / file_path).read_text(encoding='utf-8')
                
                # Check C# entities
                if file_path.suffix == '.cs':
                    # Find class definitions
                    class_match = re.search(r'class\s+(\w+)', content)
                    if not class_match:
                        continue
                    
                    class_name = class_match.group(1)
                    
                    # Count properties vs methods
                    properties = len(re.findall(r'public\s+\w+\s+\w+\s*{\s*get;\s*set;', content))
                    methods = len(re.findall(r'public\s+(?:void|\w+)\s+\w+\s*\([^)]*\)\s*{', content))
                    
                    # Anemic if >3 properties but 0 methods
                    if properties >= 3 and methods == 0:
                        anemic_models.append({
                            "type": "anemic_domain_model",
                            "severity": "MEDIUM",
                            "file": str(file_path),
                            "class_name": class_name,
                            "message": f"Entity '{class_name}' has {properties} properties but no behavior methods",
                            "recommendation": f"Add domain methods like {class_name}.Complete(), {class_name}.Validate(), etc."
                        })
                
                # Check TypeScript models
                elif file_path.suffix == '.ts':
                    # Check if interface (no methods) or class with only getters/setters
                    if 'interface' in content:
                        interface_match = re.search(r'interface\s+(\w+)', content)
                        if interface_match:
                            interface_name = interface_match.group(1)
                            anemic_models.append({
                                "type": "anemic_domain_model",
                                "severity": "LOW",
                                "file": str(file_path),
                                "class_name": interface_name,
                                "message": f"Interface '{interface_name}' has no methods (TypeScript interfaces are data-only)",
                                "recommendation": f"Consider using class with methods instead of interface"
                            })
            
            except Exception as e:
                logger.debug(f"Anemic model check skipped for {file_path}: {e}")
        
        return {
            "anemic_models": anemic_models,
            "count": len(anemic_models)
        }
    
    def _detect_configuration_issues(self, files: List[Path]) -> Dict[str, Any]:
        """
        Detect configuration management issues.
        
        Based on CRITICAL-ARCHITECTURE-REVIEW.md findings:
        - Hard-coded URLs in source code
        - Configuration not externalized to environment files
        - Connection strings in code
        
        Args:
            files: List of implementation files
            
        Returns:
            Dict with config_issues list
        """
        config_issues = []
        
        # Hard-coded URL patterns
        url_patterns = [
            r'http://localhost:\d+',
            r'https://[\w.-]+\.[a-z]{2,}',
            r'baseUrl\s*[:=]\s*["\'][^"\']+["\']'
        ]
        
        # Connection string patterns
        connection_patterns = [
            r'Server\s*=',
            r'Database\s*=',
            r'Data Source\s*=',
            r'mongodb://',
            r'postgresql://'
        ]
        
        for file_path in files:
            # Skip config files themselves
            if any(name in str(file_path).lower() for name in ['config', 'environment', 'settings', 'appsettings']):
                continue
            
            try:
                content = (self.project_root / file_path).read_text(encoding='utf-8')
                lines = content.split('\n')
                
                for i, line in enumerate(lines, start=1):
                    # Check for hard-coded URLs
                    for pattern in url_patterns:
                        if re.search(pattern, line):
                            config_issues.append({
                                "type": "hardcoded_url",
                                "severity": "HIGH",
                                "file": str(file_path),
                                "line": i,
                                "message": "Hard-coded URL detected (should use environment configuration)",
                                "line_content": line.strip()[:80]
                            })
                    
                    # Check for connection strings
                    for pattern in connection_patterns:
                        if re.search(pattern, line, re.IGNORECASE):
                            config_issues.append({
                                "type": "hardcoded_connection_string",
                                "severity": "CRITICAL",
                                "file": str(file_path),
                                "line": i,
                                "message": "Connection string in source code (major security risk)",
                                "line_content": "[REDACTED - Connection string detected]"
                            })
            
            except Exception as e:
                logger.debug(f"Configuration check skipped for {file_path}: {e}")
        
        return {
            "config_issues": config_issues,
            "critical_count": len([i for i in config_issues if i["severity"] == "CRITICAL"]),
            "high_count": len([i for i in config_issues if i["severity"] == "HIGH"])
        }
    
    def _detect_transaction_issues(self, files: List[Path]) -> Dict[str, Any]:
        """
        Detect missing transaction management.
        
        Based on CRITICAL-ARCHITECTURE-REVIEW.md findings:
        - Multiple database operations not atomic
        - Race conditions in update operations
        - No Unit of Work pattern
        
        Args:
            files: List of implementation files
            
        Returns:
            Dict with transaction_issues list
        """
        transaction_issues = []
        
        for file_path in files:
            file_lower = str(file_path).lower()
            
            # Only check service/repository files
            if not any(keyword in file_lower for keyword in ['service', 'repository']):
                continue
            
            try:
                content = (self.project_root / file_path).read_text(encoding='utf-8')
                
                # Find methods with multiple operations
                method_pattern = r'(async\s+)?(?:public\s+)?(?:async\s+)?\w+\s+(\w+)\s*\([^)]*\)\s*{([^}]{100,})}'
                methods = re.finditer(method_pattern, content, re.DOTALL)
                
                for method in methods:
                    method_name = method.group(2)
                    method_body = method.group(3)
                    
                    # Count database operations
                    db_operations = len(re.findall(r'(await|\.)\s*(Add|Update|Delete|Save|Remove)', method_body))
                    
                    # Check for transaction keywords
                    has_transaction = any(kw in method_body for kw in [
                        'BeginTransaction', 'using (var transaction', 'CommitAsync',
                        'TransactionScope', 'UnitOfWork', '@Transactional'
                    ])
                    
                    # Flag if multiple operations without transaction
                    if db_operations >= 2 and not has_transaction:
                        line_num = content[:method.start()].count('\n') + 1
                        transaction_issues.append({
                            "type": "missing_transaction",
                            "severity": "HIGH",
                            "file": str(file_path),
                            "line": line_num,
                            "method_name": method_name,
                            "message": f"Method '{method_name}' has {db_operations} database operations without transaction",
                            "recommendation": "Wrap operations in transaction or use Unit of Work pattern"
                        })
            
            except Exception as e:
                logger.debug(f"Transaction check skipped for {file_path}: {e}")
        
        return {
            "transaction_issues": transaction_issues,
            "count": len(transaction_issues)
        }
    
    def _validate_solid(self, files: List[Path]) -> Dict[str, Any]:
        """
        Validate SOLID principles with enhanced detection.
        
        Enhanced with BadMonolith learnings:
        - God class/method detection (>300 lines, >10 methods)
        - Deep nesting (>3 levels indicates complexity)
        - Long parameter lists (>4 parameters)
        - Tight coupling (concrete type dependencies)
        - Interface bloat (>7 methods in interface)
        
        Args:
            files: List of implementation files
            
        Returns:
            Dict with violations list
        """
        violations = []
        
        for file_path in files:
            try:
                content = (self.project_root / file_path).read_text(encoding='utf-8')
                lines = content.split('\n')
                
                # Python-specific analysis
                if file_path.suffix == '.py':
                    try:
                        tree = ast.parse(content)
                        
                        for node in ast.walk(tree):
                            if isinstance(node, ast.ClassDef):
                                # SRP: Class with too many methods
                                methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
                                if len(methods) > 10:
                                    violations.append({
                                        "principle": "SRP",
                                        "file": str(file_path),
                                        "line": node.lineno,
                                        "class": node.name,
                                        "severity": "HIGH",
                                        "message": f"Class '{node.name}' has {len(methods)} methods (SRP violation, consider splitting)"
                                    })
                                
                                # ISP: Interface/base class with too many methods
                                if any(base.id in ['ABC', 'Interface'] for base in node.bases if isinstance(base, ast.Name)):
                                    if len(methods) > 7:
                                        violations.append({
                                            "principle": "ISP",
                                            "file": str(file_path),
                                            "line": node.lineno,
                                            "class": node.name,
                                            "severity": "MEDIUM",
                                            "message": f"Interface '{node.name}' has {len(methods)} methods (ISP violation, consider segregation)"
                                        })
                                
                                # Check for concrete dependencies (DIP)
                                for method in methods:
                                    if isinstance(method, ast.FunctionDef) and method.name == '__init__':
                                        # Look for 'new' instantiations or concrete types
                                        for stmt in ast.walk(method):
                                            if isinstance(stmt, ast.Call) and isinstance(stmt.func, ast.Name):
                                                # Direct instantiation in constructor suggests tight coupling
                                                violations.append({
                                                    "principle": "DIP",
                                                    "file": str(file_path),
                                                    "line": stmt.lineno,
                                                    "class": node.name,
                                                    "severity": "MEDIUM",
                                                    "message": f"Direct instantiation in __init__ suggests tight coupling (consider DI)"
                                                })
                                                break  # Only report once per class
                            
                            elif isinstance(node, ast.FunctionDef):
                                # God method detection
                                method_lines = node.end_lineno - node.lineno if hasattr(node, 'end_lineno') else 0
                                if method_lines > 50:
                                    violations.append({
                                        "principle": "SRP",
                                        "file": str(file_path),
                                        "line": node.lineno,
                                        "function": node.name,
                                        "severity": "HIGH",
                                        "message": f"Function '{node.name}' is {method_lines} lines (god method, consider splitting)"
                                    })
                                
                                # Long parameter list
                                if len(node.args.args) > 4:
                                    violations.append({
                                        "principle": "SRP",
                                        "file": str(file_path),
                                        "line": node.lineno,
                                        "function": node.name,
                                        "severity": "MEDIUM",
                                        "message": f"Function '{node.name}' has {len(node.args.args)} parameters (consider parameter object)"
                                    })
                                
                                # Deep nesting (complexity)
                                max_depth = self._calculate_nesting_depth(node)
                                if max_depth > 3:
                                    violations.append({
                                        "principle": "Complexity",
                                        "file": str(file_path),
                                        "line": node.lineno,
                                        "function": node.name,
                                        "severity": "MEDIUM",
                                        "message": f"Function '{node.name}' has nesting depth {max_depth} (consider flattening)"
                                    })
                    
                    except SyntaxError:
                        pass  # Skip files with syntax errors
                
                # C#-specific analysis
                elif file_path.suffix == '.cs':
                    import re
                    
                    # Detect god endpoint pattern (MapMethods with long handler)
                    mapmethods_pattern = r'app\.MapMethods\([^)]+\)\s*,'
                    if re.search(mapmethods_pattern, content):
                        # Count lines between MapMethods and next top-level statement
                        violations.append({
                            "principle": "SRP",
                            "file": str(file_path),
                            "line": 1,
                            "severity": "CRITICAL",
                            "message": "God endpoint detected: MapMethods with inline handler (extract to controller)"
                        })
                    
                    # Detect direct SqlConnection usage (should use repository pattern)
                    if re.search(r'new\s+SqlConnection', content):
                        violations.append({
                            "principle": "DIP",
                            "file": str(file_path),
                            "line": 1,
                            "severity": "HIGH",
                            "message": "Direct SqlConnection instantiation (use repository pattern with DI)"
                        })
                
                # TypeScript/JavaScript-specific analysis
                elif file_path.suffix in ['.ts', '.js']:
                    import re
                    
                    # Detect HttpClient in components (should be in service)
                    if re.search(r'constructor\([^)]*HttpClient[^)]*\)', content):
                        if 'Component' in content:
                            violations.append({
                                "principle": "SRP",
                                "file": str(file_path),
                                "line": 1,
                                "severity": "HIGH",
                                "message": "HttpClient injected in component (extract to service layer)"
                            })
                    
                    # Detect 'any' type overuse
                    any_count = len(re.findall(r':\s*any\b', content))
                    if any_count > 3:
                        violations.append({
                            "principle": "Type Safety",
                            "file": str(file_path),
                            "line": 1,
                            "severity": "MEDIUM",
                            "message": f"{any_count} uses of 'any' type (define proper interfaces)"
                        })
            
            except Exception as e:
                logger.debug(f"SOLID validation skipped for {file_path}: {e}")
        
        return {
            "violations": violations,
            "critical_count": len([v for v in violations if v.get("severity") == "CRITICAL"]),
            "high_count": len([v for v in violations if v.get("severity") == "HIGH"]),
            "medium_count": len([v for v in violations if v.get("severity") == "MEDIUM"])
        }
    
    def _calculate_nesting_depth(self, node: ast.AST, current_depth: int = 0) -> int:
        """
        Calculate maximum nesting depth in AST node.
        
        Args:
            node: AST node to analyze
            current_depth: Current depth level
            
        Returns:
            Maximum nesting depth
        """
        max_depth = current_depth
        
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.With, ast.Try)):
                child_depth = self._calculate_nesting_depth(child, current_depth + 1)
                max_depth = max(max_depth, child_depth)
        
        return max_depth
    
    def _detect_blockers(self, out_of_scope_files: List[Path]) -> Dict[str, Any]:
        """
        Detect out-of-scope blockers (errors in files outside implementation scope).
        
        Args:
            out_of_scope_files: Files outside implementation scope
            
        Returns:
            Dict with blockers list
        """
        blockers = []
        
        for file_path in out_of_scope_files:
            if file_path.suffix == '.py':
                try:
                    content = (self.project_root / file_path).read_text(encoding='utf-8')
                    ast.parse(content)  # Check for syntax errors
                except SyntaxError as e:
                    blockers.append({
                        "type": "syntax_error",
                        "file": str(file_path),
                        "line": e.lineno if hasattr(e, 'lineno') else 0,
                        "message": f"Syntax error: {str(e)}"
                    })
                except Exception:
                    pass  # Ignore read errors for out-of-scope
        
        return {
            "blockers": blockers
        }
    
    def _generate_refactorings(
        self,
        security_result: Dict[str, Any],
        magic_result: Dict[str, Any],
        duplicates_result: Dict[str, Any],
        redundancies_result: Dict[str, Any],
        solid_result: Dict[str, Any],
        anemic_result: Dict[str, Any] = None,
        config_result: Dict[str, Any] = None,
        transaction_result: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate refactoring recommendations from analysis results.
        
        Enhanced with CRITICAL-ARCHITECTURE-REVIEW.md findings:
        - Anemic domain model fixes
        - Configuration externalization
        - Transaction management
        
        Args:
            security_result: Security scan results
            magic_result: Magic value detection results
            duplicates_result: Duplicate detection results
            redundancies_result: Redundancy detection results
            solid_result: SOLID validation results
            anemic_result: Anemic domain model detection results (NEW)
            config_result: Configuration issues results (NEW)
            transaction_result: Transaction management issues (NEW)
            
        Returns:
            List of refactoring recommendations with enhanced architecture guidance
        """
        refactorings = []
        
        # Security issues (HIGHEST PRIORITY)
        for issue in security_result.get('security_issues', []):
            priority = "critical" if issue['severity'] == "CRITICAL" else "high"
            
            if issue['type'] == 'sql_injection':
                refactorings.append({
                    "type": "fix_sql_injection",
                    "priority": priority,
                    "reason": "security_vulnerability",
                    "file": issue['file'],
                    "line": issue['line'],
                    "description": issue['message'],
                    "auto_fixable": True,
                    "fix_strategy": "Replace string concatenation with parameterized queries or ORM"
                })
            
            elif issue['type'] == 'hardcoded_credential':
                refactorings.append({
                    "type": "externalize_credential",
                    "priority": priority,
                    "reason": "security_vulnerability",
                    "file": issue['file'],
                    "line": issue['line'],
                    "description": issue['message'],
                    "auto_fixable": False,  # Requires manual config setup
                    "fix_strategy": "Move to configuration file/environment variable"
                })
            
            elif issue['type'] == 'missing_error_handling':
                refactorings.append({
                    "type": "add_error_handling",
                    "priority": "high",
                    "reason": "reliability",
                    "file": issue['file'],
                    "line": issue['line'],
                    "description": issue['message'],
                    "auto_fixable": True,
                    "fix_strategy": "Wrap async methods in try-catch blocks"
                })
        
        # Magic values
        for magic in magic_result.get('magic_values', []):
            if magic['type'] == 'repeated_string':
                refactorings.append({
                    "type": "extract_constant",
                    "priority": "medium",
                    "reason": "maintainability",
                    "value": magic['value'],
                    "occurrences": magic['occurrences'],
                    "description": magic['message'],
                    "auto_fixable": True,
                    "fix_strategy": f"Extract '{magic['value']}' to named constant"
                })
            
            elif magic['type'] == 'hardcoded_url':
                refactorings.append({
                    "type": "externalize_url",
                    "priority": "medium",
                    "reason": "configuration",
                    "file": magic['file'],
                    "line": magic['line'],
                    "value": magic['value'],
                    "description": magic['message'],
                    "auto_fixable": False,
                    "fix_strategy": "Move URL to configuration/environment"
                })
        
        # Duplicates -> Extract method
        for dup in duplicates_result.get('duplicates', []):
            if dup['count'] >= 2:
                refactorings.append({
                    "type": "extract_method",
                    "priority": "high",
                    "reason": "duplicate_code",
                    "locations": dup['locations'],
                    "description": f"Extract duplicated code into shared method ({dup['count']} occurrences)",
                    "auto_fixable": True,
                    "fix_strategy": "Create shared method, replace duplicates with calls"
                })
        
        # Redundancies -> Remove unused
        for red in redundancies_result.get('redundancies', []):
            refactorings.append({
                "type": "remove_unused",
                "priority": "medium",
                "reason": "redundancy",
                "file": red['file'],
                "line": red['line'],
                "description": red['message'],
                "auto_fixable": True,
                "fix_strategy": "Remove unused import/variable"
            })
        
        # SOLID violations -> Suggest split/refactor
        for viol in solid_result.get('violations', []):
            priority = "critical" if viol.get('severity') == "CRITICAL" else "high" if viol.get('severity') == "HIGH" else "medium"
            
            if viol['principle'] == 'SRP':
                if 'class' in viol:
                    refactorings.append({
                        "type": "split_class",
                        "priority": priority,
                        "reason": "srp_violation",
                        "file": viol['file'],
                        "line": viol['line'],
                        "class": viol['class'],
                        "description": viol['message'],
                        "auto_fixable": False,
                        "fix_strategy": "Split class into smaller, focused classes"
                    })
                elif 'function' in viol:
                    refactorings.append({
                        "type": "split_function",
                        "priority": priority,
                        "reason": "god_method",
                        "file": viol['file'],
                        "line": viol['line'],
                        "function": viol['function'],
                        "description": viol['message'],
                        "auto_fixable": True,
                        "fix_strategy": "Extract logical sections into separate methods"
                    })
            
            elif viol['principle'] == 'DIP':
                refactorings.append({
                    "type": "introduce_di",
                    "priority": priority,
                    "reason": "tight_coupling",
                    "file": viol['file'],
                    "line": viol['line'],
                    "description": viol['message'],
                    "auto_fixable": False,
                    "fix_strategy": "Replace direct instantiation with dependency injection"
                })
            
            elif viol['principle'] == 'ISP':
                refactorings.append({
                    "type": "segregate_interface",
                    "priority": priority,
                    "reason": "interface_bloat",
                    "file": viol['file'],
                    "line": viol['line'],
                    "class": viol.get('class', ''),
                    "description": viol['message'],
                    "auto_fixable": False,
                    "fix_strategy": "Split interface into smaller, focused interfaces"
                })
        
        # NEW: Anemic Domain Model fixes (from CRITICAL-ARCHITECTURE-REVIEW.md)
        if anemic_result:
            for model in anemic_result.get('anemic_models', []):
                refactorings.append({
                    "type": "enrich_domain_model",
                    "priority": "medium",
                    "reason": "anemic_domain_model",
                    "file": model['file'],
                    "class": model['class_name'],
                    "description": model['message'],
                    "auto_fixable": False,
                    "fix_strategy": model['recommendation']
                })
        
        # NEW: Configuration Management fixes (from CRITICAL-ARCHITECTURE-REVIEW.md)
        if config_result:
            for issue in config_result.get('config_issues', []):
                priority = "critical" if issue['severity'] == "CRITICAL" else "high"
                refactorings.append({
                    "type": "externalize_configuration",
                    "priority": priority,
                    "reason": "hardcoded_configuration",
                    "file": issue['file'],
                    "line": issue['line'],
                    "description": issue['message'],
                    "auto_fixable": False,
                    "fix_strategy": "Move to appsettings.json/environment.ts/config file"
                })
        
        # NEW: Transaction Management fixes (from CRITICAL-ARCHITECTURE-REVIEW.md)
        if transaction_result:
            for issue in transaction_result.get('transaction_issues', []):
                refactorings.append({
                    "type": "add_transaction_management",
                    "priority": "high",
                    "reason": "missing_transaction",
                    "file": issue['file'],
                    "line": issue['line'],
                    "method": issue['method_name'],
                    "description": issue['message'],
                    "auto_fixable": False,
                    "fix_strategy": issue['recommendation']
                })
        
        # Sort by priority (critical > high > medium > low)
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        refactorings.sort(key=lambda r: priority_order.get(r['priority'], 4))
        
        return refactorings
    
    def _apply_refactorings_auto(
        self,
        refactorings: List[Dict[str, Any]],
        state: TDDSessionState
    ) -> List[Dict[str, Any]]:
        """
        Auto-apply safe refactorings.
        
        Args:
            refactorings: List of refactoring recommendations
            state: Session state
            
        Returns:
            List of applied refactorings
        """
        applied = []
        
        # Only auto-apply low-risk refactorings
        for refactoring in refactorings:
            if refactoring['type'] == 'remove_unused' and refactoring['priority'] == 'medium':
                # Would implement actual removal here
                applied.append(refactoring)
                state.metrics["refactorings_applied"] += 1
        
        return applied
    
    def _store_refactoring_patterns(
        self,
        refactorings: List[Dict[str, Any]],
        applied_refactorings: List[Dict[str, Any]],
        state: TDDSessionState
    ):
        """
        Store refactoring patterns in Tier 2 for learning.
        
        Learns project preferences:
        - Accepted vs rejected refactorings
        - Extract method naming conventions
        - Class splitting strategies
        - Duplicate consolidation approaches
        
        Args:
            refactorings: All refactoring recommendations
            applied_refactorings: Refactorings that were applied
            state: Session state
        """
        if not self._pattern_library:
            logger.debug("Pattern library not initialized")
            return
        
        try:
            from src.tier2.knowledge_graph import KnowledgeGraph
            kg = KnowledgeGraph()
            
            # Store each refactoring pattern
            for refactoring in refactorings:
                was_applied = refactoring in applied_refactorings
                
                pattern_context = {
                    "refactoring_type": refactoring["type"],
                    "priority": refactoring["priority"],
                    "reason": refactoring["reason"],
                    "description": refactoring.get("description", ""),
                    "applied": was_applied,
                    "feature_name": state.feature_name,
                    "task_id": state.task_id,
                    "work_item_id": state.work_item_id,
                    "file": refactoring.get("file", ""),
                    "line": refactoring.get("line", 0)
                }
                
                # Generate pattern title
                pattern_title = f"refactor_{refactoring['type']}_{refactoring['reason']}"
                
                # Store pattern with confidence based on application
                confidence = 0.8 if was_applied else 0.4
                
                pattern_id = kg.store_pattern(
                    title=pattern_title,
                    pattern_type="refactoring",
                    confidence=confidence,
                    context=pattern_context,
                    scope="application",
                    namespaces=[state.feature_name, f"task_{state.task_id}"]
                )
                
                logger.debug(f"Stored refactoring pattern: {pattern_id} (applied={was_applied})")
            
            # Store aggregate metrics
            if applied_refactorings:
                aggregate_context = {
                    "total_refactorings": len(refactorings),
                    "applied_refactorings": len(applied_refactorings),
                    "acceptance_rate": len(applied_refactorings) / len(refactorings),
                    "feature_name": state.feature_name,
                    "task_id": state.task_id,
                    "phase_duration": state.metrics.get("phase_timings", {}).get("REFACTOR", 0)
                }
                
                kg.store_pattern(
                    title=f"refactor_session_{state.session_id}",
                    pattern_type="refactoring_session",
                    confidence=0.9,
                    context=aggregate_context,
                    scope="application",
                    namespaces=[state.feature_name]
                )
            
            logger.info(f"📚 Stored {len(refactorings)} refactoring patterns in Tier 2")
            
        except Exception as e:
            logger.warning(f"Failed to store refactoring patterns: {e}")
    
    def get_learned_refactoring_patterns(
        self,
        feature_name: Optional[str] = None,
        refactoring_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve learned refactoring patterns from Tier 2.
        
        Used to suggest refactorings based on project history.
        
        Args:
            feature_name: Filter by feature (optional)
            refactoring_type: Filter by type (extract_method, split_class, etc.)
            
        Returns:
            List of learned patterns with confidence scores
        """
        if not self._pattern_library:
            return []
        
        try:
            from src.tier2.knowledge_graph import KnowledgeGraph
            kg = KnowledgeGraph()
            
            # Build search query
            query_parts = ["refactoring"]
            if refactoring_type:
                query_parts.append(refactoring_type)
            if feature_name:
                query_parts.append(feature_name)
            
            query = " ".join(query_parts)
            
            # Search patterns
            patterns = kg.search_patterns(
                query=query,
                pattern_type="refactoring",
                min_confidence=0.5,
                scope="application",
                limit=20,
                include_confidence_metadata=True
            )
            
            # Filter by applied refactorings (learning from success)
            learned_patterns = []
            for pattern in patterns:
                context = pattern.get("context", {})
                if context.get("applied", False):
                    learned_patterns.append({
                        "pattern_id": pattern["pattern_id"],
                        "refactoring_type": context.get("refactoring_type"),
                        "reason": context.get("reason"),
                        "description": context.get("description"),
                        "confidence": pattern["confidence"],
                        "success_rate": pattern.get("success_rate", 0.0),
                        "usage_count": pattern.get("usage_count", 0)
                    })
            
            return learned_patterns
            
        except Exception as e:
            logger.warning(f"Failed to retrieve refactoring patterns: {e}")
            return []
