"""
Orchestrator Manifest Validator

Validates orchestrator implementations against their manifest definitions.
Prevents drift by checking:
- Required features are implemented
- Integrations are wired correctly
- Quality gates are enforced
- Workflows follow expected sequence

Used by:
- Orchestrators during initialization (self-validation)
- Healthcheck for drift detection
- CI/CD for deployment validation

Author: CORTEX Development Team
Version: 1.0
Created: 2025-12-08
"""

import os
import yaml
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime


logger = logging.getLogger(__name__)


class ValidationSeverity(Enum):
    """Validation issue severity levels"""
    CRITICAL = "critical"      # Missing critical requirement, blocks execution
    HIGH = "high"             # Missing important feature, degrades experience
    MEDIUM = "medium"         # Missing enhancement, acceptable for now
    LOW = "low"              # Nice-to-have, cosmetic issue
    INFO = "info"            # Informational, no action needed


@dataclass
class ValidationIssue:
    """Represents a single validation issue"""
    severity: ValidationSeverity
    category: str             # requirement|integration|gate|workflow|template
    item_id: str             # REQ-001, INT-003, etc.
    item_name: str
    expected: str            # What the manifest requires
    actual: str              # What was found in implementation
    resolution: str          # How to fix
    file_path: Optional[str] = None
    line_number: Optional[int] = None


@dataclass
class ValidationReport:
    """Complete validation report for an orchestrator"""
    orchestrator_name: str
    manifest_version: str
    validation_timestamp: datetime
    overall_status: str      # compliant|drift_detected|non_compliant
    compliance_score: float  # 0.0-100.0
    issues: List[ValidationIssue] = field(default_factory=list)
    summary: Dict[str, int] = field(default_factory=dict)
    total_requirements: int = 0
    implemented_count: int = 0
    
    @property
    def compliance_percentage(self) -> float:
        """Get compliance as percentage"""
        return self.compliance_score
    
    @property
    def status(self) -> str:
        """Get status text"""
        if self.compliance_score >= 80:
            return "Compliant"
        elif self.compliance_score >= 60:
            return "Drift Detected"
        else:
            return "Non-Compliant"
    
    @property
    def requirement_id(self) -> str:
        """Compatibility property for alignment checks"""
        return f"{self.orchestrator_name}_manifest"
    
    def add_issue(self, issue: ValidationIssue):
        """Add validation issue and update summary"""
        self.issues.append(issue)
        severity_key = issue.severity.value
        self.summary[severity_key] = self.summary.get(severity_key, 0) + 1
    
    def get_critical_issues(self) -> List[ValidationIssue]:
        """Get all critical severity issues"""
        return [i for i in self.issues if i.severity == ValidationSeverity.CRITICAL]
    
    def calculate_compliance_score(self) -> float:
        """Calculate compliance score based on issues"""
        if not self.issues:
            return 100.0
        
        # Weight by severity
        weights = {
            ValidationSeverity.CRITICAL: 10,
            ValidationSeverity.HIGH: 5,
            ValidationSeverity.MEDIUM: 2,
            ValidationSeverity.LOW: 1,
            ValidationSeverity.INFO: 0
        }
        
        total_weight = sum(weights[i.severity] for i in self.issues)
        max_score = 100.0
        deduction = min(total_weight * 2, max_score)
        
        return max(0.0, max_score - deduction)


class ManifestValidator:
    """
    Validates orchestrator implementations against manifest definitions.
    
    Usage:
        validator = ManifestValidator(cortex_root)
        report = validator.validate_orchestrator("planning_system_2.0")
        
        if not report.get_critical_issues():
            logger.info("✅ Orchestrator compliant with manifest")
        else:
            logger.error(f"❌ {len(report.get_critical_issues())} critical issues")
    """
    
    def __init__(self, cortex_root: str):
        """
        Initialize manifest validator.
        
        Args:
            cortex_root: Path to CORTEX root directory
        """
        self.cortex_root = Path(cortex_root)
        self.manifests_dir = self.cortex_root / "cortex-brain" / "orchestrator-manifests"
        self.schema_path = self.manifests_dir / "manifest-schema.yaml"
        self.orchestrators_dir = self.cortex_root / "src" / "orchestrators"
        
        # Caching for performance optimization
        self._manifest_cache: Dict[str, Dict[str, Any]] = {}
        self._file_content_cache: Dict[str, str] = {}
        self._method_cache: Dict[str, set] = {}
        self._validation_report_cache: Dict[str, ValidationReport] = {}
        
        # Load schema
        self.schema = self._load_schema()
    
    def _load_schema(self) -> Dict[str, Any]:
        """Load manifest schema"""
        try:
            if not self.schema_path.exists():
                logger.warning(f"Schema not found at {self.schema_path}")
                return {}
            
            with open(self.schema_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to load schema: {e}")
            return {}
    
    def load_manifest(self, manifest_path: str) -> Optional[Dict[str, Any]]:
        """
        Load manifest file with caching.
        
        Args:
            manifest_path: Path to manifest YAML file
            
        Returns:
            Manifest dict or None if not found
        """
        # Check cache first
        if manifest_path in self._manifest_cache:
            return self._manifest_cache[manifest_path]
        
        try:
            path = Path(manifest_path)
            if not path.exists():
                logger.warning(f"Manifest not found: {manifest_path}")
                return None
            
            with open(path, 'r', encoding='utf-8') as f:
                manifest = yaml.safe_load(f)
            
            # Cache the result
            self._manifest_cache[manifest_path] = manifest
            return manifest
            
        except Exception as e:
            logger.error(f"Failed to load manifest {manifest_path}: {e}")
            return None
    
    def _read_file_cached(self, file_path: str) -> Optional[str]:
        """Read file with caching to avoid repeated file I/O"""
        if file_path in self._file_content_cache:
            return self._file_content_cache[file_path]
        
        try:
            path = Path(file_path)
            if not path.exists():
                return None
            
            content = path.read_text(encoding='utf-8')
            self._file_content_cache[file_path] = content
            return content
        except Exception as e:
            logger.error(f"Failed to read {file_path}: {e}")
            return None
    
    def _extract_methods_cached(self, file_path: str) -> Set[str]:
        """Extract method names with caching"""
        if file_path in self._method_cache:
            return self._method_cache[file_path]
        
        content = self._read_file_cached(file_path)
        if not content:
            return set()
        
        import re
        pattern = r'def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\('
        methods = set(re.findall(pattern, content))
        
        self._method_cache[file_path] = methods
        return methods
    
    def validate_orchestrator(
        self,
        orchestrator_name: str,
        orchestrator_instance: Optional[Any] = None
    ) -> ValidationReport:
        """
        Validate orchestrator against its manifest.
        
        Args:
            orchestrator_name: Name of orchestrator
            orchestrator_instance: Optional orchestrator instance for runtime checks
            
        Returns:
            ValidationReport with issues and compliance score
        """
        report = ValidationReport(
            orchestrator_name=orchestrator_name,
            manifest_version="unknown",
            validation_timestamp=datetime.now(),
            overall_status="unknown",
            compliance_score=0.0
        )
        
        # Load manifest - construct path from name
        manifest_path = self.manifests_dir / f"{orchestrator_name}-manifest.yaml"
        manifest = self.load_manifest(str(manifest_path))
        if not manifest:
            report.add_issue(ValidationIssue(
                severity=ValidationSeverity.CRITICAL,
                category="manifest",
                item_id="MANIFEST-001",
                item_name="Manifest File",
                expected="Manifest file exists",
                actual="Manifest file not found",
                resolution=f"Create {orchestrator_name}-manifest.yaml in {self.manifests_dir}"
            ))
            report.overall_status = "non_compliant"
            return report
        
        report.manifest_version = manifest.get('metadata', {}).get('version', 'unknown')
        
        # Validate requirements
        self._validate_requirements(manifest, orchestrator_instance, report)
        
        # Validate integrations
        self._validate_integrations(manifest, orchestrator_instance, report)
        
        # Validate quality gates
        self._validate_quality_gates(manifest, orchestrator_instance, report)
        
        # Validate workflows
        self._validate_workflows(manifest, orchestrator_instance, report)
        
        # Calculate compliance score
        report.compliance_score = report.calculate_compliance_score()
        
        # Determine overall status
        critical_count = len(report.get_critical_issues())
        if critical_count > 0:
            report.overall_status = "non_compliant"
        elif report.compliance_score < 80:
            report.overall_status = "drift_detected"
        else:
            report.overall_status = "compliant"
        
        return report
    
    def _validate_requirements(
        self,
        manifest: Dict[str, Any],
        orchestrator_instance: Optional[Any],
        report: ValidationReport
    ):
        """Validate all requirements from manifest"""
        requirements = manifest.get('requirements', [])
        
        for req in requirements:
            req_id = req.get('requirement_id', 'UNKNOWN')
            name = req.get('name', 'Unknown')
            status = req.get('status', 'unknown')
            priority = req.get('priority', 'medium')
            validation_method = req.get('validation_method', 'manual')
            validation_criteria = req.get('validation_criteria', '')
            
            # Skip if already marked as implemented
            if status == 'implemented':
                continue
            
            # Map priority to severity
            severity_map = {
                'critical': ValidationSeverity.CRITICAL,
                'high': ValidationSeverity.HIGH,
                'medium': ValidationSeverity.MEDIUM,
                'low': ValidationSeverity.LOW
            }
            severity = severity_map.get(priority, ValidationSeverity.MEDIUM)
            
            # Check validation criteria
            is_implemented = False
            
            if validation_method == 'method_exists' and orchestrator_instance:
                # Check if method exists
                method_name = validation_criteria.split('(')[0].split('.')[-1]
                is_implemented = hasattr(orchestrator_instance, method_name)
            
            if not is_implemented and status != 'partial':
                report.add_issue(ValidationIssue(
                    severity=severity,
                    category="requirement",
                    item_id=req_id,
                    item_name=name,
                    expected=req.get('description', 'Feature should be implemented'),
                    actual=f"Status: {status}",
                    resolution=req.get('implementation_notes', 'Implement required feature'),
                    file_path=req.get('implementation_file')
                ))
    
    def _validate_integrations(
        self,
        manifest: Dict[str, Any],
        orchestrator_instance: Optional[Any],
        report: ValidationReport
    ):
        """Validate all integrations from manifest"""
        integrations = manifest.get('integrations', [])
        
        for integration in integrations:
            integration_id = integration.get('integration_id', 'UNKNOWN')
            target = integration.get('target_component', 'Unknown')
            integration_type = integration.get('integration_type', 'optional')
            status = integration.get('status', 'unknown')
            
            # Skip if implemented or optional
            if status == 'implemented':
                continue
            
            if integration_type == 'optional':
                continue
            
            # Required or conditional integration missing
            severity = ValidationSeverity.HIGH if integration_type == 'required' else ValidationSeverity.MEDIUM
            
            report.add_issue(ValidationIssue(
                severity=severity,
                category="integration",
                item_id=integration_id,
                item_name=f"Integration: {target}",
                expected=integration.get('expected_behavior', 'Integration should work'),
                actual=f"Status: {status}",
                resolution=f"Integrate with {target} component",
                file_path=integration.get('implementation_file')
            ))
    
    def _validate_quality_gates(
        self,
        manifest: Dict[str, Any],
        orchestrator_instance: Optional[Any],
        report: ValidationReport
    ):
        """Validate all quality gates from manifest"""
        gates = manifest.get('quality_gates', [])
        
        for gate in gates:
            gate_id = gate.get('gate_id', 'UNKNOWN')
            name = gate.get('name', 'Unknown')
            status = gate.get('status', 'unknown')
            priority = gate.get('priority')
            blocking = gate.get('blocking', True)
            
            # Skip if implemented
            if status == 'implemented':
                continue
            
            # Determine severity
            if blocking and priority == 'critical':
                severity = ValidationSeverity.CRITICAL
            elif blocking:
                severity = ValidationSeverity.HIGH
            else:
                severity = ValidationSeverity.MEDIUM
            
            report.add_issue(ValidationIssue(
                severity=severity,
                category="quality_gate",
                item_id=gate_id,
                item_name=name,
                expected=gate.get('validation_criteria', 'Gate should be enforced'),
                actual=f"Status: {status}",
                resolution=f"Implement {name} gate at {gate.get('trigger_point', 'appropriate point')}",
                file_path=gate.get('implementation_method')
            ))
    
    def _validate_workflows(
        self,
        manifest: Dict[str, Any],
        orchestrator_instance: Optional[Any],
        report: ValidationReport
    ):
        """Validate workflow steps from manifest"""
        workflows = manifest.get('workflows', [])
        
        for workflow in workflows:
            workflow_id = workflow.get('workflow_id', 'UNKNOWN')
            workflow_name = workflow.get('name', 'Unknown')
            phases = workflow.get('phases', [])
            
            for phase in phases:
                if not phase.get('required', False):
                    continue
                
                steps = phase.get('steps', [])
                for step in steps:
                    if not step.get('required', False):
                        continue
                    
                    status = step.get('status', 'unknown')
                    if status == 'implemented':
                        continue
                    
                    step_id = step.get('step_id', 'UNKNOWN')
                    step_name = step.get('name', 'Unknown')
                    
                    report.add_issue(ValidationIssue(
                        severity=ValidationSeverity.MEDIUM,
                        category="workflow",
                        item_id=step_id,
                        item_name=f"{workflow_name} > {step_name}",
                        expected=step.get('validation', 'Step should execute'),
                        actual=f"Status: {status}",
                        resolution="Implement required workflow step"
                    ))
    
    def generate_drift_report(
        self,
        report: ValidationReport,
        output_path: Optional[Path] = None
    ) -> str:
        """
        Generate markdown drift report.
        
        Args:
            report: ValidationReport to format
            output_path: Optional path to save report
            
        Returns:
            Markdown report string
        """
        lines = [
            f"# Orchestrator Drift Report: {report.orchestrator_name}",
            "",
            f"**Generated:** {report.validation_timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Manifest Version:** {report.manifest_version}",
            f"**Overall Status:** {report.overall_status.upper()}",
            f"**Compliance Score:** {report.compliance_score:.1f}/100.0",
            "",
            "---",
            "",
            "## Summary",
            ""
        ]
        
        # Add summary table
        if report.summary:
            lines.append("| Severity | Count |")
            lines.append("|----------|-------|")
            for severity in ValidationSeverity:
                count = report.summary.get(severity.value, 0)
                if count > 0:
                    lines.append(f"| {severity.value.upper()} | {count} |")
            lines.append("")
        
        # Add critical issues first
        critical_issues = report.get_critical_issues()
        if critical_issues:
            lines.extend([
                "## 🚨 Critical Issues",
                "",
                "These issues MUST be resolved before deployment:",
                ""
            ])
            
            for issue in critical_issues:
                lines.extend([
                    f"### {issue.item_id}: {issue.item_name}",
                    "",
                    f"**Category:** {issue.category}",
                    f"**Expected:** {issue.expected}",
                    f"**Actual:** {issue.actual}",
                    f"**Resolution:** {issue.resolution}",
                    ""
                ])
        
        # Group remaining issues by severity
        for severity in [ValidationSeverity.HIGH, ValidationSeverity.MEDIUM, ValidationSeverity.LOW]:
            severity_issues = [i for i in report.issues if i.severity == severity]
            if not severity_issues:
                continue
            
            emoji_map = {
                ValidationSeverity.HIGH: "⚠️",
                ValidationSeverity.MEDIUM: "ℹ️",
                ValidationSeverity.LOW: "💡"
            }
            emoji = emoji_map.get(severity, "")
            
            lines.extend([
                f"## {emoji} {severity.value.title()} Priority Issues",
                ""
            ])
            
            for issue in severity_issues:
                lines.extend([
                    f"### {issue.item_id}: {issue.item_name}",
                    "",
                    f"**Expected:** {issue.expected}",
                    f"**Actual:** {issue.actual}",
                    f"**Resolution:** {issue.resolution}",
                    ""
                ])
        
        # Add recommendations
        lines.extend([
            "---",
            "",
            "## Recommendations",
            ""
        ])
        
        if report.compliance_score >= 90:
            lines.append("✅ Orchestrator is highly compliant with manifest. Address remaining items during next sprint.")
        elif report.compliance_score >= 70:
            lines.append("⚠️  Orchestrator has moderate drift. Prioritize high-severity issues.")
        else:
            lines.append("❌ Orchestrator has significant drift. Immediate action required.")
        
        markdown = "\n".join(lines)
        
        # Save if path provided
        if output_path:
            try:
                output_path.parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(markdown)
                logger.info(f"📄 Drift report saved to {output_path}")
            except Exception as e:
                logger.error(f"Failed to save drift report: {e}")
        
        return markdown
    
    def validate_all_orchestrators(self) -> Dict[str, ValidationReport]:
        """
        Validate all orchestrators that have manifests.
        
        Returns:
            Dict mapping orchestrator_name to ValidationReport
        """
        reports = {}
        
        # Find all manifest files
        manifest_files = list(self.manifests_dir.glob("*-manifest.yaml"))
        
        for manifest_file in manifest_files:
            if manifest_file.name == "manifest-schema.yaml":
                continue
            
            orchestrator_name = manifest_file.stem.replace("-manifest", "")
            logger.info(f"Validating {orchestrator_name}...")
            
            report = self.validate_orchestrator(orchestrator_name)
            reports[orchestrator_name] = report
            
            # Log summary
            if report.overall_status == "compliant":
                logger.info(f"  ✅ {orchestrator_name}: Compliant ({report.compliance_score:.1f}%)")
            elif report.overall_status == "drift_detected":
                logger.warning(f"  ⚠️  {orchestrator_name}: Drift detected ({report.compliance_score:.1f}%)")
            else:
                logger.error(f"  ❌ {orchestrator_name}: Non-compliant ({report.compliance_score:.1f}%)")
        
        return reports
