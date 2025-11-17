"""
Base Setup Module Interface

SOLID Design Principles:
- Single Responsibility: Each module handles ONE setup concern
- Open/Closed: Easy to add new modules without modifying orchestrator
- Liskov Substitution: All modules are interchangeable via base interface
- Interface Segregation: Minimal required interface
- Dependency Inversion: Modules depend on abstractions, not concrete implementations

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import logging


class SetupPhase(Enum):
    """Setup execution phases for ordering."""
    PRE_VALIDATION = 10      # Validate environment before setup
    ENVIRONMENT = 20         # Environment detection and configuration
    DEPENDENCIES = 30        # Install and verify dependencies
    FEATURES = 40            # Activate optional features (Vision API, etc.)
    VALIDATION = 50          # Validate setup completed successfully
    POST_SETUP = 60          # Post-setup tasks (brain tests, etc.)


class SetupStatus(Enum):
    """Module execution status."""
    NOT_RUN = "not_run"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    WARNING = "warning"


@dataclass
class SetupResult:
    """
    Result from a setup module execution.
    
    Attributes:
        module_id: Unique module identifier
        status: Execution status
        message: Human-readable message
        details: Additional details (dict)
        errors: List of error messages
        warnings: List of warning messages
        duration_ms: Execution time in milliseconds
    """
    module_id: str
    status: SetupStatus
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    duration_ms: float = 0.0
    
    @property
    def success(self) -> bool:
        """Check if execution was successful."""
        return self.status in [SetupStatus.SUCCESS, SetupStatus.WARNING]


@dataclass
class SetupModuleMetadata:
    """
    Metadata describing a setup module.
    
    Attributes:
        module_id: Unique identifier (e.g., "platform_config", "vision_api")
        name: Display name
        description: What this module does
        phase: Which phase to run in
        priority: Order within phase (lower = earlier)
        dependencies: List of module_ids that must run first
        optional: Whether this module can be skipped on failure
        enabled_by_default: Whether to run by default
    """
    module_id: str
    name: str
    description: str
    phase: SetupPhase
    priority: int = 100
    dependencies: List[str] = field(default_factory=list)
    optional: bool = False
    enabled_by_default: bool = True


class BaseSetupModule(ABC):
    """
    Abstract base class for all setup modules.
    
    Each module must implement:
    - get_metadata(): Return module metadata
    - validate_prerequisites(): Check if module can run
    - execute(): Perform setup tasks
    - rollback(): Undo changes if possible
    
    Example:
        class VisionAPISetupModule(BaseSetupModule):
            def get_metadata(self) -> SetupModuleMetadata:
                return SetupModuleMetadata(
                    module_id="vision_api",
                    name="Vision API Activation",
                    description="Enable GitHub Copilot Vision API",
                    phase=SetupPhase.FEATURES
                )
            
            def validate_prerequisites(self, context: Dict) -> Tuple[bool, List[str]]:
                # Check config file exists, etc.
                return True, []
            
            def execute(self, context: Dict) -> SetupResult:
                # Enable Vision API in config
                return SetupResult(...)
            
            def rollback(self, context: Dict) -> bool:
                # Disable Vision API if needed
                return True
    """
    
    def __init__(self):
        """Initialize module with logger."""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._metadata: Optional[SetupModuleMetadata] = None
    
    @property
    def metadata(self) -> SetupModuleMetadata:
        """Get module metadata (cached)."""
        if self._metadata is None:
            self._metadata = self.get_metadata()
        return self._metadata
    
    @abstractmethod
    def get_metadata(self) -> SetupModuleMetadata:
        """
        Return module metadata.
        
        Returns:
            SetupModuleMetadata describing this module
        """
        pass
    
    @abstractmethod
    def validate_prerequisites(self, context: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate that prerequisites are met before execution.
        
        Args:
            context: Shared context dictionary with platform info, paths, etc.
        
        Returns:
            (is_valid, list_of_issues)
            - is_valid: True if prerequisites met
            - list_of_issues: Error messages if validation failed
        
        Example:
            def validate_prerequisites(self, context):
                issues = []
                if not context.get('project_root'):
                    issues.append("Project root not found in context")
                return len(issues) == 0, issues
        """
        pass
    
    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> SetupResult:
        """
        Execute setup tasks.
        
        Args:
            context: Shared context dictionary
                - Can read: platform info, paths, previous results
                - Can write: Results for downstream modules
        
        Returns:
            SetupResult with execution details
        
        Example:
            def execute(self, context):
                try:
                    # Perform setup
                    result = self._enable_feature()
                    
                    # Update context for downstream modules
                    context['vision_api_enabled'] = True
                    
                    return SetupResult(
                        module_id=self.metadata.module_id,
                        status=SetupStatus.SUCCESS,
                        message="Vision API enabled",
                        details={'version': '1.0'}
                    )
                except Exception as e:
                    return SetupResult(
                        module_id=self.metadata.module_id,
                        status=SetupStatus.FAILED,
                        message=str(e),
                        errors=[str(e)]
                    )
        """
        pass
    
    def rollback(self, context: Dict[str, Any]) -> bool:
        """
        Rollback changes if setup fails.
        
        Optional: Override if rollback is possible.
        
        Args:
            context: Shared context dictionary
        
        Returns:
            True if rollback successful
        """
        self.logger.info(f"No rollback needed for {self.metadata.module_id}")
        return True
    
    def should_run(self, context: Dict[str, Any]) -> bool:
        """
        Determine if module should run based on context.
        
        Override for conditional execution logic.
        
        Args:
            context: Shared context dictionary
        
        Returns:
            True if module should run
        """
        return self.metadata.enabled_by_default
    
    def log_info(self, message: str):
        """Log info message."""
        self.logger.info(f"[{self.metadata.module_id}] {message}")
    
    def log_warning(self, message: str):
        """Log warning message."""
        self.logger.warning(f"[{self.metadata.module_id}] {message}")
    
    def log_error(self, message: str):
        """Log error message."""
        self.logger.error(f"[{self.metadata.module_id}] {message}")
