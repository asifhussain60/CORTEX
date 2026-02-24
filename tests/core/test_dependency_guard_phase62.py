"""
Phase 62-C tests — safe_import() and _log_dependency_warning() in dependency_guard.

Validates the Phase 62-C additions on top of the existing Phase 59-g soft_import.

CORE-008: Tests cover the safe_import surface added in Phase 62-C.
AC_START: AC-62C-DEPENDENCY-GUARD-TESTS-001
"""
from __future__ import annotations

import sqlite3
from pathlib import Path
from unittest.mock import patch
import pytest


class TestSafeImportSuccess:
    """safe_import returns the module when import succeeds."""

    def test_imports_stdlib_module(self) -> None:
        """safe_import can import stdlib modules."""
        from cortex.core.dependency_guard import safe_import
        import os
        result = safe_import("os", warn=False)
        assert result is os

    def test_imports_cortex_module(self) -> None:
        """safe_import imports a real cortex module."""
        from cortex.core.dependency_guard import safe_import
        result = safe_import("cortex.core.result", warn=False)
        assert result is not None

    def test_success_does_not_call_log_warning(self) -> None:
        """safe_import never calls _log_dependency_warning on a successful import."""
        from cortex.core import dependency_guard
        with patch.object(dependency_guard, "_log_dependency_warning") as mock_log:
            dependency_guard.safe_import("os", warn=True)
            mock_log.assert_not_called()


class TestSafeImportFailure:
    """safe_import handles ImportError gracefully."""

    def test_returns_none_fallback_by_default(self) -> None:
        """safe_import returns None when import fails and no fallback given."""
        from cortex.core.dependency_guard import safe_import
        result = safe_import("cortex_this_does_not_exist_xyz", warn=False)
        assert result is None

    def test_returns_provided_fallback(self) -> None:
        """safe_import returns the provided fallback on ImportError."""
        from cortex.core.dependency_guard import safe_import
        sentinel = object()
        result = safe_import("cortex_this_does_not_exist_xyz", fallback=sentinel, warn=False)
        assert result is sentinel

    def test_warn_true_calls_log_warning(self) -> None:
        """safe_import calls _log_dependency_warning when warn=True."""
        from cortex.core import dependency_guard
        with patch.object(dependency_guard, "_log_dependency_warning") as mock_log:
            dependency_guard.safe_import("cortex_no_such_pkg", warn=True, caller="test.py")
            mock_log.assert_called_once()
            call_args = mock_log.call_args[0]
            assert call_args[0] == "cortex_no_such_pkg"
            assert call_args[3] == "test.py"

    def test_warn_false_does_not_call_log_warning(self) -> None:
        """safe_import does NOT call _log_dependency_warning when warn=False."""
        from cortex.core import dependency_guard
        with patch.object(dependency_guard, "_log_dependency_warning") as mock_log:
            dependency_guard.safe_import("cortex_no_such_pkg", warn=False)
            mock_log.assert_not_called()


class TestLogDependencyWarning:
    """_log_dependency_warning persists structured warnings to SQLite."""

    def test_creates_table_and_inserts_row(self, tmp_path: Path) -> None:
        """A warning row is inserted into dependency_warnings table."""
        from cortex.core import dependency_guard
        db_path = tmp_path / "test-traces.db"
        with patch.object(dependency_guard, "_DB_PATH", db_path):
            dependency_guard._log_dependency_warning(
                module_name="missing.module",
                error="No module named 'missing'",
                fallback_used=None,
                caller="some_file.py",
            )
        with sqlite3.connect(str(db_path)) as conn:
            rows = conn.execute(
                "SELECT module_name, error, fallback_used, caller, recorded_at "
                "FROM dependency_warnings"
            ).fetchall()
        assert len(rows) == 1
        row = rows[0]
        assert row[0] == "missing.module"
        assert "No module" in row[1]
        assert row[3] == "some_file.py"
        assert row[4]  # timestamp non-empty

    def test_multiple_warnings_accumulate(self, tmp_path: Path) -> None:
        """Multiple _log_dependency_warning calls insert multiple rows."""
        from cortex.core import dependency_guard
        db_path = tmp_path / "test-traces.db"
        with patch.object(dependency_guard, "_DB_PATH", db_path):
            for i in range(3):
                dependency_guard._log_dependency_warning(
                    f"pkg.{i}", f"err{i}", None, f"file{i}.py"
                )
        with sqlite3.connect(str(db_path)) as conn:
            count = conn.execute(
                "SELECT COUNT(*) FROM dependency_warnings"
            ).fetchone()[0]
        assert count == 3

    def test_does_not_raise_if_db_path_invalid(self) -> None:
        """_log_dependency_warning never raises even if DB is unavailable."""
        from cortex.core import dependency_guard
        bad_path = Path("/dev/null/no/such/path.db")
        with patch.object(dependency_guard, "_DB_PATH", bad_path):
            # Must not raise
            dependency_guard._log_dependency_warning(
                "mod", "err", None, "caller"
            )

    def test_recorded_at_is_iso_format(self, tmp_path: Path) -> None:
        """recorded_at column contains ISO-format datetime string."""
        from cortex.core import dependency_guard
        import datetime
        db_path = tmp_path / "test-traces.db"
        with patch.object(dependency_guard, "_DB_PATH", db_path):
            dependency_guard._log_dependency_warning("m", "e", None, "c")
        with sqlite3.connect(str(db_path)) as conn:
            ts = conn.execute(
                "SELECT recorded_at FROM dependency_warnings"
            ).fetchone()[0]
        # Should parse as ISO datetime
        parsed = datetime.datetime.fromisoformat(ts)
        assert parsed.year >= 2026


class TestPublicAPI:
    """Verify public API surface of cortex.core.dependency_guard."""

    def test_safe_import_in_all(self) -> None:
        """safe_import is in __all__."""
        import cortex.core.dependency_guard as dg
        assert "safe_import" in dg.__all__

    def test_log_dependency_warning_in_all(self) -> None:
        """_log_dependency_warning is in __all__."""
        import cortex.core.dependency_guard as dg
        assert "_log_dependency_warning" in dg.__all__

    def test_soft_import_still_works(self) -> None:
        """Phase 59-g soft_import is unchanged and still functional."""
        from cortex.core.dependency_guard import soft_import
        import os
        result = soft_import("os")
        assert result is os

# AC_COMPLETE: AC-62C-DEPENDENCY-GUARD-TESTS-001 ✅
