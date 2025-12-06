"""
Orchestrator Factory - Dependency Injection & Configuration Management

Eliminates redundant initialization across orchestrators by providing:
- Centralized orchestrator instantiation
- Shared dependency injection
- Configuration-driven setup
- Testability via mock injection

Based on holistic analysis findings:
- 180+ lines of duplicated initialization code
- Tight coupling between orchestrators
- No dependency injection
- Manual import/initialization in each orchestrator

Author: Asif Hussain
Created: December 6, 2025
Version: 2.0.0 (Updated with Phase 2-5 integration)
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional, Type, TypeVar, Protocol
from dataclasses import dataclass, field

# Import new frameworks from Phase 2-5
from src.orchestrators.config_manager import OrchestratorConfig
from src.orchestrators.validation_framework import (
    validate_plan,
    validate_task,
    validate_tdd_transition,
    validate_code_quality
)
from src.orchestrators.session_model import (
    SessionFactory,
    TDDSession,
    PlanningSession,
    ExecutionSession,
    SessionStatus
)

logger = logging.getLogger(__name__)

T = TypeVar('T')


# ==================== Note: OrchestratorConfig moved to config_manager.py ====================
# Import OrchestratorConfig from config_manager instead of defining here
# This eliminates duplication and provides Phase 5 features


# ==================== Protocols (Interfaces) ====================

class ITDDOrchestrator(Protocol):
    """Interface for TDD orchestrators."""
    
    def start_session(self, feature_name: str, task_id: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Start TDD session."""
        ...
    
    def execute_red_phase(self, session_id: str) -> Dict[str, Any]:
        """Execute RED phase."""
        ...
    
    def execute_green_phase(self, session_id: str) -> Dict[str, Any]:
        """Execute GREEN phase."""
        ...
    
    def execute_refactor_phase(self, session_id: str) -> Dict[str, Any]:
        """Execute REFACTOR phase."""
        ...


class IGitCheckpointOrchestrator(Protocol):
    """Interface for Git checkpoint orchestrators."""
    
    def create_checkpoint(self, message: str, checkpoint_type: str = "manual") -> Dict[str, Any]:
        """Create git checkpoint."""
        ...
    
    def create_auto_checkpoint(self, operation: str, message: str) -> Optional[str]:
        """Create automatic checkpoint."""
        ...
    
    def rollback_to_checkpoint(self, checkpoint_id: str) -> Dict[str, Any]:
        """Rollback to checkpoint."""
        ...


class ICodeExecutor(Protocol):
    """Interface for code execution agents."""
    
    def can_handle(self, request: Any) -> bool:
        """Check if can handle request."""
        ...
    
    def execute(self, request: Any) -> Any:
        """Execute code implementation."""
        ...


class ICleanupOrchestrator(Protocol):
    """Interface for cleanup orchestrators."""
    
    def execute_cleanup(self, scope: str, dry_run: bool = False) -> Dict[str, Any]:
        """Execute cleanup operations."""
        ...


# ==================== Factory ====================

class OrchestratorFactory:
    """
    Factory for creating orchestrators with dependency injection.
    
    Eliminates:
    - 180+ lines of redundant initialization code
    - Tight coupling between orchestrators
    - Manual dependency management
    - Testing difficulties
    
    Usage:
        config = OrchestratorConfig(cortex_root=Path("/path/to/cortex"))
        factory = OrchestratorFactory(config)
        
        # Get orchestrator with all dependencies injected
        plan_executor = factory.get_plan_execution_orchestrator()
        
        # For testing: inject mocks
        factory_with_mocks = OrchestratorFactory(config, tdd_orchestrator=MockTDD())
    """
    
    def __init__(
        self,
        config: OrchestratorConfig,
        # Optional dependency injection (for testing)
        tdd_orchestrator: Optional[ITDDOrchestrator] = None,
        git_checkpoint: Optional[IGitCheckpointOrchestrator] = None,
        code_executor: Optional[ICodeExecutor] = None,
        cleanup_orchestrator: Optional[ICleanupOrchestrator] = None
    ):
        """
        Initialize factory with configuration and optional mock dependencies.
        
        Args:
            config: Orchestrator configuration
            tdd_orchestrator: Optional TDD orchestrator (for testing)
            git_checkpoint: Optional git checkpoint (for testing)
            code_executor: Optional code executor (for testing)
            cleanup_orchestrator: Optional cleanup orchestrator (for testing)
        """
        self.config = config
        
        # Dependency cache (singleton per factory instance)
        self._tdd_orchestrator = tdd_orchestrator
        self._git_checkpoint = git_checkpoint
        self._code_executor = code_executor
        self._cleanup_orchestrator = cleanup_orchestrator
        
        # Orchestrator cache
        self._plan_execution_orchestrator: Optional[Any] = None
        self._planning_orchestrator: Optional[Any] = None
    
    # ==================== Shared Dependencies ====================
    
    def get_tdd_orchestrator(self) -> Optional[ITDDOrchestrator]:
        """Get or create TDD implementation orchestrator."""
        if not self.config.enable_tdd:
            return None
        
        if self._tdd_orchestrator is None:
            try:
                from src.orchestrators.tdd_implementation_orchestrator import TDDImplementationOrchestrator
                self._tdd_orchestrator = TDDImplementationOrchestrator(
                    project_root=self.config.project_root,
                    cortex_root=self.config.cortex_root,
                    enable_pattern_library=self.config.enable_pattern_library
                )
                logger.info("✅ TDDImplementationOrchestrator initialized via factory")
            except ImportError as e:
                logger.warning(f"⚠️  TDDImplementationOrchestrator not available: {e}")
                self._tdd_orchestrator = None
        
        return self._tdd_orchestrator
    
    def get_git_checkpoint(self) -> Optional[IGitCheckpointOrchestrator]:
        """Get or create Git checkpoint orchestrator."""
        if not self.config.enable_git_checkpoints:
            return None
        
        if self._git_checkpoint is None:
            try:
                from src.orchestrators.git_checkpoint_orchestrator import GitCheckpointOrchestrator
                self._git_checkpoint = GitCheckpointOrchestrator(
                    project_root=self.config.project_root
                )
                logger.info("✅ GitCheckpointOrchestrator initialized via factory")
            except ImportError as e:
                logger.warning(f"⚠️  GitCheckpointOrchestrator not available: {e}")
                self._git_checkpoint = None
        
        return self._git_checkpoint
    
    def get_code_executor(self) -> Optional[ICodeExecutor]:
        """Get or create Code Executor agent."""
        if self._code_executor is None:
            try:
                from src.cortex_agents.tactical.code_executor import CodeExecutor
                self._code_executor = CodeExecutor("CodeExecutor")
                logger.info("✅ CodeExecutor initialized via factory")
            except ImportError as e:
                logger.warning(f"⚠️  CodeExecutor not available: {e}")
                self._code_executor = None
        
        return self._code_executor
    
    def get_cleanup_orchestrator(self) -> Optional[ICleanupOrchestrator]:
        """Get or create Cleanup orchestrator."""
        if not self.config.enable_cleanup:
            return None
        
        if self._cleanup_orchestrator is None:
            try:
                from src.orchestrators.cleanup_orchestrator import CleanupOrchestrator
                self._cleanup_orchestrator = CleanupOrchestrator(
                    str(self.config.cortex_root)
                )
                logger.info("✅ CleanupOrchestrator initialized via factory")
            except ImportError as e:
                logger.warning(f"⚠️  CleanupOrchestrator not available: {e}")
                self._cleanup_orchestrator = None
        
        return self._cleanup_orchestrator
    
    # ==================== High-Level Orchestrators ====================
    
    def get_plan_execution_orchestrator(self) -> Any:
        """
        Get or create Plan Execution Orchestrator with injected dependencies.
        
        Returns:
            Plan execution orchestrator with all dependencies injected
        """
        if self._plan_execution_orchestrator is None:
            # Import here to avoid circular dependency
            from src.orchestrators.plan_execution_orchestrator_v2 import PlanExecutionOrchestratorV2
            
            self._plan_execution_orchestrator = PlanExecutionOrchestratorV2(
                cortex_root=self.config.cortex_root,
                tdd_orchestrator=self.get_tdd_orchestrator(),
                git_checkpoint=self.get_git_checkpoint(),
                code_executor=self.get_code_executor(),
                cleanup_orchestrator=self.get_cleanup_orchestrator()
            )
            logger.info("✅ PlanExecutionOrchestratorV2 created via factory")
        
        return self._plan_execution_orchestrator
    
    def get_planning_orchestrator(self) -> Any:
        """
        Get or create Planning Orchestrator with injected dependencies.
        
        Returns:
            Planning orchestrator with all dependencies injected
        """
        if self._planning_orchestrator is None:
            from src.orchestrators.planning_orchestrator import PlanningOrchestrator
            
            # Use existing planning orchestrator (no dependency injection yet)
            # This will be migrated in Phase 2
            self._planning_orchestrator = PlanningOrchestrator(str(self.config.cortex_root))
            logger.info("✅ PlanningOrchestrator created via factory (legacy mode)")
        
        return self._planning_orchestrator


# ==================== Factory Builder ====================

def create_orchestrator_factory(
    cortex_root: str,
    **config_overrides
) -> OrchestratorFactory:
    """
    Convenience function to create factory with default configuration.
    
    Args:
        cortex_root: Path to CORTEX root directory
        **config_overrides: Override default configuration values
    
    Returns:
        Configured orchestrator factory
    
    Example:
        factory = create_orchestrator_factory(
            cortex_root="/path/to/cortex",
            enable_vision_api=False,
            tdd_auto_debug=True
        )
    """
    config = OrchestratorConfig(
        cortex_root=Path(cortex_root),
        **config_overrides
    )
    
    return OrchestratorFactory(config)


__all__ = [
    'OrchestratorFactory',
    'OrchestratorConfig',
    'ITDDOrchestrator',
    'IGitCheckpointOrchestrator',
    'ICodeExecutor',
    'ICleanupOrchestrator',
    'create_orchestrator_factory'
]
