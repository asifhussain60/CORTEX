"""
Tests for AC-LIFECYCLE-002: Phase Transition Hooks
Pre/post phase callbacks for orchestrator lifecycle events.
"""
import pytest
from src.infrastructure.lifecycle_manager import LifecycleManager, LifecycleState
from src.infrastructure.phase_transition_hooks import PhaseTransitionHookManager


@pytest.mark.ac_id("AC-LIFECYCLE-002")
class TestPhaseTransitionHooks:
    """Test pre/post phase transition callbacks."""
    
    @pytest.mark.ac_id("AC-LIFECYCLE-002")
    def test_pre_phase_hook_registration(self):
        """AC-LIFECYCLE-002: Can register pre-phase hooks."""
        hook_manager = PhaseTransitionHookManager()
        
        def pre_hook():
            return {"validated": True}
        
        hook_manager.register_pre_hook(LifecycleState.ACTIVE, pre_hook)
        hooks = hook_manager.get_pre_hooks(LifecycleState.ACTIVE)
        assert len(hooks) == 1
    
    @pytest.mark.ac_id("AC-LIFECYCLE-002")
    def test_post_phase_hook_registration(self):
        """AC-LIFECYCLE-002: Can register post-phase hooks."""
        hook_manager = PhaseTransitionHookManager()
        
        def post_hook():
            return {"cleanup": True}
        
        hook_manager.register_post_hook(LifecycleState.ACTIVE, post_hook)
        hooks = hook_manager.get_post_hooks(LifecycleState.ACTIVE)
        assert len(hooks) == 1
    
    @pytest.mark.ac_id("AC-LIFECYCLE-002")
    def test_pre_hook_executes_before_transition(self):
        """AC-LIFECYCLE-002: Pre-hooks execute before state change."""
        hook_manager = PhaseTransitionHookManager()
        lifecycle = LifecycleManager()
        
        executed = []
        
        def pre_hook():
            executed.append("pre")
            return {"success": True}
        
        hook_manager.register_pre_hook(LifecycleState.SPEC, pre_hook)
        result = hook_manager.execute_pre_hooks(LifecycleState.SPEC)
        
        assert "pre" in executed
        assert result["success"] is True
    
    @pytest.mark.ac_id("AC-LIFECYCLE-002")
    def test_post_hook_executes_after_transition(self):
        """AC-LIFECYCLE-002: Post-hooks execute after state change."""
        hook_manager = PhaseTransitionHookManager()
        
        executed = []
        
        def post_hook():
            executed.append("post")
            return {"cleanup_done": True}
        
        hook_manager.register_post_hook(LifecycleState.SPEC, post_hook)
        result = hook_manager.execute_post_hooks(LifecycleState.SPEC)
        
        assert "post" in executed
        assert result["cleanup_done"] is True
    
    @pytest.mark.ac_id("AC-LIFECYCLE-002")
    def test_hook_failure_blocks_transition(self):
        """AC-LIFECYCLE-002: Failed pre-hook must block transition."""
        hook_manager = PhaseTransitionHookManager()
        
        def failing_hook():
            raise ValueError("Validation failed")
        
        hook_manager.register_pre_hook(LifecycleState.SPEC, failing_hook)
        
        with pytest.raises(ValueError):
            hook_manager.execute_pre_hooks(LifecycleState.SPEC)
