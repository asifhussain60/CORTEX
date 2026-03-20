"""Unit tests for Phase M21 planning/audit components."""

from __future__ import annotations

from pathlib import Path

from cortex.core.registry.registry_index_manager import RegistryIndexManager
from cortex.orchestrators.core.audit_coordinator_enhanced import AuditCoordinatorEnhanced
from cortex.orchestrators.support.planning_coordinator import PlanningCoordinator
from cortex.orchestrators.support.repo_plan_orchestrator import RepoPlanOrchestrator


def test_repo_plan_orchestrator_setup_plan() -> None:
    """RepoPlanOrchestrator sets up a plan record."""
    orch = RepoPlanOrchestrator()

    result = orch.setup_plan("phase-m21", {"priority": "P0"})

    assert result.plan_id == "phase-m21"
    assert result.status == "pending"


def test_registry_index_manager_lists_phase_ids() -> None:
    """RegistryIndexManager returns phase IDs from a master index file."""
    manager = RegistryIndexManager(Path("cortex-registry/cortex-master-v2.yaml"))

    phase_ids = manager.list_phase_ids()

    assert "phase-m21" in phase_ids


def test_planning_coordinator_boundary_classifier() -> None:
    """PlanningCoordinator classifies request boundaries for plan/rephrase."""
    coordinator = PlanningCoordinator()

    assert coordinator.classify_request_boundary("rephrase this request") == "REPHRASE"
    assert coordinator.classify_request_boundary("plan phase execution") == "PLAN"


def test_audit_coordinator_enhanced_rca() -> None:
    """AuditCoordinatorEnhanced provides RCA wrapper output."""
    coordinator = AuditCoordinatorEnhanced()

    result = coordinator.run_rca("f-1", "build failed")

    assert result["failure_id"] == "f-1"
    assert result["methodology"] in {"five_whys", "fishbone", "fault_tree", "causal_chain"}
