"""TDD RED — Phase 103-g: knowledge_synthesis_engine.py decomposition.

GAP-103-07: knowledge_synthesis_engine.py (1,567L) → sub-package with mixins.
CORE-008: tests written before implementation.
"""
# ruff: noqa: S101
from __future__ import annotations

import pathlib
import pytest

KSE_PKG = pathlib.Path("cortex/intelligence/knowledge/knowledge_synthesis_engine")
KSE_FLAT = pathlib.Path("cortex/intelligence/knowledge/knowledge_synthesis_engine.py")


class TestKSEPackageStructure:
    """Verify the sub-package exists with expected modules."""

    def test_kse_is_package_not_flat_file(self) -> None:
        assert KSE_PKG.is_dir(), "knowledge_synthesis_engine/ sub-package not found"
        assert not KSE_FLAT.exists(), "flat knowledge_synthesis_engine.py must be removed"

    @pytest.mark.parametrize("module", [
        "__init__.py",
        "models.py",
        "engine.py",
        "loaders.py",
        "synthesizers.py",
    ])
    def test_expected_module_exists(self, module: str) -> None:
        assert (KSE_PKG / module).exists(), f"knowledge_synthesis_engine/{module} not found"

    def test_engine_under_1000_lines(self) -> None:
        target = KSE_PKG / "engine.py"
        lines = len(target.read_text().splitlines())
        assert lines < 1000, f"engine.py is {lines}L — must be < 1000L"


class TestKSEImports:
    """All public symbols importable from the package."""

    def test_models_importable(self) -> None:
        from cortex.intelligence.knowledge.knowledge_synthesis_engine import (
            KnowledgeSource,
            SynthesizedInstruction,
        )
        assert KnowledgeSource is not None
        assert SynthesizedInstruction is not None

    def test_engine_importable(self) -> None:
        from cortex.intelligence.knowledge.knowledge_synthesis_engine import (
            KnowledgeSynthesisEngine,
        )
        assert KnowledgeSynthesisEngine is not None

    def test_factory_importable(self) -> None:
        from cortex.intelligence.knowledge.knowledge_synthesis_engine import (
            get_synthesis_engine,
        )
        assert callable(get_synthesis_engine)

    def test_backwards_compat_all_symbols(self) -> None:
        import cortex.intelligence.knowledge.knowledge_synthesis_engine as pkg
        expected = [
            "KnowledgeSource", "SynthesizedInstruction",
            "KnowledgeSynthesisEngine", "get_synthesis_engine",
        ]
        for sym in expected:
            assert hasattr(pkg, sym), f"KSE package missing re-export: {sym}"

    def test_engine_instantiates(self) -> None:
        from cortex.intelligence.knowledge.knowledge_synthesis_engine import (
            KnowledgeSynthesisEngine,
        )
        engine = KnowledgeSynthesisEngine()
        assert engine is not None
