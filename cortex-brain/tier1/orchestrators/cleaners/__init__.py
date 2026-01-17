"""Cleaner Plugins Package - SOLID-Compliant Plugin Architecture

This package provides the abstract interface and registry for VacuumOrchestrator
cleaner plugins. Each cleaner handles a specific domain of repository cleanup.

Module Structure:
- interface.py: CleanerInterface, Analysis, Report, RollbackResult
- registry.py: CleanerRegistry (plugin manager)
- md_organizer/: MD document organization cleaner (VAC-001-02, VAC-001-03)
- python_cache/: Python cache cleaner (future VAC-002)
- backups/: Backup file cleaner (future VAC-003)

SOLID Design:
- Single Responsibility: Each cleaner handles one domain
- Open/Closed: New cleaners without modifying orchestrator
- Liskov Substitution: All cleaners swap via CleanerInterface
- Interface Segregation: Minimal required methods
- Dependency Inversion: Orchestrator depends on abstraction

Usage:
    ```python
    from cortex_brain.tier1.orchestrators.cleaners import (
        CleanerInterface,
        Analysis,
        Report,
        RollbackResult,
        CleanerRegistry,
    )

    registry = CleanerRegistry()
    registry.register_cleaner(MDOrganizerCleaner)
    cleaner = registry.get_cleaner('md_organizer')
    analysis = cleaner.analyze()
    ```

Author: CORTEX Builder
Phase: PHASE-VAC-001-01
"""

from .interface import (
    CleanerInterface,
    Analysis,
    Report,
    RollbackResult,
)
from .registry import (
    CleanerRegistry,
    CleanerRegistrationError,
    CleanerNotFoundError,
)

__all__ = [
    'CleanerInterface',
    'Analysis',
    'Report',
    'RollbackResult',
    'CleanerRegistry',
    'CleanerRegistrationError',
    'CleanerNotFoundError',
]
