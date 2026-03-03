"""TDD RED — Phase 103-i: orchestrator_scaffolder.py decomposition.

GAP-103-09: orchestrator_scaffolder.py (1,455L) → sub-package with renderers.
CORE-008: tests written before implementation.
"""
# ruff: noqa: S101
from __future__ import annotations

import pathlib
import pytest

OS_PKG = pathlib.Path("cortex/tools/orchestrator_scaffolder")
OS_FLAT = pathlib.Path("cortex/tools/orchestrator_scaffolder.py")


class TestOrchestratorScaffolderPackageStructure:

    def test_os_is_package_not_flat_file(self) -> None:
        assert OS_PKG.is_dir(), "orchestrator_scaffolder/ sub-package not found"
        assert not OS_FLAT.exists(), "flat orchestrator_scaffolder.py must be removed"

    @pytest.mark.parametrize("module", [
        "__init__.py",
        "models.py",
        "scaffolder.py",
        "renderers.py",
    ])
    def test_expected_module_exists(self, module: str) -> None:
        assert (OS_PKG / module).exists(), f"orchestrator_scaffolder/{module} not found"

    def test_scaffolder_under_1000_lines(self) -> None:
        target = OS_PKG / "scaffolder.py"
        lines = len(target.read_text().splitlines())
        assert lines < 1000, f"scaffolder.py is {lines}L — must be < 1000L"


class TestOrchestratorScaffolderImports:

    def test_models_importable(self) -> None:
        from cortex.tools.orchestrator_scaffolder import (
            ScaffoldType,
            ScaffoldConfig,
            ScaffoldedFile,
            ScaffoldResult,
        )
        assert ScaffoldType is not None
        assert ScaffoldConfig is not None
        assert ScaffoldedFile is not None
        assert ScaffoldResult is not None

    def test_scaffolder_importable(self) -> None:
        from cortex.tools.orchestrator_scaffolder import OrchestratorScaffolder
        assert OrchestratorScaffolder is not None

    def test_backwards_compat_all_symbols(self) -> None:
        import cortex.tools.orchestrator_scaffolder as pkg
        expected = [
            "ScaffoldType", "ScaffoldConfig", "ScaffoldedFile",
            "ScaffoldResult", "OrchestratorScaffolder",
        ]
        for sym in expected:
            assert hasattr(pkg, sym), f"orchestrator_scaffolder package missing: {sym}"
