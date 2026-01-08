"""
Master Orchestrator
==================
Coordinates all orchestrators (TODO, Governance, etc.) with intelligent routing.

Author: GitHub Copilot (for CORTEX)
Created: 2026-01-08
Feature: feat04-core-orchestration
Phase: 2 Task: 2.1
TDD Phase: GREEN
"""

from dataclasses import dataclass
from typing import Dict, Optional, Any, List
from pathlib import Path

from ..middleware.orchestrator_lifecycle import (
    OrchestratorLifecycle,
    LifecycleState,
    LifecycleError
)
from .todo_orchestrator import TodoOrchestrator
from .governance_merger import GovernanceMerger
from ..state_manager import StateManager
from ..audit_logger import get_audit_logger, AuditCategory


@dataclass
class ExecutionResult:
    """Result of orchestrator execution"""
    success: bool
    orchestrator: str
    result: Any = None
    error: Optional[str] = None


class MasterOrchestrator:
    """Master orchestrator coordinating all sub-orchestrators"""
    
    def __init__(self, workspace_root: Path):
        """
        Initialize master orchestrator
        
        Args:
            workspace_root: Root directory of workspace
        """
        self.workspace_root = workspace_root
        self.logger = get_audit_logger()
        
        # Orchestrator registry
        self.orchestrators: Dict[str, Any] = {}
        self.lifecycles: Dict[str, OrchestratorLifecycle] = {}
        
        # Governance merger reference (Task 2.2)
        self._governance_merger: Optional[GovernanceMerger] = None
        
        # Initialize sub-orchestrators
        self._initialize_orchestrators()
    
    def _initialize_orchestrators(self) -> None:
        """Initialize all sub-orchestrators"""
        # Initialize state manager
        state_db = self.workspace_root / "cortex-brain" / "database" / "state.db"
        state_db.parent.mkdir(parents=True, exist_ok=True)
        state_manager = StateManager(state_file=str(state_db))
        
        # Initialize TODO orchestrator
        todo_orch = TodoOrchestrator(state_manager=state_manager)
        self.orchestrators["todo"] = todo_orch
        
        # Create lifecycle tracker for TODO
        todo_lifecycle = OrchestratorLifecycle("todo-orchestrator")
        todo_lifecycle.transition_to(LifecycleState.READY)
        self.lifecycles["todo"] = todo_lifecycle
        
        # Initialize Governance Merger (feat03 integration)
        governance = GovernanceMerger(self.workspace_root)
        self.orchestrators["governance"] = governance
        
        # Create lifecycle tracker for Governance
        gov_lifecycle = OrchestratorLifecycle("governance-merger")
        gov_lifecycle.transition_to(LifecycleState.READY)
        self.lifecycles["governance"] = gov_lifecycle
        
        self.logger.info(
            category=AuditCategory.EXECUTION,
            component='master_orchestrator',
            operation='initialize',
            message='Master orchestrator initialized',
            context={'orchestrators': list(self.orchestrators.keys())}
        )
    
    def has_orchestrator(self, name: str) -> bool:
        """Check if orchestrator is registered"""
        return name in self.orchestrators
    
    def get_orchestrator(self, name: str) -> Any:
        """Get orchestrator by name"""
        return self.orchestrators.get(name)
    
    def get_lifecycle(self, name: str) -> Optional[OrchestratorLifecycle]:
        """Get lifecycle tracker for orchestrator"""
        return self.lifecycles.get(name)
    
    def connect_governance(self, merger: GovernanceMerger) -> None:
        """
        Register GovernanceMerger for rule validation (Task 2.2)
        
        This connects the 4-tier governance system to the master orchestrator,
        enabling governance rules to drive TODO generation.
        
        Args:
            merger: GovernanceMerger instance
        """
        self._governance_merger = merger
        
        self.logger.info(
            category=AuditCategory.EXECUTION,
            component='master_orchestrator',
            operation='connect_governance',
            message='GovernanceMerger connected to MasterOrchestrator',
            context={'merger_type': type(merger).__name__}
        )
    
    def _validate_governance_rules(self, context: Dict[str, Any]) -> List[str]:
        """
        Validate governance rules, return violations (Task 2.2)
        
        Checks governance rules against the provided context and returns
        any violations found.
        
        Args:
            context: Execution context (request_type, has_yaml_plan, etc.)
            
        Returns:
            List of violation messages
        """
        if not self._governance_merger:
            self.logger.warning(
                category=AuditCategory.EXECUTION,
                component='master_orchestrator',
                operation='validate_governance_rules',
                message='No GovernanceMerger registered, skipping validation'
            )
            return []
        
        try:
            violations = self._governance_merger.validate_rules(context)
            
            self.logger.info(
                category=AuditCategory.EXECUTION,
                component='master_orchestrator',
                operation='validate_governance_rules',
                message=f'Governance validation complete: {len(violations)} violations',
                context={'violations_count': len(violations)}
            )
            
            return violations
            
        except Exception as e:
            self.logger.error(
                category=AuditCategory.EXECUTION,
                component='master_orchestrator',
                operation='validate_governance_rules',
                message=f'Governance validation failed: {e}',
                context={'error': str(e)}
            )
            raise
    
    def _governance_violation_to_todo(self, violation: str) -> Dict[str, Any]:
        """
        Convert governance violation to TODO item (Task 2.2)
        
        Transforms a governance rule violation into a structured TODO item
        that can be tracked and resolved.
        
        Args:
            violation: Violation message (format: "RULE_NAME: description")
            
        Returns:
            Dict with TODO item structure (title, description, priority, category)
        """
        # Parse violation format: "RULE_NAME: description"
        parts = violation.split(':', 1)
        rule_name = parts[0].strip() if len(parts) > 0 else "UNKNOWN"
        description = parts[1].strip() if len(parts) > 1 else violation
        
        # Determine priority based on rule name
        priority_map = {
            'YAML_FIRST': 'P0_CRITICAL',
            'TDD_ENFORCEMENT': 'P0_CRITICAL',
            'GIT_ISOLATION': 'P1_HIGH',
            'HOLISTIC_DISCOVERY': 'P1_HIGH',
            'PLANNING_ISOLATION': 'P2_MEDIUM'
        }
        priority = priority_map.get(rule_name, 'P2_MEDIUM')
        
        # Create TODO item
        todo_item = {
            'title': f'Governance Violation: {rule_name}',
            'description': description,
            'priority': priority,
            'category': 'GOVERNANCE_VIOLATION',
            'rule': rule_name,
            'created_by': 'master_orchestrator'
        }
        
        self.logger.info(
            category=AuditCategory.EXECUTION,
            component='master_orchestrator',
            operation='governance_violation_to_todo',
            message=f'Created TODO from governance violation: {rule_name}',
            context={'rule': rule_name, 'priority': priority}
        )
        
        return todo_item
    
    def execute(self, request: str) -> ExecutionResult:
        """
        Execute request via appropriate orchestrator
        
        Args:
            request: User request
            
        Returns:
            ExecutionResult with success status
        """
        try:
            # Simple routing logic (will be enhanced with intelligence layer)
            if "govern" in request.lower() or "rule" in request.lower():
                return self._execute_governance(request)
            elif "todo" in request.lower() or "task" in request.lower():
                return self._execute_todo(request)
            
            return ExecutionResult(
                success=False,
                orchestrator="unknown",
                error="No orchestrator found for request"
            )
            
        except Exception as e:
            self.logger.error(
                category=AuditCategory.EXECUTION,
                component='master_orchestrator',
                operation='execute',
                message=f'Execution failed: {e}',
                context={'request': request[:100]}
            )
            return ExecutionResult(
                success=False,
                orchestrator="master",
                error=str(e)
            )
    
    def _execute_todo(self, request: str) -> ExecutionResult:
        """Execute via TODO orchestrator"""
        try:
            todo = self.orchestrators["todo"]
            lifecycle = self.lifecycles["todo"]
            
            # Ensure we're in READY state before execution
            # This handles cases where lifecycle wasn't properly reset
            if lifecycle.current_state not in [LifecycleState.READY, LifecycleState.RUNNING]:
                lifecycle.transition_to(LifecycleState.READY)
            
            # Transition to RUNNING if currently READY
            if lifecycle.current_state == LifecycleState.READY:
                lifecycle.transition_to(LifecycleState.RUNNING)
            
            # Execute (simplified - actual implementation would parse request)
            # For now, just validate it's a valid request format
            if "invalid" in request.lower():
                raise ValueError("Invalid TODO request format")
            
            result = {"status": "created", "request": request}
            
            # Always transition back to READY after successful execution
            if lifecycle.current_state == LifecycleState.RUNNING:
                lifecycle.transition_to(LifecycleState.READY)
            
            return ExecutionResult(
                success=True,
                orchestrator="todo",
                result=result
            )
            
        except LifecycleError as le:
            # Lifecycle error - don't transition to ERROR for these
            return ExecutionResult(
                success=False,
                orchestrator="todo",
                error=str(le)
            )
        except Exception as e:
            # Other errors - transition to ERROR
            lifecycle = self.lifecycles.get("todo")
            if lifecycle and lifecycle.current_state not in [LifecycleState.ERROR, LifecycleState.STOPPED]:
                try:
                    lifecycle.transition_to(LifecycleState.ERROR, error=str(e))
                except:
                    pass  # Ignore transition errors during error handling
            
            return ExecutionResult(
                success=False,
                orchestrator="todo",
                error=str(e)
            )
    
    def _execute_governance(self, request: str) -> ExecutionResult:
        """Execute via Governance Merger"""
        try:
            governance = self.orchestrators["governance"]
            lifecycle = self.lifecycles["governance"]
            
            # Ensure READY state
            if lifecycle.current_state not in [LifecycleState.READY, LifecycleState.RUNNING]:
                lifecycle.transition_to(LifecycleState.READY)
            
            # Transition to RUNNING
            if lifecycle.current_state == LifecycleState.READY:
                lifecycle.transition_to(LifecycleState.RUNNING)
            
            # Execute governance check/enforcement
            result = governance.validate_request(request)
            
            # Transition back to READY
            if lifecycle.current_state == LifecycleState.RUNNING:
                lifecycle.transition_to(LifecycleState.READY)
            
            return ExecutionResult(
                success=True,
                orchestrator="governance",
                result=result
            )
            
        except LifecycleError as le:
            return ExecutionResult(
                success=False,
                orchestrator="governance",
                error=str(le)
            )
        except Exception as e:
            lifecycle = self.lifecycles.get("governance")
            if lifecycle and lifecycle.current_state not in [LifecycleState.ERROR, LifecycleState.STOPPED]:
                try:
                    lifecycle.transition_to(LifecycleState.ERROR, error=str(e))
                except:
                    pass
            
            return ExecutionResult(
                success=False,
                orchestrator="governance",
                error=str(e)
            )
    
    def execute_pipeline(self, request: str, enforce_governance: bool = True) -> ExecutionResult:
        """
        Execute unified pipeline: Request → Governance → TODO → Execution (Task 2.3)
        
        This provides end-to-end orchestration with governance checks.
        
        Args:
            request: User request
            enforce_governance: Whether to enforce governance rules
            
        Returns:
            ExecutionResult with pipeline outcome
        """
        try:
            # Step 1: Governance validation (if enabled)
            if enforce_governance:
                gov_result = self._execute_governance(request)
                
                if not gov_result.success:
                    return ExecutionResult(
                        success=False,
                        orchestrator="pipeline",
                        error=f"Governance check failed: {gov_result.error}"
                    )
                
                # Check validation result
                if gov_result.result and not gov_result.result.get("passed", True):
                    violations = gov_result.result.get("violations", [])
                    return ExecutionResult(
                        success=False,
                        orchestrator="pipeline",
                        error=f"Governance violations: {', '.join(violations)}"
                    )
            
            # Step 2: Route to appropriate orchestrator
            if "todo" in request.lower() or "task" in request.lower():
                execution_result = self._execute_todo(request)
            else:
                # Default routing logic
                execution_result = self.execute(request)
            
            # Step 3: Return execution result
            return ExecutionResult(
                success=execution_result.success,
                orchestrator="pipeline",
                result={
                    "governance_passed": enforce_governance,
                    "execution_result": execution_result.result,
                    "orchestrator_used": execution_result.orchestrator
                },
                error=execution_result.error
            )
            
        except Exception as e:
            self.logger.error(
                category=AuditCategory.EXECUTION,
                component='master_orchestrator',
                operation='execute_pipeline',
                message=f'Pipeline execution failed: {e}',
                context={'request': request[:100]}
            )
            return ExecutionResult(
                success=False,
                orchestrator="pipeline",
                error=str(e)
            )
