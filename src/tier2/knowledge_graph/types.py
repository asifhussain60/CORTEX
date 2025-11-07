"""
Knowledge Graph Shared Types

Contains common data types used across knowledge graph modules.
"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Dict, Any


class PatternType(Enum):
    """Pattern classification types."""
    WORKFLOW = "workflow"          # Recurring successful workflows
    PRINCIPLE = "principle"         # Core principles (immutable)
    ANTI_PATTERN = "anti_pattern"  # What to avoid
    SOLUTION = "solution"           # Proven solutions to problems
    CONTEXT = "context"            # Contextual knowledge


class RelationshipType(Enum):
    """Pattern relationship types."""
    EXTENDS = "extends"              # Pattern B extends Pattern A
    RELATES_TO = "relates_to"        # General relationship
    RELATED_TO = "related_to"        # Alias for relates_to
    CONTRADICTS = "contradicts"      # Patterns conflict
    SUPERSEDES = "supersedes"        # New pattern replaces old


@dataclass
class Pattern:
    """Pattern data structure."""
    pattern_id: str
    title: str
    content: str
    pattern_type: PatternType
    confidence: float
    created_at: str
    last_accessed: str
    access_count: int
    source: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    is_pinned: bool = False
    scope: str = "generic"  # Boundary enforcement ('generic' or 'application')
    namespaces: Optional[List[str]] = None  # Multi-app support (JSON array)
