"""
Migration Orchestrators - Code transformation and migration tools.

Provides orchestrators for:
- Selenium to Playwright migration
- Framework upgrades
- Code pattern transformations

Author: Asif Hussain
"""

from .selenium_playwright_orchestrator import (
    SeleniumPlaywrightOrchestrator,
    SeleniumPatternMatcher,
    PlaywrightCodeGenerator,
    ConversionEngine,
    ConversionReport,
)

__all__ = [
    "SeleniumPlaywrightOrchestrator",
    "SeleniumPatternMatcher",
    "PlaywrightCodeGenerator",
    "ConversionEngine",
    "ConversionReport",
]
