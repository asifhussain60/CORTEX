# Phase 1: Tier 1 (Working Memory - Short-Term Memory)

**Version:** 1.0  
**Date:** 2025-11-05  
**Duration:** 8-10 hours + 1 hour holistic review  
**Dependencies:** Phase 0 complete + reviewed  
**Storage:** SQLite (`cortex-brain.db` → `working_memory` schema)  
**Performance Target:** <50ms conversation queries, 50 conversation FIFO queue

---

## 🎯 Overview

**Purpose:** Build the short-term memory layer that maintains context across the last 50 conversations. Enables "Make it purple" to reference the FAB button from an earlier conversation.

**Key Deliverables:**
- Conversation tracking system (last 50 conversations)
- Message storage with entity extraction
- FIFO queue management (oldest deleted when 51st conversation starts)
- Entity extraction for cross-conversation context
- Conversation boundary detection
- Complete test coverage (22 unit + 4 integration tests)

---

## 📊 What We're Building

### Database Schema (from unified-database-schema.sql)

```sql
-- Conversations Table
CREATE TABLE working_memory_conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id TEXT UNIQUE NOT NULL,   -- UUID
    title TEXT,
    intent TEXT,                            -- PLAN, EXECUTE, TEST, etc.
    status TEXT DEFAULT 'active',           -- active, completed, archived
    outcome TEXT,                           -- success, failed, cancelled
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    message_count INTEGER DEFAULT 0,
    pattern_extracted BOOLEAN DEFAULT FALSE -- Tier 2 extracted patterns?
);

-- Messages Table
CREATE TABLE working_memory_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id TEXT REFERENCES working_memory_conversations(conversation_id),
    role TEXT CHECK(role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tokens INTEGER,
    sequence INTEGER NOT NULL
);

-- Entity Extraction
CREATE TABLE working_memory_entities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id TEXT REFERENCES working_memory_conversations(conversation_id),
    entity_type TEXT NOT NULL,              -- file, class, function, component, etc.
    entity_value TEXT NOT NULL,
    context TEXT,
    first_mentioned TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    mention_count INTEGER DEFAULT 1
);

-- Git Commits (Phase 3.5 integration)
CREATE TABLE working_memory_commits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id TEXT REFERENCES working_memory_conversations(conversation_id),
    commit_sha TEXT NOT NULL,
    commit_message TEXT,
    timestamp TIMESTAMP,
    files_changed INTEGER
);

-- Indexes for performance
CREATE INDEX idx_wm_conversations_status ON working_memory_conversations(status);
CREATE INDEX idx_wm_conversations_created ON working_memory_conversations(created_at DESC);
CREATE INDEX idx_wm_messages_conversation ON working_memory_messages(conversation_id);
CREATE INDEX idx_wm_entities_conversation ON working_memory_entities(conversation_id);
CREATE INDEX idx_wm_entities_type_value ON working_memory_entities(entity_type, entity_value);
```

---

## 🏗️ Implementation Tasks

### Task 1: WorkingMemory Core Engine
**File:** `CORTEX/src/tier1/working_memory_engine.py`  
**Duration:** 2 hours  
**Tests:** 6 unit tests

**Description:**
Core conversation tracking with SQLite backend and FIFO queue management.

**Implementation Details:**
```python
from typing import Optional, List, Dict
import sqlite3
from datetime import datetime
import uuid

class WorkingMemoryEngine:
    """Tier 1: Short-term memory for last 50 conversations"""
    
    def __init__(self, db_path: str = "cortex-brain.db"):
        self.db_path = db_path
        self.max_conversations = self._load_capacity()  # Default: 50 (configurable)
    
    def _load_capacity(self) -> int:
        """Load conversation capacity from config"""
        # Read from tier1-config.yaml or governance Rule #11
        # Default: 50, Range: 1-100
        return 50
    
    def start_conversation(self, title: str, intent: str) -> str:
        """
        Start new conversation, enforce FIFO if needed
        
        Returns:
            conversation_id: UUID for new conversation
        """
        # Check if at capacity (50 conversations)
        count = self._get_active_conversation_count()
        
        if count >= self.max_conversations:
            # FIFO: Delete oldest non-active conversation
            oldest = self._get_oldest_completed_conversation()
            if oldest:
                self._delete_conversation_with_pattern_extraction(oldest)
        
        # Create new conversation
        conversation_id = str(uuid.uuid4())
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            INSERT INTO working_memory_conversations 
            (conversation_id, title, intent, status, created_at)
            VALUES (?, ?, ?, 'active', ?)
        """, (conversation_id, title, intent, datetime.now()))
        conn.commit()
        conn.close()
        
        return conversation_id
    
    def add_message(self, conversation_id: str, role: str, content: str, 
                   tokens: Optional[int] = None):
        """Add message to conversation"""
        conn = sqlite3.connect(self.db_path)
        
        # Get current message count for sequence
        cursor = conn.execute("""
            SELECT COALESCE(MAX(sequence), 0) FROM working_memory_messages
            WHERE conversation_id = ?
        """, (conversation_id,))
        sequence = cursor.fetchone()[0] + 1
        
        # Insert message
        conn.execute("""
            INSERT INTO working_memory_messages
            (conversation_id, role, content, tokens, sequence, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (conversation_id, role, content, tokens, sequence, datetime.now()))
        
        # Update message count
        conn.execute("""
            UPDATE working_memory_conversations
            SET message_count = message_count + 1
            WHERE conversation_id = ?
        """, (conversation_id,))
        
        conn.commit()
        conn.close()
    
    def complete_conversation(self, conversation_id: str, outcome: str):
        """Mark conversation as complete"""
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            UPDATE working_memory_conversations
            SET status = 'completed', completed_at = ?, outcome = ?
            WHERE conversation_id = ?
        """, (datetime.now(), outcome, conversation_id))
        conn.commit()
        conn.close()
    
    def get_conversation(self, conversation_id: str) -> Optional[Dict]:
        """Get conversation with all messages"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        
        # Get conversation metadata
        cursor = conn.execute("""
            SELECT * FROM working_memory_conversations
            WHERE conversation_id = ?
        """, (conversation_id,))
        conv = cursor.fetchone()
        
        if not conv:
            return None
        
        # Get all messages
        cursor = conn.execute("""
            SELECT role, content, timestamp, sequence
            FROM working_memory_messages
            WHERE conversation_id = ?
            ORDER BY sequence ASC
        """, (conversation_id,))
        messages = cursor.fetchall()
        
        conn.close()
        
        return {
            'conversation_id': conv['conversation_id'],
            'title': conv['title'],
            'intent': conv['intent'],
            'status': conv['status'],
            'outcome': conv['outcome'],
            'message_count': conv['message_count'],
            'messages': [dict(m) for m in messages]
        }
    
    def get_recent_conversations(self, limit: int = 10) -> List[Dict]:
        """Get N most recent conversations (for context)"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        
        cursor = conn.execute("""
            SELECT conversation_id, title, intent, created_at, message_count
            FROM working_memory_conversations
            ORDER BY created_at DESC
            LIMIT ?
        """, (limit,))
        
        conversations = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return conversations
    
    def _get_active_conversation_count(self) -> int:
        """Get total conversation count (active + completed, not archived)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute("""
            SELECT COUNT(*) FROM working_memory_conversations
            WHERE status IN ('active', 'completed')
        """)
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    def _get_oldest_completed_conversation(self) -> Optional[str]:
        """Get oldest completed conversation for FIFO deletion"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute("""
            SELECT conversation_id FROM working_memory_conversations
            WHERE status = 'completed'
            ORDER BY created_at ASC
            LIMIT 1
        """)
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else None
    
    def _delete_conversation_with_pattern_extraction(self, conversation_id: str):
        """
        Delete conversation after extracting patterns to Tier 2
        
        This is the FIFO deletion + pattern learning integration point.
        Phase 2 will implement the pattern extraction logic.
        """
        # TODO Phase 2: Extract patterns before deletion
        # For now, mark as archived (soft delete)
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            UPDATE working_memory_conversations
            SET status = 'archived', pattern_extracted = TRUE
            WHERE conversation_id = ?
        """, (conversation_id,))
        conn.commit()
        conn.close()
```

**Success Criteria:**
- [ ] Start conversation creates UUID
- [ ] Add message increments count
- [ ] Complete conversation sets timestamp
- [ ] Get conversation returns all messages
- [ ] FIFO deletes oldest when at capacity
- [ ] Active conversation never deleted (even if oldest)

---

### Task 2: Entity Extractor
**File:** `CORTEX/src/tier1/entity_extractor.py`  
**Duration:** 2 hours  
**Tests:** 5 unit tests

**Description:**
Extract entities (files, classes, components, etc.) from conversations for context resolution.

**Implementation Details:**
```python
import re
from typing import List, Dict, Set

class EntityExtractor:
    """Extract entities from conversation for cross-conversation context"""
    
    # Entity patterns (regex)
    PATTERNS = {
        'file': r'`([a-zA-Z0-9_/\\.-]+\.(py|md|yaml|sql|ts|js|razor|cs|json))`',
        'component': r'([A-Z][a-zA-Z0-9]+(?:Component|Service|Engine|Manager|Handler))',
        'function': r'`([a-z_][a-z0-9_]+)\(\)`',
        'class': r'class\s+([A-Z][a-zA-Z0-9]+)',
        'rule': r'Rule\s*#(\d+)',
        'phase': r'Phase\s+(\d+)',
        'tier': r'Tier\s+(\d)',
    }
    
    def extract_entities(self, conversation_id: str, content: str) -> List[Dict]:
        """
        Extract all entities from message content
        
        Returns:
            List of {entity_type, entity_value, context}
        """
        entities = []
        
        for entity_type, pattern in self.PATTERNS.items():
            matches = re.findall(pattern, content, re.IGNORECASE)
            
            for match in matches:
                # Extract value (handle tuple matches from groups)
                value = match[0] if isinstance(match, tuple) else match
                
                # Get surrounding context (20 chars before/after)
                context = self._extract_context(content, value)
                
                entities.append({
                    'entity_type': entity_type,
                    'entity_value': value,
                    'context': context
                })
        
        return entities
    
    def _extract_context(self, content: str, value: str, 
                        window: int = 40) -> str:
        """Extract surrounding context for entity"""
        idx = content.find(value)
        if idx == -1:
            return ""
        
        start = max(0, idx - window)
        end = min(len(content), idx + len(value) + window)
        
        return content[start:end]
    
    def store_entities(self, db_path: str, conversation_id: str, 
                      entities: List[Dict]):
        """Store extracted entities in database"""
        import sqlite3
        from datetime import datetime
        
        conn = sqlite3.connect(db_path)
        
        for entity in entities:
            # Check if entity already exists for this conversation
            cursor = conn.execute("""
                SELECT id, mention_count FROM working_memory_entities
                WHERE conversation_id = ? AND entity_type = ? AND entity_value = ?
            """, (conversation_id, entity['entity_type'], entity['entity_value']))
            
            existing = cursor.fetchone()
            
            if existing:
                # Increment mention count
                conn.execute("""
                    UPDATE working_memory_entities
                    SET mention_count = mention_count + 1
                    WHERE id = ?
                """, (existing[0],))
            else:
                # Insert new entity
                conn.execute("""
                    INSERT INTO working_memory_entities
                    (conversation_id, entity_type, entity_value, context)
                    VALUES (?, ?, ?, ?)
                """, (conversation_id, entity['entity_type'], 
                     entity['entity_value'], entity['context']))
        
        conn.commit()
        conn.close()
    
    def get_entities_by_type(self, db_path: str, conversation_id: str,
                            entity_type: str) -> List[Dict]:
        """Get all entities of specific type from conversation"""
        import sqlite3
        
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        
        cursor = conn.execute("""
            SELECT entity_type, entity_value, context, mention_count
            FROM working_memory_entities
            WHERE conversation_id = ? AND entity_type = ?
            ORDER BY mention_count DESC
        """, (conversation_id, entity_type))
        
        entities = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return entities
    
    def find_entity_across_conversations(self, db_path: str, 
                                        entity_value: str) -> List[Dict]:
        """
        Find all conversations that mention this entity
        
        This enables "Make it purple" to find "FAB button" from earlier conversation
        """
        import sqlite3
        
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        
        cursor = conn.execute("""
            SELECT e.conversation_id, e.entity_type, e.entity_value, 
                   e.context, c.title, c.created_at
            FROM working_memory_entities e
            JOIN working_memory_conversations c ON e.conversation_id = c.conversation_id
            WHERE e.entity_value LIKE ?
            ORDER BY e.mention_count DESC, c.created_at DESC
            LIMIT 5
        """, (f'%{entity_value}%',))
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return results
```

**Success Criteria:**
- [ ] Files extracted from backtick syntax
- [ ] Components extracted (PascalCase names)
- [ ] Functions extracted (snake_case with parens)
- [ ] Rules extracted (Rule #N)
- [ ] Cross-conversation search works
- [ ] Context window captured correctly

---

### Task 3: Conversation Boundary Detector
**File:** `CORTEX/src/tier1/boundary_detector.py`  
**Duration:** 1.5 hours  
**Tests:** 4 unit tests

**Description:**
Detect when one conversation ends and another begins.

**Implementation Details:**
```python
from typing import Optional
from datetime import datetime, timedelta

class ConversationBoundaryDetector:
    """Detect conversation boundaries for automatic conversation splitting"""
    
    # Boundary detection rules
    IDLE_THRESHOLD_MINUTES = 30    # 30 min silence = new conversation
    INTENT_CHANGE_KEYWORDS = [
        'new feature', 'different topic', 'switch to',
        'now let\'s', 'moving on', 'next task'
    ]
    
    def __init__(self, working_memory: 'WorkingMemoryEngine'):
        self.wm = working_memory
    
    def should_start_new_conversation(self, last_message_time: datetime,
                                     current_message: str) -> bool:
        """
        Determine if new message should start a new conversation
        
        Triggers:
        1. Idle time > 30 minutes
        2. Explicit intent change keywords
        3. User explicitly requests new conversation
        """
        # Check idle time
        if self._is_idle_too_long(last_message_time):
            return True
        
        # Check for intent change keywords
        if self._contains_intent_change(current_message):
            return True
        
        # Check for explicit new conversation request
        if self._is_explicit_new_conversation(current_message):
            return True
        
        return False
    
    def _is_idle_too_long(self, last_message_time: datetime) -> bool:
        """Check if idle time exceeds threshold"""
        if not last_message_time:
            return True
        
        elapsed = datetime.now() - last_message_time
        return elapsed > timedelta(minutes=self.IDLE_THRESHOLD_MINUTES)
    
    def _contains_intent_change(self, message: str) -> bool:
        """Check for intent change keywords"""
        message_lower = message.lower()
        return any(keyword in message_lower 
                  for keyword in self.INTENT_CHANGE_KEYWORDS)
    
    def _is_explicit_new_conversation(self, message: str) -> bool:
        """Check for explicit new conversation request"""
        patterns = [
            'start new conversation',
            'begin new conversation',
            'new conversation',
            'fresh start'
        ]
        message_lower = message.lower()
        return any(pattern in message_lower for pattern in patterns)
    
    def detect_intent_from_message(self, message: str) -> str:
        """
        Detect intent from first message (for conversation title)
        
        Returns:
            PLAN, EXECUTE, TEST, VALIDATE, QUERY, etc.
        """
        message_lower = message.lower()
        
        # Intent patterns (ordered by priority)
        if any(word in message_lower for word in ['plan', 'design', 'create plan']):
            return 'PLAN'
        
        if any(word in message_lower for word in ['implement', 'build', 'create', 'add']):
            return 'EXECUTE'
        
        if any(word in message_lower for word in ['test', 'verify', 'validate']):
            return 'TEST'
        
        if any(word in message_lower for word in ['fix', 'debug', 'error', 'bug']):
            return 'FIX'
        
        if any(word in message_lower for word in ['explain', 'what is', 'how does']):
            return 'QUERY'
        
        if any(word in message_lower for word in ['review', 'analyze', 'check']):
            return 'VALIDATE'
        
        return 'GENERAL'
```

**Success Criteria:**
- [ ] 30+ minute idle triggers new conversation
- [ ] Intent change keywords detected
- [ ] Explicit new conversation requests honored
- [ ] Intent detection accurate (PLAN vs EXECUTE vs TEST)

---

### Task 4: FIFO Queue Manager
**File:** `CORTEX/src/tier1/fifo_queue.py`  
**Duration:** 1 hour  
**Tests:** 4 unit tests

**Description:**
Enforce Rule #11 (FIFO conversation queue with configurable capacity).

**Implementation Details:**
```python
from typing import Optional, List
import sqlite3

class FIFOQueueManager:
    """Manage FIFO queue for Tier 1 conversations (Rule #11)"""
    
    def __init__(self, db_path: str, capacity: int = 50):
        self.db_path = db_path
        self.capacity = capacity  # Configurable (1-100, default: 50)
    
    def enforce_capacity(self) -> Optional[str]:
        """
        Enforce FIFO capacity limit
        
        Returns:
            conversation_id of deleted conversation (if any)
        """
        conn = sqlite3.connect(self.db_path)
        
        # Count non-archived conversations
        cursor = conn.execute("""
            SELECT COUNT(*) FROM working_memory_conversations
            WHERE status IN ('active', 'completed')
        """)
        count = cursor.fetchone()[0]
        
        if count < self.capacity:
            conn.close()
            return None  # Under capacity
        
        # At capacity - find oldest completed conversation
        cursor = conn.execute("""
            SELECT conversation_id FROM working_memory_conversations
            WHERE status = 'completed'
            ORDER BY created_at ASC
            LIMIT 1
        """)
        
        oldest = cursor.fetchone()
        if not oldest:
            conn.close()
            return None  # No completed conversations to delete
        
        conversation_id = oldest[0]
        
        # Archive (soft delete) the conversation
        conn.execute("""
            UPDATE working_memory_conversations
            SET status = 'archived', pattern_extracted = FALSE
            WHERE conversation_id = ?
        """, (conversation_id,))
        
        conn.commit()
        conn.close()
        
        return conversation_id
    
    def get_queue_status(self) -> dict:
        """Get current queue statistics"""
        conn = sqlite3.connect(self.db_path)
        
        cursor = conn.execute("""
            SELECT status, COUNT(*) as count
            FROM working_memory_conversations
            GROUP BY status
        """)
        
        status_counts = {row[0]: row[1] for row in cursor.fetchall()}
        
        total = sum(status_counts.get(s, 0) for s in ['active', 'completed'])
        
        conn.close()
        
        return {
            'capacity': self.capacity,
            'total': total,
            'active': status_counts.get('active', 0),
            'completed': status_counts.get('completed', 0),
            'archived': status_counts.get('archived', 0),
            'available_slots': self.capacity - total,
            'utilization_percent': (total / self.capacity) * 100
        }
    
    def mark_for_pattern_extraction(self, conversation_id: str):
        """Mark conversation for Tier 2 pattern extraction before deletion"""
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            UPDATE working_memory_conversations
            SET pattern_extracted = TRUE
            WHERE conversation_id = ?
        """, (conversation_id,))
        conn.commit()
        conn.close()
```

**Success Criteria:**
- [ ] Capacity enforced (50 conversations max)
- [ ] Oldest completed conversation deleted first
- [ ] Active conversation never deleted
- [ ] Queue status accurate
- [ ] Pattern extraction flag set before deletion

---

### Task 5: Configuration System
**File:** `CORTEX/src/tier1/config.yaml` + `config_loader.py`  
**Duration:** 0.5 hours  
**Tests:** 2 unit tests

**Description:**
Configurable conversation capacity (Rule #11).

**Implementation Details:**

**config.yaml:**
```yaml
# Tier 1 - Working Memory Configuration
version: "1.0"
last_updated: "2025-11-05"

capacity:
  max_conversations: 50        # Default: 50 (Rule #11)
  min_conversations: 1         # Minimum allowed
  max_conversations_limit: 100 # Maximum allowed
  
boundary_detection:
  idle_threshold_minutes: 30   # Silence triggers new conversation
  enable_intent_detection: true
  
entity_extraction:
  enabled: true
  extract_files: true
  extract_components: true
  extract_functions: true
  extract_rules: true
  
performance:
  query_timeout_ms: 50         # Max query time
  message_batch_size: 100      # Batch inserts
```

**config_loader.py:**
```python
import yaml
from pathlib import Path

class Tier1Config:
    """Load Tier 1 configuration"""
    
    def __init__(self, config_path: str = "CORTEX/src/tier1/config.yaml"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
    
    def _load_config(self) -> dict:
        """Load YAML configuration"""
        if not self.config_path.exists():
            # Return defaults
            return self._get_defaults()
        
        with open(self.config_path) as f:
            return yaml.safe_load(f)
    
    def _get_defaults(self) -> dict:
        """Default configuration (if file missing)"""
        return {
            'capacity': {
                'max_conversations': 50,
                'min_conversations': 1,
                'max_conversations_limit': 100
            },
            'boundary_detection': {
                'idle_threshold_minutes': 30,
                'enable_intent_detection': True
            },
            'entity_extraction': {
                'enabled': True,
                'extract_files': True,
                'extract_components': True,
                'extract_functions': True,
                'extract_rules': True
            }
        }
    
    @property
    def max_conversations(self) -> int:
        """Get max conversation capacity"""
        return self.config['capacity']['max_conversations']
    
    @property
    def idle_threshold_minutes(self) -> int:
        """Get idle threshold for boundary detection"""
        return self.config['boundary_detection']['idle_threshold_minutes']
```

**Success Criteria:**
- [ ] Configuration loads from YAML
- [ ] Defaults provided if file missing
- [ ] Capacity configurable (1-100)
- [ ] All settings accessible via properties

---

### Task 6: Integration & Testing
**File:** `CORTEX/tests/tier1/` (multiple test files)  
**Duration:** 2 hours  
**Tests:** 22 unit + 4 integration tests

**Description:**
Comprehensive test coverage for all Tier 1 functionality.

**Test Structure:**
```
CORTEX/tests/tier1/
├── test_working_memory_engine.py      (6 tests)
├── test_entity_extractor.py           (5 tests)
├── test_boundary_detector.py          (4 tests)
├── test_fifo_queue.py                 (4 tests)
├── test_config_loader.py              (2 tests)
├── test_integration_end_to_end.py     (4 tests)
└── fixtures/
    ├── sample_conversations.json
    └── sample_messages.json
```

**Success Criteria:**
- [ ] All 22 unit tests passing
- [ ] All 4 integration tests passing
- [ ] Code coverage >90%
- [ ] Performance benchmarks met

---

## 📋 Test Plan (22 Unit + 4 Integration = 26 Total)

### Unit Tests (22 tests)

**WorkingMemoryEngine (6 tests):**
- [ ] `test_start_conversation()` - Creates UUID, stores metadata
- [ ] `test_add_message()` - Increments count, stores content
- [ ] `test_complete_conversation()` - Sets timestamp, outcome
- [ ] `test_get_conversation()` - Returns all messages in order
- [ ] `test_get_recent_conversations()` - Returns N most recent
- [ ] `test_fifo_deletion()` - Deletes oldest when at capacity

**EntityExtractor (5 tests):**
- [ ] `test_extract_file_entities()` - Finds files in backticks
- [ ] `test_extract_component_entities()` - Finds PascalCase components
- [ ] `test_extract_function_entities()` - Finds functions with ()
- [ ] `test_extract_rule_entities()` - Finds Rule #N references
- [ ] `test_find_entity_across_conversations()` - Cross-conversation search

**BoundaryDetector (4 tests):**
- [ ] `test_idle_threshold()` - 30+ minutes triggers new conversation
- [ ] `test_intent_change_keywords()` - Keywords detected
- [ ] `test_explicit_new_conversation()` - Explicit requests honored
- [ ] `test_detect_intent()` - PLAN vs EXECUTE vs TEST

**FIFOQueueManager (4 tests):**
- [ ] `test_enforce_capacity()` - Deletes oldest when at 50
- [ ] `test_active_protection()` - Active conversation never deleted
- [ ] `test_queue_status()` - Statistics accurate
- [ ] `test_pattern_extraction_flag()` - Flag set before deletion

**ConfigLoader (2 tests):**
- [ ] `test_load_config()` - YAML parsed correctly
- [ ] `test_defaults()` - Defaults used if file missing

**Performance (1 test):**
- [ ] `test_query_performance()` - All queries <50ms

### Integration Tests (4 tests)

**End-to-End Workflow:**
- [ ] `test_conversation_lifecycle()` - Start → Add messages → Complete → Query
- [ ] `test_fifo_with_entity_extraction()` - 51st conversation triggers FIFO + entity extraction
- [ ] `test_cross_conversation_context()` - "Make it purple" finds "FAB button"
- [ ] `test_boundary_detection_integration()` - Idle time auto-starts new conversation

---

## ⚡ Performance Benchmarks

```python
def test_conversation_query_performance():
    """Ensure conversation queries meet <50ms target"""
    import time
    
    engine = WorkingMemoryEngine()
    conversation_id = engine.start_conversation("Test", "PLAN")
    
    # Add 100 messages
    for i in range(100):
        engine.add_message(conversation_id, "user", f"Message {i}")
    
    # Measure query time
    start = time.perf_counter()
    conversation = engine.get_conversation(conversation_id)
    elapsed = (time.perf_counter() - start) * 1000  # ms
    
    assert elapsed < 50, f"Query took {elapsed}ms (target: <50ms)"
    assert len(conversation['messages']) == 100

def test_entity_extraction_performance():
    """Ensure entity extraction meets performance targets"""
    import time
    
    extractor = EntityExtractor()
    
    # Large message with many entities
    message = """
    Update `HostControlPanel.razor` and `noor-canvas.css` to add
    the FabButton component. Implement the handle_click() function
    following Rule #5 (TDD) in Phase 1.
    """
    
    start = time.perf_counter()
    entities = extractor.extract_entities("test-conv", message)
    elapsed = (time.perf_counter() - start) * 1000
    
    assert elapsed < 10, f"Extraction took {elapsed}ms (target: <10ms)"
    assert len(entities) >= 6  # Should find multiple entities

def test_fifo_performance():
    """Ensure FIFO deletion meets performance targets"""
    import time
    
    fifo = FIFOQueueManager(capacity=50)
    
    # Fill to capacity
    engine = WorkingMemoryEngine()
    for i in range(50):
        conv_id = engine.start_conversation(f"Conv {i}", "TEST")
        engine.complete_conversation(conv_id, "success")
    
    # Measure FIFO deletion time
    start = time.perf_counter()
    deleted = fifo.enforce_capacity()
    elapsed = (time.perf_counter() - start) * 1000
    
    assert elapsed < 20, f"FIFO deletion took {elapsed}ms (target: <20ms)"
    assert deleted is not None
```

**Targets:**
- Conversation query: <50ms (indexed)
- Entity extraction: <10ms per message
- FIFO deletion: <20ms
- Recent conversations: <30ms

---

## 🎯 Success Criteria

**Phase 1 complete when:**
- ✅ All 22 unit tests passing
- ✅ All 4 integration tests passing
- ✅ Conversation query <50ms (measured)
- ✅ FIFO queue works (50 conversation limit)
- ✅ Entity extraction accurate (files, components, etc.)
- ✅ Cross-conversation context works ("Make it purple")
- ✅ Configuration system functional
- ✅ Integration with Phase 0 (governance) validated
- ✅ Documentation complete
- ✅ **Holistic review passed** ⚠️ MANDATORY

---

## 📖 Documentation Deliverables

1. **API Documentation:** `CORTEX/docs/tier1-working-memory-api.md`
2. **Entity Patterns:** `CORTEX/docs/tier1-entity-patterns.md`
3. **FIFO Queue Design:** `CORTEX/docs/tier1-fifo-queue-design.md`
4. **Configuration Guide:** `CORTEX/docs/tier1-configuration.md`

---

## 🔍 MANDATORY: Holistic Review (Phase 1 Complete)

**⚠️ DO NOT PROCEED TO PHASE 2 UNTIL REVIEW COMPLETE**

### Review Checklist
Reference: `cortex-design/HOLISTIC-REVIEW-PROTOCOL.md` - Phase 1 Section

#### 1. Design Alignment ✅
- [ ] Does conversation tracking match KDS Tier 1 design?
- [ ] Is FIFO queue implemented per Rule #11 (configurable capacity)?
- [ ] Does entity extraction enable cross-conversation context?
- [ ] Is SQLite schema aligned with unified architecture?
- [ ] Does boundary detection work reliably?

#### 2. Implementation Quality ✅
- [ ] All 22 unit tests passing?
- [ ] All 4 integration tests passing?
- [ ] Code follows Python best practices?
- [ ] Type hints used consistently?
- [ ] Error handling comprehensive?
- [ ] Logging implemented?

#### 3. Performance Validation ✅
- [ ] Conversation query <50ms achieved?
- [ ] Entity extraction <10ms achieved?
- [ ] FIFO deletion <20ms achieved?
- [ ] Recent conversations <30ms achieved?

#### 4. Integration with Previous Phases ✅
- [ ] Phase 0 governance rules queryable from Tier 1?
- [ ] Database schema compatible?
- [ ] No conflicts with existing tables?

#### 5. Integration Readiness for Next Phase ✅
- [ ] Phase 2 can query conversations for pattern learning?
- [ ] Entity data ready for Tier 2 pattern extraction?
- [ ] FIFO deletion trigger ready for Tier 2 integration?
- [ ] No blocking issues for knowledge graph?

#### 6. Adjustments Needed
- [ ] Should entity extraction patterns be expanded?
- [ ] Should idle threshold be different?
- [ ] Should FIFO capacity default change from 50?

### Review Output Document
**Create:** `cortex-design/reviews/phase-1-review.md`

**Template:**
```markdown
# Phase 1 Review Report

**Date:** 2025-11-05
**Phase:** Tier 1 (Working Memory - Short-Term Memory)
**Status:** ✅ Pass / ⚠️ Pass with Adjustments / ❌ Fail

## Summary
[Assessment of Tier 1 implementation]

## Design Alignment
- ✅ FIFO queue implemented per Rule #11
- ✅ Entity extraction enables "Make it purple" use case
- ⚠️ Consider adding more entity patterns (git commits, test names)

## Implementation Quality
- ✅ All tests passing (22 unit, 4 integration)
- ✅ Code quality high, type hints consistent
- ✅ Configuration system works

## Performance Validation
- ✅ Conversation query: 42ms (target: <50ms) ✅
- ✅ Entity extraction: 7ms (target: <10ms) ✅
- ✅ FIFO deletion: 15ms (target: <20ms) ✅

## Integration Assessment
- ✅ Phase 0 rules accessible from Tier 1
- ✅ Database schema compatible
- ✅ Ready for Phase 2 pattern extraction

## Adjustments Required
1. Add git commit entity pattern (for Phase 3.5 integration)
2. Add test name entity pattern (for TDD workflow)
3. Expand entity context window from 40 to 60 chars

## Plan Updates
- Phase 2 plan: Adjust pattern extraction to use entity data
- Phase 4 plan: Add entity-based context resolution to agents

## Recommendation
⚠️ PASS WITH MINOR ADJUSTMENTS (implement above 3 items)
```

### Actions After Review

#### If Review PASSES ✅
1. **Commit review document:**
   ```bash
   git add cortex-design/reviews/phase-1-review.md
   git commit -m "docs(cortex): Phase 1 holistic review complete - PASS"
   ```

2. **Update next phase plan based on findings:**
   ```bash
   git add cortex-design/phase-plans/phase-2-knowledge-graph.md
   git commit -m "docs(cortex): Update Phase 2 plan with Phase 1 learnings"
   ```

3. **THEN proceed to Phase 2 implementation**

#### If Review REQUIRES ADJUSTMENTS ⚠️
1. Document minor issues in review report
2. Create quick fix checklist
3. Implement fixes (est. 30-45 minutes)
4. Re-run affected tests
5. Update review report with "PASS with adjustments"
6. Proceed to next phase

#### If Review FAILS ❌
1. Document critical issues
2. Create detailed fix plan
3. Implement fixes
4. Re-run complete test suite
5. Re-run review checklist
6. Only proceed when PASS achieved

### Success Metrics for Phase 1
- ✅ All tests passing (26 total)
- ✅ All benchmarks met (<50ms, <10ms, <20ms)
- ✅ FIFO queue working (50 capacity)
- ✅ Entity extraction accurate
- ✅ Review report created and approved
- ✅ Phase 2 plan updated with learnings

### Learning Capture
**Document in review:**
- What worked well? (Entity extraction patterns very effective)
- What was harder than expected? (Boundary detection edge cases)
- What assumptions were wrong? (Needed more entity types than planned)
- What should change in next phases? (Add more entity patterns upfront)

---

## 📊 Phase Timeline

| Day | Tasks | Hours | Cumulative |
|-----|-------|-------|------------|
| 1 | Task 1 (Engine) + Task 2 (Entities) | 4 | 4 |
| 2 | Task 3 (Boundary) + Task 4 (FIFO) + Task 5 (Config) | 3 | 7 |
| 3 | Task 6 (Tests) + Docs | 3 | 10 |
| 4 | **Holistic Review** + Adjustments | 1.5 | 11.5 |

**Total Estimated:** 8-10 hours implementation + 1 hour review + 0.5 hours adjustments = 9.5-11.5 hours

---

## ✅ Phase Completion Checklist

**Implementation:**
- [ ] All tasks complete
- [ ] All 22 unit tests written and passing
- [ ] All 4 integration tests written and passing
- [ ] All benchmarks met
- [ ] Documentation written
- [ ] Code reviewed

**Review:**
- [ ] Holistic review checklist completed
- [ ] Review report written
- [ ] Issues documented
- [ ] Adjustments (if any) implemented
- [ ] Phase 2 plan updated

**Commit:**
- [ ] Implementation committed
- [ ] Review report committed
- [ ] Updated plans committed

**Proceed:**
- [ ] Review status is PASS ✅
- [ ] Team notified of completion
- [ ] Phase 2 ready to start

---

**Status:** Ready for implementation  
**Next:** Phase 2 (Tier 2 - Knowledge Graph)  
**Estimated Completion:** 9.5-11.5 hours  
**⚠️ CRITICAL:** Complete holistic review before Phase 2!

---

## 🔗 Related Documents

- `HOLISTIC-REVIEW-PROTOCOL.md` - Complete review process
- `phase-0-governance.md` - Previous phase
- `phase-2-knowledge-graph.md` - Next phase
- `DESIGN-IMPROVEMENTS-SUMMARY.md` - Architecture decisions
- `unified-database-schema.sql` - Database schema
- `CORTEX-DNA.md` - Core design principles
