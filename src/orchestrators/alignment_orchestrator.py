"""
Alignment orchestrator - integrates all Phase 4 components
Runs validation → diagnostics → auto-repair → health monitoring

Part of Phase 4: Alignment Orchestrator
"""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional, List, Dict, Any
import logging

from src.validators.setup_validator import SetupValidator, ValidationResult
from src.diagnostics.environment_diagnostics import EnvironmentDiagnostics, DiagnosticResult
from src.utils.config_repair import ConfigRepair, RepairResult
from src.monitoring.system_health_monitor import SystemHealthMonitor, HealthScore
from src.orchestrators.git_checkpoint_orchestrator import GitCheckpointOrchestrator
from src.orchestrators.planning_orchestrator import PlanningOrchestrator

logger = logging.getLogger(__name__)


class AlignmentStatus(Enum):
    """Status of alignment operation"""
    ALIGNED = "aligned"      # System was already aligned
    REPAIRED = "repaired"    # System required repairs
    FAILED = "failed"        # Alignment failed


@dataclass
class AlignmentResult:
    """Result of alignment operation"""
    status: AlignmentStatus
    validation_result: ValidationResult
    diagnostic_results: list
    health_score: HealthScore
    repair_attempted: bool
    repair_result: Optional[RepairResult] = None
    message: str = ""
    orchestrator_wiring_validated: bool = False
    wiring_issues: List[str] = None
    
    def __post_init__(self):
        """Initialize mutable defaults"""
        if self.wiring_issues is None:
            self.wiring_issues = []


class AlignmentOrchestrator:
    """
    Alignment orchestrator integrating all Phase 4 components
    
    Workflow:
    1. Run validation checks
    2. Run environment diagnostics
    3. Auto-repair if issues found (optional)
    4. Calculate health score
    5. Generate comprehensive report
    """
    
    def __init__(self, root_path: Path, auto_repair: bool = True):
        """
        Initialize alignment orchestrator
        
        Args:
            root_path: Path to CORTEX root
            auto_repair: Whether to auto-repair issues
        """
        self.root_path = Path(root_path)
        self.auto_repair = auto_repair
        
        # Initialize components
        self.validator = SetupValidator(root_path=self.root_path)
        self.diagnostics = EnvironmentDiagnostics(root_path=self.root_path)
        self.repair = ConfigRepair(root_path=self.root_path)
        self.health_monitor = SystemHealthMonitor(root_path=self.root_path)
        
        # Initialize orchestrator wiring validation components
        self.git_checkpoint = GitCheckpointOrchestrator(project_root=self.root_path)
        self.planning_orchestrator = None  # Lazy init to avoid circular dependencies
    
    def run_alignment(self) -> AlignmentResult:
        """
        Run complete alignment workflow
        
        Returns:
            AlignmentResult with all component results
        """
        # Step 1: Validation
        validation_result = self.validator.validate_all()
        
        # Step 2: Diagnostics
        diagnostic_results = self.diagnostics.run_all()
        
        # Step 3: Validate orchestrator wiring (ENFORCED)
        wiring_validated, wiring_issues = self._validate_orchestrator_wiring()
        
        # Step 4: Auto-repair if needed
        repair_attempted = False
        repair_result = None
        
        if self.auto_repair and not validation_result.is_valid:
            repair_attempted = True
            repair_result = self.repair.repair_all()
            
            # Re-validate after repair
            validation_result = self.validator.validate_all()
        
        # Step 5: Health score
        health_score = self.health_monitor.calculate_health_score()
        
        # Determine overall status (WIRING VALIDATION MANDATORY)
        if not wiring_validated:
            status = AlignmentStatus.FAILED
            message = f"Orchestrator wiring validation failed: {', '.join(wiring_issues)}"
        elif validation_result.is_valid and health_score.overall_score >= 80:
            status = AlignmentStatus.ALIGNED
            message = "System is aligned and healthy"
        elif repair_attempted and validation_result.is_valid:
            status = AlignmentStatus.REPAIRED
            message = "System repaired and now aligned"
        else:
            status = AlignmentStatus.FAILED
            message = "System has issues that could not be auto-repaired"
        
        return AlignmentResult(
            status=status,
            validation_result=validation_result,
            diagnostic_results=diagnostic_results,
            health_score=health_score,
            repair_attempted=repair_attempted,
            repair_result=repair_result,
            message=message,
            orchestrator_wiring_validated=wiring_validated,
            wiring_issues=wiring_issues
        )
    
    def generate_report(self, result: AlignmentResult) -> str:
        """
        Generate comprehensive alignment report
        
        Args:
            result: AlignmentResult to report
            
        Returns:
            Formatted report string
        """
        lines = []
        lines.append("=" * 70)
        lines.append("CORTEX SYSTEM ALIGNMENT REPORT")
        lines.append("=" * 70)
        lines.append("")
        lines.append(f"Status: {result.status.value.upper()}")
        lines.append(f"Message: {result.message}")
        lines.append("")
        
        # Health Score
        lines.append(f"Overall Health: {result.health_score.overall_score}/100 ({result.health_score.status.value})")
        lines.append(f"  Validation: {result.health_score.validation_score}/100")
        lines.append(f"  Diagnostics: {result.health_score.diagnostic_score}/100")
        lines.append("")
        
        # Validation
        lines.append(f"Validation: {'✅ PASSED' if result.validation_result.is_valid else '❌ FAILED'}")
        if result.validation_result.issues:
            lines.append(f"  Issues found: {len(result.validation_result.issues)}")
        lines.append("")
        
        # Diagnostics
        lines.append(f"Diagnostics: {len(result.diagnostic_results)} checks completed")
        lines.append("")
        
        # Repair
        if result.repair_attempted:
            lines.append(f"Auto-Repair: Attempted")
            if result.repair_result:
                lines.append(f"  Actions taken: {len(result.repair_result.actions)}")
        else:
            lines.append(f"Auto-Repair: Not needed")
        
        lines.append("")
        
        # Orchestrator Wiring
        lines.append(f"Orchestrator Wiring: {'✅ VALIDATED' if result.orchestrator_wiring_validated else '❌ FAILED'}")
        if result.wiring_issues:
            lines.append(f"  Issues found: {len(result.wiring_issues)}")
            for issue in result.wiring_issues:
                lines.append(f"    - {issue}")
        lines.append("")
        lines.append("=" * 70)
        
        return "\n".join(lines)
    
    def _validate_orchestrator_wiring(self) -> tuple[bool, List[str]]:
        """
        Validate that orchestrators are properly wired for git checkpoints.
        
        This enforces SKULL rule GIT_CHECKPOINT_ENFORCEMENT by validating:
        1. GitCheckpointOrchestrator has create_auto_checkpoint method
        2. PlanningOrchestrator initializes GitCheckpointOrchestrator
        3. PlanningOrchestrator calls git checkpoints after each phase
        
        Returns:
            Tuple of (is_valid, issues_list)
        """
        issues = []
        
        # Validation 1: GitCheckpointOrchestrator has create_auto_checkpoint
        if not hasattr(self.git_checkpoint, 'create_auto_checkpoint'):
            issues.append("GitCheckpointOrchestrator missing create_auto_checkpoint method")
        else:
            if not callable(getattr(self.git_checkpoint, 'create_auto_checkpoint')):
                issues.append("GitCheckpointOrchestrator.create_auto_checkpoint is not callable")
        
        # Validation 2: Test that create_auto_checkpoint has correct signature
        try:
            import inspect
            sig = inspect.signature(self.git_checkpoint.create_auto_checkpoint)
            required_params = ['operation', 'message']
            params = list(sig.parameters.keys())
            
            for req_param in required_params:
                if req_param not in params:
                    issues.append(f"create_auto_checkpoint missing required parameter: {req_param}")
        except Exception as e:
            issues.append(f"Failed to validate create_auto_checkpoint signature: {e}")
        
        # Validation 3: PlanningOrchestrator exists and has git_checkpoint
        try:
            # Lazy init to avoid circular dependencies
            if self.planning_orchestrator is None:
                self.planning_orchestrator = PlanningOrchestrator(str(self.root_path))
            
            if not hasattr(self.planning_orchestrator, 'git_checkpoint'):
                issues.append("PlanningOrchestrator missing git_checkpoint attribute")
            else:
                # Verify it's a GitCheckpointOrchestrator instance
                if not isinstance(self.planning_orchestrator.git_checkpoint, GitCheckpointOrchestrator):
                    issues.append("PlanningOrchestrator.git_checkpoint is not a GitCheckpointOrchestrator instance")
        except Exception as e:
            issues.append(f"Failed to validate PlanningOrchestrator: {e}")
        
        # Validation 4: Check that generate_incremental_plan calls git checkpoints
        try:
            import inspect
            source = inspect.getsource(self.planning_orchestrator.generate_incremental_plan)
            
            # Look for git checkpoint calls after each phase
            phase_checkpoints = [
                'plan-phase-1',
                'plan-phase-2', 
                'plan-phase-3'
            ]
            
            for phase in phase_checkpoints:
                if phase not in source:
                    issues.append(f"PlanningOrchestrator.generate_incremental_plan missing git checkpoint for {phase}")
            
            # Verify create_auto_checkpoint is called
            if 'create_auto_checkpoint' not in source:
                issues.append("PlanningOrchestrator.generate_incremental_plan does not call create_auto_checkpoint")
                
        except Exception as e:
            logger.warning(f"Could not validate planning orchestrator source code: {e}")
            # This is a warning, not a blocker
        
        is_valid = len(issues) == 0
        
        if is_valid:
            logger.info("✅ Orchestrator wiring validation passed")
        else:
            logger.error(f"❌ Orchestrator wiring validation failed: {len(issues)} issues found")
            for issue in issues:
                logger.error(f"  - {issue}")
        
        return is_valid, issues
