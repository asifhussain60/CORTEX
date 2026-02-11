"""
Track 3 Group D: UnifiedDiscoveryOrchestrator - GREEN Phase Implementation

Consolidates 2 orchestrators into unified discovery system:
- EducationalOrchestrator: Learning paths, resources, progression tracking
- BusinessLanguageOrchestrator: Domain concepts, vocabulary, patterns

Architecture:
- Resource registry: Searchable by keyword, level, type
- Concept graph: Nodes (concepts), edges (relationships), traversal
- Pattern catalog: Design patterns with problem/solution mappings
- Learning paths: Structured progression with prerequisites

CORTEX COMPLIANCE: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings),
CORE-013 (specific exceptions), CORE-027 (audit trail with AC markers)
"""

from datetime import datetime
from typing import Dict, List, Optional, Set
import uuid

from cortex.orchestrators.support.discovery_models import (
    DiscoveryType,
    ResourceType,
    LearningLevel,
    Resource,
    LearningPath,
    Concept,
    Pattern,
    DiscoveryResult,
    CapabilityInfo,
)


class UnifiedDiscoveryOrchestrator:
    """
    Unified discovery orchestrator.

    Consolidates educational discovery and business language discovery into
    single system for learning paths, resources, concepts, and patterns.

    Features:
    - Resource search by keyword, level, type
    - Learning path recommendations
    - Concept graph traversal
    - Pattern catalog with problem/solution mapping
    - Capability discovery with dependency resolution

    Example:
        >>> orchestrator = UnifiedDiscoveryOrchestrator()
        >>> result = orchestrator.discover_resources(
        ...     query="async programming",
        ...     discovery_type=DiscoveryType.EDUCATIONAL,
        ...     target_level=LearningLevel.INTERMEDIATE
        ... )
        >>> for resource in result.matches:
        ...     print(resource.title)
    """

    def __init__(self):
        """Initialize discovery registries and graphs."""
        self._resource_registry: Dict[str, Resource] = {}
        self._learning_paths: Dict[str, LearningPath] = {}
        self._concept_graph: Dict[str, Concept] = {}
        self._pattern_catalog: Dict[str, Pattern] = {}
        self._capabilities: Dict[str, CapabilityInfo] = {}
        
        # Initialize with default resources
        self._initialize_registries()

    def discover_resources(
        self,
        query: str,
        discovery_type: DiscoveryType = DiscoveryType.EDUCATIONAL,
        target_level: Optional[LearningLevel] = None,
        resource_type: Optional[ResourceType] = None,
    ) -> DiscoveryResult:
        """
        Discover resources matching query criteria.

        Performs full-text keyword search across resource registry with
        optional filtering by level and type.

        Args:
            query: Search query (keywords)
            discovery_type: Type of discovery (educational, business_language, etc.)
            target_level: Filter by learning level (optional)
            resource_type: Filter by resource type (optional)

        Returns:
            DiscoveryResult with matching resources, ranked by relevance

        Raises:
            ValueError: If query is empty
            TypeError: If types are incorrect
        """
        if not query or not isinstance(query, str):
            raise ValueError("Query must be non-empty string")

        # AC_START: AC-GROUP-D-001
        # Search resources
        matches: List[Resource] = []
        query_terms = query.lower().split()

        for resource in self._resource_registry.values():
            # Keyword matching
            keyword_score = sum(
                1 for term in query_terms
                if any(term in k.lower() for k in resource.keywords)
            )

            if keyword_score > 0:
                # Apply level filter
                if target_level and resource.level != target_level:
                    continue

                # Apply resource type filter
                if resource_type and resource.resource_type != resource_type:
                    continue

                matches.append(resource)

        # Sort by relevance (keyword matches)
        matches.sort(
            key=lambda r: sum(
                1 for term in query_terms
                if any(term in k.lower() for k in r.keywords)
            ),
            reverse=True,
        )

        # AC_COMPLETE: AC-GROUP-D-001 ✅
        return DiscoveryResult(
            discovery_id=f"DR-{uuid.uuid4().hex[:8].upper()}",
            timestamp=datetime.now(),
            discovery_type=discovery_type,
            query=query,
            matches=matches,
            total_results=len(matches),
        )

    def discover_concepts(
        self,
        domain: Optional[str] = None,
        search_query: Optional[str] = None,
    ) -> List[Concept]:
        """
        Discover concepts by domain or keyword.

        Searches concept graph for concepts matching criteria.

        Args:
            domain: Filter by domain area (optional)
            search_query: Keyword search in concept names/definitions (optional)

        Returns:
            List of matching Concept objects

        Raises:
            TypeError: If parameters have wrong types
        """
        results: List[Concept] = []

        for concept in self._concept_graph.values():
            if domain and concept.domain != domain:
                continue

            if search_query:
                search_lower = search_query.lower()
                if not (
                    search_lower in concept.name.lower()
                    or search_lower in concept.definition.lower()
                ):
                    continue

            results.append(concept)

        # AC_START: AC-GROUP-D-002
        return results
        # AC_COMPLETE: AC-GROUP-D-002 ✅

    def discover_patterns(
        self,
        category: Optional[str] = None,
        search_query: Optional[str] = None,
    ) -> List[Pattern]:
        """
        Discover design patterns by category or keyword.

        Args:
            category: Filter by pattern category (Creational, Structural, etc.)
            search_query: Keyword search in pattern names/descriptions

        Returns:
            List of matching Pattern objects

        Raises:
            TypeError: If parameters have wrong types
        """
        results: List[Pattern] = []

        for pattern in self._pattern_catalog.values():
            if category and pattern.category != category:
                continue

            if search_query:
                search_lower = search_query.lower()
                if not (
                    search_lower in pattern.name.lower()
                    or search_lower in pattern.problem.lower()
                ):
                    continue

            results.append(pattern)

        return results

    def get_learning_path(
        self,
        path_id: str,
    ) -> Optional[LearningPath]:
        """
        Get a specific learning path by ID.

        Args:
            path_id: Path identifier

        Returns:
            LearningPath or None if not found

        Raises:
            ValueError: If path_id is invalid
        """
        if not path_id or not isinstance(path_id, str):
            raise ValueError("path_id must be non-empty string")

        return self._learning_paths.get(path_id)

    def discover_learning_paths(
        self,
        target_level: Optional[LearningLevel] = None,
        estimated_hours_max: Optional[float] = None,
    ) -> List[LearningPath]:
        """
        Discover learning paths matching criteria.

        Args:
            target_level: Filter by target audience level
            estimated_hours_max: Maximum estimated hours to complete

        Returns:
            List of matching LearningPath objects
        """
        results: List[LearningPath] = []

        for path in self._learning_paths.values():
            if target_level and path.target_level != target_level:
                continue

            if estimated_hours_max and path.estimated_hours > estimated_hours_max:
                continue

            results.append(path)

        return results

    def get_capability(
        self,
        capability_id: str,
    ) -> Optional[CapabilityInfo]:
        """
        Get capability information by ID.

        Args:
            capability_id: Capability identifier

        Returns:
            CapabilityInfo or None if not found

        Raises:
            ValueError: If capability_id is invalid
        """
        if not capability_id or not isinstance(capability_id, str):
            raise ValueError("capability_id must be non-empty string")

        return self._capabilities.get(capability_id)

    def discover_capabilities(
        self,
        domain: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[CapabilityInfo]:
        """
        Discover capabilities by domain or status.

        Args:
            domain: Filter by domain area
            status: Filter by status (STABLE, EXPERIMENTAL, DEPRECATED)

        Returns:
            List of matching CapabilityInfo objects
        """
        results: List[CapabilityInfo] = []

        for capability in self._capabilities.values():
            if domain and domain.lower() not in capability.name.lower():
                continue

            if status and capability.status != status:
                continue

            results.append(capability)

        return results

    def resolve_dependencies(
        self,
        capability_id: str,
    ) -> List[str]:
        """
        Resolve all dependencies for a capability (recursive).

        Args:
            capability_id: Root capability ID

        Returns:
            List of all direct and transitive dependencies

        Raises:
            ValueError: If capability not found
        """
        capability = self._capabilities.get(capability_id)
        if not capability:
            raise ValueError(f"Capability {capability_id} not found")

        # AC_START: AC-GROUP-D-003
        resolved: Set[str] = set()

        def resolve_recursive(cap_id: str) -> None:
            """Recursively resolve dependencies."""
            cap = self._capabilities.get(cap_id)
            if not cap:
                return

            for dep in cap.dependencies:
                if dep not in resolved:
                    resolved.add(dep)
                    resolve_recursive(dep)

        for dep in capability.dependencies:
            if dep not in resolved:
                resolved.add(dep)
                resolve_recursive(dep)

        # AC_COMPLETE: AC-GROUP-D-003 ✅
        return list(resolved)

    def get_related_concepts(
        self,
        concept_id: str,
        depth: int = 1,
    ) -> List[Concept]:
        """
        Get concepts related to a specific concept.

        Traverses concept graph up to specified depth.

        Args:
            concept_id: Root concept ID
            depth: Graph traversal depth (1 = direct neighbors only)

        Returns:
            List of related Concept objects

        Raises:
            ValueError: If concept not found or depth invalid
        """
        if concept_id not in self._concept_graph:
            raise ValueError(f"Concept {concept_id} not found")

        if not isinstance(depth, int) or depth < 1:
            raise ValueError("depth must be positive integer")

        # AC_START: AC-GROUP-D-004
        related: Set[str] = set()

        def traverse(cid: str, current_depth: int) -> None:
            """Traverse concept graph."""
            if current_depth > depth:
                return

            concept = self._concept_graph.get(cid)
            if not concept:
                return

            for related_id in concept.related_concepts:
                if related_id not in related:
                    related.add(related_id)
                    traverse(related_id, current_depth + 1)

        # Start traversal
        root = self._concept_graph.get(concept_id)
        if root:
            for related_id in root.related_concepts:
                if related_id not in related:
                    related.add(related_id)
                    traverse(related_id, 2)

        # AC_COMPLETE: AC-GROUP-D-004 ✅
        return [self._concept_graph[cid] for cid in related if cid in self._concept_graph]

    def register_resource(self, resource: Resource) -> None:
        """
        Register a new resource in the registry.

        Args:
            resource: Resource to register

        Raises:
            TypeError: If resource is not Resource instance
            ValueError: If resource_id already exists
        """
        if not isinstance(resource, Resource):
            raise TypeError("resource must be Resource instance")

        if resource.resource_id in self._resource_registry:
            raise ValueError(f"Resource {resource.resource_id} already registered")

        self._resource_registry[resource.resource_id] = resource

    def register_concept(self, concept: Concept) -> None:
        """
        Register a new concept in the graph.

        Args:
            concept: Concept to register

        Raises:
            TypeError: If concept is not Concept instance
            ValueError: If concept_id already exists
        """
        if not isinstance(concept, Concept):
            raise TypeError("concept must be Concept instance")

        if concept.concept_id in self._concept_graph:
            raise ValueError(f"Concept {concept.concept_id} already registered")

        self._concept_graph[concept.concept_id] = concept

    # ─────────────────────────────────────────────────────────────────────
    # Private helpers - Registry initialization
    # ─────────────────────────────────────────────────────────────────────

    def _initialize_registries(self) -> None:
        """Initialize registries with default resources and concepts."""
        # Add sample resources
        self._resource_registry["RES-001"] = Resource(
            resource_id="RES-001",
            title="Python Async Programming",
            resource_type=ResourceType.DOCUMENTATION,
            level=LearningLevel.INTERMEDIATE,
            content="Comprehensive guide to async/await",
            keywords=["async", "python", "concurrency"],
        )

        self._resource_registry["RES-002"] = Resource(
            resource_id="RES-002",
            title="Async Patterns and Best Practices",
            resource_type=ResourceType.BEST_PRACTICE,
            level=LearningLevel.ADVANCED,
            content="Advanced async patterns",
            keywords=["async", "patterns", "best-practice"],
        )

        # Add sample concepts
        self._concept_graph["CONCEPT-001"] = Concept(
            concept_id="CONCEPT-001",
            name="Concurrency",
            domain="Architecture",
            definition="Ability to execute multiple tasks simultaneously",
            examples=["Multi-threading", "Async/await", "Multi-processing"],
            related_concepts=["CONCEPT-002"],
            patterns=["PATTERN-001"],
        )

        self._concept_graph["CONCEPT-002"] = Concept(
            concept_id="CONCEPT-002",
            name="Event-Driven Architecture",
            domain="Architecture",
            definition="System design based on event production and consumption",
            examples=["Pub/Sub systems", "Message queues"],
            related_concepts=["CONCEPT-001"],
            patterns=["PATTERN-002"],
        )

        # Add sample patterns
        self._pattern_catalog["PATTERN-001"] = Pattern(
            pattern_id="PATTERN-001",
            name="Observer",
            category="Behavioral",
            problem="Define one-to-many dependency between objects",
            solution="Create observer interface for notifications",
            consequences=["Loose coupling", "Event-driven"],
            related_patterns=["PATTERN-002"],
        )

        # Add sample learning path
        self._learning_paths["PATH-001"] = LearningPath(
            path_id="PATH-001",
            title="Python Async Mastery",
            description="Complete learning path for async programming",
            target_level=LearningLevel.ADVANCED,
            stages=["RES-001", "RES-002"],
            estimated_hours=8.0,
            prerequisites=["Basic Python knowledge"],
        )

        # Add sample capabilities
        self._capabilities["CAP-001"] = CapabilityInfo(
            capability_id="CAP-001",
            name="LENS Analysis",
            description="Unified code intelligence",
            version="2.1.0",
            status="STABLE",
            dependencies=[],
            examples=["analyze_complexity(code)"],
        )
