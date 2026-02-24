"""COMPAT shim — cleaners.base → cleaners.cleaner_base (Phase 60 duplicate resolution).

Canonical implementation: cortex/intelligence/memory/tier1_learned/orchestrators/cleaners/cleaner_base.py
90-day retention: created 2026-02-24, expires 2026-05-24.
"""
from .cleaner_base import (  # noqa: F401
    Analysis,
    Report,
    RollbackResult,
    CleanerInterface,
)

__all__ = ["Analysis", "Report", "RollbackResult", "CleanerInterface"]
