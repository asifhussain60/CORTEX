"""
AC-LIFECYCLE-002: Phase Transition Hooks
Pre/post phase callbacks for orchestrator lifecycle management.
"""
from typing import Callable, List, Dict, Any
from src.infrastructure.lifecycle_manager import LifecycleState


class PhaseTransitionHookManager:
    """
    Manages pre/post hooks for lifecycle phase transitions.
    
    Pre-hooks: Execute before state transition (validation, setup)
    Post-hooks: Execute after state transition (cleanup, notifications)
    """
    
    def __init__(self):
        self._pre_hooks: Dict[LifecycleState, List[Callable]] = {}
        self._post_hooks: Dict[LifecycleState, List[Callable]] = {}
    
    def register_pre_hook(self, state: LifecycleState, hook: Callable):
        """Register a pre-transition hook for a lifecycle state."""
        if state not in self._pre_hooks:
            self._pre_hooks[state] = []
        self._pre_hooks[state].append(hook)
    
    def register_post_hook(self, state: LifecycleState, hook: Callable):
        """Register a post-transition hook for a lifecycle state."""
        if state not in self._post_hooks:
            self._post_hooks[state] = []
        self._post_hooks[state].append(hook)
    
    def get_pre_hooks(self, state: LifecycleState) -> List[Callable]:
        """Get all pre-hooks for a state."""
        return self._pre_hooks.get(state, [])
    
    def get_post_hooks(self, state: LifecycleState) -> List[Callable]:
        """Get all post-hooks for a state."""
        return self._post_hooks.get(state, [])
    
    def execute_pre_hooks(self, state: LifecycleState) -> Dict[str, Any]:
        """
        Execute all pre-hooks for a state.
        
        Raises:
            Exception: If any hook fails, blocks transition
            
        Returns:
            Merged results from all hooks
        """
        hooks = self.get_pre_hooks(state)
        results = {}
        
        for hook in hooks:
            hook_result = hook()
            if hook_result:
                results.update(hook_result)
        
        return results
    
    def execute_post_hooks(self, state: LifecycleState) -> Dict[str, Any]:
        """
        Execute all post-hooks for a state.
        
        Returns:
            Merged results from all hooks
        """
        hooks = self.get_post_hooks(state)
        results = {}
        
        for hook in hooks:
            hook_result = hook()
            if hook_result:
                results.update(hook_result)
        
        return results
