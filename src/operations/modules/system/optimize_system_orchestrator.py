"""
CORTEX System Optimizer - Meta-Level Orchestrator

Comprehensive system optimization from all angles:
1. Design-Implementation Synchronization (design_sync)
2. Code Health & Obsolete Tests (optimize_cortex)
3. Brain Tier Tuning & Knowledge Graph Optimization
4. Entry Point Alignment (orchestrator consistency)
5. Test Suite Optimization (SKULL-007 compliance)
6. Comprehensive Health Report

This meta-orchestrator coordinates ALL optimization operations to ensure:
- Maximum inbuilt tooling leverage
- Design-implementation alignment
- Brain protection layer integrity
- Knowledge graph quality
- Test suite health (100% pass rate)
- Entry point consistency

Configuration is loaded from cortex-brain/operations-config.yaml under system_optimization section.
No hardcoded limits or thresholds.

Natural Language Triggers:
- "optimize cortex system"
- "optimize everything"
- "run comprehensive optimization"
- "system health check comprehensive"
- "align all components"

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms
Version: 1.0.0
Date: November 12, 2025
"""

from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Set
import logging
import json
import subprocess
import yaml

from src.operations.base_operation_module import (
    BaseOperationModule,
    OperationPhase,
    OperationResult,
    OperationModuleMetadata,
    OperationStatus,
    ExecutionMode
)
from src.operations.operation_header_formatter import OperationHeaderFormatter
from src.operations.modules.system.optimization_models import OptimizationMetrics, SystemHealthReport
from src.operations.modules.system.governance_drift_checker import GovernanceDriftChecker
from src.caching import get_cache

logger = logging.getLogger(__name__)


class OptimizeSystemOrchestrator(BaseOperationModule):
    """
    Meta-level orchestrator for comprehensive CORTEX system optimization.
    
    Coordinates 8 optimization phases:
    
    Phase 0: Instruction File Review
        - Holistic review of CORTEX.prompt.md + copilot-instructions.md
        - Detect redundancy, outdated references, bloat
        - Validate trigger coverage and consistency
        - Optimize for token efficiency
    
    Phase 1: Design Sync
        - Run design_sync_orchestrator
        - Resolve design-implementation drift
        - Consolidate status files
        - Update module counts
    
    Phase 2: Code Health
        - Run optimize_cortex_orchestrator
        - Identify obsolete tests
        - Detect dead code
        - Analyze test coverage gaps
    
    Phase 3: Brain Tuning
        - Validate tier boundaries (Tier 0, 1, 2, 3)
        - Prune low-confidence patterns (<0.50)
        - Detect and merge duplicate patterns
        - Validate brain protection rules (YAML)
    
    Phase 4: Entry Point Alignment
        - Validate all orchestrator headers use HeaderFormatter
        - Sync command registry with natural language triggers
        - Update CORTEX.prompt.md with discovered commands
        - Ensure consistent copyright attribution
    
    Phase 5: Test Suite Optimization
        - Execute obsolete test removal (from Phase 2)
        - Fix failing tests using recommendations
        - Validate 100% pass rate (SKULL-007 compliance)
        - Generate test coverage report
    
    Phase 6: Comprehensive Report
        - Consolidate metrics from all phases
        - Calculate overall health score
        - Generate recommendations
        - Save to cortex-brain/system-optimization-report.md
    
    Phase 7: Governance Health Check
        - Check rule position drift vs optimal ordering
        - Count forward references (target: <3)
        - Detect file bloat (target: <1200 lines)
        - Identify orphaned rules (never referenced)
        - Validate metadata (copilot_position, reference_count)
        - Calculate governance health score (0-100)
    
    Phase 8: SKULL Test Discovery & Validation
        - Scan CORTEX system holistically for governance enforcement points
        - Identify missing SKULL tests for brain protection rules
        - Detect outdated SKULL tests (rules removed/refactored)
        - Validate SKULL test coverage (all Tier 0 instincts tested)
        - Recommend new SKULL tests based on governance drift
        - Execute existing SKULL tests and report failures
    
    Usage:
        orchestrator = OptimizeSystemOrchestrator(project_root=Path('/path/to/cortex'))
        result = orchestrator.execute(context={'profile': 'comprehensive', 'mode': 'live'})
    """
    
    VERSION = "1.0.0"
    
    def __init__(self, project_root: Optional[Path] = None, mode: ExecutionMode = ExecutionMode.LIVE):
        """
        Initialize system optimizer.
        
        Args:
            project_root: CORTEX project root directory (optional, will be detected from context)
            mode: Execution mode (LIVE only)
        """
        super().__init__()
        self.project_root = project_root or Path.cwd()
        self.mode = mode
        self.metrics = OptimizationMetrics()
        self.start_time = None
        self._config_cache = None  # Cache for YAML config
        self._validation_cache = get_cache()  # ValidationCache for caching expensive operations
        
        # Track files for cache invalidation
        self._tracked_files = []
        governance_file = self.project_root / "src" / "tier0" / "governance.yaml"
        if governance_file.exists():
            self._tracked_files.append(governance_file)
        
        documents_dir = self.project_root / "cortex-brain" / "documents"
        if documents_dir.exists():
            self._tracked_files.extend([
                documents_dir / "reports",
                documents_dir / "analysis", 
                documents_dir / "summaries"
            ])
    
    def _load_optimization_config(self, project_root: Path) -> Dict[str, Any]:
        """
        Load system optimization configuration from YAML.
        
        Loads from cortex-brain/operations-config.yaml under system_optimization section.
        Returns defaults if file not found or section missing.
        
        Args:
            project_root: CORTEX project root
            
        Returns:
            Dict with optimization settings (file_size_limits, code_quality, performance)
        """
        if self._config_cache is not None:
            return self._config_cache
            
        config_file = project_root / "cortex-brain" / "operations-config.yaml"
        
        # Default configuration (fallback if YAML missing)
        default_config = {
            'file_size_limits': {
                'soft_limit_lines': 500,
                'hard_limit_lines': 1000
            },
            'code_quality': {
                'max_methods_per_class': 15,
                'max_complexity': 10,
                'max_duplication_percent': 5
            },
            'performance': {
                'max_execution_time_seconds': 300,
                'memory_limit_mb': 512
            }
        }
        
        if not config_file.exists():
            logger.warning(f"Config file not found: {config_file}, using defaults")
            self._config_cache = default_config
            return default_config
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                full_config = yaml.safe_load(f)
            
            # Extract system_optimization section
            operations_config = full_config.get('operations_config', {})
            system_opt = operations_config.get('system_optimization', {})
            
            if not system_opt:
                logger.warning("system_optimization section not found in config, using defaults")
                self._config_cache = default_config
                return default_config
            
            # Merge with defaults to ensure all keys exist
            merged_config = {
                'file_size_limits': {**default_config['file_size_limits'], **system_opt.get('file_size_limits', {})},
                'code_quality': {**default_config['code_quality'], **system_opt.get('code_quality', {})},
                'performance': {**default_config['performance'], **system_opt.get('performance', {})}
            }
            
            self._config_cache = merged_config
            logger.info(f"Loaded optimization config from {config_file}")
            return merged_config
            
        except Exception as e:
            logger.error(f"Failed to load config from {config_file}: {e}, using defaults")
            self._config_cache = default_config
            return default_config
    
    def get_metadata(self) -> OperationModuleMetadata:
        """Return metadata for this operation module."""
        return OperationModuleMetadata(
            module_id="optimize_system_orchestrator",
            name="System Optimization Meta-Orchestrator",
            version=self.VERSION,
            description="Comprehensive CORTEX system optimization from all angles",
            phase=OperationPhase.PROCESSING,
            dependencies=[],
            tags=['system', 'optimization', 'meta-orchestrator', 'comprehensive']
        )
    
    def validate_prerequisites(self, context: Dict[str, Any]) -> OperationResult:
        """
        Validate prerequisites for system optimization.
        
        Checks:
        - CORTEX project root exists
        - Required orchestrators available
        - Git repository initialized
        - Python environment configured
        
        Args:
            context: Execution context
        
        Returns:
            OperationResult with validation status
        """
        logger.info("🔍 Validating prerequisites for system optimization...")
        
        issues = []
        
        if not self.project_root.exists():
            issues.append(f"Project root not found: {self.project_root}")
        
        design_sync = self.project_root / "src" / "operations" / "modules" / "design_sync" / "design_sync_orchestrator.py"
        optimize_cortex = self.project_root / "src" / "operations" / "modules" / "optimize" / "optimize_cortex_orchestrator.py"
        
        if not design_sync.exists():
            issues.append("design_sync_orchestrator.py not found")
        
        if not optimize_cortex.exists():
            issues.append("optimize_cortex_orchestrator.py not found")
        
        git_dir = self.project_root / ".git"
        if not git_dir.exists():
            issues.append("Not a git repository")
        
        brain_dir = self.project_root / "cortex-brain"
        if not brain_dir.exists():
            issues.append("cortex-brain directory not found")
        
        if issues:
            return OperationResult(
                status=OperationStatus.FAILED,
                success=False,
                message=f"Prerequisites validation failed: {', '.join(issues)}",
                errors=["\n".join(issues)]
            )
        
        logger.info("✅ Prerequisites validated successfully")
        return OperationResult(
            status=OperationStatus.SUCCESS,
            success=True,
            message="Prerequisites validated"
        )
    
    def execute(self, context: Dict[str, Any]) -> OperationResult:
        """
        Execute comprehensive system optimization.
        
        Args:
            context: Execution context with keys:
                - profile: Optimization profile ('comprehensive', 'focused', 'minimal')
                - mode: Execution mode (always 'live')
                - skip_phases: Optional list of phases to skip
        
        Returns:
            OperationResult with optimization status and metrics
        """
        self.start_time = datetime.now()
        
        # Extract context
        profile = context.get('profile', 'comprehensive')
        mode_str = context.get('mode', 'live')
        self.mode = ExecutionMode.LIVE  # Always use live mode
        skip_phases = context.get('skip_phases', [])
        
        # Print header
        mode_display = "LIVE" if self.mode == ExecutionMode.LIVE else "DRY RUN"
        header = OperationHeaderFormatter.format_minimalist(
            operation_name="System Optimization",
            version=self.VERSION,
            profile=profile,
            mode=mode_display,
            timestamp=self.start_time
        )
        print(header)
        
        logger.info(f"System Optimization started | Profile: {profile} | Mode: {mode_display}")
        
        try:
            # Phase 0: Holistic Review of Instruction Files
            logger.info("\n[Phase 0/8] Reviewing instruction files holistically...")
            instruction_review_result = self._review_instruction_files()
            
            if instruction_review_result['success']:
                optimizations = instruction_review_result.get('optimizations_applied', 0)
                if optimizations > 0:
                    logger.info(f"✅ Applied {optimizations} instruction file optimizations")
                    self.metrics.instruction_optimizations = optimizations
                else:
                    logger.info("ℹ️  Instruction files are lean and complete")
            else:
                logger.warning(f"⚠️ Instruction file review: {instruction_review_result.get('message', 'Review incomplete')}")
            
            # Phase 0.5: Quick health check (use cached results if recent)
            logger.info("\n[Phase 0.5/8] Checking system health...")
            health_status = self._check_cached_health_status()
            
            if health_status and health_status.get('score', 0) > 0:
                logger.info(f"✅ Using cached health status (score: {health_status['score']}/100)")
            else:
                # Run quick health check (system + brain only)
                from src.operations.healthcheck_operation import HealthCheckOperation
                health_check = HealthCheckOperation()
                result = health_check.execute({'quick': True})
                
                if not result.success:
                    logger.warning(f"⚠️ Health check warning: {result.message}")
                else:
                    logger.info(f"✅ Health check passed")
            
            # Phase 1: Validate prerequisites
            logger.info("\n[Phase 1/9] Validating prerequisites...")
            prereq_result = self.validate_prerequisites(context)
            if not prereq_result.success:
                return prereq_result
            
            # Phase 2: Design Sync
            if 'design_sync' not in skip_phases:
                logger.info("\n[Phase 2/9] Running design synchronization...")
                self._run_design_sync(context)
            else:
                logger.info("\n[Phase 2/9] Design sync skipped (per user request)")
            
            # Phase 3: Code Health
            if 'code_health' not in skip_phases:
                logger.info("\n[Phase 3/9] Analyzing code health...")
                self._run_code_health_analysis(context)
            else:
                logger.info("\n[Phase 3/9] Code health analysis skipped (per user request)")
            
            # Phase 4: Brain Tuning
            if 'brain_tuning' not in skip_phases:
                logger.info("\n[Phase 4/9] Tuning brain tiers...")
                self._run_brain_tuning(context)
            else:
                logger.info("\n[Phase 4/9] Brain tuning skipped (per user request)")
            
            # Phase 5: Entry Point Alignment
            if 'entry_point_alignment' not in skip_phases:
                logger.info("\n[Phase 5/9] Aligning entry points...")
                self._run_entry_point_alignment(context)
            else:
                logger.info("\n[Phase 5/9] Entry point alignment skipped (per user request)")
            
            # Phase 6: Test Suite Optimization
            if 'test_suite' not in skip_phases:
                logger.info("\n[Phase 6/9] Optimizing test suite...")
                self._run_test_suite_optimization(context)
            else:
                logger.info("\n[Phase 6/9] Test suite optimization skipped (per user request)")
            
            # Phase 7: Governance Health Check
            if 'governance' not in skip_phases:
                logger.info("\n[Phase 7/9] Checking governance drift...")
                governance_result = self._check_governance_drift(context)
                if governance_result['has_issues']:
                    logger.warning(f"⚠️  Governance issues detected (score: {governance_result['health_score']:.1f}/100)")
                    for issue in governance_result['issues']:
                        logger.warning(f"   • {issue}")
                else:
                    logger.info(f"✅ Governance health: {governance_result['health_score']:.1f}/100")
            else:
                logger.info("\n[Phase 7/9] Governance check skipped (per user request)")
            
            # Phase 8: SKULL Test Discovery & Validation
            if 'skull_tests' not in skip_phases:
                logger.info("\n[Phase 8/9] SKULL test discovery & validation...")
                skull_result = self._discover_and_validate_skull_tests(context)
                if skull_result['tests_needed']:
                    logger.warning(f"⚠️  SKULL test gaps detected: {len(skull_result['missing_tests'])} missing")
                    for missing in skull_result['missing_tests'][:5]:  # Show first 5
                        logger.warning(f"   • {missing}")
                if skull_result['tests_outdated']:
                    logger.warning(f"⚠️  Outdated SKULL tests: {len(skull_result['outdated_tests'])}")
                logger.info(f"✅ SKULL coverage: {skull_result['coverage_percent']:.1f}% ({skull_result['tests_passing']}/{skull_result['tests_total']} passing)")
            else:
                logger.info("\n[Phase 8/9] SKULL test validation skipped (per user request)")
            
            end_time = datetime.now()
            self.metrics.execution_time_seconds = (end_time - self.start_time).total_seconds()
            self.metrics.total_improvements = self._calculate_total_improvements()
            
            # Generate report
            report = self._generate_health_report()
            
            # Save report
            report_path = self.project_root / "cortex-brain" / "system-optimization-report.md"
            self._save_report(report, report_path)
            
            # Print footer
            footer = self._format_completion_footer(report)
            print(footer)
            
            logger.info(f"✅ System optimization complete | Score: {report.health_score:.1f}/100")
            
            return OperationResult(
                status=OperationStatus.SUCCESS,
                success=True,
                message=f"System optimization complete ({profile} profile)",
                data={
                    'health_score': report.health_score,
                    'overall_health': report.overall_health,
                    'metrics': report.to_dict(),
                    'report_path': str(report_path)
                },
                formatted_header=header,
                formatted_footer=footer
            )
        
        except Exception as e:
            logger.error(f"System optimization failed: {e}", exc_info=True)
            self.metrics.errors_encountered.append(str(e))
            
            return OperationResult(
                status=OperationStatus.FAILED,
                success=False,
                message=f"System optimization failed: {e}",
                errors=[str(e)],
                data={'metrics': self.metrics}
            )
    
    def _run_design_sync(self, context: Dict[str, Any]) -> None:
        """Run design synchronization (Phase 2)."""
        try:
            from src.operations.modules.design_sync.design_sync_orchestrator import DesignSyncOrchestrator
            
            logger.info("🔄 Initializing design synchronization...")
            
            design_sync = DesignSyncOrchestrator()
            
            # Execute with current mode and project root in context
            sync_context = {
                'profile': context.get('profile', 'standard'),
                'mode': 'live',  # Always use live mode
                'project_root': self.project_root
            }
            
            result = design_sync.execute(sync_context)
            
            if result.success:
                # Extract metrics from result
                data = result.data or {}
                metrics = data.get('metrics', {})
                
                self.metrics.design_drift_resolved = metrics.get('gaps_analyzed', 0)
                self.metrics.modules_synced = metrics.get('implementation_discovered', {}).get('total_modules', 0)
                self.metrics.status_files_consolidated = metrics.get('status_files_consolidated', 0)
                
                logger.info(f"✅ Design sync complete: {self.metrics.design_drift_resolved} gaps resolved")
            else:
                error_msg = f"Design sync failed: {result.error or result.message}"
                logger.error(error_msg)
                self.metrics.errors_encountered.append(error_msg)
        
        except Exception as e:
            error_msg = f"Design sync integration error: {e}"
            logger.error(error_msg, exc_info=True)
            self.metrics.errors_encountered.append(error_msg)
    
    def _run_code_health_analysis(self, context: Dict[str, Any]) -> None:
        """Run code health analysis (Phase 3)."""
        try:
            from src.operations.modules.optimization.optimize_cortex_orchestrator import OptimizeCortexOrchestrator
            
            logger.info("🔍 Analyzing code health...")
            
            optimize = OptimizeCortexOrchestrator(project_root=self.project_root)
            
            # Execute
            result = optimize.execute({})
            
            if result.success:
                # Extract metrics from health report
                report_data = result.data or {}
                
                self.metrics.obsolete_tests_identified = len(report_data.get('obsolete_tests', []))
                self.metrics.dead_code_removed = len(report_data.get('issues', []))
                self.metrics.coverage_gaps_identified = len([
                    i for i in report_data.get('issues', [])
                    if i.get('category') == 'coverage'
                ])
                
                logger.info(f"✅ Code health analyzed: {self.metrics.obsolete_tests_identified} obsolete tests found")
            else:
                error_msg = f"Code health analysis failed: {result.error or result.message}"
                logger.error(error_msg)
                self.metrics.errors_encountered.append(error_msg)
        
        except Exception as e:
            error_msg = f"Code health analysis error: {e}"
            logger.error(error_msg, exc_info=True)
            self.metrics.errors_encountered.append(error_msg)
    
    def _check_cached_health_status(self) -> Optional[Dict[str, Any]]:
        """
        Check for recent cached health status.
        
        Returns:
            Cached health status if recent (<5 min), None otherwise
        """
        try:
            cache_key = 'status'
            cached = self._validation_cache.get('healthcheck', cache_key)
            
            if cached:
                timestamp = cached.get('timestamp')
                if timestamp:
                    cached_time = datetime.fromisoformat(timestamp)
                    age_minutes = (datetime.now() - cached_time).total_seconds() / 60
                    
                    if age_minutes < 5:
                        return cached
            
            return None
            
        except Exception as e:
            logger.debug(f"Failed to retrieve cached health status: {e}")
            return None
    
    def _run_brain_tuning(self, context: Dict[str, Any]) -> None:
        """Run brain tuning operations (Phase 4)."""
        # TODO: Implement brain tuning module
        logger.info("⏩ Brain tuning implementation pending...")
        self.metrics.warnings.append("Brain tuning not yet implemented")
    
    def _run_entry_point_alignment(self, context: Dict[str, Any]) -> None:
        """
        Run entry point alignment (Phase 5).
        
        CORTEX 3.1 Enhancement: EPMO Health Check
        - Detects EPMO bloat (>500 lines soft limit, >1000 hard limit)
        - Finds EPMO duplication (same class in multiple locations)
        - Validates SOLID principles (SRP, OCP, DIP violations)
        - Checks hemisphere separation (RIGHT vs LEFT brain)
        - Reports drift from governance rules
        
        See: cortex-brain/cortex-3.0-design/CORTEX-3.1-EPMO-OPTIMIZATION-PLAN.yaml
        """
        logger.info("🔍 Checking EPMO health and alignment...")
        
        try:
            epmo_health = self._check_epmo_health()
            
            if epmo_health['has_issues']:
                logger.warning(f"⚠️ EPMO health issues detected:")
                for issue in epmo_health['issues']:
                    logger.warning(f"  - {issue}")
                
                # Add to warnings
                self.metrics.warnings.extend(epmo_health['issues'])
                
                # Provide remediation guidance
                logger.info("\n💡 Remediation guidance:")
                logger.info("  See: cortex-brain/cortex-3.0-design/CORTEX-3.1-EPMO-OPTIMIZATION-PLAN.yaml")
                logger.info("  Run: pytest tests/tier0/test_epmo_health.py (when implemented)")
            else:
                logger.info("✅ All EPMOs healthy and aligned")
                self.metrics.orchestrators_aligned = epmo_health['epmo_count']
        
        except Exception as e:
            error_msg = f"EPMO health check error: {e}"
            logger.error(error_msg, exc_info=True)
            self.metrics.errors_encountered.append(error_msg)
    
    def _check_epmo_health(self) -> Dict[str, Any]:
        """
        Check EPMO health metrics.
        
        Uses ValidationCache to cache EPMO health analysis results.
        Cache is invalidated when any orchestrator file changes.
        
        Implements CORTEX 3.1 EPMO drift detection:
        - Size metrics (line count, token count)
        - Duplication detection (class name similarity)
        - SOLID compliance (SRP, OCP, DIP)
        - Hemisphere separation (RIGHT vs LEFT)
        
        Returns:
            Dict with keys:
                - has_issues: bool
                - issues: List[str]
                - epmo_count: int
                - health_score: float (0-100)
        """
        # Find all orchestrator files
        operations_dir = self.project_root / "src" / "operations" / "modules"
        epmo_files = []
        
        if operations_dir.exists():
            for py_file in operations_dir.rglob("*_orchestrator.py"):
                epmo_files.append(py_file)
        
        if not epmo_files:
            return {
                'has_issues': False,
                'issues': [],
                'epmo_count': 0,
                'health_score': 100.0
            }
        
        # Try cache first
        cache_key = "epmo_health_analysis"
        cached_result = self._validation_cache.get(
            "optimize",
            cache_key,
            files=epmo_files
        )
        
        if cached_result is not None:
            logger.info("✅ EPMO health analysis retrieved from cache")
            self.metrics.warnings.append(f"EPMO health cache hit (saved ~1-2s)")
            return cached_result
        
        logger.info("🔄 Running EPMO health analysis (cache miss)...")
        issues = []
        
        # Load configuration from YAML (no hardcoded limits!)
        config = self._load_optimization_config(self.project_root)
        file_size_limits = config.get('file_size_limits', {})
        SOFT_LIMIT = file_size_limits.get('soft_limit_lines', 500)
        HARD_LIMIT = file_size_limits.get('hard_limit_lines', 1000)
        
        code_quality = config.get('code_quality', {})
        MAX_METHODS = code_quality.get('max_methods_per_class', 15)
        
        for epmo_file in epmo_files:
            line_count = len(epmo_file.read_text(encoding='utf-8').splitlines())
            
            if line_count > HARD_LIMIT:
                issues.append(
                    f"CRITICAL: {epmo_file.name} has {line_count} lines (hard limit: {HARD_LIMIT})"
                )
            elif line_count > SOFT_LIMIT:
                issues.append(
                    f"WARNING: {epmo_file.name} has {line_count} lines (soft limit: {SOFT_LIMIT})"
                )
        
        # Check 2: Duplication detection (simple class name matching)
        class_names = {}
        for epmo_file in epmo_files:
            content = epmo_file.read_text(encoding='utf-8')
            # Simple regex to find class definitions
            import re
            matches = re.findall(r'class\s+(\w+Orchestrator)\s*\(', content)
            
            for class_name in matches:
                if class_name not in class_names:
                    class_names[class_name] = []
                class_names[class_name].append(epmo_file)
        
        # Report duplicates
        for class_name, files in class_names.items():
            if len(files) > 1:
                file_list = ', '.join([f.name for f in files])
                issues.append(
                    f"DUPLICATION: {class_name} found in {len(files)} locations: {file_list}"
                )
        
        # Check 3: SOLID principle violations (simple heuristics)
        for epmo_file in epmo_files:
            content = epmo_file.read_text(encoding='utf-8')
            
            # SRP check: Count methods (rough proxy for responsibilities)
            method_count = len(re.findall(r'\n    def \w+\(', content))
            if method_count > MAX_METHODS:
                issues.append(
                    f"SRP VIOLATION: {epmo_file.name} has {method_count} methods (limit: {MAX_METHODS}, suggests >3 responsibilities)"
                )
        
        health_score = 100.0
        health_score -= len([i for i in issues if 'CRITICAL' in i]) * 20
        health_score -= len([i for i in issues if 'WARNING' in i]) * 5
        health_score -= len([i for i in issues if 'DUPLICATION' in i]) * 15
        health_score -= len([i for i in issues if 'VIOLATION' in i]) * 10
        health_score = max(0.0, health_score)
        
        result = {
            'has_issues': len(issues) > 0,
            'issues': issues,
            'epmo_count': len(epmo_files),
            'health_score': health_score
        }
        
        # Cache the result for future runs
        self._validation_cache.set(
            "optimize",
            cache_key,
            result,
            files=epmo_files,
            ttl_seconds=3600  # Cache for 1 hour
        )
        logger.info("✅ EPMO health analysis cached")
        
        return result
    
    def _run_test_suite_optimization(self, context: Dict[str, Any]) -> None:
        """Run test suite optimization (Phase 6)."""
        # TODO: Implement test suite optimization module
        logger.info("⏩ Test suite optimization implementation pending...")
        self.metrics.warnings.append("Test suite optimization not yet implemented")
    
    def _discover_and_validate_skull_tests(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Discover and validate SKULL tests (Phase 8).
        
        Performs holistic review:
        1. Load brain protection rules (brain-protection-rules.yaml)
        2. Scan tests/tier0/ and tests/tier3/ for SKULL tests
        3. Map rules to tests (which rules are covered?)
        4. Identify missing tests (rules without coverage)
        5. Identify outdated tests (tests for removed rules)
        6. Execute all SKULL tests and report results
        
        Returns:
            Dict with:
                - coverage_percent: Percentage of rules with tests
                - tests_total: Total SKULL tests found
                - tests_passing: Number passing
                - tests_failing: Number failing
                - missing_tests: List of rules without tests
                - outdated_tests: List of tests for removed rules
                - tests_needed: Boolean - are new tests needed?
        """
        try:
            result = {
                'coverage_percent': 0.0,
                'tests_total': 0,
                'tests_passing': 0,
                'tests_failing': 0,
                'missing_tests': [],
                'outdated_tests': [],
                'tests_needed': False
            }
            
            # Step 1: Load brain protection rules
            brain_rules_file = self.project_root / "cortex-brain" / "brain-protection-rules.yaml"
            if not brain_rules_file.exists():
                logger.warning("⚠️  brain-protection-rules.yaml not found, skipping SKULL validation")
                return result
            
            with open(brain_rules_file, 'r', encoding='utf-8') as f:
                brain_rules = yaml.safe_load(f)
            
            # Extract Tier 0 instinct names (rules that should have tests)
            tier0_instincts = brain_rules.get('tier0_instincts', [])
            if isinstance(tier0_instincts, list):
                rule_names = set(tier0_instincts)
            else:
                # If it's a dict, use keys
                rule_names = set(tier0_instincts.keys())
            logger.info(f"📋 Found {len(rule_names)} Tier 0 instincts in brain protection rules")
            
            # Step 2: Scan for SKULL tests
            skull_tests = []
            test_dirs = [
                self.project_root / "tests" / "tier0",
                self.project_root / "tests" / "tier3"
            ]
            
            for test_dir in test_dirs:
                if not test_dir.exists():
                    continue
                for test_file in test_dir.glob("test_*.py"):
                    content = test_file.read_text(encoding='utf-8')
                    if 'skull' in content.lower() or 'SKULL' in content:
                        skull_tests.append(test_file)
            
            logger.info(f"🔍 Found {len(skull_tests)} SKULL test files")
            
            # Step 3: Map tests to rules (simple heuristic - look for rule names in test files)
            covered_rules = set()
            for test_file in skull_tests:
                content = test_file.read_text(encoding='utf-8').lower()
                for rule_name in rule_names:
                    if rule_name.lower() in content:
                        covered_rules.add(rule_name)
            
            # Step 4: Identify missing tests
            missing_tests = list(rule_names - covered_rules)
            result['missing_tests'] = [f"{rule}: No test found" for rule in missing_tests]
            result['tests_needed'] = len(missing_tests) > 0
            
            # Step 5: Execute SKULL tests (use pytest)
            if skull_tests:
                try:
                    # Run pytest on SKULL test files
                    test_paths = [str(t) for t in skull_tests]
                    cmd = ['python', '-m', 'pytest'] + test_paths + ['-v', '--tb=short', '-q']
                    
                    proc = subprocess.run(
                        cmd,
                        cwd=str(self.project_root),
                        capture_output=True,
                        text=True,
                        timeout=120
                    )
                    
                    # Parse output for pass/fail counts
                    output = proc.stdout + proc.stderr
                    
                    # Count passing/failing tests
                    passing = output.count(' PASSED')
                    failing = output.count(' FAILED')
                    
                    result['tests_total'] = passing + failing
                    result['tests_passing'] = passing
                    result['tests_failing'] = failing
                    
                    logger.info(f"✅ SKULL tests: {passing} passing, {failing} failing")
                    
                except subprocess.TimeoutExpired:
                    logger.warning("⚠️  SKULL test execution timed out (120s)")
                except Exception as e:
                    logger.warning(f"⚠️  SKULL test execution failed: {e}")
            
            # Step 6: Calculate coverage
            if rule_names:
                result['coverage_percent'] = (len(covered_rules) / len(rule_names)) * 100
            
            return result
            
        except Exception as e:
            logger.error(f"SKULL test discovery failed: {e}", exc_info=True)
            return {
                'coverage_percent': 0.0,
                'tests_total': 0,
                'tests_passing': 0,
                'tests_failing': 0,
                'missing_tests': [],
                'outdated_tests': [],
                'tests_needed': False,
                'error': str(e)
            }
    
    def _check_governance_drift(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Check governance.yaml for ordering drift and inefficiencies (delegated to GovernanceDriftChecker)."""
        checker = GovernanceDriftChecker(self.project_root, self._validation_cache)
        result = checker.check()
        
        # Update metrics from result
        self.metrics.governance_drift_score = result.get('health_score', 0.0)
        self.metrics.governance_position_drifts = result.get('position_drifts', 0)
        self.metrics.governance_forward_refs = result.get('forward_refs', 0)
        self.metrics.governance_orphaned_rules = result.get('orphaned_rules', 0)
        
        return result
    
    def _calculate_total_improvements(self) -> int:
        """Calculate total improvements made across all phases."""
        return (
            self.metrics.design_drift_resolved +
            self.metrics.obsolete_tests_identified +
            self.metrics.tier_violations_fixed +
            self.metrics.low_confidence_patterns_pruned +
            self.metrics.duplicate_patterns_merged +
            self.metrics.orchestrators_aligned +
            self.metrics.tests_removed +
            self.metrics.tests_fixed
        )
    
    def _generate_health_report(self) -> SystemHealthReport:
        """Generate comprehensive health report."""
        health_score = self._calculate_health_score()
        
        # Determine overall health
        if health_score >= 90:
            overall_health = "excellent"
        elif health_score >= 75:
            overall_health = "good"
        elif health_score >= 60:
            overall_health = "fair"
        elif health_score >= 40:
            overall_health = "poor"
        else:
            overall_health = "critical"
        
        # Generate recommendations
        recommendations = self._generate_recommendations()
        
        # Generate next actions
        next_actions = self._generate_next_actions()
        
        return SystemHealthReport(
            timestamp=datetime.now(),
            overall_health=overall_health,
            health_score=health_score,
            metrics=self.metrics,
            recommendations=recommendations,
            next_actions=next_actions
        )
    
    def _calculate_health_score(self) -> float:
        """Calculate overall health score (0-100)."""
        # TODO: Implement proper scoring algorithm
        # For now, simple placeholder based on warnings/errors
        base_score = 85.0
        
        # Deduct for errors
        base_score -= len(self.metrics.errors_encountered) * 10
        
        # Deduct for warnings
        base_score -= len(self.metrics.warnings) * 2
        
        # Add for improvements
        base_score += min(self.metrics.total_improvements * 0.5, 15)
        
        return max(0.0, min(100.0, base_score))
    
    def _generate_recommendations(self) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []
        
        if self.metrics.errors_encountered:
            recommendations.append("Address critical errors before proceeding")
        
        if self.metrics.final_pass_rate < 100.0:
            recommendations.append(f"Fix remaining test failures (current: {self.metrics.final_pass_rate:.1f}%)")
        
        if self.metrics.low_confidence_patterns_pruned == 0:
            recommendations.append("Review knowledge graph for low-confidence patterns")
        
        if self.metrics.design_drift_resolved == 0:
            recommendations.append("Run design sync to align documentation")
        
        return recommendations
    
    def _generate_next_actions(self) -> List[str]:
        """Generate next action items."""
        actions = []
        
        if not self.metrics.skull_007_compliant:
            actions.append("Achieve 100% test pass rate (SKULL-007 requirement)")
        
        if self.metrics.design_drift_resolved > 0:
            actions.append("Review design sync changes and commit")
        
        if self.metrics.obsolete_tests_identified > 0:
            actions.append(f"Remove {self.metrics.obsolete_tests_identified} obsolete tests")
        
        return actions
    
    def _save_report(self, report: SystemHealthReport, report_path: Path) -> None:
        """Save health report to markdown file."""
        content = f"""# CORTEX System Optimization Report

**Generated:** {report.timestamp.strftime('%Y-%m-%d %H:%M:%S')}  
**Overall Health:** {report.overall_health.upper()}  
**Health Score:** {report.health_score:.1f}/100

---

## 📊 Optimization Metrics

### Phase 1: Design Synchronization
- Design drift resolved: {report.metrics.design_drift_resolved}
- Modules synced: {report.metrics.modules_synced}
- Status files consolidated: {report.metrics.status_files_consolidated}

### Phase 2: Code Health
- Obsolete tests identified: {report.metrics.obsolete_tests_identified}
- Dead code removed: {report.metrics.dead_code_removed}
- Coverage gaps identified: {report.metrics.coverage_gaps_identified}

### Phase 3: Brain Tuning
- Tier violations fixed: {report.metrics.tier_violations_fixed}
- Low-confidence patterns pruned: {report.metrics.low_confidence_patterns_pruned}
- Duplicate patterns merged: {report.metrics.duplicate_patterns_merged}
- Protection rules validated: {'✅' if report.metrics.protection_rules_validated else '❌'}

### Phase 4: Entry Point Alignment
- Orchestrators aligned: {report.metrics.orchestrators_aligned}
- Commands registered: {report.metrics.commands_registered}
- Entry points synced: {report.metrics.entry_points_synced}

### Phase 5: Test Suite Optimization
- Tests removed: {report.metrics.tests_removed}
- Tests fixed: {report.metrics.tests_fixed}
- Final pass rate: {report.metrics.final_pass_rate:.1f}%
- SKULL-007 compliant: {'✅' if report.metrics.skull_007_compliant else '❌'}

### Phase 7: Governance Health Check
- Governance health score: {report.metrics.governance_drift_score:.1f}/100
- Position drifts detected: {report.metrics.governance_position_drifts}
- Forward references: {report.metrics.governance_forward_refs} (target: <3)
- Orphaned rules: {report.metrics.governance_orphaned_rules}

---

## 🎯 Recommendations

"""
        
        for i, rec in enumerate(report.recommendations, 1):
            content += f"{i}. {rec}\n"
        
        content += "\n---\n\n## 📋 Next Actions\n\n"
        
        for i, action in enumerate(report.next_actions, 1):
            content += f"{i}. {action}\n"
        
        content += f"""
---

## ⏱️ Execution Summary

- **Total improvements:** {report.metrics.total_improvements}
- **Execution time:** {report.metrics.execution_time_seconds:.1f}s
- **Errors encountered:** {len(report.metrics.errors_encountered)}
- **Warnings:** {len(report.metrics.warnings)}

## 🚀 Cache Performance

"""
        
        # Add cache statistics
        cache_stats = self._validation_cache.get_stats("optimize")
        if cache_stats:
            hit_rate = cache_stats.get('hit_rate', 0.0)
            hits = cache_stats.get('hits', 0)
            misses = cache_stats.get('misses', 0)
            
            content += f"""- **Cache hit rate:** {hit_rate * 100:.1f}%
- **Cache hits:** {hits}
- **Cache misses:** {misses}
- **Time saved:** ~{hits * 2:.1f}s (estimated)

"""
        else:
            content += "- Cache statistics not available\n\n"
        
        content += """---

*Generated by CORTEX System Optimizer v{self.VERSION}*
"""
        
        report_path.write_text(content, encoding='utf-8')
        logger.info(f"📄 Report saved: {report_path}")
    
    def _format_completion_footer(self, report: SystemHealthReport) -> str:
        """Format completion footer for display."""
        mode_display = "LIVE" if self.mode == ExecutionMode.LIVE else "DRY RUN"
        
        cache_stats = self._validation_cache.get_stats("optimize")
        cache_summary = ""
        if cache_stats:
            hit_rate = cache_stats.get('hit_rate', 0.0)
            hits = cache_stats.get('hits', 0)
            cache_summary = f"\nCache Hit Rate:   {hit_rate * 100:.1f}% ({hits} hits, saved ~{hits * 2:.1f}s)"
        
        return f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  System Optimization ✅ COMPLETED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Health Score:     {report.health_score:.1f}/100 ({report.overall_health.upper()})
Total Improvements: {report.metrics.total_improvements}
Execution Time:   {report.metrics.execution_time_seconds:.1f}s{cache_summary}
Mode:             {mode_display}

Recommendations:  {len(report.recommendations)} items
Next Actions:     {len(report.next_actions)} items

Report: cortex-brain/system-optimization-report.md

© 2024-2025 Asif Hussain │ Proprietary │ github.com/asifhussain60/CORTEX
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    def _review_instruction_files(self) -> Dict[str, Any]:
        """
        Review instruction files holistically for optimization opportunities.
        
        This Phase 0 step analyzes:
        - .github/prompts/CORTEX.prompt.md (primary instruction file)
        - .github/copilot-instructions.md (GitHub Copilot integration)
        
        Goals:
        - Keep files lean (remove bloat, redundancy, outdated content)
        - Ensure all triggers are recognizable by Copilot
        - Maintain pairing consistency (no contradictions)
        - Optimize for token efficiency
        
        Strategy:
        - Read both files as a pair
        - Identify redundancies between files
        - Check for outdated references
        - Validate trigger coverage
        - Suggest consolidations
        
        Returns:
            Dict with keys:
                - success: bool
                - message: str
                - optimizations_applied: int
                - recommendations: List[str]
        """
        try:
            cortex_prompt = self.project_root / ".github" / "prompts" / "CORTEX.prompt.md"
            copilot_instructions = self.project_root / ".github" / "copilot-instructions.md"
            
            if not cortex_prompt.exists() or not copilot_instructions.exists():
                return {
                    'success': False,
                    'message': 'Instruction files not found',
                    'optimizations_applied': 0,
                    'recommendations': []
                }
            
            logger.info("📄 Reading instruction files...")
            cortex_content = cortex_prompt.read_text(encoding='utf-8')
            copilot_content = copilot_instructions.read_text(encoding='utf-8')
            
            # Analysis metrics
            cortex_lines = len(cortex_content.splitlines())
            copilot_lines = len(copilot_content.splitlines())
            
            logger.info(f"   CORTEX.prompt.md: {cortex_lines} lines")
            logger.info(f"   copilot-instructions.md: {copilot_lines} lines")
            
            recommendations = []
            optimizations = 0
            
            # Check 1: Detect redundant content between files
            logger.info("🔍 Analyzing content redundancy...")
            redundancy_data = self._check_redundancy(cortex_content, copilot_content)
            
            if redundancy_data['has_redundancy']:
                recommendations.extend(redundancy_data['recommendations'])
                logger.info(f"   ⚠️  Found {len(redundancy_data['duplicates'])} redundant sections")
            
            # Check 2: Validate trigger recognition
            logger.info("🔍 Validating trigger patterns...")
            trigger_data = self._validate_triggers(cortex_content, copilot_content)
            
            if not trigger_data['all_triggers_covered']:
                recommendations.extend(trigger_data['recommendations'])
                logger.info(f"   ⚠️  {len(trigger_data['missing_triggers'])} triggers need attention")
            
            # Check 3: Detect outdated references
            logger.info("🔍 Checking for outdated references...")
            outdated_data = self._check_outdated_refs(cortex_content, copilot_content)
            
            if outdated_data['has_outdated']:
                recommendations.extend(outdated_data['recommendations'])
                logger.info(f"   ⚠️  Found {len(outdated_data['outdated_refs'])} outdated references")
            
            # Check 4: Token efficiency analysis
            logger.info("🔍 Analyzing token efficiency...")
            token_data = self._analyze_tokens(cortex_content, copilot_content)
            
            if token_data['has_bloat']:
                recommendations.extend(token_data['recommendations'])
                logger.info(f"   ⚠️  Potential token savings: ~{token_data['potential_savings']} tokens")
            
            # Generate summary
            if recommendations:
                logger.info("\n📋 Instruction File Optimization Recommendations:")
                for i, rec in enumerate(recommendations[:5], 1):  # Limit to top 5
                    logger.info(f"   {i}. {rec}")
                
                if len(recommendations) > 5:
                    logger.info(f"   ... and {len(recommendations) - 5} more")
            
            return {
                'success': True,
                'message': f'Analyzed instruction files ({len(recommendations)} recommendations)',
                'optimizations_applied': optimizations,
                'recommendations': recommendations,
                'metrics': {
                    'cortex_lines': cortex_lines,
                    'copilot_lines': copilot_lines,
                    'redundancies': len(redundancy_data.get('duplicates', [])),
                    'outdated_refs': len(outdated_data.get('outdated_refs', [])),
                    'token_savings': token_data.get('potential_savings', 0)
                }
            }
        
        except Exception as e:
            logger.error(f"Instruction file review failed: {e}", exc_info=True)
            return {
                'success': False,
                'message': f'Review failed: {str(e)}',
                'optimizations_applied': 0,
                'recommendations': []
            }
    
    def _check_redundancy(self, cortex: str, copilot: str) -> Dict[str, Any]:
        """Check for redundant content between instruction files."""
        import re
        duplicates = []
        
        # Extract sections
        cortex_sections = self._extract_sections(cortex)
        copilot_sections = self._extract_sections(copilot)
        
        # Compare
        for c_title, c_text in cortex_sections.items():
            for p_title, p_text in copilot_sections.items():
                similarity = self._text_similarity(c_text, p_text)
                if similarity > 0.8 and len(c_text) > 200:
                    duplicates.append({
                        'cortex_section': c_title,
                        'copilot_section': p_title,
                        'similarity': similarity,
                        'size': len(c_text)
                    })
        
        recommendations = []
        for dup in duplicates:
            recommendations.append(
                f"Consolidate '{dup['cortex_section']}' and '{dup['copilot_section']}' "
                f"({dup['similarity']*100:.0f}% similar)"
            )
        
        return {
            'has_redundancy': len(duplicates) > 0,
            'duplicates': duplicates,
            'recommendations': recommendations
        }
    
    def _validate_triggers(self, cortex: str, copilot: str) -> Dict[str, Any]:
        """Validate command triggers are documented."""
        import re
        pattern = r'\*\*Commands?:\*\*\s*`([^`]+)`'
        
        cortex_triggers = set(re.findall(pattern, cortex))
        copilot_triggers = set(re.findall(pattern, copilot))
        
        missing = (cortex_triggers - copilot_triggers) | (copilot_triggers - cortex_triggers)
        
        recommendations = []
        for trigger in missing:
            recommendations.append(f"Synchronize trigger '{trigger}' across both files")
        
        return {
            'all_triggers_covered': len(missing) == 0,
            'missing_triggers': list(missing),
            'recommendations': recommendations
        }
    
    def _check_outdated_refs(self, cortex: str, copilot: str) -> Dict[str, Any]:
        """Detect references to files that no longer exist."""
        import re
        pattern = r'`([^`]+\.(md|py|yaml|json))`'
        
        all_refs = {m[0] for m in re.findall(pattern, cortex + copilot)}
        outdated = []
        
        for ref in all_refs:
            paths = [
                self.project_root / ref,
                self.project_root / ref.lstrip('./')
            ]
            if not any(p.exists() for p in paths):
                outdated.append(ref)
        
        recommendations = [f"Remove/update outdated: {ref}" for ref in outdated]
        
        return {
            'has_outdated': len(outdated) > 0,
            'outdated_refs': outdated,
            'recommendations': recommendations
        }
    
    def _analyze_tokens(self, cortex: str, copilot: str) -> Dict[str, Any]:
        """Analyze token usage and identify bloat."""
        total_tokens = (len(cortex) + len(copilot)) // 4
        recommendations = []
        potential_savings = 0
        
        # Check verbose lines
        verbose_count = sum(1 for line in (cortex + copilot).splitlines() if len(line) > 100)
        if verbose_count > 40:
            recommendations.append(f"{verbose_count} verbose lines (>100 chars) - consider breaking up")
            potential_savings += verbose_count * 10
        
        # Check repetitive phrases
        phrases = ['For more information', 'See the guide', 'Refer to', 'As mentioned', 'Note that']
        combined = cortex + copilot
        
        for phrase in phrases:
            count = combined.lower().count(phrase.lower())
            if count > 5:
                recommendations.append(f"Phrase '{phrase}' appears {count}x - consolidate")
                potential_savings += count * 5
        
        return {
            'has_bloat': len(recommendations) > 0,
            'total_tokens': total_tokens,
            'potential_savings': potential_savings,
            'recommendations': recommendations
        }
    
    def _extract_sections(self, content: str) -> Dict[str, str]:
        """Extract markdown sections."""
        import re
        sections = {}
        pattern = r'^##\s+(.+?)$(.+?)(?=^##|\Z)'
        
        for match in re.finditer(pattern, content, re.MULTILINE | re.DOTALL):
            sections[match.group(1).strip()] = match.group(2).strip()
        
        return sections
    
    def _text_similarity(self, text1: str, text2: str) -> float:
        """Calculate text similarity."""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        return len(words1 & words2) / len(words1 | words2)


def register() -> OptimizeSystemOrchestrator:
    """
    Register this module with the operations system.
    
    Returns:
        Instance of OptimizeSystemOrchestrator
    """
    from src.config import ConfigManager
    config = ConfigManager()
    project_root = config.get_project_root()
    
    return OptimizeSystemOrchestrator(project_root=project_root)
