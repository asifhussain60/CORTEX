"""shared_brain_store.py — Backward-compatibility shim (Phase 102-C).

The canonical file is now:
  cortex/infrastructure/shared_context_store.py

This shim will be removed after 1 consolidation session.
"""
from cortex.infrastructure.shared_context_store import *  # noqa: F401, F403

