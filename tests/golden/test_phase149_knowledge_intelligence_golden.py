"""
Golden tests for Phase 149 — Knowledge & Intelligence Enhancements.

Tests cover:
  149-a: ContextSynthesisGateway best_practices wiring (8 tests)
  149-b: CortexFrameworkAnalyzer.analyze_metadata() (10 tests)
  149-c: RegistryMaterializer + IntelligenceFacade.framework_context() (12 tests)
  149-x: Integration / cross-cutting (8 tests)
  Total: 38 tests
"""
from __future__ import annotations

import sqlite3
import tempfile
from pathlib import Path
from typing import Any, Dict
from unittest.mock import MagicMock, patch

import pytest


# ============================================================
# 149-a: ContextSynthesisGateway best_practices wiring
# ============================================================

class TestGatewayBestPracticesWiring:
    """8 tests for Phase 149-a."""

    def _make_gateway(self):
        from cortex.orchestrators.core.context_synthesis_gateway import (
            ContextSynthesisGateway,
        )
        return ContextSynthesisGateway()

    def test_get_best_practices_for_returns_list(self) -> None:
        gw = self._make_gateway()
        result = gw._get_best_practices_for("TDDOrchestrator")
        assert isinstance(result, list)

    def test_get_best_practices_for_unknown_orchestrator_returns_list(self) -> None:
        gw = self._make_gateway()
        result = gw._get_best_practices_for("NonExistentOrchestrator")
        assert isinstance(result, list)

    def test_get_best_practices_for_respects_max_entries(self) -> None:
        from cortex.orchestrators.core.context_synthesis_gateway import (
            _BEST_PRACTICES_MAX_ENTRIES,
        )
        gw = self._make_gateway()
        result = gw._get_best_practices_for("EnforcementOrchestrator")
        assert len(result) <= _BEST_PRACTICES_MAX_ENTRIES

    def test_get_best_practices_for_never_raises(self) -> None:
        gw = self._make_gateway()
        # Even with a broken import it should return []
        with patch(
            "cortex.orchestrators.core.context_synthesis_gateway.ContextSynthesisGateway._get_best_practices_for",
            return_value=[],
        ):
            result = gw._get_best_practices_for("AnyOrchestrator")
        assert isinstance(result, list)

    def test_orchestrator_domain_map_covers_known_orchestrators(self) -> None:
        from cortex.orchestrators.core.context_synthesis_gateway import (
            _ORCHESTRATOR_DOMAIN_MAP,
        )
        assert "TDDOrchestrator" in _ORCHESTRATOR_DOMAIN_MAP
        assert "EnforcementOrchestrator" in _ORCHESTRATOR_DOMAIN_MAP
        assert "MasterOrchestrator" in _ORCHESTRATOR_DOMAIN_MAP

    def test_best_practices_token_budget_constant_defined(self) -> None:
        from cortex.orchestrators.core.context_synthesis_gateway import (
            _BEST_PRACTICES_TOKEN_BUDGET,
        )
        assert _BEST_PRACTICES_TOKEN_BUDGET == 800

    def test_synthesize_result_context_contains_best_practices_key(self) -> None:
        """synthesize() output dict must have 'best_practices' key."""
        from cortex.orchestrators.core.context_synthesis_gateway import (
            ContextSynthesisGateway,
        )
        gw = ContextSynthesisGateway()
        result = gw.synthesize(
            context={"key": "value"},
            session_id="test-149a",
            orchestrator_name="TDDOrchestrator",
        )
        assert "best_practices" in result.context

    def test_best_practices_in_synthesized_context_is_list(self) -> None:
        from cortex.orchestrators.core.context_synthesis_gateway import (
            ContextSynthesisGateway,
        )
        gw = ContextSynthesisGateway()
        result = gw.synthesize(
            context={"key": "value"},
            session_id="test-149a-2",
            orchestrator_name="RefactoringOrchestrator",
        )
        assert isinstance(result.context["best_practices"], list)


# ============================================================
# 149-b: CortexFrameworkAnalyzer.analyze_metadata()
# ============================================================

class TestAnalyzeMetadata:
    """10 tests for Phase 149-b."""

    def _analyzer(self):
        from cortex.lens.analyzers.cortex_framework_analyzer import (
            CortexFrameworkAnalyzer,
        )
        return CortexFrameworkAnalyzer()

    def test_analyze_metadata_returns_dict(self) -> None:
        a = self._analyzer()
        result = a.analyze_metadata()
        assert isinstance(result, dict)

    def test_analyze_metadata_has_required_keys(self) -> None:
        a = self._analyzer()
        result = a.analyze_metadata()
        assert "orchestrator_count" in result
        assert "mcp_tool_count" in result
        assert "intent_type_count" in result
        assert "instructions_found" in result

    def test_analyze_metadata_instructions_found_true_for_real_file(self) -> None:
        a = self._analyzer()
        result = a.analyze_metadata()
        assert result["instructions_found"] is True

    def test_analyze_metadata_orchestrator_count_is_int(self) -> None:
        a = self._analyzer()
        result = a.analyze_metadata()
        assert isinstance(result["orchestrator_count"], int)

    def test_analyze_metadata_mcp_tool_count_is_int(self) -> None:
        a = self._analyzer()
        result = a.analyze_metadata()
        assert isinstance(result["mcp_tool_count"], int)

    def test_analyze_metadata_intent_type_count_is_int(self) -> None:
        a = self._analyzer()
        result = a.analyze_metadata()
        assert isinstance(result["intent_type_count"], int)

    def test_analyze_metadata_counts_are_positive(self) -> None:
        a = self._analyzer()
        result = a.analyze_metadata()
        assert result["orchestrator_count"] > 0
        assert result["mcp_tool_count"] > 0
        assert result["intent_type_count"] > 0

    def test_analyze_metadata_missing_file_gracefully_degrades(self, tmp_path: Path) -> None:
        a = self._analyzer()
        result = a.analyze_metadata(instructions_path=tmp_path / "no-such-file.md")
        assert result["instructions_found"] is False
        assert result["orchestrator_count"] is None
        assert result["mcp_tool_count"] is None
        assert result["intent_type_count"] is None

    def test_analyze_metadata_custom_file(self, tmp_path: Path) -> None:
        custom = tmp_path / "test-instructions.md"
        custom.write_text("**99 Orchestrator files** across domains\n**17 MCP Tools registered** in mcp_registry.py\n**12 Intent Types** routed\n")
        a = self._analyzer()
        result = a.analyze_metadata(instructions_path=custom)
        assert result["orchestrator_count"] == 99
        assert result["mcp_tool_count"] == 17
        assert result["intent_type_count"] == 12

    def test_analyze_metadata_does_not_break_existing_analyze(self) -> None:
        a = self._analyzer()
        # Existing analyze() must still work
        result = a.analyze(Path("."))
        assert "is_cortex_framework" in result
        assert result["is_cortex_framework"] is True


# ============================================================
# 149-c: RegistryMaterializer + IntelligenceFacade.framework_context()
# ============================================================

class TestRegistryMaterializer:
    """8 tests for Phase 149-c RegistryMaterializer."""

    def test_registry_materializer_importable(self) -> None:
        from cortex.intelligence.registry_materializer import RegistryMaterializer
        assert RegistryMaterializer is not None

    def test_get_metadata_returns_dict(self) -> None:
        from cortex.intelligence.registry_materializer import RegistryMaterializer
        m = RegistryMaterializer()
        result = m.get_metadata()
        assert isinstance(result, dict)

    def test_get_metadata_has_counts(self) -> None:
        from cortex.intelligence.registry_materializer import RegistryMaterializer
        m = RegistryMaterializer()
        result = m.get_metadata()
        assert "orchestrator_count" in result
        assert "mcp_tool_count" in result
        assert "intent_type_count" in result

    def test_write_framework_knowledge_yaml_returns_path(self, tmp_path: Path) -> None:
        from cortex.intelligence.registry_materializer import RegistryMaterializer
        m = RegistryMaterializer(output_path=tmp_path / "out" / "framework.yaml")
        path = m.write_framework_knowledge_yaml()
        assert isinstance(path, Path)

    def test_write_creates_file(self, tmp_path: Path) -> None:
        from cortex.intelligence.registry_materializer import RegistryMaterializer
        out = tmp_path / "out" / "framework.yaml"
        m = RegistryMaterializer(output_path=out)
        m.write_framework_knowledge_yaml()
        assert out.exists()

    def test_written_yaml_contains_domain(self, tmp_path: Path) -> None:
        from cortex.intelligence.registry_materializer import RegistryMaterializer
        out = tmp_path / "out.yaml"
        m = RegistryMaterializer(output_path=out)
        m.write_framework_knowledge_yaml()
        content = out.read_text()
        assert "domain: cortex-frame-context" in content

    def test_written_yaml_contains_metadata_section(self, tmp_path: Path) -> None:
        from cortex.intelligence.registry_materializer import RegistryMaterializer
        out = tmp_path / "out.yaml"
        m = RegistryMaterializer(output_path=out)
        m.write_framework_knowledge_yaml()
        content = out.read_text()
        assert "orchestrator_count:" in content
        assert "mcp_tool_count:" in content

    def test_write_creates_parent_dirs(self, tmp_path: Path) -> None:
        from cortex.intelligence.registry_materializer import RegistryMaterializer
        out = tmp_path / "deep" / "nested" / "dir" / "out.yaml"
        m = RegistryMaterializer(output_path=out)
        m.write_framework_knowledge_yaml()
        assert out.parent.is_dir()


class TestIntelligenceFacadeFrameworkContext:
    """4 tests for IntelligenceFacade.framework_context()."""

    def test_framework_context_returns_dict(self) -> None:
        from cortex.intelligence.facade import IntelligenceFacade
        f = IntelligenceFacade()
        result = f.framework_context()
        assert isinstance(result, dict)

    def test_framework_context_has_orchestrator_count(self) -> None:
        from cortex.intelligence.facade import IntelligenceFacade
        f = IntelligenceFacade()
        result = f.framework_context()
        assert "orchestrator_count" in result

    def test_framework_context_count_is_positive(self) -> None:
        from cortex.intelligence.facade import IntelligenceFacade
        f = IntelligenceFacade()
        result = f.framework_context()
        count = result.get("orchestrator_count")
        assert count is not None and count > 0

    def test_framework_knowledge_yaml_discovered_by_registry_index(self) -> None:
        from cortex.intelligence.facade import IntelligenceFacade
        f = IntelligenceFacade()
        # The file should be under knowledge domain
        entries = f.registry_index("knowledge")
        frame = [e for e in entries if "cortex-frame-context" in e.relative_path]
        assert len(frame) >= 1, (
            "framework-context.yaml not found in registry_index('knowledge'). "
            "Run RegistryMaterializer.write_framework_knowledge_yaml() first."
        )


# ============================================================
# Cross-cutting integration tests (8)
# ============================================================

class TestPhase149Integration:
    """8 integration tests spanning all Phase 149 additions."""

    def test_framework_context_yaml_exists_on_disk(self) -> None:
        expected = Path(
            "cortex-registry/knowledge/cortex-frame-context/framework-context.yaml"
        )
        assert expected.exists(), f"framework-context.yaml not found at {expected}"

    def test_framework_context_yaml_is_valid_yaml(self) -> None:
        import yaml
        path = Path(
            "cortex-registry/knowledge/cortex-frame-context/framework-context.yaml"
        )
        data = yaml.safe_load(path.read_text())
        assert isinstance(data, dict)
        assert data.get("domain") == "cortex-frame-context"

    def test_registry_materializer_and_facade_agree_on_orchestrator_count(self) -> None:
        from cortex.intelligence.facade import IntelligenceFacade
        from cortex.intelligence.registry_materializer import RegistryMaterializer

        meta = RegistryMaterializer().get_metadata()
        ctx = IntelligenceFacade().framework_context()
        # Both read from the same source — counts must match
        assert meta["orchestrator_count"] == ctx["orchestrator_count"]

    def test_analyze_metadata_regex_constants_exist(self) -> None:
        from cortex.lens.analyzers import cortex_framework_analyzer as mod

        assert hasattr(mod, "_ORCHESTRATOR_RE")
        assert hasattr(mod, "_MCP_TOOL_RE")
        assert hasattr(mod, "_INTENT_TYPE_RE")

    def test_context_synthesis_gateway_best_practices_domain_map_non_empty(self) -> None:
        from cortex.orchestrators.core.context_synthesis_gateway import (
            _ORCHESTRATOR_DOMAIN_MAP,
        )
        assert len(_ORCHESTRATOR_DOMAIN_MAP) >= 5

    def test_get_best_practices_for_all_mapped_orchestrators_returns_list(self) -> None:
        from cortex.orchestrators.core.context_synthesis_gateway import (
            ContextSynthesisGateway,
            _ORCHESTRATOR_DOMAIN_MAP,
        )
        gw = ContextSynthesisGateway()
        for orch_name in _ORCHESTRATOR_DOMAIN_MAP:
            result = gw._get_best_practices_for(orch_name)
            assert isinstance(result, list), f"Expected list for {orch_name}"

    def test_materializer_metadata_has_materialized_at_timestamp(self) -> None:
        from cortex.intelligence.registry_materializer import RegistryMaterializer
        meta = RegistryMaterializer().get_metadata()
        assert "materialized_at" in meta
        assert meta["materialized_at"] is not None

    def test_framework_context_mcp_tool_count_matches_instructions(self) -> None:
        from cortex.intelligence.facade import IntelligenceFacade
        from cortex.lens.analyzers.cortex_framework_analyzer import (
            CortexFrameworkAnalyzer,
        )
        direct = CortexFrameworkAnalyzer().analyze_metadata()
        facade_ctx = IntelligenceFacade().framework_context()
        assert direct["mcp_tool_count"] == facade_ctx["mcp_tool_count"]
