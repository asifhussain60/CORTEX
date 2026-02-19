"""Naming Utilities — CORE-028 Enforcement

Helpers for converting, validating, and classifying filenames against
CORTEX naming conventions:

* Python files (``.py``, ``.pyi``) → ``snake_case``
* Everything else → ``kebab-case``

Phase: PHASE-51
CORE: CORE-011 (type hints), CORE-012 (docstrings), CORE-028 (naming)
"""

from __future__ import annotations

import re
from typing import Optional

from .constants import PYTHON_EXTENSIONS
from .models import NamingViolation

# ─────────────────────────────────────────────────────────────────────────────
# Conversion
# ─────────────────────────────────────────────────────────────────────────────

_CAMEL_BOUNDARY = re.compile(r"(?<=[a-z0-9])(?=[A-Z])")
_SEPARATOR_RUN = re.compile(r"[-_]+")


def _split_stem_ext(filename: str) -> tuple[str, str]:
    """Split filename into (stem_without_leading_dot, full_extension).

    Handles dot-prefixed files like ``.gitignore`` and multi-dot
    extensions like ``report.tar.gz``.
    """
    if filename.startswith("."):
        prefix = "."
        rest = filename[1:]
    else:
        prefix = ""
        rest = filename

    # Find the first dot to separate stem from extensions
    dot_idx = rest.find(".")
    if dot_idx == -1:
        return prefix + rest, ""
    return prefix + rest[:dot_idx], rest[dot_idx:]


def to_kebab_case(filename: str) -> str:
    """Convert *filename* to kebab-case, preserving extension.

    Args:
        filename: Original filename (e.g. ``AUDIT_REPORT.txt``).

    Returns:
        Kebab-case filename (e.g. ``audit-report.txt``).

    Examples::

        >>> to_kebab_case("AUDIT_REPORT.txt")
        'audit-report.txt'
        >>> to_kebab_case("MyModule.py")
        'my-module.py'
    """
    stem, ext = _split_stem_ext(filename)

    dot_prefix = ""
    if stem.startswith("."):
        dot_prefix = "."
        stem = stem[1:]

    # Insert boundaries before uppercase runs (camelCase / PascalCase)
    stem = _CAMEL_BOUNDARY.sub("-", stem)
    # Replace underscores with hyphens
    stem = stem.replace("_", "-")
    # Collapse multiple separators
    stem = _SEPARATOR_RUN.sub("-", stem)
    # Lowercase everything
    stem = stem.lower().strip("-")

    return f"{dot_prefix}{stem}{ext.lower()}"


def to_snake_case(filename: str) -> str:
    """Convert *filename* to snake_case, preserving extension.

    Args:
        filename: Original filename (e.g. ``my-module.py``).

    Returns:
        Snake-case filename (e.g. ``my_module.py``).

    Examples::

        >>> to_snake_case("my-module.py")
        'my_module.py'
        >>> to_snake_case("MyModule.py")
        'my_module.py'
    """
    stem, ext = _split_stem_ext(filename)

    # Insert boundaries before uppercase runs
    stem = _CAMEL_BOUNDARY.sub("_", stem)
    # Replace hyphens with underscores
    stem = stem.replace("-", "_")
    # Collapse multiple separators
    stem = re.sub(r"_+", "_", stem)
    # Lowercase everything
    stem = stem.lower().strip("_")

    return f"{stem}{ext}"


# ─────────────────────────────────────────────────────────────────────────────
# Detection
# ─────────────────────────────────────────────────────────────────────────────

_SCREAMING_RE = re.compile(r"^[A-Z][A-Z0-9_]*$")


def is_screaming(filename: str) -> bool:
    """Return ``True`` if the filename stem is SCREAMING_CASE.

    Args:
        filename: Filename to check (e.g. ``AUDIT_REPORT.txt``).

    Returns:
        Whether the stem is entirely uppercase.
    """
    stem, _ = _split_stem_ext(filename)
    if stem.startswith("."):
        stem = stem[1:]
    return bool(_SCREAMING_RE.match(stem))


_SNAKE_RE = re.compile(r"^_{0,2}[a-z][a-z0-9_]*_{0,2}$")


def is_valid_python_name(filename: str) -> bool:
    """Return ``True`` if *filename* is valid snake_case Python.

    Allows dunder names (``__init__.py``, ``__main__.py``).

    Args:
        filename: Filename to check.

    Returns:
        Whether the name is compliant.
    """
    stem, ext = _split_stem_ext(filename)
    if ext not in PYTHON_EXTENSIONS:
        return True  # Not a Python file — vacuously valid
    return bool(_SNAKE_RE.match(stem))


_KEBAB_RE = re.compile(r"^\.?[a-z][a-z0-9\-]*$")


def is_valid_non_python_name(filename: str) -> bool:
    """Return ``True`` if *filename* is valid kebab-case (non-Python).

    Args:
        filename: Filename to check.

    Returns:
        Whether the name is compliant.
    """
    stem, ext = _split_stem_ext(filename)
    if ext in PYTHON_EXTENSIONS:
        return True  # Python files have their own rule
    return bool(_KEBAB_RE.match(stem))


# ─────────────────────────────────────────────────────────────────────────────
# Classification
# ─────────────────────────────────────────────────────────────────────────────

def classify_naming_violation(filename: str) -> Optional[NamingViolation]:
    """Classify a filename and return a violation if non-compliant.

    Args:
        filename: Filename to classify.

    Returns:
        A :class:`NamingViolation` if the name violates CORE-028, or
        ``None`` if compliant.
    """
    stem, ext = _split_stem_ext(filename)

    # Python files → must be snake_case
    if ext in PYTHON_EXTENSIONS:
        if not is_valid_python_name(filename):
            return NamingViolation(
                original_name=filename,
                suggested_name=to_snake_case(filename),
                violation_type="non_snake_case",
            )
        return None

    # Non-Python files → must be kebab-case
    if not is_valid_non_python_name(filename):
        return NamingViolation(
            original_name=filename,
            suggested_name=to_kebab_case(filename),
            violation_type="non_kebab_case",
        )
    return None


__all__ = [
    "to_kebab_case",
    "to_snake_case",
    "is_screaming",
    "is_valid_python_name",
    "is_valid_non_python_name",
    "classify_naming_violation",
]
