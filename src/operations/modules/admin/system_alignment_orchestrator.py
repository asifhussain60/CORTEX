"""
System Alignment Orchestrator - Convention-Based Discovery & Validation

Auto-discovers and validates all CORTEX enhancements without hardcoded lists.
Admin-only feature that integrates with optimize command for continuous monitoring.

Design Philosophy:
    - Convention Over Configuration
    - Zero maintenance when adding features
    - Self-healing architecture
    - Admin-only execution

Enhancement Catalog Integration:
    - Tracks features discovered since last alignment
    - Reports new features with temporal awareness
    - Updates catalog with acceptance status

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Version: 1.1
Status: IMPLEMENTATION
"""

import logging
import json
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
from src.validation.conflict_detector import ConflictDetector, Conflict
from src.validation.remediation_engine import RemediationEngine, FixTemplate
from src.validation.dashboard_generator import DashboardGenerator
from src.caching import get_cache
from src.governance import DocumentGovernance
from src.utils.progress_monitor import ProgressMonitor

# Import enhancement catalog for temporal feature tracking
from src.utils.enhancement_catalog import EnhancementCatalog, FeatureType, AcceptanceStatus
from src.discovery.enhancement_discovery import EnhancementDiscoveryEngine

# Import centralized config for cross-platform path resolution
from src.config import config

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
    # Document governance fields
    doc_governance_violations: List[Any] = field(default_factory=list)  # Duplicate/overlapping docs
    doc_governance_score: int = 100  # 0-100% documentation governance compliance
    # Align 2.0 enhancements
    conflicts: List[Conflict] = field(default_factory=list)  # Detected ecosystem conflicts
    fix_templates: List[FixTemplate] = field(default_factory=list)  # Generated fix templates
    dashboard_report: Optional[str] = None  # Visual dashboard HTML/text
    # Enhancement Catalog integration (NEW)
    catalog_features_total: int = 0  # Total features in catalog
    catalog_features_new: int = 0  # New features since last review
    catalog_days_since_review: Optional[int] = None  # Days since last alignment
    catalog_new_features: List[Dict[str, Any]] = field(default_factory=list)  # Details of new features
    catalog_features_total: int = 0  # Total features in catalog
    catalog_features_new: int = 0  # New features since last alignment
    catalog_days_since_review: Optional[int] = None  # Days since last catalog review
    catalog_new_features: List[Dict[str, Any]] = field(default_factory=list)  # New feature details
    
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
        
        # Use centralized config for cross-platform path resolution
        self.project_root = config.root_path
        self.cortex_brain = config.brain_path
        
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
        """
        Execute system alignment validation.
        
        Returns:
            OperationResult with alignment report
        """
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
        """
        Run complete system alignment validation.
        
        Args:
            monitor: Optional progress monitor for user feedback
            
        Returns:
            AlignmentReport with all validation results
        """
        cache = get_cache()
        
        report = AlignmentReport(
            timestamp=datetime.now(),
            overall_health=0
        )
        
        # Phase 0.5: Enhancement Catalog Review (NEW)
        if monitor:
            monitor.update("Reviewing CORTEX enhancement catalog")
        
        catalog_info = self._review_enhancement_catalog()
        report.catalog_features_total = catalog_info['total_count']
        report.catalog_features_new = catalog_info['new_count']
        report.catalog_days_since_review = catalog_info.get('days_since_review')
        report.catalog_new_features = catalog_info.get('new_features', [])
        
        if catalog_info['new_count'] > 0:
            logger.info(f"📊 Enhancement Catalog: {catalog_info['new_count']} new features since last alignment")
        
        # Phase 1: Discover all features (with caching)
        if monitor:
            monitor.update("Discovering orchestrators and agents")
        
        operations_dir = self.project_root / 'src' / 'operations'
        agents_dir = self.project_root / 'src' / 'agents'
        
        # Try cache for orchestrators
        orchestrators = cache.get('align', 'orchestrators', [operations_dir])
        if orchestrators is None:
            logger.info("Cache MISS: orchestrators - running discovery")
            orchestrators = self._discover_orchestrators()
            cache.set('align', 'orchestrators', orchestrators, [operations_dir], ttl_seconds=0)
        else:
            logger.info("Cache HIT: orchestrators - using cached discovery")
        
        # Try cache for agents
        agents = cache.get('align', 'agents', [agents_dir])
        if agents is None:
            logger.info("Cache MISS: agents - running discovery")
            agents = self._discover_agents()
            cache.set('align', 'agents', agents, [agents_dir], ttl_seconds=0)
        else:
            logger.info("Cache HIT: agents - using cached discovery")
        
        # Phase 1.5: Discover entry points and validate wiring
        if monitor:
            monitor.update("Validating entry point wiring")
        orphaned, ghost = self._validate_entry_points(orchestrators)
        report.orphaned_triggers = orphaned
        report.ghost_features = ghost
        
        # Phase 2: Validate integration depth (with caching)
        total_features = len(orchestrators) + len(agents.get('agents', {}))
        current_idx = 0
        
        for name, metadata in orchestrators.items():
            current_idx += 1
            if monitor:
                monitor.update(f"Scoring integrations", current_idx, total_features)
            
            # Get feature files for cache tracking
            feature_files = self._get_feature_files(name, metadata)
            
            # Try cache for integration score
            cache_key = f'integration_score:{name}'
            score = cache.get('align', cache_key, feature_files)
            
            if score is None:
                logger.debug(f"Cache MISS: {cache_key} - calculating score")
                score = self._calculate_integration_score(name, metadata, "orchestrator")
                # Convert dataclass to dict for JSON serialization
                cache.set('align', cache_key, self._score_to_dict(score), feature_files, ttl_seconds=0)
            else:
                logger.debug(f"Cache HIT: {cache_key} - using cached score")
                score = self._dict_to_score(score)
            
            report.feature_scores[name] = score
            
            # Categorize issues
            if score.score < 70:
                report.critical_issues += 1
            elif score.score < 90:
                report.warnings += 1
        
        for name, metadata in agents.items():
            current_idx += 1
            if monitor:
                monitor.update(f"Scoring integrations", current_idx, total_features)
            
            feature_files = self._get_feature_files(name, metadata)
            cache_key = f'integration_score:{name}'
            
            score = cache.get('align', cache_key, feature_files)
            if score is None:
                logger.debug(f"Cache MISS: {cache_key} - calculating score")
                score = self._calculate_integration_score(name, metadata, "agent")
                cache.set('align', cache_key, self._score_to_dict(score), feature_files, ttl_seconds=0)
            else:
                logger.debug(f"Cache HIT: {cache_key} - using cached score")
                score = self._dict_to_score(score)
            
            report.feature_scores[name] = score
            
            if score.score < 70:
                report.critical_issues += 1
            elif score.score < 90:
                report.warnings += 1
        
        # Share integration scores with deploy operation
        cache.share_result('align', 'deploy', 'orchestrators')
        cache.share_result('align', 'deploy', 'agents')
        for name in list(orchestrators.keys()) + list(agents.keys()):
            cache.share_result('align', 'deploy', f'integration_score:{name}')
        
        # Phase 3: REMOVED - Documentation validation now done in _calculate_integration_score()
        # Old _validate_documentation() used incorrect logic (checking CORTEX.prompt.md mentions)
        # New logic checks both docstrings AND guide files correctly
        
        # Phase 3.5: Validate deployment readiness (quality gates + package purity)
        if monitor:
            monitor.update("Validating deployment readiness")
        self._validate_deployment_readiness(report)
        
        # Phase 3.6: Validate Phase 1-4 gap remediation components
        if monitor:
            monitor.update("Validating gap remediation")
        self._validate_gap_remediation_components(report)
        
        # Phase 3.7: Validate file organization (CORTEX boundary)
        if monitor:
            monitor.update("Validating file organization")
        org_results = self._validate_file_organization()
        report.organization_violations = org_results.get('violations', [])
        report.organization_score = org_results.get('score', 100)
        
        # Phase 3.8: Validate template headers (v3.2 format enforcement + old format detection)
        if monitor:
            monitor.update("Validating template headers")
        # Enforces: Brain emoji (🧠), section icons (🎯 ⚠️ 💬 📝 🔍), NO old format (✓ Accept, ⚡ Challenge)
        header_results = self._validate_template_headers()
        report.header_violations = header_results.get('violations', [])
        report.header_compliance_score = header_results.get('score', 100)
        
        # Phase 3.9: Validate documentation governance (duplicate/overlapping docs)
        if monitor:
            monitor.update("Checking documentation governance")
        doc_gov_results = self._validate_documentation_governance()
        report.doc_governance_violations = doc_gov_results.get('violations', [])
        report.doc_governance_score = doc_gov_results.get('score', 100)
        
        # Phase 3.10: Align 2.0 - Detect internal conflicts
        # Skip if configured to avoid O(n²) performance issue (330k+ file ops with 575+ docs)
        skip_duplicate_detection = self.config.get('system_alignment', {}).get('skip_duplicate_detection', False)
        
        if skip_duplicate_detection:
            if monitor:
                monitor.update("Skipping conflict detection (config: skip_duplicate_detection=true)")
            logger.info("Conflict detection skipped per configuration to avoid O(n²) performance issue")
            conflicts = []
        else:
            if monitor:
                monitor.update("Detecting ecosystem conflicts")
            conflicts = self._detect_conflicts()
        
        report.conflicts = conflicts
        
        # Update critical/warning counts from conflicts
        for conflict in conflicts:
            if conflict.severity == 'critical':
                report.critical_issues += 1
            elif conflict.severity == 'warning':
                report.warnings += 1
        
        # Phase 3.11: Align 2.0 - Generate fix templates
        if monitor:
            monitor.update("Generating fix templates")
        fix_templates = self._generate_fix_templates(conflicts)
        report.fix_templates = fix_templates
        
        # Phase 3.12: Align 2.0 - Generate dashboard
        if monitor:
            monitor.update("Generating health dashboard")
        dashboard = self._generate_dashboard(report, conflicts)
        report.dashboard_report = dashboard
        
        # Phase 4: Generate auto-remediation suggestions (legacy)
        if monitor:
            monitor.update("Generating remediation suggestions")
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
                
                # Validate new template architecture
                template_issues = []
                base_templates = templates.get("base_templates", {})
                template_defs = templates.get("templates", {})
                
                # Check for base template architecture (v3.2+)
                if not base_templates:
                    template_issues.append("Missing base_templates section (v3.2 architecture)")
                else:
                    # Validate base templates have required structure
                    for base_name, base_data in base_templates.items():
                        if "base_structure" not in base_data:
                            template_issues.append(f"Base template '{base_name}' missing base_structure")
                
                # Check for H1 header format in templates (# 🧠 CORTEX)
                for template_name, template_data in template_defs.items():
                    # New architecture: templates inherit from base_templates via YAML anchors
                    if "base_structure" in template_data:
                        # Using new composition model - validate placeholders
                        base_structure = template_data.get("base_structure", "")
                        if not base_structure.startswith("# "):
                            template_issues.append(f"{template_name}: Base structure missing H1 header")
                    else:
                        # Traditional template with direct content
                        content = template_data.get("content", "")
                        if content and not content.startswith("# ") and not content.startswith("##"):
                            template_issues.append(f"{template_name}: Missing H1 header")
                    
                    # Validate Challenge field format (should not have old [✓ Accept OR ⚡ Challenge])
                    content_str = str(template_data.get("content", "")) + str(template_data.get("base_structure", ""))
                    if "[✓ Accept OR ⚡ Challenge]" in content_str or "[Accept|Challenge]" in content_str:
                        template_issues.append(f"{template_name}: Old Challenge format detected")
                
                # Check for schema version
                schema_version = templates.get("schema_version", "unknown")
                if schema_version not in ["3.2", "3.3"]:
                    template_issues.append(f"Outdated schema_version: {schema_version} (expected 3.2+)")
                
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
        """
        Validate documentation governance (duplicate/overlapping docs).
        
        Checks:
        - Duplicate documents across cortex-brain/documents/ and .github/prompts/modules/
        - Overlapping content detection (title similarity, keyword overlap)
        - Canonical name violations for module guides
        - Documents not referenced in index files
        
        Returns:
            Dict with validation results and violations
        """
        # Check if duplicate detection should be skipped (performance optimization)
        # DEFAULT: Skip duplicate detection in system alignment to prevent O(n²) catastrophe
        # Can be explicitly enabled via context: {'skip_duplicate_detection': False}
        if self.context.get('skip_duplicate_detection', True):  # Changed default from False to True
            logger.info("Skipping duplicate document detection (skip_duplicate_detection=True) - prevents O(n²) performance issue")
            return {
                'score': 100,
                'violations': [],
                'total_docs_scanned': 0,
                'duplicate_pairs': 0,
                'warning': 'Duplicate detection skipped for performance (enable with skip_duplicate_detection=False if needed)'
            }
        
        try:
            governance = DocumentGovernance(self.project_root)
            violations = []
            score = 100
            
            # Scan all existing documents for duplicates
            documents_path = self.project_root / "cortex-brain" / "documents"
            modules_path = self.project_root / ".github" / "prompts" / "modules"
            
            scanned_docs = []
            
            # Collect all markdown files
            if documents_path.exists():
                for md_file in documents_path.rglob("*.md"):
                    if md_file.is_file():
                        scanned_docs.append(md_file)
            
            if modules_path.exists():
                for md_file in modules_path.glob("*.md"):
                    if md_file.is_file():
                        scanned_docs.append(md_file)
            
            logger.info(f"Scanning {len(scanned_docs)} documents for duplicates...")
            
            # Track duplicates found (avoid reporting same pair twice)
            reported_pairs = set()
            
            for doc_path in scanned_docs:
                try:
                    # Read document content
                    with open(doc_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Find duplicates
                    duplicates = governance.find_duplicates(doc_path, content)
                    
                    # Filter by threshold (0.75 from governance rules)
                    high_similarity = [
                        d for d in duplicates 
                        if d.similarity_score >= 0.75
                    ]
                    
                    for dup in high_similarity:
                        # Create canonical pair identifier (alphabetically sorted to avoid duplicates)
                        pair_key = tuple(sorted([str(doc_path), str(dup.existing_path)]))
                        
                        if pair_key not in reported_pairs:
                            reported_pairs.add(pair_key)
                            
                            violations.append({
                                'type': 'duplicate_document',
                                'severity': 'warning' if dup.similarity_score < 0.90 else 'critical',
                                'file': str(doc_path.relative_to(self.project_root)),
                                'duplicate': str(dup.existing_path.relative_to(self.project_root)),
                                'similarity': f"{dup.similarity_score:.0%}",
                                'algorithm': dup.algorithm,
                                'recommendation': dup.recommendation
                            })
                            
                            # Deduct score based on severity
                            if dup.similarity_score >= 0.90:
                                score -= 10  # Critical: likely exact duplicate
                            else:
                                score -= 5   # Warning: high similarity
                
                except Exception as e:
                    logger.debug(f"Error scanning {doc_path}: {e}")
                    continue
            
            # Ensure score doesn't go below 0
            score = max(0, score)
            
            logger.info(f"Documentation governance: {score}% ({len(violations)} issues found)")
            
            return {
                'score': score,
                'status': 'healthy' if score >= 80 else 'degraded',
                'violations': violations,
                'critical_count': sum(1 for v in violations if v.get('severity') == 'critical'),
                'warning_count': sum(1 for v in violations if v.get('severity') == 'warning'),
                'scanned_documents': len(scanned_docs),
                'duplicate_pairs': len(reported_pairs)
            }
            
        except Exception as e:
            logger.error(f"Documentation governance validation failed: {e}")
            return {
                'score': 0,
                'status': 'error',
                'violations': [],
                'critical_count': 0,
                'warning_count': 0,
                'scanned_documents': 0,
                'duplicate_pairs': 0
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
        
        # Add documentation governance remediation suggestions
        if hasattr(report, 'doc_governance_violations'):
            governance = DocumentGovernance(self.project_root)
            
            for violation in report.doc_governance_violations:
                if violation.get('type') == 'duplicate_document':
                    # Create consolidation suggestion
                    file1 = self.project_root / violation['file']
                    file2 = self.project_root / violation['duplicate']
                    
                    # Determine which file to keep (prefer older/more established)
                    keep_file = file1 if file1.stat().st_mtime < file2.stat().st_mtime else file2
                    remove_file = file2 if keep_file == file1 else file1
                    
                    suggestion_content = (
                        f"Duplicate detected: {violation['similarity']} similarity via {violation['algorithm']}\n"
                        f"File 1: {violation['file']}\n"
                        f"File 2: {violation['duplicate']}\n\n"
                        f"Recommended action:\n"
                        f"1. Review both documents and merge unique content into: {keep_file.relative_to(self.project_root)}\n"
                        f"2. Archive/delete: {remove_file.relative_to(self.project_root)}\n"
                        f"3. Update any references to point to the consolidated document\n\n"
                        f"{violation['recommendation']}"
                    )
                    
                    report.remediation_suggestions.append(RemediationSuggestion(
                        feature_name="Documentation Governance",
                        suggestion_type="duplicate_consolidation",
                        content=suggestion_content,
                        file_path=str(keep_file)
                    ))
    
    def _apply_auto_fixes(self, report: AlignmentReport, monitor: Optional[ProgressMonitor] = None) -> List[Dict[str, Any]]:
        """
        Apply auto-remediation fixes to features.
        
        Args:
            report: AlignmentReport with remediation suggestions
            monitor: Optional progress monitor for user feedback
        
        Returns:
            List of applied fixes with success status
        """
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
    
    def _review_enhancement_catalog(self) -> Dict[str, Any]:
        """
        Review Enhancement Catalog for new features since last alignment.
        
        Phase 0.5 integration - temporal feature tracking.
        
        Returns:
            Dict with catalog statistics and new features
        """
        try:
            # Initialize catalog and discovery
            catalog = EnhancementCatalog()
            discovery = EnhancementDiscoveryEngine(self.project_root)
            
            # Get last alignment review timestamp
            last_review = catalog.get_last_review_timestamp(review_type='alignment')
            
            # Discover features since last review
            if last_review:
                days_since = (datetime.now() - last_review).days
                logger.info(f"Last alignment review: {days_since} days ago, scanning for new features...")
                discovered = discovery.discover_since(since_date=last_review)
            else:
                logger.info("First alignment review, performing quick discovery...")
                discovered = discovery.discover_since(days=7)  # Quick scan for first run
            
            # Add/update features in catalog
            new_features_count = 0
            new_features_list = []
            
            for feature in discovered:
                # Map feature type
                feature_type = self._map_feature_type_for_catalog(feature.feature_type)
                
                # Determine acceptance status from integration score
                acceptance = AcceptanceStatus.DISCOVERED
                if hasattr(self, '_integration_scores') and feature.name in self._integration_scores:
                    score = self._integration_scores[feature.name]
                    if score >= 90:
                        acceptance = AcceptanceStatus.ACCEPTED
                
                is_new = catalog.add_feature(
                    name=feature.name,
                    feature_type=feature_type,
                    description=feature.description,
                    source=feature.source,
                    metadata=feature.metadata,
                    commit_hash=feature.commit_hash,
                    file_path=feature.file_path,
                    acceptance_status=acceptance
                )
                
                if is_new:
                    new_features_count += 1
                    new_features_list.append({
                        'name': feature.name,
                        'type': feature.feature_type,
                        'description': feature.description,
                        'source': feature.source,
                        'discovered_at': feature.discovered_at.isoformat() if feature.discovered_at else None
                    })
            
            # Log this alignment review
            catalog.log_review(
                review_type='alignment',
                features_reviewed=len(discovered),
                new_features_found=new_features_count,
                notes=f"System alignment validation"
            )
            
            # Get catalog stats
            stats = catalog.get_catalog_stats()
            
            return {
                'total_count': stats['total_features'],
                'new_count': new_features_count,
                'days_since_review': (datetime.now() - last_review).days if last_review else None,
                'new_features': new_features_list,
                'last_review': last_review.isoformat() if last_review else None
            }
            
        except Exception as e:
            logger.error(f"Error reviewing enhancement catalog: {e}")
            return {
                'total_count': 0,
                'new_count': 0,
                'days_since_review': None,
                'new_features': [],
                'error': str(e)
            }
    
    def _map_feature_type_for_catalog(self, discovery_type: str) -> FeatureType:
        """
        Map discovery feature type to catalog feature type.
        
        Args:
            discovery_type: Type from EnhancementDiscoveryEngine
            
        Returns:
            Mapped FeatureType for catalog
        """
        mapping = {
            'operation': FeatureType.OPERATION,
            'agent': FeatureType.AGENT,
            'orchestrator': FeatureType.ORCHESTRATOR,
            'workflow': FeatureType.WORKFLOW,
            'template': FeatureType.TEMPLATE,
            'documentation': FeatureType.DOCUMENTATION,
            'capability': FeatureType.INTEGRATION,
            'admin_script': FeatureType.UTILITY,
            'guide': FeatureType.DOCUMENTATION,
            'prompt_module': FeatureType.DOCUMENTATION
        }
        
        return mapping.get(discovery_type, FeatureType.UTILITY)
    
    def _format_report_summary(self, report: AlignmentReport, fixes_applied: List[Dict[str, Any]] = None) -> str:
        """Format alignment report summary for display."""
        lines = []
        
        # Align 2.0: Show dashboard if available
        if report.dashboard_report:
            return report.dashboard_report
        
        # Enhancement Catalog Summary (NEW)
        if report.catalog_features_new > 0:
            lines.append(f"\n📊 Enhancement Catalog:")
            lines.append(f"   Total Features: {report.catalog_features_total}")
            lines.append(f"   New Since Last Alignment: {report.catalog_features_new}")
            if report.catalog_days_since_review:
                lines.append(f"   Days Since Review: {report.catalog_days_since_review}")
            
            # Show top 5 new features
            if report.catalog_new_features:
                lines.append(f"\n   New Features:")
                for feature in report.catalog_new_features[:5]:
                    lines.append(f"      • {feature['name']} ({feature['type']})")
                if len(report.catalog_new_features) > 5:
                    lines.append(f"      ... and {len(report.catalog_new_features) - 5} more")
        
        # Legacy format (fallback)
        if report.is_healthy:
            lines.append("\n[OK] System alignment healthy")
        else:
            lines.append(f"\n[WARN] {report.issues_found} alignment issues detected:")
            
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
        """
        Validate brain databases are accessible and healthy.
        
        Lightweight check for alignment pre-flight validation.
        
        Returns:
            Dict with 'healthy' bool and 'issues' list
        """
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
        Generate visual health dashboards (text + interactive HTML).
        
        Phase 3.12: Align 2.0 enhancement
        Phase 4: Documentation Format Enforcement - Interactive HTML dashboards
        
        Generates two outputs:
        1. Text dashboard - Console output (backward compatible)
        2. HTML dashboard - Interactive D3.js visualizations (new)
        
        Args:
            report: Alignment report
            conflicts: List of conflicts
            
        Returns:
            Formatted text dashboard string (HTML saved to file)
        """
        logger.info("Generating health dashboards...")
        
        # Generate text dashboard (existing functionality)
        text_generator = DashboardGenerator(self.project_root)
        text_dashboard = text_generator.generate_dashboard(report, conflicts)
        
        # Save to history
        text_generator.save_history(report)
        
        # Generate interactive HTML dashboard (new functionality)
        try:
            from src.generators import EPMDashboardAdapter, DashboardTemplateGenerator
            
            logger.info("Generating interactive HTML dashboard...")
            
            # Transform report data to dashboard layers
            adapter = EPMDashboardAdapter()
            layers = adapter.transform_alignment_report(report, conflicts)
            
            # Determine status
            if report.is_healthy:
                status = "healthy"
            elif report.has_warnings:
                status = "warning"
            else:
                status = "critical"
            
            # Generate HTML
            html_generator = DashboardTemplateGenerator()
            html_content = html_generator.generate_dashboard(
                operation="system-alignment",
                title="CORTEX System Alignment Report",
                data={'overall_health': report.overall_health, 'timestamp': report.timestamp.isoformat()},
                layers=layers,
                metadata={
                    'author': 'CORTEX System Alignment',
                    'status': status,
                    'generated_at': report.timestamp.isoformat()
                }
            )
            
            # Save HTML dashboard
            reports_dir = self.cortex_brain / "documents" / "reports"
            reports_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp_str = report.timestamp.strftime("%Y%m%d_%H%M%S")
            html_file = reports_dir / f"SYSTEM_ALIGNMENT_DASHBOARD_{timestamp_str}.html"
            
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"✅ Interactive dashboard saved: {html_file}")
            logger.info(f"   Open in browser for D3.js visualizations")
            
        except Exception as e:
            logger.warning(f"Failed to generate HTML dashboard: {e}")
            logger.info("Continuing with text dashboard only...")
        
        return text_dashboard
    
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
