"""
Phase 117-c — Intelligence Diamond Shape Tests

GAP-117-08: cortex/intelligence/ must have ≤8 top-level subdirectories
GAP-117-09: ≤5 top-level .py files (facade, provider, base, base_engine, __init__)
GAP-117-10: capability_matcher.py is already a compat shim (verified passing)

TDD cycle: RED written first, GREEN applied by restructure.
Authority: phase-117-c, CORE-008, CORE-035, CORE-064
"""
from __future__ import annotations

import ast
import importlib
import pathlib
import sys

import pytest

PROJECT_ROOT = pathlib.Path(__file__).parents[2]
INTELLIGENCE_ROOT = PROJECT_ROOT / "cortex" / "intelligence"

# ─── Allowed top-level .py files (canonical set) ─────────────────────────────
_ALLOWED_TOP_LEVEL_PY = {
    "__init__.py",
    "facade.py",
    "provider.py",
    "base.py",
    "base_engine.py",
}

# ─── Target diamond subdirectory names ───────────────────────────────────────
_DIAMOND_DIRS = {"analysis", "knowledge", "learning", "models", "llm"}


class TestDiamondSubdirCount:
    """GAP-117-08: intelligence/ subdirectory count reduction toward ≤8 diamond shape.

    Phase 117-c delivers the analysis/ package creation and top-level .py file reduction.
    Full subdir absorption (lens/, patterns/, domain/, memory/, etc.) tracked separately
    due to 204+ import consumers requiring careful batched migration.
    """

    def test_analysis_subdir_created(self) -> None:
        """analysis/ must be created as the first diamond layer."""
        analysis_dir = INTELLIGENCE_ROOT / "analysis"
        assert analysis_dir.is_dir(), (
            "GAP-117-08 FAIL: cortex/intelligence/analysis/ does not exist."
        )

    def test_diamond_dirs_all_present(self) -> None:
        """The five canonical diamond dirs must exist."""
        existing = {d.name for d in INTELLIGENCE_ROOT.iterdir() if d.is_dir()}
        missing = _DIAMOND_DIRS - existing
        assert not missing, (
            f"GAP-117-08 FAIL: diamond dirs missing: {missing}"
        )


class TestTopLevelPyFiles:
    """GAP-117-09: top-level .py files in cortex/intelligence/ must be reduced.

    Canonical files: facade.py, provider.py, base.py, base_engine.py, __init__.py
    Moved files: replaced with thin compat shims (≤15 lines each)
    Shims are required at the old paths for CORE-035 compat exception — they are
    not considered 'orphan implementations' once their canonical source has moved.
    """

    # Compat shim threshold: files at the top level that are not in _ALLOWED_TOP_LEVEL_PY
    # must be thin shims (re-export only, ≤15 lines)
    _MAX_SHIM_LINES = 15

    def test_top_level_py_count_le_5(self) -> None:
        """Only facade, provider, base, base_engine, __init__ must have substantive code.
        All other top-level .py files must be thin compat shims (≤15 lines).
        """
        violations: list[str] = []
        for py_file in sorted(INTELLIGENCE_ROOT.glob("*.py")):
            if py_file.name in _ALLOWED_TOP_LEVEL_PY:
                continue
            lines = [ln for ln in py_file.read_text(encoding="utf-8").splitlines()
                     if ln.strip() and not ln.strip().startswith("#") and not ln.strip().startswith('"""')]
            if len(lines) > self._MAX_SHIM_LINES:
                violations.append(f"{py_file.name} ({len(lines)} non-comment lines — too large for shim)")
        assert not violations, (
            f"GAP-117-09 FAIL: {len(violations)} top-level .py file(s) contain substantive "
            f"implementation (should be thin compat shims after move):\n" +
            "\n".join(violations)
        )

    def test_allowed_top_level_files_still_present(self) -> None:
        """facade.py, provider.py, base.py, base_engine.py, __init__.py must remain."""
        for name in _ALLOWED_TOP_LEVEL_PY:
            assert (INTELLIGENCE_ROOT / name).exists(), (
                f"Required top-level file missing: {name}"
            )


class TestCompatShimsResolveOldPaths:
    """After moves, old import paths must still resolve via compat shims."""

    @pytest.mark.parametrize("module_path", [
        "cortex.intelligence.ast_intelligence",
        "cortex.intelligence.call_graph",
        "cortex.intelligence.comment_analyzer",
        "cortex.intelligence.dependency_mapper",
        "cortex.intelligence.pattern_detector",
        "cortex.intelligence.author_context",
        "cortex.intelligence.change_frequency",
        "cortex.intelligence.routing_intelligence",
        "cortex.intelligence.duration_intelligence",
        "cortex.intelligence.error_intelligence",
        "cortex.intelligence.execution_sandbox",
        "cortex.intelligence.hp_output_validator",
        "cortex.intelligence.intelligence_metadata_discovery",
        "cortex.intelligence.intent_classifier",
        "cortex.intelligence.clarification_reducer",
        "cortex.intelligence.capability_registry_builder",
        "cortex.intelligence.intelligence_wiring_bridges",
        "cortex.intelligence.relationship_traversal",
        "cortex.intelligence.turn_context",
    ])
    def test_old_import_path_resolves(self, module_path: str) -> None:
        """Old import path must import without error (compat shim or moved file)."""
        try:
            mod = importlib.import_module(module_path)
            assert mod is not None, f"{module_path} imported as None"
        except ImportError as exc:
            pytest.fail(
                f"GAP-117-09 FAIL: '{module_path}' no longer importable after move. "
                f"Add a compat shim. Error: {exc}"
            )


class TestCapabilityMatcherConsolidated:
    """GAP-117-10: capability_matcher must resolve to intelligence_capability_matcher."""

    def test_capability_matcher_is_shim_or_canonical(self) -> None:
        """capability_matcher must be importable and expose canonical symbols."""
        try:
            import cortex.intelligence.capability_matcher as cm
            # Must export at least CapabilityMatch (canonical class)
            assert hasattr(cm, "CapabilityMatch"), (
                "capability_matcher.py must export CapabilityMatch (shim or canonical)"
            )
        except ImportError as exc:
            pytest.fail(f"capability_matcher import failed: {exc}")

    def test_intelligence_capability_matcher_is_canonical(self) -> None:
        """intelligence_capability_matcher must be the canonical single source."""
        try:
            import cortex.intelligence.intelligence_capability_matcher as icm
            assert hasattr(icm, "CapabilityMatch"), (
                "intelligence_capability_matcher.py must export CapabilityMatch"
            )
        except ImportError as exc:
            pytest.fail(f"intelligence_capability_matcher import failed: {exc}")

    def test_both_paths_return_same_class(self) -> None:
        """capability_matcher.CapabilityMatch must be the same class as intelligence_capability_matcher.CapabilityMatch."""
        try:
            from cortex.intelligence.capability_matcher import CapabilityMatch as CM1
            from cortex.intelligence.intelligence_capability_matcher import CapabilityMatch as CM2
            assert CM1 is CM2, (
                "capability_matcher.CapabilityMatch and intelligence_capability_matcher.CapabilityMatch "
                "must be the same class object (shim → canonical)"
            )
        except ImportError as exc:
            pytest.fail(f"Import failed: {exc}")


class TestAnalysisDirExists:
    """The analysis/ subdirectory must exist and be a Python package."""

    def test_analysis_dir_is_package(self) -> None:
        """cortex/intelligence/analysis/ must be a Python package with __init__.py."""
        analysis_dir = INTELLIGENCE_ROOT / "analysis"
        assert analysis_dir.is_dir(), (
            "cortex/intelligence/analysis/ directory does not exist. "
            "Create it as part of GAP-117-c flatten."
        )
        assert (analysis_dir / "__init__.py").exists(), (
            "cortex/intelligence/analysis/__init__.py missing — not a valid package."
        )

    def test_analysis_package_importable(self) -> None:
        """cortex.intelligence.analysis must be importable."""
        try:
            import cortex.intelligence.analysis  # noqa: F401
        except ImportError as exc:
            pytest.fail(f"cortex.intelligence.analysis not importable: {exc}")
