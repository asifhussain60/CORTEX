# Archive-Aware Roadmap Guide
**Version:** v2.1-lean  
**Last Updated:** January 19, 2026

---

## Quick Reference

The CORTEX roadmap has been consolidated into a **lean master YAML** with **archive awareness** to prevent duplicate work.

### Key Principle
> **Before implementing ANY phase, check if it's already in the archives**

---

## Finding Archived Phases

### Method 1: Check Master YAML Archives Section
```bash
cat _workspaces/roadmap/cortex-master.yaml | grep -A 50 "archive_references:"
```

### Method 2: Direct Archive File Inspection
```bash
# View all locked phases (PHASE-01-04, PHASE-21-22)
cat _archives/v2.1/cortex-master-v2.1-locked-phases.yaml

# View all remediation phases
cat _archives/v2.1/cortex-master-v2.1-remediation-phases.yaml

# View all enhancement phases
cat _archives/v2.1/cortex-master-v2.1-enhancement-phases.yaml
```

### Method 3: Check Archive Phases Directory
```bash
ls -la _archives/v2.1/phases/
```

---

## Archived Phases by Category

### Locked Phases (IMMUTABLE - 95 ACs)
Located: `_archives/v2.1/cortex-master-v2.1-locked-phases.yaml`

| Phase | Title | ACs | Status | Locked |
|-------|-------|-----|--------|--------|
| PHASE-01 | Governance Foundation & Core Architecture | 36 | ✅ COMPLETED | YES |
| PHASE-02-CODEBASE-COHERENCE | Codebase Coherence & Import Foundation | 3 | ✅ COMPLETED | YES |
| PHASE-03-CORE-ARCHITECTURE | Core Architecture (Extended) | 6 | ✅ COMPLETED | YES |
| PHASE-04-SAFETY-RELIABILITY | Safety & Reliability Hardening | 12 | ✅ COMPLETED | YES |
| PHASE-21-INTELLIGENT-KNOWLEDGE-PROTOCOL | Intelligent Knowledge Protocol | 21 | ✅ COMPLETED | YES |
| PHASE-22-MCP-PROTOCOL-COMPLIANCE | MCP Protocol Compliance | 17 | ✅ COMPLETED | YES |

**Total:** 95 ACs, all locked, 2,660+ tests (100% pass rate)

### Remediation Phases (IMMUTABLE - 71 ACs)
Located: `_archives/v2.1/cortex-master-v2.1-remediation-phases.yaml`

| Phase | Title | ACs | Status | Type |
|-------|-------|-----|--------|------|
| PHASE-DOC-REMEDIATION | Documentation Remediation | 8 | ✅ COMPLETED | Bug Fix |
| PHASE-REMEDIATION-01 | Core Governance Fixes | 11 | ✅ COMPLETED | Bug Fix |
| PHASE-REMEDIATION-02 | Import Path Resolution | 11 | ✅ COMPLETED | Bug Fix |
| PHASE-REMEDIATION-03 | Nested Structure Migration | 8 | ✅ COMPLETED | Bug Fix |
| PHASE-REMEDIATION-04 | AST Integration Fixes | 6 | ✅ COMPLETED | Bug Fix |
| PHASE-REMEDIATION-05 | Brittleness & Hallucination | 6 | ✅ COMPLETED | Bug Fix |
| PHASE-REMEDIATION-06 | Orchestrator Reliability | 4 | ✅ COMPLETED | Bug Fix |
| PHASE-REMEDIATION-07 | MCP Tool Exposure | 3 | ✅ COMPLETED | Bug Fix |
| PHASE-REMEDIATION-08 | Knowledge Graph Consistency | 10 | ✅ COMPLETED | Bug Fix |
| PHASE-REMEDIATION-09 | Challenge Integration | 3 | ✅ COMPLETED | Bug Fix |
| PHASE-30-DOCUMENTATION-REMEDIATION | Doc Organization & Archive Refs | 1 | ✅ COMPLETED | Bug Fix |

**Total:** 71 ACs, all locked, 100% complete

### Enhancement Phases (IMMUTABLE - 7 ACs)
Located: `_archives/v2.1/cortex-master-v2.1-enhancement-phases.yaml`

| Phase | Title | ACs | Status | Feature |
|-------|-------|-----|--------|---------|
| PHASE-ENHANCEMENT-01 | DevX Framework & Orchestration | 4 | ✅ COMPLETED | Enhancement |
| PHASE-ENHANCEMENT-02 | Response Composition & Headers | 2 | ✅ COMPLETED | Enhancement |
| PHASE-ENHANCEMENT-03 | Continuation Protocol | 1 | ✅ COMPLETED | Enhancement |

**Total:** 7 ACs, all locked, 100% complete

---

## Active Phases in Lean Master

Located: `_workspaces/roadmap/cortex-master.yaml`

| Phase | Status | ACs | Priority |
|-------|--------|-----|----------|
| PHASE-05 through PHASE-20 | Various | ~120 | P0-P2 |
| PHASE-23 | Active | TBD | P1 |
| PHASE-30 (NEW) | Design Complete | 6 | P0 |
| PHASE-PARALLEL | Active | 3 | P2 |
| PHASE-DEPLOYMENT-ENHANCED | TBD | TBD | P1 |
| PHASE-GOVERNANCE-METRICS | TBD | TBD | P2 |
| PHASE-ONBOARDING-ORCHESTRATOR | TBD | TBD | P1 |

---

## Duplication Prevention Workflow

### Before Starting ANY Phase

**Step 1: Check Archive References**
```yaml
# In cortex-master.yaml, look for:
archive_references:
  locked_phases:
    file: _archives/v2.1/cortex-master-v2.1-locked-phases.yaml
    phases: 
      - PHASE-01
      - PHASE-02-CODEBASE-COHERENCE
      - PHASE-03-CORE-ARCHITECTURE
      - ...
```

**Step 2: Search for Phase Name**
- If found in `archive_references` → Phase is COMPLETE ✅
- If found in `cortex-master.yaml` `phase_tracker` → Check status
- If not found anywhere → Phase needs to be created

**Step 3: If Phase is Archived**
- DO NOT re-implement
- Reference archived phase specs instead
- Cite archive file in documentation
- Example: "Based on PHASE-01 (see _archives/v2.1/cortex-master-v2.1-locked-phases.yaml)"

### Example: Checking PHASE-01

```bash
# Step 1: Search in lean master
grep "PHASE-01" _workspaces/roadmap/cortex-master.yaml

# Result: Not found (it's archived)

# Step 2: Check archive references
grep -A 3 "archive_references:" _workspaces/roadmap/cortex-master.yaml | grep PHASE-01

# Result: Found in locked_phases archive

# Step 3: View archived phase details
grep -A 100 "PHASE-01:" _archives/v2.1/cortex-master-v2.1-locked-phases.yaml

# RESULT: Phase is LOCKED, cannot be modified
```

---

## Archive File Structure

### Each Archive File Contains

```yaml
metadata:           # Overall project metadata
governance:         # Governance rules (shared across all)
phase_tracker:      # Only phases for this archive
  PHASE-XX:         # Phase definition
    title: ...
    description: ...
    ac_ids: N
    completed_ac_ids: N
    status: COMPLETED
    locked: true
    acceptance_criteria:
      - ac_id: AC-DOMAIN-NNN-NN
        title: ...
        status: COMPLETE
        tests: [...]
        git_checkpoint: ...
```

### Accessing Specific AC-ID from Archive

```bash
# Find which archive has AC-ID
grep -r "AC-AR-001-01" _archives/v2.1/

# Result: cortex-master-v2.1-locked-phases.yaml

# Extract AC details
grep -A 30 "ac_id: AC-AR-001-01" _archives/v2.1/cortex-master-v2.1-locked-phases.yaml
```

---

## Documentation Location Changes

### Before Consolidation
```
_workspaces/roadmap/
├── *.md (reports)
└── reports/
```

### After Consolidation
```
docs/
├── *.md (6 root documentation files)
├── reports/ (50+ report files)
│   ├── *.md
│   └── _archived_reports/ (20+ historical)
└── analysis/
```

### Finding Documentation

**For Latest Reports:**
```bash
ls -la /Users/asifhussain/PROJECTS/CORTEX/docs/reports/
```

**For Historical Analysis:**
```bash
ls -la /Users/asifhussain/PROJECTS/CORTEX/docs/reports/_archived_reports/
```

**For Consolidation Details:**
```bash
cat /Users/asifhussain/PROJECTS/CORTEX/docs/CONSOLIDATION-REPORT-20260119.md
```

---

## Git Commit & History

### Consolidation Checkpoint
```bash
git log --oneline | grep -i consolidat

# Expected output (when committed):
# abc1234 feat: consolidate master.yaml - v2.1-lean (29% reduction, archive-aware)
```

### Reverting Consolidation (if needed)
```bash
# Find the commit before consolidation
git log --oneline

# Restore original files
git checkout <commit-hash>~1 -- _workspaces/roadmap/cortex-master.yaml
```

---

## Governance Compliance

### Archive Awareness = No Duplication Risk

✅ **CORE-022** (Version Control Integration)
- Archive structure tracked in Git
- Immutable archives cannot be accidentally modified

✅ **CORE-028** (Naming Conventions)
- Archive files follow kebab-case naming
- Phase identifiers consistent throughout

✅ **CORE-001-028** (All Governance Rules)
- Archives inherit all governance rules
- AC-IDs unchanged, audit trail continues
- Hash chain integrity maintained

---

## Troubleshooting

### Q: I can't find a phase in the lean master
**A:** Check `archive_references` → it's likely archived. View the archive file directly.

### Q: Can I modify a locked archived phase?
**A:** No. Locked phases are IMMUTABLE. Create a new remediation phase if fixes are needed.

### Q: How do I know which file has AC-ID AC-GV-001-01?
**A:** Search all archives:
```bash
grep -r "AC-GV-001-01" _archives/v2.1/
```

### Q: Where did the reports go?
**A:** Moved to `/docs/reports/` for unified documentation access.

### Q: Why is master.yaml smaller?
**A:** Completed phases (173 ACs) moved to archives. Only active phases remain for faster navigation.

### Q: Will this affect the governance audit?
**A:** No. Audit trail (governance.db) is unchanged. Hash chain integrity maintained.

---

## Key Files Reference

| File/Location | Purpose | Status |
|---------------|---------|--------|
| `_workspaces/roadmap/cortex-master.yaml` | Active phases only | ✅ Lean (5,898 lines) |
| `_archives/v2.1/cortex-master-v2.1-locked-phases.yaml` | 6 locked phases (95 ACs) | 🔒 Immutable |
| `_archives/v2.1/cortex-master-v2.1-remediation-phases.yaml` | 11 remediation phases (71 ACs) | 🔒 Immutable |
| `_archives/v2.1/cortex-master-v2.1-enhancement-phases.yaml` | 3 enhancement phases (7 ACs) | 🔒 Immutable |
| `_archives/v2.1/phases/` | 10 archived phase YAML files | 📦 Reference |
| `/docs/` | All documentation (unified) | 📚 Central Hub |
| `governance.db` | Audit trail (unchanged) | ✅ Intact |

---

## Summary

✅ **Consolidation Successful**
- Master YAML 29% smaller
- Archives immutable & accessible
- Duplication prevention enabled
- Documentation centralized
- Governance intact

📌 **Always Check Archives First** before implementing any phase

🔒 **Locked Phases Cannot Be Modified** - they're production-locked

💾 **All Data Preserved** - 540 ACs still accessible

---

For details, see: `/Users/asifhussain/PROJECTS/CORTEX/docs/CONSOLIDATION-REPORT-20260119.md`
