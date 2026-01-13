"""
AC-LIFECYCLE-003: Pre/Post Phase Callbacks
Integrated callback execution with lifecycle state transitions.
"""
from src.infrastructure.lifecycle_manager import LifecycleManager, LifecycleState, TransitionResult
from src.infrastructure.phase_transition_hooks import PhaseTransitionHookManager
from datetime import datetime


class LifecycleCallbackExecutor:
    """
    Integrates lifecycle state management with pre/post hooks.
    
    Ensures callbacks execute at correct times:
    1. Execute pre-hooks (validation, setup)
    2. If pre-hooks pass, execute state transition
    3. Execute post-hooks (cleanup, notifications)
    """
    
    def __init__(self, lifecycle: LifecycleManager, hooks: PhaseTransitionHookManager):
        self.lifecycle = lifecycle
        self.hooks = hooks
    
    def transition_with_hooks(self, target_state: LifecycleState) -> TransitionResult:
        """
        Execute state transition with pre/post hooks.
        
        Args:
            target_state: Desired lifecycle state
            
        Returns:
            TransitionResult with success status
        """
        # Execute pre-hooks
        try:
            pre_results = self.hooks.execute_pre_hooks(target_state)
        except Exception as e:
            # Pre-hook failed, block transition
            return TransitionResult(
                success=False,
                from_state=self.lifecycle.current_state,
                to_state=target_state,
                message=f"Pre-hook failed: {str(e)}",
                timestamp=datetime.utcnow()
            )
        
        # Execute state transition
        transition_result = self.lifecycle.transition_to(target_state)
        
        if not transition_result.success:
            return transition_result
        
        # Execute post-hooks (even if they fail, transition completed)
        try:
            post_results = self.hooks.execute_post_hooks(target_state)
        except Exception as e:
            # Post-hook failed, but transition already succeeded
            pass
        
        return transition_result
