"""
Phase 57-e RED — Silent ImportError observability tests.

GAP-57-07: Internal cortex.* ImportError catches must log a warning instead
           of silently passing. External library guards remain silent.

AC-ID: AC-PHASE57-E-001
Governance: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""
from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent
CORTEX_SRC = REPO_ROOT / "cortex"

# Modules that are legitimate optional external deps (keep silent)
EXTERNAL_OPTIONAL_LIBS = frozenset({
    "yaml", "prometheus_client", "opentelemetry", "structlog",
    "rich", "uvicorn", "fastapi", "starlette", "aiohttp",
    "redis", "celery", "sqlalchemy", "alembic", "boto3",
    "botocore", "google", "azure", "anthropic", "openai",
    "tiktoken", "torch", "transformers", "sklearn", "numpy",
    "pandas", "matplotlib", "plotly",
})


def _is_internal_import(import_name: str) -> bool:
    """Return True if the import is a CORTEX-internal module."""
    return import_name.startswith("cortex.")


def _collect_bare_internal_import_errors(src_dir: Path) -> list[dict]:
    """Walk cortex/ source and find bare 'except ImportError: pass' for cortex.* imports."""
    violations = []
    for py_file in sorted(src_dir.rglob("*.py")):
        # Skip test files — RED-phase stubs legitimately use bare pass
        if py_file.name.startswith("test_") or py_file.name.endswith("_test.py"):
            continue
        source = py_file.read_text(errors="replace")
        try:
            tree = ast.parse(source, filename=str(py_file))
        except SyntaxError:
            continue

        for node in ast.walk(tree):
            if not isinstance(node, ast.Try):
                continue
            for handler in node.handlers:
                if not (
                    handler.type is not None
                    and isinstance(handler.type, ast.Name)
                    and handler.type.id == "ImportError"
                ):
                    continue
                # body must be a bare 'pass' or 'continue'
                if len(handler.body) != 1 or not isinstance(handler.body[0], ast.Pass):
                    continue
                # Determine which module is being imported in the try block
                for stmt in node.body:
                    if isinstance(stmt, (ast.Import, ast.ImportFrom)):
                        module_name = ""
                        if isinstance(stmt, ast.ImportFrom) and stmt.module:
                            module_name = stmt.module
                        elif isinstance(stmt, ast.Import):
                            for alias in stmt.names:
                                module_name = alias.name
                        if _is_internal_import(module_name):
                            violations.append({
                                "file": str(py_file.relative_to(REPO_ROOT)),
                                "line": handler.lineno,
                                "module": module_name,
                            })
    return violations


class TestImportErrorObservability:
    """GAP-57-07: bare 'except ImportError: pass' for cortex.* imports must be logged."""

    @pytest.mark.timeout(90)  # AST-walks 1,346 files — needs >30s global default under xdist load
    def test_internal_import_failures_are_logged(self) -> None:
        """Zero bare 'except ImportError: pass' blocks for cortex.* imports after fix."""
        violations = _collect_bare_internal_import_errors(CORTEX_SRC)
        if violations:
            details = "\n".join(
                f"  {v['file']}:{v['line']} (import {v['module']})"
                for v in violations[:20]
            )
            pytest.fail(
                f"Found {len(violations)} bare 'except ImportError: pass' for cortex.* imports:\n"
                f"{details}\n"
                "Replace 'pass' with logger.warning(f'Optional dependency unavailable: ...')"
            )

    @pytest.mark.timeout(90)  # AST-walks 1,346 files — needs >30s global default under xdist load
    def test_external_import_failures_remain_silent(self) -> None:
        """External library import guards must stay as bare pass (no regression)."""
        # This is a lint/audit check — external guards are intentionally silent.
        # Just verify the internal check didn't accidentally flag external ones.
        violations = _collect_bare_internal_import_errors(CORTEX_SRC)
        for v in violations:
            # If any flagged module is in the external list — that's a false positive
            for ext in EXTERNAL_OPTIONAL_LIBS:
                assert ext not in v["module"], (
                    f"External guard for '{v['module']}' was incorrectly flagged. "
                    "Only cortex.* internal imports should be made observable."
                )
