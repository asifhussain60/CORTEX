"""Business Knowledge Repository — compat shim (Phase 107 Sub-Phase B).

Canonical definition now lives in:
  cortex/intelligence/knowledge/business_knowledge_repository.py

This file re-exports the canonical class + retains the BusinessKnowledgeEntry
dataclass (which has no equivalent in knowledge/ and is used by domain_brain callers).

Authority: GAP-107-04 (CORE-035 — single canonical implementation)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict

# ruff: noqa: F401 — intentional re-export for backward compatibility
from cortex.intelligence.knowledge.business_knowledge_repository import (  # noqa: F401
    BusinessKnowledgeRepository,
)


@dataclass
class BusinessKnowledgeEntry:
    """A single business knowledge entry stored in the repository.

    Retained in domain_brain because it has no equivalent in knowledge/.
    Used by DomainBrainAPI and master_orchestrator_init callers.
    """

    id: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)


_COMPAT_MARKER = (
    "Phase 107 — domain_brain/business_knowledge_repository.py is now a compat shim. "
    "Use cortex.intelligence.knowledge.business_knowledge_repository."
)
