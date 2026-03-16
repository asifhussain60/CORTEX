"""Phase M10 tests for cross-domain orchestration and conflict detection contracts."""

from __future__ import annotations

from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]


def _load_cross_domain_contract() -> dict:
    path = REPO_ROOT / "cortex-registry/governance/federation/cross-domain-orchestration-contract.yaml"
    assert path.exists()
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    return data


def test_m10_cross_domain_contract_enforces_workflow_composer_gateway() -> None:
    """Cross-domain routing must stay workflow-template governed and fail-close."""
    contract = _load_cross_domain_contract()

    assert contract["id"] == "cross-domain-orchestration-contract"
    assert contract["status"] == "ACTIVE"

    routing = contract["routing_contract"]
    assert routing["mandatory_gateway"] == "Workflow Composer"
    assert "ad_hoc_cross_domain_execution_without_template" in routing["forbidden"]
    assert "workflow_template_id" in routing["required_references"]


def test_m10_conflict_detection_and_resolution_precedence_are_defined() -> None:
    """Conflict checks and precedence order are deterministic and block on conflict."""
    contract = _load_cross_domain_contract()

    conflict_detection = contract["ownership_conflict_detection"]
    assert conflict_detection["enabled"] is True
    assert conflict_detection["fail_on_conflict"] is True
    assert "single_owner_per_capability" in conflict_detection["checks"]

    assert contract["resolution_precedence"] == [
        "platform-kernel",
        "domain-teams",
        "shared-services",
    ]

    violation_actions = contract["violation_actions"]
    assert violation_actions["conflict_detected"] == "block_merge"
