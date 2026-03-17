"""Phase M7-b guardrails for active response-template runtime wiring.

Verifies that the deprecated VS Code Copilot Chat response-template workflow is
no longer referenced by active runtime surfaces and that validation accepts the
current canonical header contract.
"""

from __future__ import annotations

from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
DEPRECATED_TEMPLATE_PATH = (
    "cortex-registry/workflows/templates/governance/"
    "copilot-chat-response-template.yaml"
)
RESPONSE_SSOT_PATH = ".github/templates/cortex-response-templates.md"
RESPONSE_REGISTRY_PATH = "cortex-registry/templates/response/_registry.yaml"


def _load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def test_m7b_active_runtime_surfaces_drop_deprecated_copilot_template() -> None:
    """Active runtime surfaces must not point at the deprecated Copilot template."""
    runtime_files = [
        REPO_ROOT / "cortex-registry/workflows/templates/sdlc/code-modify-unified.yaml",
        REPO_ROOT / "cortex-registry/workflows/workflow-composer-spec.yaml",
        REPO_ROOT / "cortex-registry/core/capabilities-manifest.yaml",
        REPO_ROOT / "cortex-registry/core/tier0-skull/skull-rules.yaml",
        REPO_ROOT / "cortex/governance/response_template_validator.py",
    ]

    offenders = [
        str(path.relative_to(REPO_ROOT))
        for path in runtime_files
        if DEPRECATED_TEMPLATE_PATH in path.read_text(encoding="utf-8")
    ]

    assert offenders == [], (
        "Deprecated Copilot Chat response-template wiring remains in active runtime surfaces: "
        f"{offenders}"
    )


def test_m7b_runtime_response_contract_points_to_current_ssot_assets() -> None:
    """Active workflow metadata must point to the current SSOT/registry assets."""
    unified_workflow = _load_yaml(
        REPO_ROOT / "cortex-registry/workflows/templates/sdlc/code-modify-unified.yaml"
    )
    contracts = unified_workflow["workflow"]["required_contracts"]
    assert contracts["response_template"] == RESPONSE_SSOT_PATH

    capabilities = _load_yaml(REPO_ROOT / "cortex-registry/core/capabilities-manifest.yaml")
    governance_entries = capabilities["workflow_templates"]["domains"]["governance"]
    response_entry = next(
        entry for entry in governance_entries if entry["id"] == "copilot_chat_response_template"
    )
    assert response_entry["path"] == RESPONSE_REGISTRY_PATH


def test_m7b_response_template_validator_accepts_current_header_contract() -> None:
    """Validator must accept the canonical header contract used by current prompts."""
    from cortex.governance.response_template_validator import (  # noqa: PLC0415
        ResponseTemplateValidator,
    )

    validator = ResponseTemplateValidator()
    current_header = (
        "# 🛠️ CORTEX Architect FIX\n"
        "**Author:** Asif Hussain | © 2025–2026 CORTEX Framework. All rights reserved.\n\n"
        "---\n\n"
        "🧭 Orchestration: Classifier → TDD Builder\n"
    )

    result = validator.validate_output(current_header)
    assert result["valid"] is True, result