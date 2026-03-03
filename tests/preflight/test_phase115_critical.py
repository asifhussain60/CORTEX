"""
tests/preflight/test_phase115_critical.py — Phase 115-a + 115-b RED→GREEN

Critical fixes:
  GAP-115-01: lens_orchestrator.py monolith deleted
  GAP-115-02: infrastructure quarantine — unreferenced modules moved
  GAP-115-03: brain_state_manager.py shim imports StateSnapshot + FlushResult

Governance: CORE-008 (TDD), CORE-035 (single canonical), CORE-064 (sweep)
Phase: 115-a + 115-b
"""
import pathlib
import importlib
import pytest


# ─────────────────────────────────────────────────────────────────
# GAP-115-01: lens monolith deletion
# ─────────────────────────────────────────────────────────────────

def test_lens_orchestrator_monolith_deleted():
    """cortex/lens/lens_orchestrator.py (2,045-line monolith) must not exist.

    The package cortex/lens/lens_orchestrator/ was created in Phase 103-d.
    The monolith file must be deleted to enforce CORE-035 (single canonical).
    """
    monolith = pathlib.Path("cortex/lens/lens_orchestrator.py")
    assert not monolith.exists(), (
        "cortex/lens/lens_orchestrator.py still exists alongside the package. "
        "Delete the monolith — the package cortex/lens/lens_orchestrator/ is canonical."
    )


def test_lens_orchestrator_package_canonical():
    """LENSOrchestrator must import correctly from the package (not the monolith)."""
    try:
        from cortex.lens.lens_orchestrator import LENSOrchestrator  # noqa: F401
        assert LENSOrchestrator is not None
    except ImportError as e:
        pytest.fail(f"Cannot import LENSOrchestrator from cortex.lens.lens_orchestrator package: {e}")


# ─────────────────────────────────────────────────────────────────
# GAP-115-03: brain_state_manager shim completeness
# ─────────────────────────────────────────────────────────────────

def test_brain_state_manager_exports_state_snapshot():
    """cortex.core.brain_state_manager must export StateSnapshot."""
    try:
        from cortex.core.brain_state_manager import StateSnapshot  # noqa: F401
        assert StateSnapshot is not None
    except ImportError as e:
        pytest.fail(f"Cannot import StateSnapshot from cortex.core.brain_state_manager: {e}")


def test_brain_state_manager_exports_flush_result():
    """cortex.core.brain_state_manager must export FlushResult."""
    try:
        from cortex.core.brain_state_manager import FlushResult  # noqa: F401
        assert FlushResult is not None
    except ImportError as e:
        pytest.fail(f"Cannot import FlushResult from cortex.core.brain_state_manager: {e}")


def test_brain_state_manager_exports_reload_result():
    """cortex.core.brain_state_manager must export ReloadResult."""
    try:
        from cortex.core.brain_state_manager import ReloadResult  # noqa: F401
        assert ReloadResult is not None
    except ImportError as e:
        pytest.fail(f"Cannot import ReloadResult from cortex.core.brain_state_manager: {e}")


def test_brain_state_manager_exports_state_validation_error():
    """cortex.core.brain_state_manager must export StateValidationError."""
    try:
        from cortex.core.brain_state_manager import StateValidationError  # noqa: F401
        assert StateValidationError is not None
    except ImportError as e:
        pytest.fail(f"Cannot import StateValidationError from cortex.core.brain_state_manager: {e}")


def test_brain_state_manager_collection_no_error():
    """test_brain_state_manager.py must collect without ImportError (0 collection errors)."""
    import subprocess, sys
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/unit/brain/test_brain_state_manager.py",
         "--collect-only", "-q", "--no-header"],
        capture_output=True, text=True, cwd="."
    )
    assert "ImportError" not in result.stderr and "ImportError" not in result.stdout, (
        f"Collection error in test_brain_state_manager.py:\n{result.stderr}\n{result.stdout}"
    )


# ─────────────────────────────────────────────────────────────────
# GAP-115-02: Infrastructure quarantine
# ─────────────────────────────────────────────────────────────────

def test_quarantine_directory_exists():
    """cortex/infrastructure/_quarantine/ must exist after Phase 115-b."""
    qdir = pathlib.Path("cortex/infrastructure/_quarantine")
    assert qdir.is_dir(), "cortex/infrastructure/_quarantine/ directory missing"
