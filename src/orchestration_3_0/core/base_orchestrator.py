"""
Base Orchestrator for CORTEX 4.0

Provides common orchestrator functionality and contracts.

Author: Asif Hussain
Date: December 10, 2025
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import logging
import uuid

from .state_machine import StateMachine, OrchestratorStates
from .dependency_container import DependencyContainer
from ..session.session_manager import SessionManager, WorkflowSession

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of DoR/DoD validation."""
    passed: bool
    errors: list[str]
    warnings: list[str]
    
    def is_valid(self) -> bool:
        """Check if validation passed with no errors."""
        return self.passed and len(self.errors) == 0


@dataclass
class OrchestratorResult:
    """Result of orchestrator execution."""
    success: bool
    session_id: str
    orchestrator_name: str
    final_state: str
    execution_time_seconds: float
    outputs: Dict[str, Any]
    errors: list[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'success': self.success,
            'session_id': self.session_id,
            'orchestrator_name': self.orchestrator_name,
            'final_state': self.final_state,
            'execution_time_seconds': self.execution_time_seconds,
            'outputs': self.outputs,
            'errors': self.errors
        }


@dataclass
class WorkflowContext:
    """Context information for workflow execution."""
    tenant_id: str
    project_id: str
    user_id: str
    session_id: str
    inputs: Dict[str, Any]
    metadata: Dict[str, Any]


class BaseOrchestrator(ABC):
    """
    Base class for all CORTEX 4.0 orchestrators.
    
    Provides:
    - State machine integration
    - Session management
    - DoR/DoD validation
    - Error handling
    - Logging
    """
    
    def __init__(
        self,
        orchestrator_name: str,
        state_machine: StateMachine,
        session_manager: SessionManager,
        container: Optional[DependencyContainer] = None
    ):
        """
        Initialize base orchestrator.
        
        Args:
            orchestrator_name: Name of orchestrator
            state_machine: FSM for workflow validation
            session_manager: Session persistence manager
            container: Optional DI container
        """
        self.orchestrator_name = orchestrator_name
        self.state_machine = state_machine
        self.session_manager = session_manager
        self.container = container
        self._start_time: Optional[datetime] = None
        
        logger.info(f"{orchestrator_name} initialized")
    
    def execute(
        self,
        tenant_id: str,
        project_id: str,
        user_id: str,
        inputs: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> OrchestratorResult:
        """
        Execute orchestrator workflow.
        
        Args:
            tenant_id: Tenant identifier
            project_id: Project identifier
            user_id: User identifier
            inputs: Optional input parameters
            **kwargs: Additional arguments
            
        Returns:
            OrchestratorResult
        """
        self._start_time = datetime.now()
        session_id = str(uuid.uuid4())
        
        # Create session
        session = self.session_manager.create_session(
            session_id=session_id,
            orchestrator_name=self.orchestrator_name,
            tenant_id=tenant_id,
            project_id=project_id,
            user_id=user_id,
            initial_state=self.state_machine.current_state,
            metadata={'inputs': inputs or {}, **kwargs}
        )
        
        # Create context
        context = WorkflowContext(
            tenant_id=tenant_id,
            project_id=project_id,
            user_id=user_id,
            session_id=session_id,
            inputs=inputs or {},
            metadata=kwargs
        )
        
        try:
            # Transition to DoR validation
            self.state_machine.transition_to(OrchestratorStates.VALIDATING_DOR)
            self.session_manager.update_session_state(session_id, OrchestratorStates.VALIDATING_DOR)
            
            # Validate DoR
            dor_result = self.validate_dor(context)
            if not dor_result.is_valid():
                logger.error(f"{self.orchestrator_name} DoR validation failed: {dor_result.errors}")
                self.state_machine.transition_to(OrchestratorStates.FAILED)
                self.session_manager.fail_session(session_id, {'dor_errors': dor_result.errors})
                
                return self._create_error_result(
                    session_id=session_id,
                    errors=dor_result.errors
                )
            
            # Transition to executing
            self.state_machine.transition_to(OrchestratorStates.EXECUTING)
            self.session_manager.update_session_state(session_id, OrchestratorStates.EXECUTING)
            
            # Execute workflow
            outputs = self.execute_workflow(context)
            
            # Transition to DoD validation
            self.state_machine.transition_to(OrchestratorStates.VALIDATING_DOD)
            self.session_manager.update_session_state(session_id, OrchestratorStates.VALIDATING_DOD)
            
            # Validate DoD
            dod_result = self.validate_dod(context)
            if not dod_result.is_valid():
                logger.error(f"{self.orchestrator_name} DoD validation failed: {dod_result.errors}")
                self.state_machine.transition_to(OrchestratorStates.FAILED)
                self.session_manager.fail_session(session_id, {'dod_errors': dod_result.errors})
                
                return self._create_error_result(
                    session_id=session_id,
                    errors=dod_result.errors
                )
            
            # Success!
            self.state_machine.transition_to(OrchestratorStates.COMPLETED)
            self.session_manager.complete_session(session_id, {'outputs': outputs})
            
            execution_time = (datetime.now() - self._start_time).total_seconds()
            
            logger.info(f"{self.orchestrator_name} completed successfully in {execution_time:.2f}s")
            
            return OrchestratorResult(
                success=True,
                session_id=session_id,
                orchestrator_name=self.orchestrator_name,
                final_state=self.state_machine.current_state,
                execution_time_seconds=execution_time,
                outputs=outputs,
                errors=[]
            )
            
        except Exception as e:
            logger.exception(f"{self.orchestrator_name} execution failed")
            self.state_machine.transition_to(OrchestratorStates.FAILED)
            self.session_manager.fail_session(session_id, {'exception': str(e)})
            
            return self._create_error_result(
                session_id=session_id,
                errors=[str(e)]
            )
    
    @abstractmethod
    def validate_dor(self, context: WorkflowContext) -> ValidationResult:
        """
        Validate Definition of Ready (prerequisites).
        
        Args:
            context: Workflow context
            
        Returns:
            ValidationResult
        """
        pass
    
    @abstractmethod
    def validate_dod(self, context: WorkflowContext) -> ValidationResult:
        """
        Validate Definition of Done (completion criteria).
        
        Args:
            context: Workflow context
            
        Returns:
            ValidationResult
        """
        pass
    
    @abstractmethod
    def execute_workflow(self, context: WorkflowContext) -> Dict[str, Any]:
        """
        Execute orchestrator-specific workflow.
        
        Args:
            context: Workflow context
            
        Returns:
            Dictionary of output values
        """
        pass
    
    def _create_error_result(
        self,
        session_id: str,
        errors: list[str]
    ) -> OrchestratorResult:
        """Create error result."""
        execution_time = 0.0
        if self._start_time:
            execution_time = (datetime.now() - self._start_time).total_seconds()
        
        return OrchestratorResult(
            success=False,
            session_id=session_id,
            orchestrator_name=self.orchestrator_name,
            final_state=self.state_machine.current_state,
            execution_time_seconds=execution_time,
            outputs={},
            errors=errors
        )
