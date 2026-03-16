"""Phase M10 tests for capability pack lifecycle and handoff approvals."""

from __future__ import annotations

from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]


def _load_lifecycle() -> dict:
    path = REPO_ROOT / "cortex-registry/governance/federation/capability-pack-lifecycle.yaml"
    assert path.exists()
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    return data


def test_m10_lifecycle_states_match_federated_contract() -> None:
    """Lifecycle states preserve the five-state federated policy."""
    lifecycle = _load_lifecycle()

    assert lifecycle["id"] == "federated-capability-pack-lifecycle"
    assert lifecycle["status"] == "ACTIVE"
    assert lifecycle["lifecycle_states"] == [
        "proposed",
        "active",
        "stabilizing",
        "deprecated",
        "retired",
    ]
    assert lifecycle["default_state"] == "proposed"
    assert "retired" in lifecycle["terminal_states"]


def test_m10_lifecycle_transitions_require_approvals_and_handoff() -> None:
    """Every transition includes approvals and mandatory handoff enforcement."""
    lifecycle = _load_lifecycle()
    transitions = lifecycle.get("transitions", [])
    assert isinstance(transitions, list) and len(transitions) >= 4

    observed = {(entry["from"], entry["to"]) for entry in transitions}
    expected = {
        ("proposed", "active"),
        ("active", "stabilizing"),
        ("stabilizing", "deprecated"),
        ("deprecated", "retired"),
    }
    assert expected.issubset(observed)

    for entry in transitions:
        assert entry["approvals_required"]
        assert entry["handoff_required"] is True

    handoff_flow = lifecycle["handoff_flow"]
    assert handoff_flow["rejection_behavior"] == "fail_close"
