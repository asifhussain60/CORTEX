"""Phase 128-f — Production Purity Sweep (drift lock #47).

Verifies that ``cortex/`` source code contains no production-hostile patterns:

1. ``pdb`` import or ``pdb.set_trace()`` — interactive debugger must never ship
2. ``breakpoint()`` — Python 3.7+ interactive debugger hook must never ship
3. Hardcoded developer machine paths (``/Users/<name>/``) — breaks all non-macOS
4. Hardcoded ``DEBUG = True`` assignment — must come from environment variables
5. Bare ``__import__("pdb")`` — dynamic pdb invocation must never ship

This test complements ``tests/preflight/test_stub_eradication.py`` (which covers
TODO/FIXME/NotImplementedError stubs) with environment-specific leakage detection.

Gap ref: GAP-128-06
Drift lock: cortex-registry/governance/drift-locks/check-47-production-purity-lock.yaml
Tier: T1 (governance)
CORE rule: CORE-035 (single canonical implementation — no dev-mode leakage)
"""
from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
CORTEX_ROOT = Path(__file__).parents[2]
CORTEX_SRC = CORTEX_ROOT / "cortex"

# ---------------------------------------------------------------------------
# Patterns
# ---------------------------------------------------------------------------

# pdb / breakpoint — no legitimate reason to ship
_PDB_IMPORT_RE = re.compile(r"\bimport\s+pdb\b")
_PDB_SET_TRACE_RE = re.compile(r"\bpdb\.set_trace\s*\(\s*\)")
_PDB_DYNAMIC_RE = re.compile(r'__import__\s*\(\s*["\']pdb["\']')
_BREAKPOINT_RE = re.compile(r"\bbreakpoint\s*\(\s*\)")

# Hardcoded developer machine path — /Users/<alphanum> indicates an absolute
# macOS home dir. These must not appear in source (use Path(__file__) or env vars).
_HARDCODED_USER_PATH_RE = re.compile(r"/Users/[A-Za-z]")

# DEBUG = True as a literal assignment (not a string comparison, not a comment,
# not a docstring). We use an AST check for precision.
_DEBUG_ASSIGN_RE = re.compile(
    r"^(?!#).*\bDEBUG\s*=\s*True\b",
    re.MULTILINE,
)


# ---------------------------------------------------------------------------
# Allow-lists
# ---------------------------------------------------------------------------

# Files that legitimately reference these patterns as STRING LITERALS being
# scanned/detected — they are security/analysis tools, not violations.
_PURITY_ALLOWLIST: frozenset[str] = frozenset({
    # These files detect pdb/breakpoint/debug patterns IN USER CODE — they are
    # the guardians, not the offenders.
    "cortex/orchestrators/validation/pre_implementation_checklist.py",  # detects localhost
    "cortex/orchestrators/core/security_orchestrator.py",               # os.system scanner
    "cortex/governance/validators/",                                     # governance scanners
    "cortex/intelligence/memory/tier2_adaptive/security/__init__.py",   # forbidden-module list
    "cortex/intelligence/analysis/security_auditor.py",                 # "DEBUG = True" detector
})


def _is_allowlisted(path: Path) -> bool:
    """Return True if the file is in the purity allow-list."""
    rel = str(path.relative_to(CORTEX_ROOT))
    return any(rel.startswith(al.rstrip("/")) for al in _PURITY_ALLOWLIST)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _collect_source_files() -> list[Path]:
    """All .py files in cortex/ excluding __pycache__."""
    return [
        f
        for f in CORTEX_SRC.rglob("*.py")
        if "__pycache__" not in str(f)
    ]


def _check_pattern(pattern: re.Pattern, source_files: list[Path]) -> list[tuple[str, int, str]]:
    """Return (relpath, lineno, line) for every match of *pattern* in source files."""
    violations: list[tuple[str, int, str]] = []
    for f in source_files:
        if _is_allowlisted(f):
            continue
        try:
            text = f.read_text(errors="ignore")
        except OSError:
            continue
        for i, line in enumerate(text.splitlines(), start=1):
            if pattern.search(line):
                rel = str(f.relative_to(CORTEX_ROOT))
                violations.append((rel, i, line.strip()[:120]))
    return violations


def _check_debug_assign_ast(source_files: list[Path]) -> list[tuple[str, int, str]]:
    """Use AST to find literal ``DEBUG = True`` assignments (not in comments or strings)."""
    violations: list[tuple[str, int, str]] = []
    for f in source_files:
        if _is_allowlisted(f):
            continue
        try:
            source = f.read_text(errors="ignore")
            tree = ast.parse(source, filename=str(f))
        except (OSError, SyntaxError):
            continue
        for node in ast.walk(tree):
            if not isinstance(node, (ast.Assign, ast.AnnAssign)):
                continue
            # Check targets
            targets = []
            if isinstance(node, ast.Assign):
                targets = node.targets
                value = node.value
            else:
                targets = [node.target]
                value = node.value
            if value is None:
                continue
            # Target must be named DEBUG
            for t in targets:
                if isinstance(t, ast.Name) and t.id == "DEBUG":
                    # Value must be True constant
                    if isinstance(value, ast.Constant) and value.value is True:
                        rel = str(f.relative_to(CORTEX_ROOT))
                        violations.append((rel, node.lineno, f"DEBUG = True (AST-detected)"))
    return violations


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def source_files() -> list[Path]:
    return _collect_source_files()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_no_pdb_import(source_files):
    """No ``import pdb`` in production source — interactive debugger must not ship."""
    violations = _check_pattern(_PDB_IMPORT_RE, source_files)
    assert violations == [], (
        f"Found {len(violations)} 'import pdb' violations:\n"
        + "\n".join(f"  {p}:{ln}  {line}" for p, ln, line in violations)
    )


def test_no_pdb_set_trace(source_files):
    """No ``pdb.set_trace()`` calls in production source."""
    violations = _check_pattern(_PDB_SET_TRACE_RE, source_files)
    assert violations == [], (
        f"Found {len(violations)} 'pdb.set_trace()' violations:\n"
        + "\n".join(f"  {p}:{ln}  {line}" for p, ln, line in violations)
    )


def test_no_pdb_dynamic_import(source_files):
    """No ``__import__('pdb')`` dynamic pdb invocation in production source."""
    violations = _check_pattern(_PDB_DYNAMIC_RE, source_files)
    assert violations == [], (
        f"Found {len(violations)} dynamic pdb import violations:\n"
        + "\n".join(f"  {p}:{ln}  {line}" for p, ln, line in violations)
    )


def test_no_breakpoint(source_files):
    """No ``breakpoint()`` calls in production source."""
    violations = _check_pattern(_BREAKPOINT_RE, source_files)
    # Allow in test helpers only
    prod_violations = [v for v in violations if not v[0].startswith("tests/")]
    assert prod_violations == [], (
        f"Found {len(prod_violations)} 'breakpoint()' violations:\n"
        + "\n".join(f"  {p}:{ln}  {line}" for p, ln, line in prod_violations)
    )


def test_no_hardcoded_developer_paths(source_files):
    """No hardcoded ``/Users/<name>/`` paths in production source.

    Use ``Path(__file__).parents[N]`` or environment variables instead.
    """
    violations = _check_pattern(_HARDCODED_USER_PATH_RE, source_files)
    assert violations == [], (
        f"Found {len(violations)} hardcoded developer path violations:\n"
        + "\n".join(f"  {p}:{ln}  {line}" for p, ln, line in violations)
    )


def test_no_debug_true_literal_assignment(source_files):
    """No literal ``DEBUG = True`` assignments in production source.

    Debug flags must be read from environment variables or config files.
    Security scanners that DETECT this pattern in user code are allow-listed.
    """
    violations = _check_debug_assign_ast(source_files)
    assert violations == [], (
        f"Found {len(violations)} 'DEBUG = True' literal assignments:\n"
        + "\n".join(f"  {p}:{ln}  {line}" for p, ln, line in violations)
    )


def test_cortex_src_has_expected_minimum_files(source_files):
    """Sanity guard: cortex/ must contain at least 300 Python files.

    A count collapse indicates the scanner is not reaching the source tree.
    """
    assert len(source_files) >= 300, (
        f"cortex/ scan only found {len(source_files)} .py files — "
        "expected ≥ 300. Check that CORTEX_SRC path is correct."
    )
