"""Phase M11 tests for agent and skill workflow template creation."""

from __future__ import annotations

from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]


def _load_workflow(relative_path: str) -> dict:
    path = REPO_ROOT / relative_path
    assert path.exists(), f"Missing workflow template: {relative_path}"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    return data["workflow"]


def test_m11_agent_template_exists_with_required_sections() -> None:
    """Agent lifecycle template is present and defines mandatory sections."""
    workflow = _load_workflow(
        "cortex-registry/workflows/templates/agent-skill/agent-authoring-lifecycle.yaml"
    )

    assert workflow["id"] == "agent-skill/agent-authoring-lifecycle"
    assert workflow["status"] == "ACTIVE"
    assert workflow["mcp_first"] is True

    assert workflow["required_inputs"]
    assert workflow["required_outputs"]
    assert workflow["touchpoints"]
    assert workflow["approvals"]
    assert workflow["primitives"]


def test_m11_skill_template_exists_with_required_sections() -> None:
    """Skill lifecycle template is present and defines mandatory sections."""
    workflow = _load_workflow(
        "cortex-registry/workflows/templates/agent-skill/skill-authoring-lifecycle.yaml"
    )

    assert workflow["id"] == "agent-skill/skill-authoring-lifecycle"
    assert workflow["status"] == "ACTIVE"
    assert workflow["mcp_first"] is True

    assert workflow["required_inputs"]
    assert workflow["required_outputs"]
    assert workflow["touchpoints"]
    assert workflow["approvals"]
    assert workflow["primitives"]
