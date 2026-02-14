# Deprecated Wave Files

**Deprecated:** 2026-02-14  
**Reason:** CORE-042 simplified hierarchy to PHASE→STAGE→TASK  
**Authority:** User request + system simplification

---

## 📋 What Happened

The "Wave" terminology has been deprecated in favor of simpler PHASE→STAGE→TASK hierarchy.

**Old Hierarchy (Complex):**
```
EPIC → FEATURE → PHASE → STAGE → TASK (5 levels)
Wave (misused as both strategic and tactical unit)
```

**New Hierarchy (Simple):**
```
PHASE → STAGE → TASK (3 levels)
- PHASE: 1-4 weeks, work milestone (P-XXX)
- STAGE: 2-5 days, work unit (S-1, S-2, etc.)
- TASK: 2-8 hours, atomic work (T-001, T-002, etc.)
```

---

## 🗂️ File Preservation

**All files preserved for historical reference:**
- Wave YAML files
- Wave execution guides
- Wave completion reports
- Wave consolidation summaries

**Nothing deleted** - this is a non-destructive reorganization.

---

## 🔄 Migration Guide

**To find equivalent phase:**
1. Check `WAVE-TO-PHASE-MAPPING.yaml` in this directory
2. Search by wave ID (e.g., "WAVE-A" → "PHASE-10")
3. All metadata preserved (tests, commits, dates, hashes)

**Example:**
```yaml
- old_id: "Wave 1"
  new_id: "PHASE-01"
  name: "Foundation Security"
  tests: 336
  commits: "15+"
  date: "2026-02-13"
  git_hash: "07c84a4c1"
```

---

## 📚 Active Phase Files

**New location:** `cortex-registry/_cortex-master/work/phases/`

**Structure:**
```
work/phases/
├── active/          ← Current phases
│   ├── phase-48-holistic-validation.yaml
│   ├── phase-76-production-foundation.yaml
│   └── ENH-082-response-templates.yaml
└── completed/       ← Finished phases
    ├── 2026/
    └── wave-o/      ← Legacy wave-o preserved
```

---

## ✅ Benefits of Simplification

1. **Universal:** Works across ALL orchestrators (planning, TDD, interaction)
2. **Intuitive:** No confusion about Epic vs Feature vs Wave
3. **Aligned:** Matches existing phase-01, phase-02 structure
4. **Simpler:** 3 levels instead of 5
5. **Clear:** Each level has distinct scope and duration

---

## 🔍 Finding Historical Data

**All wave execution history preserved in:**
- Git commits (search: `git log --grep="WAVE"`)
- This archive directory
- `history/baselines/completed-waves/`
- README.md "Phase Status Summary" section

**Example git search:**
```bash
git log --oneline --grep="WAVE-A"
git log --oneline --grep="Wave 7"
```

---

**Last Updated:** 2026-02-14  
**Migration Tool:** WAVE-TO-PHASE-MAPPING.yaml  
**Questions:** See README.md or CORTEX.prompt.md
