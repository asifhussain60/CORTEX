from pathlib import Path

import yaml


MANIFEST_PATH = Path("cortex-registry/core/llm-capabilities.yaml")
REQUIRED_CAPABILITIES = {
    "intent_classification",
    "context_assembly",
    "response_formatting",
    "workflow_sequencing",
    "tdd_enforcement",
    "code_analysis",
    "persona_tone",
    "complexity_assessment",
}
ALLOWED_OWNERS = {"LLM_NATIVE", "CORTEX_OWNED", "HYBRID"}


def _load_manifest() -> dict:
    assert MANIFEST_PATH.exists(), f"Missing manifest: {MANIFEST_PATH}"
    with MANIFEST_PATH.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def test_manifest_yaml_valid():
    manifest = _load_manifest()
    assert isinstance(manifest, dict)


def test_manifest_has_required_sections():
    manifest = _load_manifest()
    assert "capabilities" in manifest
    assert "review_cadence" in manifest
    assert "adaptation_protocol" in manifest


def test_manifest_categories_complete():
    manifest = _load_manifest()
    capabilities = manifest.get("capabilities", {})
    assert REQUIRED_CAPABILITIES.issubset(set(capabilities.keys()))


def test_manifest_boundary_clear():
    manifest = _load_manifest()
    capabilities = manifest.get("capabilities", {})

    for capability_name in REQUIRED_CAPABILITIES:
        capability = capabilities.get(capability_name)
        assert isinstance(capability, dict), f"Missing capability: {capability_name}"
        owner = capability.get("owner")
        assert owner in ALLOWED_OWNERS, (
            f"Invalid owner for {capability_name}: {owner}. "
            f"Allowed owners: {sorted(ALLOWED_OWNERS)}"
        )
