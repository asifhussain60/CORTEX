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
from typing import Any, Optional

logger = logging.getLogger(__name__)

__all__ = ["soft_import"]


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
