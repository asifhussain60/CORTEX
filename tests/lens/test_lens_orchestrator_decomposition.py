"""
Phase 103-d: GAP-103-04 — RED tests for LENSOrchestrator decomposition.

Verifies that lens_orchestrator.py (2,045L) is decomposed into:
  - cortex/lens/lens_orchestrator/ package with _coordinator.py ≤ 750L
  - lens_models.py     — LENSContext dataclass
  - lens_analysis_mixin.py  — file analysis + findings helpers
  - lens_remote_mixin.py    — remote/branch analysis
  - lens_holistic_mixin.py  — repository-level holistic analysis
  - lens_company_mixin.py   — company knowledge + compliance
  - lens_vision_mixin.py    — image/vision analysis

Authority: CORE-008 (TDD-first), CORE-011 (type hints), SWEEP-103-GOD-OBJECT-DECOMPOSITION
AC-103-D-001 through AC-103-D-007
"""
from __future__ import annotations

import ast
import importlib
import inspect
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
WORKSPACE_ROOT = Path(__file__).parents[2]
LENS_PKG = WORKSPACE_ROOT / "cortex" / "lens" / "lens_orchestrator"
COORDINATOR = LENS_PKG / "_coordinator.py"
MODELS = LENS_PKG / "lens_models.py"
ANALYSIS_MIXIN = LENS_PKG / "lens_analysis_mixin.py"
REMOTE_MIXIN = LENS_PKG / "lens_remote_mixin.py"
HOLISTIC_MIXIN = LENS_PKG / "lens_holistic_mixin.py"
COMPANY_MIXIN = LENS_PKG / "lens_company_mixin.py"
VISION_MIXIN = LENS_PKG / "lens_vision_mixin.py"
INIT_FILE = LENS_PKG / "__init__.py"


# ===========================================================================
# AC-103-D-001 — Package structure
# ===========================================================================
class TestPackageStructure:
    """All 7 module files + __init__.py must exist in the package."""

    def test_package_directory_exists(self):
        assert LENS_PKG.is_dir(), f"Package dir missing: {LENS_PKG}"

    def test_init_py_exists(self):
        assert INIT_FILE.is_file(), "__init__.py missing from package"

    def test_coordinator_exists(self):
        assert COORDINATOR.is_file(), "_coordinator.py missing"

    def test_lens_models_exists(self):
        assert MODELS.is_file(), "lens_models.py missing"

    def test_lens_analysis_mixin_exists(self):
        assert ANALYSIS_MIXIN.is_file(), "lens_analysis_mixin.py missing"

    def test_lens_remote_mixin_exists(self):
        assert REMOTE_MIXIN.is_file(), "lens_remote_mixin.py missing"

    def test_lens_holistic_mixin_exists(self):
        assert HOLISTIC_MIXIN.is_file(), "lens_holistic_mixin.py missing"

    def test_lens_company_mixin_exists(self):
        assert COMPANY_MIXIN.is_file(), "lens_company_mixin.py missing"

    def test_lens_vision_mixin_exists(self):
        assert VISION_MIXIN.is_file(), "lens_vision_mixin.py missing"


# ===========================================================================
# AC-103-D-002 — Line count gate
# ===========================================================================
class TestLensOrchestratorLineCount:
    """_coordinator.py must be ≤ 750 lines (CORE-SRP gate)."""

    def test_line_count_at_or_below_750(self):
        assert COORDINATOR.is_file(), "_coordinator.py does not exist"
        lines = len(COORDINATOR.read_text(encoding="utf-8").splitlines())
        assert lines <= 750, (
            f"_coordinator.py is {lines}L — must be ≤ 750L (CORE-SRP gate)"
        )

    def test_models_file_is_not_too_large(self):
        assert MODELS.is_file(), "lens_models.py does not exist"
        lines = len(MODELS.read_text(encoding="utf-8").splitlines())
        assert lines <= 600, f"lens_models.py is {lines}L — expected ≤ 600L"

    def test_analysis_mixin_is_not_too_large(self):
        assert ANALYSIS_MIXIN.is_file(), "lens_analysis_mixin.py does not exist"
        lines = len(ANALYSIS_MIXIN.read_text(encoding="utf-8").splitlines())
        assert lines <= 800, f"lens_analysis_mixin.py is {lines}L — expected ≤ 800L"

    def test_holistic_mixin_is_not_too_large(self):
        assert HOLISTIC_MIXIN.is_file(), "lens_holistic_mixin.py does not exist"
        lines = len(HOLISTIC_MIXIN.read_text(encoding="utf-8").splitlines())
        assert lines <= 800, f"lens_holistic_mixin.py is {lines}L — expected ≤ 800L"


# ===========================================================================
# AC-103-D-003 — LENSContext in lens_models.py
# ===========================================================================
class TestLensModels:
    """lens_models.py must contain LENSContext dataclass."""

    def test_models_file_has_lens_context_class(self):
        assert MODELS.is_file()
        source = MODELS.read_text(encoding="utf-8")
        tree = ast.parse(source)
        classes = [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
        assert "LENSContext" in classes, f"LENSContext missing from lens_models.py; found: {classes}"

    def test_lens_context_has_to_dict_method(self):
        assert MODELS.is_file()
        source = MODELS.read_text(encoding="utf-8")
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == "LENSContext":
                methods = [n.name for n in ast.walk(node) if isinstance(n, ast.FunctionDef)]
                assert "to_dict" in methods, "LENSContext.to_dict() missing"
                return
        pytest.fail("LENSContext class not found in lens_models.py")

    def test_lens_context_exported_from_package(self):
        init_source = INIT_FILE.read_text(encoding="utf-8") if INIT_FILE.is_file() else ""
        assert "LENSContext" in init_source, "LENSContext not exported from __init__.py"

    def test_get_lens_orchestrator_exported_from_package(self):
        init_source = INIT_FILE.read_text(encoding="utf-8") if INIT_FILE.is_file() else ""
        assert "get_lens_orchestrator" in init_source, "get_lens_orchestrator not exported from __init__.py"


# ===========================================================================
# AC-103-D-004 — LensAnalysisMixin methods
# ===========================================================================
class TestLensAnalysisMixin:
    """lens_analysis_mixin.py must contain the file-level analysis helpers."""

    EXPECTED_METHODS = [
        "_analyze_git",
        "_analyze_ast",
        "_analyze_comments",
        "_extract_business_rules",
        "_build_relationship_findings",
        "_build_relationship_findings_fallback",
        "_build_dependency_findings",
        "_build_pattern_findings",
        "_detect_tech_stack",
    ]

    def _get_mixin_methods(self) -> list[str]:
        assert ANALYSIS_MIXIN.is_file()
        source = ANALYSIS_MIXIN.read_text(encoding="utf-8")
        tree = ast.parse(source)
        methods = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and "Mixin" in node.name:
                methods.extend(
                    n.name for n in ast.walk(node)
                    if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                )
        return methods

    @pytest.mark.parametrize("method", EXPECTED_METHODS)
    def test_mixin_has_method(self, method: str):
        methods = self._get_mixin_methods()
        assert method in methods, (
            f"LensFileAnalysisMixin missing method: {method}; found: {methods}"
        )

    def test_analysis_mixin_has_class(self):
        assert ANALYSIS_MIXIN.is_file()
        source = ANALYSIS_MIXIN.read_text(encoding="utf-8")
        tree = ast.parse(source)
        classes = [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
        mixin_classes = [c for c in classes if "Mixin" in c]
        assert mixin_classes, f"No Mixin class in lens_analysis_mixin.py; found: {classes}"


# ===========================================================================
# AC-103-D-005 — LensRemoteMixin methods
# ===========================================================================
class TestLensRemoteMixin:
    """lens_remote_mixin.py must contain remote/branch analysis methods."""

    EXPECTED_METHODS = [
        "analyze_remote",
        "_analyze_git_remote",
        "_analyze_ast_content",
        "_analyze_comments_content",
        "compare_branches",
    ]

    def _get_mixin_methods(self) -> list[str]:
        assert REMOTE_MIXIN.is_file()
        source = REMOTE_MIXIN.read_text(encoding="utf-8")
        tree = ast.parse(source)
        methods = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and "Mixin" in node.name:
                methods.extend(
                    n.name for n in ast.walk(node)
                    if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                )
        return methods

    @pytest.mark.parametrize("method", EXPECTED_METHODS)
    def test_mixin_has_method(self, method: str):
        methods = self._get_mixin_methods()
        assert method in methods, (
            f"LensRemoteMixin missing method: {method}; found: {methods}"
        )

    def test_remote_mixin_has_class(self):
        assert REMOTE_MIXIN.is_file()
        source = REMOTE_MIXIN.read_text(encoding="utf-8")
        tree = ast.parse(source)
        classes = [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
        mixin_classes = [c for c in classes if "Mixin" in c]
        assert mixin_classes, f"No Mixin class in lens_remote_mixin.py; found: {classes}"


# ===========================================================================
# AC-103-D-006 — LensHolisticMixin methods
# ===========================================================================
class TestLensHolisticMixin:
    """lens_holistic_mixin.py must contain repository-level analysis methods."""

    EXPECTED_METHODS = [
        "analyze_repository_holistic",
        "_analyze_repository_summary",
        "_analyze_codebase_structure",
        "_analyze_configurations",
        "_analyze_database_artifacts",
        "_analyze_api_specs",
        "_analyze_visual_artifacts",
        "_synthesize_security_findings",
        "_generate_holistic_recommendations",
    ]

    def _get_mixin_methods(self) -> list[str]:
        assert HOLISTIC_MIXIN.is_file()
        source = HOLISTIC_MIXIN.read_text(encoding="utf-8")
        tree = ast.parse(source)
        methods = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and "Mixin" in node.name:
                methods.extend(
                    n.name for n in ast.walk(node)
                    if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                )
        return methods

    @pytest.mark.parametrize("method", EXPECTED_METHODS)
    def test_mixin_has_method(self, method: str):
        methods = self._get_mixin_methods()
        assert method in methods, (
            f"LensHolisticMixin missing method: {method}; found: {methods}"
        )

    def test_holistic_mixin_has_class(self):
        assert HOLISTIC_MIXIN.is_file()
        source = HOLISTIC_MIXIN.read_text(encoding="utf-8")
        tree = ast.parse(source)
        classes = [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
        mixin_classes = [c for c in classes if "Mixin" in c]
        assert mixin_classes, f"No Mixin class in lens_holistic_mixin.py; found: {classes}"


# ===========================================================================
# AC-103-D-007 — LensCompanyMixin + LensVisionMixin
# ===========================================================================
class TestLensCompanyMixin:
    """lens_company_mixin.py must contain company knowledge methods."""

    EXPECTED_METHODS = [
        "analyze_with_company_knowledge",
        "_load_company_domains",
        "_detect_compliance",
        "_merge_knowledge",
    ]

    def _get_mixin_methods(self) -> list[str]:
        assert COMPANY_MIXIN.is_file()
        source = COMPANY_MIXIN.read_text(encoding="utf-8")
        tree = ast.parse(source)
        methods = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and "Mixin" in node.name:
                methods.extend(
                    n.name for n in ast.walk(node)
                    if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                )
        return methods

    @pytest.mark.parametrize("method", EXPECTED_METHODS)
    def test_mixin_has_method(self, method: str):
        methods = self._get_mixin_methods()
        assert method in methods, (
            f"LensCompanyMixin missing method: {method}; found: {methods}"
        )


class TestLensVisionMixin:
    """lens_vision_mixin.py must contain vision/image analysis methods."""

    EXPECTED_METHODS = [
        "analyze_image",
        "analyze_with_vision",
    ]

    def _get_mixin_methods(self) -> list[str]:
        assert VISION_MIXIN.is_file()
        source = VISION_MIXIN.read_text(encoding="utf-8")
        tree = ast.parse(source)
        methods = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and "Mixin" in node.name:
                methods.extend(
                    n.name for n in ast.walk(node)
                    if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                )
        return methods

    @pytest.mark.parametrize("method", EXPECTED_METHODS)
    def test_mixin_has_method(self, method: str):
        methods = self._get_mixin_methods()
        assert method in methods, (
            f"LensVisionMixin missing method: {method}; found: {methods}"
        )


# ===========================================================================
# AC-103-D-008 — Coordinator imports + backward compat
# ===========================================================================
class TestCoordinatorImports:
    """_coordinator.py must import all 5 mixins and re-export public API."""

    def test_coordinator_imports_all_mixins(self):
        assert COORDINATOR.is_file()
        source = COORDINATOR.read_text(encoding="utf-8")
        for mixin in [
            "LensFileAnalysisMixin",
            "LensRemoteMixin",
            "LensHolisticMixin",
            "LensCompanyMixin",
            "LensVisionMixin",
        ]:
            assert mixin in source, f"_coordinator.py does not import {mixin}"

    def test_coordinator_has_lens_orchestrator_class(self):
        assert COORDINATOR.is_file()
        source = COORDINATOR.read_text(encoding="utf-8")
        tree = ast.parse(source)
        classes = [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
        assert "LENSOrchestrator" in classes, (
            f"LENSOrchestrator class missing from _coordinator.py; found: {classes}"
        )

    def test_coordinator_has_get_lens_orchestrator_factory(self):
        assert COORDINATOR.is_file()
        source = COORDINATOR.read_text(encoding="utf-8")
        assert "get_lens_orchestrator" in source, (
            "get_lens_orchestrator factory missing from _coordinator.py"
        )

    def test_init_exports_lens_orchestrator(self):
        init_source = INIT_FILE.read_text(encoding="utf-8") if INIT_FILE.is_file() else ""
        assert "LENSOrchestrator" in init_source, (
            "LENSOrchestrator not exported from package __init__.py"
        )

    def test_init_exports_all_mixins(self):
        init_source = INIT_FILE.read_text(encoding="utf-8") if INIT_FILE.is_file() else ""
        for mixin in [
            "LensFileAnalysisMixin",
            "LensRemoteMixin",
            "LensHolisticMixin",
            "LensCompanyMixin",
            "LensVisionMixin",
        ]:
            assert mixin in init_source, f"__init__.py does not export {mixin}"


# ===========================================================================
# AC-103-D-009 — Runtime import test
# ===========================================================================
class TestRuntimeImport:
    """LENSOrchestrator must be importable from the package after decomposition."""

    def test_lens_orchestrator_importable(self):
        """Import from package root (backward compat via lens/__init__.py)."""
        # This should resolve via cortex.lens.__getattr__ lazy import
        try:
            from cortex.lens.lens_orchestrator import LENSOrchestrator
            assert LENSOrchestrator is not None
        except ImportError as exc:
            pytest.fail(f"Cannot import LENSOrchestrator: {exc}")

    def test_lens_context_importable(self):
        try:
            from cortex.lens.lens_orchestrator import LENSContext
            assert LENSContext is not None
        except ImportError as exc:
            pytest.fail(f"Cannot import LENSContext: {exc}")

    def test_get_lens_orchestrator_importable(self):
        try:
            from cortex.lens.lens_orchestrator import get_lens_orchestrator
            assert callable(get_lens_orchestrator)
        except ImportError as exc:
            pytest.fail(f"Cannot import get_lens_orchestrator: {exc}")

    def test_lens_orchestrator_has_analyze_file(self):
        from cortex.lens.lens_orchestrator import LENSOrchestrator
        assert hasattr(LENSOrchestrator, "analyze_file"), (
            "LENSOrchestrator.analyze_file() missing"
        )

    def test_lens_orchestrator_has_analyze_batch(self):
        from cortex.lens.lens_orchestrator import LENSOrchestrator
        assert hasattr(LENSOrchestrator, "analyze_batch"), (
            "LENSOrchestrator.analyze_batch() missing"
        )

    def test_lens_orchestrator_has_analyze_repository_holistic(self):
        from cortex.lens.lens_orchestrator import LENSOrchestrator
        assert hasattr(LENSOrchestrator, "analyze_repository_holistic"), (
            "LENSOrchestrator.analyze_repository_holistic() missing"
        )

    def test_lens_orchestrator_has_analyze_image(self):
        from cortex.lens.lens_orchestrator import LENSOrchestrator
        assert hasattr(LENSOrchestrator, "analyze_image"), (
            "LENSOrchestrator.analyze_image() missing"
        )

    def test_lens_orchestrator_has_compare_branches(self):
        from cortex.lens.lens_orchestrator import LENSOrchestrator
        assert hasattr(LENSOrchestrator, "compare_branches"), (
            "LENSOrchestrator.compare_branches() missing"
        )

    def test_lens_orchestrator_has_record_analysis_outcome(self):
        from cortex.lens.lens_orchestrator import LENSOrchestrator
        assert hasattr(LENSOrchestrator, "record_analysis_outcome"), (
            "LENSOrchestrator.record_analysis_outcome() missing"
        )
