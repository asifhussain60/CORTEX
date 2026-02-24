"""COMPAT shim — cleaners.registry → cleaners.cleaner_registry (Phase 60 duplicate resolution).

Canonical implementation: cortex/intelligence/memory/tier1_learned/orchestrators/cleaners/cleaner_registry.py
90-day retention: created 2026-02-24, expires 2026-05-24.
"""
from .cleaner_registry import (  # noqa: F401
    CleanerRegistry,
)

__all__ = ["CleanerRegistry"]
