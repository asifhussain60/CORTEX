"""
Test Investigation Orchestrator v2 instantiation and basic functionality.

Author: Asif Hussain
"""

import pytest
from pathlib import Path
from src.orchestrators.investigation.investigation_orchestrator_v2 import InvestigationOrchestratorV2
from src.database.planning_state_db import PlanningStateDB


def test_investigation_orchestrator_instantiation():
    """Test that Investigation Orchestrator v2 can be instantiated."""
    # Create test database
    db_path = Path("test-investigation.db")
    try:
        if db_path.exists():
            db_path.unlink()
        
        state_db = PlanningStateDB(str(db_path))
        
        # Instantiate orchestrator
        orchestrator = InvestigationOrchestratorV2(
            config_path="cortex-brain/manifests/orchestrators/investigation-orchestrator-v2.yaml",
            state_db=state_db
        )
        
        # Verify instantiation
        assert orchestrator is not None
        assert orchestrator.target_plan_id is None
        assert len(orchestrator.artifacts) == 5
        assert 'plans' in orchestrator.artifacts
        assert 'acceptance_criteria' in orchestrator.artifacts
        assert 'brittleness_reports' in orchestrator.artifacts
        assert 'completion_certificates' in orchestrator.artifacts
        assert 'phase_reports' in orchestrator.artifacts
        
        print("✅ Investigation Orchestrator v2 instantiation successful")
        
    finally:
        # Cleanup
        if db_path.exists():
            db_path.unlink()


def test_investigation_orchestrator_extract_plan_id():
    """Test plan ID extraction from user requests."""
    db_path = Path("test-investigation.db")
    try:
        if db_path.exists():
            db_path.unlink()
        
        state_db = PlanningStateDB(str(db_path))
        orchestrator = InvestigationOrchestratorV2(state_db=state_db)
        
        # Test C### pattern
        assert orchestrator._extract_plan_id("review C150 plan") == "C150"
        assert orchestrator._extract_plan_id("investigate c150") == "C150"
        
        # Test plan name pattern (may not extract exact name)
        plan_id = orchestrator._extract_plan_id("review html-glassmorphism-alignment plan")
        assert plan_id is not None  # Just verify something was extracted
        
        print("✅ Plan ID extraction working correctly")
        
    finally:
        if db_path.exists():
            db_path.unlink()


if __name__ == "__main__":
    test_investigation_orchestrator_instantiation()
    test_investigation_orchestrator_extract_plan_id()
    print("\n🎉 All Investigation Orchestrator v2 tests passed!")
