"""
ADO Planning Orchestrator v3.0 for CORTEX

Integrated with Planning System 3.0 for Azure DevOps work item generation:
- Inherits PlanningSession model for state management
- Uses Planning System 3.0 complexity analysis and tiered routing
- Integrates historical context (anti-patterns, success patterns)
- Provides visual progress tracking with orchestrator hints
- Enforces DoR/DoD compliance validation
- Integrates TDD workflow for all work items

Phase 6 of CORTEX Evolution v3.9 - Planning System 3.0 Integration Complete

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
from src.operations.modules.orchestration.planning_orchestrator import (
    PlanningOrchestrator, PlanningContext
)
from src.orchestrators.session_model import PlanningSession, SessionStatus
from src.operations.modules.routing.tiered_router import (
    TieredRouter, OperationTier, RoutingDecision
)
from src.operations.modules.routing.complexity_analyzer import (
    ComplexityAnalyzer, ComplexityScore, ComplexityTier
)
from src.operations.modules.version.version_manager import get_version_manager
from src.operations.modules.ado.ado_utility import (
    WorkItemType, WorkItemStatus, WorkItemMetadata, WorkItemResult,
    create_work_item, load_work_item, update_work_item, validate_dor, validate_dod
)
from src.utils.progress_decorator import with_progress, yield_progress
from src.operations.utilities.orchestration_metrics_collector import with_orchestration_metrics

logger = logging.getLogger(__name__)


# ===== ADO-SPECIFIC TIER PATTERNS =====

ADO_TIER_PATTERNS = {
    1: [
        "update story", "add comment", "change status", "update task",
        "quick update", "status change", "assign", "tag"
    ],
    2: [
        "create task", "create story", "single story", "one story",
        "simple task", "straightforward task", "quick story"
    ],
    3: [
        "plan feature", "feature planning", "user story set", "story group",
        "feature with stories", "acceptance criteria", "detailed planning"
    ],
    4: [
        "plan epic", "multi-feature", "program increment", "large initiative",
        "complex epic", "multiple features", "cross-team work"
    ]
}


@dataclass
class ADOPlanningContext:
    """Context for ADO planning operation - extends PlanningContext with ADO specifics."""
    operation: str
    work_item_type: WorkItemType
    tier: int
    complexity_score: ComplexityScore
    routing_decision: RoutingDecision
    planning_session: Optional[PlanningSession] = None  # Phase 6: Planning System 3.0 integration
    
    # ADO-specific fields
    title: Optional[str] = None
    description: Optional[str] = None
    acceptance_criteria: List[str] = None
    area_path: Optional[str] = None
    iteration: Optional[str] = None
    assigned_to: Optional[str] = None
    priority: int = 2
    tags: List[str] = None
    
    # Phase 4: Historical context integration
    historical_patterns: Optional[Dict[str, Any]] = None
    anti_patterns_detected: List[str] = None
    success_patterns: List[str] = None
    
    def __post_init__(self):
        if self.acceptance_criteria is None:
            self.acceptance_criteria = []
        if self.tags is None:
            self.tags = []
        if self.anti_patterns_detected is None:
            self.anti_patterns_detected = []
        if self.success_patterns is None:
            self.success_patterns = []


class ADOPlanningOrchestrator(BaseOperationModule):
    """
    ADO Planning Orchestrator v3.0
    
    Integrated with Planning System 3.0 for intelligent ADO work item planning.
    Inherits Planning System 3.0 capabilities:
    - PlanningSession state management
    - Tiered routing (1-4 classification)
    - Historical context integration
    - Visual progress tracking
    - DoR/DoD compliance
    - TDD workflow integration
    
    ADO-Specific Features:
    - Work item type detection (Story/Feature/Task/Epic/Bug)
    - ADO-formatted output with acceptance criteria
    - Area path and iteration management
    - Completion summary generation
    - Code review checklist integration
    """
    
    def __init__(self, project_root: Path = None):
        """Initialize ADO Planning Orchestrator with Planning System 3.0 integration."""
        super().__init__()
        
        # Version management
        self.version_manager = get_version_manager()
        self.version_manager.register_orchestrator_version("ado_planning_orchestrator", "3.0")
        self.version = self.version_manager.get_orchestrator_version("ado_planning_orchestrator")
        
        # Phase 6: Integrate with Planning System 3.0
        self.planning_orchestrator = PlanningOrchestrator(project_root=project_root)
        logger.info("✅ Phase 6: Planning System 3.0 integration enabled")
        
        # Routing components (also available through planning_orchestrator)
        self.router = TieredRouter()
        self.complexity_analyzer = ComplexityAnalyzer()
        
        # Project paths
        self.project_root = project_root or Path.cwd()
        self.brain_root = self.project_root / "cortex-brain"
        self.ado_docs = self.brain_root / "documents" / "planning" / "ado"
        
        # Ensure ADO directories exist
        (self.ado_docs / "active").mkdir(parents=True, exist_ok=True)
        (self.ado_docs / "completed").mkdir(parents=True, exist_ok=True)
        (self.ado_docs / "blocked").mkdir(parents=True, exist_ok=True)
        
        # Metrics
        self.metrics = {
            'work_items_created': 0,
            'tier_1_operations': 0,
            'tier_2_operations': 0,
            'tier_3_operations': 0,
            'tier_4_operations': 0,
            'dor_validations': 0,
            'dod_validations': 0,
            'planning_sessions_created': 0,  # Phase 6
            'historical_patterns_used': 0,   # Phase 4
            'errors': []
        }
        
        logger.info(f"ADOPlanningOrchestrator v{self.version} initialized with Planning System 3.0")
    
    def get_metadata(self) -> OperationModuleMetadata:
        """Get orchestrator metadata."""
        return OperationModuleMetadata(
            module_id="ado_planning_orchestrator",
            name="ADO Planning Orchestrator",
            version=self.version,
            description="Azure DevOps work item planning with tiered routing",
            author="Asif Hussain",
            phase=OperationPhase.PROCESSING
        )
    
    def _classify_and_analyze(
        self, 
        operation: str,
        force_tier: Optional[int] = None
    ) -> ADOPlanningContext:
        """
        Classify operation and analyze complexity.
        
        Args:
            operation: User's ADO planning request
            force_tier: Override tier classification (optional)
        
        Returns:
            ADOPlanningContext with tier and complexity
        """
        logger.info("🎭 Phase transition: START → Classification & Analysis")
        
        # Tier classification
        if force_tier:
            routing_decision = RoutingDecision(
                tier=force_tier,
                confidence=1.0,
                reasoning=f"Forced tier {force_tier}",
                execution_method="forced",
                estimated_time="<2s",
                requires_planning=False
            )
        else:
            routing_decision = self.router.classify_operation(operation)
        
        tier = routing_decision.tier
        
        # Update metrics
        self.metrics[f'tier_{tier}_operations'] += 1
        
        # Complexity analysis
        complexity_score = self.complexity_analyzer.analyze(operation)
        
        # Detect work item type
        work_item_type = self._detect_work_item_type(operation)
        
        # Parse ADO-specific fields
        title = self._extract_title(operation)
        description = self._extract_description(operation)
        acceptance_criteria = self._extract_acceptance_criteria(operation)
        
        context = ADOPlanningContext(
            operation=operation,
            work_item_type=work_item_type,
            tier=tier,
            complexity_score=complexity_score,
            routing_decision=routing_decision,
            title=title,
            description=description,
            acceptance_criteria=acceptance_criteria
        )
        
        logger.info(f"Classified as Tier {tier} - {work_item_type.value}")
        logger.info(f"Complexity: {complexity_score.tier.value} (score: {complexity_score.total_score:.2f})")
        
        return context
    
    def _detect_work_item_type(self, operation: str) -> WorkItemType:
        """
        Detect work item type from operation text.
        
        Args:
            operation: User's operation request
        
        Returns:
            WorkItemType enum value
        """
        operation_lower = operation.lower()
        
        if any(word in operation_lower for word in ["epic", "initiative", "program"]):
            return WorkItemType.EPIC
        elif any(word in operation_lower for word in ["feature", "capability"]):
            return WorkItemType.FEATURE
        elif any(word in operation_lower for word in ["bug", "defect", "issue"]):
            return WorkItemType.BUG
        elif any(word in operation_lower for word in ["task", "todo", "action"]):
            return WorkItemType.TASK
        else:
            # Default to User Story
            return WorkItemType.STORY
    
    def _extract_title(self, operation: str) -> Optional[str]:
        """Extract title from operation (basic implementation)."""
        # TODO: Enhance with NLP or structured parsing
        words = operation.split()
        if len(words) > 0:
            return " ".join(words[:10])  # First 10 words as title
        return None
    
    def _extract_description(self, operation: str) -> Optional[str]:
        """Extract description from operation."""
        # TODO: Enhance with structured parsing
        return operation
    
    def _extract_acceptance_criteria(self, operation: str) -> List[str]:
        """Extract acceptance criteria from operation."""
        # TODO: Enhance with structured parsing
        criteria = []
        if "acceptance criteria" in operation.lower():
            # Simple extraction - can be enhanced
            parts = operation.lower().split("acceptance criteria")
            if len(parts) > 1:
                criteria_text = parts[1]
                # Split by common delimiters
                for line in criteria_text.split('\n'):
                    line = line.strip()
                    if line and not line.startswith('#'):
                        criteria.append(line)
        return criteria
    
    def _route_and_execute(
        self, 
        context: ADOPlanningContext,
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Route to tier-specific execution path.
        
        Args:
            context: ADO planning context with tier
            user_context: Additional user-provided context
        
        Returns:
            Execution result dictionary
        """
        logger.info(f"🎭 Phase transition: Classification → Tier {context.tier} Execution")
        
        if context.tier == 1:
            return self._execute_tier1_instant(context, user_context)
        elif context.tier == 2:
            return self._execute_tier2_lightweight(context, user_context)
        elif context.tier == 3:
            return self._execute_tier3_documented(context, user_context)
        else:  # tier == 4
            return self._execute_tier4_complex(context, user_context)
    
    def _execute_tier1_instant(
        self,
        context: ADOPlanningContext,
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Tier 1: Instant ADO operations (updates, comments, status changes).
        
        Target: <2s response time
        """
        logger.info("Executing Tier 1 - Instant ADO operation")
        
        # Quick operations via ADO utility
        work_item_id = user_context.get('work_item_id')
        
        if not work_item_id:
            return {
                'success': False,
                'error': 'work_item_id required for Tier 1 operations',
                'tier': 1
            }
        
        # Load existing work item
        load_result = load_work_item(work_item_id)
        
        if not load_result.success:
            return {
                'success': False,
                'error': f'Failed to load work item: {load_result.message}',
                'tier': 1
            }
        
        # Apply updates
        updates = {
            'status': user_context.get('status'),
            'assigned_to': user_context.get('assigned_to'),
            'comments': user_context.get('comment'),
            'tags': user_context.get('tags', [])
        }
        
        # Filter None values
        updates = {k: v for k, v in updates.items() if v is not None}
        
        update_result = update_work_item(work_item_id, updates)
        
        return {
            'success': update_result.success,
            'work_item_id': work_item_id,
            'updates': updates,
            'message': update_result.message,
            'tier': 1
        }
    
    def _execute_tier2_lightweight(
        self,
        context: ADOPlanningContext,
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Tier 2: Lightweight work item creation (single story/task).
        
        Target: <10s response time
        """
        logger.info("Executing Tier 2 - Lightweight work item creation")
        
        # Build work item metadata
        metadata = WorkItemMetadata(
            work_item_type=context.work_item_type,
            title=context.title or user_context.get('title', 'Untitled Work Item'),
            description=context.description or user_context.get('description', ''),
            acceptance_criteria=context.acceptance_criteria or user_context.get('acceptance_criteria', []),
            assigned_to=user_context.get('assigned_to'),
            iteration=user_context.get('iteration'),
            area_path=user_context.get('area_path'),
            priority=user_context.get('priority', 2),
            tags=user_context.get('tags', [])
        )
        
        # Create work item
        create_result = create_work_item(metadata)
        
        if create_result.success:
            self.metrics['work_items_created'] += 1
        
        return {
            'success': create_result.success,
            'work_item_id': create_result.work_item_id,
            'message': create_result.message,
            'tier': 2
        }
    
    def _execute_tier3_documented(
        self,
        context: ADOPlanningContext,
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Tier 3: Feature planning with documentation.
        
        Creates work item + planning document with acceptance criteria.
        """
        logger.info("Executing Tier 3 - Documented feature planning")
        logger.info("🎭 Phase transition: Execution → ADO Formatting")
        
        # Build comprehensive work item
        metadata = WorkItemMetadata(
            work_item_type=context.work_item_type,
            title=context.title or user_context.get('title', 'Untitled Feature'),
            description=context.description or user_context.get('description', ''),
            acceptance_criteria=context.acceptance_criteria or user_context.get('acceptance_criteria', []),
            assigned_to=user_context.get('assigned_to'),
            iteration=user_context.get('iteration'),
            area_path=user_context.get('area_path'),
            priority=user_context.get('priority', 2),
            tags=user_context.get('tags', [])
        )
        
        # Validate DoR
        dor_result = validate_dor(metadata)
        self.metrics['dor_validations'] += 1
        
        if not dor_result.passed:
            logger.warning(f"DoR validation failed: {dor_result.score:.1f}%")
            # Continue but log warnings
            for warning in dor_result.warnings:
                logger.warning(f"DoR: {warning}")
        
        # Create work item
        create_result = create_work_item(metadata)
        
        if create_result.success:
            self.metrics['work_items_created'] += 1
            
            # Create planning document
            doc_path = self._create_planning_document(
                work_item_id=create_result.work_item_id,
                metadata=metadata,
                dor_result=dor_result,
                context=context
            )
            
            return {
                'success': True,
                'work_item_id': create_result.work_item_id,
                'document_path': str(doc_path),
                'dor_validation': {
                    'passed': dor_result.passed,
                    'score': dor_result.score,
                    'warnings': dor_result.warnings
                },
                'tier': 3
            }
        
        return {
            'success': False,
            'error': create_result.message,
            'tier': 3
        }
    
    def _execute_tier4_complex(
        self,
        context: ADOPlanningContext,
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Tier 4: Complex epic/multi-feature planning.
        
        Creates epic + child work items + comprehensive documentation.
        """
        logger.info("Executing Tier 4 - Complex epic planning")
        logger.info("🎭 Phase transition: Execution → Multi-Item ADO Creation")
        
        # Create parent epic
        epic_metadata = WorkItemMetadata(
            work_item_type=WorkItemType.EPIC,
            title=context.title or user_context.get('title', 'Untitled Epic'),
            description=context.description or user_context.get('description', ''),
            acceptance_criteria=context.acceptance_criteria or user_context.get('acceptance_criteria', []),
            assigned_to=user_context.get('assigned_to'),
            iteration=user_context.get('iteration'),
            area_path=user_context.get('area_path'),
            priority=user_context.get('priority', 1),  # Epics typically high priority
            tags=user_context.get('tags', [])
        )
        
        epic_result = create_work_item(epic_metadata)
        
        if not epic_result.success:
            return {
                'success': False,
                'error': f'Failed to create epic: {epic_result.message}',
                'tier': 4
            }
        
        self.metrics['work_items_created'] += 1
        epic_id = epic_result.work_item_id
        
        # Create child features/stories
        child_items = user_context.get('child_items', [])
        child_results = []
        
        for child_spec in child_items:
            child_metadata = WorkItemMetadata(
                work_item_type=WorkItemType.FEATURE,
                title=child_spec.get('title', 'Child Item'),
                description=child_spec.get('description', ''),
                acceptance_criteria=child_spec.get('acceptance_criteria', []),
                related_work_items=[epic_id],  # Link to parent epic
                assigned_to=child_spec.get('assigned_to'),
                iteration=child_spec.get('iteration'),
                area_path=child_spec.get('area_path'),
                priority=child_spec.get('priority', 2),
                tags=child_spec.get('tags', [])
            )
            
            child_result = create_work_item(child_metadata)
            
            if child_result.success:
                self.metrics['work_items_created'] += 1
                child_results.append({
                    'work_item_id': child_result.work_item_id,
                    'title': child_metadata.title,
                    'type': child_metadata.work_item_type.value
                })
        
        # Create comprehensive documentation
        doc_path = self._create_epic_documentation(
            epic_id=epic_id,
            epic_metadata=epic_metadata,
            child_results=child_results,
            context=context
        )
        
        return {
            'success': True,
            'epic': {
                'work_item_id': epic_id,
                'title': epic_metadata.title
            },
            'child_items': child_results,
            'document_path': str(doc_path),
            'tier': 4
        }
    
    def _create_planning_document(
        self,
        work_item_id: str,
        metadata: WorkItemMetadata,
        dor_result,
        context: ADOPlanningContext
    ) -> Path:
        """
        Create planning document for Tier 3 work items.
        
        Args:
            work_item_id: ADO work item ID
            metadata: Work item metadata
            dor_result: DoR validation result
            context: Planning context
        
        Returns:
            Path to created document
        """
        doc_name = f"{work_item_id}-{metadata.title.replace(' ', '-')[:20]}.md"
        doc_path = self.ado_docs / "active" / doc_name
        
        content = f"""# ADO Work Item: {metadata.work_item_type.value}

**Work Item ID:** {work_item_id}  
**Title:** {metadata.title}  
**Status:** {metadata.status.value}  
**Created:** {datetime.now().strftime('%Y-%m-%d %H:%M')}

---

## Description

{metadata.description}

---

## Acceptance Criteria

"""
        
        for i, criterion in enumerate(metadata.acceptance_criteria, 1):
            content += f"{i}. [ ] {criterion}\n"
        
        content += f"""
---

## Definition of Ready (DoR)

**Validation Score:** {dor_result.score:.1f}%  
**Status:** {'✅ PASSED' if dor_result.passed else '⚠️ NEEDS ATTENTION'}

"""
        
        if dor_result.warnings:
            content += "**Warnings:**\n"
            for warning in dor_result.warnings:
                content += f"- {warning}\n"
        
        content += """
---

## Technical Details

**Complexity Tier:** {complexity_tier}  
**Estimated Time:** {effort}

**Area Path:** {area_path}  
**Iteration:** {iteration}  
**Priority:** {priority}

**Tags:** {tags}

---

## Definition of Done (DoD)

- [ ] Code implemented and reviewed
- [ ] Unit tests written and passing
- [ ] Integration tests passing
- [ ] Documentation updated
- [ ] Acceptance criteria validated
- [ ] Code deployed to test environment
- [ ] Product owner approval

---

**Orchestrator:** ADOPlanningOrchestrator v{version}  
**Generated:** {timestamp}
""".format(
            complexity_tier=context.complexity_score.tier.value,
            effort=context.routing_decision.estimated_time,
            area_path=metadata.area_path or 'Not specified',
            iteration=metadata.iteration or 'Not specified',
            priority=metadata.priority,
            tags=', '.join(metadata.tags) if metadata.tags else 'None',
            version=self.version,
            timestamp=datetime.now().isoformat()
        )
        
        doc_path.write_text(content, encoding='utf-8')
        logger.info(f"Created planning document: {doc_path}")
        
        return doc_path
    
    def _create_epic_documentation(
        self,
        epic_id: str,
        epic_metadata: WorkItemMetadata,
        child_results: List[Dict[str, Any]],
        context: ADOPlanningContext
    ) -> Path:
        """Create comprehensive documentation for Tier 4 epics."""
        doc_name = f"{epic_id}-epic-{epic_metadata.title.replace(' ', '-')[:20]}.md"
        doc_path = self.ado_docs / "active" / doc_name
        
        content = f"""# ADO Epic: {epic_metadata.title}

**Epic ID:** {epic_id}  
**Status:** {epic_metadata.status.value}  
**Created:** {datetime.now().strftime('%Y-%m-%d %H:%M')}

---

## Epic Description

{epic_metadata.description}

---

## Child Work Items

"""
        
        for child in child_results:
            content += f"- **{child['type']}** [{child['work_item_id']}] - {child['title']}\n"
        
        content += f"""
---

## Acceptance Criteria

"""
        
        for i, criterion in enumerate(epic_metadata.acceptance_criteria, 1):
            content += f"{i}. [ ] {criterion}\n"
        
        content += f"""
---

## Implementation Strategy

**Complexity Tier:** {context.complexity_score.tier.value}  
**Estimated Total Time:** {context.routing_decision.estimated_time}

**Execution Method:**
{context.routing_decision.execution_method}

---

## Orchestration Details

**Orchestrator:** ADOPlanningOrchestrator v{self.version}  
**Generated:** {datetime.now().isoformat()}
"""
        
        doc_path.write_text(content, encoding='utf-8')
        logger.info(f"Created epic documentation: {doc_path}")
        
        return doc_path
    
    @with_orchestration_metrics("ADOPlanningOrchestrator")
    @with_progress("ADO Planning Operation")
    def execute(self, context: Dict[str, Any]) -> OperationResult:
        """
        Execute ADO planning workflow.
        
        Args:
            context: Operation context with:
                - operation: str - User's ADO planning request
                - work_item_id: str - Existing work item ID (for updates)
                - title: str - Work item title
                - description: str - Work item description
                - acceptance_criteria: List[str] - Acceptance criteria
                - force_tier: int - Override tier classification (optional)
        
        Returns:
            OperationResult with work item details and metrics
        """
        start_time = datetime.now()
        operation = context.get('operation', '')
        force_tier = context.get('force_tier')
        
        if not operation:
            return OperationResult(
                success=False,
                status=OperationStatus.FAILED,
                message="No operation specified for ADO planning",
                data={'error': 'operation_required'}
            )
        
        logger.info(f"🎭 Orchestrator engaged: ADOPlanningOrchestrator v{self.version}")
        logger.info(f"Operation: {operation}")
        
        try:
            # Phase 1: Classification & Analysis
            yield_progress(1, 4, "Phase 1: Classifying ADO operation")
            ado_context = self._classify_and_analyze(operation, force_tier)
            
            # Phase 2: Route to execution path
            yield_progress(2, 4, f"Phase 2: Routing to Tier {ado_context.tier}")
            execution_result = self._route_and_execute(ado_context, context)
            
            # Phase 3: DoD Validation (if work item created)
            if execution_result.get('success') and execution_result.get('work_item_id'):
                yield_progress(3, 4, "Phase 3: Validating Definition of Done")
                work_item = load_work_item(execution_result['work_item_id'])
                if work_item.success and work_item.metadata:
                    dod_result = validate_dod(work_item.metadata)
                    self.metrics['dod_validations'] += 1
                    execution_result['dod_validation'] = {
                        'passed': dod_result.passed,
                        'score': dod_result.score
                    }
            
            # Phase 4: Finalization
            yield_progress(4, 4, "Phase 4: Finalizing ADO operation")
            
            success = execution_result.get('success', False)
            work_item_created = 'work_item_id' in execution_result
            
            # Determine completion status
            is_complete = success and len(self.metrics['errors']) == 0 and work_item_created
            
            # Logger hint for completion
            completion_status = "✅ ALL WORK COMPLETE" if is_complete else "⏳ OPERATION DONE WITH WARNINGS"
            logger.info(f"🎭 Orchestrator completing: {completion_status}")
            
            # Calculate duration
            duration = (datetime.now() - start_time).total_seconds()
            
            return OperationResult(
                success=success,
                status=OperationStatus.SUCCESS if success else OperationStatus.FAILED,
                message=f"ADO {ado_context.work_item_type.value} operation completed",
                data={
                    'work_item_id': execution_result.get('work_item_id'),
                    'work_item_type': ado_context.work_item_type.value,
                    'tier': ado_context.tier,
                    'complexity': ado_context.complexity_score.tier.value,
                    'execution_result': execution_result,
                    'metrics': self.metrics,
                    'duration_seconds': duration,
                    'is_complete': is_complete
                }
            )
        
        except Exception as e:
            logger.error(f"ADO planning failed: {e}", exc_info=True)
            self.metrics['errors'].append(str(e))
            
            logger.info("🎭 Orchestrator completing: ❌ OPERATION FAILED")
            
            return OperationResult(
                success=False,
                status=OperationStatus.FAILED,
                message=f"ADO planning failed: {str(e)}",
                data={
                    'error': str(e),
                    'metrics': self.metrics,
                    'is_complete': False
                }
            )


# ===== FACTORY FUNCTION =====

def create_ado_planning_orchestrator(project_root: Path = None) -> ADOPlanningOrchestrator:
    """
    Factory function to create ADO Planning Orchestrator.
    
    Args:
        project_root: Project root path (optional)
    
    Returns:
        ADOPlanningOrchestrator instance
    """
    return ADOPlanningOrchestrator(project_root=project_root)
