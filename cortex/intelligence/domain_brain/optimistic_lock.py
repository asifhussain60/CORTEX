"""COMPAT shim — domain_brain.optimistic_lock → domain_brain.domain_brain_optimistic_lock (Phase 60).

Canonical: cortex/intelligence/domain_brain/domain_brain_optimistic_lock.py
90-day retention: created 2026-02-24, expires 2026-05-24.
"""
from .domain_brain_optimistic_lock import *  # noqa: F401, F403
from .domain_brain_optimistic_lock import OptimisticLockManager  # noqa: F401
