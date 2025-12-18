"""
Base Orchestrator Class for CORTEX 4.0

All orchestrators inherit from BaseOrchestrator which provides:
- Standardized initialization with config, logger, brain, templates
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
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


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
    
    Usage:
        class MyOrchestrator(BaseOrchestrator):
            def execute(self) -> OrchestratorResult:
                # Your orchestrator logic here
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
                   Optional: logger_name, log_level, brain_config, template_config
        """
        self.config = config
        self.name = config.get("name", self.__class__.__name__)
        self.version = config.get("version", "4.0.0")
        
        # Setup logging
        logger_name = config.get("logger_name", f"cortex.orchestrators.{self.name}")
        self.logger = logging.getLogger(logger_name)
        log_level = config.get("log_level", "INFO")
        self.logger.setLevel(getattr(logging, log_level))
        
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
        
        # Execution state
        self.status = OrchestratorStatus.NOT_STARTED
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.errors: List[str] = []
        self.warnings: List[str] = []
        
        self.logger.info(f"Initialized {self.name} v{self.version}")
    
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
    
    def run(self) -> OrchestratorResult:
        """
        Execute orchestrator with full lifecycle (validation, execution, error handling).
        
        This is the main entry point. It wraps execute() with:
        - Status updates
        - Timing
        - Error handling
        - Logging
        
        Returns:
            OrchestratorResult with execution details
        """
        self.logger.info(f"🎭 Orchestrator engaged: {self.name}")
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
            
            return OrchestratorResult(
                status=OrchestratorStatus.FAILED,
                success=False,
                message=f"Orchestrator failed: {error_result.error_message}",
                errors=[error_result.error_message],
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
