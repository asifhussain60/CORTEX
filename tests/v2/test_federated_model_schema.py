"""Phase M10 tests for federated ownership and collaboration schema contracts."""

from __future__ import annotations

from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]


def _load_yaml(relative_path: str) -> dict:
    path = REPO_ROOT / relative_path
    assert path.exists(), f"Missing YAML file: {relative_path}"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    return data


def test_m10_ownership_matrix_has_required_teams_and_constraints() -> None:
    """Ownership matrix defines canonical teams, boundaries, and anti-overlap constraints."""
    matrix = _load_yaml("cortex-registry/governance/federation/ownership-matrix.yaml")

    assert matrix["id"] == "federated-ownership-matrix"
    assert matrix["status"] == "ACTIVE"
    teams = matrix.get("teams", [])
    assert isinstance(teams, list) and len(teams) == 3

    team_ids = {entry["id"] for entry in teams}
    assert team_ids == {"platform-kernel", "domain-teams", "shared-services"}

    constraints = matrix["ownership_constraints"]
    assert constraints["single_canonical_owner_required"] is True
    assert constraints["duplicate_owner_for_same_capability_forbidden"] is True
    assert constraints["escalation_owner"] == "platform-kernel"


def test_m10_collaboration_contract_schema_has_required_fields_and_approvals() -> None:
    """Collaboration contract schema enforces required fields and fail-close approvals."""
    schema = _load_yaml("cortex-registry/governance/federation/collaboration-contract-schema.yaml")

    assert schema["id"] == "federated-collaboration-contract-schema"
    assert schema["status"] == "ACTIVE"

    required_fields = set(schema.get("required_fields", []))
    assert {
        "contract_id",
        "requesting_team",
        "owning_team",
        "capability_scope",
        "change_type",
        "approval_policy",
        "handoff_artifacts",
        "rollback_strategy",
        "sla",
    }.issubset(required_fields)

    approval_policy = schema["approval_policy"]
    assert approval_policy["fail_close_on_missing_approvals"] is True
    assert "platform_kernel_reviewer" in approval_policy["required_approvers"]
