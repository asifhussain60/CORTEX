"""Vacuum orchestration module for repository maintenance.

This module provides the VacuumOrchestrator coordinator that manages
cleaner plugin lifecycle and coordinates cleanup operations.

Public API:
    VacuumOrchestrator: Main coordinator for vacuum operations
    OrchestratorState: Orchestrator execution state tracking
    OrchestrationReport: Consolidated report from all cleaners
    VacuumStats: Statistics tracking (backward compatibility)
    VacuumStrategy: Vacuum strategy enum (backward compatibility)

Usage:
    ```python
    from tier1.orchestrators.vacuum import VacuumOrchestrator
    from tier1.orchestrators.cleaners import (
        RootDatabaseCleaner,
        RootArtifactsCleaner,
        MarkdownSprawlCleaner,
    )
    
    # Initialize orchestrator
    orchestrator = VacuumOrchestrator(config={
        "repository_root": "/path/to/repo",
        "dry_run": False,
    })
    
    # Register cleaners
    orchestrator.register_cleaner(RootDatabaseCleaner)
    orchestrator.register_cleaner(RootArtifactsCleaner)
    orchestrator.register_cleaner(MarkdownSprawlCleaner)
    
    # Execute vacuum cycle
    report = orchestrator.run()
    
    # Check results
    if report.status == "SUCCESS":
        print(f"Cleaned {report.total_actions} items")
    ```

Governance:
- CORE-011: Type hints 100%
- CORE-012: Google-style docstrings
- CORE-035: Single canonical implementation
- AC-VACUUM-REFACTOR-001: Plugin orchestration

Author: CORTEX Architect
Phase: PHASE-VAC-001-05
"""

from .orchestrator import (
    VacuumOrchestrator,
    OrchestratorState,
    OrchestrationReport,
    VacuumStats,
    VacuumStrategy,
)

__all__ = [
    "VacuumOrchestrator",
    "OrchestratorState",
    "OrchestrationReport",
    "VacuumStats",
    "VacuumStrategy",
]
