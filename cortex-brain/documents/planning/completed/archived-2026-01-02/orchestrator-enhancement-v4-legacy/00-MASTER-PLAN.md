# 🛡️ Planning System v5.0 Implementation - Master Plan

**Feature:** Robust Planning System with Autonomous Execution  
**Created:** January 2, 2026  
**Status:** 🔄 ACTIVE  
**Complexity:** TIER 4 (CRITICAL)  
**Compliance Score:** 10.0/10.0 ✅

---

## 📊 Visual Progress Tracker

**Overall Progress:** `████░░░░░░░░░░░░░░░░` **20%** 🔄 IN PROGRESS

| Phase | Name | Progress | Tasks | Duration | Status |
|-------|------|----------|-------|----------|--------|
| -1 | [Knowledge Library Consultation](phases/phase-minus-1-knowledge-library.md) | `██████████` | 5/5 | 15m | ✅ Complete |
| 0 | [Discovery & Requirements](phases/phase-00-discovery.md) | `████████░░` | 8/10 | 2h 15m | 🔄 In Progress |
| 1 | [Invocation Bridge (MCP Tool)](phases/phase-01-invocation-bridge.md) | `░░░░░░░░░░` | 0/12 | - | ⏸️ Not Started |
| 2 | [Orchestrator Self-Validation](phases/phase-02-orchestrator-validation.md) | `░░░░░░░░░░` | 0/15 | - | ⏸️ Not Started |
| 3 | [Continuous Knowledge Library Integration](phases/phase-03-continuous-knowledge-library.md) | `░░░░░░░░░░` | 0/10 | - | ⏸️ Not Started |
| 4 | [Maintenance-Style Progress Rendering](phases/phase-04-progress-rendering.md) | `░░░░░░░░░░` | 0/8 | - | ⏸️ Not Started |
| 5 | [Template Integration](phases/phase-05-template-integration.md) | `░░░░░░░░░░` | 0/10 | - | ⏸️ Not Started |
| 6 | [Hierarchical Plan Structure](phases/phase-06-hierarchical-structure.md) | `░░░░░░░░░░` | 0/12 | - | ⏸️ Not Started |
| 7 | [Brain Tier Update Pipeline](phases/phase-07-brain-tier-updates.md) | `░░░░░░░░░░` | 0/14 | - | ⏸️ Not Started |
| 8 | [Testing & Validation](phases/phase-08-testing.md) | `░░░░░░░░░░` | 0/18 | - | ⏸️ Not Started |
| 9 | [Migration & Documentation](phases/phase-09-migration.md) | `░░░░░░░░░░` | 0/10 | - | ⏸️ Not Started |
| 10 | [REFACTOR & Cleanup](phases/phase-10-refactor.md) | `░░░░░░░░░░` | 0/18 | - | ⏸️ Not Started |
| 11 | [Knowledge Extraction](phases/phase-11-knowledge-extraction.md) | `░░░░░░░░░░` | 0/12 | - | ⏸️ Not Started |
| 12 | [Documentation Library Update](phases/phase-12-documentation-update.md) | `░░░░░░░░░░` | 0/8 | - | ⏸️ Not Started |

**Total Tasks:** 13/152 (9%)  
**Estimated Completion:** ~7 weeks

---

## 🎯 Executive Summary

This plan implements Planning System v5.0 - a **robust, autonomous planning system** that addresses all fragility issues identified in the gap analysis. Key innovations:

1. **🛡️ Fail-Safe Hand-Off** - MCP tool guarantees orchestrator execution
2. **🔄 Continuous Knowledge Library** - Query on every turn, not just Phase -1
3. **📊 Maintenance-Style Progress** - Real-time visual progress during execution
4. **🧠 Brain Tier Integration** - Automatic knowledge extraction and updates
5. **📁 Hierarchical Plans** - Master + phase sub-files with 2-way linking
6. **🔍 Auto-Healing** - Automatically fix governance violations

**Current System Problems:**
- ❌ CORTEX interprets plans manually (orchestrator bypassed)
- ❌ No real invocation mechanism
- ❌ Knowledge library checked once (Phase -1 only)
- ❌ No brain tier updates after plan completion
- ❌ Monolithic plan structure (all phases in one file)

**v5.0 Solutions:**
- ✅ MCP tool `invoke_orchestrator()` guarantees execution
- ✅ Continuous knowledge library queries at each phase
- ✅ Brain Tier 2/3 updates after plan completion
- ✅ Hierarchical structure: master + 13 phase files + 2-way links

---

## 📋 Phase Navigation

### Discovery & Analysis
- **[Phase -1: Knowledge Library Consultation](phases/phase-minus-1-knowledge-library.md)** ✅
  - Query existing patterns, templates, best practices
  - Load applicable knowledge library files
  - Duration: 15 minutes
  
- **[Phase 0: Discovery & Requirements](phases/phase-00-discovery.md)** 🔄
  - Root cause analysis review
  - Gap analysis validation
  - Requirements prioritization
  - Duration: ~3 hours

### Core Implementation (Weeks 1-3)
- **[Phase 1: Invocation Bridge (MCP Tool)](phases/phase-01-invocation-bridge.md)** ⏸️
  - Implement `invoke_orchestrator()` MCP tool
  - Add orchestrator registry
  - Test hand-off protocol
  - Duration: ~1 week

- **[Phase 2: Orchestrator Self-Validation](phases/phase-02-orchestrator-validation.md)** ⏸️
  - Implement Phase -1 consultation logic
  - Add REFACTOR validation
  - Implement auto-healing
  - Duration: ~1 week

- **[Phase 3: Continuous Knowledge Library Integration](phases/phase-03-continuous-knowledge-library.md)** ⏸️
  - Query knowledge library at each phase
  - Extract patterns after phase completion
  - Feed back to Tier 2/3
  - Duration: ~1 week

### Progress & Structure (Weeks 4-5)
- **[Phase 4: Maintenance-Style Progress Rendering](phases/phase-04-progress-rendering.md)** ⏸️
  - Implement real-time progress updates
  - Render progress bar after each task
  - Match maintenance execution pattern
  - Duration: ~3-4 days

- **[Phase 5: Template Integration](phases/phase-05-template-integration.md)** ⏸️
  - Fix `autonomous_execution_progress` template variables
  - Wire orchestrator execution context
  - Test template rendering
  - Duration: ~3 days

- **[Phase 6: Hierarchical Plan Structure](phases/phase-06-hierarchical-structure.md)** ⏸️
  - Generate master + phase sub-files
  - Implement 2-way linking
  - Add navigation breadcrumbs
  - Duration: ~1 week

### Integration & Brain Updates (Week 6)
- **[Phase 7: Brain Tier Update Pipeline](phases/phase-07-brain-tier-updates.md)** ⏸️
  - Implement Tier 1 updates (conversation context)
  - Implement Tier 2 updates (knowledge graph)
  - Implement Tier 3 updates (dev context)
  - Detect and replace obsolete data
  - Duration: ~1 week

### Quality Assurance (Week 7)
- **[Phase 8: Testing & Validation](phases/phase-08-testing.md)** ⏸️
  - Unit tests for all components
  - Integration tests (end-to-end)
  - Performance testing
  - User acceptance testing
  - Duration: ~1 week

- **[Phase 9: Migration & Documentation](phases/phase-09-migration.md)** ⏸️
  - Update CORTEX.prompt.md
  - Update copilot-instructions.md
  - Create migration guide
  - Archive v4.0 implementation
  - Duration: ~3 days

### Cleanup & Knowledge Extraction (Final)
- **[Phase 10: REFACTOR & Cleanup](phases/phase-10-refactor.md)** ⏸️
  - Remove orphaned code
  - Eliminate duplicate implementations
  - Clean unused imports
  - Fix code smells
  - Standardize formatting
  - Duration: ~2 days

- **[Phase 11: Knowledge Extraction](phases/phase-11-knowledge-extraction.md)** ⏸️
  - Extract patterns from implementation
  - Update knowledge graph
  - Update module definitions
  - Update lessons learned
  - Duration: ~1 day

- **[Phase 12: Documentation Library Update](phases/phase-12-documentation-update.md)** ⏸️
  - Generate knowledge library entries
  - Update best practices docs
  - Create cross-references
  - Archive obsolete patterns
  - Duration: ~1 day

---

## 🔗 Related Resources

### 🛡️ Orchestrator Enhancement Plans (NEW)
> **Cross-cutting fix:** All AUTONOMOUS orchestrators share the same broken protocol.  
> See [Orchestrator Enhancement Master](../orchestrator-enhancements/00-ORCHESTRATOR-MASTER.md) for details.

| Plan | Priority | Status | Link |
|------|----------|--------|------|
| MCP Tool Infrastructure | 🔴 P0 | ⏸️ | [Plan](../orchestrator-enhancements/mcp-tool-infrastructure/00-master-plan.md) |
| Planning System v5 | 🔴 P1 | ⏸️ | [Plan](../orchestrator-enhancements/planning-system-v5/00-master-plan.md) |
| ADO Operations v2 | 🟡 P2 | ⏸️ | [Plan](../orchestrator-enhancements/ado-operations-v2/00-master-plan.md) |
| Vacuum v2 | 🟡 P2 | ⏸️ | [Plan](../orchestrator-enhancements/vacuum-v2/00-master-plan.md) |
| Cleanup v2 | 🟢 P3 | ⏸️ | [Plan](../orchestrator-enhancements/cleanup-v2/00-master-plan.md) |

### Context Documents
- [Root Cause Analysis](context/root-cause-analysis.md)
- [Gap Analysis](context/gap-analysis.md)
- [Knowledge Library Context](context/knowledge-library-context.md)
- [Current System Architecture](context/current-system-architecture.md)

### Artifacts
- [MCP Tool Specification](artifacts/mcp-tool-spec.md)
- [Orchestrator API Contract](artifacts/orchestrator-api-contract.md)
- [Progress Rendering Specification](artifacts/progress-rendering-spec.md)
- [Brain Tier Update Schema](artifacts/brain-tier-update-schema.md)

### Tracking
- [Progress Tracker (JSON)](tracking/progress-tracker.json)
- [Progress Tracker (Visual)](tracking/PROGRESS.md) ← Human-readable, synced with JSON
- [Compliance Report](tracking/compliance-report.json)
- [Validation Results](tracking/validation-results.json)

---

## 🔴 CRITICAL: Architecture Integration Analysis

**Date:** January 2, 2026  
**Finding:** All 4 🛡️ AUTONOMOUS orchestrators share the **same broken hand-off protocol**

### Affected Orchestrators

| Orchestrator | Implementation | Status |
|--------------|----------------|--------|
| Planning System | `planning_orchestrator.py` | 🛡️ BROKEN |
| ADO Operations | `ado_orchestrator.py` | 🛡️ BROKEN |
| Vacuum | System orchestrator | 🛡️ BROKEN |
| Cleanup | System orchestrator | 🛡️ BROKEN |

### Root Cause

`CORTEX.prompt.md` says "STOP and hand-off" but **there's no mechanism to actually invoke the Python orchestrator code**.

```
Current (BROKEN):
User Intent → CORTEX.prompt.md → "STOP" → ??? (nothing happens)
                                         ↑
                                   NO INVOCATION MECHANISM
```

### Proposed Fix: MCP Tool `invoke_orchestrator()`

```
Fixed Flow:
User Intent → CORTEX.prompt.md → MCP Tool invoke_orchestrator()
                                          ↓
                                   planning_orchestrator.py (EXECUTES)
```

**Why MCP Tool:**
- ✅ **Fixes ALL 4 orchestrators** with one implementation
- ✅ **Guaranteed execution** (LLM tool call → Python code runs)
- ✅ **Observability** (tool call logged, result returned)
- ✅ **Testable** (tool can be unit tested)
- ✅ **No manual bypass possible**

### Updated Component Tiers

| Tier | Components | Impact |
|------|------------|--------|
| **Tier 1: Core Infrastructure** | MCP tool server, invoke_orchestrator() | Fixes ALL orchestrators |
| **Tier 2: Base Classes** | BaseOrchestrator v4.1 | All orchestrators inherit |
| **Tier 3: Individual Orchestrators** | Planning, ADO, Vacuum, Cleanup | Use new infrastructure |
| **Tier 4: Manifests & Config** | CORTEX.prompt.md, manifests | Route to MCP tool |

### Updated LOE Estimate

| Phase | Duration | Description |
|-------|----------|-------------|
| Phase 1 | 3 days | MCP tool infrastructure |
| Phase 2 | 2 days | BaseOrchestrator v4.1 |
| Phase 3 | 4 days | Planning v5.0 |
| Phase 4 | 2 days | Other orchestrators (ADO, Vacuum, Cleanup) |
| Phase 5 | 1 day | Manifests |
| Phase 6 | 1 day | Documentation |
| **Total** | **~13 days** | — |

### Recommendation

**✅ APPROVED:** Implement Phase 1 (MCP tool) FIRST as it provides a cross-cutting fix for all AUTONOMOUS orchestrators.

---

## 📐 Architecture Diagrams

### Current (v4.0) - BROKEN
```
User Intent → CORTEX.prompt.md → ??? → planning_orchestrator.py
                                  ↑
                            MISSING LINK
```

### Future (v5.0) - ROBUST
```
User Intent → CORTEX.prompt.md → MCP Tool invoke_orchestrator() → planning_orchestrator.py
                                        ↓
                                  GUARANTEED EXECUTION
```

---

## ✅ Definition of Ready (DoR)

- [x] Gap analysis complete (67% requirements missing identified)
- [x] Root cause analysis validated
- [x] Redesign proposal reviewed
- [x] Stakeholder approval obtained
- [x] Development environment ready
- [x] Maintenance execution pattern studied
- [x] Knowledge library structure documented

---

## ✅ Definition of Done (DoD)

- [ ] All 13 phases complete (152 tasks)
- [ ] MCP tool `invoke_orchestrator()` implemented and tested
- [ ] Continuous knowledge library integration working
- [ ] Brain Tier 2/3 updates automated
- [ ] Hierarchical plan structure generated correctly
- [ ] 2-way linking functional
- [ ] Compliance score ≥8.0/10 for all generated plans
- [ ] Auto-healing successful for 90% of violations
- [ ] Performance <5s plan generation (90th percentile)
- [ ] Zero manual plan bypasses
- [ ] Migration guide complete
- [ ] All tests passing (unit, integration, performance)
- [ ] Documentation updated (CORTEX.prompt.md, copilot-instructions.md)
- [ ] Knowledge library updated with new patterns
- [ ] v4.0 archived

---

## 🎯 Success Metrics

| Metric | Current (v4.0) | Target (v5.0) |
|--------|----------------|---------------|
| Orchestrator Engagement | 0% (bypassed) | 100% |
| Phase -1 Inclusion | 0% | 100% |
| Knowledge Library Checks | 1 (Phase -1 only) | 13 (every phase) |
| REFACTOR Comprehensiveness | 6 tasks avg | 18 tasks enforced |
| Compliance Score | 6.8/10 (FAIL) | 10.0/10 (TARGET) |
| Manual Bypasses | Common | 0 (impossible) |
| Brain Tier Updates | Manual | Automatic |
| Plan Structure | Monolithic | Hierarchical |
| Progress Visibility | Template only | Real-time |

---

## 🛡️ SKULL Rules Enforced

This plan enforces ALL CORTEX governance rules:

1. **TDD_ENFORCEMENT** - Tests written before implementation
2. **HOLISTIC_DISCOVERY** - Search before create
3. **REFACTOR_CODE_CLEANUP_ENFORCEMENT** - Comprehensive Phase 10
4. **GIT_ISOLATION** - CORTEX code never in user repos
5. **PLANNING_ISOLATION** - Plans create structure, never implement
6. **HAND_OFF_PROTOCOL** - 🛡️ AUTONOMOUS orchestrators execute independently
7. **KNOWLEDGE_LIBRARY_INTEGRATION_ENFORCEMENT** - Continuous queries
8. **BRAIN_TIER_INTEGRITY** - Automatic updates, obsolete data replacement

---

## 📞 Copilot Instructions

```yaml
# This block is read by GitHub Copilot for context during implementation

response_template: autonomous_execution_progress
orchestrator_engaged: true
progress_rendering: maintenance_style  # Real-time, after each task
tdd_enforcement: mandatory
final_refactor_required: true
refactor_minimum_tasks: 18
refactor_categories: [orphaned_code, duplication, dead_code, formatting, documentation]
knowledge_library_integration: continuous  # Every phase, not just Phase -1
brain_tier_updates: automatic  # After plan completion
plan_structure: hierarchical  # Master + phase sub-files
two_way_linking: enabled
compliance_threshold: 8.0
auto_healing: enabled
invocation_mechanism: mcp_tool  # invoke_orchestrator()
```

---

## 🚀 Quick Links

- [Root Cause Analysis](../../../analysis/planning-system-redesign-proposal-2026-01-02.md#root-cause-analysis)
- [Gap Analysis](../../../analysis/planning-redesign-gap-analysis-2026-01-02.md)
- [Phase -1: Knowledge Library](phases/phase-minus-1-knowledge-library.md)
- [Phase 1: Invocation Bridge](phases/phase-01-invocation-bridge.md)
- [Progress Tracker](tracking/progress-tracker.json)

---

**Last Updated:** January 2, 2026  
**Maintained By:** CORTEX Development Team  
**License:** Proprietary - Asif Hussain
