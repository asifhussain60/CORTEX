"""Phase M14 tests for ADLC lifecycle artifacts and bounded feedback loops."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from cortex.tools.adlc_feedback_bridge import ADLCFeedbackBridge
from cortex.tools.adlc_orchestrator import ADLCOrchestrator, MaxCyclesExceeded


REPO_ROOT = Path(__file__).resolve().parents[2]


def _load(path: str) -> dict:
    data = yaml.safe_load((REPO_ROOT / path).read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    return data


def test_m14_adlc_workflow_template_and_knowledge_yaml_exist() -> None:
    """ADLC workflow and knowledge artifacts exist with core structure."""
    workflow = _load("cortex-registry/workflows/templates/lifecycle/adlc-cycle-workflow.yaml")
    knowledge = _load("cortex-registry/knowledge/sdlc/agentic-sdlc-patterns.yaml")

    assert workflow["workflow"]["mode"] == "ADLC"
    assert workflow["workflow"]["convergence"]["max_cycles"] == 3
    assert knowledge["id"] == "agentic-sdlc-patterns"
    assert knowledge["patterns"]


def test_m14_adlc_orchestrator_enforces_max_cycles() -> None:
    """ADLC orchestrator returns results within budget and raises beyond cap."""
    orchestrator = ADLCOrchestrator(max_cycles=3)
    result = orchestrator.execute_cycle(cycle=1, converged=False)
    assert result.cycle == 1
    assert result.converged is False

    with pytest.raises(MaxCyclesExceeded):
        orchestrator.execute_cycle(cycle=4, converged=False)


def test_m14_feedback_bridge_routes_stage7_to_stage2() -> None:
    """Feedback bridge routes from stage-7 feedback to stage-2 scope loop."""
    bridge = ADLCFeedbackBridge(max_cycles=3)
    action = bridge.route_feedback(cycle=2)
    assert action.from_stage == "feedback_and_learning"
    assert action.to_stage == "scope_and_risk"

    with pytest.raises(MaxCyclesExceeded):
        bridge.route_feedback(cycle=5)
