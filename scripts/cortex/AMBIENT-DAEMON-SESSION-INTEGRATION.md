# Ambient Daemon - Session Correlation Integration

**Updated:** 2025-11-13  
**Feature:** CORTEX 3.0 Session-Ambient Correlation  
**Status:** ✅ INTEGRATED

---

## Overview

The ambient capture daemon now automatically correlates all captured events (file changes, terminal commands, git operations) with active development sessions and conversations.

**Benefits:**
- Complete development narratives combining conversations + actual activity
- Precise event tagging with conversation_id when conversation is active
- Session-level event queries for "What happened in this session?"
- Automatic context for "continue" commands

---

## How It Works

### Automatic Session Detection

When the daemon captures events, it:

1. **Detects Active Session** - Finds or creates workspace session
2. **Tags with Conversation** - Links to active conversation (if any)
3. **Logs to Tier 1** - Stores in `ambient_events` table
4. **Enables Queries** - Session and conversation event retrieval

### Event Flow

```
File Change → Debouncer → _write_to_tier1() → WorkingMemory.log_ambient_event()
                                                        ↓
                                              ambient_events table
                                                        ↓
                                    Session/Conversation Correlation
```

---

## Integration Points

### Modified Function: `_write_to_tier1()`

**Location:** `scripts/cortex/auto_capture_daemon.py` line 825

**Changes:**
- Uses `tier1-working-memory.db` (new CORTEX 3.0 location)
- Calls `session_manager.get_active_session()` to find workspace session
- Calls `log_ambient_event()` instead of `store_message()`
- Tags events with `conversation_id` when conversation active
- Classifies event types (file_change, terminal_command, git_operation)

**New Helper:** `_classify_event_type()`
- Categorizes events for proper ambient_events.event_type field

---

## Usage Examples

### Querying Session Events

```python
from src.tier1.working_memory import WorkingMemory

wm = WorkingMemory()

# Get all ambient events for a session
events = wm.get_session_events("session_20251113_140000_1234")

# Filter by event type
file_changes = wm.get_session_events(
    "session_20251113_140000_1234", 
    event_type="file_change"
)

# Filter by score (high-priority events only)
critical_events = wm.get_session_events(
    "session_20251113_140000_1234",
    min_score=80
)
```

### Getting Conversation-Specific Events

```python
# What files changed during this specific conversation?
events = wm.get_conversation_events("conv_20251113_140000_a1b2c3")

for event in events:
    print(f"{event['summary']} - {event['file_path']}")
```

### Generating Development Narratives

```python
# Create complete story: conversations + ambient activity
narrative = wm.generate_session_narrative("session_20251113_140000_1234")

print(narrative)
# Output: Markdown document with:
# - Session info (workspace, duration, conversation count)
# - All conversations with their events
# - All session activity grouped by pattern
```

---

## Database Schema

### Ambient Events Table

```sql
CREATE TABLE ambient_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,           -- Links to sessions table
    conversation_id TEXT,               -- Links to active conversation (nullable)
    event_type TEXT NOT NULL,           -- file_change, terminal_command, git_operation, vscode_state
    file_path TEXT,                     -- Affected file (if applicable)
    pattern TEXT,                       -- FEATURE, BUGFIX, REFACTOR, TESTING, CONFIG, DOCS
    score INTEGER,                      -- Activity score 0-100
    summary TEXT,                       -- Natural language summary
    timestamp TEXT NOT NULL,
    metadata TEXT,                      -- JSON metadata
    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
);
```

**Indexes:**
- `idx_ambient_session` - Fast session queries
- `idx_ambient_conversation` - Fast conversation queries
- `idx_ambient_timestamp` - Chronological ordering

---

## Configuration

**Database Path:** `cortex-brain/tier1-working-memory.db`

Set via environment variable (optional):
```bash
export CORTEX_BRAIN_PATH=/path/to/cortex-brain
```

**Session Idle Threshold:** 2 hours (configurable in `cortex.config.json`)

---

## Testing

**Integration Test:** 36/36 tests passing ✅

Run tests:
```bash
pytest tests/tier1/test_session_manager.py -v
pytest tests/tier1/test_lifecycle_manager.py -v
pytest tests/tier1/test_session_correlation.py -v
```

**Manual Test:**
1. Start ambient daemon: `python scripts/cortex/auto_capture_daemon.py`
2. Make file changes in workspace
3. Query session events: `wm.get_session_events(session_id)`
4. Verify events logged with correct session_id

---

## What's Next

### Future Enhancements

1. **Real-Time Conversation Tagging**
   - Detect active conversation from VS Code extension
   - Tag events with conversation_id in real-time
   
2. **Smart Pattern Detection**
   - Improve pattern classification accuracy
   - Learn patterns from successful workflows
   
3. **Narrative Intelligence**
   - Auto-generate narrative summaries on session end
   - Identify incomplete workflows (started but not finished)

---

## Migration Notes

**Breaking Changes:** None - fully backward compatible

**Old Approach:**
- Created separate "ambient sessions" daily
- Stored events as messages in conversations
- No correlation with user conversations

**New Approach (CORTEX 3.0):**
- Uses actual workspace sessions
- Stores events in dedicated `ambient_events` table
- Links to user conversations when active
- Enables complete development narratives

**Migration:** Existing ambient data preserved. New events use new schema.

---

**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Proprietary - See LICENSE file for terms  
**Repository:** https://github.com/asifhussain60/CORTEX

**Last Updated:** 2025-11-13 14:56:00 PST
