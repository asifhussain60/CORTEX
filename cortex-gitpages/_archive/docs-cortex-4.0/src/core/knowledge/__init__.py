"""
Knowledge services package (PHASE-21).

Provides unified access to knowledge backends with intelligent routing,
change detection, bulk ingestion, versioning, search, and analytics.

Modules:
  - protocols: KnowledgeProvider protocol definition
  - router: IntelligentKnowledgeRouter for smart backend selection
  - change_detection: Change detection service
  - unified_service: Unified facade for all knowledge services
  - query_optimizer: Query optimization with caching
  - update_propagation: Change propagation across backends
  - versioning: Version tracking and rollback
  - search_engine: Full-text and semantic search
  - recommendations: Context-aware recommendations
  - analytics: Usage metrics and reporting
  - ingestion: Bulk ingestion pipeline

Governance:
  - CORE-008: TDD methodology (tests first)
  - CORE-011: Type hints mandatory
  - CORE-012: Google-style docstrings
  - CORE-013: Specific exception handling
  - CORE-027: Audit trail entries
  - CORE-028: Kebab-case filenames, <25 characters
"""

from .protocols import KnowledgeProvider

__all__ = [
    'KnowledgeProvider',
]

__version__ = '1.0.0'
__phase__ = 'PHASE-21'
