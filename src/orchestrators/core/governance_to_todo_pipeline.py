"""
Governance-to-Todo Pipeline - AC-ORCH-007

Implements the core CORTEX workflow:
  (1) GovernanceMerger merges all 4 tiers of governance rules
  (2) MasterOrchestrator evaluates request against merged ruleset
  (3) TodoManager creates actionable tasks based on evaluation
  (4) MasterOrchestrator executes tasks

This pipeline is THE CORE OF CORTEX operation.

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import logging
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from enum import Enum
from uuid import uuid4
from datetime import datetime

from src.orchestrators.core.governance_merger import GovernanceMerger
from src.orchestrators.master_orchestrator import MasterOrchestrator
from src.orchestrators.master.todo_manager import TodoManager, TaskStatus


logger = logging.getLogger("cortex.orchestrators.core.governance_to_todo_pipeline")


class RequestType(Enum):
    """Type of incoming request."""
    PLAN = "plan"
    IMPLEMENT = "implement"
    TEST = "test"
    VALIDATE = "validate"
    INVESTIGATE = "investigate"
    ADO = "ado"
    CRAWL = "crawl"
    CLEANUP = "cleanup"
    OTHER = "other"


@dataclass
class GovernanceEvaluation:
    """Result of governance evaluation."""
    request_valid: bool
    violations: List[str]
    required_actions: List[str]
    governance_rules_applied: List[str]
    tier_precedence: Dict[str, int]  # tier_name -> precedence level


@dataclass
class PipelineExecutionResult:
    """Result of complete governance-to-todo pipeline execution."""
    request_id: str
    status: str  # "success", "failed", "blocked"
    evaluation: GovernanceEvaluation
    task_ids: List[str]
    execution_results: Dict[str, Any]
    errors: List[str]


class GovernanceToTodoPipeline:
    """
    Core CORTEX workflow pipeline.
    
    Orchestrates the 4-step process:
      1. Merge all governance tiers
      2. Evaluate request against merged rules
      3. Create tasks from evaluation
      4. Execute tasks
    """

    def __init__(
        self,
        governance_merger: GovernanceMerger,
        master_orchestrator: MasterOrchestrator,
        todo_manager: TodoManager
    ):
        """Initialize pipeline with component dependencies."""
        self.governance_merger = governance_merger
        self.master_orchestrator = master_orchestrator
        self.todo_manager = todo_manager
        self.logger = logging.getLogger("cortex.governance_to_todo_pipeline")

    def execute_request(
        self,
        user_intent: str,
        request_type: RequestType,
        context: Optional[Dict[str, Any]] = None
    ) -> PipelineExecutionResult:
        """
        Execute complete governance-to-todo pipeline for a user request.
        
        Args:
            user_intent: User's request description
            request_type: Classified request type
            context: Optional execution context
            
        Returns:
            PipelineExecutionResult with full execution details
        """
        request_id = str(uuid4())
        self.logger.info(
            f"Starting pipeline execution",
            extra={
                "request_id": request_id,
                "intent": user_intent,
                "type": request_type.value
            }
        )

        result = PipelineExecutionResult(
            request_id=request_id,
            status="failed",
            evaluation=None,
            task_ids=[],
            execution_results={},
            errors=[]
        )

        try:
            # STEP 1: Merge governance tiers
            self.logger.debug(f"[{request_id}] STEP 1: Merging governance tiers")
            evaluation = self._evaluate_governance(user_intent, request_type, context)
            result.evaluation = evaluation

            if not evaluation.request_valid:
                result.status = "blocked"
                result.errors = evaluation.violations
                self.logger.warning(
                    f"[{request_id}] Request blocked by governance rules",
                    extra={"violations": evaluation.violations}
                )
                return result

            # STEP 2: Create tasks from evaluation
            self.logger.debug(f"[{request_id}] STEP 2: Creating tasks from evaluation")
            task_ids = self._create_tasks_from_evaluation(
                request_id,
                user_intent,
                evaluation
            )
            result.task_ids = task_ids
            self.logger.info(
                f"[{request_id}] Created {len(task_ids)} tasks",
                extra={"task_ids": task_ids}
            )

            # STEP 3: Execute tasks
            self.logger.debug(f"[{request_id}] STEP 3: Executing tasks")
            execution_results = self._execute_tasks(request_id, task_ids)
            result.execution_results = execution_results

            # STEP 4: Mark pipeline successful
            result.status = "success"
            self.logger.info(
                f"[{request_id}] Pipeline execution complete",
                extra={
                    "status": result.status,
                    "tasks_created": len(task_ids),
                    "results": execution_results
                }
            )

            return result

        except Exception as e:
            result.status = "failed"
            result.errors.append(str(e))
            self.logger.error(
                f"[{request_id}] Pipeline execution failed",
                exc_info=True,
                extra={"error": str(e)}
            )
            return result

    def _evaluate_governance(
        self,
        user_intent: str,
        request_type: RequestType,
        context: Optional[Dict[str, Any]] = None
    ) -> GovernanceEvaluation:
        """
        STEP 1: Merge governance tiers and evaluate request.
        
        Returns:
            GovernanceEvaluation with validation result and actions
        """
        self.logger.debug("Merging governance tiers (T0, T1, T2, T3)")
        
        try:
            # Merge all tiers
            unified_ruleset = self.governance_merger.merge_all_tiers()
            
            # Validate request against merged rules
            violations = []
            required_actions = []
            governance_rules_applied = []
            
            # Check SKULL rules (Tier 0)
            skull_violations = self._check_skull_rules(user_intent)
            violations.extend(skull_violations)
            if skull_violations:
                governance_rules_applied.append("SKULL_RULES")
            
            # Check business rules (Tier 1)
            business_violations = self._check_business_rules(user_intent, context)
            violations.extend(business_violations)
            if business_violations:
                governance_rules_applied.append("BUSINESS_RULES")
            
            # Check engineering standards (Tier 2)
            engineering_violations = self._check_engineering_standards(user_intent)
            violations.extend(engineering_violations)
            if engineering_violations:
                governance_rules_applied.append("ENGINEERING_STANDARDS")
            
            # Determine required actions based on request type
            required_actions = self._determine_required_actions(
                request_type,
                user_intent
            )
            
            return GovernanceEvaluation(
                request_valid=len(violations) == 0,
                violations=violations,
                required_actions=required_actions,
                governance_rules_applied=governance_rules_applied,
                tier_precedence={
                    "tier0_skull": 0,  # Highest precedence
                    "tier1_business": 1,
                    "tier2_engineering": 2,
                    "tier3_patterns": 3  # Lowest precedence
                }
            )
            
        except Exception as e:
            self.logger.error(f"Governance evaluation failed: {e}", exc_info=True)
            return GovernanceEvaluation(
                request_valid=False,
                violations=[f"Governance evaluation error: {str(e)}"],
                required_actions=[],
                governance_rules_applied=[],
                tier_precedence={}
            )

    def _check_skull_rules(self, user_intent: str) -> List[str]:
        """Check SKULL (Tier 0) governance violations."""
        violations = []
        
        # CORE-001: Incremental Execution
        # Check for requests that would require >500 lines
        if "generate" in user_intent.lower() and "full" in user_intent.lower():
            violations.append("CORE-001: Cannot generate >500 lines in single operation")
        
        # CORE-002: No Summary Files
        if "create summary" in user_intent.lower():
            violations.append("CORE-002: Summary file creation not allowed")
        
        # CORE-005: Path Portability
        if "hardcode" in user_intent.lower():
            violations.append("CORE-005: Hardcoded paths not allowed")
        
        # CORE-008: TDD Enforcement
        if "implement" in user_intent.lower() and "without test" in user_intent.lower():
            violations.append("CORE-008: Implementation without TDD not allowed")
        
        # CORE-009: Plan File Organization
        if "plan" in user_intent.lower() and "root" in user_intent.lower():
            violations.append("CORE-009: Root-level plans not allowed")
        
        # CORE-017: Governance Enforcement
        if "bypass governance" in user_intent.lower():
            violations.append("CORE-017: Cannot bypass governance rules")
        
        # CORE-019: TDD-Master Required
        if "direct code" in user_intent.lower():
            violations.append("CORE-019: Direct coding without TDD not allowed")
        
        return violations

    def _check_business_rules(
        self,
        user_intent: str,
        context: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """Check business rules (Tier 1) violations."""
        violations = []
        
        # Would check against cortex-brain/tier1/company-practices.yaml
        # For now, return empty (no business violations)
        
        return violations

    def _check_engineering_standards(self, user_intent: str) -> List[str]:
        """Check engineering standards (Tier 2) violations."""
        violations = []
        
        # Would check against cortex-brain/tier2/engineering-standards.yaml
        # For now, return empty (no engineering violations)
        
        return violations

    def _determine_required_actions(
        self,
        request_type: RequestType,
        user_intent: str
    ) -> List[str]:
        """Determine required actions based on request type."""
        actions = []
        
        if request_type == RequestType.PLAN:
            actions = [
                "LOAD_CONTEXT",
                "GENERATE_PLAN",
                "VALIDATE_AC_IDS",
                "SYNC_DASHBOARD"
            ]
        elif request_type == RequestType.IMPLEMENT:
            actions = [
                "LOAD_CONTEXT",
                "CREATE_FILE",
                "WRITE_TESTS",
                "RUN_TESTS",
                "UPDATE_TRACKER",
                "SYNC_DASHBOARD"
            ]
        elif request_type == RequestType.TEST:
            actions = [
                "RUN_TESTS",
                "GENERATE_COVERAGE",
                "UPDATE_TRACKER"
            ]
        elif request_type == RequestType.VALIDATE:
            actions = [
                "LOAD_CONTEXT",
                "RUN_VALIDATION",
                "VERIFY_EVIDENCE",
                "UPDATE_TRACKER"
            ]
        elif request_type == RequestType.ADO:
            actions = [
                "CONNECT_ADO",
                "LOAD_WORKITEMS",
                "CREATE_WORKITEMS",
                "UPDATE_WORKITEMS"
            ]
        else:
            actions = [
                "LOAD_CONTEXT",
                "ROUTE_REQUEST",
                "EXECUTE"
            ]
        
        return actions

    def _create_tasks_from_evaluation(
        self,
        request_id: str,
        user_intent: str,
        evaluation: GovernanceEvaluation
    ) -> List[str]:
        """
        STEP 2: Create tasks from governance evaluation.
        
        Returns:
            List of task IDs created
        """
        task_ids = []
        
        for action in evaluation.required_actions:
            task = self.todo_manager.create_task(
                name=action,
                description=f"Action required: {action}",
                metadata={
                    "request_id": request_id,
                    "user_intent": user_intent,
                    "governance_rules": evaluation.governance_rules_applied,
                    "action_type": action
                }
            )
            task_ids.append(task.id)
            self.logger.debug(
                f"Created task {task.id} for action {action}",
                extra={"task_id": task.id, "action": action}
            )
        
        return task_ids

    def _execute_tasks(
        self,
        request_id: str,
        task_ids: List[str]
    ) -> Dict[str, Any]:
        """
        STEP 3 & 4: Execute tasks in order.
        
        Returns:
            Dict with task execution results
        """
        results = {}
        
        for task_id in task_ids:
            try:
                task = self.todo_manager.get_task(task_id)
                self.logger.debug(
                    f"Executing task {task_id}: {task.name}",
                    extra={"task_id": task_id, "task_name": task.name}
                )
                
                # Mark task as in progress
                self.todo_manager.update_task_status(task_id, TaskStatus.IN_PROGRESS)
                
                # Execute via MasterOrchestrator
                # (would delegate to appropriate orchestrator based on task type)
                execution_result = self._execute_single_task(task)
                
                # Mark task as complete
                if execution_result.get("success"):
                    self.todo_manager.update_task_status(task_id, TaskStatus.COMPLETE)
                else:
                    self.todo_manager.update_task_status(task_id, TaskStatus.FAILED)
                
                results[task_id] = execution_result
                
            except Exception as e:
                self.logger.error(
                    f"Task {task_id} execution failed: {e}",
                    exc_info=True,
                    extra={"task_id": task_id}
                )
                self.todo_manager.update_task_status(task_id, TaskStatus.FAILED)
                results[task_id] = {"success": False, "error": str(e)}
        
        return results

    def _execute_single_task(self, task) -> Dict[str, Any]:
        """Execute a single task."""
        # Stub: Would delegate to orchestrator based on task.name/metadata
        return {
            "success": True,
            "task_id": task.id,
            "executed_at": datetime.now().isoformat()
        }

    def get_pipeline_status(self, request_id: str) -> Dict[str, Any]:
        """Get current status of a pipeline execution."""
        return {
            "request_id": request_id,
            "status": "executing",
            "timestamp": datetime.now().isoformat()
        }
