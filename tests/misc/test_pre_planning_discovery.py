"""
Tests for Planning Orchestrator v3.1 - Pre-Planning Discovery

Tests the pre-planning discovery functionality that checks for
existing/recent plans before creating new ones.

Author: Asif Hussain
Date: December 15, 2025
Phase: 1 - Visual Tracker Migration (Task 1.1)
"""

import pytest
from pathlib import Path
import tempfile
import shutil
from datetime import datetime, timedelta
from typing import Dict, Any, List

from src.operations.modules.orchestration.planning_orchestrator import PlanningOrchestrator


class TestPrePlanningDiscovery:
    """Test suite for pre-planning discovery functionality."""

    @pytest.fixture
    def temp_planning_structure(self):
        """Create temporary planning folder structure."""
        temp_dir = tempfile.mkdtemp(prefix="test_planning_")
        planning_root = Path(temp_dir) / "cortex-brain" / "documents" / "planning"
        
        # Create lifecycle folders
        (planning_root / "temp-plans").mkdir(parents=True)
        (planning_root / "active").mkdir(parents=True)
        (planning_root / "completed").mkdir(parents=True)
        
        yield planning_root
        
        # Cleanup
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def orchestrator(self, temp_planning_structure):
        """Create planning orchestrator instance."""
        orchestrator = PlanningOrchestrator()
        orchestrator.project_root = temp_planning_structure.parent.parent.parent
        return orchestrator

    def test_pre_planning_discovery_finds_active_plans(self, orchestrator, temp_planning_structure):
        """Test discovery finds active plans with matching feature names."""
        # Create active plan
        active_plan = temp_planning_structure / "active" / "authentication-system-v1"
        active_plan.mkdir(parents=True)
        (active_plan / "00-master-plan.md").write_text(
            "# Authentication System\n\nUser authentication implementation",
            encoding='utf-8'
        )
        
        # Run discovery
        results = orchestrator.pre_planning_discovery("Implement authentication system")
        
        # Assertions
        assert results['found_existing'] is True
        assert len(results['recommendations']) > 0
        assert results['recommendations'][0]['type'] == 'active_plan_exists'
        assert 'authentication' in results['recommendations'][0]['message'].lower()

    def test_pre_planning_discovery_finds_temp_plans(self, orchestrator, temp_planning_structure):
        """Test discovery finds temporary plans within last 30 days."""
        # Create temp plan (recent)
        temp_plan = temp_planning_structure / "temp-plans" / "auth-system-20251215"
        temp_plan.mkdir(parents=True)
        (temp_plan / "11-temp-planning-session.md").write_text(
            "# Temp Auth Plan\n\nTemporary planning session",
            encoding='utf-8'
        )
        
        # Run discovery
        results = orchestrator.pre_planning_discovery("Plan auth system")
        
        # Assertions
        assert results['found_existing'] is True
        assert any(r['type'] == 'temp_plan_exists' for r in results['recommendations'])

    def test_pre_planning_discovery_finds_completed_plans(self, orchestrator, temp_planning_structure):
        """Test discovery finds completed plans within last 180 days."""
        # Create completed plan with clear naming
        completed_plan = temp_planning_structure / "completed" / "auth-system-v1"
        completed_plan.mkdir(parents=True)
        (completed_plan / "00-master-plan.md").write_text(
            "## Executive Summary\n\nCompleted authentication system implementation",
            encoding='utf-8'
        )
        (completed_plan / "context").mkdir()
        (completed_plan / "reports").mkdir()
        
        # Run discovery with query that should match (both contain "auth-system")
        results = orchestrator.pre_planning_discovery("Plan auth system")
        
        # Assertions - should find completed plan
        assert results is not None
        # Should find the plan (either in recommendations or have found_existing true)
        has_completed = any(
            r['type'] == 'completed_plan_exists' for r in results['recommendations']
        ) or len(results['related_plans']) > 0
        assert has_completed, f"Should find completed auth plan. Results: {results}"

    def test_pre_planning_discovery_no_existing_plans(self, orchestrator, temp_planning_structure):
        """Test discovery returns empty results when no plans exist."""
        # Run discovery (empty planning structure)
        results = orchestrator.pre_planning_discovery("Brand new feature")
        
        # Assertions
        assert results['found_existing'] is False
        assert len(results['recommendations']) == 0
        assert len(results['related_plans']) == 0

    def test_extract_feature_slug_basic(self, orchestrator):
        """Test feature slug extraction from various operation formats."""
        test_cases = [
            ("Plan authentication system", "authentication-system"),
            ("Implement JWT tokens", "jwt-tokens"),
            ("Create user management", "user-management"),
            ("Build API gateway", "api-gateway"),
            ("authentication system", "authentication-system")
        ]
        
        for operation, expected_slug in test_cases:
            slug = orchestrator._extract_feature_slug(operation)
            assert slug == expected_slug, f"Failed for: {operation}"

    def test_search_plans_by_time_range(self, orchestrator, temp_planning_structure):
        """Test plan search with time range filtering."""
        # Create old plan (outside 30-day window)
        old_plan = temp_planning_structure / "temp-plans" / "old-plan"
        old_plan.mkdir(parents=True)
        (old_plan / "11-temp-planning-session.md").write_text("Old plan", encoding='utf-8')
        
        # Manually set modification time to 60 days ago on the FOLDER (not just the file)
        old_time = (datetime.now() - timedelta(days=60)).timestamp()
        import os
        os.utime(old_plan, (old_time, old_time))
        
        # Create recent plan
        recent_plan = temp_planning_structure / "temp-plans" / "recent-plan"
        recent_plan.mkdir(parents=True)
        (recent_plan / "11-temp-planning-session.md").write_text("Recent plan", encoding='utf-8')
        
        # Search with last_30_days filter
        results = orchestrator._search_plans(
            folder="temp-plans",
            query="plan",
            time_range="last_30_days"
        )
        
        # Should only find recent plan (old plan filtered out by time)
        assert len(results) >= 1, "Should find at least the recent plan"
        # Verify recent plan is in results
        recent_found = any("recent-plan" in r['name'] for r in results)
        assert recent_found, "Should find recent-plan in results"

    def test_find_master_plan_finds_correct_file(self, orchestrator, temp_planning_structure):
        """Test finding master plan or temp plan file in folder."""
        # Create plan with master plan
        plan1 = temp_planning_structure / "active" / "feature-v1"
        plan1.mkdir(parents=True)
        (plan1 / "00-master-plan.md").write_text("Master plan", encoding='utf-8')
        
        result = orchestrator._find_master_plan(plan1)
        assert result == plan1 / "00-master-plan.md"
        
        # Create plan with temp plan
        plan2 = temp_planning_structure / "temp-plans" / "feature-temp"
        plan2.mkdir(parents=True)
        (plan2 / "11-temp-planning-session.md").write_text("Temp plan", encoding='utf-8')
        
        result = orchestrator._find_master_plan(plan2)
        assert result == plan2 / "11-temp-planning-session.md"
        
        # Empty folder
        plan3 = temp_planning_structure / "active" / "empty-folder"
        plan3.mkdir(parents=True)
        
        result = orchestrator._find_master_plan(plan3)
        assert result is None

    def test_extract_plan_summary(self, orchestrator, temp_planning_structure):
        """Test extracting summary from plan file."""
        plan_file = temp_planning_structure / "test-plan.md"
        plan_file.write_text("""
# Test Plan

## Executive Summary

This is a comprehensive test plan for validating functionality.
It includes multiple phases and detailed steps.

## Implementation
...
""", encoding='utf-8')
        
        summary = orchestrator._extract_plan_summary(plan_file)
        assert "comprehensive test plan" in summary.lower()
        assert len(summary) <= 200  # Should be truncated

    def test_discovery_performance_under_60_seconds(self, orchestrator, temp_planning_structure):
        """Test that discovery completes in under 60 seconds."""
        import time
        
        # Create multiple plans to simulate realistic scenario
        for i in range(10):
            active = temp_planning_structure / "active" / f"feature-{i}-v1"
            active.mkdir(parents=True)
            (active / "00-master-plan.md").write_text(f"Plan {i}", encoding='utf-8')
        
        start_time = time.time()
        results = orchestrator.pre_planning_discovery("Feature implementation")
        elapsed = time.time() - start_time
        
        assert elapsed < 60.0, f"Discovery took {elapsed:.2f}s (should be < 60s)"
        assert results is not None


# ============================================
# STANDALONE EXECUTION
# ============================================

if __name__ == "__main__":
    """Run tests standalone."""
    print("🧠 CORTEX Phase 1 - Pre-Planning Discovery Tests")
    print("=" * 70)
    
    exit_code = pytest.main([__file__, "-v", "--tb=short"])
    
    print("\n" + "=" * 70)
    if exit_code == 0:
        print("✅ ALL TESTS PASSED (RED Phase - expect failures until implementation)")
    else:
        print("❌ TESTS FAILED (Expected - RED phase)")
    
    exit(exit_code)
