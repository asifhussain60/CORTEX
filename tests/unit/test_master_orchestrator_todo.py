"""
Tests for Master Orchestrator - TODO Integration
================================================
Tests integration between Master Orchestrator and TODO Orchestrator.

Author: GitHub Copilot (for CORTEX)
Created: 2026-01-08
Feature: feat04-core-orchestration
Phase: 2 Task: 2.1
TDD Phase: RED
"""

import pytest
from pathlib import Path
from src.orchestrators.core.master_orchestrator import MasterOrchestrator
from src.orchestrators.core.todo_orchestrator import TodoOrchestrator
from src.orchestrators.middleware.orchestrator_lifecycle import LifecycleState


class TestMasterOrchestratorTODOIntegration:
    """Test Master Orchestrator TODO integration"""
    
    @pytest.fixture
    def master(self, tmp_path):
        """Create master orchestrator"""
        return MasterOrchestrator(workspace_root=tmp_path)
    
    def test_master_registers_todo_orchestrator(self, master):
        """Should register TODO orchestrator"""
        assert master.has_orchestrator("todo")
        todo_orch = master.get_orchestrator("todo")
        assert isinstance(todo_orch, TodoOrchestrator)
    
    def test_master_can_delegate_to_todo(self, master):
        """Should delegate TODO operations to TODO orchestrator"""
        result = master.execute("create todo: Test task")
        assert result.success is True
        assert result.orchestrator == "todo"
    
    def test_master_tracks_todo_lifecycle(self, master):
        """Should track TODO orchestrator lifecycle"""
        todo = master.get_orchestrator("todo")
        lifecycle = master.get_lifecycle("todo")
        
        assert lifecycle.current_state == LifecycleState.READY
    
    def test_master_handles_todo_errors(self, master, tmp_path):
        """Should handle TODO orchestrator errors gracefully"""
        # Create invalid TODO request
        result = master.execute("create todo with invalid syntax")
        
        assert result.success is False
        assert result.error is not None
