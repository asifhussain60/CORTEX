"""
Manifest Compliance Validator - Planning System 4.0 Manifest Validation

Purpose: Validates planning-system-4.0-manifest.yaml compliance including
DoR/DoD requirements, phase structure, task format, and acceptance criteria.

Version: 1.0.0
Author: CORTEX Development Team
Created: 2025-12-24 (Week 9 Day 2)

Responsibilities:
- YAML schema validation against manifest structure
- Definition of Ready (DoR) compliance checking
- Definition of Done (DoD) compliance checking
- Phase structure and task format validation
- Acceptance criteria completeness validation
- TDD requirement enforcement

Integration Points:
- Planning System: Ensures manifest compliance
- validation_framework_adapter.py: Extends with manifest-specific rules
- Brain Protection (Tier 0): Enforces DoR/DoD governance
- TDD Intelligence: Validates TDD requirements in manifest

Week 9 Target: 300 LOC
"""

import logging
import yaml
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
from enum import Enum

logger = logging.getLogger(__name__)


class ComplianceLevel(Enum):
    """Manifest compliance levels."""
    FULL = "full"  # 100% compliant
    PARTIAL = "partial"  # Some requirements met
    NON_COMPLIANT = "non_compliant"  # Major violations


class ManifestSection(Enum):
    """Manifest sections to validate."""
    METADATA = "metadata"
    DEFINITION_OF_READY = "definition_of_ready"
    DEFINITION_OF_DONE = "definition_of_done"
    PHASES = "phases"
    TDD_REQUIREMENTS = "tdd_requirements"
    ACCEPTANCE_CRITERIA = "acceptance_criteria"


@dataclass
class ComplianceViolation:
    """Single compliance violation."""
    section: ManifestSection
    requirement: str
    severity: str  # "critical", "major", "minor"
    message: str
    suggestion: Optional[str] = None
    
    def is_critical(self) -> bool:
        """Check if violation is critical."""
        return self.severity == "critical"


@dataclass
class ComplianceReport:
    """Complete manifest compliance report."""
    compliance_level: ComplianceLevel
    violations: List[ComplianceViolation] = field(default_factory=list)
    
    critical_violations: int = 0
    major_violations: int = 0
    minor_violations: int = 0
    
    dor_compliance: float = 0.0  # 0-100%
    dod_compliance: float = 0.0  # 0-100%
    overall_score: float = 0.0  # 0-100%
    
    def add_violation(self, violation: ComplianceViolation):
        """Add violation and update counters."""
        self.violations.append(violation)
        
        if violation.severity == "critical":
            self.critical_violations += 1
        elif violation.severity == "major":
            self.major_violations += 1
        elif violation.severity == "minor":
            self.minor_violations += 1
        
        self._recalculate_compliance()
    
    def _recalculate_compliance(self):
        """Recalculate compliance level and scores."""
        # Calculate overall score
        total_violations = len(self.violations)
        if total_violations == 0:
            self.compliance_level = ComplianceLevel.FULL
            self.overall_score = 100.0
        elif self.critical_violations > 0:
            self.compliance_level = ComplianceLevel.NON_COMPLIANT
            self.overall_score = max(0.0, 50.0 - (self.critical_violations * 10))
        else:
            self.compliance_level = ComplianceLevel.PARTIAL
            penalty = (self.major_violations * 5) + (self.minor_violations * 2)
            self.overall_score = max(0.0, 100.0 - penalty)
    
    def get_critical_violations(self) -> List[ComplianceViolation]:
        """Get critical violations."""
        return [v for v in self.violations if v.is_critical()]
    
    def get_summary(self) -> str:
        """Get human-readable summary."""
        if self.compliance_level == ComplianceLevel.FULL:
            return f"✅ Fully compliant (Score: {self.overall_score:.1f}%)"
        elif self.compliance_level == ComplianceLevel.PARTIAL:
            return f"⚠️ Partially compliant (Score: {self.overall_score:.1f}%, {self.major_violations} major, {self.minor_violations} minor)"
        else:
            return f"❌ Non-compliant (Score: {self.overall_score:.1f}%, {self.critical_violations} critical violations)"


class ManifestComplianceValidator:
    """
    Validates Planning System 4.0 manifest compliance.
    
    Ensures plans adhere to manifest structure including DoR/DoD,
    phase structure, task format, and TDD requirements.
    
    Usage:
        validator = ManifestComplianceValidator(manifest_path="planning-system-4.0-manifest.yaml")
        report = validator.validate_plan_compliance(plan_data)
        
        if report.compliance_level == ComplianceLevel.FULL:
            # Proceed with plan
        else:
            # Handle violations
            for violation in report.get_critical_violations():
                print(f"Critical: {violation.message}")
    """
    
    def __init__(self, manifest_path: Optional[Path] = None):
        """
        Initialize manifest compliance validator.
        
        Args:
            manifest_path: Path to planning-system-4.0-manifest.yaml
        """
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Load manifest
        if manifest_path is None:
            # Default path relative to CORTEX root
            manifest_path = Path(__file__).parent.parent.parent.parent.parent / "cortex-brain" / "admin" / "manifests" / "planning-system-4.0-manifest.yaml"
        
        self.manifest_path = manifest_path
        self.manifest = self._load_manifest()
        
        # Extract requirements
        self.dor_requirements = self._extract_dor_requirements()
        self.dod_requirements = self._extract_dod_requirements()
        self.tdd_requirements = self._extract_tdd_requirements()
    
    # ========== Main Validation Entry Point ==========
    
    def validate_plan_compliance(self, plan_data: Dict[str, Any]) -> ComplianceReport:
        """
        Validate plan against manifest compliance.
        
        Args:
            plan_data: Plan data to validate
            
        Returns:
            Complete compliance report
        """
        self.logger.info("Starting manifest compliance validation")
        
        report = ComplianceReport(compliance_level=ComplianceLevel.FULL)
        
        # Validate metadata
        metadata_violations = self._validate_metadata_compliance(plan_data)
        for violation in metadata_violations:
            report.add_violation(violation)
        
        # Validate DoR
        dor_violations = self._validate_dor_compliance(plan_data)
        for violation in dor_violations:
            report.add_violation(violation)
        report.dor_compliance = self._calculate_dor_score(plan_data)
        
        # Validate DoD
        dod_violations = self._validate_dod_compliance(plan_data)
        for violation in dod_violations:
            report.add_violation(violation)
        report.dod_compliance = self._calculate_dod_score(plan_data)
        
        # Validate phases
        phase_violations = self._validate_phase_structure(plan_data)
        for violation in phase_violations:
            report.add_violation(violation)
        
        # Validate TDD requirements
        tdd_violations = self._validate_tdd_requirements(plan_data)
        for violation in tdd_violations:
            report.add_violation(violation)
        
        self.logger.info(f"Compliance validation complete: {report.get_summary()}")
        return report
    
    # ========== DoR Validation ==========
    
    def _validate_dor_compliance(self, plan_data: Dict[str, Any]) -> List[ComplianceViolation]:
        """Validate Definition of Ready compliance."""
        violations = []
        
        # Check if DoR section exists
        if "definition_of_ready" not in plan_data:
            violations.append(ComplianceViolation(
                section=ManifestSection.DEFINITION_OF_READY,
                requirement="DoR section presence",
                severity="critical",
                message="Missing 'definition_of_ready' section",
                suggestion="Add DoR section per manifest requirements"
            ))
            return violations
        
        dor = plan_data["definition_of_ready"]
        
        # Validate each DoR requirement
        for requirement in self.dor_requirements:
            req_key = requirement["key"]
            req_name = requirement["name"]
            
            if req_key not in dor:
                violations.append(ComplianceViolation(
                    section=ManifestSection.DEFINITION_OF_READY,
                    requirement=req_name,
                    severity="major",
                    message=f"Missing DoR requirement: {req_name}",
                    suggestion=f"Add '{req_key}' to definition_of_ready"
                ))
            elif not dor[req_key]:
                violations.append(ComplianceViolation(
                    section=ManifestSection.DEFINITION_OF_READY,
                    requirement=req_name,
                    severity="major",
                    message=f"Empty DoR requirement: {req_name}",
                    suggestion=f"Provide details for '{req_key}'"
                ))
        
        return violations
    
    def _calculate_dor_score(self, plan_data: Dict[str, Any]) -> float:
        """Calculate DoR compliance score (0-100)."""
        if "definition_of_ready" not in plan_data:
            return 0.0
        
        dor = plan_data["definition_of_ready"]
        total_requirements = len(self.dor_requirements)
        met_requirements = 0
        
        for requirement in self.dor_requirements:
            req_key = requirement["key"]
            if req_key in dor and dor[req_key]:
                met_requirements += 1
        
        return (met_requirements / total_requirements * 100) if total_requirements > 0 else 0.0
    
    # ========== DoD Validation ==========
    
    def _validate_dod_compliance(self, plan_data: Dict[str, Any]) -> List[ComplianceViolation]:
        """Validate Definition of Done compliance."""
        violations = []
        
        # Check if DoD section exists
        if "definition_of_done" not in plan_data:
            violations.append(ComplianceViolation(
                section=ManifestSection.DEFINITION_OF_DONE,
                requirement="DoD section presence",
                severity="critical",
                message="Missing 'definition_of_done' section",
                suggestion="Add DoD section per manifest requirements"
            ))
            return violations
        
        dod = plan_data["definition_of_done"]
        
        # Validate each DoD requirement
        for requirement in self.dod_requirements:
            req_key = requirement["key"]
            req_name = requirement["name"]
            
            if req_key not in dod:
                violations.append(ComplianceViolation(
                    section=ManifestSection.DEFINITION_OF_DONE,
                    requirement=req_name,
                    severity="major",
                    message=f"Missing DoD requirement: {req_name}",
                    suggestion=f"Add '{req_key}' to definition_of_done"
                ))
            elif not dod[req_key]:
                violations.append(ComplianceViolation(
                    section=ManifestSection.DEFINITION_OF_DONE,
                    requirement=req_name,
                    severity="major",
                    message=f"Empty DoD requirement: {req_name}",
                    suggestion=f"Provide details for '{req_key}'"
                ))
        
        return violations
    
    def _calculate_dod_score(self, plan_data: Dict[str, Any]) -> float:
        """Calculate DoD compliance score (0-100)."""
        if "definition_of_done" not in plan_data:
            return 0.0
        
        dod = plan_data["definition_of_done"]
        total_requirements = len(self.dod_requirements)
        met_requirements = 0
        
        for requirement in self.dod_requirements:
            req_key = requirement["key"]
            if req_key in dod and dod[req_key]:
                met_requirements += 1
        
        return (met_requirements / total_requirements * 100) if total_requirements > 0 else 0.0
    
    # ========== Phase Structure Validation ==========
    
    def _validate_phase_structure(self, plan_data: Dict[str, Any]) -> List[ComplianceViolation]:
        """Validate phase structure compliance."""
        violations = []
        
        if "phases" not in plan_data:
            violations.append(ComplianceViolation(
                section=ManifestSection.PHASES,
                requirement="Phases section presence",
                severity="critical",
                message="Missing 'phases' section"
            ))
            return violations
        
        phases = plan_data["phases"]
        
        for i, phase in enumerate(phases):
            # Required phase fields per manifest
            required_fields = ["phase_number", "phase_name", "tasks", "dor", "dod"]
            for field in required_fields:
                if field not in phase:
                    violations.append(ComplianceViolation(
                        section=ManifestSection.PHASES,
                        requirement=f"Phase {field} field",
                        severity="major",
                        message=f"Phase {i+1} missing required field: {field}"
                    ))
            
            # Validate tasks
            if "tasks" in phase:
                task_violations = self._validate_task_structure(phase["tasks"], i)
                violations.extend(task_violations)
        
        return violations
    
    def _validate_task_structure(self, tasks: List[Dict[str, Any]], phase_index: int) -> List[ComplianceViolation]:
        """Validate task structure compliance."""
        violations = []
        
        for j, task in enumerate(tasks):
            # Required task fields per manifest
            required_fields = ["task_id", "task_name", "estimated_hours", "acceptance_criteria"]
            for field in required_fields:
                if field not in task:
                    violations.append(ComplianceViolation(
                        section=ManifestSection.PHASES,
                        requirement=f"Task {field} field",
                        severity="major",
                        message=f"Phase {phase_index+1}, Task {j+1} missing: {field}"
                    ))
            
            # Validate acceptance criteria
            if "acceptance_criteria" in task:
                if not task["acceptance_criteria"]:
                    violations.append(ComplianceViolation(
                        section=ManifestSection.ACCEPTANCE_CRITERIA,
                        requirement="Non-empty acceptance criteria",
                        severity="major",
                        message=f"Phase {phase_index+1}, Task {j+1} has empty acceptance criteria"
                    ))
                elif len(task["acceptance_criteria"]) < 1:
                    violations.append(ComplianceViolation(
                        section=ManifestSection.ACCEPTANCE_CRITERIA,
                        requirement="At least 1 acceptance criterion",
                        severity="minor",
                        message=f"Phase {phase_index+1}, Task {j+1} should have acceptance criteria"
                    ))
        
        return violations
    
    # ========== TDD Requirements Validation ==========
    
    def _validate_tdd_requirements(self, plan_data: Dict[str, Any]) -> List[ComplianceViolation]:
        """Validate TDD requirements compliance."""
        violations = []
        
        # Check if TDD is required for this plan
        complexity = plan_data.get("metadata", {}).get("complexity", "low")
        if complexity in ["medium", "high", "complex"]:
            # TDD is mandatory for medium+ complexity
            if "tdd_workflow" not in plan_data:
                violations.append(ComplianceViolation(
                    section=ManifestSection.TDD_REQUIREMENTS,
                    requirement="TDD workflow presence",
                    severity="critical",
                    message=f"TDD workflow required for {complexity} complexity",
                    suggestion="Add 'tdd_workflow' section with RED→GREEN→REFACTOR phases"
                ))
        
        # If TDD workflow exists, validate structure
        if "tdd_workflow" in plan_data:
            tdd = plan_data["tdd_workflow"]
            required_phases = ["red_phase", "green_phase", "refactor_phase"]
            for phase in required_phases:
                if phase not in tdd:
                    violations.append(ComplianceViolation(
                        section=ManifestSection.TDD_REQUIREMENTS,
                        requirement=f"TDD {phase}",
                        severity="major",
                        message=f"Missing TDD phase: {phase}"
                    ))
        
        return violations
    
    # ========== Metadata Validation ==========
    
    def _validate_metadata_compliance(self, plan_data: Dict[str, Any]) -> List[ComplianceViolation]:
        """Validate metadata compliance."""
        violations = []
        
        if "metadata" not in plan_data:
            violations.append(ComplianceViolation(
                section=ManifestSection.METADATA,
                requirement="Metadata section presence",
                severity="critical",
                message="Missing 'metadata' section"
            ))
            return violations
        
        metadata = plan_data["metadata"]
        
        # Required metadata fields per manifest
        required_fields = ["plan_name", "version", "complexity", "estimated_hours", "created_at"]
        for field in required_fields:
            if field not in metadata:
                violations.append(ComplianceViolation(
                    section=ManifestSection.METADATA,
                    requirement=f"Metadata {field} field",
                    severity="major",
                    message=f"Missing metadata field: {field}"
                ))
        
        return violations
    
    # ========== Manifest Loading ==========
    
    def _load_manifest(self) -> Dict[str, Any]:
        """Load manifest YAML."""
        if not self.manifest_path.exists():
            self.logger.warning(f"Manifest not found: {self.manifest_path}")
            return self._get_default_manifest()
        
        try:
            with open(self.manifest_path, 'r') as f:
                manifest = yaml.safe_load(f)
            self.logger.info(f"Loaded manifest: {self.manifest_path}")
            return manifest
        except Exception as e:
            self.logger.error(f"Failed to load manifest: {e}")
            return self._get_default_manifest()
    
    def _get_default_manifest(self) -> Dict[str, Any]:
        """Get default manifest structure."""
        return {
            "definition_of_ready": {
                "requirements": [
                    {"key": "requirements_clear", "name": "Requirements Clear"},
                    {"key": "acceptance_criteria_defined", "name": "Acceptance Criteria Defined"},
                    {"key": "dependencies_identified", "name": "Dependencies Identified"}
                ]
            },
            "definition_of_done": {
                "requirements": [
                    {"key": "code_complete", "name": "Code Complete"},
                    {"key": "tests_passing", "name": "Tests Passing"},
                    {"key": "documentation_updated", "name": "Documentation Updated"}
                ]
            },
            "tdd_requirements": {
                "mandatory_for": ["medium", "high", "complex"]
            }
        }
    
    def _extract_dor_requirements(self) -> List[Dict[str, str]]:
        """Extract DoR requirements from manifest."""
        dor = self.manifest.get("definition_of_ready", {})
        requirements = dor.get("requirements", [])
        return requirements if requirements else [
            {"key": "requirements_clear", "name": "Requirements Clear"},
            {"key": "acceptance_criteria_defined", "name": "Acceptance Criteria Defined"},
            {"key": "dependencies_identified", "name": "Dependencies Identified"}
        ]
    
    def _extract_dod_requirements(self) -> List[Dict[str, str]]:
        """Extract DoD requirements from manifest."""
        dod = self.manifest.get("definition_of_done", {})
        requirements = dod.get("requirements", [])
        return requirements if requirements else [
            {"key": "code_complete", "name": "Code Complete"},
            {"key": "tests_passing", "name": "Tests Passing"},
            {"key": "documentation_updated", "name": "Documentation Updated"}
        ]
    
    def _extract_tdd_requirements(self) -> Dict[str, Any]:
        """Extract TDD requirements from manifest."""
        return self.manifest.get("tdd_requirements", {
            "mandatory_for": ["medium", "high", "complex"]
        })
