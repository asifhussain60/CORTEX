# © 2025-2026 Asif Hussain. All rights reserved.
# PHASE-21: Intelligent Knowledge Protocol
"""
Core knowledge abstraction for unified knowledge provider interface.

This package provides the KnowledgeProvider protocol (Tier0) that defines
the contract for all knowledge repository implementations across CORTEX.

Components:
  - protocol.py: KnowledgeProvider protocol definition (Tier0)

Usage:
    from cortex.core.knowledge import KnowledgeProvider
    
    def evaluate_knowledge(provider: KnowledgeProvider) -> None:
        if provider.is_loaded:
            domains = provider.domains
            knowledge = provider.query(keywords=["microservices"])

PHASE-21 Acceptance Criteria:
  - AC-IKP-001: Unified Knowledge Provider Protocol
  - AC-IKP-002: Intelligent Knowledge Router
  - AC-IKP-003: Change Detection Service
  - AC-IKP-004: Bulk Ingestion Pipeline

CORE Governance:
  - CORE-004: Tier organization (Protocol in Tier0)
  - CORE-011: Type hints (100% coverage)
  - CORE-012: Docstrings (Google style)
"""

from cortex.core.knowledge.protocol import (
    KnowledgeProvider,
    KnowledgeQuery,
    KnowledgeQueryResult,
)

__all__ = [
    "KnowledgeProvider",
    "KnowledgeQuery",
    "KnowledgeQueryResult",
]

__version__ = "1.0.0"
__doc_module__ = __doc__
