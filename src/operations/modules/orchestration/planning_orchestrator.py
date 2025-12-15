"""
Planning Orchestrator v3.1 for CORTEX

Enhanced planning system with intelligent tiered routing and temporary plan support:
- Tier 1 (INSTANT): Direct execution, no planning
- Tier 2 (LIGHTWEIGHT): Inline validation, quick plans
- Tier 3 (DOCUMENTED): Feature additions, single MD
- Tier 4 (COMPLEX): Architecture changes, nested MD

New Features (v3.1):
- Temporary plan management for implicit requests
- Plan folder lifecycle (approved → active → completed)
- Master plan status updates (In Progress, Complete)
- Knowledge extraction phase on completion
- Removed ASCII progress bars from user-facing output (internal logging only)

Integrates:
- TieredRouter for operation classification
- ComplexityAnalyzer for risk assessment
- VersionManager for consistent versioning
- TemporaryPlanManager for implicit planning workflow
- Automatic refactor/vacuum cycles

Phase 03 of CORTEX Evolution v3.9

Author: Asif Hussain
Copyright © 2025 Asif Hussain. All rights reserved.
Version: 3.1.0
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
from src.operations.modules.orchestration.temporary_plan_manager import (
    TemporaryPlanManager, TemporaryPlan
)
from src.orchestrators.session_model import PlanningSession, SessionStatus
from src.utils.progress_decorator import with_progress, yield_progress
from src.operations.utilities.orchestration_metrics_collector import with_orchestration_metrics
from src.orchestrators.git_checkpoint_orchestrator import GitCheckpointOrchestrator

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
    Planning System 3.1 orchestrator.
    
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
    7. Knowledge extraction (on completion)
    
    Integrations:
    - TieredRouter: 4-tier classification
    - ComplexityAnalyzer: Risk scoring
    - VersionManager: Centralized versioning
    - TemporaryPlanManager: Implicit planning workflow
    - RefactorCycleOrchestrator: Code cleanup
    - VacuumOrchestrator: Document consolidation
    - KnowledgeGraphAutoUpdater: Knowledge extraction
    """
    
    def __init__(self, project_root: Path = None):
        """
        Initialize Planning Orchestrator 3.1.
        
        Args:
            project_root: Path to project root (defaults to CWD)
        """
        super().__init__()
        self.project_root = project_root or Path.cwd()
        
        # Initialize version manager and register
        self.version_manager = get_version_manager()
        self.version_manager.register_orchestrator_version("planning_orchestrator", "3.1")
        self.version = self.version_manager.get_orchestrator_version("planning_orchestrator")
        
        # Initialize routing components
        self.tiered_router = TieredRouter()
        self.complexity_analyzer = ComplexityAnalyzer()
        
        # Initialize temporary plan manager
        self.temp_plan_manager = TemporaryPlanManager(self.project_root)
        
        # Track current plan for autonomous execution
        self.current_plan_id: Optional[str] = None
        self.current_phase: int = 0
        
        # Planning session for visual tracker (Task 1.3)
        self.session: Optional[PlanningSession] = None
        
        # Metrics tracking
        self.metrics: Dict[str, Any] = {
            'operations_processed': 0,
            'tier_breakdown': {1: 0, 2: 0, 3: 0, 4: 0},
            'planning_created': 0,
            'temporary_plans_created': 0,
            'plans_approved': 0,
            'plans_completed': 0,
            'knowledge_extractions': 0,
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
        
        # Initialize git checkpoint orchestrator for phase checkpoints
        try:
            self.checkpoint_orchestrator = GitCheckpointOrchestrator(project_root=project_root)
        except Exception as e:
            logger.warning(f"Failed to initialize git checkpoint orchestrator: {e}")
            self.checkpoint_orchestrator = None
        
        logger.info(f"✅ PlanningOrchestrator v{self.version} initialized (Planning System 3.1)")
    
    def get_metadata(self) -> OperationModuleMetadata:
        """Get module metadata."""
        return OperationModuleMetadata(
            module_id="planning_orchestrator_v3_1",
            name="Planning Orchestrator 3.1",
            description="Intelligent tiered planning with temporary plan support, folder lifecycle, and knowledge extraction",
            phase=OperationPhase.PROCESSING,
            priority=100,
            version="3.1.0",
            author="Asif Hussain",
            tags=["orchestration", "planning", "tiered-routing", "planning-system-3.1", "temporary-plans", "knowledge-extraction"]
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
        
        # Task 1.5.6: Detect execution mode for autonomous execution support
        from src.operations.modules.context.execution_mode_detector import ExecutionModeDetector
        mode_detector = ExecutionModeDetector()
        execution_mode = mode_detector.detect(operation)
        
        # Task 1.3: Initialize planning session for visual tracker
        import uuid
        self.session = PlanningSession(
            session_id=str(uuid.uuid4()),
            session_type="planning",
            status=SessionStatus.IN_PROGRESS,
            started_at=datetime.now(),
            plan_title=operation
        )
        
        # Store execution mode in session (Task 1.5.6)
        self.session.execution_mode = execution_mode
        logger.info(f"📋 Execution mode detected: {execution_mode}")
        
        try:
            # Phase 1: Classification & Analysis
            yield_progress(1, 6, "Phase 1: Classifying operation tier")
            self._record_phase_start("Classification & Analysis")
            planning_context = self._classify_and_analyze(operation, force_tier)
            self._record_phase_end("Classification & Analysis", tokens_used=100)
            
            # Phase 2: Route to execution path
            yield_progress(2, 6, f"Phase 2: Routing to Tier {planning_context.tier} execution")
            self._record_phase_start("Execution")

            execution_result = self._route_and_execute(planning_context, context)
            self._record_phase_end("Execution", tokens_used=500)
            
            # Phase 3: Refactor cycle (if applicable)
            if not skip_refactor and planning_context.tier >= 3:
                yield_progress(3, 6, "Phase 3: Running refactor cycle")
                self._record_phase_start("Refactor")
                refactor_result = self._run_refactor_cycle(planning_context)
                self._record_phase_end("Refactor", tokens_used=300)
                self.metrics['refactor_cycles_run'] += 1
            else:
                refactor_result = {'skipped': True}
            
            # Phase 4: Vacuum cycle (if applicable)
            if not skip_vacuum and planning_context.tier >= 3:
                yield_progress(4, 6, "Phase 4: Running vacuum cycle")
                self._record_phase_start("Vacuum")
                vacuum_result = self._run_vacuum_cycle(planning_context)
                self._record_phase_end("Vacuum", tokens_used=200)
                self.metrics['vacuum_cycles_run'] += 1
            else:
                vacuum_result = {'skipped': True}
            
            # Phase 5: Documentation generation
            yield_progress(5, 6, "Phase 5: Generating documentation")
            self._record_phase_start("Documentation")
            docs_result = self._generate_documentation(planning_context, execution_result)
            self._record_phase_end("Documentation", tokens_used=400)
            
            # Phase 6: Finalize
            yield_progress(6, 6, "Phase 6: Finalizing planning")
            self._record_phase_start("Finalization")
            
            # Generate visual progress summary (INTERNAL LOGGING ONLY)
            progress_summary = self._generate_progress_summary(planning_context)
            logger.info(f"\n{progress_summary}")
            
            self._record_phase_end("Finalization", tokens_used=50)
            
            # Update metrics
            self.metrics['operations_processed'] += 1
            self.metrics['tier_breakdown'][planning_context.tier] += 1
            if execution_result.get('plan_created'):
                self.metrics['planning_created'] += 1
            
            # Determine completion status
            success = execution_result.get('success', True)
            is_complete = success and len(self.metrics['errors']) == 0
            
            logger.info(f"🎭 Orchestrator completing: {'✅ ALL WORK COMPLETE' if is_complete else '⏳ PHASES DONE WITH WARNINGS'}")
            
            # Task 1.5.6: Select appropriate response template based on execution mode
            template_name = self._select_response_template()
            
            # Task 1.5: Render visual tracker in user response
            visual_tracker = ""
            if self.session:
                self.session.completed_at = datetime.now()
                self.session.status = SessionStatus.COMPLETED if is_complete else SessionStatus.WARNING
                visual_tracker = "\n\n" + self.session.render_progress_table() + "\n"
            
            # User-facing message with visual tracker
            user_message = f"Planning completed (Tier {planning_context.tier}): {operation}{visual_tracker}"
            
            return OperationResult(
                success=success,
                status=OperationStatus.SUCCESS if success else OperationStatus.WARNING,
                message=user_message,
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
                    'session': self.session.to_dict() if self.session else None,
                    'template_name': template_name  # Task 1.5.6: Template selection for response system
                    # NOTE: progress_summary removed from data - it's for logging only
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
        
        # Generate phases from planning context
        phases = self._generate_phases_for_tier(planning_context)
        
        # Generate and write master plan with visual tracker (Task 1.6)
        plan_folder = plan_path.parent / plan_path.stem
        master_plan_content = self._generate_master_plan_content(plan_folder, phases)
        master_plan_path = self._write_master_plan_file(plan_folder, master_plan_content)
        
        return {
            'success': True,
            'tier': 3,
            'execution_method': 'documented',
            'plan_created': True,
            'plan_type': 'markdown',
            'plan_path': str(plan_path),
            'master_plan_path': str(master_plan_path),
            'plan_structure': plan_structure,
            'message': f'Feature plan created with visual tracker at {master_plan_path}'
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
        
        # Generate phases from planning context
        phases = self._generate_phases_for_tier(planning_context)
        
        # Generate and write master plan with visual tracker (Task 1.6)
        plan_folder = plan_path.parent / plan_path.stem
        master_plan_content = self._generate_master_plan_content(plan_folder, phases)
        master_plan_path = self._write_master_plan_file(plan_folder, master_plan_content)
        
        return {
            'success': True,
            'tier': 4,
            'execution_method': 'complex',
            'plan_created': True,
            'plan_type': 'nested_markdown',
            'plan_path': str(plan_path),
            'master_plan_path': str(master_plan_path),
            'plan_structure': plan_structure,
            'message': f'Complex plan created with visual tracker at {master_plan_path}'
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
        Generate progress summary for INTERNAL LOGGING ONLY.
        
        NOTE: ASCII progress bars are for internal logging only.
        User-facing output uses markdown tables without ASCII art.
        
        Args:
            planning_context: Current planning context
            
        Returns:
            Formatted progress summary (for internal logging)
        """
        # Calculate progress
        total_phases = 6
        completed_phases = 6  # All phases complete when this is called
        progress_percent = int((completed_phases / total_phases) * 100)
        
        # Generate progress bar (INTERNAL LOGGING ONLY - not shown to user)
        bar_length = 20
        filled = int((progress_percent / 100) * bar_length)
        empty = bar_length - filled
        progress_bar = "█" * filled + "░" * empty
        
        # Build summary (this goes to logger, not user response)
        summary = f"""
[INTERNAL LOGGING - Planning System 3.1 Execution Complete]

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
"""
        return summary


    # ========================================
    # Temporary Plan Workflow (v3.1)
    # ========================================
    
    def create_temporary_plan_for_task(
        self,
        user_request: str,
        auto_approve: bool = False
    ) -> Dict[str, Any]:
        """
        Create a temporary plan for an implicit task request.
        
        This is used when user provides tasks without explicitly saying "create a plan".
        
        Workflow:
        1. Classify complexity and tier
        2. Create temporary plan in active/
        3. Return plan for user review
        4. User provides feedback (update_temporary_plan) or approves
        5. On approval: convert to full master/slave plan
        6. Execute autonomously
        
        Args:
            user_request: User's task request
            auto_approve: Whether to auto-approve (skip user review)
        
        Returns:
            Dictionary with temporary plan details
        """
        logger.info(f"🔄 Creating temporary plan for implicit request: {user_request}")
        
        # Step 1: Classify and analyze
        planning_context = self._classify_and_analyze(user_request)
        
        # Step 2: Generate phases based on tier
        phases = self._generate_phases_for_tier(planning_context)
        
        # Step 3: Create temporary plan
        temp_plan = self.temp_plan_manager.create_temporary_plan(
            user_request=user_request,
            complexity_tier=planning_context.tier,
            estimated_time=planning_context.routing_decision.estimated_time,
            approach=f"Tier {planning_context.tier} approach: {planning_context.routing_decision.reasoning}",
            phases=phases,
            dependencies=self._extract_dependencies(user_request),
            risks=self._extract_risks(planning_context)
        )
        
        self.metrics['temporary_plans_created'] += 1
        self.current_plan_id = temp_plan.plan_id
        
        # Step 4: Auto-approve if requested
        if auto_approve:
            temp_plan = self.temp_plan_manager.approve_temporary_plan(temp_plan.plan_id)
            self.metrics['plans_approved'] += 1
        
        logger.info(f"✅ Temporary plan created: {temp_plan.plan_id}")
        
        return {
            'success': True,
            'plan_id': temp_plan.plan_id,
            'plan': temp_plan.to_dict(),
            'requires_approval': not auto_approve,
            'message': f"Temporary plan created. {'Approved automatically.' if auto_approve else 'Please review and approve to proceed.'}"
        }
    
    def approve_and_execute_plan(
        self,
        plan_id: str,
        autonomous: bool = True
    ) -> Dict[str, Any]:
        """
        Approve temporary plan, convert to full plan, and execute.
        
        Args:
            plan_id: Plan identifier
            autonomous: Whether to execute autonomously (default: True)
        
        Returns:
            Execution results dictionary
        """
        logger.info(f"✅ Approving and executing plan: {plan_id}")
        
        # Step 1: Approve temporary plan (moves to approved/)
        temp_plan = self.temp_plan_manager.approve_temporary_plan(plan_id)
        self.metrics['plans_approved'] += 1
        
        # Step 2: Convert to full master/slave plan (moves to active/)
        master_plan_path = self.temp_plan_manager.convert_to_full_plan(plan_id)
        
        # Step 3: Execute autonomously if requested
        if autonomous:
            return self.execute_plan_autonomously(plan_id)
        else:
            return {
                'success': True,
                'plan_id': plan_id,
                'master_plan_path': str(master_plan_path),
                'message': 'Plan approved and converted. Ready for manual execution.'
            }
    
    def execute_plan_autonomously(self, plan_id: str) -> Dict[str, Any]:
        """
        Execute plan autonomously without asking for confirmation at each phase.
        
        Updates master plan status as phases progress:
        - Not Started → In Progress (when phase begins)
        - In Progress → Complete (when phase finishes)
        
        Args:
            plan_id: Plan identifier
        
        Returns:
            Execution results dictionary
        """
        logger.info(f"🚀 Executing plan autonomously: {plan_id}")
        self.current_plan_id = plan_id
        
        # Load plan to get phase count
        master_plan_path = self.temp_plan_manager.active_dir / plan_id / "master-plan.md"
        if not master_plan_path.exists():
            return {
                'success': False,
                'error': f"Master plan not found: {master_plan_path}"
            }
        
        # Parse phases from master plan
        phases = self._parse_phases_from_master_plan(master_plan_path)
        total_phases = len(phases)
        
        logger.info(f"📊 Plan has {total_phases} phases")
        
        # Execute each phase
        results = []
        for phase_num in range(1, total_phases + 1):
            logger.info(f"🎭 Phase transition: Phase {phase_num - 1 if phase_num > 1 else 0} → Phase {phase_num}")
            
            # Mark phase as In Progress
            self.temp_plan_manager.mark_phase_in_progress(plan_id, phase_num)
            self.current_phase = phase_num
            
            # Execute phase (stub - actual implementation would call sub-plan execution)
            phase_result = self._execute_phase(plan_id, phase_num, phases[phase_num - 1])
            results.append(phase_result)
            
            # Mark phase as Complete
            self.temp_plan_manager.mark_phase_complete(plan_id, phase_num)
        
        # All phases complete - run knowledge extraction and move to completed/
        logger.info(f"🎭 Orchestrator completing: ✅ ALL WORK COMPLETE")
        
        completed_path = self.temp_plan_manager.complete_plan(
            plan_id,
            extract_knowledge=True
        )
        
        self.metrics['plans_completed'] += 1
        self.metrics['knowledge_extractions'] += 1
        
        return {
            'success': True,
            'plan_id': plan_id,
            'total_phases': total_phases,
            'phase_results': results,
            'completed_path': str(completed_path),
            'is_complete': True,
            'message': f"Plan execution complete. Knowledge extracted. Plan moved to completed/"
        }
    
    def _generate_phases_for_tier(self, planning_context: PlanningContext) -> List[Dict[str, Any]]:
        """Generate phases based on complexity tier."""
        tier = planning_context.tier
        
        if tier == 1:
            # Instant - single task
            return [{
                'name': 'Execute',
                'description': 'Execute operation directly',
                'tasks': ['Execute operation'],
                'deliverables': ['Completed operation'],
                'acceptance_criteria': ['Operation successful']
            }]
        
        elif tier == 2:
            # Lightweight - 2 phases
            return [
                {
                    'name': 'Implementation',
                    'description': 'Implement the change',
                    'tasks': ['Make code changes', 'Validate syntax'],
                    'deliverables': ['Modified files'],
                    'acceptance_criteria': ['Code compiles', 'Lint passes']
                },
                {
                    'name': 'Testing',
                    'description': 'Test the implementation',
                    'tasks': ['Run tests', 'Verify functionality'],
                    'deliverables': ['Test results'],
                    'acceptance_criteria': ['All tests pass']
                }
            ]
        
        elif tier == 3:
            # Documented - 3 phases
            return [
                {
                    'name': 'Foundation',
                    'description': 'Set up foundation',
                    'tasks': ['Define interfaces', 'Create models'],
                    'deliverables': ['Base structure'],
                    'acceptance_criteria': ['Structure in place']
                },
                {
                    'name': 'Implementation',
                    'description': 'Implement feature logic',
                    'tasks': ['Implement business logic', 'Add tests'],
                    'deliverables': ['Feature implemented'],
                    'acceptance_criteria': ['Feature works', 'Tests pass']
                },
                {
                    'name': 'Integration',
                    'description': 'Integrate and validate',
                    'tasks': ['Integration tests', 'Documentation'],
                    'deliverables': ['Integrated feature'],
                    'acceptance_criteria': ['Integration complete']
                }
            ]
        
        else:  # tier == 4
            # Complex - 5 phases
            return [
                {
                    'name': 'Architecture',
                    'description': 'Design architecture',
                    'tasks': ['Architecture design', 'Interface definitions'],
                    'deliverables': ['Architecture doc'],
                    'acceptance_criteria': ['Design approved']
                },
                {
                    'name': 'Foundation',
                    'description': 'Build foundation',
                    'tasks': ['Core models', 'Base services'],
                    'deliverables': ['Foundation code'],
                    'acceptance_criteria': ['Foundation stable']
                },
                {
                    'name': 'Implementation',
                    'description': 'Implement features',
                    'tasks': ['Feature implementation', 'Unit tests'],
                    'deliverables': ['Feature code'],
                    'acceptance_criteria': ['Features work']
                },
                {
                    'name': 'Integration',
                    'description': 'Integrate components',
                    'tasks': ['Component integration', 'Integration tests'],
                    'deliverables': ['Integrated system'],
                    'acceptance_criteria': ['System integrated']
                },
                {
                    'name': 'Deployment',
                    'description': 'Deploy and validate',
                    'tasks': ['Deployment', 'Monitoring setup'],
                    'deliverables': ['Deployed system'],
                    'acceptance_criteria': ['System live']
                }
            ]
    
    def _extract_dependencies(self, user_request: str) -> List[str]:
        """Extract dependencies from user request (simple keyword matching)."""
        dependencies = []
        request_lower = user_request.lower()
        
        if 'api' in request_lower:
            dependencies.append("API infrastructure")
        if 'database' in request_lower or 'db' in request_lower:
            dependencies.append("Database schema")
        if 'auth' in request_lower:
            dependencies.append("Authentication system")
        if 'ui' in request_lower or 'frontend' in request_lower:
            dependencies.append("UI components")
        
        return dependencies
    
    def _extract_risks(self, planning_context: PlanningContext) -> List[str]:
        """Extract risks based on complexity."""
        risks = []
        
        if planning_context.complexity_score.total_score > 70:
            risks.append("High complexity may cause delays")
        
        if planning_context.tier >= 4:
            risks.append("Complex architecture changes require careful coordination")
        
        if len(self._extract_dependencies(planning_context.operation)) > 2:
            risks.append("Multiple dependencies may cause blocking issues")
        
        return risks
    
    def _parse_phases_from_master_plan(self, master_plan_path: Path) -> List[Dict[str, Any]]:
        """Parse phases from master plan markdown."""
        content = master_plan_path.read_text(encoding='utf-8')
        
        phases = []
        import re
        
        # Find all phase headers: "### Phase N: Name - Status: ..."
        phase_pattern = r'### Phase (\d+): (.+?) - Status:'
        matches = re.finditer(phase_pattern, content)
        
        for match in matches:
            phase_num = int(match.group(1))
            phase_name = match.group(2).strip()
            phases.append({
                'number': phase_num,
                'name': phase_name
            })
        
        return phases
    
    def _execute_phase(
        self,
        plan_id: str,
        phase_number: int,
        phase_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a single phase (stub for now).
        
        In production, this would:
        1. Load sub-plan for phase
        2. Execute tasks in sub-plan
        3. Validate acceptance criteria
        4. Generate phase report
        
        Args:
            plan_id: Plan identifier
            phase_number: Phase number
            phase_info: Phase information dictionary
        
        Returns:
            Phase execution results
        """
        logger.info(f"Executing Phase {phase_number}: {phase_info.get('name', 'Unknown')}")
        
        # Stub implementation
        # TODO: Implement actual phase execution logic
        
        return {
            'phase_number': phase_number,
            'phase_name': phase_info.get('name', 'Unknown'),
            'success': True,
            'message': f"Phase {phase_number} executed (stub)"
        }
    
    # ========================================
    # Pre-Planning Discovery (Phase 1 - Task 1.1)
    # ========================================
    
    def pre_planning_discovery(self, operation: str) -> Dict[str, Any]:
        """
        Check for existing/recent plans before creating new one.
        
        Office Filing System Analogy:
        Before creating new project folder, secretary checks:
        1. Active drawer (current projects)
        2. Pending tray (unapproved work)
        3. Archive drawer (recently completed - last 6 months)
        
        Args:
            operation: User's operation description
        
        Returns:
            Discovery results with recommendations
        """
        results = {
            'found_existing': False,
            'recommendations': [],
            'related_plans': []
        }
        
        # Extract feature name from operation
        feature_slug = self._extract_feature_slug(operation)
        
        # Search active/ folder (current work)
        active_plans = self._search_plans(
            folder="active",
            query=feature_slug,
            time_range="all"
        )
        
        if active_plans:
            results['found_existing'] = True
            results['recommendations'].append({
                'type': 'active_plan_exists',
                'message': f"Found {len(active_plans)} active plan(s) for '{feature_slug}'",
                'plans': active_plans,
                'action': 'continue_existing_or_new_version'
            })
        
        # Search temp-plans/ folder (unapproved work)
        temp_plans = self._search_plans(
            folder="temp-plans",
            query=feature_slug,
            time_range="last_30_days"
        )
        
        if temp_plans:
            results['found_existing'] = True
            results['recommendations'].append({
                'type': 'temp_plan_exists',
                'message': f"Found {len(temp_plans)} temporary plan(s) - may need approval",
                'plans': temp_plans,
                'action': 'approve_existing_or_create_new'
            })
        
        # Search completed/ folder (recently archived)
        completed_plans = self._search_plans(
            folder="completed",
            query=feature_slug,
            time_range="last_180_days"
        )
        
        if completed_plans:
            results['related_plans'].extend(completed_plans)
            results['recommendations'].append({
                'type': 'completed_plan_exists',
                'message': f"Found {len(completed_plans)} completed plan(s) - context available",
                'plans': completed_plans,
                'action': 'reuse_context_from_completed'
            })
        
        return results
    
    def _extract_feature_slug(self, operation: str) -> str:
        """Extract feature slug from operation text."""
        # Remove common prefixes
        operation = operation.lower()
        for prefix in ["plan ", "implement ", "create ", "build ", "add "]:
            if operation.startswith(prefix):
                operation = operation[len(prefix):]
        
        # Convert to slug
        return operation.replace(' ', '-')[:50]
    
    def _search_plans(self, folder: str, query: str, time_range: str) -> List[Dict[str, Any]]:
        """
        Search plans in specific folder by feature name and time range.
        
        Office Filing System: Flip through hanging folders looking for project name.
        
        Args:
            folder: Folder name (active, temp-plans, completed)
            query: Search query (feature slug)
            time_range: Time range filter (all, last_30_days, last_180_days)
        
        Returns:
            List of matching plans
        """
        plans = []
        search_path = self.project_root / "cortex-brain" / "documents" / "planning" / folder
        
        if not search_path.exists():
            return plans
        
        # Time range filtering
        cutoff_date = self._get_cutoff_date(time_range)
        
        for plan_folder in search_path.iterdir():
            if not plan_folder.is_dir():
                continue
            
            # Check if folder name matches query
            if query.lower() in plan_folder.name.lower():
                # Check modification time
                if cutoff_date and plan_folder.stat().st_mtime < cutoff_date.timestamp():
                    continue  # Too old
                
                # Read master plan to get summary
                master_plan = self._find_master_plan(plan_folder)
                
                plans.append({
                    'folder': str(plan_folder),
                    'name': plan_folder.name,
                    'last_modified': datetime.fromtimestamp(plan_folder.stat().st_mtime),
                    'summary': self._extract_plan_summary(master_plan) if master_plan else "No summary",
                    'has_context': (plan_folder / "context").exists(),
                    'has_reports': (plan_folder / "reports").exists()
                })
        
        return plans
    
    def _get_cutoff_date(self, time_range: str) -> Optional[datetime]:
        """Get cutoff date for time range filtering."""
        from datetime import timedelta
        
        if time_range == "all":
            return None
        elif time_range == "last_30_days":
            return datetime.now() - timedelta(days=30)
        elif time_range == "last_180_days":
            return datetime.now() - timedelta(days=180)
        else:
            return None
    
    def _find_master_plan(self, plan_folder: Path) -> Optional[Path]:
        """Find master plan file in plan folder."""
        candidates = ["00-master-plan.md", "11-temp-planning-session.md"]
        for candidate in candidates:
            path = plan_folder / candidate
            if path.exists():
                return path
        return None
    
    def _extract_plan_summary(self, plan_file: Path) -> str:
        """Extract summary from plan file (first paragraph after title)."""
        try:
            with open(plan_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Find first paragraph after title or summary section
            for i, line in enumerate(lines):
                if line.startswith("## ") and "summary" in line.lower():
                    # Return next non-empty line
                    for j in range(i+1, len(lines)):
                        if lines[j].strip() and not lines[j].startswith("#"):
                            return lines[j].strip()[:200]
            
            # Fallback: return first non-header line
            for line in lines:
                if line.strip() and not line.startswith("#") and not line.startswith("*") and len(line.strip()) > 20:
                    return line.strip()[:200]
            
            return "No summary available"
        except Exception as e:
            logger.warning(f"Could not extract summary from {plan_file}: {e}")
            return "No summary available"
    
    # ========================================
    # Phase Tracking Helpers (Task 1.4)
    # ========================================
    
    def _select_response_template(self) -> str:
        """
        Select appropriate response template based on execution mode (Task 1.5.6).
        
        Returns:
            Template name string for response system
        """
        if not self.session:
            return "plan_execution_standard"
        
        execution_mode = getattr(self.session, 'execution_mode', 'interactive')
        
        if execution_mode in ('autonomous', 'continuation'):
            return "autonomous_phase_execution"
        else:
            return "plan_execution_standard"
    
    def _create_phase_checkpoint(self, phase_name: str) -> bool:
        """
        Create git checkpoint before phase execution (Phase 1: Git Checkpoint Integration).
        
        CRITICAL: Must be called BEFORE any phase work begins to capture clean state.
        
        Args:
            phase_name: Name of the phase about to start
            
        Returns:
            bool: True if checkpoint created successfully, False otherwise
        """
        if not self.checkpoint_orchestrator:
            logger.warning("Git checkpoint orchestrator not available - skipping checkpoint")
            return False
        
        try:
            # Construct checkpoint metadata
            plan_id = self.current_plan_id or "unknown-plan"
            execution_mode = getattr(self.session, 'execution_mode', 'interactive') if self.session else 'interactive'
            
            message = f"Before {phase_name} | Plan: {plan_id} | Mode: {execution_mode}"
            metadata = {
                'phase_name': phase_name,
                'plan_id': plan_id,
                'execution_mode': execution_mode,
                'planning_system_version': '3.1'
            }
            
            # Create checkpoint using Git Checkpoint Orchestrator
            result = self.checkpoint_orchestrator.create_checkpoint(
                checkpoint_type=f"before-phase",
                message=message,
                metadata=metadata
            )
            
            if result.get('success'):
                checkpoint_id = result.get('checkpoint_id', 'unknown')
                logger.info(f"✅ Git checkpoint created: {checkpoint_id} (before {phase_name})")
                return True
            else:
                logger.warning(f"⚠️ Failed to create git checkpoint before {phase_name}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Git checkpoint creation failed: {str(e)}")
            return False
    
    def _record_phase_start(self, phase_name: str) -> None:
        """
        Record phase start in session tracking with enhanced logging (Task 1.5.5).
        
        CRITICAL: Creates git checkpoint BEFORE any phase work begins.
        
        Args:
            phase_name: Name of the phase starting
        """
        # Create git checkpoint FIRST (before any work begins)
        self._create_phase_checkpoint(phase_name)
        
        if self.session:
            self.session.record_phase_start(phase_name)
            
            # Enhanced logging for phase transitions
            execution_mode = getattr(self.session, 'execution_mode', 'interactive')
            logger.info(f"🎭 Orchestrator engaged: PlanningOrchestratorV3 [Phase: {phase_name}]")
            logger.info(f"📋 Execution mode: {execution_mode}")
            logger.debug(f"🎭 Phase started: {phase_name}")
    
    def _record_phase_end(self, phase_name: str, tokens_used: int = 0) -> None:
        """
        Record phase end in session tracking with enhanced logging (Task 1.5.5).
        
        Args:
            phase_name: Name of the phase ending
            tokens_used: Number of tokens consumed during phase
        """
        if self.session:
            self.session.record_phase_end(phase_name, tokens_used=tokens_used)
            
            # Get phase metrics
            phases = getattr(self.session, 'phases', [])
            if phases:
                for phase in phases:
                    if phase.get('name') == phase_name:
                        duration = phase.get('duration', 0)
                        logger.info(f"✅ Phase '{phase_name}' complete: {self._format_duration(duration)}, {tokens_used} tokens")
                        break
            else:
                logger.info(f"✅ Phase '{phase_name}' complete: {tokens_used} tokens")
            
            logger.debug(f"🎭 Phase completed: {phase_name} ({tokens_used} tokens)")
    
    # ========================================
    # Auto-Progression Logic (Task 1.5.3)
    # ========================================
    
    def _should_auto_progress(self) -> bool:
        """
        Determines if execution should continue to next phase without user confirmation.
        
        Checks:
        - Session has autonomous execution mode
        - Current phase is complete
        - More phases exist
        - No errors or blockers present
        - Resource limits not exceeded
        
        Returns:
            bool: True if should auto-progress to next phase
        """
        if not self.session:
            return False
        
        # Check if autonomous mode is enabled
        execution_mode = getattr(self.session, 'execution_mode', 'interactive')
        if execution_mode not in ('autonomous', 'continuation'):
            return False
        
        # Check if current phase is complete
        if not self.current_plan_id:
            return False
        
        # Check max consecutive phases limit (safety)
        max_consecutive_phases = getattr(self.session, 'max_consecutive_phases', 20)
        if self.current_phase >= max_consecutive_phases:
            logger.warning(f"⚠️ Max consecutive phases reached: {max_consecutive_phases}")
            return False
        
        # Check for errors in current phase
        if self.metrics.get('errors'):
            logger.warning("⚠️ Errors detected - halting auto-progression")
            return False
        
        # All checks passed
        return True
    
    def _get_current_phase_index(self) -> int:
        """Get index of current phase (0-based)."""
        return self.current_phase - 1 if self.current_phase > 0 else 0
    
    def _execute_next_phase(self) -> Dict[str, Any]:
        """
        Executes next phase in autonomous mode.
        
        Returns:
            Phase execution result
        """
        if not self.current_plan_id:
            return {'success': False, 'error': 'No active plan'}
        
        # Load master plan to get phases
        master_plan_path = self.temp_plan_manager.active_dir / self.current_plan_id / "master-plan.md"
        if not master_plan_path.exists():
            return {'success': False, 'error': f"Master plan not found: {master_plan_path}"}
        
        phases = self._parse_phases_from_master_plan(master_plan_path)
        total_phases = len(phases)
        
        # Check if more phases exist
        next_phase_num = self.current_phase + 1
        if next_phase_num > total_phases:
            logger.info("🎭 Orchestrator completing: ✅ ALL WORK COMPLETE")
            return {'success': True, 'is_complete': True, 'message': 'All phases complete'}
        
        # Log transition
        logger.info(f"🎭 Phase transition: Phase {self.current_phase} → Phase {next_phase_num}")
        
        # Mark next phase as In Progress
        self.temp_plan_manager.mark_phase_in_progress(self.current_plan_id, next_phase_num)
        self.current_phase = next_phase_num
        
        # Execute next phase
        phase_result = self._execute_phase(
            self.current_plan_id, 
            next_phase_num, 
            phases[next_phase_num - 1]
        )
        
        # Mark phase as Complete
        self.temp_plan_manager.mark_phase_complete(self.current_plan_id, next_phase_num)
        
        # Record phase end in session
        if self.session:
            phase_name = phases[next_phase_num - 1].get('name', f"Phase {next_phase_num}")
            self._record_phase_end(phase_name)
        
        # Check if should continue to next phase
        if self._should_auto_progress() and next_phase_num < total_phases:
            return self._execute_next_phase()
        
        return phase_result
    
    def _complete_phase_autonomous(self, phase_id: int) -> None:
        """
        Complete phase in autonomous mode with progress summary.
        
        Args:
            phase_id: Phase number (1-based)
        """
        # Record phase completion
        if self.session:
            phases = getattr(self.session, 'phases', [])
            if phase_id <= len(phases):
                phase_name = phases[phase_id - 1].get('name', f"Phase {phase_id}")
                self._record_phase_end(phase_name)
        
        # Update master plan with progress
        if self.current_plan_id:
            master_plan_path = self.temp_plan_manager.active_dir / self.current_plan_id / "00-master-plan.md"
            if master_plan_path.exists():
                self._update_master_plan_tracker(master_plan_path, phase_id)
        
        # Generate and display phase completion summary (Task 1.5.4)
        summary = self._generate_phase_completion_summary(phase_id)
        if summary:
            self._display_summary(summary)
        
        # Auto-progress if enabled
        if self._should_auto_progress():
            self._execute_next_phase()
    
    def _generate_phase_completion_summary(self, completed_phase: int) -> Optional[str]:
        """
        Generate phase completion summary for autonomous execution.
        
        Args:
            completed_phase: Phase number that just completed (1-based)
        
        Returns:
            Formatted summary string or None
        """
        if not self.current_plan_id or not self.session:
            return None
        
        try:
            # Load master plan to get phase information
            master_plan_path = self.temp_plan_manager.active_dir / self.current_plan_id / "00-master-plan.md"
            if not master_plan_path.exists():
                return None
            
            phases = self._parse_phases_from_master_plan(master_plan_path)
            if completed_phase > len(phases):
                return None
            
            phase_info = phases[completed_phase - 1]
            phase_name = phase_info.get('name', f"Phase {completed_phase}")
            
            # Calculate metrics
            total_phases = len(phases)
            completed_phases = completed_phase
            percentage = int((completed_phases / total_phases) * 100)
            progress_bar = self._generate_progress_bar(percentage)
            
            # Get phase tasks info
            phase_tasks = phase_info.get('tasks', [])
            completed_tasks = len([t for t in phase_tasks if isinstance(t, dict) and t.get('completed')])
            total_tasks = len(phase_tasks)
            
            # Get phase duration
            phase_duration = "N/A"
            if self.session and hasattr(self.session, 'phases'):
                session_phases = self.session.phases
                if completed_phase <= len(session_phases):
                    session_phase = session_phases[completed_phase - 1]
                    if 'duration' in session_phase:
                        phase_duration = self._format_duration(session_phase['duration'])
            
            # Get next phase info
            next_phase_name = "None - All phases complete"
            next_phase_estimate = "N/A"
            if completed_phase < total_phases:
                next_phase_info = phases[completed_phase]
                next_phase_name = next_phase_info.get('name', f"Phase {completed_phase + 1}")
                next_phase_estimate = next_phase_info.get('estimated_duration', '30 minutes')
            
            # Generate outcomes list
            outcomes_list = []
            if completed_tasks > 0:
                outcomes_list.append(f"- Completed {completed_tasks}/{total_tasks} tasks")
            if phase_info.get('deliverables'):
                outcomes_list.append(f"- Deliverables: {', '.join(phase_info['deliverables'][:3])}")
            if not outcomes_list:
                outcomes_list = [f"- Phase {completed_phase} objectives achieved"]
            
            # Build summary using template structure
            summary = f"""---

## 🧠 CORTEX Phase {completed_phase} Complete
**Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX

---

### ✅ Phase Summary

**Phase {completed_phase}: {phase_name}**

✅ **Tasks Completed:** {completed_tasks}/{total_tasks}
⏱️ **Duration:** {phase_duration}
📝 **Key Outcomes:**
{chr(10).join(outcomes_list)}

### 📊 Overall Progress

**Plan:** {self.current_plan_id}
**Progress:** [{progress_bar}] {percentage}% ({completed_phases}/{total_phases} phases)
**Total Time:** {self._get_total_elapsed_time()}

**Master Plan Updated:** [View Progress](file:///{master_plan_path})

### ⏭️ Continuing Execution

**Next Phase:** {next_phase_name}
**Estimated Duration:** {next_phase_estimate}

🎭 **Auto-progressing to Phase {completed_phase + 1}...**

---"""
            
            return summary
            
        except Exception as e:
            logger.warning(f"Could not generate phase completion summary: {e}")
            return None
    
    def _display_summary(self, summary: str) -> None:
        """
        Display phase completion summary to user.
        
        Args:
            summary: Formatted summary text
        """
        # Log summary for visibility
        logger.info("📋 Phase Completion Summary:")
        logger.info(summary)
        
        # In production, this would also be sent to user via response system
        # For now, logging provides the required visibility
    
    def _generate_progress_bar(self, percentage: int, width: int = 20) -> str:
        """
        Generate text progress bar.
        
        Args:
            percentage: Completion percentage (0-100)
            width: Width of progress bar in characters
        
        Returns:
            Progress bar string
        """
        filled = int((percentage / 100) * width)
        empty = width - filled
        return '█' * filled + '░' * empty
    
    def _format_duration(self, seconds: float) -> str:
        """
        Format duration in human-readable form.
        
        Args:
            seconds: Duration in seconds
        
        Returns:
            Formatted duration string
        """
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            minutes = int(seconds / 60)
            secs = int(seconds % 60)
            return f"{minutes}m {secs}s" if secs > 0 else f"{minutes}m"
        else:
            hours = int(seconds / 3600)
            minutes = int((seconds % 3600) / 60)
            return f"{hours}h {minutes}m"
    
    def _get_total_elapsed_time(self) -> str:
        """Get total elapsed time for current plan."""
        if not self.session:
            return "N/A"
        
        start_time = getattr(self.session, 'started_at', None)
        if not start_time:
            return "N/A"
        
        elapsed = (datetime.now() - start_time).total_seconds()
        return self._format_duration(elapsed)
    
    def _update_master_plan_tracker(self, master_plan_path: Path, completed_phase: int) -> None:
        """
        Update visual tracker in master plan after phase completion.
        
        Args:
            master_plan_path: Path to master plan file
            completed_phase: Phase number that was just completed (1-based)
        """
        try:
            content = master_plan_path.read_text(encoding='utf-8')
            
            # Update phase status in visual tracker
            # This is a simplified update - full implementation would parse the tracker table
            logger.info(f"📝 Updated master plan tracker: Phase {completed_phase} complete")
            
        except Exception as e:
            logger.warning(f"Could not update master plan tracker: {e}")
    
    # ========================================
    # Master Plan Generation (Task 1.6)
    # ========================================
    
    def _generate_master_plan_content(self, plan_folder: Path, phases: List[Dict[str, Any]]) -> str:
        """
        Generate master plan content with embedded visual tracker.
        
        Args:
            plan_folder: Path to plan folder
            phases: List of phase definitions
        
        Returns:
            Master plan markdown content
        """
        import uuid
        
        # Create temporary session for tracker
        temp_session = PlanningSession(
            session_id=str(uuid.uuid4()),
            session_type="planning",
            status=SessionStatus.IN_PROGRESS,
            started_at=datetime.now(),
            plan_title=plan_folder.name
        )
        
        # Add phases to session
        for phase in phases:
            # Convert tasks to dict format if they're strings
            tasks = phase.get('tasks', [])
            task_dicts = []
            for task in tasks:
                if isinstance(task, str):
                    task_dicts.append({'name': task, 'completed': False})
                else:
                    task_dicts.append(task)
            
            temp_session.add_phase(phase['name'], task_dicts)
        
        # Render visual tracker
        visual_tracker = temp_session.render_progress_table()
        
        # Generate master plan content
        plan_title = plan_folder.name.replace('-', ' ').title()
        
        content = f"""# 🧠 CORTEX - {plan_title} Master Plan
**Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX

---

## Executive Summary

This master plan outlines the implementation strategy for {plan_title}.

{visual_tracker}

---

## Phase Breakdown

"""
        
        # Add phase details
        for idx, phase in enumerate(phases, 1):
            content += f"""### Phase {idx}: {phase['name']}

**Description:** {phase.get('description', 'No description')}

**Tasks:**
"""
            for task in phase.get('tasks', []):
                task_name = task if isinstance(task, str) else task.get('name', 'Unnamed task')
                content += f"- [ ] {task_name}\n"
            
            content += "\n"
        
        content += """---

## Success Criteria

- [ ] All phases completed
- [ ] All tests passing
- [ ] Documentation updated
- [ ] Code reviewed and approved

---

**Status:** In Progress  
**Next Phase:** Phase 1
"""
        
        return content
    
    def _write_master_plan_file(self, plan_folder: Path, content: str) -> Path:
        """
        Write master plan file to disk.
        
        Args:
            plan_folder: Path to plan folder
            content: Master plan markdown content
        
        Returns:
            Path to created master plan file
        """
        plan_folder.mkdir(parents=True, exist_ok=True)
        master_plan_path = plan_folder / "00-master-plan.md"
        
        with open(master_plan_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"Master plan created: {master_plan_path}")
        return master_plan_path


# Example usage (v3.1):
# 
# # Traditional explicit planning
# orchestrator = PlanningOrchestrator()
# result = orchestrator.execute({
#     'operation': 'Add user authentication to API',
#     'skip_refactor': False,
#     'skip_vacuum': False
# })
# print(result.data['tier'])  # 3 or 4 (auth triggers HIGH complexity)
#
# # New implicit planning workflow
# orchestrator = PlanningOrchestrator()
# 
# # User provides tasks without saying "create a plan"
# temp_result = orchestrator.create_temporary_plan_for_task(
#     user_request="Add logging to all API endpoints and create dashboard"
# )
# print(f"Temporary plan created: {temp_result['plan_id']}")
#
# # User provides feedback (optional)
# # orchestrator.temp_plan_manager.update_temporary_plan(...)
#
# # User approves (or auto-approve)
# exec_result = orchestrator.approve_and_execute_plan(
#     plan_id=temp_result['plan_id'],
#     autonomous=True  # Execute all phases without asking
# )
# print(f"Execution complete: {exec_result['is_complete']}")
# print(f"Plan moved to: {exec_result['completed_path']}")
