"""Phase M11 tests for lifecycle, observability, and reuse contracts."""

from __future__ import annotations

from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]


def _load_workflow(path: str) -> dict:
    data = yaml.safe_load((REPO_ROOT / path).read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    return data["workflow"]


def test_m11_templates_define_lifecycle_states() -> None:
    """Both templates define full lifecycle state machine for managed assets."""
    expected_states = ["proposed", "active", "stabilizing", "deprecated", "retired"]
    templates = [
        "cortex-registry/workflows/templates/agent-skill/agent-authoring-lifecycle.yaml",
        "cortex-registry/workflows/templates/agent-skill/skill-authoring-lifecycle.yaml",
    ]

    for template_path in templates:
        workflow = _load_workflow(template_path)
        assert workflow["lifecycle_states"] == expected_states


def test_m11_templates_define_observability_and_composability() -> None:
    """Templates provide AC marker telemetry and reuse metadata."""
    templates = [
        "cortex-registry/workflows/templates/agent-skill/agent-authoring-lifecycle.yaml",
        "cortex-registry/workflows/templates/agent-skill/skill-authoring-lifecycle.yaml",
    ]

    for template_path in templates:
        workflow = _load_workflow(template_path)
        observability = workflow["observability"]
        composability = workflow["composability"]
        assert observability["ac_markers_required"] is True
        assert observability["telemetry_events"]
        assert composability["reusable"] is True
        assert composability["canonical_owner_required"] is True
