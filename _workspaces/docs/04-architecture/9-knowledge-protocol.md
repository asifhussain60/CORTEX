# Knowledge Protocol

> Auto-generated from cortex-impl-map.yaml on 2026-01-21

**Last Updated:** 2026-01-21  
**Audience:** Architects, Developers  
**Prerequisites:** [System Overview](1-system-overview.md), [Domain Brain](4-domain-brain.md)

## Overview

The Knowledge Protocol defines how CORTEX ingests, stores, queries, and maintains domain knowledge. It implements the Business Knowledge Ingestion Orchestrator (BKIO) pattern for structured knowledge management with conflict detection and resolution.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Knowledge Protocol Architecture                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   INTELLIGENCE SOURCES              BKIO PIPELINE              STORAGE       │
│   ┌─────────────────┐           ┌─────────────────┐      ┌─────────────────┐│
│   │ AST Adapter     │──────────▶│ Document Parser │─────▶│ Tier 3 KB      ││
│   │ Git Adapter     │──────────▶│ Entity Extractor│─────▶│ Knowledge Graph││
│   │ Comments Adapter│──────────▶│ Conflict Detect │─────▶│ governance.db  ││
│   │ Relations Adapter│─────────▶│ Conflict Resolve│      └─────────────────┘│
│   └─────────────────┘           └─────────────────┘                         │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## BKIO Pipeline

The Business Knowledge Ingestion Orchestrator processes knowledge through four stages:

### Stage 1: Document Parsing

Converts raw input into structured documents:

| Source Type | Parser | Output |
|-------------|--------|--------|
| Python Files | AST Parser | Function/Class entities |
| Markdown | MD Parser | Section/Link entities |
| YAML | YAML Parser | Config/Rule entities |
| Git History | Git Parser | Commit/Change entities |

### Stage 2: Entity Extraction

Extracts typed entities from parsed documents:

```python
@dataclass
class KnowledgeEntity:
    """A unit of domain knowledge."""
    id: str
    type: EntityType  # FUNCTION, CLASS, RULE, CONCEPT
    name: str
    source: str       # File path or origin
    attributes: Dict[str, Any]
    relationships: List[Relationship]
    version: int
    created_at: datetime
    updated_at: datetime
```

### Stage 3: Conflict Detection

Identifies conflicts before storage:

| Conflict Type | Detection Method | Resolution |
|---------------|------------------|------------|
| **Duplicate** | Hash + name match | Merge or reject |
| **Version** | Version mismatch | Latest wins |
| **Relationship** | Orphan references | Cascade delete |
| **Constraint** | Rule violation | Block ingestion |

### Stage 4: Conflict Resolution

Resolves detected conflicts using strategies:

```python
class ConflictResolutionStrategy(Enum):
    LATEST_WINS = "latest_wins"      # Newer version replaces
    MERGE = "merge"                   # Combine attributes
    MANUAL = "manual"                 # Require user decision
    REJECT = "reject"                 # Block conflicting entry
```

## Knowledge Graph (CORTEX LENS)

The Knowledge Graph stores entities and relationships:

### Graph Nodes

```python
@dataclass
class GraphNode:
    """Entity in the knowledge graph."""
    id: str
    type: str
    properties: Dict[str, Any]
    created_at: datetime
```

### Graph Edges

```python
@dataclass
class GraphEdge:
    """Relationship between entities."""
    source_id: str
    target_id: str
    relationship: str  # DEPENDS_ON, IMPLEMENTS, CALLS, etc.
    weight: float
    properties: Dict[str, Any]
```

### Graph Operations (50+)

| Category | Operations |
|----------|-----------|
| **Query** | get_node, find_by_type, search_by_name |
| **Traverse** | get_neighbors, find_path, get_subgraph |
| **Mutate** | add_node, update_node, delete_node |
| **Analyze** | get_centrality, find_clusters, detect_cycles |

## API Operations

The Domain Brain API exposes five core operations:

### Ingest

```python
async def ingest(
    source: str,
    source_type: SourceType,
    options: IngestOptions = None
) -> IngestResult:
    """
    Ingest knowledge from a source.
    
    Args:
        source: Path or content to ingest
        source_type: AST, GIT, MARKDOWN, YAML
        options: Conflict resolution, validation
    
    Returns:
        IngestResult with entities created/updated
    """
```

### Query

```python
async def query(
    query: KnowledgeQuery,
    context: QueryContext = None
) -> QueryResult:
    """
    Query the knowledge base.
    
    Args:
        query: Search criteria (type, name, relationships)
        context: Scope (tier, domain, time range)
    
    Returns:
        QueryResult with matching entities
    """
```

### Update

```python
async def update(
    entity_id: str,
    changes: Dict[str, Any],
    version: int
) -> UpdateResult:
    """
    Update an existing entity.
    
    Args:
        entity_id: Target entity
        changes: Attribute changes
        version: Expected version (optimistic lock)
    
    Returns:
        UpdateResult with new version
    """
```

### Delete

```python
async def delete(
    entity_id: str,
    cascade: bool = False
) -> DeleteResult:
    """
    Delete an entity.
    
    Args:
        entity_id: Target entity
        cascade: Delete related entities
    
    Returns:
        DeleteResult with deleted count
    """
```

### Validate

```python
async def validate(
    entity_id: str = None
) -> ValidationResult:
    """
    Validate knowledge base consistency.
    
    Args:
        entity_id: Specific entity or None for full validation
    
    Returns:
        ValidationResult with issues found
    """
```

## Tier 3 Knowledge Base

Tier 3 stores business rules and domain facts:

| Content Type | Description | Example |
|--------------|-------------|---------|
| **Business Rules** | Domain logic | "Orders > $1000 require approval" |
| **Domain Facts** | Static knowledge | "Product categories: A, B, C" |
| **Constraints** | Validation rules | "Email must be unique" |
| **Relationships** | Entity connections | "User owns Orders" |

## Consistency Validation

The Consistency Validator ensures data integrity:

| Check | Description | Frequency |
|-------|-------------|-----------|
| **Duplicate** | No duplicate entities | On ingest |
| **Orphan** | No dangling references | Hourly |
| **Cycle** | No circular dependencies | On update |
| **Version** | No stale updates | On update |

## Related

- [Knowledge Graph Diagram](../_diagrams/knowledge-graph.mmd)
- [Domain Brain](4-domain-brain.md)
- [Governance Tiers Diagram](../_diagrams/governance-tiers.mmd)
