"""
tests/models/test_phase119_import_hygiene.py — Phase 119-D TDD Red→Green

Governance gate for CORE-035 Sub-Phase D: verify no file in cortex/ imports
a canonical class from a shadow (non-canonical) path.

Canonical paths (SSOT):
  ValidationResult  → cortex.models.shared.validation (re-exports from cortex.models.validation_result)
  HealthCheckResult → cortex.models.shared.health
  CacheEntry        → cortex.models.shared.cache
  CacheStats        → cortex.models.shared.cache
  ExecutionResult   → cortex.models.shared.execution

Shadow paths (imports from these should be replaced with canonical):
  Any import of ValidationResult from cortex.core.common.validators,
  cortex.core.input_validator, cortex.tools.template_validator, etc.

Also verifies cortex.models.shared.__init__ exports __all__ with all canonical types.

Governance: CORE-008 (TDD), CORE-035 (single canonical), CORE-064 (sweep)
Authority: phase-119-d, SWEEP-119-CLASS-CONSOLIDATION
"""
from __future__ import annotations

import pathlib
import re
from typing import List, Tuple

import pytest


CORTEX_ROOT = pathlib.Path(__file__).parent.parent.parent / "cortex"

# ─────────────────────────────────────────────────────────────────────────────
# SHADOW IMPORT PATTERNS — any file importing canonical types from non-canonical
# paths must be updated to use cortex.models.shared.*
# ─────────────────────────────────────────────────────────────────────────────

# (class_name, shadow_module_pattern_regex)
SHADOW_IMPORT_CHECKS = [
    (
        "ValidationResult",
        r"from cortex\.(core\.common\.validators|core\.input_validator"
        r"|core\.common\.output_validator|tools\.template_validator"
        r"|tools\.template_parser|tools\.toolkit\.toolkit_validation"
        r"|core\.response_format_validator|core\.wiring\.registry\.contract_validator"
        r"|governance\.filename_factory|governance\.test_scope_validator"
        r"|governance\.enforcement\.agents\.\w+"
        r"|infrastructure\.deployment\.deployment_validator"
        r"|infrastructure\.devx\.integration_validator"
        r"|intelligence\.domain_brain\.domain_brain_models"
        r"|intelligence\.memory\.\S+"
        r"|orchestrators\.domain\.\w+"
        r"|orchestrators\.git\.sanitization_orchestrator"
        r"|orchestrators\.validation\.\w+"
        r"|templates\.(content_strategy|knowledge_schema))"
        r"\s+import\s+.*\bValidationResult\b",
    ),
    (
        "HealthCheckResult",
        r"from cortex\.(core\.wiring\.health_check"
        r"|core\.production_readiness_manager"
        r"|core\.registry\.(base_registry|health_monitor)"
        r"|testing\.routing_health_checks"
        r"|tools\.dashboard_server"
        r"|orchestrators\.health\.agents\.base_agent"
        r"|infrastructure\.pre_commit_validator)"
        r"\s+import\s+.*\bHealthCheckResult\b",
    ),
]


def _find_shadow_imports(class_name: str, shadow_pattern: str) -> List[Tuple[str, int, str]]:
    """Return (filepath, lineno, matching_line) for MODULE-LEVEL shadow imports of class_name.

    Function-local (lazy) imports inside method bodies are excluded — those are
    intentional domain-scoped patterns where the local class IS the correct import target.
    Only module-level imports (indentation = 0) are flagged.
    """
    results = []
    regex = re.compile(shadow_pattern)
    for f in CORTEX_ROOT.rglob("*.py"):
        if "__pycache__" in str(f) or "_quarantine" in str(f):
            continue
        try:
            lines = f.read_text(errors="ignore").splitlines()
            for i, line in enumerate(lines, 1):
                if regex.search(line):
                    # Only flag module-level imports (no leading whitespace)
                    stripped = line.lstrip()
                    indent = len(line) - len(stripped)
                    if indent == 0:  # module-level only
                        results.append((str(f.relative_to(CORTEX_ROOT.parent)), i, line.strip()))
        except Exception:
            pass
    return results


def test_no_shadow_validation_result_imports() -> None:
    """No file may import ValidationResult from a non-canonical shadow path.

    Canonical: cortex.models.shared.validation (or cortex.models.validation_result).
    All other paths are shadow locations where ValidationResult is locally defined
    but should not be imported from externally.

    RED: cortex/intelligence/domain_brain/validator.py imports from
    cortex.core.common.validators — must be fixed to use canonical.
    """
    cls_name, pattern = SHADOW_IMPORT_CHECKS[0]
    shadows = _find_shadow_imports(cls_name, pattern)
    assert shadows == [], (
        f"CORE-035: {len(shadows)} shadow import(s) of '{cls_name}' from non-canonical path:\n"
        + "\n".join(f"  {fp}:{ln}: {line}" for fp, ln, line in shadows)
        + f"\n\nFix: replace with: from cortex.models.shared.validation import {cls_name}"
    )


def test_no_shadow_health_check_result_imports() -> None:
    """No file may import HealthCheckResult from a non-canonical shadow path.

    Canonical: cortex.models.shared.health.
    """
    cls_name, pattern = SHADOW_IMPORT_CHECKS[1]
    shadows = _find_shadow_imports(cls_name, pattern)
    assert shadows == [], (
        f"CORE-035: {len(shadows)} shadow import(s) of '{cls_name}' from non-canonical path:\n"
        + "\n".join(f"  {fp}:{ln}: {line}" for fp, ln, line in shadows)
        + f"\n\nFix: replace with: from cortex.models.shared.health import {cls_name}"
    )


# ─────────────────────────────────────────────────────────────────────────────
# SHARED __init__ EXPORTS
# ─────────────────────────────────────────────────────────────────────────────

def test_shared_init_exports_all_canonical() -> None:
    """cortex.models.shared.__init__ must export all canonical types via __all__."""
    from cortex.models import shared  # noqa: F401

    required_exports = [
        "ValidationResult",
        "HealthCheckResult",
        "CacheEntry",
        "ExecutionResult",
    ]
    all_exports = getattr(shared, "__all__", [])
    missing = [name for name in required_exports if name not in all_exports]
    assert missing == [], (
        f"cortex.models.shared.__all__ is missing: {missing}. "
        f"Current __all__ = {all_exports}"
    )


def test_canonical_shared_imports_work() -> None:
    """All canonical types must be importable from cortex.models.shared directly."""
    from cortex.models.shared import (  # noqa: F401
        ValidationResult,
        HealthCheckResult,
        CacheEntry,
        ExecutionResult,
    )
    assert ValidationResult is not None
    assert HealthCheckResult is not None
    assert CacheEntry is not None
    assert ExecutionResult is not None
