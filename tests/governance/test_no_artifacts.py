"""
GAP-128-H-03: .bak/.log/.orig/_archive artifacts in the workspace.

No build or developer artifacts should accumulate in the repository.
This test enforces artifact hygiene across the workspace.

Drift lock: check-47-production-purity-lock.yaml
"""

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent

# Artifact patterns to detect
FORBIDDEN_EXTENSIONS = {".bak", ".orig", ".rej", ".swp", ".swo"}
FORBIDDEN_NAMES = {"thumbs.db", ".ds_store"}  # lower-cased for comparison
FORBIDDEN_DIR_NAMES = {"_archive", "__pycache__"}  # dirs that should not exist in committed tree

# Paths to exclude from scanning (test fixtures, vendored assets)
EXCLUDED_DIRS = {".git", ".cortex-runtime", "node_modules", ".venv", "venv", "__pycache__"}

# .log files are allowed in .cortex-runtime/ but nowhere else in the repo
ALLOWED_LOG_DIRS = {".cortex-runtime"}


def _scan_for_artifacts() -> list[str]:
    """Walk the repo and return paths of forbidden artifacts."""
    violations = []

    for item in REPO_ROOT.rglob("*"):
        # Skip excluded directories
        parts = set(item.parts)
        if parts & {str(REPO_ROOT / d) for d in EXCLUDED_DIRS}:
            continue
        if any(part in EXCLUDED_DIRS for part in item.parts):
            continue

        if item.is_file():
            # Check forbidden extensions
            if item.suffix.lower() in FORBIDDEN_EXTENSIONS:
                violations.append(str(item.relative_to(REPO_ROOT)))
            # Check forbidden filenames (case-insensitive)
            elif item.name.lower() in FORBIDDEN_NAMES:
                violations.append(str(item.relative_to(REPO_ROOT)))
            # Check .log files outside allowed dirs
            elif item.suffix.lower() == ".log":
                rel = item.relative_to(REPO_ROOT)
                if not any(part in ALLOWED_LOG_DIRS for part in rel.parts):
                    violations.append(str(rel))

        elif item.is_dir() and item.name in FORBIDDEN_DIR_NAMES:
            # _archive dirs should not exist in committed tree
            if item.name == "_archive":
                violations.append(f"DIR: {item.relative_to(REPO_ROOT)}/")

    return violations


class TestNoArtifacts:
    """Repository must not contain build/developer artifacts."""

    def test_no_bak_orig_rej_files(self):
        """No .bak, .orig, or .rej files should exist in the repository."""
        artifacts = [
            v for v in _scan_for_artifacts()
            if any(v.endswith(ext) for ext in [".bak", ".orig", ".rej"])
        ]
        assert artifacts == [], (
            f"Found {len(artifacts)} forbidden artifact file(s):\n"
            + "\n".join(f"  {a}" for a in artifacts[:20])
        )

    def test_no_vim_swap_files(self):
        """No vim swap files (.swp, .swo) should exist."""
        swaps = [
            v for v in _scan_for_artifacts()
            if v.endswith(".swp") or v.endswith(".swo")
        ]
        assert swaps == [], (
            f"Found {len(swaps)} vim swap file(s):\n"
            + "\n".join(f"  {s}" for s in swaps)
        )

    def test_no_stray_log_files(self):
        """No .log files outside .cortex-runtime/ should exist."""
        logs = [
            v for v in _scan_for_artifacts()
            if v.endswith(".log")
        ]
        assert logs == [], (
            f"Found {len(logs)} stray .log file(s) outside .cortex-runtime/:\n"
            + "\n".join(f"  {l}" for l in logs[:20])
        )

    def test_no_archive_directories(self):
        """No _archive/ directories should exist outside of the planned/ archived path."""
        archive_dirs = [
            v for v in _scan_for_artifacts()
            if v.startswith("DIR:") and "_archive" in v
            # The planned/_archived dir is a legitimate exception
            and "planned/_archived" not in v
        ]
        assert archive_dirs == [], (
            f"Found {len(archive_dirs)} _archive directory(ies):\n"
            + "\n".join(f"  {d}" for d in archive_dirs)
        )
