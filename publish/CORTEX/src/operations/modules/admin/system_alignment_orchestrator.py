"""
System Alignment Orchestrator - Convention-Based Discovery & Validation

Auto-discovers and validates all CORTEX enhancements without hardcoded lists.
Admin-only feature that integrates with optimize command for continuous monitoring.

Design Philosophy:
    - Convention Over Configuration
    - Zero maintenance when adding features
    - Self-healing architecture
    - Admin-only execution

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Version: 1.0
Status: IMPLEMENTATION
"""

import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime

from src.operations.base_operation_module import (
    BaseOperationModule,
    OperationPhase,
    OperationStatus,
    OperationResult
)

logger = logging.getLogger(__name__)


@dataclass
class IntegrationScore:
    """Integration depth score for a feature (0-100%)."""
    feature_name: str
    feature_type: str  # 'orchestrator', 'agent', etc.
    discovered: bool = False  # 20 points
    imported: bool = False  # +20 points
    instantiated: bool = False  # +20 points
    documented: bool = False  # +10 points
    tested: bool = False  # +10 points
    wired: bool = False  # +10 points
    optimized: bool = False  # +10 points
    
    @property
    def score(self) -> int:
        """Calculate 0-100 integration score."""
        total = 0
        if self.discovered:
            total += 20
        if self.imported:
            total += 20
        if self.instantiated:
            total += 20
        if self.documented:
            total += 10
        if self.tested:
            total += 10
        if self.wired:
            total += 10
        if self.optimized:
            total += 10
        return total
    
    @property
    def status(self) -> str:
        """Get status emoji and label."""
        score = self.score
        if score >= 90:
            return "✅ Healthy"
        elif score >= 70:
            return "⚠️ Warning"
        else:
            return "❌ Critical"
    
    @property
    def issues(self) -> List[str]:
        """List integration issues."""
        issues = []
        if not self.documented:
            issues.append("Missing documentation")
        if not self.tested:
            issues.append("No test coverage")
        if not self.wired:
            issues.append("Not wired to entry point")
        if not self.optimized:
            issues.append("Performance not validated")
        return issues


@dataclass
class RemediationSuggestion:
    """Auto-remediation suggestion for a feature."""
    feature_name: str
    suggestion_type: str  # 'wiring', 'test', 'documentation'
    content: str  # Generated code/template
    file_path: Optional[str] = None  # Where to save suggestion


@dataclass
class AlignmentReport:
    """System alignment validation report."""
    timestamp: datetime
    overall_health: int  # 0-100%
    critical_issues: int = 0
    warnings: int = 0
    feature_scores: Dict[str, IntegrationScore] = field(default_factory=dict)
    remediation_suggestions: List[RemediationSuggestion] = field(default_factory=list)
    orphaned_triggers: List[str] = field(default_factory=list)  # Triggers without features
    ghost_features: List[str] = field(default_factory=list)  # Features without triggers
    deployment_gate_results: Optional[Dict[str, Any]] = None  # Deployment quality gates
    package_purity_results: Optional[Dict[str, Any]] = None  # Admin leak detection
    suggestions: List[Dict[str, str]] = field(default_factory=list)
    
    @property
    def is_healthy(self) -> bool:
        """Check if system is healthy (>80% overall)."""
        return self.overall_health >= 80 and self.critical_issues == 0
    
    @property
    def has_warnings(self) -> bool:
        """Check if system has non-critical warnings."""
        return self.warnings > 0 and self.critical_issues == 0
    
    @property
    def has_errors(self) -> bool:
        """Check if system has critical errors."""
        return self.critical_issues > 0
    
    @property
    def issues_found(self) -> int:
        """Total issues (critical + warnings)."""
        return self.critical_issues + self.warnings


class SystemAlignmentOrchestrator(BaseOperationModule):
    """
    Convention-based system alignment validator.
    
    Auto-discovers all CORTEX features and validates integration depth:
    - Orchestrators (src/operations/modules/, src/workflows/)
    - Agents (src/agents/)
    - Entry points (response-templates.yaml)
    - Documentation (prompts/modules/)
    - Tests (tests/)
    - Capabilities (cortex-brain/capabilities.yaml)
    
    Scoring Algorithm:
        discovered: 20     # File exists in correct location
        imported: 40       # Can be imported without errors
        instantiated: 60   # Class can be instantiated
        documented: 70     # Has documentation
        tested: 80         # Has test coverage >70%
        wired: 90          # Entry point trigger exists
        optimized: 100     # Performance benchmarks pass
    """
    
    def __init__(self, context: Optional[Dict[str, Any]] = None):
        """Initialize system alignment orchestrator."""
        super().__init__()
        self.context = context or {}
        self.project_root = Path(self.context.get("project_root", Path.cwd()))
        self.cortex_brain = self.project_root / "cortex-brain"
        
        # Discovery components (lazy loaded)
        self._orchestrator_scanner = None
        self._agent_scanner = None
        self._entry_point_scanner = None
        self._documentation_scanner = None
    
    def _is_admin_environment(self) -> bool:
        """Check if running in CORTEX admin environment."""
        admin_path = self.cortex_brain / "admin"
        return admin_path.exists() and admin_path.is_dir()
    
    def validate(self, context: Dict[str, Any]) -> bool:
        """
        Validate module can execute.
        
        Admin-only feature - gracefully declines in user repos.
        """
        if not self._is_admin_environment():
            logger.info("System alignment is admin-only (CORTEX dev repo)")
            return False
        
        return True
    
    def validate_prerequisites(self, context: Dict[str, Any]) -> tuple[bool, List[str]]:
        """Validate prerequisites for system alignment."""
        if not self._is_admin_environment():
            return False, ["Admin environment required"]
        return True, []
    
    def execute(self, context: Dict[str, Any]) -> OperationResult:
        """
        Execute system alignment validation.
        
        Returns:
            OperationResult with alignment report
        """
        start_time = datetime.now()
        
        try:
            logger.info("🔍 Running system alignment validation...")
            
            # Run full validation
            report = self.run_full_validation()
            
            # Store report in context
            context["alignment_report"] = report
            
            # Build result message
            message = self._format_report_summary(report)
            
            duration = (datetime.now() - start_time).total_seconds()
            
            return OperationResult(
                success=report.is_healthy,
                status=OperationStatus.SUCCESS if report.is_healthy else OperationStatus.WARNING,
                message=message,
                data={"report": report},
                duration_seconds=duration
            )
            
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            logger.error(f"System alignment failed: {e}", exc_info=True)
            
            return OperationResult(
                success=False,
                status=OperationStatus.FAILED,
                message=f"System alignment validation failed: {str(e)}",
                errors=[str(e)],
                duration_seconds=duration
            )
    
    def run_full_validation(self) -> AlignmentReport:
        """
        Run complete system alignment validation.
        
        Returns:
            AlignmentReport with all validation results
        """
        report = AlignmentReport(
            timestamp=datetime.now(),
            overall_health=0
        )
        
        # Phase 1: Discover all features
        orchestrators = self._discover_orchestrators()
        agents = self._discover_agents()
        
        # Phase 1.5: Discover entry points and validate wiring
        orphaned, ghost = self._validate_entry_points(orchestrators)
        report.orphaned_triggers = orphaned
        report.ghost_features = ghost
        
        # Phase 2: Validate integration depth
        for name, metadata in orchestrators.items():
            score = self._calculate_integration_score(name, metadata, "orchestrator")
            report.feature_scores[name] = score
            
            # Categorize issues
            if score.score < 70:
                report.critical_issues += 1
            elif score.score < 90:
                report.warnings += 1
        
        for name, metadata in agents.items():
            score = self._calculate_integration_score(name, metadata, "agent")
            report.feature_scores[name] = score
            
            if score.score < 70:
                report.critical_issues += 1
            elif score.score < 90:
                report.warnings += 1
        
        # Phase 3: Validate documentation coverage
        undocumented = self._validate_documentation(orchestrators)
        for orchestrator_name in undocumented:
            if orchestrator_name in report.feature_scores:
                report.feature_scores[orchestrator_name].documented = False
        
        # Phase 3.5: Validate deployment readiness (quality gates + package purity)
        self._validate_deployment_readiness(report)
        
        # Phase 4: Generate auto-remediation suggestions
        self._generate_remediation_suggestions(report, orchestrators, agents)
        
        # Calculate overall health
        if report.feature_scores:
            total_score = sum(s.score for s in report.feature_scores.values())
            report.overall_health = total_score // len(report.feature_scores)
        else:
            report.overall_health = 100  # No features = healthy
        
        return report
    
    def _discover_orchestrators(self) -> Dict[str, Dict[str, Any]]:
        """Discover all orchestrators using convention-based scanning."""
        # Lazy load scanner
        if self._orchestrator_scanner is None:
            from src.discovery.orchestrator_scanner import OrchestratorScanner
            self._orchestrator_scanner = OrchestratorScanner(self.project_root)
        
        return self._orchestrator_scanner.discover()
    
    def _discover_agents(self) -> Dict[str, Dict[str, Any]]:
        """Discover all agents using convention-based scanning."""
        # Lazy load scanner
        if self._agent_scanner is None:
            from src.discovery.agent_scanner import AgentScanner
            self._agent_scanner = AgentScanner(self.project_root)
        
        return self._agent_scanner.discover()
    
    def _validate_entry_points(
        self,
        orchestrators: Dict[str, Dict[str, Any]]
    ) -> tuple[List[str], List[str]]:
        """Validate entry point wiring."""
        # Lazy load scanner
        if self._entry_point_scanner is None:
            from src.discovery.entry_point_scanner import EntryPointScanner
            self._entry_point_scanner = EntryPointScanner(self.project_root)
        
        return self._entry_point_scanner.validate_wiring(orchestrators)
    
    def _validate_documentation(
        self,
        orchestrators: Dict[str, Dict[str, Any]]
    ) -> List[str]:
        """Validate documentation coverage."""
        # Lazy load scanner
        if self._documentation_scanner is None:
            from src.discovery.documentation_scanner import DocumentationScanner
            self._documentation_scanner = DocumentationScanner(self.project_root)
        
        return self._documentation_scanner.validate_orchestrator_coverage(orchestrators)
    
    def _calculate_integration_score(
        self,
        name: str,
        metadata: Dict[str, Any],
        feature_type: str
    ) -> IntegrationScore:
        """
        Calculate integration score for a feature.
        
        Args:
            name: Feature name
            metadata: Discovery metadata
            feature_type: 'orchestrator' or 'agent'
        
        Returns:
            IntegrationScore with validation results
        """
        score = IntegrationScore(
            feature_name=name,
            feature_type=feature_type
        )
        
        # Layer 1: Discovered (20 points) - file exists
        score.discovered = True
        
        # Layer 2-3: Import & Instantiation validation
        module_path = metadata.get("module_path")
        if module_path:
            # Use IntegrationScorer for import/instantiation validation
            from src.validation.integration_scorer import IntegrationScorer
            scorer = IntegrationScorer(self.project_root)
            
            score.imported = scorer.validate_import(module_path)
            
            class_name = metadata.get("class_name")
            if class_name:
                score.instantiated = scorer.validate_instantiation(module_path, class_name)
        
        # Layer 4: Documentation validation
        score.documented = metadata.get("has_docstring", False)
        
        # Layer 5: Test coverage validation
        from src.validation.test_coverage_validator import TestCoverageValidator
        test_validator = TestCoverageValidator(self.project_root)
        coverage = test_validator.get_test_coverage(name, feature_type)
        score.tested = coverage.get("coverage_pct", 0) >= 70
        
        # Layer 6: Wiring validation
        from src.validation.wiring_validator import WiringValidator
        wiring_validator = WiringValidator(self.project_root)
        entry_points = self._get_entry_points()
        score.wired = wiring_validator.check_orchestrator_wired(name, entry_points)
        
        # Layer 7: Performance validation (placeholder for future)
        score.optimized = False  # TODO: Implement performance benchmarks
        
        return score
    
    def _get_entry_points(self) -> Dict[str, Dict[str, Any]]:
        """Get entry points from response templates."""
        if self._entry_point_scanner is None:
            from src.discovery.entry_point_scanner import EntryPointScanner
            self._entry_point_scanner = EntryPointScanner(self.project_root)
        
        return self._entry_point_scanner.discover()
    
    def _validate_deployment_readiness(self, report: AlignmentReport) -> None:
        """
        Phase 3: Validate deployment quality gates and package purity.
        
        Args:
            report: AlignmentReport to populate with deployment validation results
        """
        # Lazy load deployment validators
        from src.deployment.deployment_gates import DeploymentGates
        from src.deployment.package_purity_checker import PackagePurityChecker
        
        # Gate validation
        gates = DeploymentGates(self.project_root)
        gate_results = gates.validate_all_gates(alignment_report=report.__dict__)
        report.deployment_gate_results = gate_results
        
        # Track gate failures
        if not gate_results["passed"]:
            for error in gate_results.get("errors", []):
                report.critical_issues += 1
                report.suggestions.append({
                    "type": "deployment_gate",
                    "message": error
                })
        
        for warning in gate_results.get("warnings", []):
            report.warnings += 1
            report.suggestions.append({
                "type": "deployment_warning",
                "message": warning
            })
        
        # Package purity check (only if dist/ exists)
        dist_dir = self.project_root / "dist"
        if dist_dir.exists():
            purity_checker = PackagePurityChecker(dist_dir, self.project_root)
            purity_results = purity_checker.validate_purity()
            report.package_purity_results = purity_results
            
            if not purity_results["is_pure"]:
                report.critical_issues += len(purity_results.get("admin_leaks", []))
                for leak in purity_results.get("admin_leaks", []):
                    report.suggestions.append({
                        "type": "admin_leak",
                        "message": f"Admin code leaked to package: {leak}"
                    })
    
    def _generate_remediation_suggestions(
        self,
        report: AlignmentReport,
        orchestrators: Dict[str, Dict[str, Any]],
        agents: Dict[str, Dict[str, Any]]
    ) -> None:
        """
        Phase 5: Generate auto-remediation suggestions for incomplete features.
        
        Args:
            report: AlignmentReport to populate with remediation suggestions
            orchestrators: Discovered orchestrators
            agents: Discovered agents
        """
        # Lazy load remediation generators
        from src.remediation.wiring_generator import WiringGenerator
        from src.remediation.test_skeleton_generator import TestSkeletonGenerator
        from src.remediation.documentation_generator import DocumentationGenerator
        
        wiring_gen = WiringGenerator(self.project_root)
        test_gen = TestSkeletonGenerator(self.project_root)
        doc_gen = DocumentationGenerator(self.project_root)
        
        # Collect features needing remediation
        for name, score in report.feature_scores.items():
            # Get feature metadata
            metadata = orchestrators.get(name) or agents.get(name)
            if not metadata:
                continue
            
            feature_path = metadata.get("file_path", "")
            docstring = metadata.get("docstring")
            methods = metadata.get("methods", [])
            
            # Generate wiring suggestion if not wired
            if not score.wired:
                wiring_suggestion = wiring_gen.generate_wiring_suggestion(
                    feature_name=name,
                    feature_path=feature_path,
                    docstring=docstring
                )
                
                report.remediation_suggestions.append(RemediationSuggestion(
                    feature_name=name,
                    suggestion_type="wiring",
                    content=wiring_suggestion["yaml_template"] + "\n\n" + wiring_suggestion["prompt_section"],
                    file_path=None  # Suggestions shown in report, not saved
                ))
            
            # Generate test skeleton if not tested
            if not score.tested:
                test_skeleton = test_gen.generate_test_skeleton(
                    feature_name=name,
                    feature_path=feature_path,
                    methods=methods
                )
                
                report.remediation_suggestions.append(RemediationSuggestion(
                    feature_name=name,
                    suggestion_type="test",
                    content=test_skeleton["test_code"],
                    file_path=test_skeleton["test_path"]
                ))
            
            # Generate documentation if not documented
            if not score.documented:
                doc_template = doc_gen.generate_documentation_template(
                    feature_name=name,
                    feature_path=feature_path,
                    docstring=docstring,
                    methods=methods
                )
                
                report.remediation_suggestions.append(RemediationSuggestion(
                    feature_name=name,
                    suggestion_type="documentation",
                    content=doc_template["doc_content"],
                    file_path=doc_template["doc_path"]
                ))
    
    def _format_report_summary(self, report: AlignmentReport) -> str:
        """Format alignment report summary for display."""
        lines = []
        
        if report.is_healthy:
            lines.append("✅ System alignment healthy")
        else:
            lines.append(f"⚠️ {report.issues_found} alignment issues detected:")
            
            # Show top 3 issues
            issues = [
                (name, score)
                for name, score in report.feature_scores.items()
                if score.score < 90
            ]
            issues.sort(key=lambda x: x[1].score)
            
            for name, score in issues[:3]:
                lines.append(f"   - {name} ({score.score}% integration - {', '.join(score.issues)})")
            
            if len(issues) > 3:
                lines.append(f"   ... and {len(issues) - 3} more")
            
            # Show remediation suggestion count
            if report.remediation_suggestions:
                lines.append(f"\n💡 Generated {len(report.remediation_suggestions)} auto-remediation suggestions")
            
            lines.append("")
            lines.append("Run 'align report' for details and auto-remediation")
        
        return "\n".join(lines)
    
    def rollback(self, context: Dict[str, Any]) -> bool:
        """No rollback needed for read-only validation."""
        return True
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get orchestrator metadata.
        
        Returns:
            OperationModuleMetadata with module information
        """
        from src.operations.base_operation_module import OperationModuleMetadata, OperationPhase
        
        return OperationModuleMetadata(
            module_id="system_alignment",
            name="System Alignment Validator",
            description="Convention-based system alignment validator",
            phase=OperationPhase.VALIDATION,
            priority=100,
            optional=True,
            author="Asif Hussain",
            tags=["admin", "validation", "alignment"]
        )
