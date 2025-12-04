"""
System health monitoring with scoring
Aggregates validation, diagnostics, repair into unified health score

Part of Phase 4: Alignment Orchestrator
"""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional

from src.validators.setup_validator import SetupValidator, IssueSeverity
from src.diagnostics.environment_diagnostics import EnvironmentDiagnostics, DiagnosticStatus


class HealthStatus(Enum):
    """Overall health status"""
    HEALTHY = "healthy"      # Score >= 80
    DEGRADED = "degraded"    # Score 50-79
    CRITICAL = "critical"    # Score < 50


@dataclass
class HealthScore:
    """System health score"""
    overall_score: int  # 0-100
    validation_score: int
    diagnostic_score: int
    status: HealthStatus
    message: str


class SystemHealthMonitor:
    """
    System health monitoring with scoring
    
    Combines validation and diagnostics into unified health score
    """
    
    def __init__(self, root_path: Path):
        """
        Initialize health monitor
        
        Args:
            root_path: Path to CORTEX root
        """
        self.root_path = Path(root_path)
        self.validator = SetupValidator(root_path=self.root_path)
        self.diagnostics = EnvironmentDiagnostics(root_path=self.root_path)
    
    def calculate_health_score(self) -> HealthScore:
        """
        Calculate overall system health score
        
        Returns:
            HealthScore with component scores
        """
        # Run validation
        validation_result = self.validator.validate_all()
        validation_score = self._score_validation(validation_result)
        
        # Run diagnostics
        diagnostic_results = self.diagnostics.run_all()
        diagnostic_score = self._score_diagnostics(diagnostic_results)
        
        # Calculate overall (weighted average)
        overall = int((validation_score * 0.6) + (diagnostic_score * 0.4))
        
        # Determine status
        if overall >= 80:
            status = HealthStatus.HEALTHY
            message = "System is healthy"
        elif overall >= 50:
            status = HealthStatus.DEGRADED
            message = "System has issues but functional"
        else:
            status = HealthStatus.CRITICAL
            message = "System has critical issues"
        
        return HealthScore(
            overall_score=overall,
            validation_score=validation_score,
            diagnostic_score=diagnostic_score,
            status=status,
            message=message
        )
    
    def _score_validation(self, result) -> int:
        """Score validation result (0-100)"""
        if result.is_valid:
            return 100
        
        # Deduct points for issues
        score = 100
        for issue in result.issues:
            if issue.severity == IssueSeverity.CRITICAL:
                score -= 30
            elif issue.severity == IssueSeverity.ERROR:
                score -= 15
            elif issue.severity == IssueSeverity.WARNING:
                score -= 5
        
        return max(0, score)
    
    def _score_diagnostics(self, results) -> int:
        """Score diagnostic results (0-100)"""
        if not results:
            return 50  # Unknown
        
        score = 100
        for result in results:
            if result.status == DiagnosticStatus.CRITICAL:
                score -= 20
            elif result.status == DiagnosticStatus.WARNING:
                score -= 10
        
        return max(0, score)
    
    def generate_report(self, score: HealthScore) -> str:
        """
        Generate health report
        
        Args:
            score: HealthScore to report
            
        Returns:
            Formatted report string
        """
        lines = []
        lines.append("=" * 70)
        lines.append("CORTEX SYSTEM HEALTH REPORT")
        lines.append("=" * 70)
        lines.append("")
        lines.append(f"Overall Score: {score.overall_score}/100")
        lines.append(f"Status: {score.status.value.upper()}")
        lines.append(f"Message: {score.message}")
        lines.append("")
        lines.append(f"Component Scores:")
        lines.append(f"  Validation: {score.validation_score}/100")
        lines.append(f"  Diagnostics: {score.diagnostic_score}/100")
        lines.append("")
        lines.append("=" * 70)
        
        return "\n".join(lines)
