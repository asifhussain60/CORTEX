# Source Plan References

**Created:** January 2, 2026  
**Updated:** January 2, 2026 (Pre-archive review)
**Purpose:** Document the source plans that informed this holistic refactor

---

## ✅ Plans Being Consolidated

This holistic refactor consolidates the following plans:

### 1. autonomous-orchestrator-v5 ✅ CAPTURED
**Location:** `cortex-brain/documents/planning/active/autonomous-orchestrator-v5/`

**Key Documents:**
- `00-MASTER-PLAN-V5.md` - Architecture blueprint defining pure autonomous approach
- `architecture/option-1-analysis.md` - Detailed analysis of why pure autonomous is better
- `architecture/database-schema.md` - SQLite schema for planning state management
- `architecture/config-specification.md` - Config-only manifest format specification

**Captured In Holistic Refactor:**
- ✅ Pure autonomous principles → `architecture/pure-autonomous-principles.md`
- ✅ Database schema → `architecture/database-schema.md`
- ✅ Config specification → `architecture/config-specification.md`
- ✅ Implementation phases → `phases/bootstrap-strategy.md`
- ✅ Migration strategy → `phases/migration-roadmap.md`

### 2. auto-orch-v5-impl ✅ CAPTURED
**Location:** `cortex-brain/documents/planning/active/auto-orch-v5-impl/`

**Key Documents:**
- `mst-pure-autonomous.md` - Implementation plan with 11 phases
- `artifacts/file-name-rules.md` - Filename validation specification (≤20 chars)
- `context/source-plan.md` - Alignment with autonomous-v5

**Captured In Holistic Refactor:**
- ✅ 11 phases → Consolidated into bootstrap (Phases 0-4) + migration (Phases 5-10)
- ✅ Filename validation → Incorporated into Phase 0 foundation setup
- ✅ MCP tool infrastructure → `phases/bootstrap-strategy.md` Phase 1
- ✅ Implementation details → `00-MASTER-PLAN-V5.md`

---

## 🔄 Plans NOT Being Consolidated (Different Scope)

### 3. cortex-documentation ⏸️ SEPARATE PLAN
**Location:** `cortex-brain/documents/planning/active/cortex-documentation/`

**Purpose:** Glassmorphism UI standardization for documentation website

**Why Separate:**
- Completely different scope (UI design, not architecture)
- Already in progress (Phase 1 complete)
- No overlap with v5 orchestrator refactor
- Should remain as independent plan

**Status:** Keep as separate active plan

### 4. level-2-glassmorphism-standardization ⏸️ CONTINUATION MARKER
**Location:** `cortex-brain/documents/planning\active\level-2-glassmorphism-standardization/`

**Purpose:** Placeholder for continuing glassmorphism work

**Contents:** Empty `CONTINUE-NEXT-CHAT.md` file

**Action:** Can be deleted (superseded by cortex-documentation plan)

---

## Consolidation Strategy

**Problem:** Two separate plans with overlapping content and unclear execution order.

**Solution:** Consolidate into single holistic plan with bootstrap approach.

**Bootstrap Rationale:**
1. Planning System v5 doesn't exist yet
2. We need Planning v5 to create high-quality migration plans
3. Therefore: Build Planning v5 first, then use it to generate migration plans

**Execution Flow:**
```
Phase 0-4: Bootstrap Planning System v5 (manual planning)
           ↓
Phase 5: Use Planning v5 to generate migration plans
           ↓
Phase 6-10: Execute migrations using generated plans
```

---

## Alignment Verification

### Architecture Alignment
- ✅ Pure autonomous approach (Option 1 from v5 plan)
- ✅ MCP tool infrastructure (Phase 1 from impl plan)
- ✅ SQLite state database (Phase 2 from impl plan)
- ✅ BaseOrchestrator v4.1 (Phase 3 from impl plan)
- ✅ Planning Orchestrator v5 (Phase 4 from impl plan)

### Migration Alignment
- ✅ ADO Orchestrator v2 (from v5 plan)
- ✅ Vacuum Orchestrator v2 (from v5 plan)
- ✅ Cleanup Orchestrator v2 (from v5 plan)
- ✅ GUIDED orchestrator assessment (from holistic analysis)

### Standards Alignment
- ✅ Filename validation (≤20 chars from impl plan)
- ✅ Config-only manifests (from v5 plan)
- ✅ Template-driven output (from v5 plan)
- ✅ SKULL rule enforcement (from brain-protection-rules.yaml)

---

## Deviations from Source Plans

### Bootstrap Approach (NEW)
**Deviation:** Source plans assumed manual planning for all migrations.  
**Rationale:** Using Planning v5 to plan migrations is more efficient and validates the system.

### Holistic Agent Integration (EXPANDED)
**Deviation:** Source plans focused on orchestrators only.  
**Rationale:** Agent layer also suffers from hybrid ambiguity and should be addressed.

### GUIDED Orchestrator Assessment (NEW)
**Deviation:** Source plans assumed all orchestrators convert to autonomous.  
**Rationale:** Some workflows (TDD, Refinement) may benefit from remaining guided.

---

## Archive Plan

**After verification, the following will be archived:**

1. **autonomous-orchestrator-v5** → `cortex-brain/archives/planning/2026-01-02/autonomous-orchestrator-v5/`
2. **auto-orch-v5-impl** → `cortex-brain/archives/planning/2026-01-02/auto-orch-v5-impl/`
3. **level-2-glassmorphism-standardization** → Delete (empty placeholder)

**Remaining Active Plans:**
- ✅ `cortex-v5-holistic-refactor/` - Single source of truth for v5 refactor
- ✅ `cortex-documentation/` - Separate UI design plan (different scope)

---

**Verification Date:** January 2, 2026  
**Verified By:** CORTEX Plan Consolidation  
**Status:** ✅ Ready for archival

## Status of Source Plans

**After This Plan Completes:**
- Archive source plans to `cortex-brain/archives/planning/v4-plans/`
- Extract lessons learned into knowledge library
- Update references in documentation
- Keep for historical reference

**During This Plan:**
- Use as reference for architecture decisions
- Cross-reference for validation
- Ensure no requirements missed

---

## Cross-Reference Map

| Source Plan Section | Holistic Plan Phase |
|---------------------|---------------------|
| v5: Foundation | Phase 0: Foundation Setup |
| v5: MCP Tool Infrastructure | Phase 1: MCP Tool Infra |
| v5: Planning State Database | Phase 2: State Database |
| v5: BaseOrchestrator v4.1 | Phase 3: BaseOrch v4.1 |
| v5: Planning Orchestrator v5 | Phase 4: PlanOrch v5 |
| v5: Config-Only Manifests | Integrated in Phase 4 |
| v5: ADO Orchestrator v2 | Phase 6: Migration Execution |
| v5: Vacuum Orchestrator v2 | Phase 6: Migration Execution |
| v5: Cleanup Orchestrator v2 | Phase 6: Migration Execution |
| v5: Testing & Validation | Phase 8: Testing & Validation |
| v5: Migration & Documentation | Phase 9: Documentation |
| v5: REFACTOR & Cleanup | Phase 10: REFACTOR & Cleanup |
| impl: Filename Validation | Phase 0: Task 0.2 |

---

**Alignment Status:** ✅ VERIFIED - All source plan requirements captured in holistic plan.
