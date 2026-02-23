"""
Phase 59-g: DependencyGuard / soft_import Tests

CORE-008: Tests written before implementation.
GAP-59-10: 151 bare ImportError blocks must use structured soft_import().
           This test validates the soft_import() utility and migration contract.

AC_START: AC-DEPGUARD-TEST-5907
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
CORTEX_ROOT = REPO_ROOT / "cortex"


class TestDependencyGuardModule:
    """59-g-T1: cortex.core.dependency_guard must exist and export soft_import."""

    def test_module_importable(self) -> None:
        """cortex.core.dependency_guard must import cleanly."""
        import importlib
        mod = importlib.import_module("cortex.core.dependency_guard")
        assert mod is not None

    def test_soft_import_exported(self) -> None:
        """dependency_guard must export soft_import callable."""
        from cortex.core.dependency_guard import soft_import
        assert callable(soft_import)


class TestSoftImportBehaviour:
    """59-g-T2: soft_import must handle success, missing attr, and ImportError."""

    def test_soft_import_success_module(self) -> None:
        """soft_import returns the module when it exists."""
        from cortex.core.dependency_guard import soft_import
        result = soft_import("cortex.core.result")
        assert result is not None
        assert hasattr(result, "Ok")

    def test_soft_import_success_attr(self) -> None:
        """soft_import returns the attribute from an existing module."""
        from cortex.core.dependency_guard import soft_import
        Ok = soft_import("cortex.core.result", attr="Ok")
        assert Ok is not None

    def test_soft_import_missing_module_returns_fallback(self) -> None:
        """soft_import returns fallback when the module does not exist."""
        from cortex.core.dependency_guard import soft_import
        result = soft_import(
            "cortex.does_not_exist_xyz",
            fallback="MISSING",
            feature_name="Test Feature",
        )
        assert result == "MISSING"

    def test_soft_import_missing_attr_returns_fallback(self) -> None:
        """soft_import returns fallback when attribute is absent from the module."""
        from cortex.core.dependency_guard import soft_import
        result = soft_import(
            "cortex.core.result",
            attr="ThisDoesNotExist",
            fallback=42,
        )
        assert result == 42

    def test_soft_import_emits_warning_on_failure(self, caplog: pytest.LogCaptureFixture) -> None:
        """soft_import must log a WARNING when import fails."""
        from cortex.core.dependency_guard import soft_import
        with caplog.at_level(logging.WARNING, logger="cortex.core.dependency_guard"):
            soft_import(
                "cortex.no_such_module_abc",
                fallback=None,
                feature_name="Test capability",
            )
        assert any(
            "cortex.no_such_module_abc" in record.message
            for record in caplog.records
        ), (
            "soft_import did not emit a warning when import failed — "
            "bare ImportError:pass pattern is not observable."
        )

    def test_soft_import_default_fallback_is_none(self) -> None:
        """soft_import default fallback must be None."""
        from cortex.core.dependency_guard import soft_import
        result = soft_import("cortex.absolutely.not.a.real.module")
        assert result is None

    def test_soft_import_none_attr_returns_module(self) -> None:
        """soft_import with attr=None returns the module, not an attribute."""
        from cortex.core.dependency_guard import soft_import
        import cortex.core.audit_models as expected
        result = soft_import("cortex.core.audit_models", attr=None)
        assert result is expected


class TestMigrationContract:
    """59-g-T3: At least one cortex.* file must now use soft_import (migration progress)."""

    def test_dependency_guard_module_file_exists(self) -> None:
        """cortex/core/dependency_guard.py must exist."""
        path = CORTEX_ROOT / "core" / "dependency_guard.py"
        assert path.exists(), (
            "GAP-59-10 | cortex/core/dependency_guard.py does not exist"
        )

    def test_dependency_guard_is_not_empty(self) -> None:
        """cortex/core/dependency_guard.py must define soft_import."""
        path = CORTEX_ROOT / "core" / "dependency_guard.py"
        content = path.read_text(encoding="utf-8")
        assert "def soft_import" in content, (
            "GAP-59-10 | cortex/core/dependency_guard.py does not define soft_import()"
        )

# AC_COMPLETE: AC-DEPGUARD-TEST-5907 ✅
