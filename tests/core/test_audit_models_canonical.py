"""
Phase 59-a: Canonical AuditEntry Tests (RED → GREEN → REFACTOR)

CORE-008: Tests written BEFORE implementation.
CORE-035: Verifies single canonical definition across the entire codebase.
CORE-011: All functions typed.
CORE-012: All public APIs documented.

GAP-59-01: 9 duplicate AuditEntry class definitions must be consolidated
           into cortex.core.audit_models with 8 files re-exporting from there.

AC_START: AC-AUDIT-MODELS-5901
"""
from __future__ import annotations

import ast
import importlib
import inspect
import subprocess
import sys
from dataclasses import fields as dc_fields
from pathlib import Path
from typing import Set

import pytest

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).parent.parent.parent
CORTEX_ROOT = REPO_ROOT / "cortex"
CANONICAL_MODULE = "cortex.core.audit_models"
CANONICAL_CLASS = "AuditEntry"

# The 9 files that HAD their own AuditEntry definition.
# After 59-a, 8 of them must re-export; only audit_models.py defines it.
PREVIOUSLY_DUPLICATE_FILES: list[Path] = [
    CORTEX_ROOT / "core" / "intent" / "intent_reflection_protocol.py",
    CORTEX_ROOT / "intelligence" / "domain_brain" / "audit_log_manager.py",
    CORTEX_ROOT / "intelligence" / "domain_brain" / "domain_brain_models.py",
    CORTEX_ROOT / "intelligence" / "domain_brain" / "api.py",
    CORTEX_ROOT / "governance" / "audit_navigator.py",
    CORTEX_ROOT / "infrastructure" / "secrets" / "audit_trail.py",
    CORTEX_ROOT / "infrastructure" / "secrets" / "management.py",
    CORTEX_ROOT / "infrastructure" / "enhanced_audit_logger.py",
    CORTEX_ROOT / "infrastructure" / "audit_db.py",
]

# Required fields on the canonical superset definition.
REQUIRED_FIELDS: Set[str] = {
    # Core identity
    "entry_id",
    "operation",
    "timestamp",
    "status",
    # Content
    "details",
    "message",
    # Orchestrator tracking
    "ac_id",
    "orchestrator_id",
    "duration_ms",
    "error_message",
    # Domain context
    "domain",
    "entity_id",
    "entity_type",
    # Actor / key for secrets auditing
    "actor",
    "action",
    "key",
    "success",
    # Chain integrity
    "entry_hash",
    "previous_hash",
    "description",
}


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------
def _count_class_defs_in_file(path: Path, class_name: str) -> int:
    """Return the number of top-level class definitions named *class_name* in *path*."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except SyntaxError:
        return 0
    return sum(
        1
        for node in ast.walk(tree)
        if isinstance(node, ast.ClassDef) and node.name == class_name
    )


# ---------------------------------------------------------------------------
# Test 1: cortex.core.audit_models exists and exposes AuditEntry
# ---------------------------------------------------------------------------
class TestCanonicalModuleExists:
    """59-a-T1: canonical module must exist and export AuditEntry."""

    def test_canonical_module_importable(self) -> None:
        """cortex.core.audit_models must import without error."""
        try:
            mod = importlib.import_module(CANONICAL_MODULE)
        except ModuleNotFoundError as exc:
            pytest.fail(
                f"GAP-59-01 | {CANONICAL_MODULE} does not exist yet — "
                f"create cortex/core/audit_models.py (59-a GREEN phase). "
                f"Error: {exc}"
            )
        assert mod is not None

    def test_canonical_module_exports_audit_entry(self) -> None:
        """cortex.core.audit_models must have class AuditEntry."""
        mod = importlib.import_module(CANONICAL_MODULE)
        assert hasattr(mod, CANONICAL_CLASS), (
            f"GAP-59-01 | {CANONICAL_MODULE} must define class AuditEntry"
        )
        cls = getattr(mod, CANONICAL_CLASS)
        assert inspect.isclass(cls), f"AuditEntry in {CANONICAL_MODULE} must be a class"

    def test_canonical_is_dataclass(self) -> None:
        """Canonical AuditEntry must be a dataclass."""
        mod = importlib.import_module(CANONICAL_MODULE)
        cls = getattr(mod, CANONICAL_CLASS)
        # dataclasses.fields() raises TypeError if not a dataclass
        try:
            fds = dc_fields(cls)  # type: ignore[arg-type]
        except TypeError:
            pytest.fail("GAP-59-01 | AuditEntry in audit_models must be @dataclass")
        assert len(fds) >= len(REQUIRED_FIELDS), (
            f"Canonical AuditEntry must have at least {len(REQUIRED_FIELDS)} fields; "
            f"got {len(fds)}"
        )


# ---------------------------------------------------------------------------
# Test 2: Canonical definition is a superset of all variant fields
# ---------------------------------------------------------------------------
class TestCanonicalSuperset:
    """59-a-T2: canonical AuditEntry must cover every field from all 9 variants."""

    def test_all_required_fields_present(self) -> None:
        """Every field from the 9 legacy variants must exist on the canonical class."""
        mod = importlib.import_module(CANONICAL_MODULE)
        cls = getattr(mod, CANONICAL_CLASS)
        canonical_field_names: Set[str] = {f.name for f in dc_fields(cls)}  # type: ignore[arg-type]
        missing = REQUIRED_FIELDS - canonical_field_names
        assert not missing, (
            f"GAP-59-01 | Canonical AuditEntry missing fields from legacy variants: "
            f"{sorted(missing)}"
        )

    def test_all_required_fields_have_defaults(self) -> None:
        """All fields except entry_id must be optional (have defaults) for backward compat."""
        mod = importlib.import_module(CANONICAL_MODULE)
        cls = getattr(mod, CANONICAL_CLASS)
        # Fields that MUST have a default to be backward-compatible with callers
        # that only provided a subset of fields.
        # entry_id is the only mandatory field (it's the primary key).
        mandatory_allowed = {"entry_id"}
        no_default: list[str] = []
        import dataclasses
        sentinel = dataclasses.MISSING
        for f in dc_fields(cls):  # type: ignore[arg-type]
            if f.name in mandatory_allowed:
                continue
            has_default = f.default is not sentinel
            has_default_factory = f.default_factory is not sentinel  # type: ignore[misc]
            if not has_default and not has_default_factory:
                no_default.append(f.name)
        assert not no_default, (
            f"GAP-59-01 | These AuditEntry fields lack defaults (callers with subsets "
            f"will break): {no_default}"
        )

    def test_audit_entry_has_to_dict(self) -> None:
        """Canonical AuditEntry must expose to_dict() for legacy callers that used it."""
        mod = importlib.import_module(CANONICAL_MODULE)
        cls = getattr(mod, CANONICAL_CLASS)
        assert hasattr(cls, "to_dict"), (
            "GAP-59-01 | Canonical AuditEntry must have to_dict() "
            "(required by audit_db and api variants)"
        )
        instance = cls(entry_id="test-001")
        result = instance.to_dict()
        assert isinstance(result, dict), "to_dict() must return dict"
        assert "entry_id" in result


# ---------------------------------------------------------------------------
# Test 3: No duplicate class definitions remain in the 9 legacy files
# ---------------------------------------------------------------------------
class TestNoDuplicateClassDefinition:
    """59-a-T3: After 59-a, the 9 files must NOT define their own AuditEntry class."""

    @pytest.mark.parametrize("source_file", PREVIOUSLY_DUPLICATE_FILES)
    def test_file_does_not_define_audit_entry_class(self, source_file: Path) -> None:
        """Each formerly-duplicating file must not contain 'class AuditEntry'."""
        if not source_file.exists():
            pytest.skip(f"File not found (may have been removed): {source_file}")
        count = _count_class_defs_in_file(source_file, CANONICAL_CLASS)
        assert count == 0, (
            f"GAP-59-01 | {source_file.relative_to(REPO_ROOT)} still defines "
            f"'class AuditEntry' — replace with "
            f"'from cortex.core.audit_models import AuditEntry'"
        )

    @pytest.mark.parametrize("source_file", PREVIOUSLY_DUPLICATE_FILES)
    def test_file_imports_from_canonical(self, source_file: Path) -> None:
        """Each legacy file must import AuditEntry from the canonical module."""
        if not source_file.exists():
            pytest.skip(f"File not found: {source_file}")
        content = source_file.read_text(encoding="utf-8")
        assert "from cortex.core.audit_models import" in content, (
            f"GAP-59-01 | {source_file.relative_to(REPO_ROOT)} does not import "
            f"AuditEntry from cortex.core.audit_models"
        )


# ---------------------------------------------------------------------------
# Test 4: Whole-codebase grep — exactly ONE class definition
# ---------------------------------------------------------------------------
class TestCodbaseHasSingleDefinition:
    """59-a-T4: grep across entire cortex/ must find exactly 1 AuditEntry class def."""

    def test_only_one_class_audit_entry_in_codebase(self) -> None:
        """
        grep 'class AuditEntry' cortex/ --include='*.py' must yield exactly 1 result:
        cortex/core/audit_models.py
        """
        result = subprocess.run(
            [
                "grep", "-rn", "class AuditEntry",
                str(CORTEX_ROOT),
                "--include=*.py",
            ],
            capture_output=True,
            text=True,
        )
        matches = [
            line for line in result.stdout.splitlines()
            if "__pycache__" not in line and line.strip()
        ]
        assert len(matches) == 1, (
            f"GAP-59-01 | Expected exactly 1 'class AuditEntry' definition in cortex/; "
            f"found {len(matches)}:\n" + "\n".join(matches)
        )
        assert "audit_models.py" in matches[0], (
            f"GAP-59-01 | The single AuditEntry definition must be in "
            f"cortex/core/audit_models.py, not: {matches[0]}"
        )

# AC_COMPLETE: AC-AUDIT-MODELS-5901 (test file) ✅
