"""Phase M11 tests for template governance boundaries and approvals."""

from __future__ import annotations

from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]


def _load_workflow(path: str) -> dict:
    raw = yaml.safe_load((REPO_ROOT / path).read_text(encoding="utf-8"))
    assert isinstance(raw, dict)
    return raw["workflow"]


def test_m11_templates_define_required_mcp_touchpoints() -> None:
    """Both templates require cortex_plan/governance/validate touchpoints."""
    templates = [
        "cortex-registry/workflows/templates/agent-skill/agent-authoring-lifecycle.yaml",
        "cortex-registry/workflows/templates/agent-skill/skill-authoring-lifecycle.yaml",
    ]

    for template_path in templates:
        workflow = _load_workflow(template_path)
        touchpoints = workflow["touchpoints"]
        assert touchpoints["plan_tool"] == "cortex_plan"
        assert touchpoints["governance_tool"] == "cortex_governance"
        assert touchpoints["validation_tool"] == "cortex_validate"


def test_m11_templates_enforce_fail_close_approvals_and_boundaries() -> None:
    """Approval contracts must be fail-close with platform governance participation."""
    templates = [
        "cortex-registry/workflows/templates/agent-skill/agent-authoring-lifecycle.yaml",
        "cortex-registry/workflows/templates/agent-skill/skill-authoring-lifecycle.yaml",
    ]

    for template_path in templates:
        workflow = _load_workflow(template_path)
        approvals = workflow["approvals"]
        assert approvals["fail_close"] is True
        assert "platform_governance" in approvals["required"]
