"""
DevOps Orchestrator - CORTEX 4.0

Unified git operations, CI/CD, deployments, maintenance, and cleanup.

Consolidates:
- GitCheckpointOrchestrator (302 LOC)
- GitSyncAndOptimizeOrchestrator (800 LOC)
- deploy.py (120 LOC)
- cleanup.py (557 LOC)

Total: 1,779 LOC → 1,500 LOC (15% reduction)

Author: Asif Hussain
Date: December 10, 2025
"""

from typing import Dict, Any, Optional
from datetime import datetime
import logging

from ...core.base_orchestrator import (
    BaseOrchestrator,
    ValidationResult,
    WorkflowContext,
    OrchestratorResult
)
from ...core.state_machine import StateMachine, OrchestratorStates
from ...core.dependency_container import DependencyContainer
from ...session.session_manager import SessionManager

from .git_operations import GitOperations
from .checkpoint_manager import CheckpointManager
from .deployment_engine import DeploymentEngine
from .cleanup_engine import CleanupEngine
from .sync_coordinator import SyncCoordinator

logger = logging.getLogger(__name__)


class DevOpsOrchestrator(BaseOrchestrator):
    """
    Unified DevOps orchestrator for CORTEX 4.0.
    
    Provides comprehensive DevOps workflow:
    - Git checkpoint creation
    - Git sync and optimization
    - Deployment pipeline (19 gates)
    - System cleanup
    - Branch synchronization
    
    State Machine Flow:
    INITIALIZED → GIT_CHECKPOINT → GIT_SYNC → DEPLOY → CLEANUP → COMPLETED
    """
    
    def __init__(
        self,
        state_machine: StateMachine,
        session_manager: SessionManager,
        container: Optional[DependencyContainer] = None
    ):
        """
        Initialize DevOps orchestrator.
        
        Args:
            state_machine: FSM for workflow validation
            session_manager: Session persistence manager
            container: Optional DI container
        """
        super().__init__(
            orchestrator_name="DevOpsOrchestrator",
            state_machine=state_machine,
            session_manager=session_manager,
            container=container
        )
        
        # Initialize components
        self.git_ops = GitOperations()
        self.checkpoint_mgr = CheckpointManager(self.git_ops)
        self.deployment_engine = DeploymentEngine(self.git_ops)
        self.cleanup_engine = CleanupEngine()
        self.sync_coordinator = SyncCoordinator(self.git_ops)
        
        logger.info("DevOpsOrchestrator initialized with 5 components")
    
    def validate_dor(self, context: WorkflowContext) -> ValidationResult:
        """
        Validate Definition of Ready (DoR).
        
        Prerequisites:
        - Git repository initialized
        - Working directory clean (no uncommitted changes)
        - User has git credentials configured
        - Project path exists
        
        Args:
            context: Workflow context
            
        Returns:
            ValidationResult
        """
        errors = []
        warnings = []
        
        # Check if operation specified
        operation = context.inputs.get('operation')
        if not operation:
            errors.append("No operation specified (checkpoint, sync, deploy, cleanup)")
        
        # Validate git repository
        project_path = context.inputs.get('project_path', '.')
        if not self.git_ops.is_git_repository(project_path):
            errors.append(f"Not a git repository: {project_path}")
        
        # Check for uncommitted changes (warning only)
        if operation in ['deploy', 'sync']:
            if self.git_ops.has_uncommitted_changes(project_path):
                warnings.append("Uncommitted changes detected - will be stashed")
        
        # Check git credentials
        if not self.git_ops.has_git_credentials():
            errors.append("Git credentials not configured")
        
        return ValidationResult(
            passed=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    def validate_dod(self, context: WorkflowContext) -> ValidationResult:
        """
        Validate Definition of Done (DoD).
        
        Success criteria:
        - Operation completed successfully
        - No errors logged
        - Git state consistent
        - Deployment gates passed (if deploying)
        
        Args:
            context: Workflow context
            
        Returns:
            ValidationResult
        """
        errors = []
        warnings = []
        
        operation = context.inputs.get('operation')
        
        # Check operation-specific DoD
        if operation == 'checkpoint':
            if not context.metadata.get('checkpoint_created'):
                errors.append("Checkpoint not created")
        
        elif operation == 'deploy':
            if not context.metadata.get('deployment_successful'):
                errors.append("Deployment failed")
            
            gates_passed = context.metadata.get('gates_passed', 0)
            if gates_passed < 19:
                errors.append(f"Only {gates_passed}/19 deployment gates passed")
        
        elif operation == 'cleanup':
            if not context.metadata.get('cleanup_complete'):
                errors.append("Cleanup not complete")
        
        elif operation == 'sync':
            if not context.metadata.get('sync_successful'):
                errors.append("Sync failed")
        
        return ValidationResult(
            passed=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    def execute_workflow(self, context: WorkflowContext) -> Dict[str, Any]:
        """
        Execute DevOps workflow.
        
        Routes to appropriate operation:
        - checkpoint: Create git checkpoint
        - sync: Sync with remote and optimize
        - deploy: Deploy to publish branch
        - cleanup: System cleanup
        - maintenance: Full maintenance cycle
        
        Args:
            context: Workflow context
            
        Returns:
            Execution outputs
        """
        operation = context.inputs.get('operation', 'checkpoint')
        project_path = context.inputs.get('project_path', '.')
        
        logger.info(f"Executing DevOps operation: {operation}")
        
        # Route to operation handler
        if operation == 'checkpoint':
            return self._execute_checkpoint(context, project_path)
        
        elif operation == 'sync':
            return self._execute_sync(context, project_path)
        
        elif operation == 'deploy':
            return self._execute_deploy(context, project_path)
        
        elif operation == 'cleanup':
            return self._execute_cleanup(context, project_path)
        
        elif operation == 'maintenance':
            return self._execute_maintenance(context, project_path)
        
        else:
            raise ValueError(f"Unknown operation: {operation}")
    
    def _execute_checkpoint(
        self,
        context: WorkflowContext,
        project_path: str
    ) -> Dict[str, Any]:
        """
        Execute git checkpoint operation.
        
        Args:
            context: Workflow context
            project_path: Project directory path
            
        Returns:
            Checkpoint result
        """
        message = context.inputs.get('message', 'Auto-checkpoint')
        
        # Create checkpoint
        checkpoint_id = self.checkpoint_mgr.create_checkpoint(
            project_path=project_path,
            message=message,
            auto_commit=True
        )
        
        context.metadata['checkpoint_created'] = True
        context.metadata['checkpoint_id'] = checkpoint_id
        
        logger.info(f"Checkpoint created: {checkpoint_id}")
        
        return {
            'checkpoint_id': checkpoint_id,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
    
    def _execute_sync(
        self,
        context: WorkflowContext,
        project_path: str
    ) -> Dict[str, Any]:
        """
        Execute git sync and optimization.
        
        Args:
            context: Workflow context
            project_path: Project directory path
            
        Returns:
            Sync result
        """
        branch = context.inputs.get('branch', 'main')
        
        # Sync with remote
        sync_result = self.sync_coordinator.sync_with_remote(
            project_path=project_path,
            branch=branch,
            auto_resolve_conflicts=True
        )
        
        # Optimize repository
        optimize_result = self.sync_coordinator.optimize_repository(
            project_path=project_path
        )
        
        context.metadata['sync_successful'] = sync_result['success']
        context.metadata['conflicts_resolved'] = sync_result.get('conflicts_resolved', 0)
        
        logger.info(f"Sync completed: {sync_result['success']}")
        
        return {
            'sync_result': sync_result,
            'optimize_result': optimize_result
        }
    
    def _execute_deploy(
        self,
        context: WorkflowContext,
        project_path: str
    ) -> Dict[str, Any]:
        """
        Execute deployment pipeline.
        
        Args:
            context: Workflow context
            project_path: Project directory path
            
        Returns:
            Deployment result
        """
        target_branch = context.inputs.get('target_branch', 'publish')
        
        # Run deployment pipeline with 19 gates
        deployment_result = self.deployment_engine.deploy(
            project_path=project_path,
            target_branch=target_branch,
            run_tests=True,
            run_qa_checks=True
        )
        
        context.metadata['deployment_successful'] = deployment_result['success']
        context.metadata['gates_passed'] = deployment_result['gates_passed']
        
        logger.info(
            f"Deployment: {deployment_result['success']} "
            f"({deployment_result['gates_passed']}/19 gates)"
        )
        
        return deployment_result
    
    def _execute_cleanup(
        self,
        context: WorkflowContext,
        project_path: str
    ) -> Dict[str, Any]:
        """
        Execute system cleanup.
        
        Args:
            context: Workflow context
            project_path: Project directory path
            
        Returns:
            Cleanup result
        """
        cleanup_type = context.inputs.get('cleanup_type', 'standard')
        
        # Run cleanup
        cleanup_result = self.cleanup_engine.cleanup(
            project_path=project_path,
            cleanup_type=cleanup_type,
            dry_run=False
        )
        
        context.metadata['cleanup_complete'] = cleanup_result['success']
        context.metadata['files_removed'] = cleanup_result.get('files_removed', 0)
        
        logger.info(f"Cleanup completed: {cleanup_result['files_removed']} files removed")
        
        return cleanup_result
    
    def _execute_maintenance(
        self,
        context: WorkflowContext,
        project_path: str
    ) -> Dict[str, Any]:
        """
        Execute full maintenance cycle.
        
        Includes:
        1. Git checkpoint
        2. System cleanup
        3. Git sync
        4. Repository optimization
        
        Args:
            context: Workflow context
            project_path: Project directory path
            
        Returns:
            Maintenance result
        """
        results = {}
        
        # 1. Checkpoint
        checkpoint_result = self._execute_checkpoint(context, project_path)
        results['checkpoint'] = checkpoint_result
        
        # 2. Cleanup
        cleanup_result = self._execute_cleanup(context, project_path)
        results['cleanup'] = cleanup_result
        
        # 3. Sync
        sync_result = self._execute_sync(context, project_path)
        results['sync'] = sync_result
        
        logger.info("Full maintenance cycle completed")
        
        return results


def create_devops_orchestrator(
    state_machine: Optional[StateMachine] = None,
    session_manager: Optional[SessionManager] = None,
    container: Optional[DependencyContainer] = None
) -> DevOpsOrchestrator:
    """
    Factory function to create DevOps orchestrator.
    
    Args:
        state_machine: Optional FSM (creates default if not provided)
        session_manager: Optional session manager (creates default if not provided)
        container: Optional DI container
        
    Returns:
        DevOpsOrchestrator instance
    """
    from ...core.state_machine import create_basic_orchestrator_fsm
    from ...session.session_manager import get_session_manager
    
    if state_machine is None:
        state_machine = create_basic_orchestrator_fsm("DevOpsOrchestrator")
    
    if session_manager is None:
        session_manager = get_session_manager()
    
    return DevOpsOrchestrator(
        state_machine=state_machine,
        session_manager=session_manager,
        container=container
    )
