"""
Test suite for session management continuation prompt system.

Tests the BaseOrchestrator session management methods:
- update_continuation_prompt()
- check_token_usage()
- _estimate_tokens()
- _get_git_checkpoints()
"""

import pytest
from pathlib import Path
from datetime import datetime
from src.orchestration_4_0.base.base_orchestrator import BaseOrchestrator


class TestOrchestrator(BaseOrchestrator):
    """Concrete implementation of BaseOrchestrator for testing."""
    
    def _setup(self, context):
        pass
    
    def _register_phases(self):
        self.phase_manager.register_phase("phase1", "Phase 1", required=True)
        self.phase_manager.register_phase("phase2", "Phase 2", required=True)
        self.phase_manager.register_phase("phase3", "Phase 3", required=True)
    
    def _execute_phase(self, phase_name, context):
        return {"status": "success"}
    
    def _teardown(self, context):
        return {"status": "cleanup_complete"}


@pytest.fixture
def orchestrator():
    """Create test orchestrator instance."""
    return TestOrchestrator(
        name="test_session_mgmt",
        config={
            "token_warning_threshold": 80000,
            "continuation_prompt_enabled": True
        }
    )


@pytest.fixture
def plan_dir(tmp_path):
    """Create temporary plan directory structure."""
    plan_dir = tmp_path / "test-plan"
    plan_dir.mkdir()
    (plan_dir / "tracking").mkdir()
    (plan_dir / "artifacts").mkdir()
    
    # Create some dummy artifacts
    (plan_dir / "artifacts" / "test1.txt").write_text("artifact 1")
    (plan_dir / "artifacts" / "test2.txt").write_text("artifact 2")
    
    return plan_dir


class TestContinuationPrompt:
    """Test continuation prompt generation."""
    
    def test_update_continuation_prompt_creates_file(self, orchestrator, plan_dir):
        """Test that continuation prompt file is created."""
        # Register phases
        orchestrator._register_phases()
        
        # Mark first phase as complete
        orchestrator.phase_manager.start_phase("phase1")
        orchestrator.phase_manager.complete_phase("phase1")
        
        # Generate continuation prompt
        result = orchestrator.update_continuation_prompt(
            plan_name="test-plan",
            plan_id="test-123",
            plan_dir=plan_dir,
            current_phase={"number": 1, "name": "Phase 1"},
            next_phase={"number": 2, "name": "Phase 2"}
        )
        
        assert result is True
        
        # Verify file exists
        prompt_file = plan_dir / "tracking" / "CONTINUATION-PROMPT.md"
        assert prompt_file.exists()
        
        # Verify content
        content = prompt_file.read_text(encoding="utf-8")
        assert "test-plan" in content
        assert "test-123" in content
        assert "Phase 1" in content
        assert "Phase 2" in content
        assert "Continue executing plan" in content
    
    def test_continuation_prompt_includes_progress(self, orchestrator, plan_dir):
        """Test that continuation prompt shows accurate progress."""
        orchestrator._register_phases()
        
        # Complete 2 out of 3 phases
        orchestrator.phase_manager.start_phase("phase1")
        orchestrator.phase_manager.complete_phase("phase1")
        orchestrator.phase_manager.start_phase("phase2")
        orchestrator.phase_manager.complete_phase("phase2")
        
        result = orchestrator.update_continuation_prompt(
            plan_name="test-plan",
            plan_id="test-123",
            plan_dir=plan_dir,
            current_phase={"number": 2, "name": "Phase 2"},
            next_phase={"number": 3, "name": "Phase 3"}
        )
        
        assert result is True
        
        content = (plan_dir / "tracking" / "CONTINUATION-PROMPT.md").read_text(encoding="utf-8")
        assert "2/3 phases" in content
        assert "66%" in content or "67%" in content  # Allow rounding difference
    
    def test_continuation_prompt_disabled(self, plan_dir):
        """Test that continuation prompt respects disabled config."""
        orchestrator = TestOrchestrator(
            name="test_disabled",
            config={"continuation_prompt_enabled": False}
        )
        
        orchestrator._register_phases()
        
        result = orchestrator.update_continuation_prompt(
            plan_name="test-plan",
            plan_id="test-123",
            plan_dir=plan_dir,
            current_phase={"number": 1, "name": "Phase 1"},
            next_phase={"number": 2, "name": "Phase 2"}
        )
        
        assert result is False
        assert not (plan_dir / "tracking" / "CONTINUATION-PROMPT.md").exists()
    
    def test_continuation_prompt_includes_artifacts(self, orchestrator, plan_dir):
        """Test that continuation prompt shows artifact count."""
        orchestrator._register_phases()
        orchestrator.phase_manager.start_phase("phase1")
        orchestrator.phase_manager.complete_phase("phase1")
        
        result = orchestrator.update_continuation_prompt(
            plan_name="test-plan",
            plan_id="test-123",
            plan_dir=plan_dir,
            current_phase={"number": 1, "name": "Phase 1"},
            next_phase={"number": 2, "name": "Phase 2"}
        )
        
        assert result is True
        
        content = (plan_dir / "tracking" / "CONTINUATION-PROMPT.md").read_text(encoding="utf-8")
        assert "Artifacts Generated:** 2" in content


class TestTokenUsageMonitoring:
    """Test token usage estimation and warning system."""
    
    def test_check_token_usage_below_threshold(self, orchestrator):
        """Test token usage check when below threshold."""
        orchestrator._register_phases()
        orchestrator.phase_manager.start_phase("phase1")
        orchestrator.phase_manager.complete_phase("phase1")
        
        result = orchestrator.check_token_usage()
        
        assert result["estimated_tokens"] == 1000  # 1 phase * 1000
        assert result["threshold"] == 80000
        assert result["should_warn"] is False
        assert result["percentage"] < 2
    
    def test_check_token_usage_above_threshold(self):
        """Test token usage check when above threshold."""
        # Create orchestrator with low threshold
        orchestrator = TestOrchestrator(
            name="test_threshold",
            config={"token_warning_threshold": 2000}
        )
        
        orchestrator._register_phases()
        
        # Complete all 3 phases (3000 tokens estimated)
        for phase in ["phase1", "phase2", "phase3"]:
            orchestrator.phase_manager.start_phase(phase)
            orchestrator.phase_manager.complete_phase(phase)
        
        result = orchestrator.check_token_usage()
        
        assert result["estimated_tokens"] == 3000
        assert result["threshold"] == 2000
        assert result["should_warn"] is True
        assert result["percentage"] == 150.0
    
    def test_estimate_tokens_heuristic(self, orchestrator):
        """Test token estimation heuristic."""
        orchestrator._register_phases()
        
        # Complete 5 phases worth of work
        for i in range(5):
            phase_name = f"phase{i+1}"
            if i < 3:  # Only 3 phases registered
                orchestrator.phase_manager.start_phase(phase_name)
                orchestrator.phase_manager.complete_phase(phase_name)
        
        # Text estimation
        sample_text = "This is a test " * 100  # ~1600 characters
        estimated = orchestrator._estimate_tokens(sample_text)
        
        assert estimated == len(sample_text) // 4
        assert 350 < estimated < 450  # Should be around 400 tokens
    
    def test_estimate_tokens_empty_text(self, orchestrator):
        """Test token estimation with empty text falls back to phase count."""
        orchestrator._register_phases()
        orchestrator.phase_manager.start_phase("phase1")
        orchestrator.phase_manager.complete_phase("phase1")
        orchestrator.phase_manager.start_phase("phase2")
        orchestrator.phase_manager.complete_phase("phase2")
        
        estimated = orchestrator._estimate_tokens("")
        
        assert estimated == 2000  # 2 completed phases * 1000


class TestGitCheckpoints:
    """Test git checkpoint retrieval."""
    
    def test_get_git_checkpoints(self, orchestrator):
        """Test retrieval of git checkpoints."""
        checkpoints = orchestrator._get_git_checkpoints(limit=3)
        
        # Should return list (may be empty if no git repo)
        assert isinstance(checkpoints, list)
        
        # If we have checkpoints, verify structure
        if checkpoints:
            assert len(checkpoints) <= 3
            for checkpoint in checkpoints:
                assert "hash" in checkpoint
                assert "message" in checkpoint
                assert "date" in checkpoint
                assert len(checkpoint["hash"]) >= 7  # Short hash
    
    def test_get_git_checkpoints_limit(self, orchestrator):
        """Test that checkpoint limit is respected."""
        checkpoints = orchestrator._get_git_checkpoints(limit=1)
        
        if checkpoints:  # Only test if git available
            assert len(checkpoints) <= 1


class TestSessionManagementIntegration:
    """Integration tests for session management workflow."""
    
    def test_full_session_handoff_workflow(self, orchestrator, plan_dir):
        """Test complete session handoff workflow."""
        # Setup
        orchestrator._register_phases()
        
        # Execute first phase
        orchestrator.phase_manager.start_phase("phase1")
        orchestrator.phase_manager.complete_phase("phase1")
        
        # Check token usage (should be low)
        token_status = orchestrator.check_token_usage()
        assert token_status["should_warn"] is False
        
        # Generate continuation prompt
        prompt_created = orchestrator.update_continuation_prompt(
            plan_name="integration-test-plan",
            plan_id="int-test-123",
            plan_dir=plan_dir,
            current_phase={"number": 1, "name": "Phase 1", "duration": "2h"},
            next_phase={"number": 2, "name": "Phase 2", "duration": "3h"}
        )
        
        assert prompt_created is True
        
        # Verify prompt contains all necessary information
        prompt_file = plan_dir / "tracking" / "CONTINUATION-PROMPT.md"
        content = prompt_file.read_text(encoding="utf-8")
        
        # Check for key sections
        assert "Session Continuation Prompt" in content
        assert "Quick Context" in content
        assert "Continuation Instructions" in content
        assert "State Summary" in content
        assert "Important Notes" in content
        
        # Check for specific data
        assert "integration-test-plan" in content
        assert "int-test-123" in content
        assert "1/3 phases" in content
        assert "Phase 1" in content
        assert "Phase 2" in content
        
        # Check for copy-paste prompt
        assert "Follow instructions in .github/prompts/CORTEX.prompt.md" in content
        assert "PlanningStateMCP" in content or "get_plan_status" in content
    
    def test_session_handoff_at_plan_completion(self, orchestrator, plan_dir):
        """Test continuation prompt when plan is complete."""
        orchestrator._register_phases()
        
        # Complete all phases
        for phase in ["phase1", "phase2", "phase3"]:
            orchestrator.phase_manager.start_phase(phase)
            orchestrator.phase_manager.complete_phase(phase)
        
        # Generate continuation prompt with no next phase
        result = orchestrator.update_continuation_prompt(
            plan_name="completed-plan",
            plan_id="complete-123",
            plan_dir=plan_dir,
            current_phase={"number": 3, "name": "Phase 3"},
            next_phase=None
        )
        
        assert result is True
        
        content = (plan_dir / "tracking" / "CONTINUATION-PROMPT.md").read_text(encoding="utf-8")
        assert "3/3 phases" in content
        assert "100%" in content
        assert "Plan Complete" in content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
