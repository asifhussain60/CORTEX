"""
Migration Orchestrators - Code transformation and migration tools.

Provides orchestrators for:
- Python 2→3 migration planning
- Angular→React framework migration
- Generic technology stack migrations
- Selenium to Playwright migration

Author: Asif Hussain
"""

from .migration_orchestrator import (
    MigrationOrchestrator,
    MigrationPlan,
    MigrationStep,
    BreakingChange,
    RollbackStrategy,
    CompatibilityTest,
    FeatureParityCheck,
    TargetType,
    SeverityLevel,
    MigrationStatus,
)
from .selenium_playwright_orchestrator import (
    SeleniumPlaywrightOrchestrator,
    SeleniumPatternMatcher,
    PlaywrightCodeGenerator,
    ConversionEngine,
    ConversionReport,
)

__all__ = [
    "MigrationOrchestrator",
    "MigrationPlan",
    "MigrationStep",
    "BreakingChange",
    "RollbackStrategy",
    "CompatibilityTest",
    "FeatureParityCheck",
    "TargetType",
    "SeverityLevel",
    "MigrationStatus",
    "SeleniumPlaywrightOrchestrator",
    "SeleniumPatternMatcher",
    "PlaywrightCodeGenerator",
    "ConversionEngine",
    "ConversionReport",
]
