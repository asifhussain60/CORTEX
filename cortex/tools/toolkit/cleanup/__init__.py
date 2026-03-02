"""
CORTEX Toolkit - Cleanup Module

Consolidates cleanup and vacuum automation scripts.

**Consolidated Scripts:**
- .cortex-runtime/run_vacuum.py
- scripts/vacuum-runner.py

**Authority:** Phase 90 S-90-05 → Phase-51 (VacuumOrchestrator canonical)
"""

# Phase-51: VacuumAutomation replaced by VacuumOrchestrator
try:
    from cortex.orchestrators.health.vacuum_orchestrator import VacuumOrchestrator as VacuumAutomation
except ImportError:
    VacuumAutomation = None  # type: ignore[assignment,misc]

# Import consolidated cleanup from Phase 90
try:
    from pathlib import Path

    # Import from sibling cleanup.py file
    cleanup_file = Path(__file__).parent.parent / "cleanup.py"
    if cleanup_file.exists():
        import importlib.util
        spec = importlib.util.spec_from_file_location("toolkit_cleanup", cleanup_file)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            CleanupManager = module.CleanupManager
            CleanupResult = module.CleanupResult
            CleanupOperation = module.CleanupOperation
    else:
        CleanupManager = None
        CleanupResult = None
        CleanupOperation = None
except Exception:
    CleanupManager = None
    CleanupResult = None
    CleanupOperation = None

__all__ = [
    "VacuumAutomation",
    "CleanupManager",
    "CleanupResult",
    "CleanupOperation",
]
