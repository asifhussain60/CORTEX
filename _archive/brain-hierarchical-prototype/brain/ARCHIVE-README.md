# Brain Hierarchical Prototype - Archive

**Date Archived:** 2025-11-04  
**Status:** PROTOTYPE - Not actively used  
**Reason:** Dual brain structure identified and resolved

---

## What This Is

This was a **prototype of a hierarchical brain structure** with explicit tier folders:

```
brain/
├── instinct/              # Tier 0: Permanent rules
├── working-memory/        # Tier 1: Conversations  
├── long-term/             # Tier 2: Patterns
├── context-awareness/     # Tier 3: Metrics
├── imagination/           # Tier 4: Ideas
├── housekeeping/          # Tier 5: Auto-maintenance
├── sharpener/             # Testing framework
├── event-stream/          # Events log
└── health/                # Health metrics
```

## Why Archived

Analysis on **2025-11-04** revealed that:

1. ❌ **NOT referenced by any agents** - All active prompts use `kds-brain/`
2. ❌ **NOT synchronized** - Data here may differ from `kds-brain/`
3. ❌ **Purpose unclear** - Blueprint or abandoned migration target?
4. ✅ **Active structure is `kds-brain/`** - All 10+ agents working with flat structure

**Decision:** To avoid confusion and ensure we work with the **ACTIVE brain**, this prototype has been archived.

---

## Current Active Structure

The active brain is **`kds-brain/`** which implements the same **5-tier conceptual architecture** but in a **flat file organization**.

### kds-brain/ = 5 TIERS (Flat Organization)

```yaml
Tier 0 (Instinct):
  # No separate files - embedded in:
  - prompts/internal/*.md (governance rules)
  - governance/rules.md (17 core rules)
  
Tier 1 (Working Memory):
  - conversation-context.jsonl      # Last 10 messages buffer
  - conversation-history.jsonl      # Last 20 conversations (FIFO)

Tier 2 (Long-term):
  - knowledge-graph.yaml            # Consolidated patterns
  
Tier 3 (Context Awareness):
  - development-context.yaml        # Git metrics, velocity, hotspots

Tier 4 (Event Stream):
  - events.jsonl                    # All events (feeds Tier 2 updates)

Tier 5 (Health/Diagnostics):
  - anomalies.yaml                  # Protection system violations
```

**See:** `Brain Architecture.md` for complete current documentation

---

## If You Want Hierarchical Structure

This can be implemented in **v6.1+** by:

1. **Migrate data** from `kds-brain/` flat files to hierarchical folders
2. **Update all agent prompts** to reference new paths (10+ agents)
3. **Test all agents** after migration
4. **Update all scripts** that reference BRAIN files

**Estimated effort:** 2-3 days  
**Risk:** Moderate (all agents must be updated)  
**Benefit:** Better conceptual organization

**Recommendation:** Defer unless flat structure causes problems

---

## Design Inspiration

This hierarchical structure was inspired by:

- **Human brain organization** - Explicit separation of cognitive functions
- **Clean Architecture** - Each tier has its own directory
- **Discoverability** - Easy to find which tier handles what

The **flat structure** (`kds-brain/`) achieves the same conceptual separation but with simpler file organization.

---

## Files Present

The archived structure contains:

- `instinct/` - Permanent rules (not implemented)
- `working-memory/` - Conversation files (not synchronized with active)
- `long-term/` - Knowledge patterns (not synchronized with active)
- `context-awareness/` - Metrics (not synchronized with active)
- `imagination/` - Ideas/proposals (not implemented)
- `housekeeping/` - Auto-maintenance (not implemented)
- `sharpener/` - Testing framework (not implemented)
- `event-stream/` - Events (not synchronized with active)
- `health/` - Health metrics (not implemented)

⚠️ **WARNING:** Data in these folders is **NOT synchronized** with the active `kds-brain/` structure. Do not use as source of truth.

---

## Historical Context

This prototype was created as part of **KDS v6.0 planning** to visualize the conceptual architecture. However, implementation proceeded with the flat structure in `kds-brain/` which was already working and referenced by all agents.

The dual structure was discovered during pre-Week 1 validation on 2025-11-04, leading to this archival to prevent confusion.

---

**Active Brain:** `d:\PROJECTS\KDS\kds-brain/`  
**Documentation:** `d:\PROJECTS\KDS\Brain Architecture.md`  
**This Archive:** Reference only, not actively maintained
