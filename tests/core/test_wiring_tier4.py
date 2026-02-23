"""
Phase 59-f (GAP-59-09): Wiring YAML Tier 4 Registration Tests
==============================================================
Verifies that the 4 previously unregistered orchestrator tiers
(git, intelligence, synthesis, workflow) are now present in wiring.yaml
with correct structure and class names.

TDD: RED → GREEN → REFACTOR (CORE-008)
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import pytest
import yaml

WIRING_YAML_PATH = (
    Path(__file__).parents[2]
    / "cortex" / "core" / "wiring" / "specifications" / "wiring.yaml"
)


@pytest.fixture(scope="module")
def wiring() -> dict[str, Any]:
    """Load wiring.yaml once per test module."""
    assert WIRING_YAML_PATH.exists(), f"wiring.yaml not found at {WIRING_YAML_PATH}"
    with open(WIRING_YAML_PATH) as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="module")
def orchestrators(wiring) -> dict[str, list[dict]]:
    return wiring["orchestrators"]


@pytest.fixture(scope="module")
def tier4_entries(orchestrators) -> list[dict]:
    return [o for items in orchestrators.values() for o in items if o.get("tier") == 4]


class TestWiringTier4Structure:
    """GAP-59-09: 4 new tier subsections registered in wiring.yaml."""

    def test_git_tier_subsection_present(self, orchestrators):
        assert "git" in orchestrators, "Missing 'git' subsection in orchestrators"

    def test_intelligence_tier_subsection_present(self, orchestrators):
        assert "intelligence" in orchestrators, "Missing 'intelligence' subsection"

    def test_synthesis_tier_subsection_present(self, orchestrators):
        assert "synthesis" in orchestrators, "Missing 'synthesis' subsection"

    def test_workflow_tier_subsection_present(self, orchestrators):
        assert "workflow" in orchestrators, "Missing 'workflow' subsection"

    def test_at_least_ten_tier4_entries(self, tier4_entries):
        assert len(tier4_entries) >= 10, (
            f"Expected ≥10 tier 4 entries, got {len(tier4_entries)}"
        )

    def test_all_tier4_entries_have_required_fields(self, tier4_entries):
        required = {"name", "module", "class", "tier", "priority", "capabilities"}
        for entry in tier4_entries:
            missing = required - entry.keys()
            assert not missing, (
                f"Entry '{entry.get('name')}' missing fields: {missing}"
            )

    def test_all_tier4_entries_have_registration_phase(self, tier4_entries):
        for entry in tier4_entries:
            assert entry.get("registration_phase") == "59-f", (
                f"Entry '{entry.get('name')}' missing registration_phase '59-f'"
            )


class TestWiringGitTier:
    """Git orchestrators registered with correct class names."""

    def test_git_orchestrator_registered(self, orchestrators):
        names = [o["name"] for o in orchestrators["git"]]
        assert "GitOrchestrator" in names

    def test_git_publish_orchestrator_registered(self, orchestrators):
        names = [o["name"] for o in orchestrators["git"]]
        assert "GitPublishOrchestrator" in names

    def test_pre_commit_enforcement_orchestrator_registered(self, orchestrators):
        names = [o["name"] for o in orchestrators["git"]]
        assert "PreCommitEnforcementOrchestrator" in names

    def test_git_orchestrator_module_path(self, orchestrators):
        entry = next(o for o in orchestrators["git"] if o["name"] == "GitOrchestrator")
        assert entry["module"] == "cortex.orchestrators.git.git_orchestrator"
        assert entry["class"] == "GitOrchestrator"


class TestWiringIntelligenceTier:
    """Intelligence orchestrators registered with correct class names."""

    def test_intelligence_orchestrator_registered(self, orchestrators):
        names = [o["name"] for o in orchestrators["intelligence"]]
        assert "IntelligenceOrchestrator" in names

    def test_meta_auditor_agent_registered(self, orchestrators):
        names = [o["name"] for o in orchestrators["intelligence"]]
        assert "MetaAuditorAgent" in names

    def test_intelligence_orchestrator_module_path(self, orchestrators):
        entry = next(
            o for o in orchestrators["intelligence"]
            if o["name"] == "IntelligenceOrchestrator"
        )
        assert entry["module"] == "cortex.orchestrators.intelligence.intelligence_orchestrator"
        assert entry["class"] == "IntelligenceOrchestrator"


class TestWiringSynthesisTier:
    """Synthesis orchestrators registered with correct class names."""

    def test_context_aware_synthesis_gateway_registered(self, orchestrators):
        names = [o["name"] for o in orchestrators["synthesis"]]
        assert "ContextAwareSynthesisGateway" in names

    def test_synthesis_module_path(self, orchestrators):
        entry = orchestrators["synthesis"][0]
        assert entry["module"] == "cortex.orchestrators.synthesis.context_aware_synthesis"
        assert entry["class"] == "ContextAwareSynthesisGateway"


class TestWiringWorkflowTier:
    """Workflow orchestrators registered with correct class names."""

    def test_workflow_composer_registered(self, orchestrators):
        names = [o["name"] for o in orchestrators["workflow"]]
        assert "WorkflowComposer" in names

    def test_convergence_loop_executor_registered(self, orchestrators):
        names = [o["name"] for o in orchestrators["workflow"]]
        assert "ConvergenceLoopExecutor" in names

    def test_holistic_refactoring_sweep_registered(self, orchestrators):
        names = [o["name"] for o in orchestrators["workflow"]]
        assert "HolisticRefactoringSweep" in names

    def test_autonomous_workflow_executor_registered(self, orchestrators):
        names = [o["name"] for o in orchestrators["workflow"]]
        assert "AutonomousWorkflowExecutor" in names

    def test_workflow_composer_module_path(self, orchestrators):
        entry = next(o for o in orchestrators["workflow"] if o["name"] == "WorkflowComposer")
        assert entry["module"] == "cortex.orchestrators.workflow.workflow_composer"
        assert entry["class"] == "WorkflowComposer"


class TestWiringYAMLValidity:
    """Structural integrity of wiring.yaml after Phase 59-f edits."""

    def test_yaml_has_seven_orchestrator_tiers(self, orchestrators):
        expected = {"core", "domain", "support", "git", "intelligence", "synthesis", "workflow"}
        assert expected.issubset(set(orchestrators.keys())), (
            f"Missing tiers: {expected - set(orchestrators.keys())}"
        )

    def test_total_orchestrators_at_least_36(self, orchestrators):
        total = sum(len(v) for v in orchestrators.values())
        assert total >= 36, f"Expected ≥36 total, got {total}"

    def test_analyzers_section_preserved(self, wiring):
        assert "analyzers" in wiring, "analyzers: section was lost during tier 4 insertion"

    def test_config_section_preserved(self, wiring):
        assert "config" in wiring, "config: section was lost"

    def test_validation_section_preserved(self, wiring):
        assert "validation" in wiring, "validation: section was lost"

    def test_existing_tier1_orchestrators_intact(self, orchestrators):
        core_names = [o["name"] for o in orchestrators["core"]]
        assert "MasterOrchestrator" in core_names
        assert "TDDOrchestrator" in core_names
        assert "EnforcementOrchestrator" in core_names

    def test_no_duplicate_names_across_tiers(self, orchestrators):
        all_names = [o["name"] for items in orchestrators.values() for o in items]
        assert len(all_names) == len(set(all_names)), (
            f"Duplicate orchestrator names detected: "
            f"{[n for n in all_names if all_names.count(n) > 1]}"
        )
