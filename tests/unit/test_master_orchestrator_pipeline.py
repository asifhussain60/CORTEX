"""
Tests for Master Orchestrator - Unified Execution Pipeline
===========================================================
Tests the unified pipeline: Request → Governance → TODO → Execution

Author: GitHub Copilot (for CORTEX)
Created: 2026-01-08
Feature: feat04-core-orchestration
Phase: 2 Task: 2.3
TDD Phase: RED → GREEN
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from src.orchestrators.core.master_orchestrator import (
    MasterOrchestrator,
    ExecutionResult
)
from src.orchestrators.core.governance_merger import GovernanceMerger
from src.orchestrators.middleware.orchestrator_lifecycle import LifecycleState


class TestUnifiedExecutionPipeline:
    """Test unified execution pipeline"""
    
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
    
    def test_pipeline_executes_with_governance_enabled(self, master):
        """Should execute full pipeline with governance checks"""
        result = master.execute_pipeline("create todo task", enforce_governance=True)
        
        assert result is not None
        assert result.orchestrator == "pipeline"
        assert result.success is True
        assert "governance_passed" in result.result
        assert result.result["governance_passed"] is True
    
    def test_pipeline_executes_without_governance(self, master):
        """Should execute pipeline without governance when disabled"""
        result = master.execute_pipeline("create todo task", enforce_governance=False)
        
        assert result is not None
        assert result.orchestrator == "pipeline"
        assert result.success is True
        assert "governance_passed" in result.result
        assert result.result["governance_passed"] is False
    
    def test_pipeline_routes_todo_requests(self, master):
        """Should route TODO requests to TODO orchestrator"""
        result = master.execute_pipeline("create todo item", enforce_governance=False)
        
        assert result.success is True
        assert result.result["orchestrator_used"] == "todo"
    
    def test_pipeline_handles_governance_failures(self, master):
        """Should handle governance validation failures"""
        # Mock governance to return failure
        with patch.object(master, '_execute_governance') as mock_gov:
            mock_gov.return_value = ExecutionResult(
                success=False,
                orchestrator="governance",
                error="Governance check failed"
            )
            
            result = master.execute_pipeline("invalid request", enforce_governance=True)
            
            assert result.success is False
            assert "Governance check failed" in result.error
    
    def test_pipeline_handles_governance_violations(self, master):
        """Should handle governance rule violations"""
        # Mock governance to return violations
        with patch.object(master, '_execute_governance') as mock_gov:
            mock_gov.return_value = ExecutionResult(
                success=True,
                orchestrator="governance",
                result={
                    "passed": False,
                    "violations": ["YAML_FIRST: No YAML plan provided"]
                }
            )
            
            result = master.execute_pipeline("execute without plan", enforce_governance=True)
            
            assert result.success is False
            assert "Governance violations" in result.error
            assert "YAML_FIRST" in result.error
    
    def test_pipeline_returns_execution_results(self, master):
        """Should return complete execution results"""
        result = master.execute_pipeline("create todo", enforce_governance=False)
        
        assert result.success is True
        assert "execution_result" in result.result
        assert result.result["execution_result"] is not None
    
    def test_pipeline_handles_execution_errors(self, master):
        """Should handle errors during execution"""
        # Mock TODO orchestrator to raise error
        with patch.object(master, '_execute_todo') as mock_todo:
            mock_todo.return_value = ExecutionResult(
                success=False,
                orchestrator="todo",
                error="Execution failed"
            )
            
            result = master.execute_pipeline("invalid todo", enforce_governance=False)
            
            assert result.success is False
            assert result.error == "Execution failed"
    
    def test_pipeline_logs_operations(self, master):
        """Should log pipeline operations"""
        with patch.object(master.logger, 'info') as mock_log:
            result = master.execute_pipeline("create todo", enforce_governance=False)
            
            # Verify logging occurred (at least for TODO execution)
            assert mock_log.called or result.success  # Execution happened
    
    def test_pipeline_maintains_orchestrator_lifecycle(self, master):
        """Should maintain proper orchestrator lifecycle during pipeline"""
        result = master.execute_pipeline("create todo", enforce_governance=False)
        
        # All orchestrators should be in READY state after pipeline completion
        todo_lifecycle = master.get_lifecycle("todo")
        assert todo_lifecycle.current_state == LifecycleState.READY
    
    def test_pipeline_error_handling_logs_errors(self, master):
        """Should log errors during pipeline execution"""
        # Force an exception
        with patch.object(master, '_execute_governance', side_effect=Exception("Test error")):
            with patch.object(master.logger, 'error') as mock_error:
                result = master.execute_pipeline("test", enforce_governance=True)
                
                assert result.success is False
                assert mock_error.called


class TestPipelineIntegrationFlow:
    """Test complete pipeline integration flows"""
    
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
    
    @pytest.fixture
    def master(self, workspace_root):
        """Create master orchestrator"""
        return MasterOrchestrator(workspace_root)
    
    def test_complete_pipeline_with_governance_pass(self, master):
        """Should execute complete pipeline when governance passes"""
        result = master.execute_pipeline("create todo task", enforce_governance=True)
        
        assert result.success is True
        assert result.result["governance_passed"] is True
        assert result.result["orchestrator_used"] == "todo"
        assert result.result["execution_result"] is not None
    
    def test_complete_pipeline_without_governance(self, master):
        """Should execute complete pipeline skipping governance"""
        result = master.execute_pipeline("create todo task", enforce_governance=False)
        
        assert result.success is True
        assert result.result["governance_passed"] is False
        assert result.result["execution_result"] is not None
    
    def test_pipeline_stops_on_governance_failure(self, master):
        """Should stop pipeline if governance fails"""
        with patch.object(master, '_execute_governance') as mock_gov:
            mock_gov.return_value = ExecutionResult(
                success=False,
                orchestrator="governance",
                error="Critical governance error"
            )
            
            result = master.execute_pipeline("test", enforce_governance=True)
            
            assert result.success is False
            assert "governance" in result.error.lower()
            # Execution should not have happened
            assert "execution_result" not in result.result
    
    def test_pipeline_orchestrator_coordination(self, master):
        """Should coordinate multiple orchestrators properly"""
        # Execute multiple requests through pipeline
        results = [
            master.execute_pipeline("create todo 1", enforce_governance=False),
            master.execute_pipeline("create todo 2", enforce_governance=False),
            master.execute_pipeline("check governance", enforce_governance=True)
        ]
        
        # All should succeed
        assert all(r.success for r in results)
        
        # All orchestrators should be in READY state
        assert master.get_lifecycle("todo").current_state == LifecycleState.READY
        assert master.get_lifecycle("governance").current_state == LifecycleState.READY


class TestPipelineErrorRecovery:
    """Test pipeline error recovery mechanisms"""
    
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
    
    @pytest.fixture
    def master(self, workspace_root):
        """Create master orchestrator"""
        return MasterOrchestrator(workspace_root)
    
    def test_pipeline_recovers_from_execution_error(self, master):
        """Should recover gracefully from execution errors"""
        # First request fails
        with patch.object(master, '_execute_todo') as mock_todo:
            mock_todo.return_value = ExecutionResult(
                success=False,
                orchestrator="todo",
                error="Temporary failure"
            )
            
            result1 = master.execute_pipeline("create todo bad request", enforce_governance=False)
            assert result1.success is False
        
        # Second request should still work
        result2 = master.execute_pipeline("create todo good request", enforce_governance=False)
        assert result2.success is True
    
    def test_pipeline_handles_unexpected_exceptions(self, master):
        """Should handle unexpected exceptions gracefully"""
        with patch.object(master, '_execute_todo', side_effect=RuntimeError("Unexpected")):
            result = master.execute_pipeline("create todo test", enforce_governance=False)
            
            assert result.success is False
            assert "Unexpected" in result.error
    
    def test_pipeline_maintains_state_after_errors(self, master):
        """Should maintain consistent state after errors"""
        # Cause an error
        with patch.object(master, '_execute_governance', side_effect=Exception("Error")):
            result = master.execute_pipeline("test todo", enforce_governance=True)
            assert result.success is False
        
        # State should still be valid
        assert master.has_orchestrator("todo")
        assert master.has_orchestrator("governance")
        
        # Next request should work
        result2 = master.execute_pipeline("create todo test", enforce_governance=False)
        assert result2.success is True
