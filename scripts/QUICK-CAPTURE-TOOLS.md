# CORTEX Phase 4: Quick Capture CLI Tools

**Phase:** Phase 4 - Advanced CLI & Integration  
**Created:** November 9, 2025  
**Status:** Implemented  

## Overview

Quick capture tools designed for <5 second context capture to improve "continue" command success rate from 60% → 90%.

## Tools

### 1. `cortex-capture` - General Purpose Capture

Fast context capture for any type of work.

**Usage:**
```bash
# Quick capture
cortex-capture "Added purple button to UI"

# With type
cortex-capture "Fixed parser bug" --type bug

# With tags
cortex-capture "Refactored auth module" --type refactor --tags auth,security

# Interactive mode
cortex-capture --interactive
```

**Features:**
- ✅ <5 second capture time
- ✅ Auto-detects git context (branch, changed files)
- ✅ Stores in Tier 1 (Working Memory)
- ✅ Extracts patterns for Tier 2 (Knowledge Graph)
- ✅ Minimal user input required

---

### 2. `cortex-bug` - Template-Based Bug Capture

Structured bug reporting with templates.

**Usage:**
```bash
# Quick bug report
cortex-bug "Null pointer in parser.py"

# With severity
cortex-bug "Login fails" --severity critical

# With error message
cortex-bug "Database connection error" --error "ConnectionRefusedError: [Errno 111]"

# Interactive mode
cortex-bug --interactive
```

**Features:**
- ✅ Template-based capture (description, severity, files, errors)
- ✅ Auto-detects affected files
- ✅ Severity levels: low, medium, high, critical
- ✅ Captures error messages
- ✅ Fast <5 second capture

**Template Structure:**
```python
{
    "description": "Bug description",
    "steps_to_reproduce": [],
    "expected_behavior": "",
    "actual_behavior": "",
    "error_messages": [],
    "files_affected": [],
    "severity": "medium",
    "status": "open"
}
```

---

### 3. `cortex-feature` - Smart Context Feature Logging

Feature capture with intelligent context detection.

**Usage:**
```bash
# Quick feature log
cortex-feature "Added user authentication"

# With tests flag
cortex-feature "Implemented payment system" --tests

# With components
cortex-feature "Built dashboard" --components "ui,api,database"

# Interactive mode
cortex-feature --interactive
```

**Features:**
- ✅ Smart context detection (components, files, git info)
- ✅ Tests tracking flag
- ✅ Auto-detects components from file paths
- ✅ Stores in Tier 1 + Tier 2 (patterns)
- ✅ Git commit tracking

**Captured Context:**
- Description
- Components affected
- Files changed
- Tests added (yes/no)
- Git branch & commit
- Timestamp

---

### 4. `cortex-resume` - One-Command Conversation Resume

Resume conversations with zero friction.

**Usage:**
```bash
# Show last conversation
cortex-resume

# Show last 3 conversations
cortex-resume --last 3

# Search conversations
cortex-resume --search "authentication"

# Interactive mode
cortex-resume --interactive
```

**Features:**
- ✅ Show recent conversations
- ✅ Search by keyword
- ✅ Generates ready-to-paste resume prompt
- ✅ Shows conversation metadata (type, tags, timestamp)
- ✅ Fast retrieval from Tier 1

**Output Example:**
```
=== Last 3 Conversations ===

1. [FEATURE] 2025-11-09 14:30:22
   ID: abc123
   Added user authentication with JWT tokens
   Tags: auth, security

2. [BUG] 2025-11-09 13:15:10
   ID: def456
   Fixed null pointer in parser.py
   
3. [GENERAL] 2025-11-09 10:05:33
   ID: ghi789
   Refactored database connection module

============================================================
📋 Resume Prompt (copy to Copilot Chat):
============================================================

#file:prompts/user/cortex.md

Continue from last conversation:
- 2025-11-09T14:30:22: Added user authentication with JWT tokens
- 2025-11-09T13:15:10: Fixed null pointer in parser.py
- 2025-11-09T10:05:33: Refactored database connection module

============================================================
```

---

## Installation

All tools are located in `/scripts/` directory and are automatically available after CORTEX setup.

**Make executable (if needed):**
```bash
chmod +x scripts/cortex-capture
chmod +x scripts/cortex-bug
chmod +x scripts/cortex-feature
chmod +x scripts/cortex-resume
```

**Add to PATH (optional):**
```bash
# Add to ~/.zshrc or ~/.bashrc
export PATH="$PATH:/path/to/CORTEX/scripts"
```

---

## Requirements

- Python 3.8+
- CORTEX brain initialized (`python scripts/cortex_setup.py`)
- Git (for auto-context detection)

---

## Performance

All tools target **<5 second** capture time:

| Tool | Target | Typical |
|------|--------|---------|
| cortex-capture | <5s | 1-3s |
| cortex-bug | <5s | 2-4s |
| cortex-feature | <5s | 2-4s |
| cortex-resume | <5s | 0.5-2s |

**Performance factors:**
- ✅ Minimal user input
- ✅ Auto-detection of context
- ✅ Fire-and-forget pattern extraction
- ✅ Efficient tier operations

---

## Integration with CORTEX

### Tier 1: Working Memory
All captures are stored in Tier 1 for immediate access:
- Conversation history
- Searchable by keyword
- Available for "continue" commands

### Tier 2: Knowledge Graph
Patterns extracted from captures:
- Feature patterns
- Bug patterns
- Component relationships
- Tag relationships

### Tier 3: Development Context
Git context automatically captured:
- Branch information
- Changed files
- Commit history

---

## Expected Impact

**Goal:** Improve "continue" success rate from 60% → 90%

**How:**
1. **Zero Friction:** <5 second capture eliminates excuse "takes too long"
2. **Smart Context:** Auto-detection means less typing
3. **Structured Data:** Templates ensure consistency
4. **Easy Resume:** One-command conversation resumption

**Metrics to Track:**
- Capture frequency (target: 80%+ of sessions)
- Capture time (target: <5s average)
- Continue success rate (target: 90%+)
- User satisfaction (target: ≥4.0/5)

---

## Examples

### Daily Workflow

**Morning:**
```bash
# Resume yesterday's work
cortex-resume --last 3
```

**During Development:**
```bash
# Quick feature log
cortex-feature "Added login form" --tests

# Bug found
cortex-bug "Validation fails on empty email" --severity high

# General note
cortex-capture "Refactored validation logic" --type refactor
```

**End of Day:**
```bash
# Capture final state
cortex-feature "Completed authentication module" --components "auth,ui,api" --tests
```

---

## Troubleshooting

**Error: "CORTEX brain not found"**
```bash
# Initialize brain first
python scripts/cortex_setup.py
```

**Error: "Failed to import CORTEX modules"**
```bash
# Run from CORTEX root directory
cd /path/to/CORTEX
./scripts/cortex-capture "test"
```

**Slow capture (>5 seconds)**
- Check git status speed: `time git status`
- Verify tier database is not corrupted
- Check disk I/O

---

## Future Enhancements (Phase 5+)

- [ ] Shell completions (bash/zsh)
- [ ] Git hooks for auto-capture
- [ ] Recall command (`cortex-recall "last python change"`)
- [ ] Activity scoring (prioritize important captures)
- [ ] Auto-summarization of captures

---

## Related Documentation

- **Phase 4 Design:** `cortex-brain/cortex-2.0-design/PHASE-3-EXTENSION-DEFERRED.md`
- **Ambient Capture:** `scripts/cortex/auto_capture_daemon.py`
- **Tier 1 API:** `src/tier1/working_memory.py`
- **Tier 2 API:** `src/tier2/knowledge_graph.py`

---

**Status:** ✅ Implemented (Phase 4.1 - Week 11)  
**Next:** Phase 4.2 - Shell Integration (Week 12)
