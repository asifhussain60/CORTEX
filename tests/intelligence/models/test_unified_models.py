"""
Sub-Phase A — Unified Intelligence Models: RED tests.

GAP-107-01: Two competing BaseIntelligenceEngine classes (base.py ABC vs base_engine.py concrete)
GAP-107-02: Duplicate SynthesisResult / UnifiedIntelligenceContext across 3+ files

TDD Contract (CORE-008):
  - ALL tests in this file must FAIL before implementation begins.
  - Run: python3 -m pytest tests/intelligence/models/test_unified_models.py -v
  - Expected: ALL RED

Governance:
  - CORE-008: TDD mandatory — RED → GREEN → REFACTOR
  - CORE-035: Single canonical implementation
  - CORE-011: Type hints on all functions
  - CORE-012: Docstrings on all public APIs
"""

from __future__ import annotations

import ast
import pathlib
from dataclasses import fields
from typing import Any, Dict, List

import pytest

# ─────────────────────────────────────────────────────────────────────────────
# MARKER: RED gate — these imports MUST fail until implementation is created
# ─────────────────────────────────────────────────────────────────────────────

# GAP-107-01 ── Single BaseIntelligenceEngine canonical location
def _import_base_engine_from_models():
    """Import BaseIntelligenceEngine from the canonical models package."""
    from cortex.intelligence.models import BaseIntelligenceEngine  # noqa: F401
    return BaseIntelligenceEngine


# GAP-107-02 ── Single canonical data-model location
def _import_analysis_result_from_models():
    from cortex.intelligence.models import AnalysisResult  # noqa: F401
    return AnalysisResult


def _import_analysis_context_from_models():
    from cortex.intelligence.models import AnalysisContext  # noqa: F401
    return AnalysisContext


def _import_engine_metrics_from_models():
    from cortex.intelligence.models import EngineMetrics  # noqa: F401
    return EngineMetrics


def _import_synthesis_result_from_models():
    from cortex.intelligence.models import SynthesisResult  # noqa: F401
    return SynthesisResult


def _import_unified_intelligence_context_from_models():
    from cortex.intelligence.models import UnifiedIntelligenceContext  # noqa: F401
    return UnifiedIntelligenceContext


# ─────────────────────────────────────────────────────────────────────────────
# GROUP 1: canonical import tests (GAP-107-01 + GAP-107-02)
# ─────────────────────────────────────────────────────────────────────────────

class TestCanonicalModelImports:
    """Verify all canonical classes are importable from cortex.intelligence.models."""

    def test_single_base_engine_class_importable_from_models(self) -> None:
        """BaseIntelligenceEngine must be importable from cortex.intelligence.models.

        RED: cortex/intelligence/models/ package does not exist yet.
        GREEN: Create models/__init__.py exporting BaseIntelligenceEngine.
        """
        cls = _import_base_engine_from_models()
        assert cls is not None
        assert cls.__name__ == "BaseIntelligenceEngine"

    def test_analysis_result_importable_from_models(self) -> None:
        """AnalysisResult must be importable from cortex.intelligence.models.

        RED: models package missing.
        """
        cls = _import_analysis_result_from_models()
        assert cls is not None
        assert cls.__name__ == "AnalysisResult"

    def test_analysis_context_importable_from_models(self) -> None:
        """AnalysisContext must be importable from cortex.intelligence.models.

        RED: models package missing.
        """
        cls = _import_analysis_context_from_models()
        assert cls is not None
        assert cls.__name__ == "AnalysisContext"

    def test_engine_metrics_importable_from_models(self) -> None:
        """EngineMetrics must be importable from cortex.intelligence.models.

        RED: models package missing.
        """
        cls = _import_engine_metrics_from_models()
        assert cls is not None
        assert cls.__name__ == "EngineMetrics"

    def test_synthesis_result_importable_from_models(self) -> None:
        """SynthesisResult must be importable from cortex.intelligence.models.

        RED: models package missing.
        """
        cls = _import_synthesis_result_from_models()
        assert cls is not None
        assert cls.__name__ == "SynthesisResult"

    def test_unified_intelligence_context_importable_from_models(self) -> None:
        """UnifiedIntelligenceContext must be importable from cortex.intelligence.models.

        RED: models package missing.
        """
        cls = _import_unified_intelligence_context_from_models()
        assert cls is not None
        assert cls.__name__ == "UnifiedIntelligenceContext"


# ─────────────────────────────────────────────────────────────────────────────
# GROUP 2: single-definition enforcement (GAP-107-01 + GAP-107-02)
# ─────────────────────────────────────────────────────────────────────────────

class TestSingleDefinitionEnforcement:
    """Verify CORE-035: exactly one definition per class across all cortex/ source."""

    CORTEX_ROOT = pathlib.Path(__file__).parents[3] / "cortex"

    def _count_class_definitions(self, class_name: str) -> list[str]:
        """AST-scan cortex/ for all definitions of a given class name."""
        locations: list[str] = []
        for py_file in self.CORTEX_ROOT.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
            try:
                tree = ast.parse(py_file.read_text(encoding="utf-8"))
            except SyntaxError:
                continue
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and node.name == class_name:
                    locations.append(str(py_file.relative_to(self.CORTEX_ROOT.parent)))
        return locations

    def test_single_base_intelligence_engine_class_exists(self) -> None:
        """Exactly 1 BaseIntelligenceEngine class must exist across cortex/.

        RED: 2 definitions — base.py (ABC) and base_engine.py (concrete).
        GREEN: Merge into cortex/intelligence/models/base_engine.py; compat shims in old files.
        """
        locations = self._count_class_definitions("BaseIntelligenceEngine")
        assert len(locations) == 1, (
            f"CORE-035 violation: {len(locations)} BaseIntelligenceEngine definitions found.\n"
            f"Locations: {locations}\n"
            "Expected: exactly 1 in cortex/intelligence/models/base_engine.py"
        )

    def test_single_synthesis_result_definition(self) -> None:
        """The intelligence-domain SynthesisResult must live only in cortex/intelligence/models/.

        Scope: cortex/intelligence/ subdirectory only.
        - cortex/models/synthesis_result.py — permitted (GAP-80-04 superset canonical)
        - cortex/core/ conversation/context synthesizers — out of scope (different domain)
        - cortex/intelligence/tier3/ — MUST be eliminated (same domain, CORE-035 violation)

        RED: tier3/knowledge/synthesis_engine.py also defines SynthesisResult.
        GREEN: tier3 version is a different struct (with 'query' field) — rename to
               KnowledgeSynthesisResult to eliminate the name collision.
        """
        # Only scan cortex/intelligence/ for this check (scoped to intelligence domain)
        intelligence_root = self.CORTEX_ROOT / "intelligence"
        locations: list[str] = []
        for py_file in intelligence_root.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
            try:
                tree = ast.parse(py_file.read_text(encoding="utf-8"))
            except SyntaxError:
                continue
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and node.name == "SynthesisResult":
                    locations.append(str(py_file.relative_to(self.CORTEX_ROOT.parent)))

        assert len(locations) == 1, (
            f"CORE-035 violation: {len(locations)} SynthesisResult definitions in intelligence/:\n"
            f"  Locations: {locations}\n"
            "Expected exactly 1: cortex/intelligence/models/context.py\n"
            "Fix: rename tier3/knowledge/synthesis_engine.SynthesisResult → KnowledgeSynthesisResult"
        )
        assert any("models" in loc for loc in locations), (
            f"SynthesisResult must live in cortex/intelligence/models/. Found: {locations}"
        )

    def test_single_unified_intelligence_context_definition(self) -> None:
        """Exactly 1 UnifiedIntelligenceContext class must exist across cortex/.

        RED: May be a single definition already — test validates state is maintained post-merge.
        GREEN: Confirm location is cortex/intelligence/models/context.py.
        """
        locations = self._count_class_definitions("UnifiedIntelligenceContext")
        assert len(locations) == 1, (
            f"CORE-035 violation: {len(locations)} UnifiedIntelligenceContext definitions.\n"
            f"Locations: {locations}\n"
            "Expected: exactly 1 in cortex/intelligence/models/context.py"
        )
        # After GREEN: must be in models/
        assert any("models" in loc for loc in locations), (
            f"UnifiedIntelligenceContext must live in cortex/intelligence/models/. "
            f"Found: {locations}"
        )

    def test_single_engine_metrics_definition(self) -> None:
        """Exactly 1 EngineMetrics class must exist across cortex/.

        RED: Currently in base_engine.py only; after merge must be in models/.
        GREEN: Move to models/base_engine.py.
        """
        locations = self._count_class_definitions("EngineMetrics")
        assert len(locations) == 1, (
            f"CORE-035 violation: {len(locations)} EngineMetrics definitions.\n"
            f"Locations: {locations}"
        )
        assert any("models" in loc for loc in locations), (
            f"EngineMetrics must live in cortex/intelligence/models/. Found: {locations}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# GROUP 3: merged BaseIntelligenceEngine contract (GAP-107-01)
# ─────────────────────────────────────────────────────────────────────────────

class TestMergedBaseEngineContract:
    """Verify the merged BaseIntelligenceEngine satisfies both source contracts.

    Source 1 (base.py ABC): abstract analyze(AnalysisContext) + validate_context()
    Source 2 (base_engine.py): caching, metrics, enable/disable, _execute()
    Merged: must honour BOTH contracts simultaneously.
    """

    def test_merged_engine_is_abstract(self) -> None:
        """Merged BaseIntelligenceEngine must remain abstract (cannot be instantiated directly).

        RED: models/ package missing; ABC contract not yet merged.
        """
        import inspect
        cls = _import_base_engine_from_models()
        assert inspect.isabstract(cls), (
            "BaseIntelligenceEngine must be abstract — direct instantiation must raise TypeError"
        )

    def test_merged_engine_has_analyze_abstract_method(self) -> None:
        """Merged engine must expose abstract analyze() method.

        RED: models/ package missing.
        """
        cls = _import_base_engine_from_models()
        assert hasattr(cls, "analyze"), "BaseIntelligenceEngine must have analyze() method"

    def test_merged_engine_has_validate_context_abstract_method(self) -> None:
        """Merged engine must expose abstract validate_context() method.

        RED: models/ package missing.
        """
        cls = _import_base_engine_from_models()
        assert hasattr(cls, "validate_context"), (
            "BaseIntelligenceEngine must have validate_context() method"
        )

    def test_merged_engine_has_caching_interface(self) -> None:
        """Merged engine must expose clear_cache() and get_metrics() from base_engine.py.

        RED: models/ package missing.
        """
        cls = _import_base_engine_from_models()
        assert hasattr(cls, "clear_cache"), "BaseIntelligenceEngine must have clear_cache()"
        assert hasattr(cls, "get_metrics"), "BaseIntelligenceEngine must have get_metrics()"

    def test_merged_engine_has_enable_disable(self) -> None:
        """Merged engine must expose enable() / disable() from base_engine.py.

        RED: models/ package missing.
        """
        cls = _import_base_engine_from_models()
        assert hasattr(cls, "enable"), "BaseIntelligenceEngine must have enable()"
        assert hasattr(cls, "disable"), "BaseIntelligenceEngine must have disable()"

    def test_merged_engine_concrete_subclass_instantiates(self) -> None:
        """A concrete subclass of merged BaseIntelligenceEngine must instantiate cleanly.

        RED: models/ package missing.
        """
        from pathlib import Path
        cls = _import_base_engine_from_models()
        AnalysisContext = _import_analysis_context_from_models()
        AnalysisResult = _import_analysis_result_from_models()

        class ConcreteEngine(cls):  # type: ignore[misc]
            def analyze(self, context: AnalysisContext) -> AnalysisResult:
                return AnalysisResult(engine_name="test", data={}, metadata={})

            def validate_context(self, context: AnalysisContext) -> bool:
                return True

        engine = ConcreteEngine(name="test-engine", version="1.0.0")
        assert engine is not None
        assert engine.is_enabled()


# ─────────────────────────────────────────────────────────────────────────────
# GROUP 4: AnalysisResult and AnalysisContext dataclass contracts
# ─────────────────────────────────────────────────────────────────────────────

class TestModelDataclassContracts:
    """Verify canonical dataclass field contracts are preserved in the merged models."""

    def test_analysis_result_has_required_fields(self) -> None:
        """AnalysisResult must retain: engine_name, data, metadata, cache_hit.

        RED: models/ package missing.
        """
        cls = _import_analysis_result_from_models()
        field_names = {f.name for f in fields(cls)}
        required = {"engine_name", "data", "metadata", "cache_hit"}
        assert required.issubset(field_names), (
            f"AnalysisResult missing fields: {required - field_names}"
        )

    def test_analysis_context_has_required_fields(self) -> None:
        """AnalysisContext must retain: file_path, workspace_root, additional_files, config.

        RED: models/ package missing.
        """
        cls = _import_analysis_context_from_models()
        field_names = {f.name for f in fields(cls)}
        required = {"file_path", "workspace_root", "additional_files", "config"}
        assert required.issubset(field_names), (
            f"AnalysisContext missing fields: {required - field_names}"
        )

    def test_engine_metrics_has_required_fields(self) -> None:
        """EngineMetrics must retain: invocations, cache_hits, cache_misses, errors.

        RED: models/ package missing.
        """
        cls = _import_engine_metrics_from_models()
        field_names = {f.name for f in fields(cls)}
        required = {"invocations", "cache_hits", "cache_misses", "errors"}
        assert required.issubset(field_names), (
            f"EngineMetrics missing fields: {required - field_names}"
        )

    def test_synthesis_result_canonical_has_merged_rules_field(self) -> None:
        """The canonical SynthesisResult (from unified_intelligence_context.py) has merged_rules.

        RED: models/ package missing — after GREEN, only this SynthesisResult should exist.
        Note: tier3 SynthesisResult has 'query' field instead — it must be deleted.
        """
        cls = _import_synthesis_result_from_models()
        field_names = {f.name for f in fields(cls)}
        # The CANONICAL version (unified_intelligence_context.py) has these fields
        assert "merged_rules" in field_names, (
            f"SynthesisResult in models must be the canonical version (with merged_rules). "
            f"Got fields: {field_names}. "
            "Check: the tier3 duplicate (with 'query' field) must be deleted."
        )


# ─────────────────────────────────────────────────────────────────────────────
# GROUP 5: backward-compatible compat shims (GAP-107-01 + GAP-107-02)
# ─────────────────────────────────────────────────────────────────────────────

class TestCompatShims:
    """Verify old import paths continue to work via compat re-exports.

    Zero breaking changes: any caller using the old import paths must continue to work.
    Compat shims are re-export stubs only — no logic duplication.
    """

    def test_base_py_compat_shim_exports_base_engine(self) -> None:
        """'from cortex.intelligence.base import BaseIntelligenceEngine' must still work.

        RED: models/ package missing — shim not yet updated.
        GREEN: cortex/intelligence/base.py becomes: from cortex.intelligence.models import BaseIntelligenceEngine
        """
        from cortex.intelligence.base import BaseIntelligenceEngine as ViaOldPath  # noqa
        from cortex.intelligence.models import BaseIntelligenceEngine as ViaNewPath  # noqa
        assert ViaOldPath is ViaNewPath, (
            "cortex.intelligence.base.BaseIntelligenceEngine must be the SAME object "
            "as cortex.intelligence.models.BaseIntelligenceEngine (compat re-export, not a copy)"
        )

    def test_base_engine_py_compat_shim_exports_base_engine(self) -> None:
        """'from cortex.intelligence.base_engine import BaseIntelligenceEngine' must still work.

        RED: models/ package missing — shim not yet updated.
        GREEN: cortex/intelligence/base_engine.py becomes: from cortex.intelligence.models import ...
        """
        from cortex.intelligence.base_engine import BaseIntelligenceEngine as ViaOldPath  # noqa
        from cortex.intelligence.models import BaseIntelligenceEngine as ViaNewPath  # noqa
        assert ViaOldPath is ViaNewPath, (
            "cortex.intelligence.base_engine.BaseIntelligenceEngine must be the SAME object "
            "as cortex.intelligence.models.BaseIntelligenceEngine"
        )

    def test_base_engine_py_compat_shim_exports_engine_metrics(self) -> None:
        """'from cortex.intelligence.base_engine import EngineMetrics' must still work.

        RED: models/ package missing.
        """
        from cortex.intelligence.base_engine import EngineMetrics as ViaOldPath  # noqa
        from cortex.intelligence.models import EngineMetrics as ViaNewPath  # noqa
        assert ViaOldPath is ViaNewPath, (
            "cortex.intelligence.base_engine.EngineMetrics must be the SAME object "
            "as cortex.intelligence.models.EngineMetrics"
        )

    def test_knowledge_module_compat_shim_exports_synthesis_result(self) -> None:
        """'from cortex.intelligence.knowledge.unified_intelligence_context import SynthesisResult' must work.

        RED: models/ package missing; SynthesisResult not yet moved to models/.
        GREEN: unified_intelligence_context.py re-exports from models/context.py.
        """
        from cortex.intelligence.knowledge.unified_intelligence_context import (  # noqa
            SynthesisResult as ViaOldPath,
        )
        from cortex.intelligence.models import SynthesisResult as ViaNewPath  # noqa
        assert ViaOldPath is ViaNewPath, (
            "unified_intelligence_context.SynthesisResult must be the SAME object "
            "as cortex.intelligence.models.SynthesisResult (compat re-export)"
        )

    def test_knowledge_module_compat_shim_exports_unified_context(self) -> None:
        """'from cortex.intelligence.knowledge.unified_intelligence_context import UnifiedIntelligenceContext' works.

        RED: models/ package missing.
        GREEN: unified_intelligence_context.py re-exports from models/context.py.
        """
        from cortex.intelligence.knowledge.unified_intelligence_context import (  # noqa
            UnifiedIntelligenceContext as ViaOldPath,
        )
        from cortex.intelligence.models import UnifiedIntelligenceContext as ViaNewPath  # noqa
        assert ViaOldPath is ViaNewPath, (
            "unified_intelligence_context.UnifiedIntelligenceContext must be the SAME object "
            "as cortex.intelligence.models.UnifiedIntelligenceContext"
        )


# ─────────────────────────────────────────────────────────────────────────────
# GROUP 6: models package structure integrity
# ─────────────────────────────────────────────────────────────────────────────

class TestModelsPackageStructure:
    """Verify the models package exposes its public API via __init__.py."""

    MODELS_PATH = pathlib.Path(__file__).parents[3] / "cortex" / "intelligence" / "models"

    def test_models_package_directory_exists(self) -> None:
        """cortex/intelligence/models/ directory must exist.

        RED: directory does not exist yet.
        GREEN: mkdir cortex/intelligence/models/ + create __init__.py.
        """
        assert self.MODELS_PATH.is_dir(), (
            f"cortex/intelligence/models/ directory does not exist. "
            "Create it as part of Sub-Phase A implementation."
        )

    def test_models_package_has_init(self) -> None:
        """cortex/intelligence/models/__init__.py must exist.

        RED: package not created yet.
        """
        init_file = self.MODELS_PATH / "__init__.py"
        assert init_file.exists(), (
            "cortex/intelligence/models/__init__.py is missing. "
            "Create it to make models/ a proper Python package."
        )

    def test_models_package_exposes_all_canonical_classes(self) -> None:
        """cortex.intelligence.models must export all canonical classes via __init__.py.

        RED: package missing.
        GREEN: __init__.py has explicit exports for all 6 canonical classes.
        """
        import cortex.intelligence.models as m  # noqa: F401
        expected_exports = [
            "BaseIntelligenceEngine",
            "AnalysisResult",
            "AnalysisContext",
            "EngineMetrics",
            "SynthesisResult",
            "UnifiedIntelligenceContext",
        ]
        for name in expected_exports:
            assert hasattr(m, name), (
                f"cortex.intelligence.models does not export '{name}'. "
                f"Add to cortex/intelligence/models/__init__.py"
            )

    def test_models_init_has_all_in_dunder(self) -> None:
        """cortex.intelligence.models.__all__ must list all public canonical classes.

        RED: package missing.
        GREEN: Define __all__ in models/__init__.py.
        """
        import cortex.intelligence.models as m  # noqa: F401
        assert hasattr(m, "__all__"), "cortex.intelligence.models must define __all__"
        all_exports = set(m.__all__)
        required = {
            "BaseIntelligenceEngine",
            "AnalysisResult",
            "AnalysisContext",
            "EngineMetrics",
            "SynthesisResult",
            "UnifiedIntelligenceContext",
        }
        missing = required - all_exports
        assert not missing, (
            f"cortex.intelligence.models.__all__ is missing: {missing}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# GROUP 7: ruff F811 compliance — no duplicate method definitions in models
# ─────────────────────────────────────────────────────────────────────────────

class TestRuffF811Compliance:
    """Verify models/ has zero F811 (duplicate function/class definitions).

    This is a governance check — ruff F811 violations are P0.
    """

    MODELS_PATH = pathlib.Path(__file__).parents[3] / "cortex" / "intelligence" / "models"

    def test_no_f811_violations_in_models_package(self) -> None:
        """ruff check cortex/intelligence/models/ --select=F811 must return zero violations.

        RED: models/ package missing — ruff scan returns file-not-found.
        GREEN: After implementation, ruff must pass cleanly.
        """
        import subprocess
        result = subprocess.run(
            ["python3", "-m", "ruff", "check",
             str(self.MODELS_PATH),
             "--select=F811",
             "--output-format=concise"],
            capture_output=True,
            text=True,
            cwd=str(self.MODELS_PATH.parents[3]),
        )
        if not self.MODELS_PATH.is_dir():
            pytest.fail(
                "cortex/intelligence/models/ does not exist — cannot run ruff. "
                "Create the models package first."
            )
        assert result.returncode == 0, (
            f"ruff F811 violations found in models/:\n{result.stdout}\n{result.stderr}"
        )
