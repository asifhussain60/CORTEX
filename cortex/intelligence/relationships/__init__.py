"""
Relationship Intelligence Engine.

Detects and traverses code relationships:
- API endpoint mappings
- Database model relationships
- Configuration references
- Cross-file dependencies
- Call graph analysis

Authority: Phase 56 - LENS/Intelligence Hybrid Architecture
"""

from cortex.intelligence.relationships.traversal import RelationshipTraversalEngine

__all__ = ["RelationshipTraversalEngine"]
