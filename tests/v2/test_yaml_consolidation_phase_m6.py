"""Phase M6 tests for YAML governance consolidation and contract preservation."""

from __future__ import annotations

from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]


def _load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def test_m6_drift_lock_manifest_has_core_001_to_068() -> None:
    """drift-lock-manifest.yaml exists and includes CORE-001..CORE-068 metadata."""
    manifest_path = REPO_ROOT / "cortex-registry/core/drift-lock-manifest.yaml"
    assert manifest_path.exists()

    manifest = _load_yaml(manifest_path)
    rules = manifest.get("rules", [])
    assert isinstance(rules, list)

    expected_ids = {f"CORE-{index:03d}" for index in range(1, 69)}
    observed_ids = {entry.get("id") for entry in rules}
    assert expected_ids.issubset(observed_ids)

    for entry in rules:
        assert {"id", "title", "severity", "enforcement_point"}.issubset(entry.keys())


def test_m6_governance_category_manifests_exist_and_resolve() -> None:
    """rules/gates/policies category manifests exist and reference real YAML files."""
    manifest_paths = [
        REPO_ROOT / "cortex-registry/governance/rules/manifest.yaml",
        REPO_ROOT / "cortex-registry/governance/gates/manifest.yaml",
        REPO_ROOT / "cortex-registry/governance/policies/manifest.yaml",
    ]

    for manifest_path in manifest_paths:
        assert manifest_path.exists()
        data = _load_yaml(manifest_path)
        assert data.get("status") == "ACTIVE"
        entries = data.get("entries", [])
        assert isinstance(entries, list) and entries
        for entry in entries:
            target = REPO_ROOT / entry["path"]
            assert target.exists(), f"Missing manifest target: {target}"


def test_m6_unified_code_modify_workflow_contract_preserved() -> None:
    """Unified template preserves IMPLEMENT/FIX/REFACTOR mode routing and required contracts."""
    path = REPO_ROOT / "cortex-registry/workflows/templates/sdlc/code-modify-unified.yaml"
    assert path.exists()

    data = _load_yaml(path)
    workflow = data["workflow"]

    modes = workflow["mode_discriminator"]["allowed_modes"]
    assert {"IMPLEMENT", "FIX", "REFACTOR"}.issubset(set(modes))

    contracts = workflow["required_contracts"]
    for key in ["workflow_composer_spec", "response_template", "intelligence_injection"]:
        ref_path = REPO_ROOT / contracts[key]
        assert ref_path.exists(), f"Missing required contract file: {ref_path}"


def test_m6_required_injection_and_response_templates_still_present() -> None:
    """Required parity files for GAP-M6-08 remain present."""
    required_paths = [
        ".github/templates/cortex-response-templates.md",
        "cortex-registry/templates/response/_registry.yaml",
        "cortex-registry/workflows/templates/lifecycle/content-library-routing.yaml",
        "cortex-registry/workflows/templates/primitives/intelligence/intelligence-injection.yaml",
    ]

    for relative_path in required_paths:
        assert (REPO_ROOT / relative_path).exists()


def test_m6_cognition_yaml_directory_removed() -> None:
    """Legacy cognition YAML directory no longer exists."""
    cognition_dir = REPO_ROOT / "cortex-registry/knowledge/cognition"
    assert not cognition_dir.exists()
