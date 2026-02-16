"""
HolisticRefactoringSweep - Auto-Injected Workflow Epilogue (Phase 100 Stage 8).

AC_START: AC-PHASE100-S8-002
Purpose: Holistic refactoring sweep across ALL workflow-modified files
Authority: phase-100-workflow-template-library.yaml § Stage 8
Compliance: CORE-008 (TDD), CORE-035 (RefactoringOrchestrator), CORE-049 (silent execution)

Features:
- Collects ALL files modified during multi-phase workflow
- LENS baseline measurement before refactoring
- Convergence loop: measure → refactor → re-measure (until baseline met)
- Ensures holistic coherence (no local optima from individual phases)
- Auto-injection by MasterOrchestrator as final epilogue
"""

import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Any, Optional
from enum import Enum


class SweepState(Enum):
    """Sweep execution states."""
    PENDING = "pending"
    COLLECTING = "collecting"
    MEASURING = "measuring"
    REFACTORING = "refactoring"
    CONVERGED = "converged"
    FAILED = "failed"


@dataclass
class LENSScoreSnapshot:
    """
    LENS score snapshot for baseline comparison.
    
    Attributes:
        overall_score: Overall LENS score (0-100)
        maintainability: Maintainability score
        complexity: Complexity score
        duplication: Duplication score
        timestamp: When snapshot taken
    """
    overall_score: float
    maintainability: float
    complexity: float
    duplication: float
    timestamp: float


@dataclass
class RefactoringResult:
    """
    Result of refactoring operation.
    
    Attributes:
        files_refactored: Number of files refactored
        patterns_applied: List of refactoring patterns applied
        tests_pass: True if all tests still pass
    """
    files_refactored: int
    patterns_applied: List[str]
    tests_pass: bool


@dataclass
class SweepResult:
    """
    Result of HolisticRefactoringSweep execution.
    
    Attributes:
        converged: True if baseline score achieved
        cycle_count: Number of refactor cycles executed
        final_score: Final LENS score achieved
        baseline_score: Initial LENS score
        tests_pass: True if all tests still pass
        files_refactored: Total files refactored across all cycles
        audit_trail: Audit events for governance
        error_message: Error message if failed (optional)
    """
    converged: bool
    cycle_count: int
    final_score: float
    baseline_score: float
    tests_pass: bool
    files_refactored: int = 0
    audit_trail: List[Dict[str, Any]] = field(default_factory=list)
    error_message: Optional[str] = None


class HolisticRefactoringSweep:
    """
    Auto-injected holistic refactoring sweep workflow epilogue.
    
    Features:
    - Aggregates ALL files modified during workflow
    - LENS baseline score measurement
    - Convergence loop (refactor until baseline + margin met)
    - Ensures holistic coherence across multi-phase work
    - No regressions (all tests must pass after refactoring)
    
    Usage:
        sweep = HolisticRefactoringSweep(
            workflow_id="workflow-test",
            lens_analyzer=lens,
            refactoring_orchestrator=orchestrator,
            max_cycles=5
        )
        result = sweep.execute(
            modified_files=[...],
            target_score_threshold=80.0
        )
    """
    
    def __init__(
        self,
        workflow_id: str,
        lens_analyzer: Any,
        refactoring_orchestrator: Any,
        max_cycles: int = 5
    ) -> None:
        """
        Initialize HolisticRefactoringSweep.
        
        Args:
            workflow_id: Workflow identifier
            lens_analyzer: LENS analyzer instance
            refactoring_orchestrator: RefactoringOrchestrator instance
            max_cycles: Maximum convergence loop iterations
        """
        self.workflow_id = workflow_id
        self.lens_analyzer = lens_analyzer
        self.refactoring_orchestrator = refactoring_orchestrator
        self.max_cycles = max_cycles
        self.state = SweepState.PENDING
        self.audit_trail: List[Dict[str, Any]] = []
    
    def collect_all_modified_files(
        self,
        workflow_execution: Dict[str, Any]
    ) -> List[Path]:
        """
        Collect ALL files modified during workflow (all phases).
        
        Aggregates modified files from ALL phases into single list.
        
        Args:
            workflow_execution: Workflow execution metadata with phase info
        
        Returns:
            List of all modified files (deduplicated)
        """
        self.state = SweepState.COLLECTING
        
        all_files = set()
        for phase in workflow_execution.get("phases", []):
            for file in phase.get("modified_files", []):
                all_files.add(Path(file))
        
        files_list = list(all_files)
        
        # Log to audit trail
        self._log_event(
            action="collect_all_modified_files",
            files_count=len(files_list)
        )
        
        return files_list
    
    def measure_baseline_score(
        self,
        files: List[Path]
    ) -> LENSScoreSnapshot:
        """
        Measure LENS baseline score before refactoring.
        
        Args:
            files: Files to measure
        
        Returns:
            LENS score snapshot for baseline comparison
        """
        self.state = SweepState.MEASURING
        
        # LENS scoring
        scores = self.lens_analyzer.score_files(files)
        
        snapshot = LENSScoreSnapshot(
            overall_score=scores["overall_score"],
            maintainability=scores.get("maintainability", 0),
            complexity=scores.get("complexity", 0),
            duplication=scores.get("duplication", 0),
            timestamp=time.time()
        )
        
        # Log to audit trail
        self._log_event(
            action="measure_baseline_score",
            overall_score=snapshot.overall_score,
            maintainability=snapshot.maintainability,
            complexity=snapshot.complexity,
            duplication=snapshot.duplication
        )
        
        return snapshot
    
    def execute_refactoring(
        self,
        files: List[Path]
    ) -> RefactoringResult:
        """
        Execute refactoring via RefactoringOrchestrator.
        
        Delegates to RefactoringOrchestrator.refactor_files() for actual refactoring.
        
        Args:
            files: Files to refactor
        
        Returns:
            RefactoringResult with details of refactoring performed
        """
        self.state = SweepState.REFACTORING
        
        # Delegate to RefactoringOrchestrator
        raw_result = self.refactoring_orchestrator.refactor_files(
            files=files,
            holistic_mode=True  # Multi-file coherence mode
        )
        
        result = RefactoringResult(
            files_refactored=raw_result["files_refactored"],
            patterns_applied=raw_result["patterns_applied"],
            tests_pass=raw_result["tests_pass"]
        )
        
        # Log to audit trail
        self._log_event(
            action="execute_refactoring",
            files_refactored=result.files_refactored,
            patterns_applied=result.patterns_applied,
            tests_pass=result.tests_pass
        )
        
        return result
    
    def execute(
        self,
        modified_files: List[Path],
        target_score_threshold: float = 80.0
    ) -> SweepResult:
        """
        Execute convergence-gated holistic refactoring sweep.
        
        Convergence loop:
        1. Measure baseline LENS score
        2. Measure current score
        3. If score >= threshold → CONVERGED (exit)
        4. If score < threshold → refactor files
        5. Increment cycle counter
        6. If cycle < max_cycles → repeat from step 2
        7. If cycle >= max_cycles → FAILED
        
        Args:
            modified_files: Files modified during workflow
            target_score_threshold: Target LENS score to achieve
        
        Returns:
            SweepResult with convergence status
        """
        # Step 1: Measure baseline
        baseline_snapshot = self.measure_baseline_score(modified_files)
        baseline_score = baseline_snapshot.overall_score
        
        cycle_count = 0
        total_files_refactored = 0
        
        while cycle_count < self.max_cycles:
            cycle_count += 1
            self._current_cycle = cycle_count  # Track for audit logging
            
            # Step 2: Measure current score
            current_snapshot = self.measure_baseline_score(modified_files)
            current_score = current_snapshot.overall_score
            
            # Step 3: Check convergence
            if current_score >= target_score_threshold:
                # CONVERGED: Score meets threshold
                self.state = SweepState.CONVERGED
                return SweepResult(
                    converged=True,
                    cycle_count=cycle_count,
                    final_score=current_score,
                    baseline_score=baseline_score,
                    tests_pass=True,
                    files_refactored=total_files_refactored,
                    audit_trail=self.audit_trail
                )
            
            # Step 4: Refactor files
            refactor_result = self.execute_refactoring(modified_files)
            total_files_refactored += refactor_result.files_refactored
            
            # Check tests still pass
            if not refactor_result.tests_pass:
                # FAILED: Refactoring introduced regressions
                self.state = SweepState.FAILED
                return SweepResult(
                    converged=False,
                    cycle_count=cycle_count,
                    final_score=current_score,
                    baseline_score=baseline_score,
                    tests_pass=False,
                    files_refactored=total_files_refactored,
                    audit_trail=self.audit_trail,
                    error_message="Refactoring introduced test failures"
                )
            
            # Log cycle completion
            self._log_event(
                action="cycle_complete",
                cycle=cycle_count,
                current_score=current_score,
                target_score=target_score_threshold,
                files_refactored=refactor_result.files_refactored
            )
        
        # FAILED: Max cycles exceeded
        self.state = SweepState.FAILED
        final_snapshot = self.measure_baseline_score(modified_files)
        
        return SweepResult(
            converged=False,
            cycle_count=cycle_count,
            final_score=final_snapshot.overall_score,
            baseline_score=baseline_score,
            tests_pass=True,  # Tests pass, but score not met
            files_refactored=total_files_refactored,
            audit_trail=self.audit_trail,
            error_message=f"max_cycles exceeded ({self.max_cycles}), final score {final_snapshot.overall_score:.1f} < target {target_score_threshold:.1f}"
        )
    
    def _log_event(self, action: str, **kwargs: Any) -> None:
        """
        Log event to audit trail.
        
        Args:
            action: Event action name
            **kwargs: Additional event data
        """
        event = {
            "timestamp": time.time(),
            "workflow_id": self.workflow_id,
            "action": action,
            "state": self.state.value,
            "cycle": getattr(self, '_current_cycle', 0),
            **kwargs
        }
        self.audit_trail.append(event)


# AC_COMPLETE: AC-PHASE100-S8-002 ✅ Implementation complete
