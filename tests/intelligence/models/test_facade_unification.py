"""Phase 107 Sub-Phase C — LENS Merge + Facade Unification.

RED→GREEN→REFACTOR tests for GAP-107-05, GAP-107-06.

Authority: CORE-008 (TDD), CORE-035 (single canonical), CORE-064 (sweep completeness)
Tier: T1 (unit)
"""
from __future__ import annotations

import ast
import pathlib
from typing import List

import pytest

CORTEX_ROOT = pathlib.Path(__file__).parents[3]
INTELLIGENCE_DIR = CORTEX_ROOT / "cortex" / "intelligence"


# ════════════════════════════════════════════════════════════════════════════
# GAP-107-06: Single IntelligenceFacade entry point
# ════════════════════════════════════════════════════════════════════════════

class TestIntelligenceFacade:
    """GAP-107-06: One facade to rule them all — replaces 3 separate entry points."""

    def test_intelligence_facade_importable(self) -> None:
        """IntelligenceFacade must be importable from cortex.intelligence.facade."""
        from cortex.intelligence.facade import IntelligenceFacade
        assert IntelligenceFacade is not None

    def test_facade_has_analyze_method(self) -> None:
        """Facade must expose analyze() for LENS-style code analysis."""
        from cortex.intelligence.facade import IntelligenceFacade
        facade = IntelligenceFacade()
        assert hasattr(facade, "analyze"), "IntelligenceFacade must have analyze() method"
        assert callable(facade.analyze)

    def test_facade_has_synthesize_method(self) -> None:
        """Facade must expose synthesize() for knowledge synthesis."""
        from cortex.intelligence.facade import IntelligenceFacade
        facade = IntelligenceFacade()
        assert hasattr(facade, "synthesize"), "IntelligenceFacade must have synthesize() method"
        assert callable(facade.synthesize)

    def test_facade_has_query_method(self) -> None:
        """Facade must expose query() for knowledge registry queries."""
        from cortex.intelligence.facade import IntelligenceFacade
        facade = IntelligenceFacade()
        assert hasattr(facade, "query"), "IntelligenceFacade must have query() method"
        assert callable(facade.query)

    def test_facade_analyze_returns_dict(self) -> None:
        """facade.analyze() should return a structured dict result."""
        from cortex.intelligence.facade import IntelligenceFacade
        facade = IntelligenceFacade()
        result = facade.analyze(file_path="test.py", intent="IMPLEMENT")
        assert isinstance(result, dict), f"analyze() must return dict, got {type(result)}"
        assert "status" in result, "analyze() result must contain 'status' key"

    def test_facade_synthesize_returns_dict(self) -> None:
        """facade.synthesize() should return a structured dict result."""
        from cortex.intelligence.facade import IntelligenceFacade
        facade = IntelligenceFacade()
        result = facade.synthesize(query="test query")
        assert isinstance(result, dict), f"synthesize() must return dict, got {type(result)}"
        assert "status" in result, "synthesize() result must contain 'status' key"

    def test_facade_query_returns_dict(self) -> None:
        """facade.query() should return a structured dict result."""
        from cortex.intelligence.facade import IntelligenceFacade
        facade = IntelligenceFacade()
        result = facade.query(query="test query")
        assert isinstance(result, dict), f"query() must return dict, got {type(result)}"
        assert "status" in result, "query() result must contain 'status' key"


# ════════════════════════════════════════════════════════════════════════════
# GAP-107-05: LENS compat shims — old import paths must still work
# ════════════════════════════════════════════════════════════════════════════

class TestLENSCompatShims:
    """GAP-107-05: Existing lens/ and knowledge/ import paths must survive."""

    def test_lens_facade_compat_import(self) -> None:
        """from cortex.lens.facade import LENSIntelligenceFacade must still work."""
        from cortex.lens.facade import LENSIntelligenceFacade
        assert LENSIntelligenceFacade is not None

    def test_knowledge_proxy_compat_import(self) -> None:
        """from cortex.knowledge.registry_proxy import KnowledgeRegistryProxy must still work."""
        from cortex.knowledge.registry_proxy import KnowledgeRegistryProxy
        assert KnowledgeRegistryProxy is not None

    def test_provider_compat_import(self) -> None:
        """from cortex.intelligence.provider import UnifiedIntelligenceProvider must still work."""
        from cortex.intelligence.provider import UnifiedIntelligenceProvider
        assert UnifiedIntelligenceProvider is not None

    def test_intelligence_lens_dir_has_no_duplicate_facade(self) -> None:
        """After facade creation, intelligence/lens/ should not define its own facade.

        Full directory removal deferred to Sub-Phase C-2 (too many cross-references
        for a safe single-pass — 30+ files with internal imports).
        For now, verify the LENS dir doesn't create a competing IntelligenceFacade.
        """
        import ast as _ast

        lens_dir = INTELLIGENCE_DIR / "lens"
        if not lens_dir.is_dir():
            return  # Already removed — pass

        for py_file in lens_dir.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
            try:
                tree = _ast.parse(py_file.read_text(encoding="utf-8"))
            except SyntaxError:
                continue
            for node in _ast.walk(tree):
                if isinstance(node, _ast.ClassDef) and node.name == "IntelligenceFacade":
                    pytest.fail(
                        f"GAP-107-05: intelligence/lens/ contains competing "
                        f"IntelligenceFacade in {py_file.relative_to(CORTEX_ROOT)}"
                    )


# ════════════════════════════════════════════════════════════════════════════
# Convergence: Facade is the single recommended entry point
# ════════════════════════════════════════════════════════════════════════════

class TestFacadeConvergence:
    """Convergence tests for Sub-Phase C."""

    def test_single_facade_definition(self) -> None:
        """Exactly 1 class named IntelligenceFacade in cortex/."""
        cortex_dir = CORTEX_ROOT / "cortex"
        definitions: List[str] = []
        for py_file in cortex_dir.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
            try:
                tree = ast.parse(py_file.read_text(encoding="utf-8"))
            except SyntaxError:
                continue
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and node.name == "IntelligenceFacade":
                    definitions.append(str(py_file.relative_to(CORTEX_ROOT)))
        assert len(definitions) == 1, (
            f"Expected exactly 1 IntelligenceFacade, found {len(definitions)}:\n  "
            + "\n  ".join(definitions)
        )

    def test_facade_module_path(self) -> None:
        """IntelligenceFacade must live at cortex/intelligence/facade.py."""
        facade_file = INTELLIGENCE_DIR / "facade.py"
        assert facade_file.exists(), (
            "IntelligenceFacade must be at cortex/intelligence/facade.py"
        )
