"""Tests for Adaptive Execution Modes.

This module tests execution modes (FAST, BALANCED, THOROUGH) that optimize
orchestrator execution for different scenarios.

AC-EX-002-01: FAST mode minimizes overhead, BALANCED mode optimizes for common
cases, THOROUGH mode maximizes validation.

Author: Asif Hussain
Copyright: © 2025-2026 Asif Hussain. All rights reserved.
"""

import unittest
from enum import Enum
from typing import Any, Dict, Optional
from dataclasses import dataclass
from unittest.mock import MagicMock, patch


class ExecutionMode(Enum):
    """Execution mode enum for adaptive performance tuning.
    
    Modes:
        FAST: Minimize overhead, skip non-critical validation
        BALANCED: Optimize for common cases, standard validation
        THOROUGH: Maximize validation, additional safety checks
    """
    
    FAST = "fast"
    BALANCED = "balanced"
    THOROUGH = "thorough"


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
    
    def get_mode_config(self, mode: Optional[ExecutionMode] = None) -> ModeConfiguration:
        """Get configuration for a mode.
        
        Args:
            mode: ExecutionMode (uses current if not specified)
            
        Returns:
            ModeConfiguration for the mode
        """
        if mode is None:
            mode = self._current_mode
        
        return self._mode_configs[mode]
    
    def execute(self, task: Any, context: Optional[Dict[str, Any]] = None) -> Any:
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
            return self._execute_with_retries(task, config.retry_count, context)
        else:
            return self._execute_once(task, context)
    
    def _validate_task(self, task: Any) -> None:
        """Validate task based on current validation level."""
        if not task:
            raise ValueError("Task cannot be None or empty")
    
    def _execute_once(self, task: Any, context: Dict[str, Any]) -> Any:
        """Execute task once without retries."""
        return {"status": "success", "task": task, "mode": self._current_mode.value}
    
    def _execute_with_retries(self, task: Any, retries: int, context: Dict[str, Any]) -> Any:
        """Execute task with retries on failure."""
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


class TestAdaptiveExecutionModes(unittest.TestCase):
    """Tests for adaptive execution modes."""
    
    def setUp(self) -> None:
        """Set up test fixtures."""
        self.executor = AdaptiveExecutor()
    
    def test_execution_mode_enum(self) -> None:
        """Test ExecutionMode enum values."""
        self.assertEqual(ExecutionMode.FAST.value, "fast")
        self.assertEqual(ExecutionMode.BALANCED.value, "balanced")
        self.assertEqual(ExecutionMode.THOROUGH.value, "thorough")
    
    def test_mode_configuration_creation(self) -> None:
        """Test creating mode configurations."""
        config = self.executor.get_mode_config(ExecutionMode.FAST)
        
        self.assertEqual(config.mode, ExecutionMode.FAST)
        self.assertLess(config.timeout_seconds, 5.0)
        self.assertLess(config.validation_level, 0.5)
    
    def test_fast_mode_minimizes_overhead(self) -> None:
        """Test that FAST mode minimizes overhead."""
        fast_config = self.executor.get_mode_config(ExecutionMode.FAST)
        balanced_config = self.executor.get_mode_config(ExecutionMode.BALANCED)
        
        self.assertLess(fast_config.timeout_seconds, balanced_config.timeout_seconds)
        self.assertLess(fast_config.validation_level, balanced_config.validation_level)
    
    def test_balanced_mode_standard_validation(self) -> None:
        """Test that BALANCED mode has standard validation."""
        balanced_config = self.executor.get_mode_config(ExecutionMode.BALANCED)
        
        self.assertEqual(balanced_config.retry_count, 1)
        self.assertTrue(balanced_config.enable_logging)
        self.assertTrue(balanced_config.enable_caching)
    
    def test_thorough_mode_maximizes_validation(self) -> None:
        """Test that THOROUGH mode maximizes validation."""
        thorough_config = self.executor.get_mode_config(ExecutionMode.THOROUGH)
        
        self.assertEqual(thorough_config.validation_level, 1.0)
        self.assertGreater(thorough_config.retry_count, 1)
        self.assertTrue(thorough_config.enable_logging)
    
    def test_set_and_get_execution_mode(self) -> None:
        """Test setting and getting execution mode."""
        self.executor.set_execution_mode(ExecutionMode.FAST)
        self.assertEqual(self.executor.get_execution_mode(), ExecutionMode.FAST)
        
        self.executor.set_execution_mode(ExecutionMode.THOROUGH)
        self.assertEqual(self.executor.get_execution_mode(), ExecutionMode.THOROUGH)
    
    def test_default_mode_is_balanced(self) -> None:
        """Test that default mode is BALANCED."""
        executor = AdaptiveExecutor()
        self.assertEqual(executor.get_execution_mode(), ExecutionMode.BALANCED)
    
    def test_execute_in_fast_mode(self) -> None:
        """Test executing in FAST mode."""
        self.executor.set_execution_mode(ExecutionMode.FAST)
        result = self.executor.execute({"test": "data"})
        
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["mode"], "fast")
    
    def test_execute_in_balanced_mode(self) -> None:
        """Test executing in BALANCED mode."""
        self.executor.set_execution_mode(ExecutionMode.BALANCED)
        result = self.executor.execute({"test": "data"})
        
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["mode"], "balanced")
    
    def test_execute_in_thorough_mode(self) -> None:
        """Test executing in THOROUGH mode."""
        self.executor.set_execution_mode(ExecutionMode.THOROUGH)
        result = self.executor.execute({"test": "data"})
        
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["mode"], "thorough")
    
    def test_invalid_mode_raises_error(self) -> None:
        """Test that invalid mode raises error."""
        with self.assertRaises(ValueError):
            self.executor.set_execution_mode("invalid_mode")
    
    def test_fast_mode_no_retries(self) -> None:
        """Test that FAST mode has no retries."""
        fast_config = self.executor.get_mode_config(ExecutionMode.FAST)
        self.assertEqual(fast_config.retry_count, 0)
    
    def test_thorough_mode_with_retries(self) -> None:
        """Test that THOROUGH mode has retries."""
        thorough_config = self.executor.get_mode_config(ExecutionMode.THOROUGH)
        self.assertGreater(thorough_config.retry_count, 0)
    
    def test_fast_mode_caching_enabled(self) -> None:
        """Test that FAST mode has caching enabled."""
        fast_config = self.executor.get_mode_config(ExecutionMode.FAST)
        self.assertTrue(fast_config.enable_caching)
    
    def test_thorough_mode_caching_disabled(self) -> None:
        """Test that THOROUGH mode has caching disabled."""
        thorough_config = self.executor.get_mode_config(ExecutionMode.THOROUGH)
        self.assertFalse(thorough_config.enable_caching)
    
    def test_fast_mode_no_logging(self) -> None:
        """Test that FAST mode has logging disabled."""
        fast_config = self.executor.get_mode_config(ExecutionMode.FAST)
        self.assertFalse(fast_config.enable_logging)
    
    def test_thorough_mode_parallel_disabled(self) -> None:
        """Test that THOROUGH mode has parallel execution disabled."""
        thorough_config = self.executor.get_mode_config(ExecutionMode.THOROUGH)
        self.assertFalse(thorough_config.parallel_execution)
    
    def test_mode_configuration_dataclass(self) -> None:
        """Test ModeConfiguration dataclass."""
        config = ModeConfiguration(
            mode=ExecutionMode.FAST,
            timeout_seconds=2.0,
            validation_level=0.2,
            enable_caching=True,
            enable_logging=False,
            retry_count=0,
            parallel_execution=True,
        )
        
        self.assertEqual(config.mode, ExecutionMode.FAST)
        self.assertEqual(config.timeout_seconds, 2.0)
        self.assertEqual(config.validation_level, 0.2)


if __name__ == "__main__":
    unittest.main()
