"""Phase M12 tests for extension guides and operational runbooks."""

from __future__ import annotations

from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]


def _load(path: str) -> dict:
    data = yaml.safe_load((REPO_ROOT / path).read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    return data


def test_m12_extension_guides_cover_agents_skills_workflows_mcp() -> None:
    """Guides include all required extension surfaces."""
    guides = _load(
        "cortex-registry/planning/phases/v2/artifacts/phase-m12/extension-guides.yaml"
    )
    scopes = {entry["scope"] for entry in guides["guides"]}
    assert {"agents", "skills", "workflows", "mcp"}.issubset(scopes)


def test_m12_runbooks_include_ops_governance_and_rollback() -> None:
    """Runbooks include operations, governance, and rollback procedures."""
    runbooks = _load(
        "cortex-registry/planning/phases/v2/artifacts/phase-m12/operations-runbooks.yaml"
    )
    runbook_ids = {entry["id"] for entry in runbooks["runbooks"]}
    assert {"ops-health", "ops-smoke", "gov-audit", "ops-rollback"}.issubset(runbook_ids)
