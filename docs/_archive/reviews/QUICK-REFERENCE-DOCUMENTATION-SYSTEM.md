# CORTEX Documentation System - Quick Reference Card

**Created:** 2026-01-20 | **Status:** ✅ Ready | **Idempotent:** Yes | **Duplicates:** Prevented

---

## 📍 What Was Built

### 1 Agent + 3 Manifests + 3 Guides

| File | Type | Purpose | Key Feature |
|------|------|---------|---|
| **cortex-documentation.md** | Agent | Main orchestrator | 8 commands, idempotent |
| **content-registry.yaml** | Manifest | Content tracking | Duplicate prevention |
| **file-placement-policy.yaml** | Manifest | Governance rules | SSOT compliance |
| **file-manifest.yaml** | Manifest | File tracking | Progress reporting |
| **CORTEX-DOCUMENTATION-AGENT-SUMMARY.md** | Guide | System overview | How it works |
| **README-CORTEX-DOCUMENTATION-SYSTEM.md** | Guide | Quick start | Integration reference |

---

## 🎯 Core Commands

```
/docs-status        Assess current structure
/docs-plan          Show implementation roadmap
/docs-migrate       Migrate files to target structure
/docs-validate      Check links & duplicates
/docs-consolidate   Merge overlapping files
/docs-cleanup       Archive obsolete files
/docs-generate      Create/update single doc
/docs-lint          Validate format & consistency
```

---

## 🔄 Execution Pattern (Safe to Repeat)

### Run 1: Assess
```bash
/docs-status
# Output: "180 files found, 100 to archive, 80 to migrate"
```

### Run 2-N: Migrate (Any Order)
```bash
/docs-migrate 01-getting-started
/docs-migrate 02-architecture
/docs-migrate 03-api-reference
# Each idempotent → safe to repeat
```

### Run N+1: Validate
```bash
/docs-validate
# Output: "0 duplicates, 0 broken links ✓"
```

### Run N+2: Verify Idempotency
```bash
/docs-status
# Output: "No changes needed, all current ✓"
```

---

## 🚫 Prevents

| Issue | Prevention |
|-------|---|
| Duplicate files | Content hash registry |
| Data loss | Archive preservation |
| Broken links | Link validator |
| Repeated work | Registry tracks completion |
| Governance violations | Policy enforcement |
| Lost changes | Idempotent merges |
| Sync drift | Single registry SSOT |

---

## 🔐 Safety Guarantees

✅ **Idempotent:** Repeat any command, same result  
✅ **Non-destructive:** Archive preservation, no deletions  
✅ **No duplicates:** Hash-based detection  
✅ **No data loss:** Full audit trail  
✅ **Governance:** Policy enforced automatically  
✅ **Reversible:** Archives contain originals  

---

## 📊 Target State

```
Before: 180+ chaotic files
After:  80 production files

Structure:
├─ 01-getting-started/      (4 docs)
├─ 02-architecture/         (9 docs)
├─ 03-api-reference/        (11 docs)
├─ 04-guides/               (28 docs)
├─ 05-reference/            (6 docs)
├─ 06-tutorials/            (8 docs)
├─ 07-contributing/         (6 docs)
└─ _archive/               (100+ docs, historical)
```

---

## 🔗 File References

```
Agent Definition:
  .github/agents/cortex-documentation.md
  
Manifests (Stateful):
  docs/_manifests/content-registry.yaml
  docs/_manifests/file-placement-policy.yaml
  docs/_manifests/file-manifest.yaml

Documentation:
  .github/prompts/cortex-doc.prompt.md (strategy)
  .github/agents/CORTEX-DOCUMENTATION-AGENT-SUMMARY.md (detailed)
  .github/agents/README-CORTEX-DOCUMENTATION-SYSTEM.md (guide)
```

---

## ⚙️ How It Works (Simplified)

```
1. /docs-status
   Load Registry → Scan Docs → Compare → Report

2. /docs-migrate <section>
   Check Registry → Load Sources → Merge → Hash → Update Registry

3. /docs-validate
   Scan Files → Check Hashes → Validate Links → Report

4. /docs-status (repeat)
   Registry shows no changes → "Already current ✓"
```

---

## 🎓 Key Concepts

### SSOT (Single Source of Truth)
- One registry controls all state
- All decisions based on registry
- Registry updated after each operation

### Idempotent
- Can repeat operations safely
- Second run detects "already done"
- Always converges to same final state

### Content Hashing
- Every file gets MD5/SHA256 hash
- Duplicates detected by hash match
- Prevents creating duplicate files

### Registry Tracking
- Content registry = state machine
- Tracks all files, topics, status
- Updated after each operation

### Archive Preservation
- Original files moved to archive
- Full metadata preserved
- Can reconstruct if needed

---

## 🚀 Quick Start

**1. Initialize**
```bash
/docs-status
# See: "180 files, planning migration..."
```

**2. Plan**
```bash
/docs-plan
# See: "Prioritized roadmap..."
```

**3. Migrate**
```bash
/docs-migrate 01-getting-started
# See: "Migrated 4 files..."
```

**4. Validate**
```bash
/docs-validate
# See: "0 duplicates, 0 broken links ✓"
```

**5. Complete**
```bash
/docs-status
# See: "Documentation restructuring complete ✓"
```

---

## 📋 Execution Checklist

- [ ] Read `.github/agents/cortex-documentation.md`
- [ ] Review `docs/_manifests/` files (manifests)
- [ ] Run `/docs-status` (assess)
- [ ] Run `/docs-plan` (roadmap)
- [ ] Run `/docs-migrate 01-getting-started` (first migration)
- [ ] Run `/docs-validate` (verify no issues)
- [ ] Run `/docs-migrate 02-architecture` (continue)
- [ ] Run `/docs-migrate 03-api-reference` (continue)
- [ ] Run `/docs-migrate 04-guides` (continue)
- [ ] Run `/docs-cleanup` (archive)
- [ ] Run `/docs-validate` (final check)
- [ ] Run `/docs-status` (verify complete)

---

## 🔄 Repeated Execution Example

```
Day 1:
  /docs-status → "180 files, needs migration"
  /docs-migrate 01-getting-started → "Migrated 4 files"

Day 2:
  /docs-status → "176 files remaining"
  /docs-migrate 02-architecture → "Migrated 8 files"

Day 3:
  /docs-status → "168 files remaining"
  /docs-migrate 03-api-reference → "Migrated 11 files"

Day 4:
  /docs-status → "157 files remaining"
  /docs-migrate 01-getting-started (again)
  # Output: "Already current, no changes needed"

Day 5:
  /docs-status → "All done ✓"
```

---

## ✨ What Makes It Special

1. **No Duplicates:** Hash registry prevents creating copies
2. **Safe to Repeat:** Every command idempotent
3. **No Data Loss:** Archive preservation with metadata
4. **Self-Aware:** Registry tracks exact state
5. **Policy-Enforced:** Governance rules automatic
6. **Auditable:** Full operation log maintained
7. **Atomic:** All-or-nothing file operations
8. **Smart Merge:** Intelligently consolidates files

---

**Status:** ✅ System Complete & Ready for Production Execution

For detailed docs, see:
- `CORTEX-DOCUMENTATION-AGENT-SUMMARY.md` (detailed overview)
- `README-CORTEX-DOCUMENTATION-SYSTEM.md` (integration guide)
- `cortex-documentation.md` (agent commands)

