# CORTEX Tier 1: Working Memory (Short-Term Memory)

## Overview
Tier 1 is CORTEX's short-term memory layer, storing the last 20 conversations with FIFO eviction. Uses SQLite for fast queries (<100ms) and entity extraction.

## Architecture

### Storage: SQLite Database
- **File**: `cortex-brain/tier1/working_memory.db`
- **Tables**: 
  - `conversations` - Recent conversation history
  - `entities` - Extracted entities (files, classes, methods, etc.)
  - `conversation_entities` - Many-to-many relationship

### Schema Design

```sql
-- Conversations table
CREATE TABLE conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    message_count INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT 0,
    summary TEXT,
    tags TEXT  -- JSON array
);

-- Entities table (files, classes, methods, variables)
CREATE TABLE entities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_type TEXT NOT NULL,  -- file, class, method, variable, concept
    entity_name TEXT NOT NULL,
    file_path TEXT,
    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    access_count INTEGER DEFAULT 1,
    UNIQUE(entity_type, entity_name, file_path)
);

-- Conversation-Entity relationships
CREATE TABLE conversation_entities (
    conversation_id TEXT NOT NULL,
    entity_id INTEGER NOT NULL,
    relevance_score REAL DEFAULT 1.0,
    PRIMARY KEY (conversation_id, entity_id),
    FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id),
    FOREIGN KEY (entity_id) REFERENCES entities(id)
);

-- Messages table (full conversation content)
CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id TEXT NOT NULL,
    role TEXT NOT NULL,  -- user, assistant, system
    content TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id)
);
```

### Indexes for Performance
```sql
CREATE INDEX idx_conversations_created ON conversations(created_at DESC);
CREATE INDEX idx_conversations_active ON conversations(is_active);
CREATE INDEX idx_entities_type ON entities(entity_type);
CREATE INDEX idx_entities_accessed ON entities(last_accessed DESC);
CREATE INDEX idx_messages_conversation ON messages(conversation_id);
```

## FIFO Queue Management

### Rules (from governance.yaml Rule #11)
- **Capacity**: 20 conversations maximum
- **Eviction**: FIFO (oldest conversation deleted first)
- **Protection**: Active conversation NEVER deleted
- **Pattern Extraction**: Extract patterns to Tier 2 before deletion

### Eviction Process
```python
def evict_oldest_conversation():
    """When 21st conversation is added"""
    # 1. Find oldest non-active conversation
    oldest = find_oldest_inactive_conversation()
    
    # 2. Extract patterns to Tier 2 (future phase)
    # patterns = extract_patterns(oldest)
    # tier2.store_patterns(patterns)
    
    # 3. Delete conversation from Tier 1
    delete_conversation(oldest.id)
    
    # 4. Log deletion event
    log_event("conversation_evicted", oldest.id)
```

## Core Operations

### 1. Add Conversation
```python
working_memory.add_conversation(
    conversation_id="conv_20251105_001",
    title="Implement Phase 1 STM",
    messages=[
        {"role": "user", "content": "Start Phase 1"},
        {"role": "assistant", "content": "Creating Tier 1..."}
    ]
)
```

### 2. Get Recent Conversations
```python
# Get last N conversations
recent = working_memory.get_recent_conversations(limit=5)

# Get active conversation
active = working_memory.get_active_conversation()
```

### 3. Entity Extraction
```python
# Extract entities from conversation
entities = working_memory.extract_entities(conversation_id)
# Returns: [
#   {"type": "file", "name": "governance_engine.py"},
#   {"type": "class", "name": "GovernanceEngine"},
#   {"type": "method", "name": "validate_definition_of_done"}
# ]
```

### 4. Search Conversations
```python
# Search by keyword
results = working_memory.search_conversations("TDD enforcement")

# Search by entity
results = working_memory.find_conversations_with_entity(
    entity_type="file",
    entity_name="governance.yaml"
)
```

## Entity Extraction Logic

### Supported Entity Types
1. **Files**: Any file path mentioned (`.py`, `.yaml`, `.md`, etc.)
2. **Classes**: PascalCase identifiers in backticks
3. **Methods**: snake_case with parentheses `method_name()`
4. **Variables**: snake_case identifiers
5. **Concepts**: Key technical terms (TDD, SOLID, FIFO, etc.)

### Extraction Patterns
```python
PATTERNS = {
    'file': r'`([a-zA-Z0-9_\-/\\\.]+\.(py|yaml|md|json|txt))`',
    'class': r'`([A-Z][a-zA-Z0-9_]*)`',
    'method': r'`([a-z_][a-z0-9_]*)\(\)`',
    'concept': PREDEFINED_CONCEPTS  # TDD, SOLID, FIFO, etc.
}
```

## Performance Targets

| Operation | Target | Current |
|-----------|--------|---------|
| Add conversation | <50ms | TBD |
| Get recent (20) | <100ms | TBD |
| Search conversations | <150ms | TBD |
| Entity extraction | <200ms | TBD |
| FIFO eviction | <100ms | TBD |

## Test Coverage Requirements

### Unit Tests (20 tests minimum)
1. **Database Initialization** (3 tests)
   - Creates database file
   - Creates all tables
   - Creates all indexes

2. **Conversation Management** (5 tests)
   - Add conversation
   - Get conversation by ID
   - Get recent conversations
   - Mark conversation as active
   - Update conversation

3. **FIFO Queue** (4 tests)
   - Adds 20 conversations without eviction
   - Evicts oldest when 21st added
   - Never evicts active conversation
   - Logs eviction events

4. **Entity Extraction** (4 tests)
   - Extracts file entities
   - Extracts class entities
   - Extracts method entities
   - Links entities to conversations

5. **Search & Query** (4 tests)
   - Search conversations by keyword
   - Find conversations by entity
   - Get conversations by date range
   - Get entity usage statistics

## Integration with Other Tiers

### Tier 0 (Governance)
- **FIFO enforcement**: Governed by Rule #11
- **Data boundaries**: Governed by Rule #10
- **Quality gates**: All code must pass DoD/DoR

### Tier 2 (Knowledge Graph) - Future
- **Pattern extraction**: Before conversation eviction
- **Entity consolidation**: Link STM entities to LTM patterns
- **Learning transfer**: Extract insights for long-term storage

### Tier 3 (Context) - Future
- **No direct interaction**: Tier boundaries enforced
- **Separate concerns**: Tier 1 = conversations, Tier 3 = metrics

## Implementation Phases

### Phase 1.1: Database Setup (TDD)
- ✅ Write tests for schema creation
- ✅ Implement WorkingMemory class
- ✅ Create tables and indexes
- ✅ Validate schema

### Phase 1.2: Conversation CRUD (TDD)
- ✅ Write tests for CRUD operations
- ✅ Implement add_conversation()
- ✅ Implement get_conversation()
- ✅ Implement update_conversation()
- ✅ Implement delete_conversation()

### Phase 1.3: FIFO Queue (TDD)
- ✅ Write tests for FIFO logic
- ✅ Implement eviction when 21st conversation added
- ✅ Protect active conversation from eviction
- ✅ Log eviction events

### Phase 1.4: Entity Extraction (TDD)
- ✅ Write tests for entity extraction
- ✅ Implement extraction patterns
- ✅ Link entities to conversations
- ✅ Track entity access statistics

### Phase 1.5: Search & Query (TDD)
- ✅ Write tests for search operations
- ✅ Implement keyword search
- ✅ Implement entity-based search
- ✅ Implement date range queries

## Success Criteria

- ✅ 20+ unit tests passing (95%+ coverage)
- ✅ FIFO queue working correctly
- ✅ All queries <100ms
- ✅ Entity extraction functional
- ✅ Tier 0 governance rules respected
- ✅ Zero compilation errors/warnings
- ✅ Documentation complete

## Next Phase
**Phase 2**: Tier 2 (Knowledge Graph) - SQLite with FTS5 for pattern storage and semantic search
