# Tier 1: Working Memory (STM) - Feature Inventory

**Purpose:** Document all conversation memory features from KDS for CORTEX migration  
**Source:** KDS v8 Tier 1 implementation  
**Date:** 2025-11-05

---

## Overview

Tier 1 is the **SHORT-TERM MEMORY** layer that solves Copilot's amnesia problem. It enables conversation continuity across sessions ("Make it purple" references work).

**Core Functionality:**
- Last 20 complete conversations preserved
- FIFO queue (conversation-level, not message-level)
- Entity extraction and cross-referencing
- Conversation boundary detection
- 3-layer auto-recording (71% automatic)

**Current Storage:** JSONL files (~70-200 KB)  
**CORTEX Target:** SQLite with FTS5 indexing (~50-150 KB, <50ms queries)

---

## Feature Breakdown

### 1. Conversation Storage

**Current Implementation:**

**File:** `kds-brain/conversation-history.jsonl`

**Features:**
1. ✅ **Append-only JSONL format**
   - One conversation per line
   - Chronological order
   - SHA256 checksums for integrity

2. ✅ **Complete conversation capture**
   ```jsonl
   {
     "conversation_id": "conv-2025-11-05-001",
     "timestamp": "2025-11-05T10:30:00Z",
     "topic": "Add purple button to HostControlPanel",
     "messages": [
       {"role": "user", "content": "Add a purple button..."},
       {"role": "assistant", "content": "I'll create that..."}
     ],
     "outcome": "success",
     "duration_seconds": 84,
     "files_modified": ["HostControlPanel.razor", "host-panel.css"],
     "tests_created": ["host-control-panel-purple-button.spec.ts"],
     "commits": ["feat(host-panel): Add purple action button"]
   }
   ```

3. ✅ **Metadata tracking**
   - Topic/intent
   - Outcome (success/failure/partial)
   - Duration
   - Files modified
   - Tests created
   - Git commits associated

4. ✅ **Entity extraction** (automatic)
   - File paths mentioned
   - Feature names
   - Component names
   - People referenced

**CORTEX Changes:**
- SQLite schema with indexed columns
- FTS5 for full-text search
- Automatic entity table (foreign keys)
- Conversation-message one-to-many relationship

---

### 2. FIFO Queue Management

**Current Implementation:**

**Rule:** Last 20 conversations preserved, oldest deleted when 21st starts

**Features:**
1. ✅ **Conversation-level FIFO** (not message-level)
   - Entire conversations are units
   - FIFO boundary = conversation start/end
   - No time-based expiration

2. ✅ **Active conversation protection**
   - Current conversation NEVER deleted
   - Even if it's the oldest

3. ✅ **Pattern extraction before deletion**
   - Deleted conversations analyzed
   - Patterns extracted to Tier 2 (LTM)
   - Details discarded, learnings preserved

4. ✅ **Manual reset available**
   ```bash
   #file:KDS/prompts/internal/clear-conversation.md
   ```

**Capacity Math:**
```
20 conversations × ~10 messages/conv = 200 total messages
Average message: 300 bytes
Total: 60 KB message content + 10 KB metadata = 70 KB
```

**CORTEX Changes:**
- Automatic FIFO enforcement (database trigger)
- Archive table for deleted conversations (searchable)
- Configurable capacity (default 20, max 50)

---

### 3. Conversation Context (Recent Messages)

**Current Implementation:**

**File:** `kds-brain/conversation-context.jsonl`

**Features:**
1. ✅ **Last 10 messages buffer**
   - Rolling window
   - Cross-conversation messages
   - Immediate context

2. ✅ **Message-level tracking**
   ```jsonl
   {
     "message_id": "msg-2025-11-05-001-004",
     "conversation_id": "conv-2025-11-05-001",
     "timestamp": "2025-11-05T10:32:15Z",
     "role": "user",
     "content": "Make it purple",
     "entities": {
       "color_reference": "purple",
       "implicit_reference": "FAB button (from msg-2025-11-05-001-002)"
     }
   }
   ```

3. ✅ **Entity linking**
   - "it" → Previous noun phrase
   - "that file" → Last file mentioned
   - "the button" → Component from earlier

4. ✅ **Context assembly for prompts**
   - Recent messages prepended to new requests
   - Copilot sees last 10 messages + new request
   - Seamless continuity

**CORTEX Changes:**
- SQLite view (auto-populated)
- Entity resolution table
- Configurable window size (default 10)

---

### 4. Conversation Boundary Detection

**Current Implementation:**

**Logic:** Automatic detection of conversation start/end

**Boundary Triggers:**
1. ✅ **Start triggers:**
   - New feature request (PLAN intent)
   - Explicit "start new conversation"
   - > 2 hours since last message
   - Context switch detected (topic change)

2. ✅ **End triggers:**
   - Task completion (DoD validated)
   - Explicit "end conversation"
   - User says "done" or "finished"
   - > 2 hours idle

3. ✅ **Boundary markers**
   ```jsonl
   {
     "boundary_event": "conversation_start",
     "timestamp": "2025-11-05T10:30:00Z",
     "trigger": "plan_intent",
     "previous_conversation_id": "conv-2025-11-04-003"
   }
   ```

**CORTEX Changes:**
- Machine learning boundary detection (optional)
- Configurable idle timeout (default 2 hours)
- Explicit boundary commands

---

### 5. Entity Extraction

**Current Implementation:**

**Automatic extraction from messages:**

**Entity Types:**
1. ✅ **File paths**
   - Example: `HostControlPanel.razor`
   - Normalized: Absolute → Relative
   - Indexed: Quick retrieval

2. ✅ **Component names**
   - Example: `purple action button`
   - Canonical: Lowercase, stemmed

3. ✅ **Feature names**
   - Example: `invoice export`
   - Variations: "export invoices", "invoice PDF generation"

4. ✅ **People/roles**
   - Example: `user`, `host`, `participant`

5. ✅ **Actions/intents**
   - Example: `add`, `fix`, `test`, `validate`

6. ✅ **Colors/styles**
   - Example: `purple`, `#9333EA`, `hover effect`

**Extraction Process:**
```
Message received
    ↓
NLP tokenization (basic regex)
    ↓
Pattern matching:
  - File paths: .cs, .razor, .ts, .css, etc.
  - Colors: Hex codes, color names
  - Actions: Verb detection
  - Components: Noun phrases
    ↓
Entity table insert:
  {
    conversation_id: "conv-2025-11-05-001",
    entity_type: "file",
    entity_value: "HostControlPanel.razor",
    first_mentioned: "msg-2025-11-05-001-002",
    mention_count: 3
  }
```

**CORTEX Changes:**
- Enhanced NLP (spaCy or simple ML)
- Entity disambiguation
- Canonical name resolution
- Cross-conversation entity tracking

---

### 6. Cross-Conversation Linking

**Current Implementation:**

**Features:**
1. ✅ **Topic similarity detection**
   - "Add share button" (conv-001)
   - "Add purple button" (conv-008)
   - Similarity: 85% (same file, same pattern)

2. ✅ **File-based linking**
   - All conversations that modified `HostControlPanel.razor`
   - Quick lookup: "What did we do in this file?"

3. ✅ **Pattern-based linking**
   - All conversations using "button_addition_test_first" workflow
   - Reuse previous decisions

4. ✅ **Outcome-based filtering**
   - All successful conversations
   - All failed conversations (learn from mistakes)

**CORTEX Changes:**
- Vector similarity search (embeddings)
- Automatic clustering (similar conversations)
- Visual conversation graph (optional dashboard)

---

### 7. Auto-Recording System (3 Layers)

**Current Implementation:**

**Target:** 71%+ auto-recording rate

**Layer 1: GitHub Copilot Chat Import**

**Script:** `scripts/import-copilot-chats.ps1`

**Features:**
1. ✅ **Automatic import from VS Code**
   - Location: `%APPDATA%\Code\User\globalStorage\github.copilot-chat\`
   - Format: JSON chat logs
   - Parse and convert to KDS format

2. ✅ **Deduplication**
   - Skip already-imported conversations
   - Hash-based duplicate detection

3. ✅ **Metadata enhancement**
   - Extract file paths from messages
   - Detect intent automatically
   - Classify outcome (best-effort)

**Current Auto-Rate:** ~50% (manual trigger needed)

**Layer 2: Session Completion Auto-Record**

**Script:** `scripts/record-session-conversation.ps1`

**Features:**
1. ✅ **Triggered on session end**
   - When DoD validated
   - When user says "done"
   - After commit handler runs

2. ✅ **Session → Conversation mapping**
   - Session ID → Conversation ID
   - Task list → Message sequence
   - Outcome → Success/failure

3. ✅ **Automatic metadata**
   - Files modified (from git)
   - Tests created (from session state)
   - Duration (session start/end)

**Current Auto-Rate:** ~15% (sessions tracked inconsistently)

**Layer 3: Manual Recording**

**Script:** `scripts/record-conversation.ps1`

**Features:**
1. ✅ **Interactive prompts**
   - Topic/summary
   - Key decisions
   - Outcome
   - Files affected

2. ✅ **Used for critical conversations**
   - Architectural decisions
   - Major feature completions
   - Problem-solving breakthroughs

**Current Usage:** ~6% (manual fallback)

**Combined Auto-Rate:**
```
Layer 1: 50% × 0.70 (trigger rate) = 35%
Layer 2: 15% × 0.90 (capture rate) = 13.5%
Layer 3: 6% (manual)
Total: 54.5% actual (target 71%)
```

**CORTEX Changes:**
- Layer 1: VS Code extension (automatic, 90%+ capture)
- Layer 2: Webhook-based (100% session capture)
- Layer 3: CLI command (streamlined UX)
- Target: 85%+ auto-recording

---

### 8. Conversation Search & Retrieval

**Current Implementation:**

**Features:**
1. ✅ **Text search**
   ```bash
   # Search conversations by keyword
   Get-Content kds-brain/conversation-history.jsonl | 
     Select-String "purple button"
   ```

2. ✅ **Date range filtering**
   ```bash
   # Conversations in last 7 days
   Get-Content kds-brain/conversation-history.jsonl | 
     Where-Object { $_.timestamp -gt (Get-Date).AddDays(-7) }
   ```

3. ✅ **Outcome filtering**
   ```bash
   # All successful conversations
   Get-Content kds-brain/conversation-history.jsonl | 
     Where-Object { $_.outcome -eq "success" }
   ```

4. ✅ **File-based retrieval**
   ```bash
   # All conversations that modified HostControlPanel.razor
   Get-Content kds-brain/conversation-history.jsonl | 
     Where-Object { $_.files_modified -contains "HostControlPanel.razor" }
   ```

**Performance:**
- Small dataset (<20 convs): <50ms
- JSONL parsing: Sequential scan (slow for large datasets)

**CORTEX Changes:**
- SQLite indexed queries (<10ms)
- FTS5 full-text search
- Complex filters (AND/OR/NOT)
- Semantic search (optional, embeddings)

---

### 9. Context Assembly for Intent Router

**Current Implementation:**

**Purpose:** Provide conversation context to Intent Router for accurate routing

**Process:**
```
User message received: "Make it purple"
    ↓
Query conversation-context.jsonl (last 10 messages)
    ↓
Find entity: "it" → "FAB button" (from msg-001-002)
    ↓
Assemble context:
  Recent messages: [last 10]
  Current message: "Make it purple"
  Resolved entities: {"it": "FAB button"}
    ↓
Pass to Intent Router
    ↓
Router decision: EXECUTE (modify FAB button)
```

**Features:**
1. ✅ **Entity resolution**
   - Pronouns → Nouns
   - Implicit refs → Explicit refs

2. ✅ **Temporal context**
   - "Earlier we discussed X"
   - "From the last conversation..."

3. ✅ **File context**
   - "In that file..." → Resolves to last file mentioned

**CORTEX Changes:**
- Coreference resolution (advanced NLP)
- Multi-turn dialogue state tracking
- Context window tuning (10 vs 20 messages)

---

### 10. Monitoring & Health

**Current Implementation:**

**Script:** `scripts/monitor-tier1-health.ps1`

**Metrics:**
1. ✅ **Capacity tracking**
   - Current: 14/20 conversations
   - Utilization: 70%
   - Oldest conversation: 12 days ago

2. ✅ **FIFO health**
   - Deletions in last 7 days: 2
   - Patterns extracted: 8
   - Zero data loss

3. ✅ **Context buffer health**
   - Messages in buffer: 10/10 (full)
   - Oldest message: 2 hours ago
   - Entity resolution rate: 94%

4. ✅ **Auto-recording stats**
   - Layer 1: 35% capture
   - Layer 2: 13.5% capture
   - Layer 3: 6% capture
   - **Total: 54.5%** (target 71%)

5. ✅ **Quality metrics**
   - Entity extraction rate: 92%
   - Boundary detection accuracy: 88%
   - Duplicate prevention: 100%

**Report Output:**
```
═══════════════════════════════════════════════
📊 Tier 1 (Working Memory) Health Report
═══════════════════════════════════════════════

Capacity:
  Conversations: 14/20 (70% full)
  Messages (buffer): 10/10 (100% full)
  Storage: 127 KB / 200 KB target

FIFO Status:
  Oldest conversation: 12 days ago
  Deletions (last 7 days): 2
  Patterns extracted: 8
  
Auto-Recording:
  Layer 1 (Copilot): 35% ⚠️ (target 50%)
  Layer 2 (Sessions): 13.5% ⚠️ (target 30%)
  Layer 3 (Manual): 6% ✅
  TOTAL: 54.5% ⚠️ (target 71%)

Quality:
  Entity extraction: 92% ✅
  Boundary detection: 88% ✅
  Duplicate prevention: 100% ✅
  Entity resolution: 94% ✅

Recommendations:
  - Improve Layer 1 auto-capture (install VS Code extension)
  - Enable Layer 2 session webhooks
  - Capacity healthy (14/20)
  
Status: ⚠️ NEEDS IMPROVEMENT (auto-recording below target)
═══════════════════════════════════════════════
```

**CORTEX Changes:**
- Real-time dashboard metrics
- Automatic alerts (Slack/email)
- Self-healing (auto-fix common issues)

---

## Storage Schema (Current JSONL)

### conversation-history.jsonl

**Schema:**
```jsonl
{
  "conversation_id": "conv-2025-11-05-001",
  "timestamp_start": "2025-11-05T10:30:00Z",
  "timestamp_end": "2025-11-05T10:31:24Z",
  "duration_seconds": 84,
  "topic": "Add purple button to HostControlPanel",
  "intent": "PLAN",
  "messages": [
    {
      "message_id": "msg-2025-11-05-001-001",
      "timestamp": "2025-11-05T10:30:00Z",
      "role": "user",
      "content": "Add a purple button to HostControlPanel.razor"
    },
    {
      "message_id": "msg-2025-11-05-001-002",
      "timestamp": "2025-11-05T10:30:23Z",
      "role": "assistant",
      "content": "I'll create that with TDD. Starting with test..."
    }
  ],
  "outcome": "success",
  "files_modified": [
    "HostControlPanel.razor",
    "host-panel.css"
  ],
  "tests_created": [
    "Tests/UI/host-control-panel-purple-button.spec.ts"
  ],
  "commits": [
    {
      "sha": "abc123...",
      "message": "feat(host-panel): Add purple action button"
    }
  ],
  "entities": {
    "files": ["HostControlPanel.razor", "host-panel.css"],
    "components": ["purple button", "host control panel"],
    "colors": ["purple", "#9333EA"],
    "actions": ["add", "create", "test"]
  },
  "learnings": [
    "Element ID pattern: #host-panel-purple-btn",
    "Test-first reduced delivery time to 84 seconds"
  ],
  "sha256": "d4f7e3c2a1b9..." // Integrity check
}
```

### conversation-context.jsonl

**Schema:**
```jsonl
{
  "message_id": "msg-2025-11-05-001-004",
  "conversation_id": "conv-2025-11-05-001",
  "timestamp": "2025-11-05T10:32:15Z",
  "role": "user",
  "content": "Make it purple",
  "entities_raw": {
    "implicit_reference": "it"
  },
  "entities_resolved": {
    "it": {
      "type": "component",
      "value": "FAB button",
      "source": "msg-2025-11-05-001-002",
      "confidence": 0.95
    }
  },
  "in_context_window": true,
  "position_in_window": 4
}
```

---

## CORTEX SQLite Schema (Target)

### Tables

**1. conversations**
```sql
CREATE TABLE conversations (
  conversation_id TEXT PRIMARY KEY,
  timestamp_start DATETIME NOT NULL,
  timestamp_end DATETIME,
  duration_seconds INTEGER,
  topic TEXT NOT NULL,
  intent TEXT,
  outcome TEXT CHECK(outcome IN ('success', 'failure', 'partial', 'ongoing')),
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  deleted_at DATETIME, -- For FIFO archival
  
  -- Indexes for fast queries
  CONSTRAINT fk_intent FOREIGN KEY (intent) REFERENCES intents(intent_id)
);

CREATE INDEX idx_conversations_timestamp ON conversations(timestamp_start DESC);
CREATE INDEX idx_conversations_outcome ON conversations(outcome);
CREATE INDEX idx_conversations_topic ON conversations(topic);
```

**2. messages**
```sql
CREATE TABLE messages (
  message_id TEXT PRIMARY KEY,
  conversation_id TEXT NOT NULL,
  timestamp DATETIME NOT NULL,
  role TEXT CHECK(role IN ('user', 'assistant', 'system')),
  content TEXT NOT NULL,
  in_context_window BOOLEAN DEFAULT 0,
  
  FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id) ON DELETE CASCADE
);

CREATE INDEX idx_messages_conversation ON messages(conversation_id);
CREATE INDEX idx_messages_timestamp ON messages(timestamp DESC);
CREATE INDEX idx_messages_context_window ON messages(in_context_window, timestamp DESC);

-- Full-text search on message content
CREATE VIRTUAL TABLE messages_fts USING fts5(
  message_id UNINDEXED,
  content,
  content=messages,
  content_rowid=rowid
);
```

**3. entities**
```sql
CREATE TABLE entities (
  entity_id INTEGER PRIMARY KEY AUTOINCREMENT,
  conversation_id TEXT NOT NULL,
  message_id TEXT NOT NULL,
  entity_type TEXT NOT NULL, -- file, component, color, action, person
  entity_value TEXT NOT NULL,
  normalized_value TEXT, -- Canonical form
  confidence REAL DEFAULT 1.0,
  mention_count INTEGER DEFAULT 1,
  first_mentioned DATETIME,
  last_mentioned DATETIME,
  
  FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id) ON DELETE CASCADE,
  FOREIGN KEY (message_id) REFERENCES messages(message_id) ON DELETE CASCADE
);

CREATE INDEX idx_entities_conversation ON entities(conversation_id);
CREATE INDEX idx_entities_type ON entities(entity_type);
CREATE INDEX idx_entities_value ON entities(normalized_value);
```

**4. conversation_files**
```sql
CREATE TABLE conversation_files (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  conversation_id TEXT NOT NULL,
  file_path TEXT NOT NULL,
  operation TEXT, -- created, modified, deleted, read
  
  FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id) ON DELETE CASCADE
);

CREATE INDEX idx_conv_files_conversation ON conversation_files(conversation_id);
CREATE INDEX idx_conv_files_path ON conversation_files(file_path);
```

**5. conversation_commits**
```sql
CREATE TABLE conversation_commits (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  conversation_id TEXT NOT NULL,
  commit_sha TEXT NOT NULL,
  commit_message TEXT,
  commit_timestamp DATETIME,
  
  FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id) ON DELETE CASCADE
);

CREATE INDEX idx_conv_commits_conversation ON conversation_commits(conversation_id);
CREATE INDEX idx_conv_commits_sha ON conversation_commits(commit_sha);
```

**6. conversation_tests**
```sql
CREATE TABLE conversation_tests (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  conversation_id TEXT NOT NULL,
  test_file TEXT NOT NULL,
  test_status TEXT CHECK(test_status IN ('created', 'passing', 'failing', 'skipped')),
  
  FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id) ON DELETE CASCADE
);

CREATE INDEX idx_conv_tests_conversation ON conversation_tests(conversation_id);
```

**7. entity_resolutions**
```sql
CREATE TABLE entity_resolutions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  message_id TEXT NOT NULL,
  implicit_ref TEXT NOT NULL, -- "it", "that file", "the button"
  resolved_entity_id INTEGER NOT NULL,
  confidence REAL DEFAULT 1.0,
  
  FOREIGN KEY (message_id) REFERENCES messages(message_id) ON DELETE CASCADE,
  FOREIGN KEY (resolved_entity_id) REFERENCES entities(entity_id) ON DELETE CASCADE
);

CREATE INDEX idx_resolutions_message ON entity_resolutions(message_id);
```

### Views

**1. context_window (last 10 messages)**
```sql
CREATE VIEW context_window AS
SELECT *
FROM messages
WHERE in_context_window = 1
ORDER BY timestamp DESC
LIMIT 10;
```

**2. active_conversations (not deleted)**
```sql
CREATE VIEW active_conversations AS
SELECT *
FROM conversations
WHERE deleted_at IS NULL
ORDER BY timestamp_start DESC;
```

**3. fifo_candidates (oldest conversations for deletion)**
```sql
CREATE VIEW fifo_candidates AS
SELECT *
FROM conversations
WHERE deleted_at IS NULL
  AND outcome != 'ongoing' -- Don't delete active
ORDER BY timestamp_start ASC;
```

### Triggers

**1. FIFO enforcement**
```sql
CREATE TRIGGER enforce_fifo
AFTER INSERT ON conversations
BEGIN
  -- Check if we exceed 20 conversations
  DELETE FROM conversations
  WHERE conversation_id IN (
    SELECT conversation_id
    FROM fifo_candidates
    LIMIT MAX(0, (SELECT COUNT(*) FROM active_conversations) - 20)
  );
END;
```

**2. Context window maintenance**
```sql
CREATE TRIGGER update_context_window
AFTER INSERT ON messages
BEGIN
  -- Mark all messages as not in window
  UPDATE messages SET in_context_window = 0;
  
  -- Mark last 10 as in window
  UPDATE messages
  SET in_context_window = 1
  WHERE message_id IN (
    SELECT message_id
    FROM messages
    ORDER BY timestamp DESC
    LIMIT 10
  );
END;
```

**3. Entity mention count**
```sql
CREATE TRIGGER increment_entity_mentions
AFTER INSERT ON entities
WHEN NEW.entity_value IN (SELECT entity_value FROM entities WHERE entity_id != NEW.entity_id)
BEGIN
  UPDATE entities
  SET mention_count = mention_count + 1,
      last_mentioned = NEW.first_mentioned
  WHERE entity_value = NEW.entity_value
    AND entity_id != NEW.entity_id;
    
  DELETE FROM entities WHERE entity_id = NEW.entity_id;
END;
```

---

## Performance Targets

| Metric | KDS (JSONL) | CORTEX (SQLite) | Improvement |
|--------|-------------|-----------------|-------------|
| **Query latency** | 500-1000ms | <50ms | 10-20x faster |
| **Full-text search** | N/A | <100ms | New capability |
| **Entity resolution** | 200-400ms | <20ms | 10-20x faster |
| **Conversation retrieval** | 300-600ms | <10ms | 30-60x faster |
| **FIFO deletion** | Manual | Automatic | Instant |
| **Storage size** | 127 KB (14 convs) | ~90 KB (14 convs) | 30% smaller |
| **Backup/restore** | 5-10 sec | <1 sec | 5-10x faster |

---

## Migration Checklist

**Tier 1 complete when:**

### Core Features
- [ ] SQLite schema created and tested
- [ ] FIFO queue automatic enforcement
- [ ] Context window (last 10 messages) view
- [ ] Entity extraction pipeline
- [ ] Entity resolution (pronouns, implicit refs)
- [ ] Conversation boundary detection
- [ ] Full-text search (FTS5)

### Data Migration
- [ ] JSONL → SQLite conversion script
- [ ] Zero data loss validation
- [ ] Entity re-extraction from migrated conversations
- [ ] Integrity checks (SHA256 verification)

### Auto-Recording
- [ ] Layer 1: VS Code extension (90%+ capture)
- [ ] Layer 2: Webhook integration (100% sessions)
- [ ] Layer 3: CLI command (streamlined)
- [ ] Target 85%+ auto-recording rate

### Monitoring
- [ ] Real-time health dashboard
- [ ] Automatic capacity alerts
- [ ] FIFO activity logging
- [ ] Auto-recording rate tracking

### Testing
- [ ] 50 unit tests (CRUD, FIFO, entity extraction)
- [ ] 8 integration tests (cross-table queries)
- [ ] Performance benchmarks (<50ms queries)
- [ ] Data migration tests (lossless verification)

### Documentation
- [ ] SQLite schema documentation
- [ ] API reference (queries, inserts, updates)
- [ ] Migration guide (JSONL → SQLite)
- [ ] Troubleshooting guide

---

## Test Requirements

**Unit Tests (50 total):**

1. **Conversation CRUD** (10 tests)
   - Create conversation
   - Read conversation by ID
   - Update conversation outcome
   - Delete conversation (soft delete)
   - List all active conversations

2. **FIFO Queue** (8 tests)
   - Insert 21st conversation → Oldest deleted
   - Active conversation protection
   - Pattern extraction before deletion
   - FIFO trigger validation

3. **Messages** (8 tests)
   - Insert message
   - Retrieve messages by conversation
   - Context window population
   - Message full-text search

4. **Entity Extraction** (12 tests)
   - Extract file paths
   - Extract components
   - Extract colors
   - Extract actions
   - Normalize entities
   - Increment mention count

5. **Entity Resolution** (6 tests)
   - Resolve "it" to noun
   - Resolve "that file" to file path
   - Multi-hop resolution
   - Confidence scoring

6. **Conversation Boundaries** (6 tests)
   - Detect start trigger (PLAN intent)
   - Detect end trigger (DoD validated)
   - Idle timeout boundary
   - Manual boundary commands

**Integration Tests (8 total):**

1. **Cross-table queries** (3 tests)
   - Get all conversations for a file
   - Get all files modified in last 7 days
   - Get entity mention timeline

2. **Full workflow** (2 tests)
   - Complete conversation lifecycle (start → messages → end → FIFO)
   - Entity extraction → Resolution → Search

3. **Auto-recording** (3 tests)
   - Layer 1 import (Copilot Chat)
   - Layer 2 session capture
   - Layer 3 manual recording

---

## Files to Create

**CORTEX Structure:**

```
cortex-brain/
├── tier1-working-memory/
│   ├── conversations.db        # SQLite database
│   ├── schema.sql              # Schema definition
│   ├── migrations/             # Schema migrations
│   │   ├── 001_initial.sql
│   │   └── 002_add_fts5.sql
│   └── backups/                # Automatic backups
│       └── conversations-2025-11-05.db

cortex-scripts/
├── brain/
│   ├── migrate-jsonl-to-sqlite.ts   # One-time migration
│   ├── tier1-health-check.ts        # Health monitoring
│   └── backup-tier1.ts               # Backup automation

cortex-agents/
├── internal/
│   ├── conversation-manager.md      # Conversation CRUD
│   ├── entity-extractor.md          # Entity extraction
│   └── entity-resolver.md           # Entity resolution

cortex-tests/
├── unit/
│   ├── tier1-conversations.test.ts
│   ├── tier1-fifo.test.ts
│   ├── tier1-entities.test.ts
│   └── tier1-boundaries.test.ts
└── integration/
    ├── tier1-workflow.test.ts
    └── tier1-auto-recording.test.ts
```

---

## Success Criteria

**Tier 1 migration successful when:**

### Functional Parity
- ✅ All KDS conversation features work in CORTEX
- ✅ Zero data loss during migration
- ✅ FIFO queue automatic and reliable
- ✅ Context window updates in real-time
- ✅ Entity extraction ≥ 92% accuracy
- ✅ Entity resolution ≥ 94% accuracy

### Performance Gains
- ✅ Query latency <50ms (10-20x faster)
- ✅ Full-text search <100ms
- ✅ Storage 30% smaller
- ✅ FIFO enforcement automatic

### Quality Improvements
- ✅ 85%+ auto-recording rate (vs 54.5%)
- ✅ Real-time monitoring dashboard
- ✅ 50 unit + 8 integration tests passing
- ✅ 100% schema migration coverage

---

**Status:** Feature inventory complete  
**Next:** Tier 2 (Long-Term Knowledge) feature extraction  
**Estimated Implementation Time:** 2-3 days (Phase 1)
