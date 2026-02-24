"""
cortex.core.dependency_guard — Structured Optional Import Utility
=================================================================

Phase 59-g: Replaces bare ``except ImportError: pass`` blocks for
``cortex.*`` internal imports with structured, observable ``soft_import()``
calls that emit ``logger.warning`` messages instead of silently failing.

This module ONLY targets internal ``cortex.*`` imports. External library
guards (``yaml``, ``prometheus_client``, ``opentelemetry``, etc.) are
intentionally NOT migrated — they must remain as-is.

CORE Rules: CORE-035 (single implementation), CORE-011 (type hints),
            CORE-012 (docstrings), CORE-049 (silent autonomy via logger)

Usage::

    # Before (bare except ImportError):
    try:
        from cortex.some.module import SomeClass
    except ImportError:
        SomeClass = None

    # After (structured with observable warning):
    from cortex.core.dependency_guard import soft_import
    SomeClass = soft_import(
        "cortex.some.module",
        attr="SomeClass",
        fallback=None,
        feature_name="SomeClass capability",
    )

AC_START: AC-DEPGUARD-5907
"""
from __future__ import annotations

import importlib
import logging
import sqlite3
import datetime
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

__all__ = ["soft_import", "safe_import", "_log_dependency_warning"]

# SQLite audit DB path (canonical runtime location)
_DB_PATH = Path(".cortex-runtime/traces/orchestrator-traces.db")


def soft_import(
    module_name: str,
    *,
    attr: Optional[str] = None,
    fallback: Any = None,
    feature_name: Optional[str] = None,
    log_level: int = logging.WARNING,
) -> Any:
    """Attempt to import a module or attribute, returning *fallback* on failure.

    Unlike a bare ``except ImportError: pass`` block, this function emits an
    observable log message so that import failures are visible in logs and can
    be detected by the governance layer (CORE-049).

    Args:
        module_name: Fully-qualified module name to import
                     (e.g. ``"cortex.intelligence.lens.lens_orchestrator"``).
        attr: Optional attribute to extract from the imported module.
              If ``None``, the module itself is returned on success.
        fallback: Value to return on import failure (default: ``None``).
        feature_name: Human-readable name of the missing feature for log messages.
                      Defaults to ``module_name`` if not provided.
        log_level: Log level for the warning message (default: ``logging.WARNING``).

    Returns:
        The requested module or attribute on success, or *fallback* on failure.

    Example::

        LENSOrchestrator = soft_import(
            "cortex.intelligence.lens.lens_orchestrator",
            attr="LENSOrchestrator",
            fallback=None,
            feature_name="LENS Analysis",
        )
    """
    label = feature_name or (f"{module_name}.{attr}" if attr else module_name)
    try:
        mod = importlib.import_module(module_name)
        if attr is None:
            return mod
        result = getattr(mod, attr, fallback)
        if result is fallback and not hasattr(mod, attr):
            logger.log(
                log_level,
                "soft_import: attribute '%s' not found in '%s' — using fallback. "
                "Feature unavailable: %s",
                attr,
                module_name,
                label,
            )
        return result
    except ImportError as exc:
        logger.log(
            log_level,
            "soft_import: cannot import '%s' — %s. Feature unavailable: %s",
            module_name,
            exc,
            label,
        )
        return fallback
    except Exception as exc:  # noqa: BLE001
        logger.log(
            log_level,
            "soft_import: unexpected error importing '%s' — %s. Feature unavailable: %s",
            module_name,
            exc,
            label,
        )
        return fallback


# AC_COMPLETE: AC-DEPGUARD-5907 ✅


# ---------------------------------------------------------------------------
# Phase 62-C: safe_import() + SQLite DependencyWarning persistence
# AC_START: AC-62C-DEPENDENCY-GUARD-001
# ---------------------------------------------------------------------------

def _log_dependency_warning(
    module_name: str,
    error: str,
    fallback_used: Any,
    caller: str,
) -> None:
    """Persist a dependency degradation warning to the SQLite audit DB.

    Never raises — DB failures are swallowed so the caller is never disrupted.

    Args:
        module_name: The module that failed to import.
        error: The ImportError message.
        fallback_used: The fallback value that was returned.
        caller: Description of the calling file/context.
    """
    msg = (
        f"[DEPENDENCY DEGRADED] {module_name} unavailable — "
        f"fallback={fallback_used!r} caller={caller or 'unknown'} error={error}"
    )
    logger.warning(msg)
    try:
        _DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(str(_DB_PATH)) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS dependency_warnings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    module_name TEXT NOT NULL,
                    error TEXT,
                    fallback_used TEXT,
                    caller TEXT,
                    recorded_at TEXT NOT NULL
                )
            """)
            conn.execute(
                "INSERT INTO dependency_warnings VALUES (NULL,?,?,?,?,?)",
                (
                    module_name,
                    error,
                    repr(fallback_used),
                    caller,
                    datetime.datetime.utcnow().isoformat(),
                ),
            )
    except Exception:  # noqa: BLE001
        pass  # Never let audit logging crash the caller


def safe_import(
    module_name: str,
    fallback: Any = None,
    warn: bool = True,
    caller: str = "",
) -> Any:
    """Import a module safely with structured degradation warning.

    Replaces bare ``except ImportError: pass`` blocks. On failure, optionally
    persists a structured warning to the SQLite audit DB so operators can
    detect capability degradation at runtime.

    Args:
        module_name: Dotted module path to import (e.g. ``"cortex.core.result"``).
        fallback: Value to return if import fails (default: ``None``).
        warn: If True, log warning to SQLite audit DB on failure (default: ``True``).
        caller: Caller description for audit trail (e.g. ``__file__``).

    Returns:
        The imported module on success, or *fallback* on failure.

    Example::

        lens = safe_import(
            "cortex.lens.lens_orchestrator",
            fallback=None,
            warn=True,
            caller=__file__,
        )
    """
    try:
        return importlib.import_module(module_name)
    except ImportError as exc:
        if warn:
            _log_dependency_warning(module_name, str(exc), fallback, caller)
        return fallback


# AC_COMPLETE: AC-62C-DEPENDENCY-GUARD-001 ✅
