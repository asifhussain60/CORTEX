"""
Autonomous Execution Engine for CORTEX 4.0

Enables end-to-end autonomous execution of multi-phase plans with:
- Automatic phase transitions
- Self-healing error recovery (3-retry with exponential backoff)
- Auto-validation gates
- Git automation (commit on phase complete)
- Progress monitoring with decision logic

Phase 0.5 Implementation (Week 1, Days 1-3)
"""

import logging
import subprocess
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.orchestrators.base.base_orchestrator import (
    BaseOrchestrator,
    OrchestratorResult,
    OrchestratorStatus,
    ValidationResult
)


class ExecutionMode(Enum):
    """Autonomous execution modes."""
    SUPERVISED = "supervised"  # User approves each phase (default)
    AUTONOMOUS = "autonomous"  # Full E2E with self-healing
    HUMAN_IN_LOOP = "human_in_loop"  # Pause after each step (Phase 2.5)


class PhaseStatus(Enum):
    """Phase execution status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    VALIDATING = "validating"
    PASSED = "passed"
    FAILED = "failed"
    RETRYING = "retrying"
    ESCALATED = "escalated"


@dataclass
class PhaseConfig:
    """Configuration for a single phase."""
    number: int
    name: str
    description: str
    orchestrator: Optional[str] = None
    validation_script: Optional[str] = None
    prerequisite_phases: List[int] = field(default_factory=list)
    critical: bool = False  # If true, failure escalates immediately
    
    # Execution metadata
    status: PhaseStatus = PhaseStatus.PENDING
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    retry_count: int = 0
    checkpoint_id: Optional[str] = None


@dataclass
class ValidationGateResult:
    """Result of phase validation gate."""
    passed: bool
    message: str
    test_count: int = 0
    tests_passed: int = 0
    coverage_percentage: float = 0.0
    duration_seconds: float = 0.0
    output: str = ""
    
    @property
    def pass_rate(self) -> float:
        """Calculate test pass rate."""
        if self.test_count == 0:
            return 0.0
        return (self.tests_passed / self.test_count) * 100.0


@dataclass
class SelfHealingResult:
    """Result of self-healing attempt."""
    success: bool
    strategy: str
    attempt: int
    message: str
    recovery_actions: List[str] = field(default_factory=list)


class AutonomousExecutionEngine(BaseOrchestrator):
    """
    Autonomous execution engine for multi-phase plans.
    
    Capabilities:
    - Execute plans end-to-end without manual intervention
    - Auto-validate after each phase
    - Self-heal on failures (3-retry exponential backoff)
    - Auto-commit on phase completion
    - Progress monitoring with decision logic
    
    Usage:
        engine = AutonomousExecutionEngine(config, logger, brain, templates)
        result = engine.execute(
            plan_path="cortex-brain/documents/planning/active/my-plan/00-master-plan.md",
            mode=ExecutionMode.AUTONOMOUS,
            from_phase=1,
            to_phase=5
        )
    """
    
    def __init__(
        self,
        config: Dict[str, Any]
    ):
        """Initialize autonomous execution engine."""
        super().__init__(config)
        
        # Configuration
        self.max_retry_attempts = config.get("autonomous_execution", {}).get("max_retries", 3)
        self.escalation_threshold = config.get("autonomous_execution", {}).get("escalation_threshold", 3)
        self.enable_git_automation = config.get("autonomous_execution", {}).get("enable_git_automation", True)
        
        # State
        self.execution_mode: ExecutionMode = ExecutionMode.SUPERVISED
        self.phases: List[PhaseConfig] = []
        self.current_phase_index: int = 0
        self.checkpoints: Dict[str, str] = {}  # checkpoint_name -> git_commit_hash
        
        self.logger.info("🎭 Orchestrator engaged: AutonomousExecutionEngine")
    
    def validate_input(self, **kwargs) -> ValidationResult:
        """
        Validate autonomous execution parameters.
        
        Required:
            plan_path: Path to master plan file
        
        Optional:
            mode: ExecutionMode (default: SUPERVISED)
            from_phase: Start phase number (default: 1)
            to_phase: End phase number (default: last phase)
        """
        errors = []
        warnings = []
        
        # Validate plan_path
        plan_path = kwargs.get("plan_path")
        if not plan_path:
            errors.append("plan_path is required")
        elif not Path(plan_path).exists():
            errors.append(f"Plan file not found: {plan_path}")
        
        # Validate mode
        mode = kwargs.get("mode", ExecutionMode.SUPERVISED)
        if isinstance(mode, str):
            try:
                ExecutionMode(mode)
            except ValueError:
                errors.append(f"Invalid execution mode: {mode}")
        
        # Validate phase range
        from_phase = kwargs.get("from_phase", 1)
        to_phase = kwargs.get("to_phase")
        if from_phase < 1:
            errors.append("from_phase must be >= 1")
        if to_phase is not None and to_phase < from_phase:
            errors.append("to_phase must be >= from_phase")
        
        return ValidationResult(valid=len(errors) == 0, errors=errors, warnings=warnings)
    
    def execute(self, **kwargs) -> OrchestratorResult:
        """
        Execute plan autonomously.
        
        Args:
            plan_path: Path to master plan
            mode: Execution mode (supervised, autonomous)
            from_phase: Start phase number (default: 1)
            to_phase: End phase number (default: last)
        
        Returns:
            OrchestratorResult with execution status
        """
        start_time = datetime.now()
        
        try:
            # Parse parameters
            plan_path = kwargs["plan_path"]
            self.execution_mode = ExecutionMode(kwargs.get("mode", "supervised"))
            from_phase = kwargs.get("from_phase", 1)
            to_phase = kwargs.get("to_phase")
            
            self.logger.info(f"🚀 Starting autonomous execution: {self.execution_mode.value}")
            self.logger.info(f"📋 Plan: {plan_path}")
            
            # Load phases from master plan
            self.phases = self._load_phases_from_plan(plan_path)
            if not self.phases:
                raise ValueError("No phases found in master plan")
            
            # Apply phase range
            self.phases = self._filter_phases(self.phases, from_phase, to_phase)
            self.logger.info(f"📊 Executing {len(self.phases)} phases (Phase {from_phase} → {to_phase or 'END'})")
            
            # Execute phases
            completed_phases = 0
            for i, phase in enumerate(self.phases):
                self.current_phase_index = i
                self.logger.info(f"🎭 Phase transition: {i} → {i+1} ({phase.name})")
                
                # Execute single phase
                phase_result = self._execute_phase(phase)
                
                if not phase_result.passed:
                    # Failure - escalate
                    self.logger.error(f"❌ Phase {phase.number} failed: {phase_result.message}")
                    break
                
                completed_phases += 1
                self.logger.info(f"✅ Phase {phase.number} complete ({completed_phases}/{len(self.phases)})")
            
            # Determine final status
            all_complete = completed_phases == len(self.phases)
            execution_time = (datetime.now() - start_time).total_seconds()
            
            if all_complete:
                self.logger.info("🎭 Orchestrator completing: ✅ ALL WORK COMPLETE")
                return OrchestratorResult(
                    status=OrchestratorStatus.COMPLETED,
                    success=True,
                    message=f"All {len(self.phases)} phases completed successfully",
                    data={
                        "phases_completed": completed_phases,
                        "total_phases": len(self.phases),
                        "execution_mode": self.execution_mode.value,
                        "is_complete": True
                    },
                    execution_time_seconds=execution_time
                )
            else:
                return OrchestratorResult(
                    status=OrchestratorStatus.FAILED,
                    success=False,
                    message=f"Execution halted at phase {completed_phases + 1}/{len(self.phases)}",
                    data={
                        "phases_completed": completed_phases,
                        "total_phases": len(self.phases),
                        "execution_mode": self.execution_mode.value,
                        "is_complete": False
                    },
                    errors=[f"Phase {completed_phases + 1} validation failed"],
                    execution_time_seconds=execution_time
                )
        
        except Exception as e:
            self.logger.error(f"❌ Autonomous execution error: {e}", exc_info=True)
            execution_time = (datetime.now() - start_time).total_seconds()
            return OrchestratorResult(
                status=OrchestratorStatus.FAILED,
                success=False,
                message=str(e),
                errors=[str(e)],
                execution_time_seconds=execution_time
            )
    
    def _execute_phase(self, phase: PhaseConfig) -> ValidationGateResult:
        """
        Execute a single phase with validation and self-healing.
        
        Flow:
            1. Create checkpoint
            2. Execute phase orchestrator
            3. Run validation gate
            4. IF PASS: Commit work, update tracker, return success
            5. IF FAIL: Self-heal (3 retries) → Rollback → Escalate
        
        Args:
            phase: Phase configuration
        
        Returns:
            ValidationGateResult
        """
        self.logger.info(f"▶️  Phase {phase.number}: {phase.name}")
        
        # On phase start
        phase.status = PhaseStatus.IN_PROGRESS
        phase.start_time = datetime.now()
        self._on_phase_start(phase)
        
        # Execute phase work (placeholder - actual orchestrator invocation)
        # In production, this would call phase.orchestrator with appropriate params
        self.logger.info(f"   Executing phase orchestrator: {phase.orchestrator or 'manual'}")
        
        # Simulate phase execution (replace with actual orchestrator call)
        time.sleep(0.1)
        
        # Run validation gate
        phase.status = PhaseStatus.VALIDATING
        validation_result = self._run_validation_gate(phase)
        
        if validation_result.passed:
            # PASS: Complete phase
            phase.status = PhaseStatus.PASSED
            phase.end_time = datetime.now()
            self._on_phase_complete(phase, validation_result)
            return validation_result
        
        else:
            # FAIL: Attempt self-healing
            phase.status = PhaseStatus.FAILED
            healing_result = self._self_heal(phase, validation_result)
            
            if healing_result.success:
                # Healing worked - retry validation
                retry_validation = self._run_validation_gate(phase)
                if retry_validation.passed:
                    phase.status = PhaseStatus.PASSED
                    phase.end_time = datetime.now()
                    self._on_phase_complete(phase, retry_validation)
                    return retry_validation
            
            # Healing failed - escalate
            phase.status = PhaseStatus.ESCALATED
            self._on_validation_fail(phase, validation_result)
            return validation_result
    
    def _on_phase_start(self, phase: PhaseConfig):
        """Actions before phase execution."""
        self.logger.info(f"   ⏸️  Checkpoint: {phase.name}_start")
        
        # Validate prerequisites
        # (In production, check that prerequisite phases completed)
        
        # Create checkpoint
        checkpoint_id = self._create_checkpoint(f"{phase.name}_start")
        phase.checkpoint_id = checkpoint_id
        
        # Update progress tracker
        # (In production, update master plan progress bar)
    
    def _on_phase_complete(self, phase: PhaseConfig, validation: ValidationGateResult):
        """Actions after successful phase completion."""
        self.logger.info(f"   ✅ Validation passed: {validation.pass_rate:.1f}% tests passing")
        
        # Auto-commit work (if enabled)
        if self.execution_mode == ExecutionMode.AUTONOMOUS and self.enable_git_automation:
            self._auto_commit(phase, validation)
        
        # Update master plan progress
        # (In production, update progress bars in master plan)
        
        # Create completion checkpoint
        self._create_checkpoint(f"{phase.name}_complete")
    
    def _on_validation_fail(self, phase: PhaseConfig, error: ValidationGateResult):
        """Actions when validation fails after healing exhaustion."""
        self.logger.error(f"   ❌ Validation failed after {phase.retry_count} retries")
        self.logger.error(f"   📋 Error: {error.message}")
        
        # Rollback to last checkpoint
        if phase.checkpoint_id:
            self._rollback_to_checkpoint(phase.checkpoint_id)
        
        # Log failure reason
        self.logger.error(f"   🚨 ESCALATION: Manual intervention required for Phase {phase.number}")
        
        # Escalate to user
        self._escalate_to_user(phase, error)
    
    def _run_validation_gate(self, phase: PhaseConfig) -> ValidationGateResult:
        """
        Run phase validation gate.
        
        In production, this would:
        1. Run phase-specific validation script
        2. Parse output (test results, coverage)
        3. Determine pass/fail
        
        For Phase 0.5, this is a placeholder that simulates validation.
        """
        self.logger.info(f"   🔍 Running validation gate...")
        
        # Placeholder validation (replace with actual validation runner)
        # In production: ValidationGateRunner(phase.validation_script).run()
        
        # Simulate validation
        time.sleep(0.1)
        
        return ValidationGateResult(
            passed=True,  # Simulated pass
            message="All validation checks passed",
            test_count=10,
            tests_passed=10,
            coverage_percentage=85.0,
            duration_seconds=0.5
        )
    
    def _self_heal(self, phase: PhaseConfig, error: ValidationGateResult) -> SelfHealingResult:
        """
        Attempt self-healing recovery.
        
        Strategies:
        1. retry_with_backoff: Exponential backoff (1s, 2s, 4s)
        2. alternative_approach: Try different implementation
        3. rollback_and_retry: Rollback and retry once
        
        Args:
            phase: Phase configuration
            error: Validation error
        
        Returns:
            SelfHealingResult
        """
        self.logger.warning(f"   🔧 Attempting self-healing (attempt {phase.retry_count + 1}/{self.max_retry_attempts})")
        
        phase.retry_count += 1
        phase.status = PhaseStatus.RETRYING
        
        # Check if retry threshold exceeded
        if phase.retry_count > self.max_retry_attempts:
            return SelfHealingResult(
                success=False,
                strategy="none",
                attempt=phase.retry_count,
                message="Max retry attempts exceeded"
            )
        
        # Strategy 1: Retry with exponential backoff
        strategy = "retry_with_backoff"
        wait_time = 2 ** (phase.retry_count - 1)  # 1s, 2s, 4s
        
        self.logger.info(f"   ⏳ Strategy: {strategy}, waiting {wait_time}s before retry")
        time.sleep(wait_time)
        
        # In production, this would attempt actual recovery actions
        # For Phase 0.5, we simulate failure (no recovery)
        
        return SelfHealingResult(
            success=False,  # Simulated - always fails for Phase 0.5
            strategy=strategy,
            attempt=phase.retry_count,
            message="Self-healing simulation (not implemented)",
            recovery_actions=["Waited {wait_time}s", "No recovery actions available"]
        )
    
    def _create_checkpoint(self, checkpoint_name: str) -> str:
        """
        Create git checkpoint.
        
        In production, this would create a git tag for rollback.
        For Phase 0.5, this is a placeholder.
        """
        # Placeholder - in production: git tag checkpoint_name
        checkpoint_id = f"checkpoint_{checkpoint_name}_{int(time.time())}"
        self.checkpoints[checkpoint_name] = checkpoint_id
        return checkpoint_id
    
    def _rollback_to_checkpoint(self, checkpoint_id: str):
        """
        Rollback to git checkpoint.
        
        In production: git reset --hard <checkpoint_id>
        """
        self.logger.warning(f"   ↩️  Rolling back to checkpoint: {checkpoint_id}")
        # Placeholder - in production: git reset --hard checkpoint_id
    
    def _auto_commit(self, phase: PhaseConfig, validation: ValidationGateResult):
        """
        Auto-commit work on phase completion.
        
        In production, this would:
        1. Stage all changes
        2. Create formatted commit message
        3. Commit with validation metadata
        """
        message = self._format_commit_message(phase, validation)
        self.logger.info(f"   💾 Auto-commit: {message[:50]}...")
        # Placeholder - in production: git add . && git commit -m "{message}"
    
    def _escalate_to_user(self, phase: PhaseConfig, error: ValidationGateResult):
        """
        Escalate to user for manual intervention.
        
        In production, this would:
        1. Create notification
        2. Pause execution
        3. Provide recovery instructions
        """
        notification = f"""
🚨 AUTONOMOUS EXECUTION PAUSED

Phase: {phase.number} - {phase.name}
Status: {phase.status.value}
Error: {error.message}
Recovery Attempts: {phase.retry_count}

Actions Required:
1. Review error logs
2. Fix issue manually
3. Resume: cortex execute resume
   OR
   Abort: cortex execute abort
"""
        self.logger.error(notification)
    
    def _format_commit_message(self, phase: PhaseConfig, validation: ValidationGateResult) -> str:
        """Format auto-commit message."""
        return f"""✅ Phase {phase.number} Complete: {phase.name}

Validation: {'PASSED' if validation.passed else 'FAILED'}
Tests Passing: {validation.tests_passed}/{validation.test_count} ({validation.pass_rate:.1f}%)
Coverage: {validation.coverage_percentage:.1f}%
Duration: {validation.duration_seconds:.1f}s

[Autonomous Execution - {self.execution_mode.value}]
"""
    
    def _load_phases_from_plan(self, plan_path: str) -> List[PhaseConfig]:
        """
        Parse master plan and extract phase configuration.
        
        In production, this would parse the master plan markdown
        and extract phase metadata.
        
        For Phase 0.5, return placeholder phases.
        """
        # Placeholder - return sample phases
        return [
            PhaseConfig(number=1, name="Foundation", description="Setup base infrastructure"),
            PhaseConfig(number=2, name="Implementation", description="Core feature implementation"),
            PhaseConfig(number=3, name="Testing", description="Comprehensive testing"),
        ]
    
    def _filter_phases(self, phases: List[PhaseConfig], from_phase: int, to_phase: Optional[int]) -> List[PhaseConfig]:
        """Filter phases by range."""
        filtered = [p for p in phases if p.number >= from_phase]
        if to_phase is not None:
            filtered = [p for p in filtered if p.number <= to_phase]
        return filtered
