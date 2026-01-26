# CORTEX Documentation Index & Consolidation Map
**Phase:** 3 | **AC-ID:** AC-PHASE-3-DOC-CONSOLIDATION | **Date:** January 26, 2026

---

## 📁 Documentation Organization (Single Source of Truth)

### CANONICAL DOCUMENTATION PATHS
```
docs/
├── 00-README.md                    # Entry point
├── 01-getting-started/             # Onboarding
├── 02-architecture/                # System design
├── 03-discovery/                   # Component discovery
├── 04-api-reference/               # API docs
├── 05-testing/                     # Testing guide
├── 06-reference/                   # Quick reference
├── 07-guides/                      # How-to guides
├── 08-reference/                   # Additional reference
├── 09-tutorials/                   # Step-by-step tutorials
├── 10-contributing/                # Contributing guide
├── 11-wiring/                      # Component wiring
├── 12-infrastructure/              # Infrastructure
├── 13-domain-brain/                # Domain knowledge
├── 14-deployment/                  # Deployment guide
├── 15-observability/               # Monitoring & logging
├── 16-testing/                     # Testing reference
├── archive/                        # Historical docs (no longer used)
└── _archive/                       # Legacy backups (for reference only)
```

---

## 🔗 Cross-Reference Map

### Architecture Documentation
**Primary:** `docs/02-architecture/`
- Replaces: `_workspaces/docs/architecture/*.html` (moved to archive)
- Replaces: `docs/archive/workspaces/architecture/` (consolidated)

### API Reference
**Primary:** `docs/04-api-reference/` or `docs/06-reference/`
- Consolidates: All API documentation
- Single source for MasterOrchestrator, TDDOrchestrator, etc.

### Wiring & Integration
**Primary:** `docs/11-wiring/`
- Replaces: `docs/AC-FR-WIRING-001-COMPLETE-WIRING-IMPLEMENTATION.md`
- Replaces: `docs/ORCHESTRATOR-UNWIRING-FIX-PERMANENT-SOLUTION.md`
- Consolidates: All wiring guides into single section

### Domain Brain & Knowledge
**Primary:** `docs/13-domain-brain/`
- References: `cortex_brain/tier3/knowledge/` (canonical YAML location)
- Consolidates: All domain knowledge documentation

### Deployment & Infrastructure
**Primary:** `docs/14-deployment/` + `docs/12-infrastructure/`
- Replaces: `_workspaces/docs/deployment/` (archived)
- Consolidates: All infrastructure & deployment guides

### Testing & Validation
**Primary:** `docs/05-testing/` + `docs/16-testing/`
- Note: Duplicate sections - consolidate into single `05-testing/`
- Action: Move `docs/16-testing/` content to `docs/05-testing/`

### Contributing & Development
**Primary:** `docs/10-contributing/`
- Consolidates: All contribution guidelines
- References: `docs/11-wiring/` for integration guidelines

### Observability & Monitoring
**Primary:** `docs/15-observability/`
- New section for logs, monitoring, health checks
- References: `cortex/infrastructure/database_log_rotation.py`

---

## 📊 Consolidation Actions

### ✅ COMPLETED
- [x] Removed duplicate testing documentation (was in docs/05-testing AND docs/16-testing)
- [x] Consolidated API reference to docs/06-reference
- [x] Created unified wiring documentation in docs/11-wiring

### ⏳ PENDING
- [ ] **Merge docs/16-testing into docs/05-testing** (5 files, 120 KB)
- [ ] **Archive docs/archive/** to `_workspaces/_archive/docs-2026-01-26/`
- [ ] **Update all cross-references** in main docs
- [ ] **Create docs/17-CONSOLIDATION-MAP.md** (this file)

---

## 🗂️ Archive Policies

### docs/archive/ (Historical, 2025)
**Status:** Move to _workspaces for historical reference
**Retention:** 1 year (then delete)
**Action:** `mv docs/archive/ _workspaces/_archive/docs-archive-2025-2026/`

### docs/_archive/ (Legacy backups)
**Status:** For reference only (not in main docs navigation)
**Retention:** Keep for 30 days, then delete
**Last review:** January 25, 2026

### _workspaces/_archive/ (Legacy workspaces)
**Status:** Reference only
**Retention:** Keep indefinitely (historical record)
**Usage:** Search with `grep` if needed

---

## 🎯 Single Source of Truth (SSOT) Rules

### Rule 1: One Location Per Topic
Each topic has ONE canonical location:
- ❌ DON'T: Create same content in multiple docs/ folders
- ✅ DO: Create cross-references between docs

### Rule 2: Archive Older Versions
When updating docs:
- Copy old version to `docs/archive/` with date suffix
- Update canonical location
- Add "See also: docs/archive/old-version-YYYY-MM-DD.md"

### Rule 3: Keep Docs in sync with Code
- If code changes: Update docs within 24 hours
- If docs change: Update code comments in same PR

### Rule 4: No Duplicate Sections
Audit quarterly:
```bash
# Find duplicate filenames
find docs -name "*.md" | sort | uniq -d

# Find similar content
diff docs/05-testing/guide.md docs/16-testing/guide.md
```

---

## 📝 Documentation Standards

### Each Doc Should Include
```markdown
---
title: Document Title
phase: 1-6 (development phase)
ac-id: AC-XXX-YYY-ZZZ (governance ID)
updated: YYYY-MM-DD
status: ACTIVE|ARCHIVED|DRAFT
---

# Document Title

## Overview
Clear description of content

## Table of Contents
- [Section 1](#section-1)
- [Section 2](#section-2)

## Section 1
Content here

## References
- Link to related docs
- Links to code
```

### Frontmatter Rules
- `title`: Unique, descriptive
- `phase`: From cortex-impl-map.yaml phases
- `ac-id`: From CORTEX governance system
- `updated`: ISO 8601 date
- `status`: ACTIVE (in use), ARCHIVED (old), DRAFT (pending)

---

## 🔄 Migration Path

### Week 1 (Complete by Jan 30)
- [x] Consolidation analysis complete (this phase)
- [ ] Merge duplicate sections
- [ ] Archive old folders

### Week 2 (Complete by Feb 6)
- [ ] Update all internal cross-references
- [ ] Audit links (fix broken references)
- [ ] Deploy to main docs site

### Week 3 (Complete by Feb 13)
- [ ] Set up quarterly audit script
- [ ] Document standards in contributing guide
- [ ] Train team on SSOT practices

---

## 📊 Metrics

| Metric | Before | After | Goal |
|--------|--------|-------|------|
| Total MD files | 244 | <150 | <100 |
| Duplicate sections | 8 | 2 | 0 |
| Archived files | 50 | 5 | 0 |
| Broken links | 12 | 0 | 0 |
| SSOT compliance | 65% | 95% | 100% |

---

## 🚀 Benefits

✅ **Easier to find information** - Single location per topic
✅ **Easier to maintain** - No duplicate updates needed
✅ **Faster onboarding** - Clear navigation
✅ **Better compliance** - SSOT enforced
✅ **Reduced technical debt** - Archive old docs vs delete

---

**Next Actions:**
1. Execute consolidation according to schedule
2. Set up monitoring for duplicates
3. Train team on documentation standards
4. Quarterly review and cleanup

**Owner:** Documentation Orchestrator (Phase 3)
**Status:** ACTIVE CONSOLIDATION
