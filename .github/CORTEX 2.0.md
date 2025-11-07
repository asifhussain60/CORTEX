# CORTEX 2.0 Requirements - Pain Points from CORTEX 1.0

**Version:** 2.0.0-alpha  
**Date:** 2025-11-07  
**Status:** Requirements Specification

---

## 🎯 Core Architecture Requirement

### REQ-001: Plugin Architecture System
**Problem:** CORTEX 1.0 has hardcoded functionality leading to bloat  
**Requirement:** Implement plugin hook system for extensibility

**Specification:**
- Create base plugin interface with lifecycle hooks (init, execute, cleanup, validate)
- Core functionality categories:
  - **Cleanup Plugins:** Folder cleanup, code cleanup, temp file removal
  - **Organization Plugins:** File organizer, structure validator
  - **Maintenance Plugins:** Database optimization, cache management
  - **Documentation Plugins:** MkDocs refresh, diagram generation
- Plugin registry with auto-discovery
- Plugin dependency resolution
- Plugin enable/disable without code changes
- Plugin configuration via YAML

**Benefits:**
- Reduce core bloat (move non-essential features to plugins)
- Easy to add new functionality without modifying core
- Users can create custom plugins for their needs
- Better separation of concerns

---

## 🔄 Conversation & Task Management

### REQ-002: Conversation Interruption & Resume
**Problem:** When Copilot is stopped mid-task, it doesn't resume where it left off  
**Requirement:** Track execution state to enable seamless resume

**Specification:**
- Track current conversation phase (planning, executing, testing, validating)
- Save last completed action with checkpoint
- On resume, query user: "Continue from [last action]? (Y/n)"
- If user modified CORTEX entry point mid-conversation, detect changes and incorporate
- Store conversation state in Tier 1 with resume capability flag

**User Experience:**
```
User: [stops Copilot mid-task]
User: [modifies cortex.md with new instruction]
User: "Continue"

CORTEX: "I see you updated the entry point. Changes detected:
  - New instruction: [summary]
  
  I was at: Phase 2, Task 3 (implementing UserService)
  
  Options:
  1. Continue Task 3 with new instructions
  2. Re-plan from current point
  3. Start fresh with new instructions
  
  Your choice: [1]"
```

### REQ-003: Actionable Request Tracking (Task Persistence)
**Problem:** No tracking of conversation-generated tasks that are pending  
**Requirement:** Database-backed task tracking with status management

**Specification:**
- New table: `tier1_actionable_requests`
  - Fields: request_id, conversation_id, description, status, priority, created_at, due_date, completed_at
  - Status: PENDING, IN_PROGRESS, COMPLETED, CANCELLED, OBSOLETE
- Auto-extract actionable items from conversations using intent detection
- Display pending items on every CORTEX invocation:
  ```
  ⚡ Pending Requests (3):
  1. [PENDING] Add authentication to login page (2 days old)
  2. [IN_PROGRESS] Fix invoice export bug (started 1 hour ago)
  3. [PENDING] Update user documentation (1 week old) [RECOMMEND: Remove - obsolete?]
  ```
- User commands:
  - "Show pending" - List all pending requests
  - "Remove request 3" - Cancel/remove specific request
  - "Continue request 2" - Resume specific request
- Auto-recommendations for cleanup:
  - Requests >30 days old: "RECOMMEND: Review - may be obsolete"
  - Duplicate requests: "RECOMMEND: Merge with request #5"
  - Completed elsewhere: "DETECT: Similar commit found, mark complete?"

### REQ-004: Automatic Request Cleanup
**Problem:** No cleanup mechanism, request list will bloat  
**Requirement:** Time-based and rule-based auto-cleanup with user confirmation

**Specification:**
- Auto-archive completed requests after 7 days
- Flag obsolete requests (>60 days old, no activity)
- Weekly digest: "5 old requests detected, review for cleanup?"
- Soft delete with 30-day recovery window
- Configurable retention policies in cortex.config.json

---

## 🗂️ Path Management

### REQ-005: Relative Path System with Environment Configuration
**Problem:** Hardcoded paths break when CORTEX runs on different machines/OS  
**Requirement:** All internal paths relative with environment-specific resolution

**Specification:**
- Never hardcode absolute paths in CORTEX code
- All paths stored as relative to project root
- Environment detection: Windows, macOS, Linux
- Configuration: `cortex.config.json` with machine-specific sections:
  ```json
  {
    "machines": {
      "DESKTOP-WINDOWS": {
        "project_root": "D:\\PROJECTS\\MyApp",
        "brain_path": "D:\\PROJECTS\\CORTEX\\cortex-brain"
      },
      "MacBook-Pro": {
        "project_root": "/Users/asif/Projects/MyApp",
        "brain_path": "/Users/asif/Projects/CORTEX/cortex-brain"
      }
    }
  }
  ```
- Path resolver utility: `resolve_path("cortex-brain/tier1/")`
- Automatic machine detection (hostname-based)
- Path validation on CORTEX startup
- Clear error messages if paths not configured

**Benefits:**
- Work seamlessly across Windows, macOS, Linux
- Same user, multiple machines, zero friction
- Clone repo anywhere, configure once, works forever

---

## 🛡️ Knowledge Boundary Enforcement

### REQ-006: Strict Core Knowledge Protection
**Problem:** Project-specific data can pollute CORTEX's core operational knowledge  
**Requirement:** Enforce strict separation with validation and auto-correction

**Specification:**
- Define protected namespaces:
  - `cortex.core.*` - How CORTEX functions (rules, agents, workflows)
  - `cortex.project.*` - Project-specific patterns and data
- Tier 0 NEVER contains project data (only CORTEX rules)
- Tier 2 patterns tagged with scope: `core` or `application`
- Brain Protector validates on every update:
  - ❌ Block: Project class names in Tier 0
  - ❌ Block: Application-specific rules in governance
  - ✅ Allow: CORTEX architecture patterns in Tier 2 (scope: core)
- Auto-migration: If project data detected in wrong tier, auto-move with warning
- Audit command: `cortex self-review --knowledge-boundaries`

**Examples:**
```yaml
# ✅ CORRECT: Generic CORTEX pattern (Tier 2, scope: core)
pattern:
  name: "tdd_workflow_pattern"
  scope: "core"
  namespace: "cortex.core.workflows"

# ❌ INCORRECT: Project-specific in Tier 0 (Brain Protector blocks)
rule:
  name: "UserService must use DI"
  scope: "application"
  namespace: "myapp.services"  # <-- BLOCKED: Project data in Tier 0
```

---

## 📚 Documentation System

### REQ-007: MkDocs Complete Auto-Refresh
**Problem:** Manual refreshes create duplicates, miss obsolete content, incorrect structure  
**Requirement:** Intelligent full documentation regeneration

**Specification:**
- Command: `cortex refresh-docs --full`
- Process:
  1. **Scan Phase:** Detect all existing docs, inventory structure
  2. **Cleanup Phase:** Remove obsolete files (not in index), delete duplicates
  3. **Generation Phase:** Regenerate from source (code, brain, rules)
  4. **Structure Phase:** Organize with correct hierarchy
  5. **Validation Phase:** Check for broken links, missing sections
- Required structure:
  ```
  docs/
    index.md                    # HOME: Rules front and center
    awakening-of-cortex.md      # PROMINENT: Second item
    guides/                     # LEFT MENU: Organized categories
    reference/
    architecture/
    story/
  ```
- Home page structure (index.md):
  ```markdown
  # CORTEX Documentation
  
  ## 📜 The Rulebook (CORE)
  [Display all 27 rules with one-line descriptions]
  
  ## 📖 The Awakening of CORTEX
  [Link to story with preview]
  
  ## 🚀 Quick Start
  ## 📚 Guides
  ## 🏗️ Architecture
  ```
- MkDocs configuration auto-generated with logical left menu
- No duplicates: Track all generated files in `.mkdocs-manifest.json`
- Obsolete detection: Files in docs/ but not in manifest = DELETE

**User Experience:**
```
User: "Refresh documentation"

CORTEX:
  ✓ Scanning existing docs (48 files)
  ✓ Detected 3 duplicates, 5 obsolete files
  ✓ Removing duplicates...
  ✓ Removing obsolete files...
  ✓ Regenerating from source...
  ✓ Structuring navigation (6 categories)
  ✓ Validating links (127 checked, 0 broken)
  
  ✅ Documentation refreshed: docs/site/
  📊 Added: 4 new files
  🗑️ Removed: 8 obsolete files
  📝 Updated: 12 modified files
```

---

## 🔍 Self-Review System

### REQ-008: Comprehensive System Health Check
**Problem:** No automated way to verify CORTEX is functioning correctly  
**Requirement:** Multi-phase self-review with auto-fix capabilities

**Specification:**
- Command: `cortex self-review --full`
- Phases (in order):

**Phase 0: Rule Compliance Audit (HOLY GRAIL)**
- Scan all recent conversations (last 20)
- Verify every action aligned with rulebook
- Check for rule violations: TDD skipped? DoD not met?
- Report violations with evidence and corrective actions
- **Output:** `self-review/rule-compliance-report.md`

**Phase 1: Protection Layer Validation**
- Verify all protection tests exist and are current
- Run Brain Protector test suite (8 tests minimum)
- Check FIFO queue enforcement
- Validate tier boundary protection
- **Output:** `self-review/protection-validation.md`

**Phase 2: Test Execution & Auto-Fix**
- Run all 60+ tests (tier0, tier1, tier2, tier3, agents)
- If failures detected:
  - Analyze failure root cause
  - Attempt auto-fix (simple issues)
  - Report complex issues for manual review
- **Output:** `self-review/test-results.md`

**Phase 3: Efficiency & Redundancy Scan**
- Scan for duplicate code patterns
- Detect unused imports, dead code
- Find inefficient queries (>target performance)
- Identify redundant files
- **Output:** `self-review/efficiency-report.md` with recommendations

**Phase 4: Cleanup Execution**
- Trigger cleanup plugins:
  - Delete temporary files (*.tmp, *.bak, __pycache__)
  - Reorganize misplaced files
  - Archive old logs (>30 days)
- File bloat prevention:
  - Compress old event logs
  - Archive completed conversations
  - Prune low-confidence patterns (confidence <0.3, unused >90 days)
- **Output:** `self-review/cleanup-summary.md`

**Phase 5: Documentation Sync**
- Detect changes since last doc refresh
- If significant changes, trigger `refresh-docs --full`
- Update architecture diagrams if structure changed
- **Output:** `self-review/documentation-sync.md`

**Phase 6: File Bloat Analysis**
- Scan for large files (>1MB)
- Check for runaway logs
- Detect duplicate content
- Recommend archival candidates
- **Internal Data Structure:** Maintain `file-inventory.json` with:
  - File paths, sizes, last modified, access frequency
  - Growth rate tracking
  - Bloat score (size × low-access-frequency)

**Final Report:**
```
📊 CORTEX Self-Review Report (2025-11-07)

✅ PASS: Rule Compliance (100% aligned)
✅ PASS: Protection Layer (8/8 tests passing)
⚠️  WARN: Test Suite (58/60 passing, 2 auto-fixed)
✅ PASS: Efficiency Scan (3 minor issues, auto-fixed)
✅ PASS: Cleanup Complete (47 files removed, 230MB freed)
✅ PASS: Documentation Synced
✅ PASS: File Bloat Prevention (archive: 12 files)

Overall Health: EXCELLENT (98/100)
Recommendations: None
Next Review: 2025-11-14 (7 days)
```

---

## 💾 Database Maintenance

### REQ-009: Automatic Database Optimization
**Problem:** No plan for database cleanup, will bloat over time  
**Requirement:** Auto-maintenance with archival and optimization

**Specification:**
- **Daily Maintenance (Low Impact):**
  - VACUUM to reclaim space
  - ANALYZE to update query planner statistics
  - Delete soft-deleted records >30 days old
  
- **Weekly Maintenance (Medium Impact):**
  - Archive completed conversations >30 days to separate archive DB
  - Prune low-value patterns (confidence <0.3, unused >90 days)
  - Compress old event logs (>7 days) to JSON archives
  - Re-index FTS5 tables for optimal performance
  
- **Monthly Maintenance (High Impact):**
  - Full VACUUM with REINDEX
  - Archive old Tier 3 metrics (>90 days) to separate DB
  - Purge duplicate patterns (merge similar patterns)
  - Optimize file hotspot history (keep only last 90 days)
  
- **Configurable Retention Policies:**
  ```yaml
  retention:
    tier1_conversations: 30 days  # After this, archive to tier1_archive.db
    tier2_patterns_min_confidence: 0.30  # Below this + unused 90d = DELETE
    tier3_metrics_window: 90 days  # Older data archived
    tier4_events_compression: 7 days  # Compress to .jsonl.gz
    archived_data_retention: 1 year  # Separate archive DB
  ```
  
- **Monitoring:**
  - Track database size over time
  - Alert if growth exceeds threshold (>100MB/month)
  - Report maintenance actions in self-review
  
- **Manual Override:**
  - `cortex db-maintenance --now` (run immediately)
  - `cortex db-maintenance --archive-all` (aggressive cleanup)
  - `cortex db-maintenance --restore <date>` (restore from archive)

---

## ✂️ Incremental File Creation

### REQ-010: Prevent Length Limit Errors (Tier 0 Rule)
**Problem:** Copilot creates large files in one response, hits length limit  
**Requirement:** Automatic chunking for all file creation >100 lines

**Specification:**
- **Rule #28:** "Incremental File Creation" (already exists, enforce strictly)
- Automatic detection: If file >100 lines, split into chunks
- Chunk size: 100-150 lines per tool call
- User feedback during chunking:
  ```
  Creating large file (450 lines), splitting into chunks...
  ✓ Chunk 1/3 created (lines 1-150)
  ✓ Chunk 2/3 created (lines 151-300)
  ✓ Chunk 3/3 created (lines 301-450)
  ✅ File complete: path/to/large-file.py
  ```
- Apply to:
  - Python modules
  - Markdown documentation
  - YAML configuration files
  - Any text file >100 lines
- **Implementation:** Wrapper around create_file tool
  - Analyze content length before creation
  - If >100 lines: Split, create sequentially
  - If <100 lines: Create directly

**Prevention in Tier 0:**
- Add to governance.yaml as immutable rule
- Brain Protector enforces: Challenges any attempt to create large file in one go
- Agents trained to chunk automatically

---

## 📊 Summary of Requirements

| Req ID | Category | Priority | Impact | Effort |
|--------|----------|----------|--------|--------|
| REQ-001 | Plugin Architecture | HIGH | High (enables extensibility) | Medium |
| REQ-002 | Conversation Resume | HIGH | High (user experience) | Medium |
| REQ-003 | Task Tracking | HIGH | High (productivity) | Medium |
| REQ-004 | Auto-Cleanup | MEDIUM | Medium (maintenance) | Low |
| REQ-005 | Path Management | HIGH | High (portability) | Low |
| REQ-006 | Knowledge Boundaries | CRITICAL | Critical (integrity) | Medium |
| REQ-007 | MkDocs Auto-Refresh | MEDIUM | Medium (documentation quality) | Medium |
| REQ-008 | Self-Review System | HIGH | High (reliability) | High |
| REQ-009 | DB Maintenance | MEDIUM | Medium (performance) | Medium |
| REQ-010 | Incremental Creation | CRITICAL | Critical (prevents errors) | Low |

**Total Estimated Effort:** 60-80 hours (hybrid approach with existing foundation)