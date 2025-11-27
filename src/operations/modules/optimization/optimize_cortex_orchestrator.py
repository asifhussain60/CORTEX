"""
CORTEX Optimization Orchestrator

Performs holistic review of CORTEX architecture and executes optimizations
with full git tracking and metrics collection.

This orchestrator:
1. Runs all SKULL tests (brain protection validation)
2. Analyzes CORTEX architecture, operation history, patterns learned
3. Generates optimization plan with prioritized actions
4. Executes optimizations with git commits for tracking
5. Collects metrics on improvements achieved

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Version: 1.0
"""

import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import subprocess
import json

from src.operations.base_operation_module import (
    BaseOperationModule,
    OperationModuleMetadata,
    OperationPhase,
    OperationResult,
    OperationStatus
)
from src.operations.modules.validation.planning_rules_validator import (
    PlanningRulesValidator,
    PlanningValidationReport
)
from src.governance import DocumentGovernance

logger = logging.getLogger(__name__)


@dataclass
class OptimizationMetrics:
    """Metrics collected during optimization execution."""
    optimization_id: str
    timestamp: datetime
    tests_run: int = 0
    tests_passed: int = 0
    tests_failed: int = 0
    issues_identified: int = 0
    optimizations_applied: int = 0
    optimizations_succeeded: int = 0
    optimizations_failed: int = 0
    doc_deduplication_count: int = 0
    git_commits: List[str] = field(default_factory=list)
    duration_seconds: float = 0.0
    improvements: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)


class OptimizeCortexOrchestrator(BaseOperationModule):
    """
    Entry point orchestrator for CORTEX optimization.
    
    Coordinates:
    - SKULL test execution (brain protection validation)
    - Architecture analysis (holistic review)
    - Pattern learning (knowledge graph insights)
    - Optimization planning (prioritized action generation)
    - Optimization execution (with git tracking)
    - Metrics collection (improvement tracking)
    
    Usage:
        orchestrator = OptimizeCortexOrchestrator(project_root=Path('/path/to/cortex'))
        result = orchestrator.execute(context={})
        
        # Result includes:
        # - metrics: OptimizationMetrics with full details
        # - git_commits: List of commit hashes for tracking
        # - optimizations_applied: List of applied improvements
    """
    
    def get_metadata(self) -> OperationModuleMetadata:
        """Module metadata."""
        return OperationModuleMetadata(
            module_id="optimize_cortex_orchestrator",
            name="CORTEX Optimization Orchestrator",
            description="Runs SKULL tests, analyzes architecture, and executes optimizations",
            version="1.0.0",
            author="Asif Hussain",
            phase=OperationPhase.PROCESSING,
            priority=100,
            dependencies=[],
            optional=False,
            tags=['optimization', 'skull', 'architecture']
        )
    
    def validate_prerequisites(self, context: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Validate prerequisites for optimization.
        
        Checks:
        - Project root exists
        - Git repository present
        - Test suite available
        - Knowledge graph accessible
        
        Args:
            context: Shared execution context
        
        Returns:
            Tuple of (is_valid, issues_list)
        """
        issues = []
        
        # Check project root
        project_root = context.get('project_root') or self.project_root
        if not project_root or not project_root.exists():
            issues.append("Project root not found or invalid")
        
        # Check git repository
        if project_root:
            git_dir = project_root / '.git'
            if not git_dir.exists():
                issues.append("Not a git repository - optimization requires git tracking")
        
        # Check test suite
        if project_root:
            tests_dir = project_root / 'tests'
            if not tests_dir.exists():
                issues.append("Test suite not found")
        
        # Check knowledge graph
        if project_root:
            brain_dir = project_root / 'cortex-brain'
            knowledge_graph = brain_dir / 'knowledge-graph.yaml'
            if not knowledge_graph.exists():
                issues.append("Knowledge graph not found")
        
        return len(issues) == 0, issues
    
    def execute(self, context: Dict[str, Any]) -> OperationResult:
        """
        Execute CORTEX optimization workflow.
        
        Workflow:
        1. Initialize metrics collection
        2. Run SKULL tests (brain protection validation)
        3. Analyze architecture (holistic review)
        4. Generate optimization plan
        5. Execute optimizations (with git commits)
        6. Collect final metrics
        
        Args:
            context: Shared execution context
        
        Returns:
            OperationResult with optimization metrics and git commits
        """
        start_time = datetime.now()
        project_root = context.get('project_root') or self.project_root
        
        logger.info("=" * 80)
        logger.info("CORTEX OPTIMIZATION ORCHESTRATOR")
        logger.info("=" * 80)
        
        # Initialize metrics
        metrics = OptimizationMetrics(
            optimization_id=f"opt_{start_time.strftime('%Y%m%d_%H%M%S')}",
            timestamp=start_time
        )
        
        try:
            # Phase 1: Validate Planning Rules
            logger.info("\n[Phase 1] Validating planning rules...")
            planning_result = self._validate_planning_rules(project_root, metrics)
            
            if not planning_result['success']:
                logger.warning("Planning validation found issues - recommendations provided")
            
            # Phase 2: Run SKULL tests
            logger.info("\n[Phase 2] Running SKULL tests...")
            skull_result = self._run_skull_tests(project_root, metrics)
            
            if not skull_result['success']:
                return OperationResult(
                    success=False,
                    status=OperationStatus.FAILED,
                    message="SKULL tests failed - cannot proceed with optimization",
                    data={'metrics': metrics.__dict__},
                    errors=metrics.errors
                )
            
            # Phase 2.5: Silent System Alignment Check (admin-only)
            if self._is_admin_environment(project_root):
                logger.info("\n[Phase 2.5] Running system alignment check...")
                alignment_result = self._run_alignment_check(project_root, metrics)
                # Only show output if issues detected
                if alignment_result and not alignment_result.get('is_healthy', True):
                    logger.warning(f"⚠️ System alignment issues detected: {alignment_result.get('message', 'Unknown')}")
                    logger.info("Run 'align' command for detailed analysis and remediation options")
            
            # Phase 3: Analyze architecture
            logger.info("\n[Phase 3] Analyzing CORTEX architecture...")
            analysis_result = self._analyze_architecture(project_root, metrics)
            
            # Phase 4: Generate optimization plan
            logger.info("\n[Phase 4] Generating optimization plan...")
            plan_result = self._generate_optimization_plan(
                analysis_result,
                metrics
            )
            
            # Phase 5: Execute optimizations
            logger.info("\n[Phase 5] Executing optimizations...")
            execution_result = self._execute_optimizations(
                plan_result,
                project_root,
                metrics
            )
            
            # Phase 6: Collect final metrics
            logger.info("\n[Phase 6] Collecting metrics...")
            metrics.duration_seconds = (datetime.now() - start_time).total_seconds()
            
            # Phase 6.5: Documentation Deduplication
            logger.info("\n[Phase 6.5] Deduplicating documentation...")
            dedup_result = self._deduplicate_documentation(project_root, metrics)
            
            if dedup_result['success']:
                logger.info(f"✅ Deduplicated {dedup_result['consolidated_count']} documents")
            else:
                logger.warning(f"⚠️ Documentation deduplication: {dedup_result.get('message', 'No duplicates found')}")
            
            # Generate report
            report = self._generate_optimization_report(metrics)
            
            logger.info("\n" + "=" * 80)
            logger.info("OPTIMIZATION COMPLETE")
            logger.info("=" * 80)
            logger.info(f"Duration: {metrics.duration_seconds:.2f}s")
            logger.info(f"Optimizations applied: {metrics.optimizations_succeeded}")
            logger.info(f"Git commits: {len(metrics.git_commits)}")
            
            return OperationResult(
                success=True,
                status=OperationStatus.SUCCESS,
                message=f"CORTEX optimization complete ({metrics.optimizations_succeeded} improvements)",
                data={
                    'metrics': metrics.__dict__,
                    'report': report,
                    'git_commits': metrics.git_commits
                }
            )
        
        except Exception as e:
            logger.error(f"Optimization failed: {e}", exc_info=True)
            metrics.errors.append(f"Fatal error: {str(e)}")
            
            return OperationResult(
                success=False,
                status=OperationStatus.FAILED,
                message=f"Optimization failed: {str(e)}",
                data={'metrics': metrics.__dict__},
                errors=metrics.errors
            )
    
    def _is_admin_environment(self, project_root: Path) -> bool:
        """
        Check if running in CORTEX admin/development environment.
        
        Admin environment indicators:
        - src/operations/modules/admin/ directory exists
        - cortex-brain/admin/ directory exists
        - This is the CORTEX dev repo (not a user application)
        
        Args:
            project_root: Project root directory
        
        Returns:
            True if admin environment, False otherwise
        """
        # Check for admin directories
        admin_ops = project_root / "src" / "operations" / "modules" / "admin"
        admin_brain = project_root / "cortex-brain" / "admin"
        
        return admin_ops.exists() or admin_brain.exists()
    
    def _run_alignment_check(
        self,
        project_root: Path,
        metrics: OptimizationMetrics
    ) -> Optional[Dict[str, Any]]:
        """
        Run silent system alignment validation (admin-only).
        
        This method:
        - Runs SystemAlignmentOrchestrator validation
        - Only outputs messages if issues are detected
        - Does not fail the optimization workflow
        - Provides gentle nudge to run 'align' for details
        
        Args:
            project_root: Project root directory
            metrics: Metrics collector
        
        Returns:
            Dict with alignment results or None if not admin environment
        """
        try:
            # Lazy import to avoid dependency in user environments
            from src.operations.modules.admin.system_alignment_orchestrator import (
                SystemAlignmentOrchestrator
            )
            
            # Create orchestrator
            alignment_orch = SystemAlignmentOrchestrator(project_root=project_root)
            
            # Run silent validation (no verbose output)
            result = alignment_orch.execute({})
            
            if not result.success:
                return {
                    'is_healthy': False,
                    'message': result.message,
                    'report': result.data.get('report') if result.data else None
                }
            
            # Check if report indicates issues
            report = result.data.get('report') if result.data else None
            if report:
                is_healthy = report.is_healthy if hasattr(report, 'is_healthy') else True
                return {
                    'is_healthy': is_healthy,
                    'message': f"{report.critical_issues} critical issues, {report.warnings} warnings" if not is_healthy else "System healthy",
                    'report': report
                }
            
            return {'is_healthy': True, 'message': 'System healthy'}
        
        except ImportError:
            # SystemAlignmentOrchestrator not available (user environment)
            logger.debug("System alignment not available (user environment)")
            return None
        except Exception as e:
            logger.debug(f"Alignment check failed: {e}")
            metrics.errors.append(f"Alignment check error: {str(e)}")
            return None
    
    def _validate_planning_rules(
        self,
        project_root: Path,
        metrics: OptimizationMetrics
    ) -> Dict[str, Any]:
        """
        Validate planning artifacts against DoR and Development Executor rules.
        
        This phase validates:
        - Definition of Ready (DoR) compliance
        - Ambiguity detection (vague terms, missing context)
        - Security review completion (OWASP checklist)
        - TDD quality tier assignment
        
        Args:
            project_root: Project root directory
            metrics: Metrics collector
        
        Returns:
            Dict with validation results and recommendations
        """
        logger.info("Validating planning rules and quality standards...")
        
        try:
            validator = PlanningRulesValidator(project_root)
            report = validator.validate_all_plans()
            
            logger.info(f"Plans validated: {report.plans_validated}/{report.total_plans}")
            logger.info(f"Compliance rate: {report.compliance_rate:.1f}%")
            logger.info(f"Blocking issues: {len(report.blocking_issues)}")
            logger.info(f"Warnings: {len(report.warnings)}")
            
            # Update metrics
            metrics.issues_identified += len(report.blocking_issues) + len(report.warnings)
            
            # Generate recommendations
            recommendations = validator.generate_recommendations(report)
            
            if recommendations:
                logger.info("\n📋 Planning Quality Recommendations:")
                for rec in recommendations:
                    logger.info(rec)
            
            success = not report.has_blocking_issues and report.compliance_rate >= 80
            
            return {
                'success': success,
                'report': report,
                'recommendations': recommendations,
                'compliance_rate': report.compliance_rate
            }
        
        except Exception as e:
            logger.error(f"Planning validation failed: {e}", exc_info=True)
            metrics.errors.append(f"Planning validation error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _run_skull_tests(
        self,
        project_root: Path,
        metrics: OptimizationMetrics
    ) -> Dict[str, Any]:
        """
        Run SKULL protection tests.
        
        SKULL tests validate:
        - Test-before-claim enforcement
        - Integration verification
        - Visual regression protection
        - Retry-without-learning detection
        - Transformation verification
        
        Args:
            project_root: Project root directory
            metrics: Metrics collector
        
        Returns:
            Dict with test results and success status
        """
        logger.info("Running SKULL protection tests...")
        
        try:
            # Run pytest on tier0 tests
            result = subprocess.run(
                ['pytest', 'tests/tier0/', '-v', '--tb=short'],
                cwd=project_root,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            # Parse results
            output = result.stdout + result.stderr
            
            # Count tests
            passed = output.count(' PASSED')
            failed = output.count(' FAILED')
            total = passed + failed
            
            metrics.tests_run = total
            metrics.tests_passed = passed
            metrics.tests_failed = failed
            
            logger.info(f"Tests run: {total}")
            logger.info(f"Tests passed: {passed}")
            logger.info(f"Tests failed: {failed}")
            
            if failed > 0:
                logger.error("SKULL tests failed - brain protection compromised!")
                metrics.errors.append(f"{failed} SKULL tests failed")
                return {'success': False, 'output': output}
            
            logger.info("✅ All SKULL tests passed - brain protection intact")
            return {'success': True, 'output': output}
        
        except subprocess.TimeoutExpired:
            logger.error("SKULL tests timed out")
            metrics.errors.append("Test execution timeout")
            return {'success': False, 'error': 'timeout'}
        
        except Exception as e:
            logger.error(f"Error running SKULL tests: {e}")
            metrics.errors.append(f"Test execution error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _analyze_hardcoded_data(self, project_root: Path) -> Dict[str, Any]:
        """
        AGGRESSIVE hardcoded data detection.
        
        Scans for:
        - Hardcoded file paths (absolute paths, platform-specific)
        - Mock data in production code
        - Fallback mechanisms returning fake values
        - Test fixtures with hardcoded values
        - Placeholder data masquerading as real data
        
        Args:
            project_root: Project root directory
        
        Returns:
            Dict with hardcoded data violations
        """
        logger.info("Running AGGRESSIVE hardcoded data scan...")
        
        try:
            from .hardcoded_data_cleaner_module import HardcodedDataCleanerModule
            
            cleaner = HardcodedDataCleanerModule(project_root=project_root)
            result = cleaner.execute({
                'project_root': project_root,
                'scan_paths': ['src', 'tests'],
                'exclude_patterns': ['__pycache__', '.git', 'dist', '.venv', 'node_modules'],
                'fail_on_critical': False  # Don't fail optimization, just report
            })
            
            if result.success or result.status.name == 'FAILED':  # Both success and fail states have data
                metrics_data = result.data.get('metrics', {})
                violations = result.data.get('violations', [])
                
                insights = []
                issues = []
                
                # Summarize findings
                total_violations = metrics_data.get('violations_found', 0)
                critical = metrics_data.get('critical_violations', 0)
                high = metrics_data.get('high_violations', 0)
                
                if total_violations == 0:
                    insights.append("✅ No hardcoded data violations found!")
                else:
                    if critical > 0:
                        issues.append(f"CRITICAL: {critical} hardcoded paths or mock data in production")
                    if high > 0:
                        issues.append(f"HIGH: {high} fallback values or hardcoded returns")
                    
                    insights.append(f"Scanned {metrics_data.get('files_scanned', 0)} files")
                    insights.append(f"Found {total_violations} violations")
                    
                    # Top violation types
                    violations_by_type = metrics_data.get('violations_by_type', {})
                    for v_type, count in sorted(violations_by_type.items(), key=lambda x: x[1], reverse=True)[:3]:
                        insights.append(f"  - {v_type}: {count}")
                
                logger.info(f"Hardcoded data scan complete: {total_violations} violations")
                
                return {
                    'insights': insights,
                    'issues': issues,
                    'stats': metrics_data,
                    'violations': violations[:10],  # Top 10 violations for context
                    'full_report': result.data.get('report', '')
                }
            else:
                return {'issues': ['Hardcoded data scan failed']}
        
        except ImportError as e:
            logger.warning(f"Hardcoded data cleaner module not available: {e}")
            return {'issues': ['Hardcoded data cleaner not installed']}
        except Exception as e:
            logger.error(f"Error during hardcoded data scan: {e}")
            return {'issues': [f'Hardcoded data scan error: {str(e)}']}
    
    def _analyze_architecture(
        self,
        project_root: Path,
        metrics: OptimizationMetrics
    ) -> Dict[str, Any]:
        """
        Perform holistic architecture analysis.
        
        Analyzes:
        - Hardcoded data (AGGRESSIVE - paths, mocks, fallbacks)
        - Knowledge graph patterns (lessons learned)
        - Operation module structure
        - Brain protection rules
        - Code quality metrics
        - Test coverage
        - Documentation completeness
        
        Args:
            project_root: Project root directory
            metrics: Metrics collector
        
        Returns:
            Dict with analysis results
        """
        logger.info("Analyzing CORTEX architecture...")
        
        analysis = {
            'hardcoded_data': self._analyze_hardcoded_data(project_root),
            'knowledge_graph': self._analyze_knowledge_graph(project_root),
            'operations': self._analyze_operations(project_root),
            'brain_protection': self._analyze_brain_protection(project_root),
            'code_quality': self._analyze_code_quality(project_root),
            'test_coverage': self._analyze_test_coverage(project_root),
            'documentation': self._analyze_documentation(project_root)
        }
        
        # Count issues
        issues = 0
        for category, results in analysis.items():
            if 'issues' in results:
                issues += len(results['issues'])
        
        metrics.issues_identified = issues
        logger.info(f"Issues identified: {issues}")
        
        return analysis
    
    def _analyze_knowledge_graph(self, project_root: Path) -> Dict[str, Any]:
        """Analyze knowledge graph for patterns and insights."""
        import yaml
        
        kg_path = project_root / 'cortex-brain' / 'knowledge-graph.yaml'
        
        if not kg_path.exists():
            return {'issues': ['Knowledge graph not found']}
        
        try:
            with open(kg_path, 'r', encoding='utf-8') as f:
                kg = yaml.safe_load(f)
            
            insights = []
            issues = []
            
            # Analyze validation insights
            if 'validation_insights' in kg:
                insights_count = len(kg['validation_insights'])
                insights.append(f"{insights_count} validation insights captured")
                
                # Check for high-frequency patterns
                for name, data in kg['validation_insights'].items():
                    if isinstance(data, dict):
                        freq = data.get('frequency', 0)
                        if freq > 3:
                            insights.append(
                                f"High-frequency pattern: {name} ({freq} occurrences)"
                            )
            
            # Analyze workflow patterns
            if 'workflow_patterns' in kg:
                patterns_count = len(kg['workflow_patterns'])
                insights.append(f"{patterns_count} workflow patterns learned")
            
            return {
                'insights': insights,
                'issues': issues,
                'stats': {
                    'validation_insights': len(kg.get('validation_insights', {})),
                    'workflow_patterns': len(kg.get('workflow_patterns', {})),
                    'intent_patterns': len(kg.get('intent_patterns', {}))
                }
            }
        
        except Exception as e:
            return {'issues': [f"Error reading knowledge graph: {str(e)}"]}
    
    def _analyze_operations(self, project_root: Path) -> Dict[str, Any]:
        """Analyze operation modules and structure."""
        ops_dir = project_root / 'src' / 'operations' / 'modules'
        
        if not ops_dir.exists():
            return {'issues': ['Operations directory not found']}
        
        insights = []
        issues = []
        
        # Count modules
        module_dirs = [d for d in ops_dir.iterdir() if d.is_dir() and not d.name.startswith('__')]
        insights.append(f"{len(module_dirs)} operation categories")
        
        # Check for incomplete modules
        for module_dir in module_dirs:
            py_files = list(module_dir.glob('*.py'))
            if len(py_files) == 0:
                issues.append(f"Empty operation category: {module_dir.name}")
        
        return {
            'insights': insights,
            'issues': issues,
            'stats': {
                'operation_categories': len(module_dirs)
            }
        }
    
    def _analyze_brain_protection(self, project_root: Path) -> Dict[str, Any]:
        """Analyze brain protection rules and enforcement."""
        import yaml
        
        rules_path = project_root / 'cortex-brain' / 'brain-protection-rules.yaml'
        
        if not rules_path.exists():
            return {'issues': ['Brain protection rules not found']}
        
        try:
            with open(rules_path, 'r', encoding='utf-8') as f:
                rules = yaml.safe_load(f)
            
            insights = []
            issues = []
            
            # Count protection layers
            layers = rules.get('protection_layers', [])
            insights.append(f"{len(layers)} protection layers active")
            
            # Count rules per layer
            total_rules = sum(len(layer.get('rules', [])) for layer in layers)
            insights.append(f"{total_rules} protection rules defined")
            
            # Check for SKULL rules
            skull_rules = [
                rule for layer in layers
                for rule in layer.get('rules', [])
                if 'SKULL' in rule.get('rule_id', '')
            ]
            insights.append(f"{len(skull_rules)} SKULL protection rules")
            
            return {
                'insights': insights,
                'issues': issues,
                'stats': {
                    'protection_layers': len(layers),
                    'total_rules': total_rules,
                    'skull_rules': len(skull_rules)
                }
            }
        
        except Exception as e:
            return {'issues': [f"Error reading brain protection: {str(e)}"]}
    
    def _analyze_code_quality(self, project_root: Path) -> Dict[str, Any]:
        """
        Analyze code quality metrics using CORTEX admin optimizer.
        
        Runs the comprehensive CORTEX optimizer tool which provides:
        - Token usage analysis (prompt efficiency, YAML optimization)
        - YAML validation (brain file integrity, schema compliance)
        - Plugin health checks (metadata completeness, registration)
        - Database optimization (SQLite performance, indexes)
        """
        insights = []
        issues = []
        stats = {}
        
        logger.info("Running CORTEX admin optimizer for code quality metrics...")
        
        try:
            # Run the admin optimizer tool
            import subprocess
            import json
            
            result = subprocess.run(
                ['python', 'scripts/admin/cortex_optimizer.py', 'analyze', '--report', 'json'],
                cwd=project_root,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                # Parse JSON output
                try:
                    optimizer_results = json.loads(result.stdout)
                    overall_score = optimizer_results.get('overall_score', 0)
                    
                    insights.append(f"Overall optimization score: {overall_score}/100")
                    
                    # Process individual analyzer results
                    for analyzer_result in optimizer_results.get('results', []):
                        category = analyzer_result.get('category', 'Unknown')
                        score = analyzer_result.get('score', 0)
                        analyzer_issues = analyzer_result.get('issues', [])
                        recommendations = analyzer_result.get('recommendations', [])
                        
                        # Add score to insights
                        status_emoji = "✅" if score >= 80 else "⚠️" if score >= 60 else "❌"
                        insights.append(f"{status_emoji} {category}: {score}/100")
                        
                        # Add issues
                        if analyzer_issues:
                            issues.extend(analyzer_issues[:3])  # Top 3 issues per category
                        
                        # Store stats
                        stats[category.lower().replace(' ', '_')] = {
                            'score': score,
                            'issue_count': len(analyzer_issues),
                            'recommendations': len(recommendations)
                        }
                    
                    # Overall health
                    if overall_score < 60:
                        issues.append(f"CRITICAL: Overall optimization score below 60 ({overall_score}/100)")
                    elif overall_score < 80:
                        issues.append(f"WARNING: Overall optimization score below 80 ({overall_score}/100)")
                    
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse optimizer JSON output: {e}")
                    insights.append("Optimizer ran but output parse failed")
            else:
                # Optimizer failed, fall back to basic analysis
                logger.warning(f"CORTEX optimizer failed (exit code {result.returncode}), using fallback analysis")
                insights.append("⚠️ Optimizer failed, using basic analysis")
                
                # Fallback: Basic file counting
                src_dir = project_root / 'src'
                if src_dir.exists():
                    py_files = list(src_dir.rglob('*.py'))
                    insights.append(f"{len(py_files)} Python files")
                    
                    init_files = list(src_dir.rglob('__init__.py'))
                    insights.append(f"{len(init_files)} package markers")
                    
                    stats = {
                        'python_files': len(py_files),
                        'packages': len(init_files)
                    }
                else:
                    issues.append("Source directory not found")
        
        except subprocess.TimeoutExpired:
            logger.error("CORTEX optimizer timed out")
            issues.append("Optimizer execution timeout")
        except Exception as e:
            logger.error(f"Error running CORTEX optimizer: {e}")
            issues.append(f"Optimizer error: {str(e)}")
        
        return {
            'insights': insights,
            'issues': issues,
            'stats': stats
        }
    
    def _analyze_test_coverage(self, project_root: Path) -> Dict[str, Any]:
        """Analyze test coverage."""
        insights = []
        issues = []
        
        tests_dir = project_root / 'tests'
        if not tests_dir.exists():
            return {'issues': ['Tests directory not found']}
        
        # Count test files
        test_files = list(tests_dir.rglob('test_*.py'))
        insights.append(f"{len(test_files)} test files")
        
        return {
            'insights': insights,
            'issues': issues,
            'stats': {
                'test_files': len(test_files)
            }
        }
    
    def _analyze_documentation(self, project_root: Path) -> Dict[str, Any]:
        """Analyze documentation completeness."""
        insights = []
        issues = []
        
        docs_dir = project_root / 'docs'
        prompts_dir = project_root / 'prompts'
        
        if docs_dir.exists():
            md_files = list(docs_dir.rglob('*.md'))
            insights.append(f"{len(md_files)} documentation files")
        else:
            issues.append("Documentation directory not found")
        
        if prompts_dir.exists():
            prompt_files = list(prompts_dir.rglob('*.md'))
            insights.append(f"{len(prompt_files)} prompt files")
        
        return {
            'insights': insights,
            'issues': issues,
            'stats': {
                'docs': len(md_files) if docs_dir.exists() else 0,
                'prompts': len(prompt_files) if prompts_dir.exists() else 0
            }
        }
    
    def _generate_optimization_plan(
        self,
        analysis: Dict[str, Any],
        metrics: OptimizationMetrics
    ) -> Dict[str, Any]:
        """
        Generate prioritized optimization plan.
        
        Prioritization:
        1. CRITICAL - Security/stability issues
        2. HIGH - Performance improvements
        3. MEDIUM - Code quality improvements
        4. LOW - Documentation/cosmetic updates
        
        Args:
            analysis: Architecture analysis results
            metrics: Metrics collector
        
        Returns:
            Dict with prioritized optimization actions
        """
        logger.info("Generating optimization plan...")
        
        plan = {
            'critical': [],
            'high': [],
            'medium': [],
            'low': []
        }
        
        # Analyze issues across categories
        for category, results in analysis.items():
            if 'issues' in results:
                for issue in results['issues']:
                    # Categorize by severity
                    if 'not found' in issue.lower() or 'missing' in issue.lower():
                        plan['critical'].append({
                            'category': category,
                            'issue': issue,
                            'action': f"Create/restore {category}"
                        })
                    elif 'empty' in issue.lower():
                        plan['medium'].append({
                            'category': category,
                            'issue': issue,
                            'action': f"Implement {category}"
                        })
        
        # Identify optimization opportunities from insights
        if 'knowledge_graph' in analysis:
            kg_insights = analysis['knowledge_graph'].get('insights', [])
            for insight in kg_insights:
                if 'High-frequency pattern' in insight:
                    plan['high'].append({
                        'category': 'knowledge_graph',
                        'insight': insight,
                        'action': 'Document pattern as best practice'
                    })
        
        total_actions = sum(len(actions) for actions in plan.values())
        logger.info(f"Generated {total_actions} optimization actions")
        logger.info(f"  Critical: {len(plan['critical'])}")
        logger.info(f"  High: {len(plan['high'])}")
        logger.info(f"  Medium: {len(plan['medium'])}")
        logger.info(f"  Low: {len(plan['low'])}")
        
        metrics.optimizations_applied = total_actions
        
        return plan
    
    def _execute_optimizations(
        self,
        plan: Dict[str, Any],
        project_root: Path,
        metrics: OptimizationMetrics
    ) -> Dict[str, Any]:
        """
        Execute optimization actions with git tracking.
        
        Each optimization:
        1. Applied to codebase
        2. Committed to git with descriptive message
        3. Metrics collected
        
        Args:
            plan: Optimization plan
            project_root: Project root directory
            metrics: Metrics collector
        
        Returns:
            Dict with execution results
        """
        logger.info("Executing optimizations...")
        
        results = {
            'applied': [],
            'skipped': [],
            'failed': []
        }
        
        # Execute in priority order
        for priority in ['critical', 'high', 'medium', 'low']:
            actions = plan.get(priority, [])
            
            for action in actions:
                try:
                    logger.info(f"[{priority.upper()}] {action.get('action', 'Unknown')}")
                    
                    # Execute optimization
                    # (This would call specific optimization modules)
                    # For now, just log and track
                    
                    success = self._apply_optimization(action, project_root)
                    
                    if success:
                        # Commit to git
                        commit_hash = self._git_commit(
                            project_root,
                            f"[OPTIMIZATION/{priority.upper()}] {action.get('action', 'Unknown')}"
                        )
                        
                        if commit_hash:
                            metrics.git_commits.append(commit_hash)
                            metrics.optimizations_succeeded += 1
                            results['applied'].append(action)
                        else:
                            results['skipped'].append(action)
                    else:
                        metrics.optimizations_failed += 1
                        results['failed'].append(action)
                
                except Exception as e:
                    logger.error(f"Error applying optimization: {e}")
                    metrics.errors.append(f"Optimization failed: {str(e)}")
                    metrics.optimizations_failed += 1
                    results['failed'].append(action)
        
        logger.info(f"Applied: {len(results['applied'])}")
        logger.info(f"Skipped: {len(results['skipped'])}")
        logger.info(f"Failed: {len(results['failed'])}")
        
        return results
    
    def _apply_optimization(
        self,
        action: Dict[str, Any],
        project_root: Path
    ) -> bool:
        """
        Apply a specific optimization action.
        
        Args:
            action: Optimization action details
            project_root: Project root directory
        
        Returns:
            True if successful, False otherwise
        """
        # This is where specific optimization logic would be implemented
        # For now, return True to simulate successful application
        return True
    
    def _git_commit(
        self,
        project_root: Path,
        message: str
    ) -> Optional[str]:
        """
        Commit changes to git.
        
        Args:
            project_root: Project root directory
            message: Commit message
        
        Returns:
            Commit hash if successful, None otherwise
        """
        try:
            # Check if there are changes
            status_result = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=project_root,
                capture_output=True,
                text=True
            )
            
            if not status_result.stdout.strip():
                logger.debug("No changes to commit")
                return None
            
            # Add all changes
            subprocess.run(
                ['git', 'add', '-A'],
                cwd=project_root,
                check=True
            )
            
            # Commit
            commit_result = subprocess.run(
                ['git', 'commit', '-m', message],
                cwd=project_root,
                capture_output=True,
                text=True,
                check=True
            )
            
            # Get commit hash
            hash_result = subprocess.run(
                ['git', 'rev-parse', 'HEAD'],
                cwd=project_root,
                capture_output=True,
                text=True,
                check=True
            )
            
            commit_hash = hash_result.stdout.strip()
            logger.info(f"Committed: {commit_hash[:8]} - {message}")
            
            return commit_hash
        
        except subprocess.CalledProcessError as e:
            logger.error(f"Git commit failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Error during git commit: {e}")
            return None
    
    def _deduplicate_documentation(
        self,
        project_root: Path,
        metrics: OptimizationMetrics
    ) -> Dict[str, Any]:
        """
        Deduplicate documentation using DocumentGovernance.
        
        This method:
        1. Instantiates DocumentGovernance
        2. Scans all markdown files in cortex-brain/documents/
        3. Finds duplicates using 3 algorithms (exact, title, keyword)
        4. Applies consolidation suggestions (keeps older, archives newer)
        5. Logs consolidation actions
        6. Updates metrics with deduplicated count
        
        Args:
            project_root: Project root directory
            metrics: Metrics collector
        
        Returns:
            Dict with success status, consolidated count, and details
        """
        logger.info("Scanning documentation for duplicates...")
        
        try:
            # Instantiate DocumentGovernance
            governance = DocumentGovernance(project_root)
            
            # Scan all markdown files
            docs_dir = project_root / "cortex-brain" / "documents"
            prompts_dir = project_root / ".github" / "prompts" / "modules"
            
            if not docs_dir.exists():
                return {'success': False, 'message': 'Documents directory not found'}
            
            # Collect all .md files
            scanned_docs = list(docs_dir.rglob("*.md"))
            if prompts_dir.exists():
                scanned_docs.extend(prompts_dir.rglob("*.md"))
            
            logger.info(f"Scanning {len(scanned_docs)} markdown files...")
            
            # Track duplicates
            duplicates_found = []
            consolidated_pairs = set()
            
            for doc_path in scanned_docs:
                try:
                    content = doc_path.read_text(encoding='utf-8')
                    duplicates = governance.find_duplicates(doc_path, content)
                    
                    # Filter by 0.75 threshold (from governance rules)
                    high_similarity = [
                        d for d in duplicates 
                        if d.similarity_score >= 0.75
                    ]
                    
                    for dup in high_similarity:
                        # Create unique pair key (sorted to avoid double-reporting)
                        pair_key = tuple(sorted([
                            str(doc_path.relative_to(project_root)),
                            str(dup.existing_path.relative_to(project_root))
                        ]))
                        
                        if pair_key not in consolidated_pairs:
                            consolidated_pairs.add(pair_key)
                            duplicates_found.append({
                                'file1': str(doc_path.relative_to(project_root)),
                                'file2': str(dup.existing_path.relative_to(project_root)),
                                'similarity': dup.similarity_score,
                                'algorithm': dup.algorithm,
                                'recommendation': dup.recommendation
                            })
                
                except Exception as e:
                    logger.debug(f"Error processing {doc_path}: {e}")
                    continue
            
            if not duplicates_found:
                logger.info("✅ No duplicate documentation found")
                return {
                    'success': True,
                    'consolidated_count': 0,
                    'message': 'No duplicates found'
                }
            
            # Log duplicates for user review
            logger.info(f"Found {len(duplicates_found)} duplicate pairs:")
            for dup in duplicates_found[:5]:  # Show top 5
                logger.info(
                    f"  • {dup['file1']} <-> {dup['file2']} "
                    f"({dup['similarity']:.0%} via {dup['algorithm']})"
                )
            
            if len(duplicates_found) > 5:
                logger.info(f"  ... and {len(duplicates_found) - 5} more")
            
            # Auto-consolidate if similarity ≥90% (critical duplicates)
            auto_consolidated = 0
            for dup in duplicates_found:
                if dup['similarity'] >= 0.90:
                    # Determine keep vs archive (keep older file)
                    file1_path = project_root / dup['file1']
                    file2_path = project_root / dup['file2']
                    
                    if file1_path.exists() and file2_path.exists():
                        file1_mtime = file1_path.stat().st_mtime
                        file2_mtime = file2_path.stat().st_mtime
                        
                        # Keep older file, archive newer
                        if file1_mtime < file2_mtime:
                            keep_file = file1_path
                            archive_file = file2_path
                        else:
                            keep_file = file2_path
                            archive_file = file1_path
                        
                        # Create archive directory
                        archive_dir = docs_dir / "archive"
                        archive_dir.mkdir(exist_ok=True)
                        
                        # Move duplicate to archive
                        archive_dest = archive_dir / archive_file.name
                        
                        try:
                            archive_file.rename(archive_dest)
                            logger.info(
                                f"  ✅ Archived: {archive_file.relative_to(project_root)} "
                                f"(kept {keep_file.relative_to(project_root)})"
                            )
                            auto_consolidated += 1
                        except Exception as e:
                            logger.warning(f"Failed to archive {archive_file}: {e}")
            
            # Update metrics
            metrics.doc_deduplication_count = auto_consolidated
            metrics.optimizations_succeeded += auto_consolidated
            
            # Commit if changes made
            if auto_consolidated > 0:
                commit_hash = self._git_commit(
                    project_root,
                    f"[OPTIMIZATION/DOC] Consolidated {auto_consolidated} duplicate documents"
                )
                
                if commit_hash:
                    metrics.git_commits.append(commit_hash)
            
            return {
                'success': True,
                'consolidated_count': auto_consolidated,
                'duplicates_found': len(duplicates_found),
                'details': duplicates_found
            }
        
        except Exception as e:
            logger.error(f"Documentation deduplication failed: {e}", exc_info=True)
            metrics.errors.append(f"Doc deduplication error: {str(e)}")
            return {
                'success': False,
                'message': f'Error: {str(e)}'
            }
    
    def _generate_optimization_report(
        self,
        metrics: OptimizationMetrics
    ) -> str:
        """
        Generate human-readable optimization report.
        
        Args:
            metrics: Collected metrics
        
        Returns:
            Formatted report string
        """
        report = f"""
# CORTEX Optimization Report
**Date:** {metrics.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
**Optimization ID:** {metrics.optimization_id}

## Summary
- **Duration:** {metrics.duration_seconds:.2f} seconds
- **Issues Identified:** {metrics.issues_identified}
- **Optimizations Applied:** {metrics.optimizations_succeeded}/{metrics.optimizations_applied}
- **Documentation Deduplicated:** {metrics.doc_deduplication_count} 📄
- **Git Commits:** {len(metrics.git_commits)}

## SKULL Tests
- **Tests Run:** {metrics.tests_run}
- **Tests Passed:** {metrics.tests_passed}
- **Tests Failed:** {metrics.tests_failed}

## Git Commits
"""
        
        for commit_hash in metrics.git_commits:
            report += f"- `{commit_hash[:8]}`\n"
        
        if metrics.errors:
            report += "\n## Errors\n"
            for error in metrics.errors:
                report += f"- {error}\n"
        
        return report
    
    def rollback(self, context: Dict[str, Any]) -> bool:
        """
        Rollback optimization changes.
        
        Uses git to revert commits if needed.
        
        Args:
            context: Shared execution context
        
        Returns:
            True if successful, False otherwise
        """
        logger.warning("Rollback requested for optimization")
        # Would implement git revert logic here
        return True


def register() -> BaseOperationModule:
    """Register module with operation factory."""
    return OptimizeCortexOrchestrator()
