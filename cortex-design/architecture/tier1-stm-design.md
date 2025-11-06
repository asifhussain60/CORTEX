# Tier 1: Short-Term Memory (STM) Design

**Version:** 1.0  
**Date:** 2025-11-05  
**Status:** 🏗️ DESIGN SPECIFICATION  
**Purpose:** Conversation history and working memory (last 20 conversations)

---

## 🎯 Overview

**Tier 1 = SHORT-TERM MEMORY** - Copilot's working memory that solves the amnesia problem.

**Purpose:**
- Store last 20 complete conversations (FIFO queue)
- Extract entities (files, intents, agents, components)
- Enable context continuity ("Make it purple" knows what "it" means)
- Support cross-conversation references
- Feed pattern extraction to Tier 2

**Storage:** SQLite (`cortex-brain.db`)  
**Size Target:** <100 KB  
**Performance Target:** <50ms for conversation queries

---

## 📊 SQLite Schema

### Table: `conversations`

```sql
CREATE TABLE conversations (
    id TEXT PRIMARY KEY,                    -- UUID (e.g., "conv_2025-11-05_1430_abc123")
    topic TEXT NOT NULL,                    -- Conversation topic (extracted from first message)
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,                 -- NULL if active, timestamp when completed
    status TEXT NOT NULL DEFAULT 'active' CHECK(status IN ('active', 'completed', 'deleted')),
    message_count INTEGER NOT NULL DEFAULT 0,
    outcome TEXT CHECK(outcome IN ('success', 'abandoned', 'error', NULL)),
    duration_seconds INTEGER,               -- Calculated when completed
    tags TEXT,                              -- JSON array of tags
    metadata TEXT                           -- JSON object for extensibility
);

-- Indexes
CREATE INDEX idx_conversations_created ON conversations(created_at DESC);
CREATE INDEX idx_conversations_status ON conversations(status);
CREATE INDEX idx_conversations_outcome ON conversations(outcome);

-- FIFO enforcement trigger
CREATE TRIGGER enforce_fifo_limit
AFTER INSERT ON conversations
WHEN (SELECT COUNT(*) FROM conversations WHERE status != 'deleted') > 20
BEGIN
    -- Mark oldest completed conversation as deleted (preserve active conversation)
    UPDATE conversations 
    SET status = 'deleted'
    WHERE id = (
        SELECT id FROM conversations 
        WHERE status = 'completed' 
        ORDER BY created_at ASC 
        LIMIT 1
    );
END;
```

### Table: `messages`

```sql
CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id TEXT NOT NULL,
    sequence INTEGER NOT NULL,              -- Message order within conversation
    role TEXT NOT NULL CHECK(role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    agent TEXT,                             -- Agent that generated message (if assistant)
    tool_calls TEXT,                        -- JSON array of tool calls
    metadata TEXT,                          -- JSON for extensibility
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE,
    UNIQUE(conversation_id, sequence)
);

-- Indexes
CREATE INDEX idx_messages_conversation ON messages(conversation_id, sequence);
CREATE INDEX idx_messages_timestamp ON messages(timestamp DESC);
CREATE INDEX idx_messages_role ON messages(role);
```

### Table: `conversation_entities`

```sql
CREATE TABLE conversation_entities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id TEXT NOT NULL,
    entity_type TEXT NOT NULL CHECK(entity_type IN ('file', 'intent', 'agent', 'component', 'test', 'error')),
    entity_value TEXT NOT NULL,
    confidence REAL NOT NULL CHECK(confidence >= 0.0 AND confidence <= 1.0),
    first_mention_message_id INTEGER,       -- Message where entity first appeared
    mention_count INTEGER NOT NULL DEFAULT 1,
    metadata TEXT,                          -- JSON for entity-specific data
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE,
    FOREIGN KEY (first_mention_message_id) REFERENCES messages(id) ON DELETE SET NULL
);

-- Indexes
CREATE INDEX idx_entities_conversation ON conversation_entities(conversation_id);
CREATE INDEX idx_entities_type ON conversation_entities(entity_type);
CREATE INDEX idx_entities_value ON conversation_entities(entity_value);
CREATE INDEX idx_entities_confidence ON conversation_entities(confidence DESC);

-- Unique constraint: one entity value per type per conversation
CREATE UNIQUE INDEX idx_entities_unique ON conversation_entities(conversation_id, entity_type, entity_value);
```

### Table: `conversation_files`

```sql
CREATE TABLE conversation_files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id TEXT NOT NULL,
    file_path TEXT NOT NULL,                -- Relative path from workspace root
    file_type TEXT,                         -- Extension or type (e.g., "cs", "md", "razor")
    action TEXT CHECK(action IN ('read', 'write', 'create', 'delete', 'reference')),
    first_mention_message_id INTEGER,
    mention_count INTEGER NOT NULL DEFAULT 1,
    metadata TEXT,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE,
    FOREIGN KEY (first_mention_message_id) REFERENCES messages(id) ON DELETE SET NULL
);

-- Indexes
CREATE INDEX idx_files_conversation ON conversation_files(conversation_id);
CREATE INDEX idx_files_path ON conversation_files(file_path);
CREATE INDEX idx_files_type ON conversation_files(file_type);

-- Unique constraint: one file path per conversation
CREATE UNIQUE INDEX idx_files_unique ON conversation_files(conversation_id, file_path);
```

### FTS5 Virtual Table (Full-Text Search)

```sql
-- Full-text search across conversations
CREATE VIRTUAL TABLE conversations_fts USING fts5(
    topic,
    tags,
    content='conversations',
    content_rowid='rowid'
);

-- Triggers to keep FTS index updated
CREATE TRIGGER conversations_fts_insert AFTER INSERT ON conversations
BEGIN
    INSERT INTO conversations_fts(rowid, topic, tags)
    VALUES (new.rowid, new.topic, new.tags);
END;

CREATE TRIGGER conversations_fts_delete AFTER DELETE ON conversations
BEGIN
    DELETE FROM conversations_fts WHERE rowid = old.rowid;
END;

CREATE TRIGGER conversations_fts_update AFTER UPDATE ON conversations
BEGIN
    UPDATE conversations_fts SET topic = new.topic, tags = new.tags WHERE rowid = new.rowid;
END;

-- Full-text search across messages
CREATE VIRTUAL TABLE messages_fts USING fts5(
    content,
    content='messages',
    content_rowid='id'
);

-- Triggers for messages FTS
CREATE TRIGGER messages_fts_insert AFTER INSERT ON messages
BEGIN
    INSERT INTO messages_fts(rowid, content)
    VALUES (new.id, new.content);
END;

CREATE TRIGGER messages_fts_delete AFTER DELETE ON messages
BEGIN
    DELETE FROM messages_fts WHERE rowid = old.id;
END;

CREATE TRIGGER messages_fts_update AFTER UPDATE ON messages
BEGIN
    UPDATE messages_fts SET content = new.content WHERE rowid = new.id;
END;
```

---

## 🔄 FIFO Rotation Algorithm

### Capacity Management

**Rule:** Maximum 20 conversations (excluding deleted)  
**Active conversation:** Never deleted (even if oldest)  
**Deletion:** Oldest completed conversation when 21st conversation created

### Algorithm

```python
class FIFOManager:
    """Manages conversation FIFO rotation"""
    
    MAX_CONVERSATIONS = 20
    
    def add_conversation(self, conversation: Conversation) -> None:
        """
        Add new conversation, trigger FIFO rotation if needed.
        SQLite trigger handles automatic deletion.
        """
        # Insert conversation
        db.execute("""
            INSERT INTO conversations (id, topic, created_at, status)
            VALUES (?, ?, ?, 'active')
        """, [conversation.id, conversation.topic, conversation.created_at])
        
        # Trigger will automatically delete oldest if count > 20
        # (See enforce_fifo_limit trigger in schema)
    
    def complete_conversation(self, conversation_id: str) -> None:
        """Mark conversation as completed"""
        db.execute("""
            UPDATE conversations
            SET status = 'completed',
                completed_at = CURRENT_TIMESTAMP,
                duration_seconds = (
                    SELECT (julianday(CURRENT_TIMESTAMP) - julianday(created_at)) * 86400
                    FROM conversations WHERE id = ?
                )
            WHERE id = ?
        """, [conversation_id, conversation_id])
    
    def get_deletable_conversation(self) -> Optional[str]:
        """
        Get oldest completed conversation for deletion.
        Never deletes active conversation.
        """
        result = db.execute("""
            SELECT id FROM conversations
            WHERE status = 'completed'
            ORDER BY created_at ASC
            LIMIT 1
        """).fetchone()
        
        return result['id'] if result else None
    
    def get_conversation_count(self) -> int:
        """Get count of non-deleted conversations"""
        result = db.execute("""
            SELECT COUNT(*) as count
            FROM conversations
            WHERE status != 'deleted'
        """).fetchone()
        
        return result['count']
```

### Pattern Extraction Before Deletion

```python
def extract_patterns_before_deletion(conversation_id: str) -> None:
    """
    Extract patterns from conversation before FIFO deletion.
    Called automatically by trigger or before manual deletion.
    """
    conversation = get_conversation(conversation_id)
    
    if not conversation:
        return
    
    # Extract patterns (Tier 2 responsibility)
    from tier2.pattern_extractor import PatternExtractor
    extractor = PatternExtractor()
    
    patterns = extractor.extract_from_conversation(conversation)
    
    # Save to Tier 2
    for pattern in patterns:
        extractor.save_pattern(pattern)
    
    # Mark conversation as extracted
    db.execute("""
        UPDATE conversations
        SET metadata = json_set(COALESCE(metadata, '{}'), '$.pattern_extracted', true)
        WHERE id = ?
    """, [conversation_id])
```

---

## 🧩 Entity Extraction

### Entity Types

| Type | Description | Example |
|------|-------------|---------|
| `file` | File paths mentioned | `InvoiceService.cs` |
| `intent` | User's intention | `PLAN`, `EXECUTE`, `TEST` |
| `agent` | KDS agents invoked | `work-planner`, `code-executor` |
| `component` | Code components | `InvoiceExporter`, `PdfService` |
| `test` | Test files/methods | `InvoiceServiceTests.cs` |
| `error` | Errors encountered | `CS1002`, `NullReferenceException` |

### Extraction Algorithm

```python
import re
from typing import List, Dict

class EntityExtractor:
    """Extracts entities from conversation messages"""
    
    FILE_PATTERNS = [
        r'`([^`]+\.(cs|ts|js|razor|md|json|yaml))`',  # Inline code
        r'(?:file|File|FILE):\s*([^\s]+)',            # File: prefix
        r'([A-Z][a-zA-Z]+\.(cs|ts|js|razor))'         # PascalCase.ext
    ]
    
    INTENT_KEYWORDS = {
        'PLAN': ['plan', 'design', 'create plan', 'how to'],
        'EXECUTE': ['implement', 'write code', 'add feature', 'create'],
        'TEST': ['test', 'verify', 'validate', 'check'],
        'FIX': ['fix', 'debug', 'resolve', 'repair'],
        'REFACTOR': ['refactor', 'improve', 'clean up', 'optimize']
    }
    
    AGENT_PATTERNS = [
        r'#file:KDS/prompts/internal/([a-z-]+\.md)',  # Agent file references
        r'(intent-router|work-planner|code-executor|test-generator)',  # Direct mentions
    ]
    
    def extract_entities(self, message: str, conversation_id: str, message_id: int) -> List[Dict]:
        """Extract all entities from a message"""
        entities = []
        
        # Extract files
        for pattern in self.FILE_PATTERNS:
            for match in re.finditer(pattern, message, re.IGNORECASE):
                file_path = match.group(1) if match.lastindex >= 1 else match.group(0)
                entities.append({
                    'type': 'file',
                    'value': file_path,
                    'confidence': 0.95
                })
        
        # Extract intent
        intent = self._extract_intent(message)
        if intent:
            entities.append({
                'type': 'intent',
                'value': intent,
                'confidence': 0.85
            })
        
        # Extract agents
        for pattern in self.AGENT_PATTERNS:
            for match in re.finditer(pattern, message):
                agent = match.group(1) if match.lastindex >= 1 else match.group(0)
                entities.append({
                    'type': 'agent',
                    'value': agent,
                    'confidence': 0.90
                })
        
        # Extract components (PascalCase identifiers)
        components = re.findall(r'\b([A-Z][a-zA-Z]{2,}(?:Service|Controller|Repository|Component|Model))\b', message)
        for comp in components:
            entities.append({
                'type': 'component',
                'value': comp,
                'confidence': 0.75
            })
        
        # Extract errors (error codes)
        errors = re.findall(r'(CS\d{4}|TS\d{4}|error [A-Z]+\d+)', message)
        for error in errors:
            entities.append({
                'type': 'error',
                'value': error,
                'confidence': 0.95
            })
        
        return entities
    
    def _extract_intent(self, message: str) -> Optional[str]:
        """Determine primary intent from message"""
        message_lower = message.lower()
        
        for intent, keywords in self.INTENT_KEYWORDS.items():
            if any(kw in message_lower for kw in keywords):
                return intent
        
        return None
    
    def save_entities(self, conversation_id: str, message_id: int, entities: List[Dict]) -> None:
        """Save extracted entities to database"""
        for entity in entities:
            # Check if entity already exists for this conversation
            existing = db.execute("""
                SELECT id, mention_count FROM conversation_entities
                WHERE conversation_id = ? AND entity_type = ? AND entity_value = ?
            """, [conversation_id, entity['type'], entity['value']]).fetchone()
            
            if existing:
                # Update mention count
                db.execute("""
                    UPDATE conversation_entities
                    SET mention_count = mention_count + 1
                    WHERE id = ?
                """, [existing['id']])
            else:
                # Insert new entity
                db.execute("""
                    INSERT INTO conversation_entities (
                        conversation_id, entity_type, entity_value, confidence, first_mention_message_id
                    ) VALUES (?, ?, ?, ?, ?)
                """, [conversation_id, entity['type'], entity['value'], entity['confidence'], message_id])
```

---

## 🔍 Query Patterns

### Conversation Queries

```python
# Get recent conversations (dashboard, agent context)
def get_recent_conversations(limit: int = 20) -> List[Conversation]:
    """<30ms - Get most recent conversations"""
    return db.execute("""
        SELECT * FROM conversations
        WHERE status != 'deleted'
        ORDER BY created_at DESC
        LIMIT ?
    """, [limit]).fetchall()

# Get conversation with messages
def get_conversation_with_messages(conversation_id: str) -> Dict:
    """<50ms - Get conversation + all messages"""
    conversation = db.execute("""
        SELECT * FROM conversations WHERE id = ?
    """, [conversation_id]).fetchone()
    
    messages = db.execute("""
        SELECT * FROM messages
        WHERE conversation_id = ?
        ORDER BY sequence ASC
    """, [conversation_id]).fetchall()
    
    return {
        'conversation': conversation,
        'messages': messages
    }

# Get conversation entities
def get_conversation_entities(conversation_id: str, entity_type: str = None) -> List[Entity]:
    """<20ms - Get entities (optionally filtered by type)"""
    if entity_type:
        return db.execute("""
            SELECT * FROM conversation_entities
            WHERE conversation_id = ? AND entity_type = ?
            ORDER BY confidence DESC, mention_count DESC
        """, [conversation_id, entity_type]).fetchall()
    else:
        return db.execute("""
            SELECT * FROM conversation_entities
            WHERE conversation_id = ?
            ORDER BY entity_type, confidence DESC
        """, [conversation_id]).fetchall()

# Search conversations (FTS5)
def search_conversations(query: str, limit: int = 10) -> List[Dict]:
    """<100ms - Full-text search across conversations"""
    return db.execute("""
        SELECT 
            conversations.*,
            snippet(conversations_fts, -1, '<mark>', '</mark>', '...', 20) AS snippet,
            bm25(conversations_fts) AS rank
        FROM conversations
        JOIN conversations_fts ON conversations.rowid = conversations_fts.rowid
        WHERE conversations_fts MATCH ?
        ORDER BY rank
        LIMIT ?
    """, [query, limit]).fetchall()

# Search messages (FTS5)
def search_messages(query: str, limit: int = 20) -> List[Dict]:
    """<100ms - Full-text search across messages"""
    return db.execute("""
        SELECT 
            messages.*,
            conversations.topic,
            snippet(messages_fts, -1, '<mark>', '</mark>', '...', 30) AS snippet,
            bm25(messages_fts) AS rank
        FROM messages
        JOIN messages_fts ON messages.id = messages_fts.rowid
        JOIN conversations ON messages.conversation_id = conversations.id
        WHERE messages_fts MATCH ?
        ORDER BY rank
        LIMIT ?
    """, [query, limit]).fetchall()
```

### Entity Queries

```python
# Find conversations with specific file
def find_conversations_with_file(file_path: str) -> List[str]:
    """<15ms - Find all conversations mentioning a file"""
    results = db.execute("""
        SELECT DISTINCT conversation_id
        FROM conversation_files
        WHERE file_path LIKE ?
        ORDER BY mention_count DESC
    """, [f'%{file_path}%']).fetchall()
    
    return [r['conversation_id'] for r in results]

# Get files frequently modified together
def get_co_modified_files(file_path: str, min_conversations: int = 2) -> List[Dict]:
    """<30ms - Find files often modified together (co-modification pattern)"""
    return db.execute("""
        SELECT 
            cf2.file_path,
            COUNT(DISTINCT cf1.conversation_id) as co_modification_count
        FROM conversation_files cf1
        JOIN conversation_files cf2 
            ON cf1.conversation_id = cf2.conversation_id
            AND cf1.file_path != cf2.file_path
        WHERE cf1.file_path = ?
        GROUP BY cf2.file_path
        HAVING co_modification_count >= ?
        ORDER BY co_modification_count DESC
    """, [file_path, min_conversations]).fetchall()

# Get intent distribution
def get_intent_distribution() -> Dict[str, int]:
    """<20ms - Get intent frequency"""
    results = db.execute("""
        SELECT entity_value as intent, COUNT(*) as count
        FROM conversation_entities
        WHERE entity_type = 'intent'
        GROUP BY entity_value
        ORDER BY count DESC
    """).fetchall()
    
    return {r['intent']: r['count'] for r in results}
```

---

## 🧪 Test Specifications (58 tests)

### Conversation CRUD (10 tests)

```python
def test_create_conversation():
    conv_id = create_conversation("Add invoice export")
    assert conv_id is not None
    
def test_get_conversation():
    conv = get_conversation(conv_id)
    assert conv['topic'] == "Add invoice export"
    
def test_complete_conversation():
    complete_conversation(conv_id)
    conv = get_conversation(conv_id)
    assert conv['status'] == 'completed'
    assert conv['completed_at'] is not None
```

### FIFO Rotation (6 tests)

```python
def test_fifo_enforces_20_limit():
    # Create 21 conversations
    for i in range(21):
        create_conversation(f"Conversation {i}")
    
    count = get_conversation_count()
    assert count == 20, "FIFO should limit to 20 conversations"

def test_fifo_deletes_oldest_completed():
    # Create 20, complete first, add 21st
    oldest_id = create_conversation("Oldest")
    complete_conversation(oldest_id)
    
    for i in range(19):
        create_conversation(f"Conv {i}")
    
    # Add 21st
    create_conversation("Newest")
    
    # Oldest should be deleted
    oldest = get_conversation(oldest_id)
    assert oldest is None or oldest['status'] == 'deleted'

def test_fifo_preserves_active_conversation():
    # Create 20 conversations, don't complete first
    first_id = create_conversation("Active")
    
    for i in range(20):
        conv_id = create_conversation(f"Conv {i}")
        complete_conversation(conv_id)
    
    # First conversation should still exist (active)
    first = get_conversation(first_id)
    assert first['status'] == 'active'
```

### Entity Extraction (8 tests)

```python
def test_extract_file_entities():
    message = "I modified InvoiceService.cs and InvoiceController.cs"
    entities = EntityExtractor().extract_entities(message, conv_id, msg_id)
    
    file_entities = [e for e in entities if e['type'] == 'file']
    assert len(file_entities) == 2
    assert 'InvoiceService.cs' in [e['value'] for e in file_entities]

def test_extract_intent_entities():
    message = "I want to implement PDF export functionality"
    entities = EntityExtractor().extract_entities(message, conv_id, msg_id)
    
    intent_entities = [e for e in entities if e['type'] == 'intent']
    assert len(intent_entities) == 1
    assert intent_entities[0]['value'] == 'EXECUTE'

def test_entity_mention_count():
    # First mention
    save_entity(conv_id, 'file', 'InvoiceService.cs', msg_id_1)
    entity = get_entity(conv_id, 'file', 'InvoiceService.cs')
    assert entity['mention_count'] == 1
    
    # Second mention
    save_entity(conv_id, 'file', 'InvoiceService.cs', msg_id_2)
    entity = get_entity(conv_id, 'file', 'InvoiceService.cs')
    assert entity['mention_count'] == 2
```

### Cross-Conversation Linking (4 tests)

```python
def test_find_conversations_with_file():
    # Create 3 conversations, 2 mention same file
    conv1 = create_conversation("Export feature")
    save_file_entity(conv1, 'InvoiceService.cs')
    
    conv2 = create_conversation("Fix bug")
    save_file_entity(conv2, 'InvoiceService.cs')
    
    conv3 = create_conversation("Unrelated")
    save_file_entity(conv3, 'CustomerService.cs')
    
    convs = find_conversations_with_file('InvoiceService.cs')
    assert len(convs) == 2
    assert conv1 in convs and conv2 in convs
```

### FTS Search (5 tests)

```python
def test_search_conversations_fts():
    create_conversation("Add PDF export to invoices")
    create_conversation("Fix null reference in customer service")
    
    results = search_conversations("invoice")
    assert len(results) >= 1
    assert 'PDF export' in results[0]['snippet']

def test_search_messages_fts():
    conv_id = create_conversation("Feature work")
    add_message(conv_id, "Implement PDF export")
    add_message(conv_id, "Create InvoiceExporter class")
    
    results = search_messages("InvoiceExporter")
    assert len(results) >= 1
```

### Query Performance (5 tests)

```python
def test_conversation_load_performance():
    # Load conversation with 50 messages
    conv_id = create_conversation_with_messages(50)
    
    start = time.perf_counter()
    get_conversation_with_messages(conv_id)
    elapsed_ms = (time.perf_counter() - start) * 1000
    
    assert elapsed_ms < 50, f"Conversation load took {elapsed_ms}ms (target: <50ms)"

def test_entity_search_performance():
    # 1000 entities across 20 conversations
    setup_entity_test_data(1000)
    
    start = time.perf_counter()
    find_conversations_with_file('InvoiceService.cs')
    elapsed_ms = (time.perf_counter() - start) * 1000
    
    assert elapsed_ms < 30, f"Entity search took {elapsed_ms}ms (target: <30ms)"
```

### Integration with Tier 2 (8 tests)

```python
def test_pattern_extraction_before_deletion():
    conv_id = create_conversation_with_full_workflow()
    complete_conversation(conv_id)
    
    # Trigger FIFO deletion
    trigger_fifo_rotation()
    
    # Verify patterns extracted to Tier 2
    from tier2 import get_patterns_from_conversation
    patterns = get_patterns_from_conversation(conv_id)
    assert len(patterns) > 0
```

### Remaining tests: Message CRUD, file tracking, error handling, edge cases (12 tests)

---

## 📊 Performance Benchmarks

| Operation | Target | Test Method |
|-----------|--------|-------------|
| Create conversation | <10ms | Single insert |
| Get conversation + messages | <50ms | Join query (50 messages) |
| Entity extraction | <20ms | Per message |
| Entity search | <30ms | Indexed query |
| FTS conversation search | <100ms | Full-text search (20 convs) |
| FTS message search | <100ms | Full-text search (500 msgs) |
| FIFO rotation | <50ms | Delete + trigger |

---

## 🔄 Migration from KDS v8

### Source: `kds-brain/conversation-history.jsonl`

```python
# scripts/migrate-tier1.py

def migrate_conversation_history():
    """Migrate conversation-history.jsonl → SQLite Tier 1"""
    
    # Read KDS v8 JSONL
    with open('kds-brain/conversation-history.jsonl') as f:
        conversations = [json.loads(line) for line in f]
    
    # Migrate each conversation
    for conv in conversations[-20:]:  # Last 20 only
        conv_id = conv['id']
        
        # Insert conversation
        db.execute("""
            INSERT INTO conversations (id, topic, created_at, status)
            VALUES (?, ?, ?, 'completed')
        """, [conv_id, conv['topic'], conv['timestamp']])
        
        # Insert messages
        for seq, msg in enumerate(conv['messages'], 1):
            db.execute("""
                INSERT INTO messages (conversation_id, sequence, role, content, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """, [conv_id, seq, msg['role'], msg['content'], msg['timestamp']])
        
        # Extract and save entities
        extractor = EntityExtractor()
        for msg_id, msg in zip(get_message_ids(conv_id), conv['messages']):
            entities = extractor.extract_entities(msg['content'], conv_id, msg_id)
            extractor.save_entities(conv_id, msg_id, entities)
    
    print(f"✅ Migrated {len(conversations[-20:])} conversations to Tier 1")
```

---

## 📚 Related Documents

- [Architecture Overview](overview.md)
- [Tier 0: Governance](tier0-governance.md)
- [Tier 2: LTM Design](tier2-ltm-design.md)
- [Storage Schema](storage-schema.md)

---

**Status:** ✅ Tier 1 STM Design Complete  
**Next:** Create Tier 2 LTM design  
**Version:** 1.0 (Initial design)

