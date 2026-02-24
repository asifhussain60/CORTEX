"""CORTEX Toolkit — Generic file-based intelligence operations.

Consolidated reusable components extracted from domain-specific implementations:

Subpackages:
    filesystem:      Hierarchical scanning, filename intelligence, organization detection
    batch:           Unified batch processing with adapters/filters/transformers
    transformation:  Content sanitization, safe renaming, collision detection
    metadata:        External enrichment, local extraction, confidence scoring
    workflow:        Generic pipeline orchestration with step definitions
    adapters:        Domain-specific extensions (media, code, documents)

Authority:
    Phase: toolkit-consolidation
    CORE Rules: CORE-011 (type hints), CORE-012 (docstrings), CORE-035 (canonical)

AC_START: AC-TOOLKIT-CONSOLIDATION-2026-02-24-001
"""

__version__ = "1.0.0"
__all__ = [
    "filesystem",
    "batch",
    "transformation",
    "metadata",
    "workflow",
    "adapters",
]
