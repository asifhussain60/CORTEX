# Migration Plans Roadmap

**Document Type:** Migration Strategy  
**Plan:** CORTEX v5.0 Holistic Refactor  
**Created:** January 2, 2026

---

## 🎯 Overview

After Planning System v5 bootstrap completes, use the new planning system to generate detailed migration plans for all remaining orchestrators and agents.

---

## 📋 Migration Plan List

### 1. ADO Orchestrator v2 Migration

**Command:** `/CORTEX Plan ADO Orchestrator v2 migration`

**Scope:**
- Convert `ado-planning-manifest.yaml` to config-only format
- Implement pure Python work item generation logic
- Add database state tracking for ADO operations
- Integrate with MCP tool invocation
- Create templates for:
  - User stories
  - Features
  - Acceptance criteria
  - Estimation reports

**Estimated Duration:** 3 days

**Success Criteria:**
- User runs `ado story [feature]`
- ADO Orchestrator v2 generates work items autonomously
- Zero CORTEX execution (hand-off only)
- Output consistent and high-quality

---

### 2. Vacuum Orchestrator v2 Migration

**Command:** `/CORTEX Plan Vacuum Orchestrator v2 migration`

**Scope:**
- Convert `cortex-vacuum.prompt.md` to config-only manifest
- Implement Python-owned filesystem operations:
  - Deep scan and categorization
  - File moving/renaming
  - Duplicate detection
  - Bloat identification
- Add rollback capability (snapshot filesystem state)
- Integrate with MCP tool invocation
- Create validation checkpoints

**Estimated Duration:** 2.5 days

**Success Criteria:**
- User runs `vacuum [path]`
- Vacuum Orchestrator v2 cleans and organizes autonomously
- Rollback works if validation fails
- No orphaned files

---

### 3. Cleanup Orchestrator v2 Migration

**Command:** `/CORTEX Plan Cleanup Orchestrator v2 migration`

**Scope:**
- Convert `cleanup-rules.yaml` to config-only manifest
- Implement pure Python cleanup logic:
  - Cache clearing
  - Temp file removal
  - Bloat detection
  - Log rotation
- Add database tracking for cleanup operations
- Integrate with Maintenance Pipeline (Phase 2)
- Create safety validations (prevent data loss)

**Estimated Duration:** 2 days

**Success Criteria:**
- User runs `cleanup cache` or `cleanup full`
- Cleanup Orchestrator v2 removes bloat autonomously
- Critical files never deleted
- Recovery possible via snapshots

---

### 4. Agent Layer MCP Integration

**Command:** `/CORTEX Plan Agent layer MCP integration`

**Scope:**
- Connect 2 specialist agents to MCP protocol:
  - TDD Mastery Agent
  - Debug Agent
- Create unified agent invocation interface
- Integrate with response template system
- Add agent state tracking to database
- Update CORTEX.prompt.md intent routing for agent operations

**Estimated Duration:** 4 days

**Success Criteria:**
- Agents invocable via MCP tools
- Response templates render correctly
- Agent state persists across sessions
- Error handling robust

---

### 5. GUIDED Orchestrators Assessment

**Command:** `/CORTEX Plan GUIDED orchestrators assessment`

**Scope:**
- Evaluate all GUIDED orchestrators for pure autonomous potential:
  - TDD Mastery Orchestrator
  - Debug Orchestrator
  - Refactor Orchestrator
  - Sanitization Orchestrator
  - Refinement Orchestrator
  - Onboarding Orchestrator
- Determine which benefit from config-driven approach
- Create migration plans for selected orchestrators
- Document decision rationale

**Estimated Duration:** 12.5 days (includes implementation of selected migrations)

**Decision Framework:**
```
IF orchestrator has:
  - Complex multi-phase workflow ✅ → Consider pure autonomous
  - Repetitive output generation ✅ → Consider template-driven
  - Dynamic user interaction ❌ → Keep guided
  - Simple linear steps ❌ → Keep guided
THEN migrate to pure autonomous
ELSE keep as guided (CORTEX executes)
```

**Candidate for Pure Autonomous:**
- ✅ **Refactor Orchestrator** - Complex analysis, template-driven reports
- ✅ **Sanitization Orchestrator** - Deterministic 5-phase cleanup
- ⚠️ **TDD Mastery** - May benefit from hybrid (Python test execution + CORTEX guidance)

**Keep as Guided:**
- ❌ **Onboarding** - Interactive, user-paced
- ❌ **Debug Orchestrator** - Requires human analysis of errors
- ❌ **Refinement** - Subjective improvement decisions

---

## 📐 Migration Plan Structure

Each generated plan will follow v5 structure:

```
cortex-brain/documents/planning/active/{migration-plan-name}/
├── 00-MASTER-PLAN-V5.md
│   ├── Executive Summary
│   ├── Visual Progress Tracker
│   ├── Root Cause Analysis
│   ├── Implementation Strategy
│   ├── Success Criteria
│   └── Rollback Plan
├── context/
│   ├── current-implementation-analysis.md
│   ├── manifest-comparison.md
│   └── dependencies.md
├── artifacts/
│   ├── new-manifest.yaml (config-only)
│   ├── orchestrator-v2.py (pure Python)
│   └── templates/ (Jinja2 files)
├── reports/
│   ├── progress-report-001.md
│   └── final-migration-report.md
├── tracking/
│   └── state-snapshot.json
├── phases/
│   ├── phase-1-analysis.md
│   ├── phase-2-implementation.md
│   └── phase-3-testing.md
├── architecture/
│   ├── config-structure.md
│   └── execution-flow.md
└── future-structure/
    ├── src/orchestrators/{orchestrator_name}_v2.py
    └── cortex-brain/manifests/orchestrators/{orchestrator}-2.0-manifest.yaml
```

---

## 🔄 Execution Sequence

### Week 1: ADO + Vacuum (5.5 days)
1. Generate ADO migration plan (0.1 days)
2. Execute ADO migration (3 days)
3. Generate Vacuum migration plan (0.1 days)
4. Execute Vacuum migration (2.5 days)

### Week 2: Cleanup + Agent Integration (6 days)
5. Generate Cleanup migration plan (0.1 days)
6. Execute Cleanup migration (2 days)
7. Generate Agent integration plan (0.1 days)
8. Execute Agent integration (4 days)

### Week 3-4: GUIDED Assessment (12.5 days)
9. Generate GUIDED assessment plan (0.3 days)
10. Analyze each GUIDED orchestrator (3 days)
11. Create migration plans for selected orchestrators (1 day)
12. Execute migrations (8 days)
13. Final validation (0.5 days)

**Total:** ~24 days (Phase 6)

---

## 📊 Success Metrics

### Per-Migration Success:
- ✅ Manifest is config-only (validation script passes)
- ✅ Python owns all execution logic
- ✅ Database state management implemented
- ✅ MCP tool invocation works
- ✅ Response template renders correctly
- ✅ Unit tests pass (≥90% coverage)
- ✅ Integration test passes (end-to-end)
- ✅ Documentation complete

### Overall Migration Success:
- ✅ All AUTONOMOUS orchestrators use MCP
- ✅ Zero hybrid control flow
- ✅ Single source of truth (database)
- ✅ Consistent folder structures
- ✅ No manual intervention required
- ✅ All tests passing
- ✅ User documentation updated

---

## 🚧 Migration Dependencies

```
Bootstrap (Phase 0-4)
    ↓
Planning System v5 ✅ Operational
    ↓
    ├─→ ADO v2 Migration (no dependencies)
    ├─→ Vacuum v2 Migration (no dependencies)
    ├─→ Cleanup v2 Migration (depends on Vacuum for file detection)
    └─→ Agent MCP Integration (no dependencies)
        ↓
        GUIDED Assessment (depends on Agent integration completion)
            ↓
            Selected GUIDED Migrations (depends on assessment)
```

**Critical Path:** Bootstrap → Planning v5 → Any migration can start

---

## 🔧 Risk Management

### Risk: Plan Generation Quality

**Mitigation:**
- First generated plan manually reviewed
- Template adjustments based on review
- Validation checkpoints in planning manifest
- User can refine plan before execution

### Risk: Migration Complexity Underestimated

**Mitigation:**
- TIER 4/5 migrations get extra buffer
- Each migration has rollback plan
- Database snapshots before major changes
- Can pause migration to reassess

### Risk: Breaking Existing Functionality

**Mitigation:**
- Old orchestrator stays active during migration
- New orchestrator tested in isolation
- Feature flag to enable/disable v2
- Gradual rollout (internal → beta → production)

---

## 📋 Migration Checklist Template

For each migration:

**Pre-Migration:**
- [ ] Planning System v5 generates migration plan
- [ ] Plan reviewed and approved
- [ ] Dependencies verified
- [ ] Test environment prepared
- [ ] Rollback strategy documented

**During Migration:**
- [ ] Config-only manifest created
- [ ] Python implementation complete
- [ ] Database integration added
- [ ] Templates created
- [ ] Unit tests written and passing
- [ ] Integration tests passing
- [ ] Code review completed

**Post-Migration:**
- [ ] Old orchestrator archived
- [ ] New orchestrator registered in MCP
- [ ] CORTEX.prompt.md updated
- [ ] Response templates verified
- [ ] User documentation updated
- [ ] Migration report generated
- [ ] Lessons learned documented

---

## 🎯 Final State

After all migrations complete:

**All AUTONOMOUS Orchestrators:**
```
User Intent
    ↓
CORTEX.prompt.md (route) → LLMIntentClassifier
    ↓
MCP Tool: invoke_orchestrator(name, request)
    ↓
Python Orchestrator (owns everything)
    ↓
Database State Management
    ↓
Generated Outputs (markdown, JSON, reports)
    ↓
CORTEX displays summary (thin client)
```

**All GUIDED Orchestrators:**
- Assessed for pure autonomous potential
- Migrated if beneficial
- Kept as guided if interactive/subjective
- Documented decision rationale

**System Benefits:**
- ✅ Zero execution ambiguity
- ✅ Single source of truth
- ✅ Atomic operations with rollback
- ✅ Consistent quality
- ✅ Testable and maintainable
- ✅ Scalable architecture

---

## 📚 References

- Bootstrap strategy: `phases/bootstrap-strategy.md`
- Pure autonomous principles: `architecture/pure-autonomous-principles.md`
- Database schema: `architecture/database-schema.md`
- Config specification: `architecture/config-specification.md`
- Migration checklist: (this document)
