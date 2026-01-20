# Domain Brain

**Last Updated:** 2026-01-20  
**Audience:** Architects, Developers  
**Prerequisites:** [System Overview](1-system-overview.md)

## Overview

The Domain Brain is CORTEX's centralized knowledge management system that ingests, stores, and retrieves business knowledge from multiple intelligence sources. It provides orchestrators with context-aware domain knowledge for informed decision-making, with built-in conflict detection and resolution.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           INTELLIGENCE SOURCES                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │AST Adapter  │  │Git Adapter  │  │Comments     │  │Relationships        │ │
│  │(Code Parse) │  │(History)    │  │Adapter      │  │Adapter              │ │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────────┬──────────┘ │
│         │                │                │                    │            │
└─────────┼────────────────┼────────────────┼────────────────────┼────────────┘
          │                │                │                    │
          └────────────────┴────────────────┴────────────────────┘
                                    │
                    ┌───────────────▼───────────────┐
                    │       BKIO Orchestrator       │
                    │  (Business Knowledge Ingestion)│
                    │  ├─ Document Parsing          │
                    │  ├─ Entity Extraction         │
                    │  ├─ Conflict Detection        │
                    │  └─ Conflict Resolution       │
                    └───────────────┬───────────────┘
                                    │
                    ┌───────────────▼───────────────┐
                    │       Domain Brain API        │
                    │  ├─ Ingest (add knowledge)    │
                    │  ├─ Query (retrieve knowledge)│
                    │  ├─ Update (modify entities)  │
                    │  ├─ Delete (remove entities)  │
                    │  └─ Validate (consistency)    │
                    └───────────────┬───────────────┘
                                    │
          ┌─────────────────────────┼─────────────────────────┐
          │                         │                         │
          ▼                         ▼                         ▼
┌─────────────────┐   ┌─────────────────────┐   ┌─────────────────────┐
│  TIER 3         │   │  Knowledge Graph    │   │  Consistency        │
│  Knowledge Base │   │  (CORTEX LENS)      │   │  Validator          │
│                 │   │                     │   │                     │
│ • Business Rules│   │ • GraphNode (entity)│   │ • Conflict detection│
│ • Domain Facts  │   │ • GraphEdge (rel)   │   │ • Duplicate check   │
│ • Constraints   │   │ • 50+ query ops     │   │ • Orphan detection  │
│ • Relationships │   │ • Path finding      │   │ • Version tracking  │
└─────────────────┘   └─────────────────────┘   └─────────────────────┘
```

## Intelligence Adapters

The Domain Brain integrates with four intelligence sources:

### AST Adapter (Code Structure)

Extracts structured information from source code:

| Entity Type | Extracted Information |
|-------------|----------------------|
| **Functions** | Name, parameters, return type, docstring |
| **Classes** | Name, bases, methods, attributes |
| **Imports** | Module, aliases, dependencies |
| **Variables** | Name, type hints, assignments |

**Implementation:** `src/core/knowledge/ast_adapter.py`

### Git Adapter (History)

Extracts change patterns from version control:

| Entity Type | Extracted Information |
|-------------|----------------------|
| **Commits** | Author, message, files changed |
| **Changes** | Additions, deletions, modifications |
| **Patterns** | Frequently changed files, hotspots |
| **Authors** | Expertise areas, contribution patterns |

**Implementation:** `src/core/knowledge/git_adapter.py`

### Comments Adapter (Intent)

Extracts semantic information from code comments:

| Comment Type | Extracted Information |
|--------------|----------------------|
| **Docstrings** | Function/class documentation |
| **TODOs** | Pending work items |
| **FIXMEs** | Known issues |
| **Notes** | Developer intent, context |

**Implementation:** `src/core/knowledge/comments_adapter.py`

### Relationships Adapter (Dependencies)

Extracts code relationships and dependencies:

| Relationship Type | Description |
|-------------------|-------------|
| **calls** | Function A calls function B |
| **imports** | Module A imports module B |
| **depends_on** | Component A depends on component B |
| **inherits** | Class A inherits from class B |
| **uses** | Entity A uses entity B |

**Implementation:** `src/core/knowledge/relationships_adapter.py`

## BKIO (Business Knowledge Ingestion Orchestrator)

The BKIO orchestrator handles document ingestion and conflict resolution:

### Document Parsing

Supported formats:

| Format | Parser | Use Case |
|--------|--------|----------|
| **YAML** | PyYAML | Configuration, rules |
| **JSON** | json module | API specs, data |
| **Markdown** | markdown-it | Documentation |
| **CSV** | csv module | Tabular data |

### Entity Extraction

```python
# Example entity extraction
entities = bkio.extract_entities(document)
# Returns: [Entity(type='rule', name='CORE-008', value='TDD mandatory'), ...]
```

### Conflict Detection

The BKIO detects conflicts across knowledge sources:

| Conflict Type | Detection Method | Example |
|---------------|------------------|---------|
| **Duplicate** | Hash-based deduplication | Same rule defined twice |
| **Contradiction** | Semantic analysis | Rule A says X, Rule B says NOT X |
| **Inconsistency** | Type checking | Number expected, string provided |
| **Orphan** | Reference validation | Reference to non-existent entity |

### Conflict Resolution

Resolution follows a hierarchical priority:

```
Resolution Priority:
1. BKIO (business documents) - Highest
2. Relationships Adapter
3. AST Adapter
4. Git Adapter
5. LENS Synthesis - Lowest (for unresolved)
```

**Implementation:** PHASE-17-DOMAIN-BRAIN (353 tests passing)

## Knowledge Graph (CORTEX LENS)

The Knowledge Graph provides structured knowledge storage and querying:

### Graph Components

```python
@dataclass
class GraphNode:
    """Entity representation in knowledge graph."""
    id: str
    type: EntityType  # FUNCTION, CLASS, API, MODEL, PATTERN, CONFIG, SCHEMA
    name: str
    metadata: Dict[str, Any]
    
@dataclass
class GraphEdge:
    """Relationship between entities."""
    source_id: str
    target_id: str
    relationship: RelationType  # calls, imports, depends_on, inherits, etc.
    metadata: Dict[str, Any]
```

### Relationship Types

| Type | Description | Example |
|------|-------------|---------|
| **calls** | Function invocation | `main() → helper()` |
| **imports** | Module import | `orchestrator → domain_brain` |
| **depends_on** | Dependency relationship | `API → Database` |
| **persists** | Data persistence | `Service → Repository` |
| **queries** | Data retrieval | `Handler → Cache` |
| **triggers** | Event triggering | `Event → Handler` |
| **validates** | Validation relationship | `Validator → Schema` |
| **transforms** | Data transformation | `Parser → Formatter` |
| **configures** | Configuration | `Config → Service` |
| **extends** | Extension/inheritance | `ChildClass → ParentClass` |
| **implements** | Interface implementation | `Adapter → Interface` |
| **uses** | General usage | `Component → Utility` |
| **contains** | Containment | `Module → Function` |
| **references** | Reference | `Doc → Entity` |
| **tests** | Test relationship | `TestSuite → Function` |

### Query Operations

The Knowledge Graph supports 50+ query operations:

```python
# Find all functions in a module
functions = graph.find_by_type(EntityType.FUNCTION, module="orchestrator")

# Traverse dependencies
dependencies = graph.traverse(start_node, max_depth=3)

# Check reachability
is_reachable = graph.is_reachable(node_a, node_b)

# Impact analysis
affected = graph.impact_analysis(changed_node)

# Path finding
path = graph.shortest_path(source, target)
```

**Implementation:** PHASE-07-INTENT-ROUTER (IR-004-01, 36 tests)

## Domain Brain API

### Core Operations

| Method | Description | Parameters |
|--------|-------------|------------|
| `ingest(document)` | Add knowledge from document | Document path/content |
| `query(criteria)` | Retrieve matching knowledge | Domain, keywords, filters |
| `update(entity_id, data)` | Modify existing entity | Entity ID, new data |
| `delete(entity_id)` | Remove entity | Entity ID |
| `validate()` | Check knowledge consistency | None |

### Query Interface

```python
# Query by domain
knowledge = domain_brain.query(
    domains=["financial", "compliance"],
    keywords=["transaction", "audit"],
    max_results=10,
    include_relationships=True
)

# Query by entity type
rules = domain_brain.query(
    entity_type=EntityType.RULE,
    filters={"severity": "CRITICAL"}
)

# Query with context
context_knowledge = domain_brain.query_with_context(
    current_file="src/orchestrators/planning.py",
    operation="implement_feature",
    depth=2
)
```

### Integration with Orchestrators

```python
class PlanningOrchestrator:
    def __init__(self, domain_brain: DomainBrain):
        self.domain_brain = domain_brain
    
    def execute(self, context: OrchestrationContext) -> Result:
        # Retrieve relevant knowledge
        knowledge = self.domain_brain.query(
            domains=["planning"],
            keywords=context.intent_keywords,
            max_results=5
        )
        
        # Use knowledge in decision-making
        if knowledge.contains_requirement("governance_required"):
            self.add_governance_step()
        
        # Execute with knowledge context
        return self.execute_with_knowledge(context, knowledge)
```

## Edge Case Handling

The Domain Brain includes comprehensive edge case handling:

### Duplicate Upload Detection (AC-DB-E01)

```python
# Hash-based deduplication
existing_hash = domain_brain.compute_hash(document)
if domain_brain.exists(existing_hash):
    raise DuplicateDocumentError(f"Document already exists: {existing_hash}")
```

### Brain Vacuum Prevention (AC-DB-E02)

```yaml
# TTL + archival strategy
knowledge_retention:
  active_ttl_days: 365
  archive_after_days: 180
  cleanup_schedule: "0 0 * * 0"  # Weekly
```

### Conflict Escalation Workflow (AC-DB-E03)

```
Conflict Detected
    │
    ├─ Tier 1: Automatic resolution (priority-based)
    │
    ├─ Tier 2: LENS synthesis (AI-assisted)
    │
    └─ Tier 3: Human escalation (manual resolution)
```

### Orphan Reference Detection (AC-DB-E04)

```python
# Detect and flag orphan references
orphans = domain_brain.detect_orphan_references()
for orphan in orphans:
    logger.warning(f"Orphan reference: {orphan.source} → {orphan.target}")
```

### Concurrent Write Handling (AC-DB-E05)

```python
# Optimistic locking with version tracking
with domain_brain.transaction() as txn:
    entity = txn.get(entity_id, for_update=True)
    if entity.version != expected_version:
        raise ConcurrentModificationError()
    entity.update(new_data)
    txn.commit()
```

### Version Tracking & Safe Deletion (AC-DB-E06)

```python
# Safe deletion with version preservation
domain_brain.archive(entity_id)  # Move to archive, preserve history
# OR
domain_brain.delete(entity_id, force=False)  # Soft delete with recovery option
```

## Tier 3 Knowledge Structure

Knowledge is organized in the Tier 3 knowledge base:

```
cortex_brain/
├── tier3/
│   ├── business_rules/
│   │   ├── financial.yaml
│   │   ├── compliance.yaml
│   │   └── operational.yaml
│   ├── domain_facts/
│   │   ├── entities.yaml
│   │   ├── relationships.yaml
│   │   └── constraints.yaml
│   └── knowledge_graph/
│       ├── nodes.json
│       └── edges.json
```

## Configuration

### Domain Brain Configuration

```yaml
# cortex-config.yaml
domain_brain:
  storage:
    type: "file"  # or "database"
    path: "cortex_brain/tier3"
  indexing:
    enabled: true
    rebuild_on_start: false
  caching:
    enabled: true
    ttl_seconds: 3600
    max_size_mb: 100
  conflict_resolution:
    strategy: "priority"
    escalation_threshold: 3
```

## Performance Characteristics

| Operation | Expected Latency | Throughput |
|-----------|------------------|------------|
| Query (cached) | <10ms | 1000+ qps |
| Query (uncached) | <100ms | 100+ qps |
| Batch ingestion (100 docs) | <5s | - |
| Validation | <50ms | - |
| Audit logging | <10ms | - |

## Related Documentation

- [System Overview](1-system-overview.md) - Architecture context
- [Orchestration Engine](3-orchestration-engine.md) - How orchestrators use Domain Brain
- [LENS Protocol](#) - Intent comprehension integration
- [Knowledge Ecosystem](../04-guides/advanced/knowledge-ecosystem.md) - Advanced usage
- [Troubleshooting](../04-guides/operations/4-troubleshooting.md) - Common issues
