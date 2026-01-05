"""
Test Suite for PlanningStateDB Wiring Fixes (Phase 24)

Tests method signature fixes for orchestrator integration:
- start_phase() dual-signature support (phase_id OR plan_id+phase_number)
- update_plan_status() method implementation
- Base orchestrator v4.1 integration

TDD Cycle: RED → GREEN → REFACTOR
Phase: Phase 24 (PlanningStateDB Method Signatures)
"""

import pytest
import tempfile
import os
from pathlib import Path
from src.database.planning_state_db import PlanningStateDB


class TestPlanningStateDBStartPhase:
    """Test start_phase() dual-signature support."""
    
    @pytest.fixture
    def state_db(self):
        """Create temporary database for testing."""
        db_path = tempfile.mktemp(suffix='.db')
        db = PlanningStateDB(db_path=db_path)
        yield db
        db.close()
        if os.path.exists(db_path):
            os.remove(db_path)
    
    def test_start_phase_with_phase_id_only(self, state_db):
        """
        RED: Test Pattern 1 - start_phase(phase_id="phase-123")
        Updates existing phase to in_progress status.
        """
        # Setup: Create a plan and phase
        plan_id = state_db.create_plan(
            feature_name="test-feature",
            complexity_tier=1,
            strategy="test"
        )
        
        phase_id = state_db.create_phase(
            plan_id=plan_id,
            phase_number=1,
            name="Test Phase"
        )
        
        # Test: Start phase using phase_id only
        result_phase_id = state_db.start_phase(phase_id=phase_id)
        
        assert result_phase_id == phase_id, \
            f"Should return same phase_id, got {result_phase_id}"
        
        # Verify phase status updated
        phase = state_db.get_phase(phase_id)
        assert phase['status'] == 'in_progress', \
            f"Phase status should be in_progress, got {phase['status']}"
        assert phase['started_at'] is not None, \
            "Phase should have started_at timestamp"
    
    def test_start_phase_with_plan_id_and_phase_number(self, state_db):
        """
        RED: Test Pattern 2 - start_phase(plan_id="plan-456", phase_number=1, config={})
        Creates new phase AND starts it in one call.
        """
        # Setup: Create a plan
        plan_id = state_db.create_plan(
            feature_name="test-feature",
            complexity_tier=1,
            strategy="test"
        )
        
        # Test: Create and start phase in one call
        phase_config = {
            'name': 'Auto-created Phase',
            'description': 'Test auto-creation',
            'estimated_hours': 2.0
        }
        
        phase_id = state_db.start_phase(
            plan_id=plan_id,
            phase_number=1,
            config=phase_config
        )
        
        assert phase_id is not None, "Should return phase_id"
        assert phase_id.startswith('phase-'), \
            f"Phase ID should have 'phase-' prefix, got {phase_id}"
        
        # Verify phase created AND started
        phase = state_db.get_phase(phase_id)
        assert phase is not None, "Phase should exist"
        assert phase['status'] == 'in_progress', \
            f"Phase should be in_progress, got {phase['status']}"
        assert phase['started_at'] is not None, \
            "Phase should have started_at timestamp"
        assert phase['name'] == 'Auto-created Phase', \
            f"Phase name should be from config, got {phase['name']}"
    
    def test_start_phase_requires_either_pattern(self, state_db):
        """RED: Test that start_phase raises error if neither pattern provided."""
        with pytest.raises(ValueError, match="Must provide either phase_id OR"):
            state_db.start_phase()  # No arguments
    
    def test_start_phase_base_orchestrator_pattern(self, state_db):
        """
        RED: Test exact pattern used by base_orchestrator_v4_1.py line 277:
        phase_id = self.state_db.start_phase(
            plan_id=self.plan_id,
            phase_number=phase_number,
            config=phase_config
        )
        """
        # Setup: Create plan
        plan_id = state_db.create_plan(
            feature_name="orchestrator-test",
            complexity_tier=2,
            strategy="feature"
        )
        
        # Test: Use exact orchestrator pattern
        phase_config = {
            'name': 'Phase 1',
            'description': 'First phase',
            'estimated_hours': 3.0,
            'python_executor': 'scripts/phase_1.py'
        }
        
        phase_id = state_db.start_phase(
            plan_id=plan_id,
            phase_number=1,
            config=phase_config
        )
        
        # Verify orchestrator expectations met
        assert isinstance(phase_id, str), \
            f"Orchestrator expects string phase_id, got {type(phase_id)}"
        assert len(phase_id) > 0, "Phase ID should not be empty"
        
        # Verify phase accessible
        phase = state_db.get_phase(phase_id)
        assert phase['plan_id'] == plan_id
        assert phase['phase_number'] == 1
        assert phase['status'] == 'in_progress'


class TestPlanningStateDBUpdatePlanStatus:
    """Test update_plan_status() method (currently missing)."""
    
    @pytest.fixture
    def state_db(self):
        """Create temporary database for testing."""
        db_path = tempfile.mktemp(suffix='.db')
        db = PlanningStateDB(db_path=db_path)
        yield db
        db.close()
        if os.path.exists(db_path):
            os.remove(db_path)
    
    def test_update_plan_status_method_exists(self, state_db):
        """RED: Test that update_plan_status method exists."""
        assert hasattr(state_db, 'update_plan_status'), \
            "PlanningStateDB should have update_plan_status method"
        assert callable(state_db.update_plan_status), \
            "update_plan_status should be callable"
    
    def test_update_plan_status_to_completed(self, state_db):
        """RED: Test updating plan status to completed."""
        # Setup: Create plan
        plan_id = state_db.create_plan(
            feature_name="test-plan",
            complexity_tier=1,
            strategy="test"
        )
        
        # Start the plan
        state_db.start_plan(plan_id)
        
        # Test: Update to completed
        result = state_db.update_plan_status(plan_id, 'completed')
        assert result is True, "Should return True on successful update"
        
        # Verify status updated
        plan = state_db.get_plan(plan_id)
        assert plan['status'] == 'completed', \
            f"Plan status should be completed, got {plan['status']}"
        assert plan['completed_at'] is not None, \
            "Plan should have completed_at timestamp"
    
    def test_update_plan_status_to_failed(self, state_db):
        """RED: Test updating plan status to failed."""
        # Setup: Create and start plan
        plan_id = state_db.create_plan(
            feature_name="test-plan",
            complexity_tier=1,
            strategy="test"
        )
        state_db.start_plan(plan_id)
        
        # Test: Update to failed
        result = state_db.update_plan_status(plan_id, 'failed')
        assert result is True, "Should return True on successful update"
        
        # Verify status updated
        plan = state_db.get_plan(plan_id)
        assert plan['status'] == 'failed', \
            f"Plan status should be failed, got {plan['status']}"
    
    def test_update_plan_status_to_paused(self, state_db):
        """RED: Test updating plan status to paused."""
        # Setup: Create and start plan
        plan_id = state_db.create_plan(
            feature_name="test-plan",
            complexity_tier=1,
            strategy="test"
        )
        state_db.start_plan(plan_id)
        
        # Test: Update to paused
        result = state_db.update_plan_status(plan_id, 'paused')
        assert result is True, "Should return True on successful update"
        
        # Verify status updated
        plan = state_db.get_plan(plan_id)
        assert plan['status'] == 'paused', \
            f"Plan status should be paused, got {plan['status']}"
    
    def test_update_plan_status_invalid_status(self, state_db):
        """RED: Test that invalid status raises error."""
        # Setup: Create plan
        plan_id = state_db.create_plan(
            feature_name="test-plan",
            complexity_tier=1,
            strategy="test"
        )
        
        # Test: Invalid status should raise error
        with pytest.raises(ValueError, match="Invalid status"):
            state_db.update_plan_status(plan_id, 'invalid_status')
    
    def test_update_plan_status_planning_orchestrator_pattern(self, state_db):
        """
        RED: Test exact pattern used by planning_orchestrator_v5.py:
        - Line 301: self.state_db.update_plan_status(self.plan_id, 'completed')
        - Line 343: self.state_db.update_plan_status(self.plan_id, 'failed')
        """
        # Setup: Create plan
        plan_id = state_db.create_plan(
            feature_name="orchestrator-test",
            complexity_tier=3,
            strategy="feature"
        )
        state_db.start_plan(plan_id)
        
        # Test: Planning orchestrator success pattern
        state_db.update_plan_status(plan_id, 'completed')
        plan = state_db.get_plan(plan_id)
        assert plan['status'] == 'completed'
        
        # Create another plan for failure pattern
        plan_id_2 = state_db.create_plan(
            feature_name="failed-plan",
            complexity_tier=1,
            strategy="test"
        )
        state_db.start_plan(plan_id_2)
        
        # Test: Planning orchestrator failure pattern
        state_db.update_plan_status(plan_id_2, 'failed')
        plan2 = state_db.get_plan(plan_id_2)
        assert plan2['status'] == 'failed'


class TestBaseOrchestratorIntegration:
    """Test integration with base orchestrator v4.1."""
    
    @pytest.fixture
    def state_db(self):
        """Create temporary database for testing."""
        db_path = tempfile.mktemp(suffix='.db')
        db = PlanningStateDB(db_path=db_path)
        yield db
        db.close()
        if os.path.exists(db_path):
            os.remove(db_path)
    
    def test_orchestrator_workflow_simulation(self, state_db):
        """
        RED: Simulate full base orchestrator workflow:
        1. Create plan
        2. Start plan
        3. Start phase (create + start in one call)
        4. Complete phase
        5. Update plan status
        """
        # Step 1: Create plan
        plan_id = state_db.create_plan(
            feature_name="full-workflow-test",
            complexity_tier=2,
            strategy="feature"
        )
        
        # Step 2: Start plan
        state_db.start_plan(plan_id)
        
        # Step 3: Start phase (orchestrator pattern)
        phase_config = {
            'name': 'Setup Verification',
            'description': 'Verify environment',
            'estimated_hours': 0.5
        }
        phase_id = state_db.start_phase(
            plan_id=plan_id,
            phase_number=-2,
            config=phase_config
        )
        
        assert phase_id is not None, "Phase should be created and started"
        
        # Step 4: Complete phase
        phase_result = {'success': True, 'output': 'Environment verified'}
        success = state_db.complete_phase(phase_id, result=phase_result)
        assert success is True, "Phase should complete successfully"
        
        # Step 5: Update plan status
        state_db.update_plan_status(plan_id, 'completed')
        
        # Verify final state
        plan = state_db.get_plan(plan_id)
        assert plan['status'] == 'completed', "Plan should be completed"
        
        phase = state_db.get_phase(phase_id)
        assert phase['status'] == 'completed', "Phase should be completed"


# TDD Summary
"""
Phase 24 Test Coverage:

✅ start_phase() Dual-Signature (5 tests)
   - Pattern 1: phase_id only
   - Pattern 2: plan_id + phase_number + config
   - Error handling for invalid arguments
   - Base orchestrator integration pattern
   - Phase creation and start in one call

✅ update_plan_status() Method (6 tests)
   - Method exists and callable
   - Update to 'completed'
   - Update to 'failed'
   - Update to 'paused'
   - Invalid status error handling
   - Planning orchestrator pattern

✅ Base Orchestrator Integration (1 test)
   - Full workflow simulation

TOTAL: 12 tests
EXPECTED: Some RED (update_plan_status not yet implemented)
NEXT: Implement missing method to make tests GREEN
"""
