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
from src.validation.file_organization_validator import FileOrganizationValidator
from src.validation.template_header_validator import TemplateHeaderValidator

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
        """Get status text based on score."""
        score = self.score
        if score >= 90:
            return "[OK] Healthy"
        elif score >= 70:
            return "[WARN] Warning"
        else:
            return "[CRIT] Critical"
    
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
    # New validation fields
    organization_violations: List[Any] = field(default_factory=list)  # File organization issues
    organization_score: int = 100  # 0-100% file organization compliance
    header_violations: List[Any] = field(default_factory=list)  # Template header issues
    header_compliance_score: int = 100  # 0-100% template header compliance
    
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
        
        # Phase 3: REMOVED - Documentation validation now done in _calculate_integration_score()
        # Old _validate_documentation() used incorrect logic (checking CORTEX.prompt.md mentions)
        # New logic checks both docstrings AND guide files correctly
        
        # Phase 3.5: Validate deployment readiness (quality gates + package purity)
        self._validate_deployment_readiness(report)
        
        # Phase 3.6: Validate Phase 1-4 gap remediation components
        self._validate_gap_remediation_components(report)
        
        # Phase 3.7: Validate file organization (CORTEX boundary)
        org_results = self._validate_file_organization()
        report.organization_violations = org_results.get('violations', [])
        report.organization_score = org_results.get('score', 100)
        
        # Phase 3.8: Validate template headers (legal compliance)
        header_results = self._validate_template_headers()
        report.header_violations = header_results.get('violations', [])
        report.header_compliance_score = header_results.get('score', 100)
        
        # Phase 4: Generate auto-remediation suggestions
        self._generate_remediation_suggestions(report, orchestrators, agents)
        
        # Calculate overall health (production features only for deployment threshold)
        if report.feature_scores:
            production_scores = [
                s for s in report.feature_scores.values()
                if self._is_production_feature(s.feature_name, orchestrators, agents)
            ]
            
            if production_scores:
                # Production health (used for deployment gates)
                total_score = sum(s.score for s in production_scores)
                report.overall_health = total_score // len(production_scores)
                
                # Log classification breakdown
                admin_count = sum(1 for s in report.feature_scores.values() 
                                 if self._get_classification(s.feature_name, orchestrators, agents) == "admin")
                internal_count = sum(1 for s in report.feature_scores.values() 
                                    if self._get_classification(s.feature_name, orchestrators, agents) == "internal")
                production_count = len(production_scores)
                
                logger.info(f"Feature classification: {production_count} production, {admin_count} admin, {internal_count} internal")
            else:
                report.overall_health = 100  # No production features = healthy
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
        
        # Layer 4: Documentation validation (check both docstring AND guide file)
        has_docstring = metadata.get("has_docstring", False)
        has_guide = self._check_guide_file_exists(name, feature_type)
        score.documented = has_docstring and has_guide
        
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
        
        # Layer 7: Performance validation (check for benchmark files)
        if module_path and class_name:
            from src.validation.integration_scorer import IntegrationScorer
            perf_scorer = IntegrationScorer(self.project_root)
            score.optimized = perf_scorer.validate_performance(module_path, class_name)
        else:
            score.optimized = False
        
        return score
    
    def _check_guide_file_exists(self, feature_name: str, feature_type: str) -> bool:
        """
        Check if guide file exists for a feature.
        
        Args:
            feature_name: Name of the feature (e.g., 'TDDWorkflowOrchestrator')
            feature_type: Type of feature ('orchestrator', 'agent', etc.)
        
        Returns:
            bool: True if guide file exists, False otherwise
        """
        # Convert feature name to guide filename format
        # TDDWorkflowOrchestrator -> tdd-workflow-orchestrator-guide.md
        # GitCheckpointOrchestrator -> git-checkpoint-orchestrator-guide.md
        
        # Remove common suffixes
        name_base = feature_name.replace("Orchestrator", "").replace("Agent", "").replace("Module", "")
        
        # Convert CamelCase to kebab-case (handle acronyms specially)
        import re
        # First, handle common acronyms by converting them to lowercase
        name_base = name_base.replace("TDD", "Tdd").replace("API", "Api").replace("HTTP", "Http")
        kebab_name = re.sub(r'(?<!^)(?=[A-Z])', '-', name_base).lower()
        
        # Construct guide filename
        guide_name = f"{kebab_name}-{feature_type}-guide.md"
        guide_path = self.project_root / ".github" / "prompts" / "modules" / guide_name
        
        exists = guide_path.exists()
        
        # Check if it's not just a stub (has substantial content)
        if exists:
            try:
                content = guide_path.read_text(encoding='utf-8')
                # Consider it documented if it has more than 1000 characters and isn't mostly placeholders
                is_substantial = len(content) > 1000 and '[Feature 1]' not in content
                return is_substantial
            except Exception:
                return False
        
        return False
    
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
    
    def _validate_gap_remediation_components(self, report: AlignmentReport) -> None:
        """
        Phase 3.6: Validate Phase 1-4 gap remediation components.
        
        Validates:
        - GitHub Actions workflows (feedback-aggregation.yml)
        - Template format compliance (H1 headers, Challenge field)
        - Brain protection rule severity (NO_ROOT_FILES blocked enforcement)
        - Configuration schemas (plan-schema.yaml, lint-rules.yaml)
        
        Args:
            report: AlignmentReport to populate with gap remediation validation results
        """
        # 1. Validate GitHub Actions workflows
        workflows_path = self.project_root / ".github" / "workflows"
        feedback_workflow = workflows_path / "feedback-aggregation.yml"
        
        if not feedback_workflow.exists():
            report.critical_issues += 1
            report.suggestions.append({
                "type": "missing_workflow",
                "message": "Missing feedback-aggregation.yml workflow (Gap #7 - Feedback Automation)"
            })
        else:
            # Validate workflow structure
            try:
                import yaml
                with open(feedback_workflow, "r", encoding="utf-8") as f:
                    workflow_content = yaml.safe_load(f)
                    
                if "schedule" not in workflow_content.get("on", {}):
                    report.warnings += 1
                    report.suggestions.append({
                        "type": "workflow_config",
                        "message": "feedback-aggregation.yml missing schedule trigger"
                    })
            except Exception as e:
                report.warnings += 1
                report.suggestions.append({
                    "type": "workflow_parse",
                    "message": f"Failed to parse feedback-aggregation.yml: {e}"
                })
        
        # 2. Validate template format compliance
        templates_path = self.project_root / "cortex-brain" / "response-templates.yaml"
        
        if not templates_path.exists():
            report.critical_issues += 1
            report.suggestions.append({
                "type": "missing_templates",
                "message": "Missing cortex-brain/response-templates.yaml"
            })
        else:
            try:
                import yaml
                with open(templates_path, "r", encoding="utf-8") as f:
                    templates = yaml.safe_load(f)
                
                # Check for H1 header format (# 🧠 CORTEX)
                template_issues = []
                for template_name, template_data in templates.get("templates", {}).items():
                    content = template_data.get("content", "")
                    
                    # Validate H1 header
                    if not content.startswith("# ") and not content.startswith("##"):
                        template_issues.append(f"{template_name}: Missing H1 header")
                    
                    # Validate Challenge field format
                    if "Challenge:" in content and "[✓ Accept OR ⚡ Challenge]" in content:
                        template_issues.append(f"{template_name}: Old Challenge format detected")
                
                if template_issues:
                    report.warnings += len(template_issues)
                    for issue in template_issues[:3]:  # Show first 3
                        report.suggestions.append({
                            "type": "template_format",
                            "message": f"Template format issue: {issue}"
                        })
                    
                    if len(template_issues) > 3:
                        report.suggestions.append({
                            "type": "template_format",
                            "message": f"...and {len(template_issues) - 3} more template format issues"
                        })
            
            except Exception as e:
                report.warnings += 1
                report.suggestions.append({
                    "type": "template_parse",
                    "message": f"Failed to parse response-templates.yaml: {e}"
                })
        
        # 3. Validate brain protection rule severity
        brain_rules_path = self.project_root / "cortex-brain" / "brain-protection-rules.yaml"
        
        if not brain_rules_path.exists():
            report.critical_issues += 1
            report.suggestions.append({
                "type": "missing_brain_rules",
                "message": "Missing cortex-brain/brain-protection-rules.yaml"
            })
        else:
            try:
                import yaml
                with open(brain_rules_path, "r", encoding="utf-8") as f:
                    brain_rules = yaml.safe_load(f)
                
                # Check NO_ROOT_FILES protection level
                layers = brain_rules.get("layers", {})
                layer_8 = layers.get("layer_8_document_organization", {})
                rules = layer_8.get("rules", [])
                
                no_root_files_rule = next(
                    (r for r in rules if r.get("id") == "NO_ROOT_FILES"),
                    None
                )
                
                if no_root_files_rule:
                    severity = no_root_files_rule.get("severity")
                    if severity != "blocked":
                        report.warnings += 1
                        report.suggestions.append({
                            "type": "brain_protection",
                            "message": f"NO_ROOT_FILES protection is '{severity}', should be 'blocked' (Gap #5 strengthening)"
                        })
                else:
                    report.warnings += 1
                    report.suggestions.append({
                        "type": "brain_protection",
                        "message": "NO_ROOT_FILES protection rule not found in Layer 8"
                    })
                
                # Verify DOCUMENT_ORGANIZATION_ENFORCEMENT in Tier 0 instincts
                tier0_instincts = brain_rules.get("tier0_instincts", [])
                if "DOCUMENT_ORGANIZATION_ENFORCEMENT" not in tier0_instincts:
                    report.warnings += 1
                    report.suggestions.append({
                        "type": "brain_protection",
                        "message": "DOCUMENT_ORGANIZATION_ENFORCEMENT missing from Tier 0 instincts"
                    })
            
            except Exception as e:
                report.warnings += 1
                report.suggestions.append({
                    "type": "brain_rules_parse",
                    "message": f"Failed to parse brain-protection-rules.yaml: {e}"
                })
        
        # 4. Validate configuration schemas
        config_path = self.project_root / "cortex-brain" / "config"
        plan_schema = config_path / "plan-schema.yaml"
        lint_rules = config_path / "lint-rules.yaml"
        
        if not plan_schema.exists():
            report.warnings += 1
            report.suggestions.append({
                "type": "missing_schema",
                "message": "Missing cortex-brain/config/plan-schema.yaml (Gap #4 - Planning System)"
            })
        
        if not lint_rules.exists():
            report.warnings += 1
            report.suggestions.append({
                "type": "missing_config",
                "message": "Missing cortex-brain/config/lint-rules.yaml (Gap #3 - Lint Validation)"
            })
        
        # 5. Validate orchestrator presence (auto-discovered, but check key ones)
        expected_orchestrators = [
            "GitCheckpointOrchestrator",
            "MetricsTracker",
            "LintValidationOrchestrator",
            "SessionCompletionOrchestrator",
            "PlanningOrchestrator",
            "UpgradeOrchestrator"
        ]
        
        discovered_names = {score.feature_name for score in report.feature_scores.values()}
        missing_orchestrators = [name for name in expected_orchestrators if name not in discovered_names]
        
        if missing_orchestrators:
            report.critical_issues += len(missing_orchestrators)
            for name in missing_orchestrators:
                report.suggestions.append({
                    "type": "missing_orchestrator",
                    "message": f"Gap remediation orchestrator not discovered: {name}"
                })
        
        # 6. Validate feedback aggregator
        feedback_aggregator_path = self.project_root / "src" / "feedback" / "feedback_aggregator.py"
        
        if not feedback_aggregator_path.exists():
            report.critical_issues += 1
            report.suggestions.append({
                "type": "missing_module",
                "message": "Missing src/feedback/feedback_aggregator.py (Gap #7 - Feedback Automation)"
            })
    
    def _validate_file_organization(self) -> Dict[str, Any]:
        """
        Validate file organization and CORTEX boundary.
        
        Returns:
            Dict with validation results and violations
        """
        try:
            validator = FileOrganizationValidator(self.project_root)
            results = validator.validate()
            
            # Add remediation templates
            results['remediation_templates'] = validator.generate_remediation_templates()
            
            logger.info(f"File organization: {results['score']:.1f}% ({results['critical_count']} critical, {results['warning_count']} warnings)")
            return results
            
        except Exception as e:
            logger.error(f"File organization validation failed: {e}")
            return {
                'score': 0,
                'status': 'error',
                'violations': [],
                'critical_count': 0,
                'warning_count': 0,
                'remediation_templates': []
            }
    
    def _validate_template_headers(self) -> Dict[str, Any]:
        """
        Validate response template headers for legal compliance.
        
        Returns:
            Dict with validation results and violations
        """
        try:
            templates_path = self.project_root / "cortex-brain" / "response-templates.yaml"
            if not templates_path.exists():
                logger.warning(f"Templates file not found: {templates_path}")
                return {
                    'score': 0,
                    'status': 'not_found',
                    'violations': [],
                    'critical_count': 0,
                    'warning_count': 0,
                    'remediation_templates': []
                }
            
            validator = TemplateHeaderValidator(templates_path)
            results = validator.validate()
            
            # Add remediation templates
            results['remediation_templates'] = validator.generate_remediation_templates()
            
            logger.info(f"Template headers: {results['score']:.1f}% compliant ({results['compliant_templates']}/{results['total_templates']})")
            return results
            
        except Exception as e:
            logger.error(f"Template header validation failed: {e}")
            return {
                'score': 0,
                'status': 'error',
                'violations': [],
                'critical_count': 0,
                'warning_count': 0,
                'remediation_templates': []
            }
    
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
        
        # Add file organization remediation suggestions
        if hasattr(report, 'organization_violations'):
            org_validator = FileOrganizationValidator(self.project_root)
            org_validator.violations = report.organization_violations
            org_templates = org_validator.generate_remediation_templates()
            
            for template in org_templates:
                report.remediation_suggestions.append(RemediationSuggestion(
                    feature_name="File Organization",
                    suggestion_type="organization",
                    content=f"{template['description']}\n\nCommand: {template.get('command', 'N/A')}",
                    file_path=template.get('destination')
                ))
        
        # Add template header remediation suggestions
        if hasattr(report, 'header_violations'):
            templates_path = self.project_root / "cortex-brain" / "response-templates.yaml"
            header_validator = TemplateHeaderValidator(templates_path)
            header_validator.violations = report.header_violations
            header_templates = header_validator.generate_remediation_templates()
            
            for template in header_templates:
                report.remediation_suggestions.append(RemediationSuggestion(
                    feature_name=template['template_name'],
                    suggestion_type="header_compliance",
                    content=f"{template['description']}\n\n{template.get('header_content', '')}",
                    file_path=None
                ))
    
    def _format_report_summary(self, report: AlignmentReport) -> str:
        """Format alignment report summary for display."""
        lines = []
        
        if report.is_healthy:
            lines.append("[OK] System alignment healthy")
        else:
            lines.append(f"[WARN] {report.issues_found} alignment issues detected:")
            
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
                lines.append(f"\n[INFO] Generated {len(report.remediation_suggestions)} auto-remediation suggestions")
            
            lines.append("")
            lines.append("Run 'align report' for details and auto-remediation")
        
        return "\n".join(lines)
    
    def rollback(self, context: Dict[str, Any]) -> bool:
        """No rollback needed for read-only validation."""
        return True
    
    def _is_production_feature(
        self,
        feature_name: str,
        orchestrators: Dict[str, Dict[str, Any]],
        agents: Dict[str, Dict[str, Any]]
    ) -> bool:
        """
        Check if feature is production (user-facing).
        
        Args:
            feature_name: Feature name
            orchestrators: Discovered orchestrators
            agents: Discovered agents
        
        Returns:
            True if feature is production
        """
        classification = self._get_classification(feature_name, orchestrators, agents)
        return classification == "production"
    
    def _get_classification(
        self,
        feature_name: str,
        orchestrators: Dict[str, Dict[str, Any]],
        agents: Dict[str, Dict[str, Any]]
    ) -> str:
        """
        Get feature classification.
        
        Args:
            feature_name: Feature name
            orchestrators: Discovered orchestrators
            agents: Discovered agents
        
        Returns:
            Classification: 'production', 'admin', or 'internal'
        """
        # Check orchestrators
        if feature_name in orchestrators:
            return orchestrators[feature_name].get("classification", "production")
        
        # Check agents
        if feature_name in agents:
            return agents[feature_name].get("classification", "production")
        
        # Default
        return "production"
    
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
