"""
Discovery Models — Data classes and enums for UnifiedDiscoveryOrchestrator.

Provides shared type definitions for educational and business language discovery:
- DiscoveryType: classification of discovery requests
- ResourceType: types of learnable resources
- LearningLevel: skill level progression
- Resource, LearningPath, Concept, Pattern: domain entities
- DiscoveryResult, CapabilityInfo: output structures

CORTEX COMPLIANCE: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings),
CORE-028 (snake_case), CORE-035 (single canonical implementation)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class DiscoveryType(str, Enum):
    """Classification of discovery request kinds."""

    EDUCATIONAL = "educational"
    BUSINESS_LANGUAGE = "business_language"
    PATTERN = "pattern"
    CAPABILITY = "capability"


class ResourceType(str, Enum):
    """Types of learnable resource artifacts."""

    ARTICLE = "article"
    VIDEO = "video"
    COURSE = "course"
    BOOK = "book"
    TUTORIAL = "tutorial"
    REFERENCE = "reference"
    EXAMPLE = "example"


class LearningLevel(str, Enum):
    """Skill-level progression tiers."""

    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


@dataclass
class Resource:
    """A single learnable resource artifact.

    Attributes:
        id: Unique resource identifier.
        title: Human-readable title.
        resource_type: Classification of resource kind.
        level: Skill level targeted by this resource.
        keywords: Searchable keyword tags.
        description: Short summary of content.
        url: Optional link to external source.
    """

    id: str
    title: str
    resource_type: ResourceType
    level: LearningLevel
    keywords: List[str] = field(default_factory=list)
    description: str = ""
    url: Optional[str] = None


@dataclass
class LearningPath:
    """Structured progression of resources toward a learning goal.

    Attributes:
        id: Unique path identifier.
        name: Human-readable path name.
        description: Goal description.
        resources: Ordered list of resource IDs.
        prerequisites: Prerequisite path IDs.
        level: Overall skill level of path.
    """

    id: str
    name: str
    description: str = ""
    resources: List[str] = field(default_factory=list)
    prerequisites: List[str] = field(default_factory=list)
    level: LearningLevel = LearningLevel.BEGINNER


@dataclass
class Concept:
    """A domain concept node in the concept graph.

    Attributes:
        id: Unique concept identifier.
        name: Concept name.
        domain: Domain this concept belongs to.
        definition: Plain-language definition.
        related_concepts: IDs of related concept nodes.
        synonyms: Alternative names for this concept.
    """

    id: str
    name: str
    domain: str = ""
    definition: str = ""
    related_concepts: List[str] = field(default_factory=list)
    synonyms: List[str] = field(default_factory=list)


@dataclass
class Pattern:
    """A design pattern with problem/solution mapping.

    Attributes:
        id: Unique pattern identifier.
        name: Pattern name.
        problem: The problem this pattern solves.
        solution: How the pattern solves it.
        examples: Concrete usage examples.
        tags: Searchable classification tags.
    """

    id: str
    name: str
    problem: str = ""
    solution: str = ""
    examples: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)


@dataclass
class DiscoveryResult:
    """Output of a discovery query.

    Attributes:
        query: Original search query.
        discovery_type: Kind of discovery performed.
        matches: Matched resources.
        learning_paths: Recommended learning paths.
        concepts: Related concepts surfaced.
        patterns: Matched patterns.
        total_matches: Total count of all matches across categories.
    """

    query: str
    discovery_type: DiscoveryType
    matches: List[Resource] = field(default_factory=list)
    learning_paths: List[LearningPath] = field(default_factory=list)
    concepts: List[Concept] = field(default_factory=list)
    patterns: List[Pattern] = field(default_factory=list)
    total_matches: int = 0

    def __post_init__(self) -> None:
        """Compute total_matches if not explicitly set."""
        if self.total_matches == 0:
            self.total_matches = (
                len(self.matches)
                + len(self.learning_paths)
                + len(self.concepts)
                + len(self.patterns)
            )


@dataclass
class CapabilityInfo:
    """Discovered capability with dependency metadata.

    Attributes:
        name: Capability name.
        description: What the capability provides.
        dependencies: Other capability names this depends on.
        providers: Module or class names that provide this capability.
        available: Whether the capability is currently resolvable.
    """

    name: str
    description: str = ""
    dependencies: List[str] = field(default_factory=list)
    providers: List[str] = field(default_factory=list)
    available: bool = True
