# CORTEX Roadmap Holistic Review & Enhancement Plan

**Date:** 2026-01-20  
**Authority:** cortex-builder.prompt.md (CORTEX implementation guidelines)  
**Status:** CRITICAL ISSUES IDENTIFIED - ACTION REQUIRED

---

## Executive Summary

Comprehensive roadmap analysis reveals **6 critical brittleness issues** and **3 major hallucinations** requiring immediate remediation. Current cortex-impl-map.yaml contains **internally contradictory phase status claims** (22 phases marked "IMPLEMENTED" with full test counts, while referenced files document all tools as "STUBS returning mock data").

**Immediate Action Required:** Establish canonical cortex-master.yaml with authoritative phase_tracker before proceeding with any phase implementation.

---

## 🔴 CRITICAL ISSUES

### Issue 1: Phase Completion Hallucinations
**Severity:** 🔴 CRITICAL - Blocks all decisions

**Evidence:**
- cortex-impl-map.yaml: Lines 100-150 list 22 phases as "IMPLEMENTED" with specific test counts (arch-005 through arch-025)
- mcp-impl-status.yaml: Explicitly documents "14/14 tools STUB_IMPLEMENTATIONS" returning mock data
- impl-tdd-prod-ready-remediation.yaml: Documents "263 test collection errors" and "NOT_STARTED" status
- Contradiction: Cannot claim phase "IMPLEMENTED" if it produces 263 import errors

**Impact:** 
- Architecture decisions based on false completion status
- Risk of decisions relying on non-existent functionality
- Credibility of entire roadmap undermined

**Required Fix:**
- Audit each claimed "IMPLEMENTED" phase against actual test pass rate
- Document blocking test failures for each phase
- Convert to honest status: LOCKED (complete), PARTIAL (in progress), STUB (mock only), MISSING (not started)

### Issue 2: Authority Chain Missing
**Severity:** 🔴 CRITICAL - No single source of truth

**Evidence:**
- cortex-builder.prompt.md references `cortex-master.yaml` (v3.0 truth-based) with phase_tracker
- Actual roadmap has cortex-impl-map.yaml (version 3.0-consolidated) without phase_tracker
- Multiple status files (mcp-impl-status.yaml, module-mapping.yaml, etc.) with conflicting status claims
- No phase_tracker structure to determine locked vs. ready phases

**Impact:**
- Cannot follow cortex-builder.prompt.md's "ONE PATH FORWARD" principle
- No authoritative decision tree to determine next phase
- Risk of duplicate/conflicting implementation efforts

**Required Fix:**
```yaml
Create: cortex-master.yaml (3.1 with phase_tracker)
Section: phase_tracker
- Each phase: id, title, locked (boolean), blocked_by (array), tests_passing (count/goal)
- Single authority for all phase decisions
```

### Issue 3: TDD Blocking Issue Not Prioritized
**Severity:** 🔴 CRITICAL - Blocks all other work

**Evidence:**
- consolidation-001-src-cleanup.yaml: NOT_STARTED, blocking repository cleanliness
- 263 test collection errors (src.* → cortex.* migration incomplete)
- impl-tdd-prod-ready-remediation.yaml: "2-3 weeks effort, READY FOR IMPLEMENTATION" but NOT STARTED
- No phase can safely proceed while 263 import errors exist

**Impact:**
- Test collection fundamentally broken
- Cannot validate ANY implementation
- Entire CI/CD pipeline unreliable
- All later phases inherit corrupted foundation

**Required Fix:**
1. Elevate consolidation-001-src-cleanup to P0 IMMEDIATE (this week)
2. Execute impl-tdd-prod-ready-remediation Phase 1-2 (foundation + core)
3. Validate 0 import errors before allowing other phases

### Issue 4: Core Rules Missing (Governance Authority)
**Severity:** 🔴 CRITICAL - Blocks governance enforcement

**Evidence:**
- cortex-impl-map.yaml line 66: `core_rules_missing: true`
- cortex_brain/tier0/governance/ should contain core-rules.yaml (does not exist)
- Multiple phases claim governance implementation but governance system incomplete
- Governance CLI, validation, enforcement cannot work without rules

**Impact:**
- All governance-dependent phases have unmet dependencies
- CORE-008/011/012/013 enforcement not possible
- Risk of allowing non-compliant code

**Required Fix:**
- Create cortex_brain/tier0/governance/core-rules.yaml with all CORE-* rule definitions
- Reference: cortex/core/governance/ has enforcement logic but no rule source
- Should define 28+ governance rules (documented in architecture)

### Issue 5: Tier System Incomplete
**Severity:** 🔴 CRITICAL - Blocks tier2 implementations

**Evidence:**
- cortex-impl-map.yaml lines 61-65:
  ```
  tier0_files: 2  # prompt-versions.yaml, repo-registry.yaml
  tier1_files: 0  # Empty directory
  tier2_files: 0  # Empty directory
  ```
- Phases claim "hallucination prevention" (tier2) complete with 160 tests
- Cannot be complete if tier2 is empty

**Impact:**
- Tier2 implementations unverifiable
- Cannot enforce tier policies
- Hallucination prevention claims unsubstantiated

**Required Fix:**
- Populate tier0 with governance rules (core-rules.yaml)
- Populate tier1 with operational policies
- Populate tier2 with safety/security rules
- Verify each phase's tier dependencies are met

### Issue 6: MCP Tool Exposure False Claim
**Severity:** 🟠 HIGH - Blocks production readiness

**Evidence:**
- cortex-impl-map.yaml line 20: `mcp_tools_exposed: 14  # All stubs currently`
- mcp-impl-status.yaml: All 14 tools documented as STUB, returning mock data
- Actual callable tools: 0 (echo_tool is intentional echo, not functional integration)
- Production cannot rely on tools that return mock data

**Impact:**
- MCP protocol claims credibility undermined
- Production deployment impossible until tools implemented
- Claude/IDE integration non-functional

**Required Fix:**
- Clear phase: MCP tool implementation phases (Phases 26+)
- Each tool requires impl-mcp-tool-{name}.yaml phase file
- Implement sequentially: status_tool, query_tool, validate_tool, etc.

---

## 📊 ROOT CAUSE ANALYSIS

### Why Brittleness Occurred

1. **Conflicting Status Documents**
   - Multiple YAML files with contradictory claims
   - No enforcement mechanism to keep them synchronized
   - Manual status updates prone to inconsistency

2. **Lack of Authority Chain**
   - No single cortex-master.yaml phase_tracker
   - Each phase tracked independently (or not tracked)
   - Cannot trace dependencies or blocking issues

3. **Incomplete Governance Infrastructure**
   - core-rules.yaml missing
   - Cannot enforce CORE-008/011/012/013
   - Phases claim compliance without enforcement

4. **Test Collection Broken**
   - 263 import errors unresolved
   - Phase completion claims not validated against actual test pass rate
   - No gating mechanism to prevent false completion claims

---

## ✅ ENHANCEMENT PLAN

### Phase 0: Roadmap Healing (P0 - THIS WEEK - 8 hours)

**Objective:** Establish authoritative roadmap structure enabling all downstream decisions

**Tasks:**

1. **Create cortex-master.yaml (3.1) - Authority Structure** (2 hours)
   ```yaml
   File: _workspaces/roadmap/cortex-master.yaml (NEW)
   Sections:
     - metadata: Version 3.1, date, authority
     - phase_tracker: All phases with locked/blocked status
     - blocked_phases: Phases that cannot proceed
     - critical_path: P0 immediate phases in order
     - blocked_reasons: Why each phase is locked/unblocked
   ```

2. **Create core-rules.yaml - Governance Authority** (1 hour)
   ```yaml
   File: cortex_brain/tier0/governance/core-rules.yaml (NEW)
   Content: All 28+ CORE-* rules from cortex/core/governance/
   Defines: CORE-008 (TDD), CORE-011 (types), CORE-012 (docstrings), CORE-013 (errors), etc.
   ```

3. **Update cortex-impl-map.yaml - Align with Reality** (2 hours)
   - Add phase_tracker section
   - Change "IMPLEMENTED" claims to accurate status (LOCKED/PARTIAL/STUB/MISSING)
   - Remove contradictions with mcp-impl-status.yaml
   - Document blocking issues explicitly

4. **Audit Test Collection Status** (2 hours)
   - Run pytest --collect-only 2>&1 | grep -E "(error|ERROR|failed|FAILED)" > test-errors.log
   - Count remaining import errors (target: 0, current: 263)
   - Document blocking modules explicitly

5. **Create Phase Dependency Map** (1 hour)
   ```yaml
   File: _workspaces/roadmap/reports/PHASE-DEPENDENCY-MAP.yaml (NEW)
   - Which phases block which
   - Clear order for implementation
   - No circular dependencies
   ```

**Success Criteria:**
- ✅ cortex-master.yaml exists with authoritative phase_tracker
- ✅ core-rules.yaml exists with 28+ CORE-* rules
- ✅ cortex-impl-map.yaml updated to remove contradictions
- ✅ All team members can answer: "Can we proceed with PHASE-X?" by consulting cortex-master.yaml

### Phase 1: TDD Blocking Issue Resolution (P0 - NEXT WEEK - 32 hours)

**Objective:** Reduce 263 import errors to 0, enabling all other phases

**Tasks:**

1. **Consolidation Phase (12 hours)**
   - Execute consolidation-001-src-cleanup.yaml
   - Migrate all src.* imports to cortex.*
   - Verify 0 import errors

2. **TDD Remediation Phase 1-2 (20 hours)**
   - Implement foundation (5 core modules)
   - Implement core infrastructure (5 modules)
   - Full type hints + docstrings + tests
   - Target: 90% test collection success

**Success Criteria:**
- ✅ pytest --collect-only returns 6599 tests, 0 errors
- ✅ Phase 1-2 all ACs complete
- ✅ All phases can proceed

### Phase 2: Tier System Population (P1 - WEEK 2 - 12 hours)

**Objective:** Complete governance infrastructure

**Tasks:**

1. **Populate tier0 (2 hours)**
   - Verify core-rules.yaml loaded
   - Verify 28+ rules accessible

2. **Populate tier1 (5 hours)**
   - Define operational policies
   - Add to cortex_brain/tier1/

3. **Populate tier2 (5 hours)**
   - Define safety/security rules
   - Add to cortex_brain/tier2/
   - Verify hallucination prevention prerequisites

**Success Criteria:**
- ✅ All 3 tier levels populated
- ✅ Governance enforcement operational
- ✅ Tier2 phases can proceed

### Phase 3: Toolkit & MCP Preparation (P1 - WEEK 2 - 16 hours)

**Objective:** Prepare MCP infrastructure for real tool implementation

**Tasks:**

1. **Fix MCP Configs (1 hour)**
   - Update src.mcp → cortex.mcp in vscode-mcp.json
   - Update src.mcp → cortex.mcp in claude-desktop.json
   - Verify MCP connectivity

2. **Design MCP Tool Registry (3 hours)**
   - Create cortex/mcp/tool_registry.yaml
   - Define tool schema
   - Plan implementation phases per tool

3. **Toolkit Entry Point (4 hours)**
   - Complete cortex/tools/toolkit/__init__.py
   - Implement command dispatcher
   - Wire to tool registry

4. **Create Tool Implementation Phases (8 hours)**
   - impl-mcp-status-tool.yaml
   - impl-mcp-query-tool.yaml
   - impl-mcp-validate-tool.yaml
   - etc. (14 total phases)

**Success Criteria:**
- ✅ `cortex help` lists all 15 CLI tools
- ✅ MCP configs point to cortex.mcp
- ✅ 14 tool implementation phases documented

---

## 🎯 PRIORITIZED NEXT STEPS

### THIS WEEK (P0 IMMEDIATE)

```
1. Create cortex-master.yaml with phase_tracker (2 hours)
2. Create core-rules.yaml in cortex_brain/tier0/governance/ (1 hour)
3. Update cortex-impl-map.yaml to align with reality (2 hours)
4. Execute consolidation-001-src-cleanup.yaml (4 hours)
5. Validate 0 import errors (1 hour)

Total: 10 hours
Goal: Establish clean roadmap authority + unblock test collection
```

### NEXT WEEK (P0 CONTINUATION)

```
1. Implement TDD Phase 1-2 (32 hours = full week)
2. Achieve 90% test collection success
3. Lock foundational phases
```

### FOLLOWING WEEK (P1)

```
1. Populate tier system (12 hours)
2. Prepare MCP infrastructure (16 hours)
3. Begin TDD Phase 3
```

---

## 📝 Recommended Action

Per cortex-builder.prompt.md guidelines:

> **"Before implementing any phase: Check cortex-master.yaml → verify implementation status"**

**Current Status:** cortex-master.yaml does not exist. cortex-impl-map.yaml contains unverified claims.

**Required:** Proceed with Phase 0 (Roadmap Healing) THIS WEEK before any other phase implementation.

**Decision:** 
- ✅ Proceed with Phase 0 creation? (yes/no)
- 🚫 DO NOT proceed with TDD/toolkit/MCP phases until Phase 0 complete

---

## Files to Create/Update

| File | Action | Priority | Time |
|------|--------|----------|------|
| cortex-master.yaml | CREATE (new) | P0 | 2 hrs |
| cortex_brain/tier0/governance/core-rules.yaml | CREATE (new) | P0 | 1 hr |
| cortex-impl-map.yaml | UPDATE (fixes) | P0 | 2 hrs |
| _workspaces/roadmap/reports/PHASE-DEPENDENCY-MAP.yaml | CREATE (new) | P0 | 1 hr |
| _workspaces/roadmap/phases/consolidation-001-src-cleanup.yaml | EXECUTE | P0 | 4 hrs |
| _workspaces/roadmap/phases/phase-0-roadmap-healing.yaml | CREATE (spec) | P0 | 1 hr |

**Total Phase 0 Effort:** ~10 hours (1 day concentrated work)

**Blocker Removal:** Enables all downstream phases

---

## Governance Compliance

**This plan enforces:**
- ✅ CORE-026: Git checkpoints (before major action)
- ✅ CORE-008: Tests before code (roadmap tests authority claims)
- ✅ CORE-027: AC_START → AC_EXECUTE → AC_COMPLETE audit trail
- ✅ CORE-017: Strict enforcement (no hallucinations in roadmap)

**Decision Gate:** Do not proceed with any phase until cortex-master.yaml authority established.
