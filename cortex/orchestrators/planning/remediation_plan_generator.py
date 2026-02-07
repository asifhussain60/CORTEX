"""
AC-ENH-059-002: RemediationPlanGenerator - Implementation

Generates structured remediation plans from audit findings.
Implements ENH-059: Audit-Driven Auto-Planning specification.

Authority: ENH-059 (P1, 8.5 confidence)
"""

from typing import List, Dict, Any
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class AuditFinding:
    """Single audit finding."""
    severity: str  # P0, P1, P2
    category: str
    description: str
    files_affected: List[str]
    estimated_effort_minutes: int


@dataclass
class RemediationPhase:
    """Single remediation phase."""
    phase_id: str
    name: str
    description: str
    estimated_minutes: int
    risk_level: str  # LOW, MEDIUM, HIGH
    dependencies: List[str] = field(default_factory=list)
    test_requirements: List[str] = field(default_factory=list)
    files_to_modify: List[str] = field(default_factory=list)


@dataclass
class RemediationPlan:
    """Complete remediation plan."""
    phases: List[RemediationPhase]
    total_effort_minutes: int
    overall_risk: str
    execution_options: List[Dict[str, Any]] = field(default_factory=list)


# ============================================================================
# REMEDIATION PLAN GENERATOR
# ============================================================================

class RemediationPlanGenerator:
    """
    Generates structured remediation plans from audit findings.
    
    Features:
    - Groups findings into logical phases
    - Calculates dependencies between phases
    - Assesses risk per phase
    - Estimates effort
    - Generates 4 execution options
    """
    
    def __init__(self):
        """Initialize generator."""
        logger.info("RemediationPlanGenerator initialized")
    
    def generate_plan(self, findings: List[AuditFinding]) -> RemediationPlan:
        """
        Generate remediation plan from audit findings.
        
        Args:
            findings: List of audit findings
            
        Returns:
            RemediationPlan with phases and execution options
        """
        if not findings:
            return RemediationPlan(
                phases=[],
                total_effort_minutes=0,
                overall_risk="LOW",
                execution_options=self._generate_execution_options()
            )
        
        # Group findings by severity and category
        phases = self._group_findings_into_phases(findings)
        
        # Calculate dependencies
        phases = self._calculate_dependencies(phases)
        
        # Assess risk per phase
        for phase in phases:
            phase.risk_level = self._assess_risk(phase)
        
        # Calculate total effort
        total_effort = sum(phase.estimated_minutes for phase in phases)
        
        # Assess overall risk
        overall_risk = self._assess_overall_risk(phases)
        
        plan = RemediationPlan(
            phases=phases,
            total_effort_minutes=total_effort,
            overall_risk=overall_risk,
            execution_options=self._generate_execution_options()
        )
        
        logger.info(f"Generated plan with {len(phases)} phases, {total_effort}min effort")
        
        return plan
    
    def _group_findings_into_phases(
        self,
        findings: List[AuditFinding]
    ) -> List[RemediationPhase]:
        """Group findings into logical phases."""
        phases = []
        
        # Phase 1: P0 Critical Fixes
        p0_findings = [f for f in findings if f.severity == "P0"]
        if p0_findings:
            phase1 = RemediationPhase(
                phase_id="PHASE-1",
                name="Critical Fixes",
                description="Fix critical P0 issues blocking operation",
                estimated_minutes=sum(f.estimated_effort_minutes for f in p0_findings),
                risk_level="LOW",  # Will be assessed
                dependencies=[],
                test_requirements=[
                    "Unit tests for all fixes",
                    "Integration tests pass",
                    "No regressions introduced"
                ],
                files_to_modify=self._deduplicate_files(
                    [f for finding in p0_findings for f in finding.files_affected]
                )
            )
            phases.append(phase1)
        
        # Phase 2+: P1/P2 Improvements
        p1_findings = [f for f in findings if f.severity == "P1"]
        if p1_findings:
            # Group P1 by category
            p1_by_category = self._group_by_category(p1_findings)
            
            for idx, (category, category_findings) in enumerate(p1_by_category.items(), start=2):
                phase = RemediationPhase(
                    phase_id=f"PHASE-{idx}",
                    name=category,
                    description=f"Address {category.lower()} issues",
                    estimated_minutes=sum(
                        f.estimated_effort_minutes for f in category_findings
                    ),
                    risk_level="MEDIUM",  # Will be assessed
                    dependencies=[],  # Will be calculated
                    test_requirements=[
                        f"{category} validation tests",
                        "Integration with Phase 1",
                        "End-to-end verification"
                    ],
                    files_to_modify=self._deduplicate_files(
                        [f for finding in category_findings for f in finding.files_affected]
                    )
                )
                phases.append(phase)
        
        return phases
    
    def _calculate_dependencies(
        self,
        phases: List[RemediationPhase]
    ) -> List[RemediationPhase]:
        """Calculate dependencies between phases."""
        if len(phases) <= 1:
            return phases
        
        # Phase 1 has no dependencies
        # All other phases depend on Phase 1 (foundation)
        for phase in phases[1:]:
            phase.dependencies.append(phases[0].phase_id)
        
        return phases
    
    def _assess_risk(self, phase: RemediationPhase) -> str:
        """Assess risk level for a phase."""
        # P0 critical fixes are typically LOW risk (simple, focused)
        if phase.phase_id == "PHASE-1":
            return "LOW"
        
        # Risk based on number of files and estimated time
        file_count = len(phase.files_to_modify)
        
        if file_count <= 2 and phase.estimated_minutes <= 30:
            return "LOW"
        elif file_count <= 5 and phase.estimated_minutes <= 60:
            return "MEDIUM"
        else:
            return "HIGH"
    
    def _assess_overall_risk(self, phases: List[RemediationPhase]) -> str:
        """Assess overall plan risk."""
        if not phases:
            return "LOW"
        
        risk_scores = {"LOW": 1, "MEDIUM": 2, "HIGH": 3}
        max_risk = max(risk_scores.get(p.risk_level, 1) for p in phases)
        
        if max_risk == 1:
            return "LOW"
        elif max_risk == 2:
            return "LOW-MEDIUM"
        else:
            return "MEDIUM-HIGH"
    
    def _generate_execution_options(self) -> List[Dict[str, Any]]:
        """Generate 4 execution options."""
        return [
            {
                "number": 1,
                "name": "Auto-execute all phases",
                "description": "Complete all phases automatically with test gating",
                "benefits": [
                    "Auto-commit after each successful phase",
                    "Emergency stop on failures",
                    "Fastest completion time"
                ],
                "autonomous": True
            },
            {
                "number": 2,
                "name": "Execute phase-by-phase",
                "description": "Review and approve each phase individually",
                "benefits": [
                    "Manual commit control",
                    "Maximum control and visibility",
                    "Review before proceeding"
                ],
                "default": True,
                "autonomous": False
            },
            {
                "number": 3,
                "name": "Review plan only",
                "description": "Save plan to markdown file without execution",
                "benefits": [
                    "Good for planning sessions",
                    "Share with team",
                    "Execute later"
                ],
                "autonomous": False
            },
            {
                "number": 4,
                "name": "Cancel",
                "description": "Exit without changes or plan file",
                "benefits": [],
                "autonomous": False
            }
        ]
    
    def calculate_dependencies(self, phases: List[RemediationPhase]) -> List[RemediationPhase]:
        """Public method to calculate dependencies."""
        return self._calculate_dependencies(phases)
    
    def assess_risk(self, phase: RemediationPhase) -> str:
        """Public method to assess risk."""
        return self._assess_risk(phase)
    
    def _deduplicate_files(self, files: List[str]) -> List[str]:
        """Remove duplicate file paths."""
        return list(dict.fromkeys(files))  # Preserves order
    
    def _group_by_category(
        self,
        findings: List[AuditFinding]
    ) -> Dict[str, List[AuditFinding]]:
        """Group findings by category."""
        grouped: Dict[str, List[AuditFinding]] = {}
        for finding in findings:
            if finding.category not in grouped:
                grouped[finding.category] = []
            grouped[finding.category].append(finding)
        return grouped
