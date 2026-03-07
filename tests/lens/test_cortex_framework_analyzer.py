"""Tests for CortexFrameworkAnalyzer — Phase 131-b (GAP-131-02).

TDD RED phase: All tests must FAIL before implementation exists.
Target: cortex/lens/analyzers/cortex_framework_analyzer.py

CORE-008: TDD mandatory — write failing tests first.
"""

from __future__ import annotations

from pathlib import Path

import pytest


# ─────────────────────────────────────────────────────────────────────────────
# Module import
# ─────────────────────────────────────────────────────────────────────────────

class TestCortexFrameworkAnalyzerImport:
    """Verify CortexFrameworkAnalyzer can be imported."""

    def test_module_importable(self) -> None:
        """CortexFrameworkAnalyzer module must exist and be importable."""
        from cortex.lens.analyzers.cortex_framework_analyzer import (  # noqa: F401
            CortexFrameworkAnalyzer,
        )

    def test_class_importable(self) -> None:
        """CortexFrameworkAnalyzer class must be importable."""
        from cortex.lens.analyzers.cortex_framework_analyzer import CortexFrameworkAnalyzer
        assert CortexFrameworkAnalyzer is not None


# ─────────────────────────────────────────────────────────────────────────────
# Instantiation
# ─────────────────────────────────────────────────────────────────────────────

class TestCortexFrameworkAnalyzerInstantiation:
    """CortexFrameworkAnalyzer construction."""

    def test_instantiates_without_args(self) -> None:
        """CortexFrameworkAnalyzer() must construct without required arguments."""
        from cortex.lens.analyzers.cortex_framework_analyzer import CortexFrameworkAnalyzer
        analyzer = CortexFrameworkAnalyzer()
        assert analyzer is not None

    def test_has_analyze_method(self) -> None:
        """analyze() method must exist."""
        from cortex.lens.analyzers.cortex_framework_analyzer import CortexFrameworkAnalyzer
        assert callable(getattr(CortexFrameworkAnalyzer(), "analyze", None))

    def test_has_is_cortex_framework_method(self) -> None:
        """is_cortex_framework() convenience method must exist."""
        from cortex.lens.analyzers.cortex_framework_analyzer import CortexFrameworkAnalyzer
        assert callable(getattr(CortexFrameworkAnalyzer(), "is_cortex_framework", None))


# ─────────────────────────────────────────────────────────────────────────────
# CORTEX repo detection
# ─────────────────────────────────────────────────────────────────────────────

class TestCortexRepoDetection:
    """CortexFrameworkAnalyzer correctly identifies CORTEX repos."""

    def test_cortex_repo_detected_with_registry_and_orchestrators(self, tmp_path: Path) -> None:
        """Repo with cortex-registry/ AND cortex/orchestrators/ must be detected as CORTEX."""
        from cortex.lens.analyzers.cortex_framework_analyzer import CortexFrameworkAnalyzer
        (tmp_path / "cortex-registry").mkdir()
        (tmp_path / "cortex").mkdir()
        (tmp_path / "cortex" / "orchestrators").mkdir(parents=True)
        result = CortexFrameworkAnalyzer().analyze(tmp_path)
        assert result["is_cortex_framework"] is True

    def test_non_cortex_repo_returns_false(self, tmp_path: Path) -> None:
        """A plain Python repo without CORTEX markers must return is_cortex_framework=False."""
        from cortex.lens.analyzers.cortex_framework_analyzer import CortexFrameworkAnalyzer
        (tmp_path / "src").mkdir()
        (tmp_path / "tests").mkdir()
        (tmp_path / "requirements.txt").write_text("flask\nrequests\n")
        result = CortexFrameworkAnalyzer().analyze(tmp_path)
        assert result["is_cortex_framework"] is False

    def test_empty_directory_returns_false(self, tmp_path: Path) -> None:
        """An empty directory must return is_cortex_framework=False without raising."""
        from cortex.lens.analyzers.cortex_framework_analyzer import CortexFrameworkAnalyzer
        result = CortexFrameworkAnalyzer().analyze(tmp_path)
        assert result["is_cortex_framework"] is False

    def test_nonexistent_path_returns_false(self) -> None:
        """A non-existent path must return is_cortex_framework=False without raising."""
        from cortex.lens.analyzers.cortex_framework_analyzer import CortexFrameworkAnalyzer
        result = CortexFrameworkAnalyzer().analyze(Path("/nonexistent/xyz/path"))
        assert result["is_cortex_framework"] is False

    def test_cortex_runtime_dir_is_positive_signal(self, tmp_path: Path) -> None:
        """Presence of .cortex-runtime/ is a positive CORTEX indicator."""
        from cortex.lens.analyzers.cortex_framework_analyzer import CortexFrameworkAnalyzer
        (tmp_path / "cortex-registry").mkdir()
        (tmp_path / ".cortex-runtime").mkdir()
        result = CortexFrameworkAnalyzer().analyze(tmp_path)
        assert result["is_cortex_framework"] is True

    def test_only_cortex_registry_is_not_enough(self, tmp_path: Path) -> None:
        """cortex-registry/ alone is insufficient — needs a second signal."""
        from cortex.lens.analyzers.cortex_framework_analyzer import CortexFrameworkAnalyzer
        (tmp_path / "cortex-registry").mkdir()
        result = CortexFrameworkAnalyzer().analyze(tmp_path)
        # Single signal is ambiguous — must require ≥2 signals
        assert result["is_cortex_framework"] is False


# ─────────────────────────────────────────────────────────────────────────────
# analyze() return structure
# ─────────────────────────────────────────────────────────────────────────────

class TestAnalyzeReturnStructure:
    """analyze() must return a well-formed dict."""

    def test_analyze_returns_dict(self, tmp_path: Path) -> None:
        """analyze() must return a dict."""
        from cortex.lens.analyzers.cortex_framework_analyzer import CortexFrameworkAnalyzer
        result = CortexFrameworkAnalyzer().analyze(tmp_path)
        assert isinstance(result, dict)

    def test_analyze_has_is_cortex_framework_key(self, tmp_path: Path) -> None:
        """Result must contain 'is_cortex_framework' boolean key."""
        from cortex.lens.analyzers.cortex_framework_analyzer import CortexFrameworkAnalyzer
        result = CortexFrameworkAnalyzer().analyze(tmp_path)
        assert "is_cortex_framework" in result
        assert isinstance(result["is_cortex_framework"], bool)

    def test_analyze_has_signals_detected_key(self, tmp_path: Path) -> None:
        """Result must contain 'signals_detected' list key."""
        from cortex.lens.analyzers.cortex_framework_analyzer import CortexFrameworkAnalyzer
        result = CortexFrameworkAnalyzer().analyze(tmp_path)
        assert "signals_detected" in result
        assert isinstance(result["signals_detected"], list)

    def test_analyze_has_confidence_key(self, tmp_path: Path) -> None:
        """Result must contain 'confidence' float key."""
        from cortex.lens.analyzers.cortex_framework_analyzer import CortexFrameworkAnalyzer
        result = CortexFrameworkAnalyzer().analyze(tmp_path)
        assert "confidence" in result
        assert isinstance(result["confidence"], float)

    def test_cortex_repo_confidence_is_high(self, tmp_path: Path) -> None:
        """Full CORTEX repo must return confidence ≥ 0.6."""
        from cortex.lens.analyzers.cortex_framework_analyzer import CortexFrameworkAnalyzer
        (tmp_path / "cortex-registry").mkdir()
        (tmp_path / "cortex").mkdir()
        (tmp_path / "cortex" / "orchestrators").mkdir()
        (tmp_path / ".cortex-runtime").mkdir()
        (tmp_path / "cortex" / "__init__.py").write_text("")
        result = CortexFrameworkAnalyzer().analyze(tmp_path)
        assert result["confidence"] >= 0.6, (
            f"Expected confidence ≥ 0.6, got {result['confidence']}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# is_cortex_framework() convenience method
# ─────────────────────────────────────────────────────────────────────────────

class TestIsCortexFrameworkConvenience:
    """is_cortex_framework() must return a plain bool."""

    def test_convenience_method_returns_bool(self, tmp_path: Path) -> None:
        """is_cortex_framework() must return a bool."""
        from cortex.lens.analyzers.cortex_framework_analyzer import CortexFrameworkAnalyzer
        result = CortexFrameworkAnalyzer().is_cortex_framework(tmp_path)
        assert isinstance(result, bool)

    def test_convenience_true_for_cortex_repo(self, tmp_path: Path) -> None:
        """is_cortex_framework() must return True for a CORTEX repo."""
        from cortex.lens.analyzers.cortex_framework_analyzer import CortexFrameworkAnalyzer
        (tmp_path / "cortex-registry").mkdir()
        (tmp_path / "cortex").mkdir()
        (tmp_path / "cortex" / "orchestrators").mkdir()
        assert CortexFrameworkAnalyzer().is_cortex_framework(tmp_path) is True

    def test_convenience_false_for_non_cortex(self, tmp_path: Path) -> None:
        """is_cortex_framework() must return False for a non-CORTEX repo."""
        from cortex.lens.analyzers.cortex_framework_analyzer import CortexFrameworkAnalyzer
        (tmp_path / "src").mkdir()
        assert CortexFrameworkAnalyzer().is_cortex_framework(tmp_path) is False


# ─────────────────────────────────────────────────────────────────────────────
# IntelligenceFacade integration
# ─────────────────────────────────────────────────────────────────────────────

class TestFacadeIntegration:
    """IntelligenceFacade must expose is_cortex_framework()."""

    def test_facade_has_is_cortex_framework(self) -> None:
        """IntelligenceFacade must have is_cortex_framework() method."""
        from cortex.intelligence.facade import IntelligenceFacade
        facade = IntelligenceFacade()
        assert callable(getattr(facade, "is_cortex_framework", None))

    def test_facade_is_cortex_framework_returns_bool(self, tmp_path: Path) -> None:
        """facade.is_cortex_framework() must return a bool."""
        from cortex.intelligence.facade import IntelligenceFacade
        result = IntelligenceFacade().is_cortex_framework(tmp_path)
        assert isinstance(result, bool)
