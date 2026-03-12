"""Tests — GV-028..GV-034 governance rules in capabilities-manifest.yaml (Phase 151-b)

Enforces that all 7 new governance rules are present in the canonical manifest.

CORE: CORE-008 (TDD mandatory)
Source: GitHub Issue #18 — FB-20260312-006, FB-20260312-007
"""

from pathlib import Path

import pytest
import yaml

_MANIFEST = Path(__file__).parent.parent.parent / "cortex-registry" / "core" / "capabilities-manifest.yaml"
_GV_RULES = ("GV-028", "GV-029", "GV-030", "GV-031", "GV-032", "GV-033", "GV-034")


def _load_manifest() -> dict:
    return yaml.safe_load(_MANIFEST.read_text(encoding="utf-8"))


def _get_gv_rule_ids(manifest: dict) -> set:
    governance = manifest.get("governance", {})
    rules = governance.get("governance_rules", [])
    return {r["id"] for r in rules if isinstance(r, dict) and "id" in r}


def test_manifest_yaml_parses_cleanly() -> None:
    """YAML must be parseable without errors."""
    data = _load_manifest()
    assert isinstance(data, dict)


def test_gv028_defined() -> None:
    """GV-028: VACUUM_PROTECTED_ROOTS is immutable frozenset rule is present."""
    ids = _get_gv_rule_ids(_load_manifest())
    assert "GV-028" in ids, f"GV-028 not found. Present: {sorted(ids)}"


def test_gv029_defined() -> None:
    """GV-029: _is_protected() guard rule is present."""
    ids = _get_gv_rule_ids(_load_manifest())
    assert "GV-029" in ids, f"GV-029 not found. Present: {sorted(ids)}"


def test_gv030_defined() -> None:
    """GV-030: Tab renderers require PersonaLayer.adapt() rule is present."""
    ids = _get_gv_rule_ids(_load_manifest())
    assert "GV-030" in ids, f"GV-030 not found. Present: {sorted(ids)}"


def test_gv031_defined() -> None:
    """GV-031: Persona-aware output never raises rule is present."""
    ids = _get_gv_rule_ids(_load_manifest())
    assert "GV-031" in ids, f"GV-031 not found. Present: {sorted(ids)}"


def test_gv032_defined() -> None:
    """GV-032: No tab renderer bypasses DashboardGenerator rule is present."""
    ids = _get_gv_rule_ids(_load_manifest())
    assert "GV-032" in ids, f"GV-032 not found. Present: {sorted(ids)}"


def test_gv033_defined() -> None:
    """GV-033: VACUUM_PROTECTED_ROOTS canonical root guard rule is present."""
    ids = _get_gv_rule_ids(_load_manifest())
    assert "GV-033" in ids, f"GV-033 not found. Present: {sorted(ids)}"


def test_gv034_defined() -> None:
    """GV-034: TabRenderer.render_tab() contract rule is present."""
    ids = _get_gv_rule_ids(_load_manifest())
    assert "GV-034" in ids, f"GV-034 not found. Present: {sorted(ids)}"


def test_all_gv_rules_have_required_fields() -> None:
    """Each GV rule must have id, description, enforcement, and source_phase."""
    manifest = _load_manifest()
    governance = manifest.get("governance", {})
    rules = governance.get("governance_rules", [])
    gv_rules = {r["id"]: r for r in rules if isinstance(r, dict) and r.get("id", "").startswith("GV-0")}
    required_fields = {"id", "description", "enforcement", "source_phase"}
    for rule_id in _GV_RULES:
        assert rule_id in gv_rules, f"{rule_id} missing from governance_rules"
        rule = gv_rules[rule_id]
        missing = required_fields - set(rule.keys())
        assert not missing, f"{rule_id} is missing fields: {missing}"
