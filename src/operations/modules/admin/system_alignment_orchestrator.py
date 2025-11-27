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
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

from src.operations.base_operation_module import (
    BaseOperationModule,
    OperationPhase,
    OperationStatus,
    OperationResult
)
from src.operations.modules.admin.alignment_models import (
    IntegrationScore,
    RemediationSuggestion,
    AlignmentReport
)
from src.operations.modules.admin.alignment_validators import FullValidationRunner
from src.operations.modules.admin.gap_remediation_validator import GapRemediationValidator
from src.operations.modules.admin.remediation_suggestions_generator import RemediationSuggestionsGenerator
from src.validation.file_organization_validator import FileOrganizationValidator
from src.validation.template_header_validator import TemplateHeaderValidator
from src.validation.conflict_detector import ConflictDetector, Conflict
from src.validation.remediation_engine import RemediationEngine, FixTemplate
from src.validation.dashboard_generator import DashboardGenerator
from src.caching import get_cache
from src.governance import DocumentGovernance
from src.utils.progress_monitor import ProgressMonitor

logger = logging.getLogger(__name__)


class SystemAlignmentOrchestrator(BaseOperationModule):
    """
    Convention-based system alignment validator.
    
    Auto-discovers features and validates integration depth.
    Scoring: discovered(20), imported(40), instantiated(60), documented(70),
    tested(80), wired(90), optimized(100)
    """
    
    def __init__(self, context: Optional[Dict[str, Any]] = None):
        """Initialize system alignment orchestrator."""
        super().__init__()
        self.context = context or {}
        self.project_root = Path(self.context.get("project_root", Path.cwd()))
        self.cortex_brain = self.project_root / "cortex-brain"
        
        # Load configuration
        self.config = self._load_config()
        
        # Discovery components (lazy loaded)
        self._orchestrator_scanner = None
        self._agent_scanner = None
        self._entry_point_scanner = None
        self._documentation_scanner = None
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from cortex.config.json."""
        config_path = self.project_root / "cortex.config.json"
        
        if not config_path.exists():
            logger.warning(f"Config file not found at {config_path}, using defaults")
            return {}
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load config from {config_path}: {e}")
            return {}
    
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
        """Execute system alignment validation."""
        start_time = datetime.now()
        monitor = ProgressMonitor("System Alignment", hang_timeout_seconds=60.0)
        
        try:
            monitor.start()
            monitor.update("Validating brain accessibility")
            
            # Phase 0: Validate brain accessibility
            brain_check = self._validate_brain_accessibility()
            
            if not brain_check['healthy']:
                logger.error(f"❌ Brain validation failed: {', '.join(brain_check['issues'])}")
                monitor.fail("Brain validation failed")
                return OperationResult(
                    success=False,
                    status=OperationStatus.FAILED,
                    message=f"Brain validation failed: {', '.join(brain_check['issues'])}",
                    errors=brain_check['issues'],
                    duration_seconds=(datetime.now() - start_time).total_seconds()
                )
            
            monitor.update("Brain verified, running validation")
            
            # Run full validation with monitoring
            report = self.run_full_validation(monitor)
            
            # Store report in context
            context["alignment_report"] = report
            
            # Phase 6: Align 2.0 - Interactive remediation if requested
            interactive_fix = context.get('interactive_fix', False)
            fixes_applied = []
            
            if interactive_fix and report.fix_templates:
                monitor.update(f"Interactive remediation ({len(report.fix_templates)} fixes available)")
                fixes_applied = self._apply_interactive_fixes(report, monitor)
                
                # Re-run validation to update scores after fixes
                if fixes_applied:
                    monitor.update("Re-validating after fixes")
                    report = self.run_full_validation(monitor)
                    context["alignment_report"] = report
            
            # Phase 6 (legacy): Auto-fix issues if enabled
            auto_fix_enabled = context.get('auto_fix', False)
            legacy_fixes = []
            
            if auto_fix_enabled and report.remediation_suggestions:
                monitor.update(f"Applying {len(report.remediation_suggestions)} auto-fixes")
                legacy_fixes = self._apply_auto_fixes(report, monitor)
                
                # Re-run validation to update scores after fixes
                if legacy_fixes:
                    monitor.update("Re-validating after fixes")
                    report = self.run_full_validation(monitor)
                    context["alignment_report"] = report
                    fixes_applied.extend(legacy_fixes)
            
            # Build result message
            message = self._format_report_summary(report, fixes_applied)
            
            duration = (datetime.now() - start_time).total_seconds()
            monitor.complete()
            
            return OperationResult(
                success=report.is_healthy,
                status=OperationStatus.SUCCESS if report.is_healthy else OperationStatus.WARNING,
                message=message,
                data={"report": report, "fixes_applied": fixes_applied},
                duration_seconds=duration
            )
            
        except KeyboardInterrupt:
            monitor.fail("Cancelled by user")
            duration = (datetime.now() - start_time).total_seconds()
            return OperationResult(
                success=False,
                status=OperationStatus.FAILED,
                message="System alignment cancelled by user",
                errors=["User cancelled operation"],
                duration_seconds=duration
            )
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            logger.error(f"System alignment failed: {e}", exc_info=True)
            monitor.fail(str(e))
            
            return OperationResult(
                success=False,
                status=OperationStatus.FAILED,
                message=f"System alignment validation failed: {str(e)}",
                errors=[str(e)],
                duration_seconds=duration
            )
    
    def run_full_validation(self, monitor: Optional[ProgressMonitor] = None) -> AlignmentReport:
        """Run complete system alignment validation (delegated to FullValidationRunner)."""
        runner = FullValidationRunner(
            self.project_root,
            self.config,
            self._discover_orchestrators,
            self._discover_agents,
            self._validate_entry_points,
            self._calculate_integration_score,
            self._validate_deployment_readiness,
            self._validate_gap_remediation_components,
            self._validate_file_organization,
            self._validate_template_headers,
            self._validate_documentation_governance,
            self._detect_conflicts,
            self._generate_fix_templates,
            self._generate_dashboard,
            self._generate_remediation_suggestions,
            self._is_production_feature,
            self._get_classification,
            self._get_feature_files,
            self._score_to_dict,
            self._dict_to_score
        )
        return runner.run(monitor)
    
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
        
        # For agents, check entry_point_scanner.py mappings
        # For orchestrators, check response template entry points
        if feature_type == "agent":
            # Check if agent is in entry_point_scanner.py mappings
            scanner_path = self.project_root / "src" / "discovery" / "entry_point_scanner.py"
            if scanner_path.exists():
                scanner_content = scanner_path.read_text(encoding='utf-8')
                # Check if agent name appears in the mappings dict
                score.wired = f'"{name}"' in scanner_content or f"'{name}'" in scanner_content
            else:
                score.wired = False
        else:
            # Orchestrators use the original method
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
        name_base = name_base.replace("TDD", "Tdd").replace("API", "Api").replace("HTTP", "Http").replace("EPM", "Epm").replace("ADO", "Ado")
        # Insert hyphen before uppercase letters, then remove leading hyphen if present
        kebab_name = re.sub(r'([A-Z])', r'-\1', name_base).lstrip('-').lower()
        
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
        """Validate Phase 1-4 gap remediation components (delegated to GapRemediationValidator)."""
        validator = GapRemediationValidator(self.project_root)
        validator.validate(report)
    
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
        Validate response template headers for v3.2 format compliance.
        
        Enforces:
        - Brain emoji (🧠) in all titles: "# 🧠 CORTEX [Title]"
        - Section icons: 🎯 Understanding | ⚠️ Challenge | 💬 Response | 📝 Request | 🔍 Next Steps
        - Author & GitHub attribution
        - NO old format: "✓ Accept" or "⚡ Challenge" in headers
        
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
    
    def _validate_documentation_governance(self) -> Dict[str, Any]:
        """Validate documentation governance (delegated to GapRemediationValidator)."""
        from src.operations.modules.admin.documentation_governance_validator import DocumentationGovernanceValidator
        validator = DocumentationGovernanceValidator(self.project_root, self.context)
        return validator.validate()
    
    def _generate_remediation_suggestions(
        self,
        report: AlignmentReport,
        orchestrators: Dict[str, Dict[str, Any]],
        agents: Dict[str, Dict[str, Any]]
    ) -> None:
        """Generate auto-remediation suggestions (delegated to RemediationSuggestionsGenerator)."""
        generator = RemediationSuggestionsGenerator(self.project_root)
        generator.generate(report, orchestrators, agents)
    
    def _apply_auto_fixes(self, report: AlignmentReport, monitor: Optional[ProgressMonitor] = None) -> List[Dict[str, Any]]:
        """Apply auto-remediation fixes to features."""
        fixes_applied = []
        
        for suggestion in report.remediation_suggestions:
            fix_result = {
                'feature_name': suggestion.feature_name,
                'type': suggestion.suggestion_type,
                'success': False,
                'message': ''
            }
            
            try:
                if suggestion.suggestion_type == 'wiring':
                    # Apply wiring fix: add template to response-templates.yaml
                    fix_result['success'] = self._apply_wiring_fix(suggestion)
                    fix_result['message'] = 'Template added to response-templates.yaml'
                
                elif suggestion.suggestion_type == 'test':
                    # Apply test fix: create test skeleton file
                    fix_result['success'] = self._apply_test_fix(suggestion)
                    fix_result['message'] = 'Test skeleton created'
                
                elif suggestion.suggestion_type == 'documentation':
                    # Apply documentation fix: create guide file
                    fix_result['success'] = self._apply_documentation_fix(suggestion)
                    fix_result['message'] = 'Documentation guide created'
                
                else:
                    fix_result['message'] = f'Unknown fix type: {suggestion.suggestion_type}'
                
                if monitor and fix_result['success']:
                    monitor.update(f"Applied {suggestion.suggestion_type} fix for {suggestion.feature_name}")
                
            except Exception as e:
                fix_result['message'] = f'Error: {str(e)}'
                logger.error(f"Failed to apply {suggestion.suggestion_type} fix for {suggestion.feature_name}: {e}")
            
            fixes_applied.append(fix_result)
        
        return fixes_applied
    
    def _apply_wiring_fix(self, suggestion: RemediationSuggestion) -> bool:
        """Apply wiring fix by adding template to response-templates.yaml."""
        try:
            templates_file = self.project_root / "cortex-brain" / "response-templates.yaml"
            
            if not templates_file.exists():
                logger.error(f"response-templates.yaml not found at {templates_file}")
                return False
            
            # Read current content
            with open(templates_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Append template (suggestion.content contains the full YAML template)
            with open(templates_file, 'a', encoding='utf-8') as f:
                f.write('\n# Auto-generated template\n')
                f.write(suggestion.content)
                f.write('\n')
            
            return True
        except Exception as e:
            logger.error(f"Failed to apply wiring fix: {e}")
            return False
    
    def _apply_test_fix(self, suggestion: RemediationSuggestion) -> bool:
        """Apply test fix by creating test skeleton file."""
        try:
            if not suggestion.file_path:
                return False
            
            test_file = Path(suggestion.file_path)
            test_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Write test skeleton (suggestion.content contains the full test code)
            with open(test_file, 'w', encoding='utf-8') as f:
                f.write(suggestion.content)
            
            return True
        except Exception as e:
            logger.error(f"Failed to apply test fix: {e}")
            return False
    
    def _apply_documentation_fix(self, suggestion: RemediationSuggestion) -> bool:
        """Apply documentation fix by creating guide file."""
        try:
            if not suggestion.file_path:
                return False
            
            doc_file = Path(suggestion.file_path)
            doc_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Write documentation (suggestion.content contains the full guide)
            with open(doc_file, 'w', encoding='utf-8') as f:
                f.write(suggestion.content)
            
            return True
        except Exception as e:
            logger.error(f"Failed to apply documentation fix: {e}")
            return False
    
    def _format_report_summary(self, report: AlignmentReport, fixes_applied: List[Dict[str, Any]] = None) -> str:
        """Format alignment report summary for display."""
        lines = []
        
        # Align 2.0: Show dashboard if available
        if report.dashboard_report:
            return report.dashboard_report
        
        # Legacy format (fallback)
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
            
            # Show conflict summary (Align 2.0)
            if report.conflicts:
                critical_conflicts = [c for c in report.conflicts if c.severity == 'critical']
                warning_conflicts = [c for c in report.conflicts if c.severity == 'warning']
                
                lines.append(f"\n[INFO] Detected {len(report.conflicts)} ecosystem conflicts:")
                if critical_conflicts:
                    lines.append(f"   ❌ Critical: {len(critical_conflicts)}")
                if warning_conflicts:
                    lines.append(f"   ⚠️  Warning: {len(warning_conflicts)}")
            
            # Show auto-fix results if any
            if fixes_applied:
                lines.append(f"\n[INFO] Applied {len(fixes_applied)} fixes:")
                for fix in (fixes_applied[:5] if isinstance(fixes_applied[0], dict) else fixes_applied[:5]):
                    if isinstance(fix, dict):
                        status = "✅" if fix['success'] else "❌"
                        lines.append(f"   {status} {fix['type']}: {fix['feature_name']}")
                    else:
                        lines.append(f"   ✅ {fix}")
                if len(fixes_applied) > 5:
                    lines.append(f"   ... and {len(fixes_applied) - 5} more")
            
            # Show remediation suggestion count
            if report.fix_templates:
                auto_fixable = [t for t in report.fix_templates if t.risk_level == 'low']
                lines.append(f"\n[INFO] Generated {len(report.fix_templates)} fix templates ({len(auto_fixable)} low-risk)")
            
            if report.remediation_suggestions:
                lines.append(f"[INFO] Generated {len(report.remediation_suggestions)} legacy remediation suggestions")
            
            lines.append("")
            lines.append("Run 'align report' for detailed dashboard with trends and recommendations")
            lines.append("Run 'align fix --interactive' to apply fixes with confirmation")
        
        return "\n".join(lines)
    
    def _validate_brain_accessibility(self) -> Dict[str, Any]:
        """Validate brain databases are accessible and healthy."""
        issues = []
        
        # Check Tier 1 database
        tier1_db = self.cortex_brain / "tier1" / "working_memory.db"
        if not tier1_db.exists():
            issues.append("Tier 1 database not found")
        else:
            try:
                import sqlite3
                conn = sqlite3.connect(str(tier1_db))
                cursor = conn.cursor()
                cursor.execute("PRAGMA integrity_check")
                result = cursor.fetchone()[0]
                conn.close()
                
                if result != 'ok':
                    issues.append("Tier 1 database integrity check failed")
            except Exception as e:
                issues.append(f"Tier 1 database error: {str(e)}")
        
        # Check Tier 2 database
        tier2_db = self.cortex_brain / "tier2" / "knowledge_graph.db"
        if not tier2_db.exists():
            issues.append("Tier 2 database not found")
        else:
            try:
                import sqlite3
                conn = sqlite3.connect(str(tier2_db))
                cursor = conn.cursor()
                cursor.execute("PRAGMA integrity_check")
                result = cursor.fetchone()[0]
                conn.close()
                
                if result != 'ok':
                    issues.append("Tier 2 database integrity check failed")
            except Exception as e:
                issues.append(f"Tier 2 database error: {str(e)}")
        
        # Check brain protection rules
        brain_rules = self.cortex_brain / "brain-protection-rules.yaml"
        if not brain_rules.exists():
            issues.append("Brain protection rules not found")
        
        return {
            'healthy': len(issues) == 0,
            'issues': issues
        }
    
    def rollback(self, context: Dict[str, Any]) -> bool:
        """No rollback needed for read-only validation."""
        return True
    
    def _is_production_feature(
        self,
        feature_name: str,
        orchestrators: Dict[str, Dict[str, Any]],
        agents: Dict[str, Dict[str, Any]]
    ) -> bool:
        """Check if feature is production (user-facing)."""
        classification = self._get_classification(feature_name, orchestrators, agents)
        return classification == "production"
    
    def _get_classification(
        self,
        feature_name: str,
        orchestrators: Dict[str, Dict[str, Any]],
        agents: Dict[str, Dict[str, Any]]
    ) -> str:
        """Get feature classification."""
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
    
    def _get_feature_files(self, feature_name: str, metadata: Dict[str, Any]) -> List[Path]:
        """
        Get list of files to track for cache invalidation.
        
        Args:
            feature_name: Feature name
            metadata: Feature metadata with file paths
        
        Returns:
            List of Paths to track for this feature
        """
        files = []
        
        # Add main implementation file
        if 'file_path' in metadata:
            file_path = Path(metadata['file_path'])
            if file_path.exists():
                files.append(file_path)
        
        # Add test file if exists
        test_path = self.project_root / 'tests' / f'test_{feature_name}.py'
        if test_path.exists():
            files.append(test_path)
        
        # Add module guide if exists
        guide_path = self.project_root / '.github' / 'prompts' / 'modules' / f'{feature_name}-guide.md'
        if guide_path.exists():
            files.append(guide_path)
        
        return files
    
    def _score_to_dict(self, score: IntegrationScore) -> Dict[str, Any]:
        """Convert IntegrationScore dataclass to dict for cache serialization."""
        return {
            'feature_name': score.feature_name,
            'feature_type': score.feature_type,
            'discovered': score.discovered,
            'imported': score.imported,
            'instantiated': score.instantiated,
            'documented': score.documented,
            'tested': score.tested,
            'wired': score.wired,
            'optimized': score.optimized
        }
    
    def _dict_to_score(self, data: Dict[str, Any]) -> IntegrationScore:
        """Convert dict back to IntegrationScore dataclass."""
        return IntegrationScore(
            feature_name=data['feature_name'],
            feature_type=data['feature_type'],
            discovered=data['discovered'],
            imported=data['imported'],
            instantiated=data['instantiated'],
            documented=data['documented'],
            tested=data['tested'],
            wired=data['wired'],
            optimized=data['optimized']
        )
    
    def _detect_conflicts(self) -> List[Conflict]:
        """
        Detect internal CORTEX ecosystem conflicts.
        
        Phase 3.10: Align 2.0 enhancement
        
        Returns:
            List of detected conflicts
        """
        logger.info("Running conflict detection...")
        
        detector = ConflictDetector(self.project_root)
        conflicts = detector.detect_all_conflicts()
        
        logger.info(f"Found {len(conflicts)} conflicts")
        return conflicts
    
    def _generate_fix_templates(self, conflicts: List[Conflict]) -> List[FixTemplate]:
        """
        Generate fix templates for conflicts.
        
        Phase 3.11: Align 2.0 enhancement
        
        Args:
            conflicts: List of detected conflicts
            
        Returns:
            List of fix templates
        """
        logger.info("Generating fix templates...")
        
        engine = RemediationEngine(self.project_root)
        templates = []
        
        for conflict in conflicts:
            template = engine.generate_fix_template(conflict)
            if template:
                templates.append(template)
        
        logger.info(f"Generated {len(templates)} fix templates")
        return templates
    
    def _generate_dashboard(self, report: AlignmentReport, conflicts: List[Conflict]) -> str:
        """
        Generate visual health dashboard.
        
        Phase 3.12: Align 2.0 enhancement
        
        Args:
            report: Alignment report
            conflicts: List of conflicts
            
        Returns:
            Formatted dashboard string
        """
        logger.info("Generating health dashboard...")
        
        generator = DashboardGenerator(self.project_root)
        dashboard = generator.generate_dashboard(report, conflicts)
        
        # Save to history
        generator.save_history(report)
        
        return dashboard
    
    def _apply_interactive_fixes(self, report: AlignmentReport, monitor: Optional[ProgressMonitor]) -> List[str]:
        """
        Apply fixes interactively with user confirmation.
        
        Align 2.0: Smart remediation with consent
        
        Args:
            report: Alignment report with fix templates
            monitor: Progress monitor
            
        Returns:
            List of applied fix descriptions
        """
        logger.info("Starting interactive remediation...")
        
        engine = RemediationEngine(self.project_root)
        applied_fixes = []
        
        # Create checkpoint before any fixes
        print("\n🔒 Creating safety checkpoint...")
        if not engine.create_checkpoint():
            logger.error("Failed to create checkpoint - aborting remediation")
            return []
        
        # Present fixes one by one
        for idx, fix_template in enumerate(report.fix_templates, 1):
            print(f"\n\n{'='*80}")
            print(f"FIX {idx}/{len(report.fix_templates)}")
            print(f"{'='*80}")
            
            # Show preview and request confirmation
            if engine.request_confirmation(fix_template):
                success = engine.apply_fix(fix_template)
                
                if success:
                    applied_fixes.append(fix_template.description)
                    logger.info(f"✅ Fix applied: {fix_template.description}")
                else:
                    logger.error(f"❌ Fix failed: {fix_template.description}")
                    response = input("Continue with remaining fixes? [y/N]: ").strip().lower()
                    if response != 'y':
                        logger.info("Remediation stopped by user")
                        break
            else:
                logger.info(f"⏭️ Skipped: {fix_template.description}")
        
        if applied_fixes:
            print(f"\n\n✅ Applied {len(applied_fixes)} fixes successfully")
            print(f"🔒 Checkpoint available for rollback: git reset --hard {engine.checkpoint_sha[:8]}")
        else:
            print("\n\nℹ️ No fixes applied")
        
        return applied_fixes
