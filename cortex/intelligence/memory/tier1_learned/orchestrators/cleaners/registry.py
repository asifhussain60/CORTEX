"""COMPAT shim — cleaners.registry → cleaners.cleaner_registry (Phase 60 duplicate resolution).

Canonical implementation: cortex/intelligence/memory/tier1_learned/orchestrators/cleaners/cleaner_registry.py
90-day retention: created 2026-02-24, expires 2026-05-24.
"""
from .cleaner_registry import (  # noqa: F401
    CleanerRegistry,
)


class CleanerRegistrationError(Exception):
    """Raised when a cleaner cannot be registered due to validation failures.

    This exception is emitted by CleanerRegistry.register() when:
    - The supplied class is not a valid CleanerInterface subclass.
    - The domain key is already registered (duplicate prevention, CORE-035).
    - Required metadata fields are missing or malformed.
    """


__all__ = ["CleanerRegistry", "CleanerRegistrationError"]
