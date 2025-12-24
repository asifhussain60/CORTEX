"""
Base Orchestrator Class for CORTEX 4.0

All orchestrators inherit from BaseOrchestrator which provides:
- Standardized initialization with config, logger, brain, templates
- Workspace detection and context (Phase 11)
- Abstract execute() method for orchestrator logic
- Input validation framework
- Error handling integration
- Phase management integration
- Metrics collection

Design Principles:
1. All orchestrators follow the same lifecycle
2. Configuration is injected (DI-ready)
3. Brain tiers are accessed through unified interface
4. Templates are managed centrally
5. Errors are handled consistently
6. Workspace-aware file operations (Phase 11)
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional
import uuid

# Import adaptive execution components
from src.operations.modules.orchestration.adaptive_execution import (
    ExecutionMode,
    AdaptiveExecutionConfig,
    SafetyGuardrail
)

# Phase 11: Workspace detection
from src.core.workspace_detector import detect_active_workspace, WorkspaceInfo


class OrchestratorStatus(Enum):
    """Orchestrator execution status."""
    NOT_STARTED = "not_started"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ValidationResult:
    """Result of input validation."""
    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    @property
    def has_errors(self) -> bool:
        """Check if validation has errors."""
        return len(self.errors) > 0
    
    @property
    def has_warnings(self) -> bool:
        """Check if validation has warnings."""
        return len(self.warnings) > 0


@dataclass
class OrchestratorResult:
    """Result of orchestrator execution."""
    status: OrchestratorStatus
    success: bool
    message: str
    data: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    execution_time_seconds: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    
    @property
    def is_complete(self) -> bool:
        """Check if orchestrator completed successfully."""
        return self.success and self.status == OrchestratorStatus.COMPLETED


@dataclass
class ErrorResult:
    """Result of error handling."""
    handled: bool
    error_type: str
    error_message: str
    recovery_attempted: bool
    recovery_successful: bool
    should_retry: bool = False
    retry_delay_seconds: float = 0.0


class BaseOrchestrator(ABC):
    """
    Base class for all CORTEX 4.0 orchestrators.
    
    Provides standardized initialization, execution lifecycle, error handling,
    and integration with brain tiers, templates, and configuration.
    
    Lifecycle:
        1. __init__() - Initialize with config
        2. validate_input() - Validate parameters
        3. execute() - Main orchestrator logic (abstract - implement in subclass)
        4. handle_error() - Handle any errors (optional override)
    
    Workspace Awareness (Phase 11):
        - self.workspace_info: Current active workspace information
        - self.target_directory: Where to write files (active workspace path)
        - self.workspace_id: Current workspace UUID
        - self.workspace_name: Human-readable workspace name
    
    Usage:
        class MyOrchestrator(BaseOrchestrator):
            def execute(self) -> OrchestratorResult:
                # Files will be written to self.target_directory
                output_file = self.target_directory / "output.txt"
                output_file.write_text("Hello from workspace!")
                
                return OrchestratorResult(
                    status=OrchestratorStatus.COMPLETED,
                    success=True,
                    message="Operation complete"
                )
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize orchestrator with configuration.
        
        Args:
            config: Orchestrator configuration dictionary
                   Must contain at least: name, version
                   Optional: logger_name, log_level, brain_config, template_config,
                            execution_mode, adaptive_config, workspace_id (override)
        """
        self.config = config
        self.name = config.get("name", self.__class__.__name__)
        self.version = config.get("version", "4.0.0")
        
        # Setup logging
        logger_name = config.get("logger_name", f"cortex.orchestrators.{self.name}")
        self.logger = logging.getLogger(logger_name)
        log_level = config.get("log_level", "INFO")
        self.logger.setLevel(getattr(logging, log_level))
        
        # Phase 11: Detect active workspace
        try:
            self.workspace_info = detect_active_workspace()
            self.target_directory = self.workspace_info.path
            self.workspace_id = self.workspace_info.workspace_id
            self.workspace_name = self.workspace_info.name
            self.logger.info(
                f"[workspace:{self.workspace_name}] Orchestrator initialized - "
                f"target directory: {self.target_directory}"
            )
        except Exception as e:
            self.logger.warning(f"Workspace detection failed: {e}")
            # Fallback to workspace_root from config
            self.target_directory = Path(config.get("workspace_root", Path.cwd()))
            self.workspace_info = None
            self.workspace_id = "unknown"
            self.workspace_name = "unknown"
        
        # Initialize brain interface
        workspace_root = Path(config.get("workspace_root", Path.cwd()))
        brain_config = config.get("brain_config", {})
        
        try:
            from src.brain import BrainInterface
            self.brain = BrainInterface(workspace_root, brain_config)
            self.logger.debug("Brain interface initialized")
        except Exception as e:
            self.logger.warning(f"Failed to initialize brain interface: {e}")
            self.brain = None
        
        # Initialize template manager (lazy-loaded in Phase 1)
        # Will be replaced with: self.template_manager = TemplateManager(config.get("template_config", {}))
        self.template_manager = None  # Placeholder for Phase 1
        
        # Adaptive execution configuration
        self.execution_mode = config.get("execution_mode", ExecutionMode.SUPERVISED)
        adaptive_config_dict = config.get("adaptive_config", {})
        adaptive_config = AdaptiveExecutionConfig(**adaptive_config_dict) if adaptive_config_dict else AdaptiveExecutionConfig()
        self.safety_guardrail = SafetyGuardrail(adaptive_config)
        
        # Auto-rollback enabled for AUTONOMOUS mode
        self.auto_rollback_enabled = (self.execution_mode == ExecutionMode.AUTONOMOUS)
        
        # Checkpoint management
        self._checkpoints: List[Dict[str, Any]] = []
        self.current_phase = None
        
        # Execution state
        self.status = OrchestratorStatus.NOT_STARTED
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.errors: List[str] = []
        self.warnings: List[str] = []
        
        self.logger.info(f"[workspace:{self.workspace_name}] Initialized {self.name} v{self.version}")
        self.logger.debug(f"Execution mode: {self.execution_mode.value if isinstance(self.execution_mode, ExecutionMode) else self.execution_mode}")
        self.logger.debug(f"Auto-rollback: {'enabled' if self.auto_rollback_enabled else 'disabled'}")
    
    @abstractmethod
    def execute(self) -> OrchestratorResult:
        """
        Execute orchestrator logic.
        
        MUST be implemented by all subclasses.
        
        Returns:
            OrchestratorResult with status, success, message, and data
        
        Raises:
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement execute() method"
        )
    
    def validate_input(self, params: Dict[str, Any]) -> ValidationResult:
        """
        Validate orchestrator input parameters.
        
        Override this method to add custom validation logic.
        Base implementation checks for required fields in config.
        
        Args:
            params: Input parameters to validate
        
        Returns:
            ValidationResult with valid flag and any errors/warnings
        """
        errors = []
        warnings = []
        
        # Check required config fields
        required_fields = ["name", "version"]
        for field in required_fields:
            if field not in self.config:
                errors.append(f"Missing required config field: {field}")
        
        # Check params if any expected
        expected_params = self.config.get("expected_params", [])
        for param in expected_params:
            if param not in params:
                errors.append(f"Missing required parameter: {param}")
        
        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    def handle_error(self, error: Exception) -> ErrorResult:
        """
        Handle orchestrator errors.
        
        Override this method to add custom error handling logic.
        Base implementation logs error and returns ErrorResult.
        
        Args:
            error: Exception that occurred
        
        Returns:
            ErrorResult with handling details
        """
        error_type = error.__class__.__name__
        error_message = str(error)
        
        self.logger.error(f"{error_type}: {error_message}", exc_info=True)
        self.errors.append(error_message)
        
        return ErrorResult(
            handled=True,
            error_type=error_type,
            error_message=error_message,
            recovery_attempted=False,
            recovery_successful=False,
            should_retry=False
        )
    
    def create_checkpoint(self, phase: str, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a checkpoint of current execution state.
        
        Args:
            phase: Current phase name
            state: Current state to save
        
        Returns:
            Checkpoint dictionary with id, phase, state, and timestamp
        """
        checkpoint = {
            "checkpoint_id": str(uuid.uuid4()),
            "phase": phase,
            "state": state.copy(),
            "timestamp": datetime.now().isoformat()
        }
        self._checkpoints.append(checkpoint)
        self.logger.debug(f"Checkpoint created for phase '{phase}': {checkpoint['checkpoint_id']}")
        return checkpoint
    
    def restore_checkpoint(self, checkpoint_id: str) -> bool:
        """
        Restore orchestrator state from a checkpoint.
        
        Args:
            checkpoint_id: ID of checkpoint to restore
        
        Returns:
            True if checkpoint restored successfully, False otherwise
        """
        for checkpoint in self._checkpoints:
            if checkpoint["checkpoint_id"] == checkpoint_id:
                self.current_phase = checkpoint["phase"]
                self.logger.info(f"Restored checkpoint {checkpoint_id} for phase '{checkpoint['phase']}'")
                return True
        
        self.logger.warning(f"Checkpoint {checkpoint_id} not found")
        return False
    
    def list_checkpoints(self) -> List[Dict[str, Any]]:
        """
        Get list of all saved checkpoints.
        
        Returns:
            List of checkpoint dictionaries
        """
        return self._checkpoints.copy()
    
    def validate_action(self, action: Dict[str, Any]) -> ValidationResult:
        """
        Validate an action using safety guardrails.
        
        Args:
            action: Action dictionary to validate
        
        Returns:
            ValidationResult with validation outcome
        """
        validation = self.safety_guardrail.validate_action(action)
        
        if not validation.get("allowed", True):
            return ValidationResult(
                valid=False,
                errors=[f"Unsafe action: {validation.get('reason', 'Unknown reason')}"]
            )
        
        return ValidationResult(valid=True)
    
    def run(self) -> OrchestratorResult:
        """
        Execute orchestrator with full lifecycle (validation, execution, error handling).
        
        This is the main entry point. It wraps execute() with:
        - Status updates
        - Timing
        - Error handling
        - Logging
        - Auto-rollback (if enabled)
        
        Returns:
            OrchestratorResult with execution details
        """
        self.logger.info(f"🎭 Orchestrator engaged: {self.name} [workspace:{self.workspace_name}]")
        self.status = OrchestratorStatus.RUNNING
        self.start_time = datetime.now()
        
        try:
            # Execute orchestrator logic
            result = self.execute()
            
            # Update status
            self.status = result.status
            self.end_time = datetime.now()
            result.execution_time_seconds = (self.end_time - self.start_time).total_seconds()
            
            # Log completion
            if result.success:
                self.logger.info(f"🎭 Orchestrator completing: ✅ {self.name} - {result.message}")
            else:
                self.logger.warning(f"🎭 Orchestrator completing: ⚠️ {self.name} - {result.message}")
            
            return result
            
        except Exception as e:
            # Handle error
            error_result = self.handle_error(e)
            self.status = OrchestratorStatus.FAILED
            self.end_time = datetime.now()
            
            # Auto-rollback if enabled
            rolled_back = False
            checkpoint_restored = None
            if self.auto_rollback_enabled and len(self._checkpoints) > 0:
                last_checkpoint = self._checkpoints[-1]
                if self.restore_checkpoint(last_checkpoint["checkpoint_id"]):
                    rolled_back = True
                    checkpoint_restored = last_checkpoint["checkpoint_id"]
                    self.logger.info(f"Auto-rollback triggered: Restored checkpoint {checkpoint_restored}")
            
            return OrchestratorResult(
                status=OrchestratorStatus.FAILED,
                success=False,
                message=f"Orchestrator failed: {error_result.error_message}",
                errors=[error_result.error_message],
                data={
                    "rolled_back": rolled_back,
                    "checkpoint_restored": checkpoint_restored
                },
                execution_time_seconds=(self.end_time - self.start_time).total_seconds()
            )
    
    def get_execution_time(self) -> float:
        """
        Get orchestrator execution time in seconds.
        
        Returns:
            Execution time in seconds, or 0 if not started/completed
        """
        if self.start_time is None:
            return 0.0
        
        end_time = self.end_time or datetime.now()
        return (end_time - self.start_time).total_seconds()
    
    def __repr__(self) -> str:
        """String representation of orchestrator."""
        return f"{self.__class__.__name__}(name='{self.name}', version='{self.version}', status={self.status.value})"
