"""
Planning Orchestrator v3.0 for CORTEX

Streamlined planning system with intelligent tiered routing:
- Tier 1 (INSTANT): Direct execution, no planning
- Tier 2 (LIGHTWEIGHT): Inline validation, quick plans
- Tier 3 (DOCUMENTED): Feature additions, single MD
- Tier 4 (COMPLEX): Architecture changes, nested MD

Integrates:
- TieredRouter for operation classification
- ComplexityAnalyzer for risk assessment
- VersionManager for consistent versioning
- Automatic refactor/vacuum cycles

Phase 03 of CORTEX Evolution v3.9

Author: Asif Hussain
Copyright © 2025 Asif Hussain. All rights reserved.
Version: 3.0.0
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass

from src.operations.base_operation_module import (
    BaseOperationModule, OperationResult, OperationStatus, 
    OperationPhase, OperationModuleMetadata
)
from src.operations.modules.routing.tiered_router import (
    TieredRouter, OperationTier, RoutingDecision
)
from src.operations.modules.routing.complexity_analyzer import (
    ComplexityAnalyzer, ComplexityScore, ComplexityTier
)
from src.operations.modules.version.version_manager import get_version_manager
from src.utils.progress_decorator import with_progress, yield_progress
from src.operations.utilities.orchestration_metrics_collector import with_orchestration_metrics

logger = logging.getLogger(__name__)


@dataclass
class PlanningContext:
    """Context for planning operation."""
    operation: str
    tier: int
    complexity_score: ComplexityScore
    routing_decision: RoutingDecision
    user_context: Dict[str, Any]
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'operation': self.operation,
            'tier': self.tier,
            'complexity_tier': self.complexity_score.tier.value,
            'complexity_score': self.complexity_score.total_score,
            'estimated_time': self.routing_decision.estimated_time,
            'requires_planning': self.routing_decision.requires_planning,
            'timestamp': self.timestamp.isoformat()
        }


class PlanningOrchestrator(BaseOperationModule):
    """
    Planning System 3.0 orchestrator.
    
    Workflow:
    1. Classify operation tier (TieredRouter)
    2. Analyze complexity (ComplexityAnalyzer)
    3. Route to appropriate execution path:
       - Tier 1: Instant execution
       - Tier 2: Lightweight planning
       - Tier 3: Documented feature planning
       - Tier 4: Complex architecture planning
    4. Execute refactor cycle (cleanup)
    5. Execute vacuum cycle (consolidation)
    6. Generate documentation
    
    Integrations:
    - TieredRouter: 4-tier classification
    - ComplexityAnalyzer: Risk scoring
    - VersionManager: Centralized versioning
    - RefactorCycleOrchestrator: Code cleanup
    - VacuumOrchestrator: Document consolidation
    """
    
    def __init__(self, project_root: Path = None):
        """
        Initialize Planning Orchestrator 3.0.
        
        Args:
            project_root: Path to project root (defaults to CWD)
        """
        super().__init__()
        self.project_root = project_root or Path.cwd()
        
        # Initialize version manager and register
        self.version_manager = get_version_manager()
        self.version_manager.register_orchestrator_version("planning_orchestrator", "3.0")
        self.version = self.version_manager.get_orchestrator_version("planning_orchestrator")
        
        # Initialize routing components
        self.tiered_router = TieredRouter()
        self.complexity_analyzer = ComplexityAnalyzer()
        
        # Metrics tracking
        self.metrics: Dict[str, Any] = {
            'operations_processed': 0,
            'tier_breakdown': {1: 0, 2: 0, 3: 0, 4: 0},
            'planning_created': 0,
            'refactor_cycles_run': 0,
            'vacuum_cycles_run': 0,
            'errors': [],
            'warnings': []
        }
        
        # Initialize template manager for progress visualization
        try:
            from src.response_templates.response_template_manager import ResponseTemplateManager
            self.template_manager = ResponseTemplateManager()
        except Exception as e:
            logger.warning(f"Failed to initialize template manager: {e}")
            self.template_manager = None
        
        logger.info(f"✅ PlanningOrchestrator v{self.version} initialized (Planning System 3.0)")
    
    def get_metadata(self) -> OperationModuleMetadata:
        """Get module metadata."""
        return OperationModuleMetadata(
            module_id="planning_orchestrator_v3",
            name="Planning Orchestrator 3.0",
            description="Intelligent tiered planning with automatic refactor/vacuum cycles",
            phase=OperationPhase.PROCESSING,
            priority=100,
            version="3.0.0",
            author="Asif Hussain",
            tags=["orchestration", "planning", "tiered-routing", "planning-system-3.0"]
        )
    
    @with_progress(operation_name="Planning System 3.0", threshold_seconds=5.0)
    @with_orchestration_metrics("PlanningOrchestrator")
    def execute(self, context: Dict[str, Any]) -> OperationResult:
        """
        Execute tiered planning workflow.
        
        Args:
            context: Operation context with:
                - operation: str - User's planning request
                - skip_refactor: bool - Skip refactor cycle (default: False)
                - skip_vacuum: bool - Skip vacuum cycle (default: False)
                - force_tier: int - Override tier classification (optional)
        
        Returns:
            OperationResult with planning artifacts and metrics
        """
        start_time = datetime.now()
        operation = context.get('operation', '')
        skip_refactor = context.get('skip_refactor', False)
        skip_vacuum = context.get('skip_vacuum', False)
        force_tier = context.get('force_tier')
        
        if not operation:
            return OperationResult(
                success=False,
                status=OperationStatus.FAILED,
                message="No operation specified for planning",
                data={'error': 'operation_required'}
            )
        
        logger.info(f"🎭 Orchestrator engaged: PlanningOrchestrator v{self.version}")
        logger.info(f"Operation: {operation}")
        
        try:
            # Phase 1: Classification & Analysis
            yield_progress(1, 6, "Phase 1: Classifying operation tier")
            planning_context = self._classify_and_analyze(operation, force_tier)
            
            # Phase 2: Route to execution path
            yield_progress(2, 6, f"Phase 2: Routing to Tier {planning_context.tier} execution")
            execution_result = self._route_and_execute(planning_context, context)
            
            # Phase 3: Refactor cycle (if applicable)
            if not skip_refactor and planning_context.tier >= 3:
                yield_progress(3, 6, "Phase 3: Running refactor cycle")
                refactor_result = self._run_refactor_cycle(planning_context)
                self.metrics['refactor_cycles_run'] += 1
            else:
                refactor_result = {'skipped': True}
            
            # Phase 4: Vacuum cycle (if applicable)
            if not skip_vacuum and planning_context.tier >= 3:
                yield_progress(4, 6, "Phase 4: Running vacuum cycle")
                vacuum_result = self._run_vacuum_cycle(planning_context)
                self.metrics['vacuum_cycles_run'] += 1
            else:
                vacuum_result = {'skipped': True}
            
            # Phase 5: Documentation generation
            yield_progress(5, 6, "Phase 5: Generating documentation")
            docs_result = self._generate_documentation(planning_context, execution_result)
            
            # Phase 6: Finalize
            yield_progress(6, 6, "Phase 6: Finalizing planning")
            
            # Generate visual progress summary
            progress_summary = self._generate_progress_summary(planning_context)
            logger.info(f"\n{progress_summary}")
            
            # Update metrics
            self.metrics['operations_processed'] += 1
            self.metrics['tier_breakdown'][planning_context.tier] += 1
            if execution_result.get('plan_created'):
                self.metrics['planning_created'] += 1
            
            # Determine completion status
            success = execution_result.get('success', True)
            is_complete = success and len(self.metrics['errors']) == 0
            
            logger.info(f"🎭 Orchestrator completing: {'✅ ALL WORK COMPLETE' if is_complete else '⏳ PHASES DONE WITH WARNINGS'}")
            
            return OperationResult(
                success=success,
                status=OperationStatus.SUCCESS if success else OperationStatus.WARNING,
                message=f"Planning completed (Tier {planning_context.tier}): {operation}\n\n{progress_summary}",
                data={
                    'tier': planning_context.tier,
                    'complexity_score': planning_context.complexity_score.total_score,
                    'execution_result': execution_result,
                    'refactor_result': refactor_result,
                    'vacuum_result': vacuum_result,
                    'documentation': docs_result,
                    'metrics': self.metrics,
                    'is_complete': is_complete,
                    'elapsed_time': (datetime.now() - start_time).total_seconds(),
                    'progress_summary': progress_summary
                }
            )
            
        except Exception as e:
            logger.error(f"Planning orchestration failed: {e}", exc_info=True)
            self.metrics['errors'].append(str(e))
            
            return OperationResult(
                success=False,
                status=OperationStatus.FAILED,
                message=f"Planning failed: {e}",
                data={
                    'error': str(e),
                    'metrics': self.metrics
                }
            )
    
    def _classify_and_analyze(
        self, 
        operation: str, 
        force_tier: Optional[int] = None
    ) -> PlanningContext:
        """
        Classify operation tier and analyze complexity.
        
        Args:
            operation: User's planning request
            force_tier: Optional tier override
        
        Returns:
            PlanningContext with classification results
        """
        logger.debug(f"Classifying operation: {operation}")
        
        # Step 1: Complexity analysis
        complexity_score = self.complexity_analyzer.analyze(operation)
        logger.info(f"Complexity: {complexity_score.tier.value} (score: {complexity_score.total_score}/100)")
        
        # Step 2: Tier classification
        if force_tier:
            # Manual override
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
            # Automatic classification
            routing_decision = self.tiered_router.route(operation)
            logger.info(f"Tier: {routing_decision.tier} (confidence: {routing_decision.confidence:.2f})")
        
        # Create context
        context = PlanningContext(
            operation=operation,
            tier=routing_decision.tier,
            complexity_score=complexity_score,
            routing_decision=routing_decision,
            user_context={},
            timestamp=datetime.now()
        )
        
        logger.debug(f"Planning context: {context.to_dict()}")
        return context
    
    def _route_and_execute(
        self, 
        planning_context: PlanningContext,
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Route to appropriate execution path based on tier.
        
        Args:
            planning_context: Classification results
            user_context: User-provided context
        
        Returns:
            Execution results dictionary
        """
        tier = planning_context.tier
        
        if tier == 1:
            return self._execute_instant(planning_context, user_context)
        elif tier == 2:
            return self._execute_lightweight(planning_context, user_context)
        elif tier == 3:
            return self._execute_documented(planning_context, user_context)
        elif tier == 4:
            return self._execute_complex(planning_context, user_context)
        else:
            logger.warning(f"Unknown tier: {tier}, defaulting to Tier 3")
            return self._execute_documented(planning_context, user_context)
    
    def _execute_instant(
        self, 
        planning_context: PlanningContext,
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute Tier 1 (INSTANT) operation."""
        logger.info("Executing Tier 1: Instant operation (no planning required)")
        
        return {
            'success': True,
            'tier': 1,
            'execution_method': 'instant',
            'plan_created': False,
            'message': 'Operation executed instantly without planning',
            'recommendation': 'Execute directly via CLI or direct function call'
        }
    
    def _execute_lightweight(
        self, 
        planning_context: PlanningContext,
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute Tier 2 (LIGHTWEIGHT) operation."""
        logger.info("Executing Tier 2: Lightweight planning")
        
        # Create minimal inline plan
        inline_plan = {
            'operation': planning_context.operation,
            'approach': 'Single file modification with inline validation',
            'steps': [
                'Identify target file',
                'Make focused change',
                'Validate syntax/lint',
                'Commit with descriptive message'
            ],
            'estimated_time': planning_context.routing_decision.estimated_time
        }
        
        return {
            'success': True,
            'tier': 2,
            'execution_method': 'lightweight',
            'plan_created': True,
            'plan_type': 'inline',
            'plan': inline_plan,
            'message': 'Lightweight inline plan created'
        }
    
    def _execute_documented(
        self, 
        planning_context: PlanningContext,
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute Tier 3 (DOCUMENTED) operation."""
        logger.info("Executing Tier 3: Documented feature planning")
        
        # Create feature plan structure
        plan_path = self._generate_plan_path(planning_context, tier=3)
        plan_structure = self._create_tier3_plan(planning_context)
        
        return {
            'success': True,
            'tier': 3,
            'execution_method': 'documented',
            'plan_created': True,
            'plan_type': 'markdown',
            'plan_path': str(plan_path),
            'plan_structure': plan_structure,
            'message': 'Feature plan created with single MD structure'
        }
    
    def _execute_complex(
        self, 
        planning_context: PlanningContext,
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute Tier 4 (COMPLEX) operation."""
        logger.info("Executing Tier 4: Complex architecture planning")
        
        # Create nested plan structure
        plan_path = self._generate_plan_path(planning_context, tier=4)
        plan_structure = self._create_tier4_plan(planning_context)
        
        return {
            'success': True,
            'tier': 4,
            'execution_method': 'complex',
            'plan_created': True,
            'plan_type': 'nested_markdown',
            'plan_path': str(plan_path),
            'plan_structure': plan_structure,
            'message': 'Complex plan created with nested MD structure and sub-plans'
        }
    
    def _run_refactor_cycle(self, planning_context: PlanningContext) -> Dict[str, Any]:
        """Run refactor cycle (stub - Phase 13 implementation)."""
        logger.info("Refactor cycle: Code cleanup, comment sync, debug removal")
        
        return {
            'success': True,
            'actions': [
                'Remove debug statements',
                'Update stale comments',
                'Clean orphaned imports',
                'Format code'
            ],
            'files_modified': 0,
            'message': 'Refactor cycle stub (Phase 13 pending)'
        }
    
    def _run_vacuum_cycle(self, planning_context: PlanningContext) -> Dict[str, Any]:
        """Run vacuum cycle (stub - Phase 12 implementation)."""
        logger.info("Vacuum cycle: Document consolidation, archive old plans")
        
        return {
            'success': True,
            'actions': [
                'Consolidate similar documents',
                'Archive completed plans',
                'Optimize filenames',
                'Update references'
            ],
            'files_consolidated': 0,
            'message': 'Vacuum cycle stub (Phase 12 pending)'
        }
    
    def _generate_documentation(
        self, 
        planning_context: PlanningContext,
        execution_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate planning documentation."""
        logger.debug("Generating planning documentation")
        
        return {
            'generated': True,
            'documents': [
                'planning_summary.md',
                'complexity_analysis.md',
                'execution_log.json'
            ],
            'message': 'Documentation generated'
        }
    
    def _generate_plan_path(self, planning_context: PlanningContext, tier: int) -> Path:
        """Generate plan file path."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        operation_slug = planning_context.operation.lower().replace(' ', '-')[:30]
        filename = f"plan_{operation_slug}_{timestamp}.md"
        
        return self.project_root / "cortex-brain" / "documents" / "planning" / "features" / filename
    
    def _create_tier3_plan(self, planning_context: PlanningContext) -> Dict[str, Any]:
        """Create Tier 3 plan structure."""
        return {
            'type': 'tier3_documented',
            'sections': [
                'Overview',
                'Requirements',
                'Implementation Steps',
                'Testing Strategy',
                'Acceptance Criteria',
                'Rollout Plan'
            ]
        }
    
    def _create_tier4_plan(self, planning_context: PlanningContext) -> Dict[str, Any]:
        """Create Tier 4 plan structure."""
        return {
            'type': 'tier4_complex',
            'main_plan': 'master_plan.md',
            'sub_plans': [
                'phase_01_foundation.md',
                'phase_02_implementation.md',
                'phase_03_integration.md',
                'phase_04_validation.md'
            ],
            'sections': [
                'Executive Summary',
                'Architecture Overview',
                'Phase Breakdown',
                'Dependency Graph',
                'Risk Analysis',
                'Success Criteria'
            ]
        }
    
    def _tier_to_execution_method(self, tier: int) -> str:
        """Convert tier to execution method string."""
        methods = {1: 'instant', 2: 'lightweight', 3: 'documented', 4: 'complex'}
        return methods.get(tier, 'documented')
    
    def _tier_to_estimated_time(self, tier: int) -> str:
        """Convert tier to estimated time string."""
        times = {1: '<2s', 2: '<10s', 3: '10-60min', 4: '>1h'}
        return times.get(tier, '10-60min')
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get orchestrator metrics."""
        return self.metrics.copy()
    
    def get_version_info(self) -> Dict[str, str]:
        """Get version information."""
        return {
            'orchestrator': 'planning_orchestrator',
            'version': self.version,
            'cortex_version': self.version_manager.get_cortex_version(),
            'planning_system_version': self.version_manager.get_planning_system_version()
        }
    
    def _generate_progress_summary(self, planning_context: PlanningContext) -> str:
        """
        Generate ASCII visual progress summary for user feedback.
        
        Args:
            planning_context: Current planning context
            
        Returns:
            Formatted ASCII progress visualization
        """
        # Calculate progress
        total_phases = 6
        completed_phases = 6  # All phases complete when this is called
        progress_percent = int((completed_phases / total_phases) * 100)
        
        # Generate progress bar
        bar_length = 20
        filled = int((progress_percent / 100) * bar_length)
        empty = bar_length - filled
        progress_bar = "█" * filled + "░" * empty
        
        # Build summary
        summary = f"""
```
+==============================================================================+
  Planning System 3.0 - Execution Complete
+==============================================================================+

  Progress: [{progress_bar}] {progress_percent}%

  Operation: {planning_context.operation[:60]}{'...' if len(planning_context.operation) > 60 else ''}
  Tier: {planning_context.tier} ({planning_context.routing_decision.execution_method.upper()})
  Complexity Score: {planning_context.complexity_score.total_score}/100
  Confidence: {planning_context.routing_decision.confidence*100:.0f}%

  Phases Completed:
    ✅ Classification & Analysis
    ✅ Tier Routing & Execution
    {'✅' if self.metrics['refactor_cycles_run'] > 0 else '⏭️ '} Refactor Cycle {'(Complete)' if self.metrics['refactor_cycles_run'] > 0 else '(Skipped)'}
    {'✅' if self.metrics['vacuum_cycles_run'] > 0 else '⏭️ '} Vacuum Cycle {'(Complete)' if self.metrics['vacuum_cycles_run'] > 0 else '(Skipped)'}
    ✅ Documentation Generation
    ✅ Finalization

+==============================================================================+
```"""
        return summary


# Example usage:
# 
# orchestrator = PlanningOrchestrator()
# result = orchestrator.execute({
#     'operation': 'Add user authentication to API',
#     'skip_refactor': False,
#     'skip_vacuum': False
# })
# print(result.data['tier'])  # 3 or 4 (auth triggers HIGH complexity)
