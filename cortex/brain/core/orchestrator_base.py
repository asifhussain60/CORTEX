"""
Base Orchestrator Abstract Class

Defines the standard interface for all orchestrators in CORTEX.
All domain-specific orchestrators must inherit from OrchestratorBase.

This enables:
- Standardized lifecycle management (initialize, validate, execute, complete)
- Governance context injection
- Tier-based access control
- Audit trail integration
- MCP tool exposure
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set
from datetime import datetime
import uuid


class OrchestrationStatus(Enum):
    """Orchestrator execution status"""
    INITIALIZED = "initialized"
    VALIDATING = "validating"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    HALTED = "halted"


@dataclass
class OrchestrationContext:
    """Context passed to orchestrator during execution"""
    
    orchestrator_id: str
    orchestrator_name: str
    execution_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    # Governance context
    tier_access: Set[int] = field(default_factory=lambda: {0, 1, 2, 3})
    required_rules: List[str] = field(default_factory=list)
    
    # Execution parameters
    parameters: Dict[str, Any] = field(default_factory=dict)
    environment: str = "development"  # development | staging | production
    
    # Audit trail
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    audit_enabled: bool = True
    
    # Status tracking
    status: OrchestrationStatus = OrchestrationStatus.INITIALIZED
    progress_percent: int = 0
    
    # Error handling
    error_message: Optional[str] = None
    error_code: Optional[str] = None
    
    def __post_init__(self):
        """Validate context on creation"""
        if not self.orchestrator_id or not self.orchestrator_name:
            raise ValueError("orchestrator_id and orchestrator_name are required")
        if not self.execution_id:
            self.execution_id = str(uuid.uuid4())
        if self.start_time is None:
            self.start_time = datetime.utcnow()


@dataclass
class OrchestrationResult:
    """Result returned by orchestrator"""
    
    orchestrator_id: str
    execution_id: str
    status: OrchestrationStatus
    output: Any = None
    
    # Success metrics
    success: bool = False
    message: str = ""
    
    # Error handling
    error_code: Optional[str] = None
    
    # Governance compliance
    rules_evaluated: int = 0
    rules_passed: int = 0
    violations: List[str] = field(default_factory=list)
    
    # Audit trail
    audit_entries_count: int = 0
    hash_chain_valid: bool = False
    
    # Timing
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_seconds: float = 0.0
    
    # Evidence
    evidence_bundle_id: Optional[str] = None


class OrchestratorBase(ABC):
    """
    Abstract base class for all CORTEX orchestrators.
    
    Subclasses must implement:
    - execute(): The main orchestration logic
    - validate_context(): Pre-execution validation
    
    Lifecycle:
    1. __init__() - Orchestrator instantiated with context
    2. validate_context() - Hook: Validate context before execution
    3. execute() - Abstract: Main execution logic
    4. on_start() - Hook: Called at execution start (after validation)
    5. on_complete() - Hook: Called after execution completes (before result)
    6. Result returned with metadata
    """
    
    def __init__(self, context: OrchestrationContext):
        """
        Initialize orchestrator with execution context.
        
        Args:
            context: OrchestrationContext with parameters and governance info
            
        Raises:
            ValueError: If context is invalid
            TypeError: If context is not OrchestrationContext
        """
        if not isinstance(context, OrchestrationContext):
            raise TypeError(f"context must be OrchestrationContext, got {type(context)}")
        
        self.context = context
        self.result: Optional[OrchestrationResult] = None
        self._execution_log: List[str] = []
        
    # =========================================================================
    # Public Interface
    # =========================================================================
    
    def run(self) -> OrchestrationResult:
        """
        Execute the orchestrator with full lifecycle management.
        
        Returns:
            OrchestrationResult with execution outcome
        """
        try:
            # Phase 1: Validation
            self.context.status = OrchestrationStatus.VALIDATING
            self._log("Starting validation phase")
            
            validation_errors = self.validate_context()
            if validation_errors:
                return self._create_failure_result(
                    status=OrchestrationStatus.VALIDATING,
                    message=f"Validation failed: {'; '.join(validation_errors)}",
                    error_code="VALIDATION_FAILED"
                )
            
            self._log("Validation passed")
            
            # Phase 2: Pre-execution hook
            self._log("Calling on_start() hook")
            self.on_start()
            
            # Phase 3: Execution
            self.context.status = OrchestrationStatus.EXECUTING
            self._log("Starting execution phase")
            
            output = self.execute()
            
            self._log("Execution completed successfully")
            
            # Phase 4: Post-execution hook
            self.context.status = OrchestrationStatus.COMPLETED
            self._log("Calling on_complete() hook")
            self.on_complete()
            
            # Phase 5: Result creation
            self.context.end_time = datetime.utcnow()
            self.result = self._create_success_result(output)
            
            return self.result
            
        except Exception as e:
            self._log(f"Execution failed with error: {str(e)}")
            self.context.status = OrchestrationStatus.FAILED
            self.context.error_message = str(e)
            self.context.error_code = type(e).__name__
            
            return self._create_failure_result(
                status=OrchestrationStatus.FAILED,
                message=str(e),
                error_code=type(e).__name__
            )
    
    # =========================================================================
    # Abstract Methods (Must be implemented by subclasses)
    # =========================================================================
    
    @abstractmethod
    def execute(self) -> Any:
        """
        Main execution logic for this orchestrator.
        
        Subclasses implement domain-specific logic here.
        
        Returns:
            Orchestrator-specific output
            
        Raises:
            Any exception will be caught and converted to failure result
        """
        pass
    
    def validate_context(self) -> List[str]:
        """
        Validate context before execution.
        
        Hook method that subclasses can override to perform validation.
        Default implementation performs minimal checks.
        
        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        
        # Minimal validation
        if not self.context.orchestrator_id:
            errors.append("orchestrator_id is required")
        if not self.context.parameters:
            self._log("Warning: parameters is empty")
        
        return errors
    
    # =========================================================================
    # Lifecycle Hooks (Can be overridden by subclasses)
    # =========================================================================
    
    def on_start(self) -> None:
        """
        Hook called immediately before execution.
        
        Subclasses can override to perform setup.
        Default implementation does nothing.
        """
        pass
    
    def on_complete(self) -> None:
        """
        Hook called immediately after execution completes.
        
        Subclasses can override to perform cleanup.
        Default implementation does nothing.
        """
        pass
    
    # =========================================================================
    # Governance & Access Control
    # =========================================================================
    
    def get_tier_access(self) -> Set[int]:
        """
        Get the tiers this orchestrator can access.
        
        Returns:
            Set of tier numbers (0, 1, 2, 3)
        """
        return self.context.tier_access
    
    def can_access_tier(self, tier: int) -> bool:
        """
        Check if orchestrator can access a specific tier.
        
        Args:
            tier: Tier number (0-3)
            
        Returns:
            True if tier access is allowed
        """
        return tier in self.context.tier_access
    
    def get_required_rules(self) -> List[str]:
        """
        Get the governance rules required by this orchestrator.
        
        Subclasses should override to declare dependencies.
        
        Returns:
            List of SKULL rule IDs
        """
        return self.context.required_rules
    
    # =========================================================================
    # Logging & Audit
    # =========================================================================
    
    def _log(self, message: str) -> None:
        """
        Log a message to execution log.
        
        Args:
            message: Message to log
        """
        timestamp = datetime.utcnow().isoformat()
        entry = f"[{timestamp}] {message}"
        self._execution_log.append(entry)
    
    def get_execution_log(self) -> List[str]:
        """
        Get the execution log.
        
        Returns:
            List of log entries
        """
        return self._execution_log.copy()
    
    # =========================================================================
    # Result Creation Helpers
    # =========================================================================
    
    def _create_success_result(self, output: Any) -> OrchestrationResult:
        """Create a success result."""
        return OrchestrationResult(
            orchestrator_id=self.context.orchestrator_id,
            execution_id=self.context.execution_id,
            status=OrchestrationStatus.COMPLETED,
            output=output,
            success=True,
            message="Execution completed successfully",
            start_time=self.context.start_time,
            end_time=self.context.end_time,
            duration_seconds=(
                (self.context.end_time - self.context.start_time).total_seconds()
                if self.context.end_time and self.context.start_time
                else 0.0
            ),
        )
    
    def _create_failure_result(
        self,
        status: OrchestrationStatus,
        message: str,
        error_code: Optional[str] = None
    ) -> OrchestrationResult:
        """Create a failure result."""
        return OrchestrationResult(
            orchestrator_id=self.context.orchestrator_id,
            execution_id=self.context.execution_id,
            status=status,
            success=False,
            message=message,
            error_code=error_code,
            start_time=self.context.start_time,
            end_time=datetime.utcnow(),
            duration_seconds=(
                (datetime.utcnow() - self.context.start_time).total_seconds()
                if self.context.start_time
                else 0.0
            ),
        )
    
    # =========================================================================
    # Metadata
    # =========================================================================
    
    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"id={self.context.orchestrator_id}, "
            f"execution={self.context.execution_id}, "
            f"status={self.context.status.value})"
        )
