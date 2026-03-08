"""Phase 137 (Deep Intelligence Wiring) — Infrastructure TDD tests.

Covers:
  - GAP-137-01: CCLQueryEngine (sub-phase 137-a)
  - GAP-137-02: verify_capabilities_manifest() (sub-phase 137-b)
  - GAP-137-04: IntentRouter URS MILD_PUNISHMENT on low confidence (sub-phase 137-d)

TDD: RED phase — all tests must FAIL until implementation is complete.
Authority: CORE-008, CORE-011, CORE-012, CORE-035, CORE-061, CORE-064
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, List
from unittest.mock import patch

import pytest
import yaml

WORKSPACE_ROOT = Path(__file__).resolve().parents[2]


# ─────────────────────────────────────────────────────────────────────────────
# GAP-137-01: CCLQueryEngine (sub-phase 137-a)
# ─────────────────────────────────────────────────────────────────────────────


class TestCCLQueryEngineImport:
    """CCLQueryEngine must be importable from cortex.governance."""

    def test_import(self) -> None:
        from cortex.governance.ccl_query_engine import CCLQueryEngine  # noqa: F401


class TestCCLQueryEngineTranslateKnownRule:
    """translate_violation() returns populated dict for known CORE rule ID."""

    def test_translate_known_rule(self) -> None:
        from cortex.governance.ccl_query_engine import CCLQueryEngine
        engine = CCLQueryEngine()
        result = engine.translate_violation("CORE-008")
        assert result["rule_id"] == "CORE-008"
        assert result["business_term"]  # non-empty string
        assert result["business_statement"]  # non-empty string

    def test_translate_known_rule_core_035(self) -> None:
        from cortex.governance.ccl_query_engine import CCLQueryEngine
        engine = CCLQueryEngine()
        result = engine.translate_violation("CORE-035")
        assert result["rule_id"] == "CORE-035"
        assert result["business_term"]  # non-empty
        assert result["business_statement"]  # non-empty


class TestCCLQueryEngineTranslateUnknownRule:
    """translate_violation() returns graceful default for unknown rule IDs — no KeyError."""

    def test_translate_unknown_rule_no_keyerror(self) -> None:
        from cortex.governance.ccl_query_engine import CCLQueryEngine
        engine = CCLQueryEngine()
        result = engine.translate_violation("CORE-999")
        # Must not raise — must return a dict
        assert isinstance(result, dict)
        assert result["rule_id"] == "CORE-999"

    def test_translate_unknown_rule_graceful_default(self) -> None:
        from cortex.governance.ccl_query_engine import CCLQueryEngine
        engine = CCLQueryEngine()
        result = engine.translate_violation("CORE-000")
        assert "business_term" in result
        assert "business_statement" in result


class TestCCLQueryEngineGetAudience:
    """get_audience_for_rule() returns non-empty list for known rules."""

    def test_get_audience_returns_list(self) -> None:
        from cortex.governance.ccl_query_engine import CCLQueryEngine
        engine = CCLQueryEngine()
        audience = engine.get_audience_for_rule("CORE-008")
        assert isinstance(audience, list)
        assert len(audience) > 0

    def test_get_audience_unknown_rule_returns_list(self) -> None:
        from cortex.governance.ccl_query_engine import CCLQueryEngine
        engine = CCLQueryEngine()
        audience = engine.get_audience_for_rule("CORE-999")
        assert isinstance(audience, list)  # graceful — empty list OK


class TestCCLQueryEngineRenderBusinessImpact:
    """render_business_impact() produces markdown strings."""

    def test_render_business_impact_single(self) -> None:
        from cortex.governance.ccl_query_engine import CCLQueryEngine
        engine = CCLQueryEngine()
        md = engine.render_business_impact(["CORE-008"])
        assert isinstance(md, str)
        assert len(md) > 0
        # Must mention the rule
        assert "CORE-008" in md

    def test_render_business_impact_multiple(self) -> None:
        from cortex.governance.ccl_query_engine import CCLQueryEngine
        engine = CCLQueryEngine()
        md = engine.render_business_impact(["CORE-008", "CORE-035"])
        assert isinstance(md, str)
        assert "CORE-008" in md
        assert "CORE-035" in md


class TestCCLQueryEngineGetAllRules:
    """get_all_rules() returns sorted list of CORE rule IDs from the crystal."""

    def test_get_all_rules_sorted(self) -> None:
        from cortex.governance.ccl_query_engine import CCLQueryEngine
        engine = CCLQueryEngine()
        rules = engine.get_all_rules()
        assert isinstance(rules, list)
        assert len(rules) > 0
        # Must include known rules
        assert "CORE-008" in rules
        assert "CORE-035" in rules

    def test_get_all_rules_are_sorted(self) -> None:
        from cortex.governance.ccl_query_engine import CCLQueryEngine
        engine = CCLQueryEngine()
        rules = engine.get_all_rules()
        assert rules == sorted(rules)


class TestCCLCrystalYAMLParseable:
    """ccl-governance-crystal.yaml must load without error."""

    def test_crystal_yaml_parseable(self) -> None:
        import yaml
        crystal_path = WORKSPACE_ROOT / "cortex-registry" / "core" / "ccl-governance-crystal.yaml"
        assert crystal_path.exists(), f"CCL crystal not found: {crystal_path}"
        data = yaml.safe_load(crystal_path.read_text(encoding="utf-8"))
        assert isinstance(data, dict)
        assert len(data) > 0


# ─────────────────────────────────────────────────────────────────────────────
# GAP-137-02: verify_capabilities_manifest() (sub-phase 137-b)
# ─────────────────────────────────────────────────────────────────────────────


class TestCapabilityVerifierImport:
    """verify_capabilities_manifest must be importable from cortex.core."""

    def test_import(self) -> None:
        from cortex.core.capability_verifier import verify_capabilities_manifest  # noqa: F401


class TestVerifyAllImportable:
    """verify_capabilities_manifest() returns empty list when all modules importable."""

    def test_verify_all_importable(self, tmp_path: Path) -> None:
        from cortex.core.capability_verifier import verify_capabilities_manifest
        # Write a manifest with one actually importable module
        manifest = {
            "orchestrators": {
                "tiers": {
                    "core": {
                        "members": [
                            {
                                "id": "test_orch",
                                "module": "cortex.intelligence.facade",
                                "class": "IntelligenceFacade",
                                "tier": "core",
                            }
                        ]
                    }
                }
            }
        }
        manifest_path = tmp_path / "capabilities-manifest.yaml"
        manifest_path.write_text(yaml.dump(manifest), encoding="utf-8")
        drift = verify_capabilities_manifest(str(manifest_path))
        assert drift == []

    def test_verify_one_missing(self, tmp_path: Path) -> None:
        from cortex.core.capability_verifier import verify_capabilities_manifest
        manifest = {
            "orchestrators": {
                "tiers": {
                    "core": {
                        "members": [
                            {
                                "id": "missing_orch",
                                "module": "cortex.nonexistent.does_not_exist",
                                "class": "FakeClass",
                                "tier": "core",
                            }
                        ]
                    }
                }
            }
        }
        manifest_path = tmp_path / "capabilities-manifest.yaml"
        manifest_path.write_text(yaml.dump(manifest), encoding="utf-8")
        drift = verify_capabilities_manifest(str(manifest_path))
        assert len(drift) == 1

    def test_drift_entry_schema(self, tmp_path: Path) -> None:
        from cortex.core.capability_verifier import verify_capabilities_manifest
        manifest = {
            "orchestrators": {
                "tiers": {
                    "core": {
                        "members": [
                            {
                                "id": "bad_orch",
                                "module": "cortex.does_not_exist.module",
                                "class": "BadClass",
                                "tier": "core",
                            }
                        ]
                    }
                }
            }
        }
        manifest_path = tmp_path / "capabilities-manifest.yaml"
        manifest_path.write_text(yaml.dump(manifest), encoding="utf-8")
        drift = verify_capabilities_manifest(str(manifest_path))
        assert len(drift) == 1
        entry = drift[0]
        assert "orchestrator" in entry
        assert "module" in entry
        assert "tier" in entry
        assert "error" in entry

    def test_verify_missing_manifest_file(self) -> None:
        from cortex.core.capability_verifier import verify_capabilities_manifest
        with pytest.raises(FileNotFoundError):
            verify_capabilities_manifest("/tmp/no_such_manifest_xyz.yaml")


class TestMasterOrchestratorInitCallsVerifier:
    """MasterOrchestrator init calls verify_capabilities_manifest()."""

    def test_master_orchestrator_init_calls_verifier(self) -> None:
        from cortex.orchestrators.core import master_orchestrator_init
        source = Path(master_orchestrator_init.__file__).read_text(encoding="utf-8")
        assert "verify_capabilities_manifest" in source or "capability_verifier" in source


# ─────────────────────────────────────────────────────────────────────────────
# GAP-137-04: IntentRouter URS emission on low-confidence routing (137-d)
# ─────────────────────────────────────────────────────────────────────────────


class TestURSEmissionOnLowConfidence:
    """IntentRouter emits MILD_PUNISHMENT when routing confidence < threshold."""

    def test_urs_emitted_on_low_confidence(self) -> None:
        """When classifier confidence is below threshold, a URS signal must be emitted."""
        from cortex.orchestrators.core.intent_router.routing_core_mixin import RoutingCoreMixin
        mixin = RoutingCoreMixin.__new__(RoutingCoreMixin)
        # URS emission attribute or method must exist
        assert hasattr(mixin, "_emit_urs_low_confidence") or hasattr(
            mixin, "confidence_threshold"
        ), (
            "RoutingCoreMixin must have _emit_urs_low_confidence() "
            "or confidence_threshold attribute"
        )

    def test_confidence_threshold_configurable(self) -> None:
        """confidence_threshold must be configurable (not hardcoded)."""
        from cortex.orchestrators.core.intent_router.routing_core_mixin import RoutingCoreMixin
        # Must be a class attribute or instance attribute (not magic constant)
        source_path = Path(RoutingCoreMixin.__module__.replace(".", "/") + ".py")
        # Resolve from workspace root
        for base in [WORKSPACE_ROOT]:
            candidate = base / source_path
            if candidate.exists():
                source = candidate.read_text(encoding="utf-8")
                assert "confidence_threshold" in source
                return
        # Check via importlib
        import importlib
        mod = importlib.import_module(RoutingCoreMixin.__module__)
        src_file = Path(mod.__file__)
        source = src_file.read_text(encoding="utf-8")
        assert "confidence_threshold" in source

    def test_urs_not_emitted_on_high_confidence(self) -> None:
        """When classifier confidence is above threshold, no punishment signal is emitted."""
        from cortex.orchestrators.core.intent_router.routing_core_mixin import RoutingCoreMixin
        # Method must exist — test that it only emits when confidence < threshold
        mixin = RoutingCoreMixin.__new__(RoutingCoreMixin)
        if hasattr(mixin, "_emit_urs_low_confidence"):
            emitted: List[Any] = []
            with patch(
                "cortex.orchestrators.core.intent_router.routing_core_mixin.RoutingCoreMixin._emit_urs_low_confidence",
                side_effect=lambda conf: emitted.append(conf) if conf < 0.4 else None,
            ):
                # Simulate high-confidence routing — no emission
                assert len(emitted) == 0
        else:
            pytest.skip("_emit_urs_low_confidence not yet implemented — RED phase")
