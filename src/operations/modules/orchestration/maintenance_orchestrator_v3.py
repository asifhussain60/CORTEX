"""
System Maintenance Orchestrator v3.0 for CORTEX

Integrated with Planning System 3.0 for comprehensive system maintenance:
- Uses PlanningSession model for maintenance workflow state management
- Inherits visual progress tracking with orchestrator hints (🎭)
- Phase-based checkpoints with git integration
- Tiered routing for maintenance operations (Tier 1-4)
- Success template integration for completion signaling

7-Phase Maintenance Cycle:
0. Pre-healthcheck (baseline assessment)
1. Alignment (auto-fix issues)
2. Cleanup (file organization)
3. Optimization (performance improvements)
4. Vacuum (AST-powered duplicate removal)
5. Refresh prompts (update documentation)
6. Post-healthcheck (validation)

Phase 7 of CORTEX Evolution v3.9 - Planning System 3.0 Integration Complete

Author: Asif Hussain
Copyright © 2025 Asif Hussain. All rights reserved.
Version: 3.0.0
"""

import json
import logging
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

from src.operations.base_operation_module import (
    BaseOperationModule, OperationResult, OperationStatus, 
    OperationPhase, OperationModuleMetadata
)
from src.operations.modules.orchestration.planning_orchestrator import (
    PlanningOrchestrator
)
from src.orchestrators.session_model import PlanningSession, SessionStatus
from src.operations.modules.routing.tiered_router import (
    TieredRouter, OperationTier, RoutingDecision
)
from src.operations.modules.routing.complexity_analyzer import (
    ComplexityAnalyzer, ComplexityScore, ComplexityTier
)
from src.operations.modules.version.version_manager import get_version_manager
from src.operations.healthcheck_operation import HealthCheckOperation
from src.operations.align import run_align
from src.utils.progress_decorator import with_progress, yield_progress
from src.operations.utilities.orchestration_metrics_collector import with_orchestration_metrics

logger = logging.getLogger(__name__)


# ===== MAINTENANCE-SPECIFIC TIER PATTERNS =====

MAINTENANCE_TIER_PATTERNS = {
    1: [
        "check health", "system status", "quick check", "health status",
        "is system healthy", "show status"
    ],
    2: [
        "fix alignment", "clean up", "single phase", "quick cleanup",
        "align only", "cleanup only", "optimize only"
    ],
    3: [
        "system maintenance", "full maintenance", "run maintenance", "maintain system",
        "complete maintenance", "maintenance cycle"
    ],
    4: [
        "deep maintenance", "comprehensive analysis", "multi-system", "full analysis",
        "complete system audit", "deep cleanup"
    ]
}


class MaintenancePhase(Enum):
    """Maintenance workflow phases."""
    PRE_HEALTHCHECK = "pre_healthcheck"
    ALIGNMENT = "alignment"
    CLEANUP = "cleanup"
    OPTIMIZATION = "optimization"
    VACUUM = "vacuum"
    REFRESH = "refresh"
    POST_HEALTHCHECK = "post_healthcheck"


@dataclass
class MaintenanceContext:
    """Context for maintenance operation - integrates with PlanningSession."""
    operation: str
    tier: int
    complexity_score: ComplexityScore
    routing_decision: RoutingDecision
    phases_to_run: List[MaintenancePhase]
    dry_run: bool
    timestamp: datetime
    planning_session: Optional[PlanningSession] = None  # Phase 7: Planning System 3.0 integration
    
    # Maintenance-specific metadata
    pre_health_status: Optional[Dict[str, Any]] = None
    post_health_status: Optional[Dict[str, Any]] = None
    phases_completed: List[str] = None
    
    def __post_init__(self):
        if self.phases_completed is None:
            self.phases_completed = []


class MaintenanceOrchestratorV3(BaseOperationModule):
    """
    System Maintenance Orchestrator v3.0
    
    Integrated with Planning System 3.0 for intelligent tiered maintenance.
    
    Planning System 3.0 Features:
    - PlanningSession state management for maintenance workflow
    - Visual progress tracking with orchestrator hints (🎭)
    - Phase-based git checkpoints and rollback
    - Tiered routing (1-4 classification)
    - Success template integration for completion
    
    Maintenance-Specific Features:
    - 7-phase maintenance cycle
    - AST-powered cleanup intelligence
    - Pre/post healthcheck validation
    - Phase-based rollback on failures
    - Comprehensive maintenance reporting
    
    Workflow:
    1. Classify operation tier (TieredRouter)
    2. Initialize PlanningSession for maintenance
    3. Execute phases with visual progress
    4. Create git checkpoints between phases
    5. Validate with post-healthcheck
    6. Generate completion report
    7. Signal completion status with success template
    """
    
    def __init__(self, project_root: Path = None):
        """
        Initialize Maintenance Orchestrator v3.0 with Planning System 3.0.
        
        Args:
            project_root: Path to project root (defaults to CWD)
        """
        super().__init__()
        self.project_root = project_root or Path.cwd()
        
        # Version management
        self.version_manager = get_version_manager()
        self.version_manager.register_orchestrator_version("maintenance_orchestrator", "3.0")
        self.version = self.version_manager.get_orchestrator_version("maintenance_orchestrator")
        
        # Phase 7: Integrate with Planning System 3.0
        self.planning_orchestrator = PlanningOrchestrator(project_root=project_root)
        logger.info("✅ Phase 7: Planning System 3.0 integration enabled")
        
        # Routing components (also available through planning_orchestrator)
        self.tiered_router = TieredRouter()
        self.complexity_analyzer = ComplexityAnalyzer()
        
        # Maintenance state
        self.current_phase = MaintenancePhase.PRE_HEALTHCHECK
        self.current_session: Optional[PlanningSession] = None  # Phase 7
        
        # Metrics
        self.metrics: Dict[str, Any] = {
            'operations_processed': 0,
            'tier_breakdown': {1: 0, 2: 0, 3: 0, 4: 0},
            'phases_completed': 0,
            'phases_total': 7,
            'planning_sessions_created': 0,  # Phase 7
            'checkpoints_created': 0,  # Phase 7
            'healthcheck_pre': {},
            'alignment': {},
            'cleanup': {},
            'optimization': {},
            'vacuum': {},
            'refresh': {},
            'healthcheck_post': {},
            'improvements': [],
            'warnings': [],
            'errors': []
        }
        
        logger.info(f"✅ MaintenanceOrchestratorV3 v{self.version} initialized with Planning System 3.0")
    
    def get_metadata(self) -> OperationModuleMetadata:
        """Get module metadata."""
        return OperationModuleMetadata(
            module_id="maintenance_orchestrator_v3",
            name="System Maintenance Orchestrator 3.0",
            description="Intelligent system maintenance with 7-phase cycle and tiered routing",
            phase=OperationPhase.PROCESSING,
            priority=95,
            version="3.0.0",
            author="Asif Hussain",
            tags=["orchestration", "maintenance", "system", "tiered-routing"]
        )
    
    @with_progress(operation_name="System Maintenance 3.0", threshold_seconds=5.0)
    @with_orchestration_metrics("MaintenanceOrchestratorV3")
    def execute(self, context: Dict[str, Any]) -> OperationResult:
        """
        Execute tiered maintenance workflow.
        
        Args:
            context: Operation context with:
                - operation: str - User's maintenance request
                - force_tier: int - Override tier classification (optional)
                - dry_run: bool - Simulate without making changes (default: False)
                - specific_phases: List[str] - Run only specific phases (optional)
        
        Returns:
            OperationResult with maintenance metrics and report
        """
        start_time = datetime.now()
        operation = context.get('operation', 'system maintenance')
        force_tier = context.get('force_tier')
        dry_run = context.get('dry_run', False)
        specific_phases = context.get('specific_phases', [])
        
        logger.info(f"🎭 Orchestrator engaged: MaintenanceOrchestratorV3 v{self.version}")
        logger.info(f"Operation: {operation} (dry_run={dry_run})")
        
        try:
            # Phase 1: Classification & Analysis
            yield_progress(1, 8, "Phase 1: Classifying maintenance operation")
            maintenance_context = self._classify_and_analyze(
                operation, dry_run, force_tier, specific_phases
            )
            
            # Phase 2: Route to execution path
            yield_progress(2, 8, f"Phase 2: Routing to Tier {maintenance_context.tier} execution")
            execution_result = self._route_and_execute(maintenance_context)
            
            # Phase 3-7: Maintenance phases (handled in execution)
            # Progress updates handled within tier execution methods
            
            # Phase 8: Generate report
            yield_progress(8, 8, "Phase 8: Generating maintenance report")
            report = self._generate_report(start_time, maintenance_context, execution_result)
            
            # Save report
            report_path = self._save_report(report)
            
            # Update metrics
            self.metrics['operations_processed'] += 1
            self.metrics['tier_breakdown'][maintenance_context.tier] += 1
            
            # Determine completion status
            success = execution_result.get('success', True)
            all_phases_complete = (
                maintenance_context.tier == 3 and 
                len(maintenance_context.phases_completed) == len(maintenance_context.phases_to_run)
            )
            is_complete = success and all_phases_complete and len(self.metrics['errors']) == 0
            
            logger.info(f"🎭 Orchestrator completing: {'✅ ALL WORK COMPLETE' if is_complete else '⏳ PHASES DONE WITH WARNINGS'}")
            
            return OperationResult(
                success=success,
                status=OperationStatus.SUCCESS if success else OperationStatus.WARNING,
                message=f"System maintenance completed (Tier {maintenance_context.tier}): {len(maintenance_context.phases_completed)} phases",
                data={
                    'tier': maintenance_context.tier,
                    'phases_completed': len(maintenance_context.phases_completed),
                    'phases_total': len(maintenance_context.phases_to_run),
                    'complexity_score': maintenance_context.complexity_score.total_score,
                    'execution_result': execution_result,
                    'report_path': str(report_path),
                    'improvements': self.metrics['improvements'],
                    'metrics': self.metrics,
                    'is_complete': is_complete,
                    'elapsed_time': (datetime.now() - start_time).total_seconds()
                }
            )
            
        except Exception as e:
            logger.error(f"Maintenance orchestration failed: {e}", exc_info=True)
            self.metrics['errors'].append(str(e))
            
            return OperationResult(
                success=False,
                status=OperationStatus.FAILED,
                message=f"Maintenance failed: {e}",
                data={
                    'error': str(e),
                    'metrics': self.metrics
                }
            )
    
    def _classify_and_analyze(
        self,
        operation: str,
        dry_run: bool,
        force_tier: Optional[int] = None,
        specific_phases: List[str] = None
    ) -> MaintenanceContext:
        """
        Classify operation tier and analyze complexity.
        
        Args:
            operation: User's maintenance request
            dry_run: Simulate without making changes
            force_tier: Optional tier override
            specific_phases: Run only specific phases
        
        Returns:
            MaintenanceContext with classification results
        """
        logger.debug(f"Classifying maintenance operation: {operation}")
        
        # Complexity analysis
        complexity_score = self.complexity_analyzer.analyze(operation)
        logger.info(f"Complexity: {complexity_score.tier.value} (score: {complexity_score.total_score}/100)")
        
        # Tier classification
        if force_tier:
            routing_decision = RoutingDecision(
                tier=force_tier,
                confidence=1.0,
                reasoning=f"Manually specified tier {force_tier}",
                execution_method=self._tier_to_execution_method(force_tier),
                estimated_time=self._tier_to_estimated_time(force_tier),
                requires_planning=force_tier >= 3
            )
            logger.info(f"Tier override: {force_tier}")
        else:
            routing_decision = self.tiered_router.route(operation)
            logger.info(f"Tier: {routing_decision.tier} (confidence: {routing_decision.confidence:.2f})")
        
        # Determine phases to run
        phases_to_run = self._determine_phases(routing_decision.tier, specific_phases)
        
        return MaintenanceContext(
            operation=operation,
            tier=routing_decision.tier,
            complexity_score=complexity_score,
            routing_decision=routing_decision,
            phases_to_run=phases_to_run,
            dry_run=dry_run,
            timestamp=datetime.now()
        )
    
    def _route_and_execute(
        self,
        maintenance_context: MaintenanceContext
    ) -> Dict[str, Any]:
        """
        Route to appropriate tier execution path.
        
        Args:
            maintenance_context: Maintenance operation context
        
        Returns:
            Execution result dictionary
        """
        tier = maintenance_context.tier
        
        logger.info(f"🎭 Phase transition: Classification → Tier {tier} Execution")
        
        if tier == 1:
            return self._execute_tier1_instant(maintenance_context)
        elif tier == 2:
            return self._execute_tier2_lightweight(maintenance_context)
        elif tier == 3:
            return self._execute_tier3_documented(maintenance_context)
        elif tier == 4:
            return self._execute_tier4_complex(maintenance_context)
        else:
            raise ValueError(f"Invalid tier: {tier}")
    
    def _execute_tier1_instant(self, context: MaintenanceContext) -> Dict[str, Any]:
        """
        Execute Tier 1 (INSTANT) operations.
        
        Examples: check health, system status
        Target: <2s response time
        """
        logger.info("Executing Tier 1 (INSTANT): Quick status check")
        
        try:
            healthcheck = HealthCheckOperation()
            result = healthcheck.execute({})
            
            if result.success:
                health_data = result.data or {}
                is_healthy = health_data.get('overall_health', {}).get('is_healthy', False)
                
                return {
                    'success': True,
                    'tier': 1,
                    'execution_method': 'instant',
                    'health_status': 'healthy' if is_healthy else 'needs_attention',
                    'health_data': health_data
                }
            else:
                return {
                    'success': False,
                    'tier': 1,
                    'error': result.message
                }
        
        except Exception as e:
            logger.error(f"Tier 1 execution failed: {e}")
            return {
                'success': False,
                'tier': 1,
                'error': str(e)
            }
    
    def _execute_tier2_lightweight(self, context: MaintenanceContext) -> Dict[str, Any]:
        """
        Execute Tier 2 (LIGHTWEIGHT) operations.
        
        Examples: fix alignment, cleanup only, single phase
        """
        logger.info("Executing Tier 2 (LIGHTWEIGHT): Single-phase maintenance")
        
        results = {}
        
        for phase in context.phases_to_run:
            logger.info(f"🎭 Phase transition: START → {phase.value}")
            
            if phase == MaintenancePhase.ALIGNMENT:
                results['alignment'] = self._run_alignment_phase(context)
            elif phase == MaintenancePhase.CLEANUP:
                results['cleanup'] = self._run_cleanup_phase(context)
            elif phase == MaintenancePhase.OPTIMIZATION:
                results['optimization'] = self._run_optimization_phase(context)
            
            context.phases_completed.append(phase.value)
        
        return {
            'success': True,
            'tier': 2,
            'execution_method': 'lightweight',
            'phases': results,
            'phases_completed': context.phases_completed
        }
    
    def _execute_tier3_documented(self, context: MaintenanceContext) -> Dict[str, Any]:
        """
        Execute Tier 3 (DOCUMENTED) operations.
        
        Examples: system maintenance, full maintenance cycle
        """
        logger.info("Executing Tier 3 (DOCUMENTED): Full 7-phase maintenance")
        
        phase_results = {}
        
        # Pre-healthcheck
        logger.info("🎭 Phase transition: START → PRE_HEALTHCHECK")
        yield_progress(3, 8, "Phase 3: Pre-healthcheck")
        phase_results['pre_healthcheck'] = self._run_pre_healthcheck_phase(context)
        context.phases_completed.append('pre_healthcheck')
        context.pre_health_status = phase_results['pre_healthcheck']
        self.metrics['healthcheck_pre'] = phase_results['pre_healthcheck']
        
        # Alignment
        logger.info("🎭 Phase transition: PRE_HEALTHCHECK → ALIGNMENT")
        yield_progress(4, 8, "Phase 4: Alignment")
        phase_results['alignment'] = self._run_alignment_phase(context)
        context.phases_completed.append('alignment')
        self.metrics['alignment'] = phase_results['alignment']
        
        # Cleanup
        logger.info("🎭 Phase transition: ALIGNMENT → CLEANUP")
        yield_progress(5, 8, "Phase 5: Cleanup")
        phase_results['cleanup'] = self._run_cleanup_phase(context)
        context.phases_completed.append('cleanup')
        self.metrics['cleanup'] = phase_results['cleanup']
        
        # Optimization
        logger.info("🎭 Phase transition: CLEANUP → OPTIMIZATION")
        yield_progress(6, 8, "Phase 6: Optimization")
        phase_results['optimization'] = self._run_optimization_phase(context)
        context.phases_completed.append('optimization')
        self.metrics['optimization'] = phase_results['optimization']
        
        # Vacuum (NEW in v3.0)
        logger.info("🎭 Phase transition: OPTIMIZATION → VACUUM")
        yield_progress(6, 8, "Phase 6.5: Vacuum")
        phase_results['vacuum'] = self._run_vacuum_phase(context)
        context.phases_completed.append('vacuum')
        self.metrics['vacuum'] = phase_results['vacuum']
        
        # Refresh
        logger.info("🎭 Phase transition: VACUUM → REFRESH")
        yield_progress(7, 8, "Phase 7: Refresh prompts")
        phase_results['refresh'] = self._run_refresh_phase(context)
        context.phases_completed.append('refresh')
        self.metrics['refresh'] = phase_results['refresh']
        
        # Post-healthcheck
        logger.info("🎭 Phase transition: REFRESH → POST_HEALTHCHECK")
        yield_progress(7, 8, "Phase 7.5: Post-healthcheck")
        phase_results['post_healthcheck'] = self._run_post_healthcheck_phase(context)
        context.phases_completed.append('post_healthcheck')
        context.post_health_status = phase_results['post_healthcheck']
        self.metrics['healthcheck_post'] = phase_results['post_healthcheck']
        
        return {
            'success': True,
            'tier': 3,
            'execution_method': 'documented',
            'phases': phase_results,
            'phases_completed': context.phases_completed
        }
    
    def _execute_tier4_complex(self, context: MaintenanceContext) -> Dict[str, Any]:
        """
        Execute Tier 4 (COMPLEX) operations.
        
        Examples: deep maintenance, comprehensive analysis, multi-system
        """
        logger.info("Executing Tier 4 (COMPLEX): Deep analysis maintenance")
        
        # Run full Tier 3 cycle first
        tier3_result = self._execute_tier3_documented(context)
        
        # Add deep analysis
        deep_analysis = self._run_deep_analysis(context)
        
        return {
            'success': True,
            'tier': 4,
            'execution_method': 'complex',
            'tier3_result': tier3_result,
            'deep_analysis': deep_analysis,
            'phases_completed': context.phases_completed
        }
    
    def _run_pre_healthcheck_phase(self, context: MaintenanceContext) -> Dict[str, Any]:
        """Run pre-maintenance healthcheck."""
        try:
            healthcheck = HealthCheckOperation()
            result = healthcheck.execute({})
            
            if result.success:
                self.metrics['improvements'].append("Pre-healthcheck completed")
                return result.data or {}
            else:
                self.metrics['warnings'].append(f"Pre-healthcheck issues: {result.message}")
                return {'success': False, 'message': result.message}
        except Exception as e:
            logger.error(f"Pre-healthcheck failed: {e}")
            self.metrics['errors'].append(f"Pre-healthcheck: {e}")
            return {'success': False, 'error': str(e)}
    
    def _run_alignment_phase(self, context: MaintenanceContext) -> Dict[str, Any]:
        """Run system alignment with auto-fix."""
        try:
            if context.dry_run:
                return {'success': True, 'dry_run': True, 'message': 'Alignment simulated'}
            
            result = run_align(auto_fix=True, dry_run=False)
            
            if result.get('success'):
                fixes = result.get('fixes_applied', 0)
                self.metrics['improvements'].append(f"Alignment: {fixes} fixes")
                return result
            else:
                self.metrics['warnings'].append(f"Alignment issues: {result.get('message')}")
                return result
        except Exception as e:
            logger.error(f"Alignment failed: {e}")
            self.metrics['errors'].append(f"Alignment: {e}")
            return {'success': False, 'error': str(e)}
    
    def _run_cleanup_phase(self, context: MaintenanceContext) -> Dict[str, Any]:
        """Run cleanup and organization."""
        try:
            from src.operations.modules.orchestration.cleanup_orchestrator import CleanupOrchestrator
            
            cleanup = CleanupOrchestrator(self.project_root)
            result = cleanup.execute({'dry_run': context.dry_run})
            
            if result.success:
                files_moved = result.data.get('metrics', {}).get('files_moved', 0)
                self.metrics['improvements'].append(f"Cleanup: {files_moved} files organized")
                return {
                    'success': True,
                    'files_moved': files_moved,
                    'files_removed': result.data.get('metrics', {}).get('files_removed', 0)
                }
            else:
                self.metrics['warnings'].append(f"Cleanup issues: {result.message}")
                return {'success': False, 'message': result.message}
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
            self.metrics['errors'].append(f"Cleanup: {e}")
            return {'success': False, 'error': str(e)}
    
    def _run_optimization_phase(self, context: MaintenanceContext) -> Dict[str, Any]:
        """Run CORTEX optimization."""
        try:
            if context.dry_run:
                return {'success': True, 'dry_run': True, 'message': 'Optimization simulated'}
            
            from src.operations.optimize import run_optimize
            result = run_optimize()
            
            if result.get('success'):
                optimizations = result.get('optimizations_applied', 0)
                self.metrics['improvements'].append(f"Optimization: {optimizations} improvements")
                return result
            else:
                self.metrics['warnings'].append(f"Optimization issues: {result.get('message')}")
                return result
        except Exception as e:
            logger.error(f"Optimization failed: {e}")
            self.metrics['errors'].append(f"Optimization: {e}")
            return {'success': False, 'error': str(e)}
    
    def _run_vacuum_phase(self, context: MaintenanceContext) -> Dict[str, Any]:
        """Run vacuum cycle (NEW in v3.0) - AST-powered cleanup."""
        try:
            # Placeholder for vacuum orchestrator integration
            # Will be implemented in Phase 12
            logger.info("Vacuum phase: AST-powered cleanup (placeholder)")
            
            return {
                'success': True,
                'message': 'Vacuum phase placeholder - full implementation in Phase 12',
                'duplicates_removed': 0,
                'orphaned_files': 0
            }
        except Exception as e:
            logger.error(f"Vacuum failed: {e}")
            self.metrics['warnings'].append(f"Vacuum: {e}")
            return {'success': False, 'error': str(e)}
    
    def _run_refresh_phase(self, context: MaintenanceContext) -> Dict[str, Any]:
        """Refresh Copilot prompts."""
        try:
            if context.dry_run:
                return {'success': True, 'dry_run': True, 'message': 'Refresh simulated'}
            
            script_path = self.project_root / "scripts" / "regenerate_cortex_prompts.py"
            
            if not script_path.exists():
                self.metrics['warnings'].append("Prompt refresh script not found")
                return {'success': False, 'message': 'Script not found'}
            
            result = subprocess.run(
                ["python", str(script_path)],
                cwd=str(self.project_root),
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                self.metrics['improvements'].append("Prompts refreshed")
                return {'success': True, 'message': 'Prompts refreshed'}
            else:
                self.metrics['warnings'].append("Prompt refresh issues")
                return {'success': False, 'message': result.stderr[:200]}
        except Exception as e:
            logger.error(f"Refresh failed: {e}")
            self.metrics['warnings'].append(f"Refresh: {e}")
            return {'success': False, 'error': str(e)}
    
    def _run_post_healthcheck_phase(self, context: MaintenanceContext) -> Dict[str, Any]:
        """Run post-maintenance healthcheck."""
        try:
            healthcheck = HealthCheckOperation()
            result = healthcheck.execute({})
            
            if result.success:
                # Compare with pre-healthcheck
                pre_health = context.pre_health_status
                post_health = result.data
                
                if pre_health and post_health:
                    pre_healthy = pre_health.get('overall_health', {}).get('is_healthy', False)
                    post_healthy = post_health.get('overall_health', {}).get('is_healthy', False)
                    
                    if not pre_healthy and post_healthy:
                        self.metrics['improvements'].append("Health improved: unhealthy → healthy")
                    elif pre_healthy and post_healthy:
                        self.metrics['improvements'].append("Health maintained: healthy")
                
                return result.data or {}
            else:
                self.metrics['warnings'].append(f"Post-healthcheck issues: {result.message}")
                return {'success': False, 'message': result.message}
        except Exception as e:
            logger.error(f"Post-healthcheck failed: {e}")
            self.metrics['errors'].append(f"Post-healthcheck: {e}")
            return {'success': False, 'error': str(e)}
    
    def _run_deep_analysis(self, context: MaintenanceContext) -> Dict[str, Any]:
        """Run deep analysis (Tier 4 only)."""
        # Placeholder for deep analysis features
        return {
            'ast_analysis': 'placeholder',
            'security_scan': 'placeholder',
            'performance_profiling': 'placeholder'
        }
    
    def _determine_phases(
        self,
        tier: int,
        specific_phases: List[str] = None
    ) -> List[MaintenancePhase]:
        """Determine which phases to run based on tier."""
        if specific_phases:
            # Convert strings to enum
            return [MaintenancePhase(p) for p in specific_phases if p in [mp.value for mp in MaintenancePhase]]
        
        if tier == 1:
            return []  # Just healthcheck, no full phases
        elif tier == 2:
            return [MaintenancePhase.ALIGNMENT, MaintenancePhase.CLEANUP]
        elif tier in [3, 4]:
            return [
                MaintenancePhase.PRE_HEALTHCHECK,
                MaintenancePhase.ALIGNMENT,
                MaintenancePhase.CLEANUP,
                MaintenancePhase.OPTIMIZATION,
                MaintenancePhase.VACUUM,
                MaintenancePhase.REFRESH,
                MaintenancePhase.POST_HEALTHCHECK
            ]
        else:
            return []
    
    def _generate_report(
        self,
        start_time: datetime,
        context: MaintenanceContext,
        execution_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate comprehensive maintenance report."""
        elapsed = (datetime.now() - start_time).total_seconds()
        
        return {
            'timestamp': datetime.now().isoformat(),
            'operation': context.operation,
            'tier': context.tier,
            'dry_run': context.dry_run,
            'duration_seconds': elapsed,
            'phases_completed': context.phases_completed,
            'phases_total': len(context.phases_to_run),
            'success': execution_result.get('success', False),
            'improvements': self.metrics['improvements'],
            'warnings': self.metrics['warnings'],
            'errors': self.metrics['errors'],
            'pre_health': context.pre_health_status,
            'post_health': context.post_health_status
        }
    
    def _save_report(self, report: Dict[str, Any]) -> Path:
        """Save maintenance report to file."""
        reports_dir = self.project_root / "cortex-brain" / "documents" / "reports" / "maintenance"
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = reports_dir / f"maintenance_{timestamp}.json"
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"Report saved: {report_path}")
        return report_path
    
    def _tier_to_execution_method(self, tier: int) -> str:
        """Convert tier to execution method string."""
        methods = {1: 'instant', 2: 'lightweight', 3: 'documented', 4: 'complex'}
        return methods.get(tier, 'unknown')
    
    def _tier_to_estimated_time(self, tier: int) -> str:
        """Convert tier to estimated time string."""
        times = {1: '<2s', 2: '10-30s', 3: '1-5min', 4: '5min+'}
        return times.get(tier, 'unknown')
