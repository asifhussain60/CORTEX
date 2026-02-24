"""COMPAT shim — cleaners.interface → cleaners.cleaner_interface (Phase 60 duplicate resolution).

Canonical implementation: cortex/intelligence/memory/tier1_learned/orchestrators/cleaners/cleaner_interface.py
90-day retention: created 2026-02-24, expires 2026-05-24.
"""
from .cleaner_interface import (  # noqa: F401
    CleanupResult,
    CleanerInterface,
)

__all__ = ["CleanupResult", "CleanerInterface"]
