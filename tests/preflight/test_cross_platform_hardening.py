"""Preflight: Cross-platform hardening checks (Phase 113 Sub-phase 0).

Prevents Windows failures caused by bare Path.read_text() calls
(no encoding parameter leads to UnicodeDecodeError on cp1252) and
bare Path.relative_to() producing backslash paths that fail frozenset lookups.

Root cause: issues.md / chat01.md Windows audit session — 15 preflight failures traced to
encoding and path-separator mismatches.

Each test is fast (regex scan, no imports) — runs in < 5s.
Tier: T0 (preflight)
"""
import pathlib
import re
from typing import List, Tuple

import pytest

CORTEX_ROOT = pathlib.Path(__file__).parents[2]

# ── Allowlists ──────────────────────────────────────────────────────────────
# Files that legitimately call bare read_text() — document why each is safe.
_READ_TEXT_ALLOWED: frozenset = frozenset({
    # file_utils.py itself defines safe_read_text() and wraps read_text with encoding=
    "cortex/core/common/file_utils.py",
})

# Directories where bare read_text() is tolerated (test fixtures, generated code)
_READ_TEXT_ALLOWED_DIRS: tuple = (
    "tests/fixtures/",
    "tests/golden/",
    "_workspaces/",
)


def _all_cortex_py_files() -> List[pathlib.Path]:
    """Return all non-pycache Python files under cortex/."""
    return [
        f for f in (CORTEX_ROOT / "cortex").rglob("*.py")
        if "__pycache__" not in str(f)
    ]


def _all_test_py_files() -> List[pathlib.Path]:
    """Return all non-pycache Python test files under tests/."""
    return [
        f for f in (CORTEX_ROOT / "tests").rglob("*.py")
        if "__pycache__" not in str(f)
        and f.name.startswith("test_")
    ]


# Regex: matches `.read_text()` WITHOUT encoding= or errors= keyword args.
# Positive match = bare read_text() call that needs hardening.
_BARE_READ_TEXT_RE = re.compile(
    r"\.read_text\(\s*\)"  # .read_text()  — no args at all
)


class TestNoNewBareReadText:
    """Block NEW bare ``read_text()`` calls in production cortex/ source.

    Existing violations are tracked separately — this test ensures the count
    does NOT increase beyond the baseline.  The ``safe_read_text()`` utility
    in ``cortex.core.common.file_utils`` should be used instead.
    """

    pytestmark = pytest.mark.timeout(60)

    # ── Baseline: known bare read_text() count in cortex/ source ────────────
    # Update this number ONLY when actively sweeping existing calls.
    # It must NEVER increase — only decrease or stay the same.
    _CORTEX_SOURCE_BASELINE = 250  # approximate current count in cortex/ source

    def test_no_new_bare_read_text_in_source(self) -> None:
        """Bare read_text() count in cortex/ must not exceed baseline.

        Any new code should use ``safe_read_text()`` or
        ``path.read_text(encoding="utf-8")`` explicitly.
        """
        violations: List[Tuple[str, int]] = []

        for f in _all_cortex_py_files():
            rel = str(f.relative_to(CORTEX_ROOT)).replace("\\", "/")
            if rel in _READ_TEXT_ALLOWED:
                continue
            if any(rel.startswith(d) for d in _READ_TEXT_ALLOWED_DIRS):
                continue
            try:
                source = f.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue
            for i, line in enumerate(source.splitlines(), 1):
                # Skip comments
                stripped = line.strip()
                if stripped.startswith("#"):
                    continue
                if _BARE_READ_TEXT_RE.search(line):
                    violations.append((f"{rel}:{i}", stripped))

        assert len(violations) <= self._CORTEX_SOURCE_BASELINE, (
            f"CROSS-PLATFORM VIOLATION: {len(violations)} bare read_text() calls "
            f"found in cortex/ (baseline: {self._CORTEX_SOURCE_BASELINE}). "
            f"Use safe_read_text() or read_text(encoding='utf-8') instead.\n"
            f"New violations:\n  "
            + "\n  ".join(f"{loc}: {code}" for loc, code in violations[:20])
        )


class TestNormalizationUtilitiesExist:
    """Verify cross-platform utilities exist and are importable."""

    def test_safe_read_text_importable(self) -> None:
        """safe_read_text must be importable from file_utils."""
        from cortex.core.common.file_utils import safe_read_text
        assert callable(safe_read_text)

    def test_normalize_rel_path_importable(self) -> None:
        """normalize_rel_path must be importable from file_utils."""
        from cortex.core.common.file_utils import normalize_rel_path
        assert callable(normalize_rel_path)

    def test_safe_read_text_returns_string(self) -> None:
        """safe_read_text must return a string when given a valid file."""
        from cortex.core.common.file_utils import safe_read_text
        # Read this test file itself
        content = safe_read_text(pathlib.Path(__file__))
        assert isinstance(content, str)
        assert "TestNormalizationUtilitiesExist" in content

    def test_normalize_rel_path_uses_forward_slashes(self) -> None:
        """normalize_rel_path must always produce forward slashes."""
        from cortex.core.common.file_utils import normalize_rel_path
        result = normalize_rel_path(pathlib.Path(__file__), CORTEX_ROOT)
        assert "\\" not in result
        assert "tests/preflight/test_cross_platform_hardening.py" == result

    def test_safe_read_text_handles_utf8(self) -> None:
        """safe_read_text must not crash on UTF-8 encoded files."""
        from cortex.core.common.file_utils import safe_read_text
        # Read a known UTF-8 file (this file)
        content = safe_read_text(pathlib.Path(__file__))
        assert len(content) > 0


class TestPreflightFilesUseEncoding:
    """All preflight test files themselves must use encoding= on read_text().

    Lead by example — preflight tests are the first thing that runs on any
    platform.  If THEY break on Windows, the entire audit pipeline is dead.
    """

    def test_preflight_tests_use_encoding(self) -> None:
        """All read_text() calls in tests/preflight/ must specify encoding=."""
        preflight_dir = CORTEX_ROOT / "tests" / "preflight"
        violations: List[Tuple[str, int, str]] = []

        for f in preflight_dir.rglob("*.py"):
            if "__pycache__" in str(f):
                continue
            try:
                source = f.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue
            # Use AST to find only actual code lines (not docstrings/comments)
            try:
                import ast as _ast
                tree = _ast.parse(source)
                # Collect all docstring line ranges to exclude
                docstring_lines: set = set()
                for node in _ast.walk(tree):
                    if isinstance(node, (_ast.FunctionDef, _ast.AsyncFunctionDef,
                                         _ast.ClassDef, _ast.Module)):
                        if (node.body and isinstance(node.body[0], _ast.Expr)
                                and isinstance(getattr(node.body[0], 'value', None),
                                               _ast.Constant)
                                and isinstance(node.body[0].value.value, str)):
                            ds = node.body[0]
                            for dl in range(ds.lineno, ds.end_lineno + 1):
                                docstring_lines.add(dl)
            except Exception:
                docstring_lines = set()

            for i, line in enumerate(source.splitlines(), 1):
                if i in docstring_lines:
                    continue
                stripped = line.strip()
                if stripped.startswith("#"):
                    continue
                if stripped.startswith(('"""', "'''", '"', "'", 'r"', "r'")):
                    continue
                if _BARE_READ_TEXT_RE.search(line):
                    rel = str(f.relative_to(CORTEX_ROOT)).replace("\\", "/")
                    violations.append((rel, i, stripped))

        assert not violations, (
            f"PREFLIGHT SELF-GOVERNANCE: {len(violations)} bare read_text() "
            f"calls in tests/preflight/. These MUST use encoding='utf-8' "
            f"to work on Windows:\n"
            + "\n".join(f"  {r}:{ln}: {txt}" for r, ln, txt in violations)
        )
