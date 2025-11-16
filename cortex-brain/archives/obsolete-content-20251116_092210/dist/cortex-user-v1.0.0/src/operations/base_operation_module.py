"""
Base Operation Module - Universal Abstract Interface

This module provides the abstract base class that ALL operation modules inherit from,
whether for setup, story refresh, documentation updates, cleanup, or any other CORTEX command.

Design Principles (SOLID):
    - Single Responsibility: Each module does ONE thing
    - Open/Closed: Add new modules without modifying orchestrator
    - Liskov Substitution: All modules are interchangeable
    - Interface Segregation: Minimal required interface
    - Dependency Inversion: Depend on abstractions, not concrete implementations

Author: Asif Hussain
Version: 2.0 (Universal Operations Architecture)
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime


class OperationPhase(Enum):
    """
    Universal phases for operation execution.
    
    All CORTEX operations follow these phases:
        PRE_VALIDATION: Validate prerequisites before starting
        PREPARATION: Prepare resources, load data, setup context
        ENVIRONMENT: Configure environment-specific settings
        DEPENDENCIES: Install/verify dependencies
        PROCESSING: Main processing logic
        FEATURES: Enable/configure features
        VALIDATION: Verify results
        FINALIZATION: Cleanup, reporting, completion
    """
    PRE_VALIDATION = "pre_validation"
    PREPARATION = "preparation"
    ENVIRONMENT = "environment"
    DEPENDENCIES = "dependencies"
    PROCESSING = "processing"
    FEATURES = "features"
    VALIDATION = "validation"
    FINALIZATION = "finalization"
    
    @property
    def order(self) -> int:
        """Get execution order for phase."""
        order_map = {
            OperationPhase.PRE_VALIDATION: 0,
            OperationPhase.PREPARATION: 1,
            OperationPhase.ENVIRONMENT: 2,
            OperationPhase.DEPENDENCIES: 3,
            OperationPhase.PROCESSING: 4,
            OperationPhase.FEATURES: 5,
            OperationPhase.VALIDATION: 6,
            OperationPhase.FINALIZATION: 7,
        }
        return order_map[self]


class ExecutionMode(Enum):
    """Execution mode for operations."""
    LIVE = "live"  # Execute actual changes
    DRY_RUN = "dry_run"  # Preview only, no changes


class OperationStatus(Enum):
    """Status of operation module execution."""
    NOT_STARTED = "not_started"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    WARNING = "warning"  # Success with warnings


@dataclass
class OperationResult:
    """
    Result of operation module execution.
    
    Universal across ALL operations (setup, cleanup, story refresh, etc.)
    
    Attributes:
        success: Whether module executed successfully
        status: Current module status
        message: Human-readable result message
        data: Operation-specific data (file paths, counts, metrics, etc.)
        errors: List of error messages if failed
        warnings: List of warning messages
        duration_seconds: Execution time
        timestamp: When module completed
        execution_mode: Whether this was a dry-run or live execution
        formatted_header: Formatted header for Copilot Chat display
        formatted_footer: Formatted footer for Copilot Chat display
    """
    success: bool
    status: OperationStatus
    message: str
    data: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    duration_seconds: float = 0.0
    timestamp: Optional[datetime] = None
    execution_mode: ExecutionMode = ExecutionMode.LIVE
    formatted_header: Optional[str] = None
    formatted_footer: Optional[str] = None
    
    def __post_init__(self):
        """Set timestamp if not provided."""
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class OperationModuleMetadata:
    """
    Metadata describing an operation module.
    
    Universal metadata applicable to ALL operations.
    
    Attributes:
        module_id: Unique identifier (e.g., 'platform_detection', 'refresh_story')
        name: Human-readable name
        description: What the module does
        phase: Which phase this module runs in
        priority: Execution order within phase (lower = earlier)
        dependencies: Module IDs that must complete before this module
        optional: Whether module failure should stop operation
        version: Module version for compatibility tracking
        author: Module author for copyright attribution
        tags: Categorization tags (e.g., ['environment', 'required'])
    """
    module_id: str
    name: str
    description: str
    phase: OperationPhase
    priority: int = 50
    dependencies: List[str] = field(default_factory=list)
    optional: bool = False
    version: str = "1.0"
    author: str = "Asif Hussain"  # Default copyright holder
    tags: List[str] = field(default_factory=list)


class BaseOperationModule(ABC):
    """
    Abstract base class for ALL CORTEX operation modules.
    
    This interface is used by:
        - Setup modules (platform detection, vision API, etc.)
        - Story refresh modules (load story, transform voice, etc.)
        - Cleanup modules (scan files, remove old logs, etc.)
        - Documentation modules (build docs, validate links, etc.)
        - And any future operations
    
    Key Methods:
        get_metadata(): Returns module metadata
        validate_prerequisites(): Checks if module can run
        execute(): Performs module's main work
        rollback(): Undoes changes if needed
        should_run(): Conditional execution check
    
    Example Usage:
        class MyCustomModule(BaseOperationModule):
            def get_metadata(self):
                return OperationModuleMetadata(
                    module_id="my_module",
                    name="My Custom Module",
                    description="Does something useful",
                    phase=OperationPhase.PROCESSING
                )
            
            def execute(self, context):
                # Do work
                return OperationResult(
                    success=True,
                    status=OperationStatus.SUCCESS,
                    message="Work completed"
                )
    """
    
    def __init__(self):
        """Initialize base module with logger."""
        self._metadata = None
        self._last_result = None
        self._execution_mode = ExecutionMode.LIVE
        # Create logger for this specific module class
        self.logger = logging.getLogger(f"{self.__class__.__module__}.{self.__class__.__name__}")
    
    @property
    def metadata(self) -> OperationModuleMetadata:
        """Get cached metadata."""
        if self._metadata is None:
            self._metadata = self.get_metadata()
        return self._metadata
    
    @property
    def execution_mode(self) -> ExecutionMode:
        """Get current execution mode."""
        return self._execution_mode
    
    @execution_mode.setter
    def execution_mode(self, mode: ExecutionMode) -> None:
        """Set execution mode."""
        self._execution_mode = mode
    
    @property
    def is_dry_run(self) -> bool:
        """Check if module is in dry-run mode."""
        return self._execution_mode == ExecutionMode.DRY_RUN
    
    @abstractmethod
    def get_metadata(self) -> OperationModuleMetadata:
        """
        Return metadata describing this module.
        
        Returns:
            OperationModuleMetadata with module information
        """
        pass
    
    def validate_prerequisites(self, context: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Validate that prerequisites for this module are met.
        
        Override to add custom prerequisite checks (e.g., required files exist,
        environment variables set, previous modules completed).
        
        Args:
            context: Shared context dictionary with operation state
        
        Returns:
            Tuple of (is_valid, issues_list)
                - is_valid: True if prerequisites met
                - issues_list: List of issue descriptions (empty if valid)
        
        Example:
            def validate_prerequisites(self, context):
                issues = []
                if 'project_root' not in context:
                    issues.append("project_root not set in context")
                if not Path(context.get('config_file', '')).exists():
                    issues.append("Config file not found")
                return len(issues) == 0, issues
        """
        return True, []
    
    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> OperationResult:
        """
        Execute the module's main work.
        
        This is where the module performs its primary function:
            - Setup modules: Configure environment
            - Story modules: Transform documentation
            - Cleanup modules: Remove temporary files
            - Docs modules: Build documentation
        
        Args:
            context: Shared context dictionary
                - Read context from previous modules
                - Write results for downstream modules
                - Access operation-wide configuration
        
        Returns:
            OperationResult with execution status and data
        
        Example:
            def execute(self, context):
                try:
                    project_root = context['project_root']
                    # Do work
                    context['my_module_output'] = result_data
                    
                    return OperationResult(
                        success=True,
                        status=OperationStatus.SUCCESS,
                        message="Module completed successfully",
                        data={'processed': 42}
                    )
                except Exception as e:
                    return OperationResult(
                        success=False,
                        status=OperationStatus.FAILED,
                        message=f"Module failed: {e}",
                        errors=[str(e)]
                    )
        """
        pass
    
    def rollback(self, context: Dict[str, Any]) -> bool:
        """
        Rollback changes made by this module.
        
        Called when:
            - This module failed and needs cleanup
            - A downstream module failed and operation is rolling back
            - User cancels operation mid-flight
        
        Override to implement custom rollback logic:
            - Delete created files
            - Restore backups
            - Revert configuration changes
            - Undo database modifications
        
        Args:
            context: Shared context dictionary (may contain rollback hints)
        
        Returns:
            True if rollback successful, False if rollback failed
        
        Example:
            def rollback(self, context):
                try:
                    backup_file = context.get('my_module_backup')
                    if backup_file:
                        shutil.copy(backup_file, original_file)
                    return True
                except Exception as e:
                    logger.error(f"Rollback failed: {e}")
                    return False
        """
        return True  # Default: no-op rollback
    
    def should_run(self, context: Dict[str, Any]) -> bool:
        """
        Determine if this module should run based on context.
        
        Override for conditional execution:
            - Skip if feature already configured
            - Skip if not needed on this platform
            - Skip if user preferences disable it
        
        Args:
            context: Shared context dictionary
        
        Returns:
            True if module should run, False to skip
        
        Example:
            def should_run(self, context):
                # Only run on Windows
                return context.get('platform') == 'windows'
            
            def should_run(self, context):
                # Skip if already configured
                config = context.get('config', {})
                return not config.get('vision_api', {}).get('enabled', False)
        """
        return True  # Default: always run
    
    def get_progress_message(self) -> str:
        """
        Get progress message to show while module is running.
        
        Returns:
            Human-readable progress message
        
        Example:
            def get_progress_message(self):
                return f"Installing {self.package_count} Python packages..."
        """
        return f"Running {self.metadata.name}..."
    
    def __str__(self) -> str:
        """String representation of module."""
        return f"{self.metadata.module_id} ({self.metadata.name})"
    
    def __repr__(self) -> str:
        """Developer representation of module."""
        return (
            f"<{self.__class__.__name__} "
            f"id={self.metadata.module_id} "
            f"phase={self.metadata.phase.value} "
            f"priority={self.metadata.priority}>"
        )
    
    # Convenience logging methods for use in subclasses
    def log_info(self, message: str) -> None:
        """Log info message (convenience wrapper)."""
        self.logger.info(message)
    
    def log_error(self, message: str) -> None:
        """Log error message (convenience wrapper)."""
        self.logger.error(message)
    
    def log_warning(self, message: str) -> None:
        """Log warning message (convenience wrapper)."""
        self.logger.warning(message)
    
    def log_debug(self, message: str) -> None:
        """Log debug message (convenience wrapper)."""
        self.logger.debug(message)
