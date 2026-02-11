"""
Tests for Unused Orchestrator Consolidation Strategy - Track 3 Part C.

Tests removal planning, prioritization, and consolidation tracking.

AC_START: AC-WAVE7T3-PC-TEST-001
Tests: 20 total (registry: 6, remover: 10, consolidation: 4)
"""

import pytest
from cortex.orchestrators.unused_orchestrators_remover import (
    UnusedOrchestratorInfo,
    RemovalRisk,
    RemovalPlan,
    UnusedOrchestratorsRegistry,
    UnusedOrchestratorRemover,
)


class TestUnusedOrchestratorsRegistry:
    """Tests for unused orchestrators registry."""

    def test_registry_has_unused_orchestrators(self):
        """Test registry contains unused orchestrators."""
        registry = UnusedOrchestratorsRegistry()
        all_unused = registry.get_all_unused()
        assert len(all_unused) == 5

    def test_get_all_unused(self):
        """Test retrieving all unused orchestrators."""
        registry = UnusedOrchestratorsRegistry()
        all_unused = registry.get_all_unused()
        
        assert all(isinstance(o, UnusedOrchestratorInfo) for o in all_unused)
        names = [o.name for o in all_unused]
        assert "conversation_continuer" in names
        assert "orchestrator_bootstrap" in names

    def test_get_safe_to_remove(self):
        """Test filtering safe-to-remove orchestrators."""
        registry = UnusedOrchestratorsRegistry()
        safe = registry.get_safe_to_remove()
        
        assert len(safe) >= 3
        assert all(o.removal_risk == RemovalRisk.SAFE for o in safe)

    def test_get_by_risk_safe(self):
        """Test filtering by safe risk level."""
        registry = UnusedOrchestratorsRegistry()
        safe = registry.get_by_risk(RemovalRisk.SAFE)
        assert len(safe) >= 3

    def test_get_by_risk_low(self):
        """Test filtering by low risk level."""
        registry = UnusedOrchestratorsRegistry()
        low = registry.get_by_risk(RemovalRisk.LOW)
        assert len(low) >= 1

    def test_get_truly_unused(self):
        """Test getting truly unused (0 imports, 0 references)."""
        registry = UnusedOrchestratorsRegistry()
        truly_unused = registry.get_truly_unused()
        
        assert len(truly_unused) == 5  # All 5 are truly unused
        assert all(o.is_truly_unused() for o in truly_unused)

    def test_removal_summary(self):
        """Test removal summary."""
        registry = UnusedOrchestratorsRegistry()
        summary = registry.get_removal_summary()
        
        assert summary["total_unused"] == 5
        assert summary["safe_to_remove"] >= 3
        assert summary["truly_unused"] == 5
        assert "total_files_to_remove" in summary


class TestUnusedOrchestratorRemover:
    """Tests for removal planning and execution."""

    def test_remover_initialization(self):
        """Test remover initialization."""
        remover = UnusedOrchestratorRemover()
        assert remover is not None
        assert len(remover.registry.get_all_unused()) == 5

    def test_create_removal_plan(self):
        """Test creating removal plan."""
        remover = UnusedOrchestratorRemover()
        orchestrator_info = UnusedOrchestratorInfo(
            name="test_unused",
            file_path="test.py",
            removal_risk=RemovalRisk.SAFE,
            reason="Test removal"
        )
        
        plan = remover.create_removal_plan(orchestrator_info)
        assert plan is not None
        assert len(plan.actions) > 0
        assert len(plan.validation_steps) > 0

    def test_get_removal_priority(self):
        """Test removal priority ordering."""
        remover = UnusedOrchestratorRemover()
        priority = remover.get_removal_priority()
        
        assert len(priority) == 5
        # Safe should come before low
        safe_indices = [i for i, o in enumerate(priority) if o.removal_risk == RemovalRisk.SAFE]
        low_indices = [i for i, o in enumerate(priority) if o.removal_risk == RemovalRisk.LOW]
        
        if safe_indices and low_indices:
            assert max(safe_indices) < min(low_indices)

    def test_mark_removal_complete(self):
        """Test marking removal as complete."""
        remover = UnusedOrchestratorRemover()
        result = remover.mark_removal_complete("conversation_continuer")
        
        assert result is True
        assert "conversation_continuer" in remover.completed_removals

    def test_skip_removal(self):
        """Test skipping removal."""
        remover = UnusedOrchestratorRemover()
        result = remover.skip_removal("state_recovery", "Need further analysis")
        
        assert result is True
        assert "state_recovery" in remover.skipped_removals

    def test_mark_removal_clears_skip(self):
        """Test that marking complete clears skip status."""
        remover = UnusedOrchestratorRemover()
        remover.skip_removal("conversation_continuer", "Skipped initially")
        remover.mark_removal_complete("conversation_continuer")
        
        assert "conversation_continuer" in remover.completed_removals
        assert "conversation_continuer" not in remover.skipped_removals

    def test_get_removal_status_initial(self):
        """Test removal status at start."""
        remover = UnusedOrchestratorRemover()
        status = remover.get_removal_status()
        
        assert status["total_unused"] == 5
        assert status["completed_removals"] == 0
        assert status["remaining"] == 5
        assert status["progress_percentage"] == 0.0

    def test_get_removal_status_with_progress(self):
        """Test removal status with progress."""
        remover = UnusedOrchestratorRemover()
        remover.mark_removal_complete("conversation_continuer")
        remover.mark_removal_complete("continuation_chain")
        remover.skip_removal("state_recovery", "Needs review")
        
        status = remover.get_removal_status()
        assert status["completed_removals"] == 2
        assert status["skipped"] == 1
        assert status["remaining"] == 2
        assert status["progress_percentage"] == pytest.approx(40.0, rel=1e-1)

    def test_can_safely_remove_safe_orchestrator(self):
        """Test can safely remove safe orchestrators."""
        remover = UnusedOrchestratorRemover()
        safe_orchs = remover.registry.get_safe_to_remove()
        
        for orch in safe_orchs:
            assert remover.can_safely_remove(orch) is True

    def test_cannot_safely_remove_high_risk(self):
        """Test cannot safely remove high-risk orchestrators."""
        remover = UnusedOrchestratorRemover()
        high_risk = UnusedOrchestratorInfo(
            name="high_risk_orch",
            file_path="test.py",
            removal_risk=RemovalRisk.HIGH,
            reason="Unknown dependencies"
        )
        
        assert remover.can_safely_remove(high_risk) is False

    def test_get_consolidation_summary(self):
        """Test consolidation summary."""
        remover = UnusedOrchestratorRemover()
        summary = remover.get_consolidation_summary()
        
        assert summary["total_unused"] == 5
        assert summary["safe_to_remove"] >= 3
        assert "progress_percentage" in summary


class TestRemovalPlans:
    """Tests for removal plan generation."""

    def test_removal_plan_for_conversation_continuer(self):
        """Test removal plan for conversation_continuer."""
        remover = UnusedOrchestratorRemover()
        registry = UnusedOrchestratorsRegistry()
        
        orch = [o for o in registry.get_all_unused() if o.name == "conversation_continuer"][0]
        plan = remover.create_removal_plan(orch)
        
        assert plan is not None
        assert len(plan.actions) > 0
        assert "conversation_continuer" in plan.actions[0]

    def test_removal_plan_for_orchestrator_composite(self):
        """Test removal plan for orchestrator_composite."""
        remover = UnusedOrchestratorRemover()
        registry = UnusedOrchestratorsRegistry()
        
        orch = [o for o in registry.get_all_unused() if o.name == "orchestrator_composite"][0]
        plan = remover.create_removal_plan(orch)
        
        assert plan is not None
        assert orch.reason == "Replaced by OrchestratorCompositionStrategy (Track 3 Part A)"

    def test_create_all_removal_plans(self):
        """Test creating all removal plans."""
        remover = UnusedOrchestratorRemover()
        plans = remover.create_all_removal_plans()
        
        assert len(plans) == 5
        assert all(isinstance(p, RemovalPlan) for p in plans.values())

    def test_get_removal_plan_for_orchestrator(self):
        """Test getting specific removal plan."""
        remover = UnusedOrchestratorRemover()
        remover.create_all_removal_plans()
        
        plan = remover.get_removal_plan_for_orchestrator("conversation_continuer")
        assert plan is not None
        assert plan.orchestrator_info.name == "conversation_continuer"


class TestConsolidationMetrics:
    """Tests for consolidation metrics."""

    def test_unused_orchestrator_count(self):
        """Test count of unused orchestrators."""
        registry = UnusedOrchestratorsRegistry()
        all_unused = registry.get_all_unused()
        assert len(all_unused) == 5

    def test_safe_removal_count(self):
        """Test count of safe-to-remove orchestrators."""
        registry = UnusedOrchestratorsRegistry()
        safe = registry.get_safe_to_remove()
        assert len(safe) >= 3

    def test_risk_distribution(self):
        """Test risk distribution of unused orchestrators."""
        registry = UnusedOrchestratorsRegistry()
        all_unused = registry.get_all_unused()
        
        risk_counts = {}
        for orch in all_unused:
            risk = orch.removal_risk.value
            risk_counts[risk] = risk_counts.get(risk, 0) + 1
        
        assert risk_counts["safe"] >= 3
        assert risk_counts["low"] >= 1

    def test_truly_unused_all_have_zero_references(self):
        """Test all truly unused have 0 imports and references."""
        registry = UnusedOrchestratorsRegistry()
        truly_unused = registry.get_truly_unused()
        
        for orch in truly_unused:
            assert orch.import_count == 0
            assert orch.reference_count == 0


# AC_COMPLETE: AC-WAVE7T3-PC-TEST-001 ✅ 20 test cases for unused orchestrator removal
