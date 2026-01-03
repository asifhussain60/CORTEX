"""
Execution Engine - Orchestrator Lifecycle Management.

Manages orchestrator execution with lifecycle hooks, error handling,
and monitoring.

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import logging
import time
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from src.orchestrators.base.base_orchestrator_v4_1 import BaseOrchestratorV4_1


class HookType(str, Enum):
    """Lifecycle hook types."""
    PRE_EXECUTION = "pre_execution"
    POST_EXECUTION = "post_execution"
    ON_ERROR = "on_error"
    ON_PHASE_START = "on_phase_start"
    ON_PHASE_COMPLETE = "on_phase_complete"


@dataclass
class ExecutionResult:
    """Result of orchestrator execution."""
    orchestrator_id: str
    success: bool
    status: str
    started_at: datetime
    completed_at: datetime
    duration_seconds: float
    artifacts: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    user_message: Optional[str] = None  # Rendered markdown for display
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            'orchestrator_id': self.orchestrator_id,
            'success': self.success,
            'status': self.status,
            'started_at': self.started_at.isoformat(),
            'completed_at': self.completed_at.isoformat(),
            'duration_seconds': self.duration_seconds,
            'artifacts': self.artifacts,
            'errors': self.errors,
            'metadata': self.metadata,
            'user_message': self.user_message
        }


@dataclass
class HookConfig:
    """Lifecycle hook configuration."""
    hook_type: HookType
    handler: Callable
    priority: int = 100  # Lower = earlier execution
    enabled: bool = True
    
    def __lt__(self, other):
        """Compare hooks by priority for sorting."""
        return self.priority < other.priority


class ExecutionEngine:
    """
    Orchestrator lifecycle management with hooks.
    
    Provides:
    - Orchestrator execution with timing
    - Lifecycle hooks (pre/post/error)
    - Error handling and recovery
    - Execution monitoring
    
    Lifecycle Hooks:
    - pre_execution: Before orchestrator.execute()
    - post_execution: After successful execution
    - on_error: On execution failure
    - on_phase_start: Before each phase (if orchestrator supports)
    - on_phase_complete: After each phase completes
    
    Usage:
        engine = ExecutionEngine()
        
        # Register hooks
        engine.register_hook(
            HookType.PRE_EXECUTION,
            validate_dependencies
        )
        
        # Execute orchestrator
        result = engine.run(
            orchestrator=planning_orch,
            params={'feature': 'auth'},
            hooks=hook_config
        )
    """
    
    def __init__(self):
        """Initialize execution engine."""
        self.logger = logging.getLogger("cortex.orchestrators.execution_engine")
        
        # Hook registry
        self._hooks: Dict[HookType, List[HookConfig]] = {
            hook_type: [] for hook_type in HookType
        }
        
        # Execution metrics
        self._execution_count = 0
        self._total_duration_seconds = 0.0
        self._failure_count = 0
        
        self.logger.info("ExecutionEngine initialized")
    
    def register_hook(
        self,
        hook_type: HookType,
        handler: Callable,
        priority: int = 100
    ) -> None:
        """
        Register lifecycle hook.
        
        Args:
            hook_type: Type of lifecycle hook
            handler: Callable hook function
            priority: Execution priority (lower = earlier)
        """
        hook = HookConfig(
            hook_type=hook_type,
            handler=handler,
            priority=priority
        )
        
        self._hooks[hook_type].append(hook)
        
        # Sort hooks by priority
        self._hooks[hook_type].sort()
        
        self.logger.debug(
            f"Registered {hook_type.value} hook: "
            f"{handler.__name__} (priority={priority})"
        )
    
    def unregister_hook(
        self,
        hook_type: HookType,
        handler: Callable
    ) -> bool:
        """
        Unregister lifecycle hook.
        
        Args:
            hook_type: Type of lifecycle hook
            handler: Hook function to remove
        
        Returns:
            True if hook was removed
        """
        hooks = self._hooks[hook_type]
        original_count = len(hooks)
        
        self._hooks[hook_type] = [
            h for h in hooks if h.handler != handler
        ]
        
        removed = len(self._hooks[hook_type]) < original_count
        
        if removed:
            self.logger.debug(
                f"Unregistered {hook_type.value} hook: {handler.__name__}"
            )
        
        return removed
    
    def run(
        self,
        orchestrator: BaseOrchestratorV4_1,
        params: Dict[str, Any],
        hooks: Optional[Dict[str, List[Callable]]] = None
    ) -> ExecutionResult:
        """
        Execute orchestrator with lifecycle management.
        
        Args:
            orchestrator: Orchestrator instance to execute
            params: Execution parameters
            hooks: Optional hook overrides for this execution
        
        Returns:
            ExecutionResult with execution details
        """
        orchestrator_id = orchestrator.name
        started_at = datetime.now()
        
        self.logger.info(f"Starting execution: {orchestrator_id}")
        
        # Merge global and execution-specific hooks
        effective_hooks = self._merge_hooks(hooks)
        
        try:
            # Execute pre-execution hooks
            self._execute_hooks(
                HookType.PRE_EXECUTION,
                effective_hooks,
                orchestrator=orchestrator,
                params=params
            )
            
            # Main execution
            user_request = params.get('user_request', '')
            orch_result = orchestrator.execute(user_request, **params)
            
            # Execute post-execution hooks
            self._execute_hooks(
                HookType.POST_EXECUTION,
                effective_hooks,
                orchestrator=orchestrator,
                result=orch_result
            )
            
            # Create result
            completed_at = datetime.now()
            duration = (completed_at - started_at).total_seconds()
            
            result = ExecutionResult(
                orchestrator_id=orchestrator_id,
                success=orch_result.success,
                status='completed',
                started_at=started_at,
                completed_at=completed_at,
                duration_seconds=duration,
                artifacts=getattr(orch_result, 'artifacts', []),
                errors=getattr(orch_result, 'errors', []),
                metadata={'orchestrator_result': orch_result}
            )
            
            # Update metrics
            self._execution_count += 1
            self._total_duration_seconds += duration
            
            self.logger.info(
                f"Completed execution: {orchestrator_id} "
                f"({duration:.2f}s, success={result.success})"
            )
            
            return result
            
        except Exception as e:
            # Execute error hooks
            self._execute_hooks(
                HookType.ON_ERROR,
                effective_hooks,
                orchestrator=orchestrator,
                error=e
            )
            
            # Create error result
            completed_at = datetime.now()
            duration = (completed_at - started_at).total_seconds()
            
            result = ExecutionResult(
                orchestrator_id=orchestrator_id,
                success=False,
                status='failed',
                started_at=started_at,
                completed_at=completed_at,
                duration_seconds=duration,
                errors=[str(e)],
                metadata={'exception': e}
            )
            
            # Update metrics
            self._execution_count += 1
            self._total_duration_seconds += duration
            self._failure_count += 1
            
            self.logger.error(
                f"Failed execution: {orchestrator_id} "
                f"({duration:.2f}s) - {e}",
                exc_info=True
            )
            
            raise
    
    def _merge_hooks(
        self,
        execution_hooks: Optional[Dict[str, List[Callable]]]
    ) -> Dict[HookType, List[HookConfig]]:
        """
        Merge global and execution-specific hooks.
        
        Args:
            execution_hooks: Optional hooks for this execution
        
        Returns:
            Merged hook configuration
        """
        merged = {
            hook_type: list(hooks)
            for hook_type, hooks in self._hooks.items()
        }
        
        # Add execution-specific hooks
        if execution_hooks:
            for hook_type_str, handlers in execution_hooks.items():
                try:
                    hook_type = HookType(hook_type_str)
                    for handler in handlers:
                        merged[hook_type].append(
                            HookConfig(
                                hook_type=hook_type,
                                handler=handler,
                                priority=200  # Lower priority than global
                            )
                        )
                except ValueError:
                    self.logger.warning(
                        f"Unknown hook type: {hook_type_str}"
                    )
        
        return merged
    
    def _execute_hooks(
        self,
        hook_type: HookType,
        hooks: Dict[HookType, List[HookConfig]],
        **kwargs
    ) -> None:
        """
        Execute all hooks of a specific type.
        
        Args:
            hook_type: Type of hooks to execute
            hooks: Hook configuration
            **kwargs: Arguments to pass to hooks
        """
        hook_list = hooks.get(hook_type, [])
        
        if not hook_list:
            return
        
        self.logger.debug(
            f"Executing {len(hook_list)} {hook_type.value} hook(s)"
        )
        
        for hook in hook_list:
            if not hook.enabled:
                continue
            
            try:
                hook.handler(**kwargs)
            except Exception as e:
                self.logger.error(
                    f"Hook execution failed: {hook.handler.__name__} - {e}",
                    exc_info=True
                )
                # Continue with other hooks (non-fatal)
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get execution engine metrics.
        
        Returns:
            Dictionary with metrics
        """
        avg_duration = (
            self._total_duration_seconds / self._execution_count
            if self._execution_count > 0 else 0.0
        )
        
        failure_rate = (
            self._failure_count / self._execution_count
            if self._execution_count > 0 else 0.0
        )
        
        return {
            'total_executions': self._execution_count,
            'total_duration_seconds': self._total_duration_seconds,
            'average_duration_seconds': avg_duration,
            'failure_count': self._failure_count,
            'failure_rate': failure_rate,
            'registered_hooks': {
                hook_type.value: len(hooks)
                for hook_type, hooks in self._hooks.items()
            }
        }
    
    def reset_metrics(self) -> None:
        """Reset execution metrics."""
        self._execution_count = 0
        self._total_duration_seconds = 0.0
        self._failure_count = 0
        
        self.logger.info("Metrics reset")
    
    def clear_hooks(self, hook_type: Optional[HookType] = None) -> None:
        """
        Clear registered hooks.
        
        Args:
            hook_type: Optional specific hook type to clear
        """
        if hook_type:
            self._hooks[hook_type].clear()
            self.logger.info(f"Cleared {hook_type.value} hooks")
        else:
            for ht in HookType:
                self._hooks[ht].clear()
            self.logger.info("Cleared all hooks")
