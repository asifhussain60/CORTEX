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
from dataclasses import dataclass, field
import logging
import json
import subprocess

from src.operations.base_operation_module import (
    BaseOperationModule,
    OperationPhase,
    OperationResult,
    OperationModuleMetadata,
    OperationStatus,
    ExecutionMode
)
from src.operations.dry_run_mixin import DryRunOrchestratorMixin
from src.operations.header_formatter import HeaderFormatter

logger = logging.getLogger(__name__)


@dataclass
class OptimizationMetrics:
    """Comprehensive optimization metrics from all phases."""
    # Phase 1: Design Sync
    design_drift_resolved: int = 0
    modules_synced: int = 0
    status_files_consolidated: int = 0
    
    # Phase 2: Code Health
    obsolete_tests_identified: int = 0
    dead_code_removed: int = 0
    coverage_gaps_identified: int = 0
    
    # Phase 3: Brain Tuning
    tier_violations_fixed: int = 0
    low_confidence_patterns_pruned: int = 0
    duplicate_patterns_merged: int = 0
    protection_rules_validated: bool = False
    
    # Phase 4: Entry Point Alignment
    orchestrators_aligned: int = 0
    commands_registered: int = 0
    entry_points_synced: int = 0
    
    # Phase 5: Test Suite Optimization
    tests_removed: int = 0
    tests_fixed: int = 0
    final_pass_rate: float = 0.0
    skull_007_compliant: bool = False
    
    # Overall
    total_improvements: int = 0
    execution_time_seconds: float = 0.0
    errors_encountered: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class SystemHealthReport:
    """Comprehensive system health report."""
    timestamp: datetime
    overall_health: str  # excellent, good, fair, poor, critical
    health_score: float  # 0.0 to 100.0
    metrics: OptimizationMetrics
    recommendations: List[str] = field(default_factory=list)
    next_actions: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'timestamp': self.timestamp.isoformat(),
            'overall_health': self.overall_health,
            'health_score': self.health_score,
            'metrics': {
                'design_sync': {
                    'drift_resolved': self.metrics.design_drift_resolved,
                    'modules_synced': self.metrics.modules_synced,
                    'status_files_consolidated': self.metrics.status_files_consolidated
                },
                'code_health': {
                    'obsolete_tests_identified': self.metrics.obsolete_tests_identified,
                    'dead_code_removed': self.metrics.dead_code_removed,
                    'coverage_gaps_identified': self.metrics.coverage_gaps_identified
                },
                'brain_tuning': {
                    'tier_violations_fixed': self.metrics.tier_violations_fixed,
                    'patterns_pruned': self.metrics.low_confidence_patterns_pruned,
                    'patterns_merged': self.metrics.duplicate_patterns_merged,
                    'protection_rules_validated': self.metrics.protection_rules_validated
                },
                'entry_point_alignment': {
                    'orchestrators_aligned': self.metrics.orchestrators_aligned,
                    'commands_registered': self.metrics.commands_registered,
                    'entry_points_synced': self.metrics.entry_points_synced
                },
                'test_suite': {
                    'tests_removed': self.metrics.tests_removed,
                    'tests_fixed': self.metrics.tests_fixed,
                    'final_pass_rate': self.metrics.final_pass_rate,
                    'skull_007_compliant': self.metrics.skull_007_compliant
                }
            },
            'total_improvements': self.metrics.total_improvements,
            'execution_time': self.metrics.execution_time_seconds,
            'errors': self.metrics.errors_encountered,
            'warnings': self.metrics.warnings,
            'recommendations': self.recommendations,
            'next_actions': self.next_actions
        }


class OptimizeSystemOrchestrator(DryRunOrchestratorMixin, BaseOperationModule):
    """
    Meta-level orchestrator for comprehensive CORTEX system optimization.
    
    Coordinates 6 optimization phases:
    
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
    
    Usage:
        orchestrator = OptimizeSystemOrchestrator(project_root=Path('/path/to/cortex'))
        result = orchestrator.execute(context={'profile': 'comprehensive', 'mode': 'live'})
    """
    
    VERSION = "1.0.0"
    
    def __init__(self, project_root: Path, mode: ExecutionMode = ExecutionMode.LIVE):
        """
        Initialize system optimizer.
        
        Args:
            project_root: CORTEX project root directory
            mode: Execution mode (LIVE or DRY_RUN)
        """
        super().__init__()
        self.project_root = project_root
        self.mode = mode
        self.metrics = OptimizationMetrics()
        self.start_time = None
    
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
        
        # Check project root
        if not self.project_root.exists():
            issues.append(f"Project root not found: {self.project_root}")
        
        # Check required orchestrators
        design_sync = self.project_root / "src" / "operations" / "modules" / "design_sync" / "design_sync_orchestrator.py"
        optimize_cortex = self.project_root / "src" / "operations" / "modules" / "optimize" / "optimize_cortex_orchestrator.py"
        
        if not design_sync.exists():
            issues.append("design_sync_orchestrator.py not found")
        
        if not optimize_cortex.exists():
            issues.append("optimize_cortex_orchestrator.py not found")
        
        # Check git
        git_dir = self.project_root / ".git"
        if not git_dir.exists():
            issues.append("Not a git repository")
        
        # Check brain directories
        brain_dir = self.project_root / "cortex-brain"
        if not brain_dir.exists():
            issues.append("cortex-brain directory not found")
        
        if issues:
            return OperationResult(
                module_id=self.metadata.module_id,
                phase=OperationPhase.PRE_VALIDATION,
                status=OperationStatus.FAILED,
                success=False,
                message=f"Prerequisites validation failed: {', '.join(issues)}",
                error="\n".join(issues)
            )
        
        logger.info("✅ Prerequisites validated successfully")
        return OperationResult(
            module_id=self.metadata.module_id,
            phase=OperationPhase.PRE_VALIDATION,
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
                - mode: Execution mode ('live' or 'dry_run')
                - skip_phases: Optional list of phases to skip
        
        Returns:
            OperationResult with optimization status and metrics
        """
        self.start_time = datetime.now()
        
        # Extract context
        profile = context.get('profile', 'comprehensive')
        mode_str = context.get('mode', 'live')
        self.mode = ExecutionMode.LIVE if mode_str == 'live' else ExecutionMode.DRY_RUN
        skip_phases = context.get('skip_phases', [])
        
        # Print header
        mode_display = "LIVE" if self.mode == ExecutionMode.LIVE else "DRY RUN"
        header = HeaderFormatter.format_minimalist(
            operation_name="System Optimization",
            version=self.VERSION,
            profile=profile,
            mode=mode_display,
            timestamp=self.start_time
        )
        print(header)
        
        logger.info(f"System Optimization started | Profile: {profile} | Mode: {mode_display}")
        
        try:
            # Phase 1: Validate prerequisites
            logger.info("\n[Phase 1/6] Validating prerequisites...")
            prereq_result = self.validate_prerequisites(context)
            if not prereq_result.success:
                return prereq_result
            
            # Phase 2: Design Sync
            if 'design_sync' not in skip_phases:
                logger.info("\n[Phase 2/6] Running design synchronization...")
                self._run_design_sync(context)
            else:
                logger.info("\n[Phase 2/6] Design sync skipped (per user request)")
            
            # Phase 3: Code Health
            if 'code_health' not in skip_phases:
                logger.info("\n[Phase 3/6] Analyzing code health...")
                self._run_code_health_analysis(context)
            else:
                logger.info("\n[Phase 3/6] Code health analysis skipped (per user request)")
            
            # Phase 4: Brain Tuning
            if 'brain_tuning' not in skip_phases:
                logger.info("\n[Phase 4/6] Tuning brain tiers...")
                self._run_brain_tuning(context)
            else:
                logger.info("\n[Phase 4/6] Brain tuning skipped (per user request)")
            
            # Phase 5: Entry Point Alignment
            if 'entry_point_alignment' not in skip_phases:
                logger.info("\n[Phase 5/6] Aligning entry points...")
                self._run_entry_point_alignment(context)
            else:
                logger.info("\n[Phase 5/6] Entry point alignment skipped (per user request)")
            
            # Phase 6: Test Suite Optimization
            if 'test_suite' not in skip_phases:
                logger.info("\n[Phase 6/6] Optimizing test suite...")
                self._run_test_suite_optimization(context)
            else:
                logger.info("\n[Phase 6/6] Test suite optimization skipped (per user request)")
            
            # Calculate metrics
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
                module_id=self.metadata.module_id,
                phase=OperationPhase.FINALIZATION,
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
                module_id=self.metadata.module_id,
                phase=OperationPhase.PROCESSING,
                status=OperationStatus.FAILED,
                success=False,
                message=f"System optimization failed: {e}",
                error=str(e),
                data={'metrics': self.metrics}
            )
    
    def _run_design_sync(self, context: Dict[str, Any]) -> None:
        """Run design synchronization (Phase 2)."""
        try:
            from src.operations.modules.design_sync.design_sync_orchestrator import DesignSyncOrchestrator
            
            logger.info("🔄 Initializing design synchronization...")
            
            # Create orchestrator
            design_sync = DesignSyncOrchestrator(project_root=self.project_root)
            
            # Execute with current mode
            sync_context = {
                'profile': context.get('profile', 'standard'),
                'mode': 'dry_run' if self.mode == ExecutionMode.DRY_RUN else 'live'
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
            from src.operations.modules.optimize.optimize_cortex_orchestrator import OptimizeCortexOrchestrator
            
            logger.info("🔍 Analyzing code health...")
            
            # Create orchestrator
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
    
    def _run_brain_tuning(self, context: Dict[str, Any]) -> None:
        """Run brain tuning operations (Phase 4)."""
        # TODO: Implement brain tuning module
        logger.info("⏩ Brain tuning implementation pending...")
        self.metrics.warnings.append("Brain tuning not yet implemented")
    
    def _run_entry_point_alignment(self, context: Dict[str, Any]) -> None:
        """Run entry point alignment (Phase 5)."""
        # TODO: Implement entry point alignment module
        logger.info("⏩ Entry point alignment implementation pending...")
        self.metrics.warnings.append("Entry point alignment not yet implemented")
    
    def _run_test_suite_optimization(self, context: Dict[str, Any]) -> None:
        """Run test suite optimization (Phase 6)."""
        # TODO: Implement test suite optimization module
        logger.info("⏩ Test suite optimization implementation pending...")
        self.metrics.warnings.append("Test suite optimization not yet implemented")
    
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
        # Calculate health score (0-100)
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

---

*Generated by CORTEX System Optimizer v{self.VERSION}*
"""
        
        report_path.write_text(content, encoding='utf-8')
        logger.info(f"📄 Report saved: {report_path}")
    
    def _format_completion_footer(self, report: SystemHealthReport) -> str:
        """Format completion footer for display."""
        mode_display = "LIVE" if self.mode == ExecutionMode.LIVE else "DRY RUN"
        
        return f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  System Optimization ✅ COMPLETED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Health Score:     {report.health_score:.1f}/100 ({report.overall_health.upper()})
Total Improvements: {report.metrics.total_improvements}
Execution Time:   {report.metrics.execution_time_seconds:.1f}s
Mode:             {mode_display}

Recommendations:  {len(report.recommendations)} items
Next Actions:     {len(report.next_actions)} items

Report: cortex-brain/system-optimization-report.md

© 2024-2025 Asif Hussain │ Proprietary │ github.com/asifhussain60/CORTEX
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""


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
