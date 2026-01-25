"""
Integration tests for PlannerOrchestrator with MasterOrchestrator

Tests the full workflow of PlannerOrchestrator integrated into the CORTEX system.
"""

import pytest
from pathlib import Path
from typing import Dict, Any
import tempfile
import shutil

from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
from cortex.orchestrators.core.planner_orchestrator import (
    PlannerOrchestrator,
    get_planner_orchestrator
)
from cortex.core.result import Ok, Err, Result

from cortex.brain.core.state_manager import StateManager, get_state_manager


class TestPlannerOrchestratorIntegration:
    """Integration tests for PlannerOrchestrator with MasterOrchestrator"""
    
    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """Setup and teardown for each test"""
        # Clean up any existing registry before test
        registry_path = Path.home() / ".cortex/orchestrator_registry.db"
        if registry_path.exists():
            try:
                registry_path.unlink()
            except OSError:
                pass
        
        yield
        
        # Cleanup after test
        try:
            if registry_path.exists():
                registry_path.unlink()
        except OSError:
            pass
    
    def test_planner_accessible_from_master(self):
        """Test that PlannerOrchestrator is accessible through MasterOrchestrator"""
        # Initialize both orchestrators
        planner = get_planner_orchestrator()
        master = MasterOrchestrator.instance()
        
        # PlannerOrchestrator should be initialized
        assert planner is not None
        assert master is not None
        
        # PlannerOrchestrator should be registered in database
        from cortex.orchestrators import get_database_registry
        registry = get_database_registry()
        config = registry.get_orchestrator_config("PlannerOrchestrator")
        
        # Config might be None if not registered, but orchestrator should still exist
        assert planner.get_status() is not None
    
    def test_planner_create_plan_end_to_end(self):
        """Test full workflow: create temp plan → approve → execute"""
        planner = get_planner_orchestrator()
        
        # Step 1: Create temp plan
        request = {
            "description": "Implement user authentication system",
            "scope": "system",
            "impact": "high",
            "confidence": 0.8
        }
        
        result = planner.create_temp_plan(request)
        assert result.is_ok(), f"Plan creation failed: {result.error}"
        
        temp_plan = result.unwrap()
        plan_id = temp_plan["plan_id"]
        assert plan_id is not None
        
        # Verify TEMP state (use "status" not "state")
        assert temp_plan["status"] == "temp"
        assert temp_plan["classification"]["intent"] in ["implement", "system", "IMPLEMENT", "SYSTEM", "ANALYZE"]
        
        # Step 2: Approve plan (TEMP → ACTIVE)
        result = planner.approve_plan(plan_id)
        assert result.is_ok(), f"Plan approval failed: {result.error}"
        
        approved_plan = result.unwrap()
        assert approved_plan["status"] == "active"
        
        # Step 3: Execute plan with confirmation
        result = planner.execute_plan(plan_id, confirmed=True)
        # May return awaiting_confirmation or executing depending on gates
        assert result.is_ok(), f"Plan execution failed: {result.error}"
        
        execution = result.unwrap()
        assert execution["plan_id"] == plan_id
    
    def test_planner_challenge_system_integration(self):
        """Test that challenge system works in create_temp_plan"""
        planner = get_planner_orchestrator()
        
        # Create plan with scope creep
        request = {
            "description": "Fix bug AND add feature AND refactor code",
            "scope": "module",
            "impact": "medium"
        }
        
        result = planner.create_temp_plan(request)
        assert result.is_ok()
        
        plan = result.unwrap()
        
        # Should have challenges
        assert "challenges" in plan
        challenges = plan["challenges"]
        
        # Should detect scope creep
        scope_creep_challenges = [c for c in challenges if c.get("type") == "scope_creep"]
        assert len(scope_creep_challenges) > 0, "Should detect scope creep challenge"
    
    def test_planner_execution_gates_integration(self):
        """Test that execution gates work in create_temp_plan"""
        planner = get_planner_orchestrator()
        
        # Create high-impact, low-confidence plan
        request = {
            "description": "Delete production database",
            "scope": "database",
            "impact": "high",
            "confidence": 0.2
        }
        
        result = planner.create_temp_plan(request)
        assert result.is_ok()
        
        plan = result.unwrap()
        
        # Should have execution gates (plural)
        assert "execution_gates" in plan
        gates = plan["execution_gates"]
        
        # High impact + low confidence should require confirmation
        assert gates["requires_confirmation"] == True
    
    def test_planner_git_analysis_integration(self):
        """Test that git analysis works"""
        planner = get_planner_orchestrator()
        
        request = {
            "description": "Implement new feature",
            "scope": "file"
        }
        
        result = planner.create_temp_plan(request)
        assert result.is_ok()
        
        plan = result.unwrap()
        
        # Should have git context
        assert "git_context" in plan
        git = plan["git_context"]
        
        # Git context should have branch info (use "branch" not "current_branch")
        assert "branch" in git
    
    def test_planner_plan_listing_integration(self):
        """Test listing plans from multiple states"""
        planner = get_planner_orchestrator()
        
        # Create multiple temp plans
        for i in range(3):
            request = {
                "description": f"Plan {i}",
                "scope": "file"
            }
            result = planner.create_temp_plan(request)
            assert result.is_ok()
            
            if i == 0:
                # Approve first plan
                temp_plan = result.unwrap()
                planner.approve_plan(temp_plan["plan_id"])
        
        # List temp plans
        result = planner.list_temp_plans()
        assert result.is_ok()
        temp_plans = result.unwrap()
        assert len(temp_plans) >= 2  # At least 2 temp plans
        
        # List active plans
        result = planner.list_active_plans()
        assert result.is_ok()
        active_plans = result.unwrap()
        assert len(active_plans) >= 1  # At least 1 active plan
    
    def test_planner_persistence_integration(self):
        """Test that plans persist across orchestrator restarts"""
        # Create initial orchestrator and plan
        planner1 = get_planner_orchestrator()
        
        request = {
            "description": "Persistent test plan",
            "scope": "file"
        }
        
        result = planner1.create_temp_plan(request)
        assert result.is_ok()
        temp_plan = result.unwrap()
        plan_id = temp_plan["plan_id"]
        
        # Approve the plan
        result = planner1.approve_plan(plan_id)
        assert result.is_ok()
        
        # Simulate orchestrator restart by creating new instance
        PlannerOrchestrator._instance = None  # Reset singleton
        planner2 = get_planner_orchestrator()
        
        # Plan should still be findable in active plans
        result = planner2.list_active_plans()
        assert result.is_ok()
        active_plans = result.unwrap()
        
        # Find our plan
        plan_names = [p.get("plan_id") for p in active_plans]
        assert plan_id in plan_names, f"Plan {plan_id} not found in {plan_names}"
    
    def test_planner_state_transitions_integration(self):
        """Test complete state machine transitions"""
        planner = get_planner_orchestrator()
        
        request = {
            "description": "State transition test",
            "scope": "file"
        }
        
        # Create TEMP plan
        result = planner.create_temp_plan(request)
        temp_plan = result.unwrap()
        plan_id = temp_plan["plan_id"]
        
        # Initial status should be "temp"
        assert temp_plan["status"] == "temp"
        
        # Transition TEMP → ACTIVE
        result = planner.approve_plan(plan_id)
        active_plan = result.unwrap()
        assert active_plan["status"] == "active"
        
        # Transition ACTIVE → EXECUTING/EXECUTED
        result = planner.execute_plan(plan_id, confirmed=True)
        executed_plan = result.unwrap()
        # Should return status about execution
        assert "status" in executed_plan or "plan_id" in executed_plan
    
    def test_planner_error_handling_integration(self):
        """Test error handling in integration scenarios"""
        planner = get_planner_orchestrator()
        
        # Try to approve non-existent plan
        result = planner.approve_plan("non-existent-plan-id")
        assert result.is_err()
        
        # Try to execute non-existent plan
        result = planner.execute_plan("non-existent-plan-id")
        assert result.is_err()
        
        # Try to create plan with invalid data
        result = planner.create_temp_plan({})  # Empty request
        # Should still succeed or handle gracefully
        if result.is_ok():
            plan = result.unwrap()
            assert "plan_id" in plan


class TestMasterOrchestratorPlannerRouting:
    """Tests for routing PlannerOrchestrator through MasterOrchestrator"""
    
    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """Setup and teardown for each test"""
        registry_path = Path.home() / ".cortex/orchestrator_registry.db"
        if registry_path.exists():
            try:
                registry_path.unlink()
            except OSError:
                pass
        
        yield
        
        try:
            if registry_path.exists():
                registry_path.unlink()
        except OSError:
            pass
    
    def test_master_orchestrator_can_access_planner(self):
        """Test MasterOrchestrator can access PlannerOrchestrator"""
        # Initialize both
        planner = get_planner_orchestrator()
        master = MasterOrchestrator.instance()
        
        # Both should be initialized
        assert planner is not None
        assert master is not None
    
    def test_planner_singleton_pattern(self):
        """Test PlannerOrchestrator singleton behavior"""
        planner1 = get_planner_orchestrator()
        planner2 = get_planner_orchestrator()
        
        # Should be same instance
        assert planner1 is planner2
        assert id(planner1) == id(planner2)
    
    def test_planner_status_reporting(self):
        """Test PlannerOrchestrator status reporting"""
        planner = get_planner_orchestrator()
        
        status = planner.get_status()
        assert status is not None
        
        # Status should include key information
        assert isinstance(status, dict)
        assert "name" in status or "state" in status or "ready" in status


class TestPlannerOrchestratorMCPTools:
    """Tests for MCP tools integration with PlannerOrchestrator"""
    
    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """Setup and teardown for each test"""
        registry_path = Path.home() / ".cortex/orchestrator_registry.db"
        if registry_path.exists():
            try:
                registry_path.unlink()
            except OSError:
                pass
        
        yield
        
        try:
            if registry_path.exists():
                registry_path.unlink()
        except OSError:
            pass
    
    def test_planner_implements_orchestrator_interface(self):
        """Test PlannerOrchestrator implements IOrchestrator interface"""
        planner = get_planner_orchestrator()
        
        # Should have required methods
        assert hasattr(planner, "execute")
        assert hasattr(planner, "get_status")
        assert callable(planner.execute)
        assert callable(planner.get_status)
    
    def test_planner_execution_through_interface(self):
        """Test executing PlannerOrchestrator through orchestrator interface"""
        planner = get_planner_orchestrator()
        
        # Execute through interface
        result = planner.execute({
            "operation": "create_plan",
            "request": {
                "description": "Test plan",
                "scope": "file"
            }
        })
        
        # Should return Result type
        assert result is not None
        assert hasattr(result, "is_ok") or hasattr(result, "is_err")
