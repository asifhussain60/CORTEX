"""Adaptive Execution Modes for task optimization.

This module implements execution modes (FAST, BALANCED, THOROUGH) that provide
different performance/quality trade-offs for orchestrator task execution.

AC-EX-002-01: FAST mode minimizes overhead, BALANCED mode optimizes for common
cases, THOROUGH mode maximizes validation.

Author: Asif Hussain
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional
from cortex.models.canonical_enums import ExecutionMode




@dataclass
class ModeConfiguration:
    """Configuration for an execution mode.
    
    Attributes:
        mode: ExecutionMode
        timeout_seconds: Maximum execution time
        validation_level: How strict validation should be (0.0-1.0)
        enable_caching: Whether to use caching
        enable_logging: Whether to enable detailed logging
        retry_count: Number of retries on failure
        parallel_execution: Whether to parallelize operations
    """
    
    mode: ExecutionMode
    timeout_seconds: float
    validation_level: float  # 0.0 = none, 1.0 = maximum
    enable_caching: bool
    enable_logging: bool
    retry_count: int
    parallel_execution: bool


class AdaptiveExecutor:
    """Executes tasks with configurable performance/quality trade-offs.
    
    Provides three execution modes:
    - FAST: Minimizes overhead and latency
    - BALANCED: Optimizes for common use cases
    - THOROUGH: Maximizes validation and reliability
    
    Example:
        >>> executor = AdaptiveExecutor()
        >>> executor.set_execution_mode(ExecutionMode.FAST)
        >>> result = executor.execute({"task": "example"})
    """
    
    def __init__(self) -> None:
        """Initialize the AdaptiveExecutor with mode configurations."""
        self._mode_configs: Dict[ExecutionMode, ModeConfiguration] = {
            ExecutionMode.FAST: ModeConfiguration(
                mode=ExecutionMode.FAST,
                timeout_seconds=2.0,
                validation_level=0.2,
                enable_caching=True,
                enable_logging=False,
                retry_count=0,
                parallel_execution=True,
            ),
            ExecutionMode.BALANCED: ModeConfiguration(
                mode=ExecutionMode.BALANCED,
                timeout_seconds=5.0,
                validation_level=0.6,
                enable_caching=True,
                enable_logging=True,
                retry_count=1,
                parallel_execution=True,
            ),
            ExecutionMode.THOROUGH: ModeConfiguration(
                mode=ExecutionMode.THOROUGH,
                timeout_seconds=15.0,
                validation_level=1.0,
                enable_caching=False,
                enable_logging=True,
                retry_count=3,
                parallel_execution=False,
            ),
        }
        self._current_mode = ExecutionMode.BALANCED
    
    def set_execution_mode(self, mode: ExecutionMode) -> None:
        """Set the execution mode.
        
        Args:
            mode: ExecutionMode to use
            
        Raises:
            ValueError: If mode is not an ExecutionMode
        """
        if not isinstance(mode, ExecutionMode):
            raise ValueError("mode must be an ExecutionMode")
        self._current_mode = mode
    
    def get_execution_mode(self) -> ExecutionMode:
        """Get the current execution mode.
        
        Returns:
            Current ExecutionMode
        """
        return self._current_mode
    
    def get_mode_config(
        self,
        mode: Optional[ExecutionMode] = None,
    ) -> ModeConfiguration:
        """Get configuration for a mode.
        
        Args:
            mode: ExecutionMode (uses current if not specified)
            
        Returns:
            ModeConfiguration for the mode
        """
        if mode is None:
            mode = self._current_mode
        return self._mode_configs[mode]
    
    def execute(
        self,
        task: Any,
        context: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Execute a task with current mode configuration.
        
        Args:
            task: Task to execute
            context: Optional execution context
            
        Returns:
            Task result
        """
        if context is None:
            context = {}
        
        config = self.get_mode_config()
        
        # Simulate execution with mode-specific behavior
        if config.validation_level > 0:
            self._validate_task(task)
        
        if config.retry_count > 0:
            return self._execute_with_retries(
                task,
                config.retry_count,
                context,
            )
        else:
            return self._execute_once(task, context)
    
    def _validate_task(self, task: Any) -> None:
        """Validate task based on current validation level.
        
        Args:
            task: Task to validate
            
        Raises:
            ValueError: If task is invalid
        """
        if not task:
            raise ValueError("Task cannot be None or empty")
    
    def _execute_once(
        self,
        task: Any,
        context: Dict[str, Any],
    ) -> Any:
        """Execute task once without retries.
        
        Args:
            task: Task to execute
            context: Execution context
            
        Returns:
            Execution result
        """
        return {
            "status": "success",
            "task": task,
            "mode": self._current_mode.value,
        }
    
    def _execute_with_retries(
        self,
        task: Any,
        retries: int,
        context: Dict[str, Any],
    ) -> Any:
        """Execute task with retries on failure.
        
        Args:
            task: Task to execute
            retries: Number of retries allowed
            context: Execution context
            
        Returns:
            Execution result
            
        Raises:
            Exception: If all retries fail
        """
        last_error = None
        
        for attempt in range(retries + 1):
            try:
                return self._execute_once(task, context)
            except Exception as e:
                last_error = e
                if attempt == retries:
                    raise
        
        if last_error:
            raise last_error
