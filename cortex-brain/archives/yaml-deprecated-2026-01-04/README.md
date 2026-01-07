# YAML Brain Sources - DEPRECATED

**Deprecated:** 2026-01-04  
**Reason:** Migrated to SQLite databases for performance, consistency, and reliability

---

## 🚫 DO NOT USE THESE FILES IN PRODUCTION

These YAML files are **archived for historical reference only**. All production code now uses SQLite databases.

---

## 🔄 Replacement Locations

| Old YAML Source | New Database | Schema Location |
|-----------------|--------------|-----------------|
| `conversation-context.jsonl` | `tier1/working_memory.db` | SQLite: conversations, messages, entities, files_modified |
| `knowledge-graph.yaml` | `tier2/knowledge_graph.db` | SQLite: patterns, pattern_relationships, pattern_tags |
| `development-context.yaml` | `tier3/policies/*.json` | JSON: token-efficiency-metrics.yaml, policies/ |

---

## 📊 Database Schemas

### Tier 1: `tier1/working_memory.db`
```sql
-- conversations: conversation metadata
-- messages: conversation messages with timestamps
-- entities: extracted entities (files, functions, classes)
-- files_modified: tracking of modified files per conversation
```

### Tier 2: `tier2/knowledge_graph.db`
```sql
-- patterns: development patterns and practices
-- pattern_relationships: connections between patterns
-- pattern_tags: categorization tags
-- confidence_decay_log: pattern confidence tracking
```

### Tier 3: `tier3/policies/`
- Development policies stored as JSON files
- Token efficiency metrics in YAML
- Context management rules

---

## 🔧 Migration Scripts

If you need to re-migrate data from these YAML files:

```bash
# Tier 1 migration
python src/tier1/migrate_tier1.py \
  --source cortex-brain/archives/yaml-deprecated-2026-01-04/conversation-context.jsonl \
  --target cortex-brain/tier1/working_memory.db

# Tier 2 migration
python src/tier2/migrate_tier2.py \
  --source cortex-brain/archives/yaml-deprecated-2026-01-04/knowledge-graph.yaml \
  --target cortex-brain/tier2/knowledge_graph.db

# Tier 3 migration
python src/tier3/migrate_tier3.py \
  --source cortex-brain/archives/yaml-deprecated-2026-01-04/development-context.yaml \
  --target cortex-brain/tier3/policies/
```

---

## ⚠️ Why This Change?

**Problems with YAML sources:**
- Dual-source brittleness (code reading both YAML + DB)
- Data inconsistency risk (YAML updated, DB stale)
- Race conditions (two sources conflicting)
- Performance degradation (double I/O)
- Maintenance burden (keeping 2 sources in sync)

**Benefits of SQLite:**
- Single source of truth
- ACID transactions (atomicity, consistency)
- Better performance (indexed queries)
- Concurrent access support
- Industry-standard reliability

---

## 📚 Documentation

**Updated Documentation:**
- `README.md` - Brain architecture section
- `cortex-brain/documents/cortex-architecture-quick-ref.md` - Migration notice
- `cortex-brain/documents/orchestrators-quick-ref.md` - Database references

---

## 🔒 Archive Policy

**Retention:** Indefinite (historical reference)  
**Access:** Read-only (archived state)  
**Restoration:** Not recommended (use migration scripts if needed)

---

**Archived:** 2026-01-04  
**C50-19:** Brain Data Source Cutover  
**Author:** CORTEX Investigation Orchestrator  

**Copyright © 2026 Asif Hussain. All rights reserved.**
