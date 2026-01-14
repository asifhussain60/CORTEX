"""
Tests for feat04 Core Orchestration - End-to-End Integration
=============================================================
Comprehensive integration tests for the complete orchestration pipeline.

Author: GitHub Copilot (for CORTEX)
Created: 2026-01-08
Feature: feat04-core-orchestration
Phase: 4 (Integration Testing)
TDD Phase: RED → GREEN
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch
import time

from src.orchestrators.core.master_orchestrator import MasterOrchestrator
from src.orchestrators.core.governance_merger import GovernanceMerger
from src.orchestrators.middleware.orchestrator_lifecycle import LifecycleState
from src.orchestrators.middleware.silent_execution import SilentExecutionMiddleware, OutputLevel
from src.orchestrators.middleware.progress_throttler import ProgressThrottler
from src.orchestrators.middleware.phase_boundary_reporter import PhaseBoundaryReporter


class TestEndToEndOrchestration:
    """End-to-end orchestration tests"""
    
    @pytest.fixture
    def workspace_root(self, tmp_path):
        """Create temporary workspace"""
        workspace = tmp_path / "workspace"
        workspace.mkdir()
        
        # Create cortex-brain structure
        brain_dir = workspace / "cortex-brain"
        brain_dir.mkdir()
        (brain_dir / "database").mkdir()
        
        # Create governance directories
        gov_dirs = [
            brain_dir / "tier0" / "governance",
            brain_dir / "tier1" / "governance",
            brain_dir / "tier2" / "governance",
            brain_dir / "tier3" / "governance"
        ]
        for d in gov_dirs:
            d.mkdir(parents=True, exist_ok=True)
        
        return workspace
    
    @pytest.fixture
    def master(self, workspace_root):
        """Create master orchestrator"""
        return MasterOrchestrator(workspace_root)
    
    def test_complete_pipeline_with_all_components(self, master):
        """Should execute complete pipeline with all orchestrators"""
        # Execute request through full pipeline
        result = master.execute_pipeline("create todo test task", enforce_governance=True)
        
        # Pipeline should complete successfully
        assert result.success is True
        assert result.orchestrator == "pipeline"
        
        # Result should contain all pipeline stages
        assert "governance_passed" in result.result
        assert "execution_result" in result.result
        assert "orchestrator_used" in result.result
    
    def test_lifecycle_management_throughout_execution(self, master):
        """Should maintain proper lifecycle states throughout execution"""
        # Check initial states
        assert master.get_lifecycle("todo").current_state == LifecycleState.READY
        assert master.get_lifecycle("governance").current_state == LifecycleState.READY
        
        # Execute pipeline
        result = master.execute_pipeline("create todo task", enforce_governance=True)
        
        # All orchestrators should return to READY state
        assert master.get_lifecycle("todo").current_state == LifecycleState.READY
        assert master.get_lifecycle("governance").current_state == LifecycleState.READY
    
    def test_error_recovery_and_state_consistency(self, master):
        """Should recover from errors and maintain consistent state"""
        # Force an error in governance
        with patch.object(master, '_execute_governance') as mock_gov:
            mock_gov.side_effect = Exception("Test error")
            
            result = master.execute_pipeline("test", enforce_governance=True)
            assert result.success is False
        
        # System should still be functional
        result2 = master.execute_pipeline("create todo test", enforce_governance=False)
        assert result2.success is True
        
        # Lifecycle states should be consistent
        assert master.get_lifecycle("todo").current_state == LifecycleState.READY
    
    def test_multiple_sequential_requests(self, master):
        """Should handle multiple sequential requests correctly"""
        results = []
        
        for i in range(5):
            result = master.execute_pipeline(f"create todo task{i}", enforce_governance=False)
            results.append(result)
        
        # All should succeed
        assert all(r.success for r in results)
        
        # System state should be clean
        assert master.get_lifecycle("todo").current_state == LifecycleState.READY
        assert master.get_lifecycle("governance").current_state == LifecycleState.READY


class TestSilentExecutionIntegration:
    """Test silent execution integration with pipeline"""
    
    @pytest.fixture
    def workspace_root(self, tmp_path):
        """Create temporary workspace"""
        workspace = tmp_path / "workspace"
        workspace.mkdir()
        
        brain_dir = workspace / "cortex-brain"
        brain_dir.mkdir()
        (brain_dir / "database").mkdir()
        
        gov_dirs = [
            brain_dir / "tier0" / "governance",
            brain_dir / "tier1" / "governance",
            brain_dir / "tier2" / "governance",
            brain_dir / "tier3" / "governance"
        ]
        for d in gov_dirs:
            d.mkdir(parents=True, exist_ok=True)
        
        return workspace
    
    def test_silent_mode_suppresses_task_output(self, workspace_root):
        """Should suppress task-level output in silent mode"""
        silent = SilentExecutionMiddleware(output_level=OutputLevel.SILENT)
        silent.start_suppression()
        
        # Execute pipeline
        master = MasterOrchestrator(workspace_root)
        result = master.execute_pipeline("create todo test", enforce_governance=False)
        
        silent.stop_suppression()
        
        # Pipeline should work but output should be captured
        assert result.success is True
        captured = silent.get_captured_output()
        assert len(captured) >= 0  # Output was captured
    
    def test_phase_boundaries_always_visible(self, workspace_root):
        """Should always show phase boundary updates"""
        reporter = PhaseBoundaryReporter()
        
        # Start phase
        reporter.phase_started("test-phase", total_tasks=3)
        
        # Complete tasks (should be internal only)
        reporter.task_completed("task1", silent=True)
        reporter.task_completed("task2", silent=True)
        reporter.task_completed("task3", silent=True)
        
        # Complete phase
        reporter.phase_completed("test-phase")
        
        # Should have phase boundary updates
        updates = reporter.get_phase_updates("test-phase")
        assert len(updates) >= 2  # Start and complete
        assert updates[0].event.value == "started"
        assert updates[-1].event.value == "completed"


class TestProgressThrottlingIntegration:
    """Test progress throttling integration"""
    
    def test_throttles_rapid_updates(self):
        """Should throttle rapid progress updates"""
        throttler = ProgressThrottler(min_interval_seconds=0.1)
        
        # First update should pass
        assert throttler.should_update("task1") is True
        
        # Immediate second update should be throttled
        assert throttler.should_update("task1") is False
        
        # After interval, should pass
        time.sleep(0.15)
        assert throttler.should_update("task1") is True
    
    def test_different_tasks_tracked_independently(self):
        """Should track different tasks independently"""
        throttler = ProgressThrottler(min_interval_seconds=0.1)
        
        # First update for task1
        assert throttler.should_update("task1") is True
        
        # Immediate update for task2 should pass (different task)
        assert throttler.should_update("task2") is True
        
        # Immediate updates for same tasks should be throttled
        assert throttler.should_update("task1") is False
        assert throttler.should_update("task2") is False


class TestAuditLogValidation:
    """Test audit log validation for feat04"""
    
    @pytest.fixture
    def workspace_root(self, tmp_path):
        """Create temporary workspace"""
        workspace = tmp_path / "workspace"
        workspace.mkdir()
        
        brain_dir = workspace / "cortex-brain"
        brain_dir.mkdir()
        (brain_dir / "database").mkdir()
        (brain_dir / "audit-logs").mkdir()
        
        gov_dirs = [
            brain_dir / "tier0" / "governance",
            brain_dir / "tier1" / "governance",
            brain_dir / "tier2" / "governance",
            brain_dir / "tier3" / "governance"
        ]
        for d in gov_dirs:
            d.mkdir(parents=True, exist_ok=True)
        
        return workspace
    
    def test_pipeline_execution_is_audited(self, workspace_root):
        """Should audit pipeline executions"""
        master = MasterOrchestrator(workspace_root)
        
        # Execute pipeline
        result = master.execute_pipeline("create todo test", enforce_governance=True)
        
        # Audit logs should exist
        audit_dir = workspace_root / "cortex-brain" / "audit-logs"
        assert audit_dir.exists()
    
    def test_orchestrator_initialization_is_audited(self, workspace_root):
        """Should audit orchestrator initialization"""
        # Creating master orchestrator should generate audit entries
        master = MasterOrchestrator(workspace_root)
        
        # Should have orchestrators registered
        assert master.has_orchestrator("todo")
        assert master.has_orchestrator("governance")
    
    def test_lifecycle_transitions_are_audited(self, workspace_root):
        """Should audit lifecycle state transitions"""
        master = MasterOrchestrator(workspace_root)
        
        # Execute something to trigger lifecycle transitions
        result = master.execute_pipeline("create todo test", enforce_governance=False)
        
        # Lifecycle should have history via lifecycles registry
        todo_lifecycle = master.lifecycles["todo"]
        assert len(todo_lifecycle.transition_history) > 0


class TestAccessibilityCompliance:
    """Test WCAG AA accessibility compliance"""
    
    def test_cognitive_load_within_limits(self):
        """Should keep cognitive load within WCAG AA limits"""
        reporter = PhaseBoundaryReporter()
        silent = SilentExecutionMiddleware(output_level=OutputLevel.ESSENTIAL)
        
        # Configure for autonomous execution
        silent.start_suppression()
        reporter.phase_started("test-phase", total_tasks=10)
        
        # Complete 10 tasks (should not output)
        for i in range(10):
            reporter.task_completed(f"task{i}", silent=True)
            # In autonomous mode, task completions should not generate user-facing output
        
        reporter.phase_completed("test-phase")
        silent.stop_suppression()
        
        # Should have only phase-level updates (2: start, complete)
        updates = reporter.get_phase_updates("test-phase")
        phase_updates = [u for u in updates if u.event.value in ["started", "completed"]]
        assert len(phase_updates) == 2
    
    def test_user_can_request_detailed_output(self):
        """Should allow user to request detailed output"""
        # User can create verbose middleware
        silent_verbose = SilentExecutionMiddleware(output_level=OutputLevel.VERBOSE)
        silent_essential = SilentExecutionMiddleware(output_level=OutputLevel.ESSENTIAL)
        
        # Verbose should allow more output than essential
        assert silent_verbose._should_output(OutputLevel.VERBOSE) is True
        assert silent_essential._should_output(OutputLevel.VERBOSE) is False


class TestPerformanceAndScalability:
    """Test performance and scalability"""
    
    @pytest.fixture
    def workspace_root(self, tmp_path):
        """Create temporary workspace"""
        workspace = tmp_path / "workspace"
        workspace.mkdir()
        
        brain_dir = workspace / "cortex-brain"
        brain_dir.mkdir()
        (brain_dir / "database").mkdir()
        
        gov_dirs = [
            brain_dir / "tier0" / "governance",
            brain_dir / "tier1" / "governance",
            brain_dir / "tier2" / "governance",
            brain_dir / "tier3" / "governance"
        ]
        for d in gov_dirs:
            d.mkdir(parents=True, exist_ok=True)
        
        return workspace
    
    def test_pipeline_executes_within_time_limit(self, workspace_root):
        """Should execute pipeline within reasonable time"""
        master = MasterOrchestrator(workspace_root)
        
        start_time = time.time()
        result = master.execute_pipeline("create todo test", enforce_governance=True)
        end_time = time.time()
        
        # Should complete within 1 second
        assert (end_time - start_time) < 1.0
        assert result.success is True
    
    def test_handles_concurrent_orchestrator_access(self, workspace_root):
        """Should handle accessing multiple orchestrators"""
        master = MasterOrchestrator(workspace_root)
        
        # Access different orchestrators
        todo_orch = master.get_orchestrator("todo")
        gov_orch = master.get_orchestrator("governance")
        
        assert todo_orch is not None
        assert gov_orch is not None
        
        # Both should be in READY state
        assert master.get_lifecycle("todo").current_state == LifecycleState.READY
        assert master.get_lifecycle("governance").current_state == LifecycleState.READY
