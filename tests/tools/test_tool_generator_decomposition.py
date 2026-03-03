"""TDD RED — Phase 103-j: tool_generator.py decomposition.

GAP-103-10: tool_generator.py (1,426L) → sub-package with per-type generators.
CORE-008: tests written before implementation.
"""
# ruff: noqa: S101
from __future__ import annotations

import pathlib
import pytest

TG_PKG = pathlib.Path("cortex/tools/tool_generator")
TG_FLAT = pathlib.Path("cortex/tools/tool_generator.py")


class TestToolGeneratorPackageStructure:

    def test_tg_is_package_not_flat_file(self) -> None:
        assert TG_PKG.is_dir(), "tool_generator/ sub-package not found"
        assert not TG_FLAT.exists(), "flat tool_generator.py must be removed"

    @pytest.mark.parametrize("module", [
        "__init__.py",
        "models.py",
        "generator.py",
        "renderers.py",
    ])
    def test_expected_module_exists(self, module: str) -> None:
        assert (TG_PKG / module).exists(), f"tool_generator/{module} not found"

    def test_generator_under_1000_lines(self) -> None:
        target = TG_PKG / "generator.py"
        lines = len(target.read_text().splitlines())
        assert lines < 1000, f"generator.py is {lines}L — must be < 1000L"


class TestToolGeneratorImports:

    def test_models_importable(self) -> None:
        from cortex.tools.tool_generator import (
            ToolType,
            GenerationConfig,
            GeneratedTool,
            GenerationResult,
        )
        assert ToolType is not None
        assert GenerationConfig is not None
        assert GeneratedTool is not None
        assert GenerationResult is not None

    def test_generator_importable(self) -> None:
        from cortex.tools.tool_generator import ToolGenerator
        assert ToolGenerator is not None

    def test_backwards_compat_all_symbols(self) -> None:
        import cortex.tools.tool_generator as pkg
        expected = [
            "ToolType", "GenerationConfig", "GeneratedTool",
            "GenerationResult", "ToolGenerator",
        ]
        for sym in expected:
            assert hasattr(pkg, sym), f"tool_generator package missing: {sym}"

    def test_generator_instantiates(self) -> None:
        from cortex.tools.tool_generator import ToolGenerator
        gen = ToolGenerator()
        assert gen is not None
