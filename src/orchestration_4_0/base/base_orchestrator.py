"""
Base Orchestrator for CORTEX 4.0

Provides template method pattern for all orchestrators with:
- Phase management
- Error handling
- Lifecycle hooks
- Dependency injection integration
- Progress tracking
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

from .phase_manager import PhaseManager, PhaseStatus
from .error_handler import ErrorHandler, ErrorSeverity, RecoveryStrategy, OrchestratorError


class BaseOrchestrator(ABC):
    """
    Abstract base class for all CORTEX 4.0 orchestrators.
    
    Template Method Pattern:
    1. _setup() - Initialize orchestrator-specific resources
    2. _register_phases() - Define phases for this orchestrator
    3. _execute_phase(phase_name) - Execute a single phase
    4. _teardown() - Cleanup resources
    
    Subclasses must implement these methods.
    """
    
    def __init__(
        self,
        name: str,
        logger: Optional[logging.Logger] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize base orchestrator.
        
        Args:
            name: Orchestrator name (e.g., "execution", "planning")
            logger: Optional logger instance (created if not provided)
            config: Optional configuration dictionary
        """
        self.name = name
        self.logger = logger or logging.getLogger(f"cortex.orchestration.{name}")
        self.config = config or {}
        
        # Core components
        self.phase_manager = PhaseManager(orchestrator_name=name)
        self.error_handler = ErrorHandler(
            orchestrator_name=name,
            max_retries=self.config.get("max_retries", 3)
        )
        
        # State tracking
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.is_running: bool = False
        self.is_complete: bool = False
        self.result: Optional[Dict[str, Any]] = None
        
        self.logger.info(f"🎭 Orchestrator initialized: {name}")
    
    def execute(self, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Main execution entry point (Template Method).
        
        Orchestrates the full workflow:
        1. Setup
        2. Register phases
        3. Execute phases in order
        4. Handle errors
        5. Teardown
        
        Args:
            context: Execution context data
            
        Returns:
            Execution result dictionary
            
        Raises:
            RuntimeError: If orchestrator already running or critical error occurs
        """
        if self.is_running:
            raise RuntimeError(f"Orchestrator {self.name} already running")
        
        self.is_running = True
        self.started_at = datetime.now()
        self.logger.info(f"🎭 Orchestrator engaged: {self.name}")
        
        try:
            # Step 1: Setup
            self.logger.debug("Running setup...")
            setup_result = self._setup(context or {})
            
            # Step 2: Register phases
            self.logger.debug("Registering phases...")
            self._register_phases()
            
            # Step 3: Execute phases
            self.logger.debug(f"Executing {len(self.phase_manager.phases)} phases...")
            for phase in self.phase_manager.phases:
                self._execute_phase_with_error_handling(phase.name, context or {})
                
                # Stop if critical error occurred
                if self.error_handler.has_critical_errors():
                    self.logger.error("❌ Critical error occurred, stopping execution")
                    break
            
            # Step 4: Collect results
            self.result = self._collect_results()
            
            # Step 5: Determine completion status
            self.is_complete = self._is_workflow_complete()
            
            if self.is_complete:
                self.logger.info(f"🎭 Orchestrator completing: ✅ ALL WORK COMPLETE")
            
            return self.result
            
        except Exception as e:
            self.logger.error(f"❌ Orchestrator failed: {e}")
            self.error_handler.handle_error(
                phase="orchestrator",
                exception=e,
                severity=ErrorSeverity.CRITICAL
            )
            raise
        
        finally:
            # Always run teardown
            try:
                self.logger.debug("Running teardown...")
                self._teardown(context or {})
            except Exception as e:
                self.logger.error(f"⚠️  Teardown failed: {e}")
            
            self.is_running = False
            self.completed_at = datetime.now()
            
            # Log summary
            duration = (self.completed_at - self.started_at).total_seconds()
            progress = self.phase_manager.get_progress()
            self.logger.info(
                f"🎭 Orchestrator finished: {self.name} "
                f"({duration:.2f}s, {progress['completed']}/{progress['total_phases']} phases complete)"
            )
    
    def _execute_phase_with_error_handling(
        self,
        phase_name: str,
        context: Dict[str, Any]
    ) -> None:
        """
        Execute a phase with error handling and retry logic.
        
        Args:
            phase_name: Name of phase to execute
            context: Execution context
        """
        while True:
            try:
                # Start phase
                self.phase_manager.start_phase(phase_name)
                
                # Execute phase-specific logic
                result = self._execute_phase(phase_name, context)
                
                # Complete phase
                self.phase_manager.complete_phase(phase_name, result)
                
                # Reset retry counter on success
                self.error_handler.reset_retries(phase_name)
                break
                
            except Exception as e:
                # Handle error
                error = self.error_handler.handle_error(
                    phase=phase_name,
                    exception=e,
                    context={"attempt": self.error_handler.retry_counts.get(phase_name, 0)}
                )
                
                # Fail phase
                self.phase_manager.fail_phase(phase_name, str(e))
                
                # Determine action based on recovery strategy
                if error.recovery_strategy == RecoveryStrategy.RETRY and self.error_handler.can_retry(phase_name):
                    self.error_handler.record_retry(phase_name)
                    self.logger.info(f"🔄 Retrying phase: {phase_name}")
                    self.phase_manager.phases[self.phase_manager.phases.index(
                        self.phase_manager._get_phase(phase_name)
                    )].status = PhaseStatus.PENDING
                    continue
                
                elif error.recovery_strategy == RecoveryStrategy.SKIP:
                    self.phase_manager.skip_phase(phase_name, f"Skipped due to error: {str(e)}")
                    self.logger.warning(f"⏭️  Skipping phase: {phase_name}")
                    break
                
                elif error.recovery_strategy == RecoveryStrategy.FAIL_FAST:
                    self.logger.error(f"❌ Failing fast due to error in phase: {phase_name}")
                    raise
                
                else:
                    # For other strategies, just log and continue
                    self.logger.warning(f"⚠️  Continuing after error in phase: {phase_name}")
                    break
    
    def _collect_results(self) -> Dict[str, Any]:
        """
        Collect results from all phases.
        
        Returns:
            Dictionary with orchestrator results
        """
        phase_results = {}
        for phase in self.phase_manager.phases:
            if phase.result:
                phase_results[phase.name] = phase.result
        
        progress = self.phase_manager.get_progress()
        error_summary = self.error_handler.get_error_summary()
        
        return {
            "orchestrator": self.name,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": datetime.now().isoformat(),
            "duration_seconds": (datetime.now() - self.started_at).total_seconds() if self.started_at else 0,
            "progress": progress,
            "errors": error_summary,
            "phase_results": phase_results,
            "is_complete": self._is_workflow_complete()
        }
    
    def _is_workflow_complete(self) -> bool:
        """
        Determine if workflow is fully complete.
        
        Returns:
            True if all required phases completed successfully
        """
        # Check if any critical errors
        if self.error_handler.has_critical_errors():
            return False
        
        # Check if all required phases completed
        for phase in self.phase_manager.phases:
            if phase.required and phase.status != PhaseStatus.COMPLETED:
                return False
        
        return True
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current orchestrator status.
        
        Returns:
            Dictionary with status information
        """
        return {
            "name": self.name,
            "is_running": self.is_running,
            "is_complete": self.is_complete,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "progress": self.phase_manager.get_progress(),
            "errors": self.error_handler.get_error_summary()
        }
    
    # Public wrapper methods for testing and external access
    
    def setup(self, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Public wrapper for setup.
        
        Args:
            context: Optional execution context
            
        Returns:
            Setup result
        """
        return self._setup(context or {})
    
    def teardown(self, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Public wrapper for teardown.
        
        Args:
            context: Optional teardown context
            
        Returns:
            Teardown result
        """
        return self._teardown(context or {})
    
    def execute_phase(self, phase_name: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Public wrapper for phase execution.
        
        Args:
            phase_name: Name of phase to execute
            context: Optional execution context
            
        Returns:
            Phase execution result
        """
        return self._execute_phase(phase_name, context or {})
    
    # Abstract methods that subclasses must implement
    
    @abstractmethod
    def _setup(self, context: Dict[str, Any]) -> None:
        """
        Setup orchestrator-specific resources.
        
        Called before phases are registered.
        
        Args:
            context: Execution context
        """
        pass
    
    @abstractmethod
    def _register_phases(self) -> None:
        """
        Register all phases for this orchestrator.
        
        Use self.phase_manager.register_phase() to add phases.
        """
        pass
    
    @abstractmethod
    def _execute_phase(self, phase_name: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Execute a specific phase.
        
        Args:
            phase_name: Name of phase to execute
            context: Execution context
            
        Returns:
            Optional phase result data
        """
        pass
    
    @abstractmethod
    def _teardown(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Cleanup orchestrator-specific resources.
        
        Called after all phases complete (even if errors occurred).
        
        Args:
            context: Teardown context
            
        Returns:
            Teardown result
        """
        pass
