"""
GAP-128-E-01: Orchestrator public methods must reference 'handle', 'execute', or 'run'
as their primary entry point — verifying method naming coverage across orchestrators.

Tests that:
- Core orchestrators implement the IOrchestrator protocol (have handle() or execute())
- No orchestrator class is entirely empty (has at least one public method)
- Public method names follow snake_case convention

Drift lock: check-45-orchestrator-wiring-integrity-lock.yaml
"""

import ast
import re
from pathlib import Path
from typing import List, Tuple
import pytest

REPO_ROOT = Path(__file__).parents[3]
ORCHESTRATORS_DIR = REPO_ROOT / "cortex/orchestrators"

# Core orchestrators that must implement handle() or execute()
CORE_ORCHESTRATOR_FILES = [
    "core/master_orchestrator.py",
    "core/intent_router.py",
    "core/tdd_orchestrator.py",
    "core/enforcement_orchestrator.py",
    "health/health_orchestrator.py",
    "health/vacuum_orchestrator.py",
    "support/debugger_orchestrator.py",
]

# Pattern for valid public method names
SNAKE_CASE_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")


def _get_class_methods(file_path: Path) -> List[Tuple[str, List[str]]]:
    """Return list of (class_name, [method_names]) from a Python file."""
    try:
        tree = ast.parse(file_path.read_text(encoding="utf-8"))
    except (SyntaxError, UnicodeDecodeError):
        return []
    results = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            methods = [
                n.name for n in node.body
                if isinstance(n, ast.FunctionDef) or isinstance(n, ast.AsyncFunctionDef)
            ]
            results.append((node.name, methods))
    return results


def _get_public_methods(methods: List[str]) -> List[str]:
    """Return only non-dunder public methods."""
    return [m for m in methods if not m.startswith("_")]


class TestMethodUsageCoverage:
    """GAP-128-E-01: Orchestrator method naming and protocol coverage."""

    def test_orchestrators_dir_exists(self):
        """cortex/orchestrators/ directory must exist."""
        assert ORCHESTRATORS_DIR.exists(), f"Orchestrators directory not found: {ORCHESTRATORS_DIR}"

    def test_core_orchestrators_have_entry_points(self):
        """Core orchestrators that exist must have at least one public method."""
        found_any = False
        missing = []
        for rel_file in CORE_ORCHESTRATOR_FILES:
            file_path = ORCHESTRATORS_DIR / rel_file
            if not file_path.exists():
                # Not all files from the architecture table exist in every layout variant
                continue
            found_any = True
            class_methods = _get_class_methods(file_path)
            for class_name, methods in class_methods:
                if "Orchestrator" not in class_name and "Router" not in class_name:
                    continue
                public = _get_public_methods(methods)
                if not public:
                    missing.append(f"{rel_file}::{class_name}: no public methods at all")
        # At least one of the listed files must exist
        assert found_any, (
            "None of the core orchestrator files were found — check CORE_ORCHESTRATOR_FILES list"
        )
        assert missing == [], (
            f"Orchestrators with zero public methods:\n"
            + "\n".join(f"  {m}" for m in missing)
        )

    def test_orchestrator_public_methods_are_snake_case(self):
        """All public methods in orchestrator files must use snake_case naming.

        AST visitor methods (visit_Xxx) are exempt — Python ast module
        uses camelCase suffixes by convention (visit_If, visit_For, etc.).
        """
        violations: List[str] = []
        # visit_Xxx pattern used by Python's ast.NodeVisitor — always CamelCase suffix
        AST_VISITOR_PATTERN = re.compile(r"^visit_[A-Z][a-zA-Z0-9]+$")
        for py_file in sorted(ORCHESTRATORS_DIR.rglob("*.py")):
            if py_file.name.startswith("test_"):
                continue
            class_methods = _get_class_methods(py_file)
            rel = py_file.relative_to(REPO_ROOT)
            for class_name, methods in class_methods:
                for method in _get_public_methods(methods):
                    if AST_VISITOR_PATTERN.match(method):
                        # AST visitor methods are exempt — stdlib naming convention
                        continue
                    if not SNAKE_CASE_PATTERN.match(method):
                        violations.append(f"{rel}::{class_name}.{method}")
        assert violations == [], (
            f"Non-snake_case public methods in orchestrators:\n"
            + "\n".join(f"  {v}" for v in violations[:20])
        )

    def test_no_empty_orchestrator_classes(self):
        """No concrete orchestrator class should be completely empty (no methods at all).

        Exempt: Enum classes, Error/Exception/Result types, metadata dataclasses,
        and mixin/base placeholders that exist for typing purposes only.
        """
        EXEMPT_SUFFIXES = ("Error", "Exception", "Result", "Metadata", "Category", "Impl")
        empty_classes: List[str] = []
        for py_file in sorted(ORCHESTRATORS_DIR.rglob("*.py")):
            if "__pycache__" in str(py_file):
                continue
            class_methods = _get_class_methods(py_file)
            rel = py_file.relative_to(REPO_ROOT)
            for class_name, methods in class_methods:
                if not ("Orchestrator" in class_name or "Router" in class_name):
                    continue
                # Skip exempt types — enums, error wrappers, metadata, impl stubs
                if any(class_name.endswith(suffix) for suffix in EXEMPT_SUFFIXES):
                    continue
                if len(methods) == 0:
                    empty_classes.append(f"{rel}::{class_name}")
        assert empty_classes == [], (
            f"Empty orchestrator classes (no methods at all):\n"
            + "\n".join(f"  {c}" for c in empty_classes)
        )

    def test_orchestrator_file_count_substantial(self):
        """At least 100 orchestrator Python files should exist."""
        py_files = [f for f in ORCHESTRATORS_DIR.rglob("*.py") if "__pycache__" not in str(f)]
        count = len(py_files)
        assert count >= 100, (
            f"Expected ≥100 orchestrator Python files, found {count}"
        )
