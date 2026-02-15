"""
Golden tests for PlanAuditorAgent — syncs registry with dashboard.

Authority: Phase 29 S1 | Zero-Mock Philosophy
Test Count: 6 golden tests
"""
import pytest
from pathlib import Path
from cortex.agents.plan_auditor_agent import PlanAuditorAgent, DashboardSyncResult


class TestPlanAuditorSync:
    """Golden test: Plan-auditor syncs registry with dashboard."""
    
    def test_detect_dashboard_drift(self, tmp_path: Path) -> None:
        """Golden: Detect drift between registry and dashboard."""
        agent = PlanAuditorAgent()
        
        # Registry says Phase 23 completed, dashboard shows active
        registry_state = {"phase-23": {"status": "completed"}}
        dashboard_state = {"phase-23": {"status": "active"}}
        
        sync_result = agent.detect_drift(registry_state, dashboard_state)
        
        assert sync_result.has_drift is True
        assert "phase-23" in sync_result.drifted_phases
    
    def test_auto_sync_dashboard(self, tmp_path: Path) -> None:
        """Golden: Auto-sync dashboard from registry."""
        agent = PlanAuditorAgent()
        
        registry_path = tmp_path / "registry"
        dashboard_path = tmp_path / "dashboard"
        registry_path.mkdir()
        dashboard_path.mkdir()
        
        # Sync registry → dashboard
        sync_result = agent.sync_dashboard(registry_path, dashboard_path)
        
        assert sync_result.synced is True
        assert sync_result.phases_updated > 0
    
    def test_prevent_manual_dashboard_edits(self) -> None:
        """Golden: Detect manual dashboard edits (should use registry only)."""
        agent = PlanAuditorAgent()
        
        # Dashboard edited manually (registry unchanged)
        registry_version = "6.3"
        dashboard_version = "6.3-modified"
        
        validation = agent.validate_dashboard_source(registry_version, dashboard_version)
        
        assert validation.manual_edit_detected is True


class TestPlanAuditorIntegration:
    """Golden test: Plan-auditor integrates with PlanOrchestrator."""
    
    @pytest.mark.skip(reason="PlanOrchestrator integration deferred to S2")
    def test_plan_orchestrator_uses_plan_auditor(self) -> None:
        """Golden: PlanOrchestrator invokes plan-auditor for sync."""
        # Integration test deferred until PlanOrchestrator updated
        pass
    
    @pytest.mark.skip(reason="PlanOrchestrator integration deferred to S2")
    def test_dashboard_update_after_phase_completion(self) -> None:
        """Golden: Dashboard auto-syncs after phase completion."""
        # Integration test deferred until PlanOrchestrator updated
        pass
