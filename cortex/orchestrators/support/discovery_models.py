"""
Shared data models for discovery orchestrator.

Consolidates data structures for:
- Educational discovery (learning paths, concepts, resources)
- Business language discovery (domain-specific vocabulary, patterns)

CORTEX COMPLIANCE: CORE-011 (type hints), CORE-012 (docstrings)
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional
from datetime import datetime


class DiscoveryType(Enum):
    """Types of discovery operations."""

    EDUCATIONAL = "educational"
    BUSINESS_LANGUAGE = "business_language"
    PATTERN = "pattern"
    CAPABILITY = "capability"


class ResourceType(Enum):
    """Types of educational resources."""

    DOCUMENTATION = "documentation"
    EXAMPLE = "example"
    BEST_PRACTICE = "best_practice"
    ANTI_PATTERN = "anti_pattern"
    REFERENCE = "reference"


class LearningLevel(Enum):
    """Complexity level for educational content."""

    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


@dataclass
class Resource:
    """Educational resource for discovery."""

    resource_id: str
    """Unique resource identifier."""

    title: str
    """Resource title."""

    resource_type: ResourceType
    """Type of resource (documentation, example, etc.)."""

    level: LearningLevel
    """Complexity level."""

    content: str
    """Resource content or description."""

    keywords: List[str] = field(default_factory=list)
    """Search keywords for discovery."""

    url: Optional[str] = None
    """Reference URL if applicable."""

    related_resources: List[str] = field(default_factory=list)
    """IDs of related resources."""


@dataclass
class LearningPath:
    """Structured learning path for discovering concepts."""

    path_id: str
    """Unique path identifier."""

    title: str
    """Path title."""

    description: str
    """Path description."""

    target_level: LearningLevel
    """Target audience level."""

    stages: List[str]
    """Resource IDs in sequence order."""

    estimated_hours: float
    """Estimated time to complete."""

    prerequisites: List[str] = field(default_factory=list)
    """Required knowledge before starting."""


@dataclass
class Concept:
    """Business domain concept for discovery."""

    concept_id: str
    """Unique concept identifier."""

    name: str
    """Concept name."""

    domain: str
    """Domain area."""

    definition: str
    """Formal definition."""

    examples: List[str] = field(default_factory=list)
    """Real-world examples."""

    related_concepts: List[str] = field(default_factory=list)
    """Connected concepts (conceptual graph)."""

    patterns: List[str] = field(default_factory=list)
    """Associated design patterns."""


@dataclass
class Pattern:
    """Design or implementation pattern for discovery."""

    pattern_id: str
    """Unique pattern identifier."""

    name: str
    """Pattern name."""

    category: str
    """Pattern category (creational, structural, behavioral, etc.)."""

    problem: str
    """Problem this pattern solves."""

    solution: str
    """Solution approach."""

    consequences: List[str]
    """Pros and cons of applying pattern."""

    code_example: Optional[str] = None
    """Code example of pattern."""

    related_patterns: List[str] = field(default_factory=list)
    """Other related patterns."""


@dataclass
class DiscoveryResult:
    """Result from a discovery operation."""

    discovery_id: str
    """Unique discovery operation ID."""

    timestamp: datetime
    """When discovery was performed."""

    discovery_type: DiscoveryType
    """Type of discovery performed."""

    query: str
    """Original search query."""

    matches: List[Resource]
    """Matching resources found."""

    concepts: List[Concept] = field(default_factory=list)
    """Relevant concepts discovered."""

    patterns: List[Pattern] = field(default_factory=list)
    """Relevant patterns discovered."""

    total_results: int = 0
    """Total matches found."""


@dataclass
class CapabilityInfo:
    """Information about a system capability."""

    capability_id: str
    """Unique capability identifier."""

    name: str
    """Capability name."""

    description: str
    """What the capability does."""

    version: str
    """Capability version."""

    status: str
    """Status: STABLE, EXPERIMENTAL, DEPRECATED."""

    dependencies: List[str] = field(default_factory=list)
    """Required capabilities or modules."""

    documentation_url: Optional[str] = None
    """URL to full documentation."""

    examples: List[str] = field(default_factory=list)
    """Usage examples."""
