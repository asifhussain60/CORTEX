# CORTEX Tier 2: Knowledge Graph (Long-Term Memory)

## Overview
Tier 2 is CORTEX's long-term memory layer, storing consolidated patterns, learnings, and historical insights. Uses SQLite with FTS5 (Full-Text Search) for semantic search capabilities.

## Architecture

### Storage: SQLite with FTS5
- **File**: `cortex-brain/tier2/knowledge_graph.db`
- **Tables**: 
  - `patterns` - Consolidated learnings and insights
  - `pattern_relationships` - Links between related patterns
  - `pattern_tags` - Tag-based categorization
  - `pattern_fts` - FTS5 virtual table for semantic search

### Schema Design

```sql
-- Patterns table (core knowledge storage)
CREATE TABLE patterns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pattern_id TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    pattern_type TEXT NOT NULL,  -- workflow, principle, anti_pattern, solution, etc.
    confidence REAL DEFAULT 1.0,  -- 0.0 to 1.0
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    access_count INTEGER DEFAULT 0,
    source TEXT,  -- Where pattern came from (conversation_id, manual, etc.)
    metadata TEXT  -- JSON: {priority, tags, related_files, etc.}
);

-- Pattern relationships (knowledge graph edges)
CREATE TABLE pattern_relationships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    from_pattern_id TEXT NOT NULL,
    to_pattern_id TEXT NOT NULL,
    relationship_type TEXT NOT NULL,  -- related_to, replaces, extends, conflicts_with
    strength REAL DEFAULT 1.0,  -- 0.0 to 1.0
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (from_pattern_id) REFERENCES patterns(pattern_id),
    FOREIGN KEY (to_pattern_id) REFERENCES patterns(pattern_id),
    UNIQUE(from_pattern_id, to_pattern_id, relationship_type)
);

-- Pattern tags
CREATE TABLE pattern_tags (
    pattern_id TEXT NOT NULL,
    tag TEXT NOT NULL,
    PRIMARY KEY (pattern_id, tag),
    FOREIGN KEY (pattern_id) REFERENCES patterns(pattern_id)
);

-- FTS5 virtual table for semantic search
CREATE VIRTUAL TABLE pattern_fts USING fts5(
    pattern_id UNINDEXED,
    title,
    content,
    tags,
    content='patterns',
    content_rowid='id'
);
```

### Indexes for Performance
```sql
CREATE INDEX idx_patterns_type ON patterns(pattern_type);
CREATE INDEX idx_patterns_confidence ON patterns(confidence DESC);
CREATE INDEX idx_patterns_accessed ON patterns(last_accessed DESC);
CREATE INDEX idx_relationships_from ON pattern_relationships(from_pattern_id);
CREATE INDEX idx_relationships_to ON pattern_relationships(to_pattern_id);
```

## Pattern Types

### 1. Workflows
- **Description**: Proven development workflows
- **Example**: "TDD cycle: RED → GREEN → REFACTOR"
- **Confidence**: Based on success rate

### 2. Principles
- **Description**: Core design principles
- **Example**: "Single Responsibility Principle"
- **Confidence**: High (fundamental truths)

### 3. Anti-Patterns
- **Description**: Things to avoid
- **Example**: "God classes violate SRP"
- **Confidence**: Based on detection frequency

### 4. Solutions
- **Description**: Reusable problem solutions
- **Example**: "FIFO queue for memory management"
- **Confidence**: Based on application success

### 5. Context
- **Description**: Project-specific knowledge
- **Example**: "CORTEX uses 4-tier architecture"
- **Confidence**: High (current state)

## Pattern Confidence Decay

### Decay Logic (from governance.yaml Rule #12)
```python
decay_rules = {
    'unused_60_days': -0.10,   # Reduce confidence by 10%
    'unused_90_days': -0.25,   # Reduce confidence by 25%
    'unused_120_days': 'mark_for_deletion',
    'confidence_below_30': 'auto_delete'
}
```

### Exceptions
- Tier 0 rules (never decay)
- Explicitly pinned patterns
- Patterns with high relationship count

## Core Operations

### 1. Add Pattern
```python
knowledge_graph.add_pattern(
    pattern_id="pattern_tdd_cycle",
    title="TDD Development Cycle",
    content="Write failing test first (RED), implement code (GREEN), refactor (REFACTOR)",
    pattern_type=PatternType.WORKFLOW,
    confidence=1.0,
    tags=["tdd", "testing", "quality"],
    source="conversation_xyz"
)
```

### 2. Search Patterns (FTS5)
```python
# Semantic search using FTS5
results = knowledge_graph.search_patterns(
    query="test driven development",
    min_confidence=0.5
)
# Returns patterns ranked by relevance
```

### 3. Link Patterns
```python
# Create relationship between patterns
knowledge_graph.link_patterns(
    from_pattern="pattern_tdd_cycle",
    to_pattern="pattern_refactoring",
    relationship_type=RelationshipType.EXTENDS,
    strength=0.9
)
```

### 4. Get Related Patterns
```python
# Find patterns related to a given pattern
related = knowledge_graph.get_related_patterns(
    pattern_id="pattern_tdd_cycle",
    relationship_type=RelationshipType.RELATED_TO,
    max_depth=2  # Traverse graph up to 2 levels
)
```

### 5. Decay Management
```python
# Apply confidence decay to unused patterns
decayed = knowledge_graph.apply_confidence_decay()
# Returns: {
#   'decayed_count': 5,
#   'deleted_count': 2,
#   'patterns_affected': [...]
# }
```

## FTS5 Full-Text Search

### Features
- **Ranking**: BM25 algorithm for relevance scoring
- **Phrase Search**: "exact phrase" matching
- **Prefix Search**: partial* matching
- **Boolean**: AND, OR, NOT operators
- **Highlighting**: Extract snippets with matches

### Search Examples
```python
# Simple keyword search
results = kg.search_patterns("testing")

# Phrase search
results = kg.search_patterns('"test driven development"')

# Boolean search
results = kg.search_patterns("testing AND refactoring NOT manual")

# Prefix search
results = kg.search_patterns("refactor*")
```

## Performance Targets

| Operation | Target | Expected |
|-----------|--------|----------|
| Add pattern | <50ms | ~20ms |
| Search patterns (FTS5) | <100ms | ~50ms |
| Get pattern by ID | <10ms | ~5ms |
| Get related patterns | <150ms | ~80ms |
| Apply decay (100 patterns) | <500ms | ~300ms |

## Test Coverage Requirements

### Unit Tests (25 tests minimum)
1. **Database Initialization** (3 tests)
   - Creates database file
   - Creates all tables
   - Creates FTS5 virtual table

2. **Pattern Management** (6 tests)
   - Add pattern
   - Get pattern by ID
   - Update pattern
   - Delete pattern
   - List patterns by type
   - Update access timestamp

3. **FTS5 Search** (5 tests)
   - Simple keyword search
   - Phrase search
   - Boolean search (AND, OR, NOT)
   - Prefix search
   - Ranking by relevance

4. **Pattern Relationships** (4 tests)
   - Link two patterns
   - Get related patterns
   - Traverse graph (multi-level)
   - Detect circular relationships

5. **Confidence Decay** (4 tests)
   - Apply decay based on age
   - Delete low-confidence patterns
   - Protect pinned patterns
   - Track decay history

6. **Tag Management** (3 tests)
   - Add tags to pattern
   - Find patterns by tag
   - Get tag cloud (frequency)

## Integration with Other Tiers

### Tier 1 (Working Memory)
- **Pattern Extraction**: Extract patterns from conversations before eviction
- **Entity Linking**: Link STM entities to LTM patterns
- **Learning Transfer**: Move recurring insights from Tier 1 to Tier 2

### Tier 0 (Governance)
- **Decay Rules**: Governed by Rule #12
- **Data Boundaries**: Governed by Rule #10
- **Quality Gates**: All code must pass DoD/DoR

### Tier 3 (Context) - Future
- **No direct interaction**: Tier boundaries enforced
- **Separate concerns**: Tier 2 = patterns, Tier 3 = metrics

## Implementation Phases

### Phase 2.1: Database Setup (TDD)
- ✅ Write tests for schema creation
- ✅ Implement KnowledgeGraph class
- ✅ Create tables and FTS5 virtual table
- ✅ Validate schema

### Phase 2.2: Pattern CRUD (TDD)
- ✅ Write tests for CRUD operations
- ✅ Implement add_pattern()
- ✅ Implement get_pattern()
- ✅ Implement update_pattern()
- ✅ Implement delete_pattern()

### Phase 2.3: FTS5 Search (TDD)
- ✅ Write tests for search operations
- ✅ Implement search_patterns()
- ✅ Test ranking and relevance
- ✅ Test phrase, boolean, prefix search

### Phase 2.4: Pattern Relationships (TDD)
- ✅ Write tests for graph operations
- ✅ Implement link_patterns()
- ✅ Implement get_related_patterns()
- ✅ Implement graph traversal

### Phase 2.5: Confidence Decay (TDD)
- ✅ Write tests for decay logic
- ✅ Implement apply_confidence_decay()
- ✅ Implement protection mechanisms
- ✅ Track decay history

## Success Criteria

- ✅ 25+ unit tests passing (95%+ coverage)
- ✅ FTS5 search working correctly
- ✅ Pattern relationships functional
- ✅ Confidence decay implemented
- ✅ All queries <150ms
- ✅ Tier 0 governance rules respected
- ✅ Zero compilation errors/warnings
- ✅ Documentation complete

## SQLite FTS5 Benefits

### Why FTS5?
1. **Semantic Search**: BM25 ranking algorithm
2. **Fast**: 10-100x faster than text scanning
3. **Built-in**: Part of SQLite (no external dependencies)
4. **Powerful**: Supports phrases, booleans, prefix matching
5. **Lightweight**: No separate search engine needed

### FTS5 vs. Alternatives
- **vs. YAML**: 100x faster search
- **vs. Elasticsearch**: No separate service, simpler
- **vs. LIKE queries**: 50x faster, better ranking

## Next Phase
**Phase 3**: Tier 3 (Development Context) - Git/Test/Build metrics with JSON storage
