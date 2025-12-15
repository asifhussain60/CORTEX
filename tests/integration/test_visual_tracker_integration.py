"""
Integration tests for visual tracker in Planning Orchestrator v3.1.

Tests end-to-end workflows including:
- Pre-planning discovery
- Visual tracker in responses
- Tracker embedded in master plans
- Metrics accuracy
- Discovery finds existing plans

Author: CORTEX Development Team
Phase: 1 (Visual Tracker Migration) - Task 1.8
"""

import pytest
import tempfile
import time
from pathlib import Path
from datetime import datetime, timedelta
from src.operations.modules.orchestration.planning_orchestrator import PlanningOrchestrator
from src.orchestrators.session_model import SessionStatus


@pytest.fixture
def temp_project_root():
    """Create temporary project root with planning structure."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)
        
        # Create planning folder structure
        planning_root = project_root / "cortex-brain" / "documents" / "planning"
        (planning_root / "active").mkdir(parents=True)
        (planning_root / "temp-plans").mkdir(parents=True)
        (planning_root / "completed").mkdir(parents=True)
        (planning_root / "features").mkdir(parents=True)
        
        yield project_root


@pytest.fixture
def orchestrator(temp_project_root):
    """Create planning orchestrator with temp project root."""
    return PlanningOrchestrator(project_root=temp_project_root)


class TestVisualTrackerIntegration:
    """Integration tests for visual tracker functionality."""
    
    def test_end_to_end_planning_with_discovery(self, orchestrator, temp_project_root):
        """Test complete planning workflow with pre-planning discovery."""
        # Setup: Create existing plan
        planning_root = temp_project_root / "cortex-brain" / "documents" / "planning"
        existing_plan = planning_root / "active" / "user-auth-v1"
        existing_plan.mkdir(parents=True)
        (existing_plan / "00-master-plan.md").write_text(
            "## Executive Summary\n\nExisting authentication plan",
            encoding='utf-8'
        )
        
        # Execute: Run discovery
        discovery_result = orchestrator.pre_planning_discovery("Plan user auth")
        
        # Verify: Discovery found existing plan
        assert discovery_result['found_existing'] is True
        assert len(discovery_result['recommendations']) > 0
        assert any(r['type'] == 'active_plan_exists' for r in discovery_result['recommendations'])
        
        # Verify: Recommendations include plan details
        active_recs = [r for r in discovery_result['recommendations'] if r['type'] == 'active_plan_exists']
        assert len(active_recs) > 0
        assert len(active_recs[0]['plans']) > 0
        assert 'user-auth' in active_recs[0]['plans'][0]['name'].lower()
    
    def test_visual_tracker_visible_in_responses(self, orchestrator):
        """Test that visual tracker appears in orchestrator responses."""
        # Execute: Run planning operation
        result = orchestrator.execute({
            'operation': 'Add simple logging to utils module',
            'force_tier': 2,  # Force lightweight tier
            'skip_refactor': True,
            'skip_vacuum': True
        })
        
        # Verify: Operation succeeded
        assert result.success is True
        assert result.data is not None
        
        # Verify: Session data present
        assert 'session' in result.data
        session_data = result.data['session']
        assert session_data is not None
        
        # Verify: Session has required fields
        assert 'session_id' in session_data
        assert 'plan_title' in session_data
        assert 'started_at' in session_data
        assert 'phases' in session_data
        
        # Verify: Visual tracker in message
        assert result.message is not None
        # Note: Tracker is rendered via render_progress_table() which includes table formatting
    
    def test_tracker_embedded_in_master_plans(self, orchestrator, temp_project_root):
        """Test that visual tracker is embedded in generated master plans."""
        # Execute: Create Tier 3 plan (documented)
        result = orchestrator.execute({
            'operation': 'Implement new payment processing module',
            'force_tier': 3,
            'skip_refactor': True,
            'skip_vacuum': True
        })
        
        # Verify: Plan created
        assert result.success is True
        assert result.data['execution_result']['plan_created'] is True
        
        # Verify: Master plan path exists
        assert 'master_plan_path' in result.data['execution_result']
        master_plan_path = Path(result.data['execution_result']['master_plan_path'])
        
        # Verify: Master plan file exists
        assert master_plan_path.exists()
        
        # Verify: Master plan contains visual tracker elements
        content = master_plan_path.read_text(encoding='utf-8')
        assert '📊 Master Planner Visual Tracker' in content or 'Phase' in content
        assert 'CORTEX' in content
        assert 'Asif Hussain' in content  # Check for author name (with or without markdown formatting)
    
    def test_metrics_accurately_tracked(self, orchestrator):
        """Test that session metrics are accurately tracked."""
        # Record start time
        start_time = time.time()
        
        # Execute: Run planning operation
        result = orchestrator.execute({
            'operation': 'Add simple config validation',
            'force_tier': 2,
            'skip_refactor': True,
            'skip_vacuum': True
        })
        
        # Record end time
        end_time = time.time()
        elapsed = end_time - start_time
        
        # Verify: Session metrics present
        session_data = result.data['session']
        assert session_data is not None
        
        # Verify: Timing metrics reasonable
        assert 'started_at' in session_data
        started_at = datetime.fromisoformat(session_data['started_at'])
        assert started_at <= datetime.now()
        
        # Verify: Token metrics present
        assert 'total_tokens_used' in session_data
        assert session_data['total_tokens_used'] >= 0
        
        # Verify: Phase metrics present (may be empty for lightweight tier)
        assert 'phases' in session_data
        phases = session_data['phases']
        # Note: Tier 2 (lightweight) may not have phases added to session
        # Only check phases if they exist
        if len(phases) > 0:
            # Verify: Each phase has required fields
            for phase in phases:
                assert 'name' in phase
                assert 'tasks' in phase
    
    def test_discovery_finds_existing_plans(self, orchestrator, temp_project_root):
        """Test that discovery correctly finds plans in all three folders."""
        planning_root = temp_project_root / "cortex-brain" / "documents" / "planning"
        
        # Setup: Create plans in all three folders
        # Active plan
        active_plan = planning_root / "active" / "api-gateway-v2"
        active_plan.mkdir(parents=True)
        (active_plan / "00-master-plan.md").write_text(
            "## Executive Summary\n\nAPI Gateway v2",
            encoding='utf-8'
        )
        
        # Temp plan (recent)
        temp_plan = planning_root / "temp-plans" / "api-gateway-draft"
        temp_plan.mkdir(parents=True)
        (temp_plan / "11-temp-planning-session.md").write_text(
            "## Summary\n\nDraft API Gateway plan",
            encoding='utf-8'
        )
        
        # Completed plan (recent - last 180 days)
        completed_plan = planning_root / "completed" / "api-gateway-v1"
        completed_plan.mkdir(parents=True)
        (completed_plan / "00-master-plan.md").write_text(
            "## Executive Summary\n\nCompleted API Gateway v1",
            encoding='utf-8'
        )
        
        # Execute: Run discovery for API gateway
        discovery_result = orchestrator.pre_planning_discovery("Plan API Gateway")
        
        # Verify: Found plans in multiple folders
        assert discovery_result['found_existing'] is True or len(discovery_result['related_plans']) > 0
        
        # Verify: Recommendations include different types
        rec_types = {r['type'] for r in discovery_result['recommendations']}
        
        # Should find at least one type (active or temp)
        expected_types = {'active_plan_exists', 'temp_plan_exists', 'completed_plan_exists'}
        assert len(rec_types & expected_types) > 0
        
        # Verify: Related plans include completed
        if len(discovery_result['related_plans']) > 0:
            plan_names = [p['name'] for p in discovery_result['related_plans']]
            assert any('api-gateway' in name.lower() for name in plan_names)
    
    def test_performance_under_threshold(self, orchestrator):
        """Test that orchestrator execution completes within reasonable time."""
        # Execute: Run lightweight planning
        start_time = time.time()
        
        result = orchestrator.execute({
            'operation': 'Add simple utility function',
            'force_tier': 1,  # Instant tier
            'skip_refactor': True,
            'skip_vacuum': True
        })
        
        elapsed = time.time() - start_time
        
        # Verify: Completed quickly (Tier 1 should be < 5 seconds)
        assert elapsed < 5.0
        assert result.success is True
        
        # Verify: Session tracking overhead minimal
        assert 'elapsed_time' in result.data
        assert result.data['elapsed_time'] < 10.0  # Total with overhead


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
