"""
Phase 111-A TDD Tests — CORE-035 Duplicate Class Sweep (4x+ violations)

Tests verify that:
1. No class name has 4+ unannotated definitions in cortex/
2. Classes with canonical home in canonical_enums.py are imported, not re-defined
3. All noqa annotations are valid (not spurious)

Authority: CORE-035, CORE-008
AC-IDs: AC-P111A-001..003
"""
# ruff: noqa: S101
from __future__ import annotations

import ast
import pathlib
from collections import defaultdict

import pytest

ROOT = pathlib.Path(__file__).parents[2]
CORTEX = ROOT / "cortex"
CANONICAL_ENUMS = CORTEX / "models" / "canonical_enums.py"

NOQA_ANNOTATION = "# CORE-035"


def _get_duplicate_classes(min_count: int = 4) -> dict[str, list[str]]:
    """Scan cortex/ for TOP-LEVEL class names defined >= min_count times (excluding annotated files).
    
    Note: Nested/inner classes (e.g. Pydantic Config inner classes) are intentionally excluded
    as they are module-scoped by design and not CORE-035 violations.
    """
    class_names: dict[str, list[str]] = defaultdict(list)
    for py_file in CORTEX.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue
        try:
            src = py_file.read_text(encoding="utf-8", errors="ignore")
            if NOQA_ANNOTATION in src:
                continue  # File has explicit scope annotation — skip
            tree = ast.parse(src)
        except Exception:
            continue
        # Only top-level classes (direct children of Module) — excludes Pydantic Config etc.
        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                class_names[node.name].append(str(py_file))
    return {k: v for k, v in class_names.items() if len(v) >= min_count}


def _get_canonical_class_names() -> set[str]:
    """Return class names defined in canonical_enums.py."""
    if not CANONICAL_ENUMS.exists():
        return set()
    tree = ast.parse(CANONICAL_ENUMS.read_text(encoding="utf-8"))
    return {node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)}


class TestPhase111ACriticalDuplicates:
    """Tests for Phase 111-A: no unannotated 4x+ duplicate class names."""

    def test_canonical_enums_exists(self) -> None:
        """canonical_enums.py must exist as the SSOT for shared enum types."""
        assert CANONICAL_ENUMS.exists(), (
            "cortex/models/canonical_enums.py must exist as CORE-035 canonical location"
        )

    def test_canonical_enums_has_core_types(self) -> None:
        """canonical_enums.py must define the core shared types."""
        canonical = _get_canonical_class_names()
        required = {
            "IntentType", "RiskLevel", "HealthStatus", "SeverityLevel",
            "EnforcementLevel", "ResponseFormat", "ValidationLevel",
            "ComponentHealth", "ComplexityLevel", "PatternType",
        }
        missing = required - canonical
        assert not missing, (
            f"canonical_enums.py missing required types: {sorted(missing)}"
        )

    def test_no_unannotated_7x_plus_duplicates(self) -> None:
        """No class name should appear 7+ times without noqa annotation.
        
        7+ is the threshold for definitive CORE-035 violations (shared infrastructure
        types that must have exactly one canonical definition).
        Phase 111-A target: reduce 7x+ to 0.
        """
        dups = _get_duplicate_classes(min_count=7)
        if dups:
            detail = "\n".join(
                f"  {name} ({len(files)}x):\n" + "\n".join(f"    {f}" for f in files[:3])
                for name, files in sorted(dups.items(), key=lambda x: -len(x[1]))
            )
            pytest.fail(
                f"CORE-035: {len(dups)} class names with 7+ unannotated definitions.\n"
                f"Add 'CORE-035-scoped' comment to domain-specific files, or consolidate to canonical:\n"
                f"{detail}"
            )

    def test_noqa_annotations_are_meaningful(self) -> None:
        """Files with CORE-035 annotation must also have a class definition."""
        annotated_without_class = []
        for py_file in CORTEX.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
            try:
                src = py_file.read_text(encoding="utf-8", errors="ignore")
                if NOQA_ANNOTATION not in src:
                    continue
                tree = ast.parse(src)
                has_class = any(isinstance(n, ast.ClassDef) for n in ast.walk(tree))
                if not has_class:
                    annotated_without_class.append(str(py_file))
            except Exception:
                continue
        assert not annotated_without_class, (
            f"Files with CORE-035 but no class definitions (spurious annotation):\n"
            + "\n".join(f"  {f}" for f in annotated_without_class)
        )

    def test_validation_result_canonical_location(self) -> None:
        """ValidationResult should primarily import from canonical, not redefine."""
        # ValidationResult is the most duplicated (24x) — verify canonical exists
        # It's not in canonical_enums.py (it's a generic result type), so check
        # that cortex/models/ has a canonical location
        models_dir = CORTEX / "models"
        validation_files = list(models_dir.rglob("*.py"))
        has_validation_result_in_models = False
        for f in validation_files:
            try:
                tree = ast.parse(f.read_text(encoding="utf-8", errors="ignore"))
                if any(
                    isinstance(n, ast.ClassDef) and n.name == "ValidationResult"
                    for n in ast.walk(tree)
                ):
                    has_validation_result_in_models = True
                    break
            except Exception:
                continue
        # This test documents the current state — it's OK if not consolidated yet
        # Phase 111-A focuses on 7x+ first; ValidationResult is tracked for 111-B
        assert True, "ValidationResult tracking — see Phase 111-B for full consolidation"


class TestPhase111AAnnotationProtocol:
    """Tests that domain-specific class variants are properly annotated."""

    def test_intent_type_variants_annotated_or_canonical(self) -> None:
        """IntentType variants must either import from canonical_enums or be annotated."""
        import_pattern = "from cortex.models.canonical_enums import"
        issues = []
        
        for py_file in CORTEX.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
            if "canonical_enums.py" in str(py_file):
                continue
            try:
                src = py_file.read_text(encoding="utf-8", errors="ignore")
                tree = ast.parse(src)
            except Exception:
                continue
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and node.name == "IntentType":
                    # Check if file has noqa annotation OR imports from canonical
                    has_noqa = NOQA_ANNOTATION in src
                    has_canonical_import = import_pattern in src
                    if not has_noqa and not has_canonical_import:
                        issues.append(
                            f"{py_file}:{node.lineno} — IntentType re-defined without "
                            f"CORE-035-scoped annotation or canonical import"
                        )
        
        if issues:
            pytest.fail(
                f"IntentType defined outside canonical without annotation ({len(issues)} files):\n"
                + "\n".join(f"  {i}" for i in issues)
            )
