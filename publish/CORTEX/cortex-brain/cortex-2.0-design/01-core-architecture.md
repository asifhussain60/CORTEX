# CORTEX 2.0 Core Architecture

**Document:** 01-core-architecture.md  
**Version:** 2.0.0-alpha  
**Date:** 2025-11-07

---

## 🎯 Architecture Philosophy

CORTEX 2.0 uses a **Hybrid Approach** - not a fresh start, but strategic evolution:

- **KEEP 70%:** Proven foundations that work excellently
- **REFACTOR 20%:** Pain points that need improvement  
- **ENHANCE 10%:** New capabilities for future growth

---

## ✅ What We Keep from CORTEX 1.0

### 1. Dual-Hemisphere Brain Model
**Status:** KEEP (proven design)

- LEFT BRAIN (Tactical): Test-first execution, precise code changes
- RIGHT BRAIN (Strategic): Planning, pattern recognition, risk assessment
- Corpus Callosum: Coordination between hemispheres

**Why Keep:** Natural specialization, clear responsibilities, works excellently

### 2. 5-Tier Memory System
**Status:** KEEP (with enhancements)

| Tier | Purpose | Keep/Enhance |
|------|---------|--------------|
| **Tier 0** | Instinct (Rules) | KEEP + Add Rule #28 enforcement |
| **Tier 1** | Working Memory | KEEP + Add conversation state tracking |
| **Tier 2** | Knowledge Graph | KEEP + Enhance boundary validation |
| **Tier 3** | Development Context | KEEP + Add bloat tracking |
| **Tier 4** | Event Stream | KEEP + Add compression |

**Why Keep:** Proven 60/60 tests passing, 52% faster than targets

### 3. The 27 Rules
**Status:** KEEP (add 1 new rule)

All existing rules remain, plus:
- **Rule #28:** Plugin Hook System enforcement
- **Rule #29:** Conversation State Persistence

**Why Keep:** 100% test coverage, clear governance, brain protected

### 4. Database Schema
**Status:** KEEP (extend with new tables)

Existing 25 tables proven and optimized:
- FTS5 full-text search working excellently
- Proper indexes for <50ms queries
- FIFO queue implementation solid

**Enhancement:** Add 5 new tables (see document 11)

### 5. Agent Architecture
**Status:** KEEP (10 existing agents + 2 new)

Existing 10 agents remain:
- 5 LEFT BRAIN (Builder, Tester, Fixer, Inspector, Archivist)
- 5 RIGHT BRAIN (Dispatcher, Planner, Analyst, Governor, Protector)

**New Agents:**
- **Plugin Manager** (RIGHT BRAIN) - Manages plugin lifecycle
- **State Manager** (RIGHT BRAIN) - Manages conversation state

### 6. SOLID Principles
**Status:** KEEP (foundation of quality)

- Single Responsibility
- Open/Closed
- Liskov Substitution
- Interface Segregation
- Dependency Inversion

**Why Keep:** Prevents bloat, enables extensibility

### 7. Test Suite
**Status:** KEEP (60 tests, expand to ~80)

All existing tests remain:
- 8 Tier 0 tests
- 15 Tier 1 tests
- 17 Tier 2 tests
- 15 Tier 3 tests
- 5 Agent tests

**New Tests:** ~20 additional for new features

---

## 🔄 What We Refactor

### 1. Path Management System
**Problem:** Hardcoded absolute paths  
**Solution:** Relative path resolver with environment config  
**Document:** 04-path-management.md

### 2. Conversation State
**Problem:** Can't resume after interruption  
**Solution:** Persistent state tracking with checkpoints  
**Document:** 03-conversation-state.md

### 3. Documentation System
**Problem:** Manual refresh creates duplicates  
**Solution:** Intelligent auto-refresh with cleanup  
**Document:** 06-documentation-system.md

### 4. Knowledge Boundaries
**Problem:** Validation exists but not strict enough  
**Solution:** Automated enforcement with auto-migration  
**Document:** 05-knowledge-boundaries.md

---

## 🚀 What We Add (New Capabilities)

### 1. Plugin Architecture
**New Capability:** Extensible hook system  
**Benefits:** Reduce core bloat, user customization, easy feature addition  
**Document:** 02-plugin-system.md

### 2. Self-Review System
**New Capability:** Comprehensive system health checks  
**Benefits:** Automated maintenance, rule compliance auditing, auto-fix  
**Document:** 07-self-review-system.md

### 3. Database Maintenance
**New Capability:** Automatic optimization and archival  
**Benefits:** Keep database lean, prevent bloat, maintain performance  
**Document:** 08-database-maintenance.md

### 4. Task Tracking
**New Capability:** Persistent actionable requests  
**Benefits:** Never lose track of work, cross-session continuity  
**Document:** 03-conversation-state.md

---

## 🏗️ CORTEX 2.0 System Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    CORTEX 2.0 ARCHITECTURE                       │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              Universal Entry Point (cortex.md)            │   │
│  │              + State Manager (Resume Support)             │   │
│  └───────────────────────────┬──────────────────────────────┘   │
│                              │                                   │
│  ┌───────────────────────────┴──────────────────────────────┐   │
│  │              RIGHT BRAIN (Strategic Planner)              │   │
│  │  ┌─────────────────────────────────────────────────────┐ │   │
│  │  │ • Dispatcher (Intent Router)                        │ │   │
│  │  │ • Planner (Work Breakdown)                          │ │   │
│  │  │ • Analyst (Screenshot Analysis)                     │ │   │
│  │  │ • Governor (CORTEX Change Control)                  │ │   │
│  │  │ • Brain Protector (Risk Challenge)                  │ │   │
│  │  │ • Plugin Manager (NEW: Lifecycle Management)        │ │   │
│  │  │ • State Manager (NEW: Conversation State)           │ │   │
│  │  └─────────────────────────────────────────────────────┘ │   │
│  └───────────────────────────┬──────────────────────────────┘   │
│                              │                                   │
│  ┌───────────────────────────┴──────────────────────────────┐   │
│  │            Corpus Callosum (Message Queue)                │   │
│  └───────────────────────────┬──────────────────────────────┘   │
│                              │                                   │
│  ┌───────────────────────────┴──────────────────────────────┐   │
│  │              LEFT BRAIN (Tactical Executor)               │   │
│  │  ┌─────────────────────────────────────────────────────┐ │   │
│  │  │ • Builder (Code Executor)                           │ │   │
│  │  │ • Tester (Test Generator)                           │ │   │
│  │  │ • Fixer (Error Corrector)                           │ │   │
│  │  │ • Inspector (Health Validator)                      │ │   │
│  │  │ • Archivist (Commit Handler)                        │ │   │
│  │  └─────────────────────────────────────────────────────┘ │   │
│  └───────────────────────────┬──────────────────────────────┘   │
│                              │                                   │
│  ┌───────────────────────────┴──────────────────────────────┐   │
│  │                   5-TIER MEMORY SYSTEM                    │   │
│  │  ┌─────────────────────────────────────────────────────┐ │   │
│  │  │ Tier 0: Instinct (29 Rules + Plugin Hooks)          │ │   │
│  │  │ Tier 1: Working Memory (20 Conversations + State)   │ │   │
│  │  │ Tier 2: Knowledge Graph (Patterns + Boundaries)     │ │   │
│  │  │ Tier 3: Dev Context (Git + Bloat Tracking)          │ │   │
│  │  │ Tier 4: Events (Compressed After 7 Days)            │ │   │
│  │  └─────────────────────────────────────────────────────┘ │   │
│  └───────────────────────────┬──────────────────────────────┘   │
│                              │                                   │
│  ┌───────────────────────────┴──────────────────────────────┐   │
│  │                   PLUGIN SYSTEM (NEW)                     │   │
│  │  ┌─────────────────────────────────────────────────────┐ │   │
│  │  │ Plugin Registry | Lifecycle Manager | Hook System   │ │   │
│  │  │                                                      │ │   │
│  │  │ Core Plugins:                                        │ │   │
│  │  │  • Cleanup Plugin (folder, code, temp files)         │ │   │
│  │  │  • Organization Plugin (structure validation)        │ │   │
│  │  │  • Documentation Plugin (MkDocs auto-refresh)        │ │   │
│  │  │  • Self-Review Plugin (health checks)                │ │   │
│  │  │  • DB Maintenance Plugin (optimization)              │ │   │
│  │  └─────────────────────────────────────────────────────┘ │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │           CROSS-CUTTING CONCERNS (Enhanced)               │   │
│  │  • Path Resolver (Environment-Agnostic Paths)             │   │
│  │  • Knowledge Boundary Enforcer (Auto-Validation)          │   │
│  │  • Incremental File Creator (Chunk Large Files)           │   │
│  │  • State Persister (Conversation Checkpoints)             │   │
│  │  • Task Tracker (Actionable Request DB)                   │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📊 Component Breakdown

### Core Components (Unchanged)
- Universal Entry Point
- 10 Existing Agents
- 5-Tier Memory System
- Corpus Callosum
- 27 Rules (Tier 0)

### New Components
- Plugin Manager (Agent)
- State Manager (Agent)
- Plugin System (Infrastructure)
- Path Resolver (Utility)
- Task Tracker (Database Layer)
- Incremental File Creator (Utility)

### Enhanced Components
- Brain Protector (stricter validation)
- Documentation System (auto-refresh)
- Database (new tables + maintenance)
- Knowledge Graph (boundary enforcement)

---

## 🔌 Plugin Integration Points

CORTEX 2.0 provides hooks at key stages:

### Lifecycle Hooks
```python
@plugin_hook("before_conversation_start")
def prepare_environment(context):
    # Run before any conversation processing
    pass

@plugin_hook("after_task_complete")
def cleanup_artifacts(task_result):
    # Run after each task completion
    pass

@plugin_hook("on_self_review")
def custom_health_check():
    # Run during self-review process
    pass
```

### Category Hooks
- **Cleanup Hooks:** Triggered during cleanup phases
- **Validation Hooks:** Triggered during validation
- **Documentation Hooks:** Triggered during doc refresh
- **Maintenance Hooks:** Triggered during DB maintenance

---

## 🎯 Design Goals Achieved

| Goal | How Achieved |
|------|--------------|
| **Reduce Bloat** | Plugin system moves non-essential features out of core |
| **Resume Conversations** | State Manager tracks checkpoints, enables resume |
| **Track Tasks** | Persistent actionable request DB with status |
| **Cross-Platform** | Path Resolver with environment-specific config |
| **Protect Core Knowledge** | Automated boundary validation and enforcement |
| **Smart Docs** | Auto-refresh with duplicate detection and cleanup |
| **Self-Healing** | Comprehensive self-review with auto-fix capabilities |
| **Database Optimization** | Automatic maintenance, archival, compression |
| **Prevent Length Errors** | Incremental file creation enforced at Tier 0 |

---

## 📈 Migration Impact

### Code Changes
- **Core Code:** ~30% modified (paths, state, plugins)
- **Database Schema:** +5 new tables
- **Tests:** +20 new tests
- **Documentation:** Complete restructure

### Performance Impact
- **Tier 1-3:** No performance degradation (same queries)
- **Tier 4:** Faster (compression reduces size)
- **Startup:** +50ms (plugin loading)
- **Overall:** <5% overhead from new features

### Breaking Changes
- Path references (auto-migrated)
- cortex.config.json format (v2.0 schema)
- Plugin system (new feature, backward compatible)

---

## 🚀 Next Steps

1. ✅ Core architecture defined
2. ⏳ Design plugin system (document 02)
3. 📋 Design conversation state (document 03)
4. 📋 Continue with remaining design documents

**Status:** Core architecture complete, ready for detailed subsystem design

---

**See Also:**
- 02-plugin-system.md (Plugin architecture details)
- 03-conversation-state.md (State management)
- 12-migration-strategy.md (Migration from 1.0)
