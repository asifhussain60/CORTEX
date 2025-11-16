# CORTEX Pattern Cleanup & Amnesia - Quick Reference

**Purpose:** Quick guide to using pattern cleanup and enhanced amnesia systems.

---

## 🧹 Pattern Cleanup Automation

### Basic Usage

```python
from CORTEX.src.tier2.knowledge_graph import KnowledgeGraph
from CORTEX.src.tier2.pattern_cleanup import PatternCleanup

# Initialize
kg = KnowledgeGraph()
cleanup = PatternCleanup(kg)

# Apply automatic decay (safe - protects generic patterns)
stats = cleanup.apply_automatic_decay()
print(f"Decayed: {stats.decayed_count}, Deleted: {stats.deleted_count}")

# Consolidate similar patterns
stats = cleanup.consolidate_similar_patterns(namespace="KSESSIONS")
print(f"Consolidated: {stats.consolidated_count}")

# Remove stale patterns
stats = cleanup.remove_stale_patterns(stale_days=90)
print(f"Removed: {stats.deleted_count}")

# Get recommendations
recs = cleanup.get_cleanup_recommendations()
print(f"Decay candidates: {recs['decay_candidates']}")
print(f"Stale candidates: {recs['stale_candidates']}")

# Optimize database
cleanup.optimize_database()
```

### Configuration

```python
# Adjust thresholds (class attributes)
PatternCleanup.DECAY_RATE = 0.01          # 1% per day
PatternCleanup.DECAY_THRESHOLD_DAYS = 30  # Start after 30 days
PatternCleanup.MIN_CONFIDENCE = 0.3       # Delete below this
PatternCleanup.STALE_THRESHOLD_DAYS = 90  # Mark stale after 90 days
PatternCleanup.SIMILARITY_THRESHOLD = 0.70  # Consolidate if >70% similar
```

### Protection Guarantees

✅ **NEVER touches:**
- `scope='generic'` patterns (CORTEX core intelligence)
- Patterns with `CORTEX-core` in namespaces
- Pinned patterns

✅ **Always safe to run** - protection is automatic

---

## 🧠 Enhanced Amnesia System

### Basic Usage

```python
from CORTEX.src.tier2.knowledge_graph import KnowledgeGraph
from CORTEX.src.tier2.amnesia import EnhancedAmnesia

# Initialize
kg = KnowledgeGraph()
amnesia = EnhancedAmnesia(kg)

# Preview what would be deleted
preview = amnesia.get_deletion_preview(namespace="KSESSIONS")
print(f"Would delete: {preview['would_delete']}")
print(f"Would protect: {preview['would_protect']}")

# Delete by namespace (SAFE - protections built-in)
stats = amnesia.delete_by_namespace("KSESSIONS", dry_run=True)
print(f"DRY RUN: Would delete {stats.patterns_deleted} patterns")

# Execute deletion
stats = amnesia.delete_by_namespace("KSESSIONS", require_confirmation=False)
print(f"Deleted: {stats.patterns_deleted}, Protected: {stats.protected_count}")

# Delete by confidence
stats = amnesia.delete_by_confidence(max_confidence=0.5)
print(f"Deleted: {stats.patterns_deleted}")

# Delete by age
stats = amnesia.delete_by_age(days_inactive=120)
print(f"Deleted: {stats.patterns_deleted}")
```

### Advanced Operations

```python
# Clear entire application scope (NUCLEAR - requires confirmation)
stats = amnesia.clear_application_scope(
    confirmation_code="DELETE_ALL_APPLICATIONS",
    dry_run=True  # Test first!
)

# Export deletion log for recovery
from pathlib import Path
log_path = Path("deletion_log.json")
amnesia.export_deletion_log(log_path)

# Bypass safety threshold (DANGEROUS - testing only!)
stats = amnesia.delete_by_namespace(
    "KSESSIONS",
    bypass_safety=True  # Use with extreme caution
)
```

### Protection Guarantees

✅ **NEVER deletes:**
- `scope='generic'` patterns
- Patterns with `CORTEX-core` in namespaces
- `CORTEX-core` namespace itself (BLOCKED)

✅ **Safety mechanisms:**
- 50% mass deletion threshold
- Confirmation codes for destructive operations
- Multi-namespace safety (partial removal only)
- Dry-run preview available
- Full audit logging

❌ **FORBIDDEN:**
```python
# This will raise ValueError
amnesia.delete_by_namespace("CORTEX-core")  # ❌ BLOCKED

# This will raise ValueError without confirmation
amnesia.clear_application_scope()  # ❌ Requires confirmation code

# This will raise RuntimeError if >50% deletion
amnesia.delete_by_namespace("KSESSIONS")  # ❌ If >50% of patterns
```

---

## 🔍 Common Scenarios

### Scenario 1: Clean Up Old Application Knowledge

```python
# 1. Preview what will be deleted
preview = amnesia.get_deletion_preview(
    namespace="KSESSIONS",
    days_inactive=90
)
print(f"Would delete: {preview['would_delete']} patterns")

# 2. Delete patterns inactive >90 days
stats = amnesia.delete_by_age(
    days_inactive=90,
    namespace="KSESSIONS",
    dry_run=False
)
print(f"Deleted: {stats.patterns_deleted}")

# 3. Optimize database
cleanup.optimize_database()
```

### Scenario 2: Remove Low Quality Patterns

```python
# 1. Get recommendations
recs = cleanup.get_cleanup_recommendations()
print(f"Low confidence candidates: {recs['low_confidence_candidates']}")

# 2. Delete patterns with confidence <0.3
stats = amnesia.delete_by_confidence(
    max_confidence=0.3,
    namespace="KSESSIONS"
)
print(f"Deleted: {stats.patterns_deleted}")
```

### Scenario 3: Clear Application Completely

```python
# 1. Preview deletion
preview = amnesia.get_deletion_preview(namespace="KSESSIONS")
print(f"Total patterns: {preview['total_patterns']}")
print(f"Would delete: {preview['would_delete']}")
print(f"Would protect: {preview['would_protect']}")

# 2. Export current state (backup)
amnesia.export_deletion_log(Path("backup_before_clear.json"))

# 3. Delete all KSESSIONS patterns (requires bypass if >50%)
stats = amnesia.delete_by_namespace(
    "KSESSIONS",
    require_confirmation=False,
    bypass_safety=True  # Only if you're sure!
)
print(f"Deleted: {stats.patterns_deleted}")
```

### Scenario 4: Regular Maintenance

```python
# Run this periodically (daily/weekly)

# 1. Apply automatic decay
decay_stats = cleanup.apply_automatic_decay()

# 2. Consolidate similar patterns
consolidate_stats = cleanup.consolidate_similar_patterns()

# 3. Remove stale patterns
stale_stats = cleanup.remove_stale_patterns(stale_days=90)

# 4. Optimize database
cleanup.optimize_database()

# 5. Report
print(f"""
Maintenance Complete:
  Decayed: {decay_stats.decayed_count}
  Deleted: {decay_stats.deleted_count}
  Consolidated: {consolidate_stats.consolidated_count}
  Stale Removed: {stale_stats.deleted_count}
""")
```

---

## ⚙️ Configuration Options

### Pattern Cleanup

```python
# Decay settings
cleanup.DECAY_RATE = 0.01               # 1% per day (default)
cleanup.DECAY_THRESHOLD_DAYS = 30       # Days before decay starts
cleanup.MIN_CONFIDENCE = 0.3            # Delete threshold
cleanup.STALE_THRESHOLD_DAYS = 90       # Stale pattern age
cleanup.SIMILARITY_THRESHOLD = 0.70     # Consolidation similarity

# Usage with custom settings
stats = cleanup.apply_automatic_decay(protect_generic=True)
stats = cleanup.consolidate_similar_patterns(namespace="KSESSIONS", dry_run=False)
stats = cleanup.remove_stale_patterns(stale_days=60)
```

### Enhanced Amnesia

```python
# Safety settings
amnesia.MAX_DELETION_PCT = 0.50         # 50% max deletion threshold
amnesia.REQUIRE_CONFIRMATION_ABOVE = 10 # Confirm if deleting >10 patterns

# Usage with options
stats = amnesia.delete_by_namespace(
    namespace="KSESSIONS",
    require_confirmation=True,   # Check threshold
    dry_run=False,               # Execute (not preview)
    bypass_safety=False          # Respect 50% limit
)

stats = amnesia.delete_by_confidence(
    max_confidence=0.5,
    protect_generic=True,        # Never delete generic
    namespace="KSESSIONS",       # Limit to namespace
    dry_run=False                # Execute
)

stats = amnesia.delete_by_age(
    days_inactive=90,
    protect_generic=True,
    namespace="KSESSIONS",
    dry_run=False
)
```

---

## 🛡️ Safety Checklist

**Before running ANY deletion operation:**

- [ ] ✅ Run with `dry_run=True` first
- [ ] ✅ Check preview results (`get_deletion_preview()`)
- [ ] ✅ Export deletion log for recovery
- [ ] ✅ Verify you're targeting correct namespace
- [ ] ✅ Confirm generic patterns are protected
- [ ] ✅ Test with small subset first
- [ ] ✅ Have backup/recovery plan

**Never bypass safety unless:**
- ❌ You're testing in isolated environment
- ❌ You have full backup
- ❌ You understand the consequences
- ❌ You've run dry-run multiple times

---

## 📊 Monitoring & Logging

### Check Cleanup Stats

```python
# Get recommendations
recs = cleanup.get_cleanup_recommendations()
print(f"""
Pattern Health:
  Total: {recs['total_patterns']}
  Generic: {recs['generic_patterns']} (protected)
  Application: {recs['application_patterns']}
  
Cleanup Candidates:
  Decay: {recs['decay_candidates']}
  Stale: {recs['stale_candidates']}
  Low Confidence: {recs['low_confidence_candidates']}
""")
```

### View Decay History

```python
# Get decay log
log = kg.get_decay_log(limit=50)
for entry in log:
    print(f"{entry['pattern_id']}: {entry['old_confidence']} → {entry['new_confidence']}")
    print(f"  Reason: {entry['reason']}")
    print(f"  Date: {entry['decay_date']}")
```

### Export Audit Trail

```python
# Export deletion log
amnesia.export_deletion_log(Path("deletion_audit.json"))

# Check deletion stats
stats = amnesia.delete_by_namespace("KSESSIONS", dry_run=True)
print(f"Deletion log entries: {len(stats.deletion_log)}")
for entry in stats.deletion_log:
    print(f"  {entry['pattern_id']}: {entry['action']}")
```

---

## 🚨 Emergency Recovery

### If You Accidentally Deleted Too Much

1. **Check deletion log:**
```python
log_path = Path("deletion_audit.json")
if log_path.exists():
    import json
    with open(log_path) as f:
        log = json.load(f)
    print(f"Deleted {len(log)} patterns")
```

2. **Review what was deleted:**
```python
for entry in log:
    print(f"Pattern: {entry['pattern_id']}")
    print(f"Reason: {entry['reason']}")
    print(f"Date: {entry['date']}")
```

3. **Restore from backup** (if available):
   - Use database backup
   - Re-run pattern learning from events
   - Rebuild knowledge graph

---

## 📖 Further Reading

- **Architecture:** `CORTEX/docs/architecture/BRAIN-CONVERSATION-MEMORY-DESIGN.md`
- **Gap Analysis:** `KNOWLEDGE-BOUNDARIES-GAP-FIX.md`
- **Progress:** `PHASES-4-5-COMPLETE.md`
- **Tests:** `CORTEX/tests/tier2/test_pattern_cleanup.py`, `test_amnesia.py`

---

**Last Updated:** November 6, 2025  
**Version:** 1.0 (Phases 4-5 Complete)
