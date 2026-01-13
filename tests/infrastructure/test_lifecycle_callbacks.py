"""
Tests for AC-LIFECYCLE-003: Pre/Post Phase Callbacks
Integrated callback execution with lifecycle transitions.
"""
import pytest
from src.infrastructure.lifecycle_manager import LifecycleManager, LifecycleState
from src.infrastructure.phase_transition_hooks import PhaseTransitionHookManager
from src.infrastructure.lifecycle_callbacks import LifecycleCallbackExecutor


@pytest.mark.ac_id("AC-LIFECYCLE-003")
class TestLifecycleCallbacks:
    """Test integrated callback execution with lifecycle."""
    
    @pytest.mark.ac_id("AC-LIFECYCLE-003")
    def test_lifecycle_with_callbacks_integration(self):
        """AC-LIFECYCLE-003: Lifecycle integrates with callback system."""
        lifecycle = LifecycleManager()
        hooks = PhaseTransitionHookManager()
        executor = LifecycleCallbackExecutor(lifecycle, hooks)
        
        assert executor.lifecycle == lifecycle
        assert executor.hooks == hooks
    
    @pytest.mark.ac_id("AC-LIFECYCLE-003")
    def test_transition_executes_pre_and_post_hooks(self):
        """AC-LIFECYCLE-003: Transition triggers pre/post hooks."""
        lifecycle = LifecycleManager()
        hooks = PhaseTransitionHookManager()
        executor = LifecycleCallbackExecutor(lifecycle, hooks)
        
        executed = []
        
        def pre_hook():
            executed.append("pre")
            return {"validated": True}
        
        def post_hook():
            executed.append("post")
            return {"notified": True}
        
        hooks.register_pre_hook(LifecycleState.SPEC, pre_hook)
        hooks.register_post_hook(LifecycleState.SPEC, post_hook)
        
        result = executor.transition_with_hooks(LifecycleState.SPEC)
        
        assert result.success is True
        assert "pre" in executed
        assert "post" in executed
        assert executed.index("pre") < executed.index("post")
    
    @pytest.mark.ac_id("AC-LIFECYCLE-003")
    def test_failed_pre_hook_prevents_transition(self):
        """AC-LIFECYCLE-003: Failed pre-hook blocks state change."""
        lifecycle = LifecycleManager()
        hooks = PhaseTransitionHookManager()
        executor = LifecycleCallbackExecutor(lifecycle, hooks)
        
        def failing_pre_hook():
            raise ValueError("Pre-validation failed")
        
        hooks.register_pre_hook(LifecycleState.SPEC, failing_pre_hook)
        
        result = executor.transition_with_hooks(LifecycleState.SPEC)
        
        # Transition should fail, state unchanged
        assert result.success is False
        assert lifecycle.current_state == LifecycleState.IDLE
