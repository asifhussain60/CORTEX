"""
Alignment orchestrator - integrates all Phase 4 components
Runs validation → diagnostics → auto-repair → health monitoring

Part of Phase 4: Alignment Orchestrator
"""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional

from src.validators.setup_validator import SetupValidator, ValidationResult
from src.diagnostics.environment_diagnostics import EnvironmentDiagnostics, DiagnosticResult
from src.utils.config_repair import ConfigRepair, RepairResult
from src.monitoring.system_health_monitor import SystemHealthMonitor, HealthScore


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
        
        # Step 3: Auto-repair if needed
        repair_attempted = False
        repair_result = None
        
        if self.auto_repair and not validation_result.is_valid:
            repair_attempted = True
            repair_result = self.repair.repair_all()
            
            # Re-validate after repair
            validation_result = self.validator.validate_all()
        
        # Step 4: Health score
        health_score = self.health_monitor.calculate_health_score()
        
        # Determine overall status
        if validation_result.is_valid and health_score.overall_score >= 80:
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
            message=message
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
        lines.append("=" * 70)
        
        return "\n".join(lines)
