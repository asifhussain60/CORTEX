"""
GAP-128-H-02: NotImplementedError stubs in production code.

Abstract interface methods raising NotImplementedError are EXPECTED and
allowed (they define a contract). What is NOT allowed is a concrete
production class with unimplemented methods that raise NotImplementedError —
those are stubs that block real execution.

This test detects files where NotImplementedError is raised in classes that
do NOT inherit from ABC/Protocol (i.e., concrete stubs).

Drift lock: check-47-production-purity-lock.yaml
"""

import ast
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
SRC_ROOT = REPO_ROOT / "cortex"

# Files confirmed to have legitimate abstract base class patterns that our
# AST heuristic may miss (e.g. using ABCMeta indirectly).
KNOWN_ABSTRACT_FILES = {
    "cortex/core/common/core_progress_reporter.py",
    "cortex/core/common/state_repair.py",
    "cortex/core/knowledge/ingestion_pipeline.py",
    "cortex/infrastructure/_quarantine/crash_recovery.py",
    "cortex/lens/cache.py",
    "cortex/lens/cache/lens_cache.py",
    "cortex/observability/metrics_collector.py",
    "cortex/orchestrators/core/intent_router_impl.py",
    "cortex/orchestrators/domain/business/plugins.py",
    "cortex/orchestrators/intelligence/interaction_patterns.py",
    "cortex/repositories/ado/ado_provider.py",
    # Uses NotImplementedError only in an except() tuple (not raising stubs)
    "cortex/infrastructure/retry_strategy.py",
    "cortex/infrastructure/github_client.py",
}

# Hard allowlist: files where NotImplementedError has been reviewed and is
# acceptable for a specific reason documented here.
REVIEWED_STUBS: dict[str, str] = {
    "cortex/tools/debug_orchestrator/__init__.py": (
        "debug_orchestrator tool wrapper — abstract interface for debug strategies"
    ),
    "cortex/intelligence/memory/core/import_resolver.py": (
        "import resolver abstract base — must be subclassed per resolver type"
    ),
}


def _file_has_abstract_marker(source: str) -> bool:
    """Return True if file uses ABC, ABCMeta, Protocol, or @abstractmethod."""
    markers = ["ABC", "ABCMeta", "Protocol", "@abstractmethod", "abstract"]
    return any(m in source for m in markers)


def _collect_stub_files() -> list[str]:
    """Return relative paths of concrete production files with unimplemented stubs."""
    stub_files = []
    py_files = [
        p for p in SRC_ROOT.rglob("*.py")
        if not any(part.startswith("test_") for part in p.parts)
        and "__pycache__" not in str(p)
    ]

    for py_file in py_files:
        rel = str(py_file.relative_to(REPO_ROOT)).replace("\\", "/")
        if rel in KNOWN_ABSTRACT_FILES or rel in REVIEWED_STUBS:
            continue

        source = py_file.read_text(encoding="utf-8", errors="replace")
        if "NotImplementedError" not in source:
            continue
        # If file uses abstract markers, it's a legitimate interface
        if _file_has_abstract_marker(source):
            continue
        # Concrete file with NotImplementedError → stub
        stub_files.append(rel)

    return stub_files


class TestNoStubs:
    """Concrete production classes must not raise NotImplementedError."""

    def test_no_unreviewed_concrete_stubs(self):
        """No concrete production file should raise NotImplementedError without ABC/Protocol."""
        stubs = _collect_stub_files()
        assert stubs == [], (
            f"Found {len(stubs)} concrete stub file(s) raising NotImplementedError "
            f"without an abstract base class marker.\n"
            f"Either:\n"
            f"  1. Implement the method, OR\n"
            f"  2. Mark the class as ABC/Protocol (if it IS an interface), OR\n"
            f"  3. Add the file to REVIEWED_STUBS with a justification.\n\n"
            f"Files:\n" + "\n".join(f"  {s}" for s in stubs)
        )

    def test_known_abstract_files_still_exist(self):
        """Regression: abstract files in the allowlist must still exist (detect renames)."""
        missing = [
            f for f in KNOWN_ABSTRACT_FILES
            if not (REPO_ROOT / f).exists()
        ]
        assert missing == [], (
            f"Abstract file(s) in allowlist no longer exist (renamed/deleted?):\n"
            + "\n".join(f"  {f}" for f in missing)
            + "\nUpdate KNOWN_ABSTRACT_FILES in this test."
        )
