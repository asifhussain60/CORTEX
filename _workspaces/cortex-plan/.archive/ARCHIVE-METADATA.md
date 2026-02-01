# Archive Metadata
**Date:** 2026-02-01  
**Reason:** Superseded by PHASE-18-ENTERPRISE-DASHBOARD-SYSTEM.yaml  
**Archived By:** CORTEX Architect (cortex-architect.prompt.md)

---

## Archived Files

| File | Original Purpose | Superseded By | Archive Reason |
|------|------------------|---------------|----------------|
| PHASE-14-LENS-DASHBOARD.yaml | Original LENS dashboard plan | PHASE-18-ENTERPRISE-DASHBOARD-SYSTEM.yaml | Phase 18 provides enterprise-scale replacement with single adaptive template |
| PHASE-14-LENS-DASHBOARD-IMPLEMENTATION.yaml | LENS dashboard implementation details | PHASE-18-ENTERPRISE-DASHBOARD-SYSTEM.yaml | Superseded by Phase 18 architecture |
| PHASE-14.5-UNIVERSAL-DASHBOARD.yaml | Universal dashboard attempt | PHASE-18-ENTERPRISE-DASHBOARD-SYSTEM.yaml | Phase 18 implements single adaptive template (approved approach) |
| PHASE-14-ADAPTIVE-DASHBOARD-COMPARISON.md | Comparison of dashboard approaches | PHASE-18-ENTERPRISE-DASHBOARD-SYSTEM.yaml | Decision made: single adaptive template |
| PHASE-14-QUICK-REFERENCE.md | Phase 14 quick reference | PHASE-18-ENTERPRISE-DASHBOARD-SYSTEM.yaml (Phase 18.8) | Superseded by Phase 18 implementation |
| PHASE-14-LENS-DASHBOARD-QUICK-REF.md | LENS dashboard quick ref | PHASE-18-ENTERPRISE-DASHBOARD-SYSTEM.yaml | Superseded |
| PHASE-14-PROMPT-CONSOLIDATION.yaml | Prompt consolidation plan | Completed in Phase 8.x | Separate concern, completed |

---

## Restoration Instructions

If any archived file is needed:
```bash
cd D:\PROJECTS\CORTEX\_workspaces\cortex-plan\.archive
# Copy desired file back to parent directory
cp <filename> ../
```

## Git History Preservation

All files remain in git history:
```bash
git log --follow -- _workspaces/cortex-plan/<filename>
```

---

## Phase 18 References

Phase 18 declares dependencies on:
- PHASE-15-STATIC-REPO-VISUALIZATION.yaml (kept - complementary)
- PHASE-14-LENS-DASHBOARD-IMPLEMENTATION.yaml (archived - superseded)

Phase 18 provides:
- Single adaptive template (PHASE-14.5 goal achieved)
- Enterprise-scale dashboard (PHASE-14 goal expanded)
- Automated generation system (Phase 18.8)
- Comprehensive testing (all tabs + HTML lint)

---

**Archive Status:** Complete  
**Active Plan:** PHASE-18-ENTERPRISE-DASHBOARD-SYSTEM.yaml
