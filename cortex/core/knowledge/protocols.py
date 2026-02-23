"""
Protocols module - Re-exports from protocol.py for compatibility.

This module exists for backwards compatibility with imports expecting
`cortex.core.knowledge.protocols` (plural).

The canonical definitions are in `cortex.core.knowledge.protocol` (singular).
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
