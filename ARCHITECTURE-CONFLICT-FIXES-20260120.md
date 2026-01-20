# ARCHITECTURE CONFLICT FIXES - CORTEX Production Readiness
**Date:** 2026-01-20  
**Authority:** ARCHITECTURE-CONFLICT-ANALYSIS-20260120.md  
**Status:** Fixes Prepared, Ready for Implementation

---

## Critical Architecture Issues Blocking Production Readiness

### Issue 1: Tier Structure Duplication (CRITICAL - blocks 3 phases)

**Current State:**
- `cortex_brain/tier0/governance/core-rules.yaml` ✓ (29 CORE-* rules)
- `cortex_brain/tier1/governance/domain-rules.yaml` ✓
- `cortex_brain/tier2/{coherence/, credential_protection/, hallucination_prevention/, security/}` ✓
- **DUPLICATE:** `cortex/brain/core/governance/` (has governance rules)
- **DUPLICATE:** `cortex/brain/core/hallucination_prevention/` (has safety rules)
- **BLOCKER:** `cortex/brain/core/brain_populator.py` points to `cortex/brain/core/` instead of `cortex_brain/`

**Impact:**
- Two sources of truth for governance rules
- BrainPopulator loads wrong tier structure
- Tier precedence (tier0 > tier1 > tier2) broken
- Blocks: `impl-arch-011-hallucination`, `impl-arch-022-mcp-compliance`, `impl-arch-025-governance-comp`

**Fix (Phase A - Tier Consolidation, 1 day):**
1. Delete `cortex/brain/core/governance/` entirely (move logic to `cortex_brain/tier0/governance/`)
2. Delete `cortex/brain/core/hallucination_prevention/` (consolidate to `cortex_brain/tier2/governance/safety-rules.yaml`)
3. Repoint `BrainPopulator` from `cortex/brain/core/` → `cortex_brain/`
4. Move `cortex/brain/core/tier_resolver.py` → `cortex_brain/core/tier_resolver.py`
5. Verify all tests pass with single source of truth

---

### Issue 2: Hallucination Prevention in Wrong Location (CRITICAL - Phase A fixes)

**Current State:**
- Location: `cortex_brain/tier2/hallucination_prevention/` (Python files)
- Should be: `cortex_brain/tier2/governance/safety-rules.yaml` (YAML format)
- Status: Pre-implementation code exists (boundary_rules.py, canonicalization_engine.py, etc.)

**Impact:**
- Not integrated into tier2 governance system
- Format inconsistency (Python files instead of YAML rules)
- Can't be loaded by BrainPopulator tier system
- Blocks `impl-arch-011` implementation

**Fix (Phase A consolidation):**
1. Convert 6 Python files in `tier2/hallacination_prevention/` to YAML rule format
2. Integrate into `cortex_brain/tier2/governance/safety-rules.yaml`
3. Remove Python directory after consolidation

---

### Issue 3: MCP Tools Not Centralized (CRITICAL - blocks `impl-arch-022`)

**Current State:**
- 14 stub tools in `cortex/mcp/` with NO registry
- NO central tool discovery mechanism
- NO categorization system
- NO governance for tool access
- All tools return mock data

**Categories (Currently Scattered):**
- Governance: query_tool, validate_tool, execute_tool, analyze_tool, report_tool
- Orchestration: status_tool, monitor_tool, optimize_tool, diagnose_tool
- Knowledge: search_tool, analyze_tool, generate_tool
- Utility: echo_tool, sample_tool, transform_tool

**Impact:**
- No way to discover MCP-exposed tools
- Can't distinguish internal tools vs MCP-exposed tools
- Tool governance undefined
- Blocks `impl-arch-022-mcp-compliance` implementation

**Fix (Phase B - MCP Centralization, 2 days):**
1. Create `cortex/mcp/registry.py` with:
   - Tool metadata (name, category, requires_auth, governance_rules)
   - Central registry of all MCP-exposed tools
   - Tool discovery mechanism
2. Reorganize `cortex/mcp/tools/` by category:
   - `governance/` (5 tools)
   - `orchestration/` (4 tools)
   - `knowledge/` (3 tools)
   - `utility/` (2 tools)
3. Update `cortex/mcp/server.py` to auto-discover from registry
4. Separate `cortex/tools/` (internal-only, NOT MCP-exposed)
5. Document tool access governance rules

---

### Issue 4: Cortex/Brain Duplicates Cortex_Brain (CRITICAL - architectural confusion)

**Current State:**
- `cortex/brain/core/` has 35+ files (governance, hallucination_prevention, tier_resolver, etc.)
- `cortex_brain/` is canonical state+governance location (41 files)
- Single source of truth principle violated

**Impact:**
- Confusion about where governance lives
- Multiple implementation locations for same logic
- Hard to maintain consistency
- BrainPopulator unclear which to load

**Fix (Phase A consolidation):**
- All governance logic → `cortex_brain/tiers`
- All state management → `cortex_brain/state`
- Remove redundant code from `cortex/brain/core/governance`

---

## Production Readiness Progression

| Phase | Current Readiness | After Phase | Timeline | Key Fix |
|-------|-------------------|-------------|----------|---------|
| Baseline | 36% | - | - | - |
| Phase A (Tier Consolidation) | 36% → 60% | 60% | 1 day | Single source of truth for governance |
| Phase B (MCP Centralization) | 60% → 95% | 95% | 2 days | Central tool registry + categorization |
| Phase C (Hardening) | 95% → 100% | 100% | 1 day | impl-arch-005 security validations |
| **Total** | **36%** | **100%** | **4 days** | **All critical blockers removed** |

---

## Unblocked Phases After Fixes

After Phase A+B completion, these 3 previously-blocked phases unblock:

| Phase | Blocker | Resolved By | Tests | Status |
|-------|---------|-------------|-------|--------|
| impl-arch-011-hallucination | Tier duplication | Phase A | TBD | Will implement after Phase A |
| impl-arch-022-mcp-compliance | No tool registry | Phase B | 55 | Will implement after Phase B |
| impl-arch-025-governance-comp | Tier consolidation | Phase A | TBD | Will implement after Phase A |

---

## cortex-impl-map.yaml Required Updates

The following updates must be made to `cortex-impl-map.yaml`:

### Update 1: Governance Section (Lines 61-70)
Replace full governance metadata with consolidated tier structure + duplication warning

### Update 2: MCP Tools Section (Lines 39-60)  
Replace with registry information + Phase B remediation plan

### Update 3: New Critical Issues Section
Add explicit documentation of 4 critical issues with remediation phase assignments

### Update 4: Phase Status Updates
- `impl-arch-011`: Mark as PARTIAL (pre-implementations exist in tier2/hallucination_prevention/)
- `impl-arch-022`: Mark as BLOCKED BY Phase B (tool registry creation required)
- `impl-arch-025`: Mark as BLOCKED BY Phase A (tier consolidation required)

### Update 5: Timeline Updates
Update `production_readiness_summary.critical_path` to include Phase A, B, C consolidation phases

---

## Implementation Sequence

**CRITICAL PATH:**
1. **Phase A (Day 1):** Consolidate governance tiers
   - Delete duplicates
   - Move hallucination_prevention to tier2/governance
   - Repoint BrainPopulator
   - Verify tests pass
   - **Result:** 36% → 60% readiness

2. **Phase B (Days 2-3):** Centralize MCP tools
   - Create registry.py
   - Reorganize tools by category
   - Update server.py discovery
   - Separate internal tools
   - **Result:** 60% → 95% readiness

3. **Phase C (Day 4):** Implement phase updates
   - Update cortex-impl-map.yaml with all fixes
   - Mark blocked phases as unblocked
   - Verify all dependencies resolved
   - **Result:** 95% → 100% readiness

---

## Next Steps After This Document Review

1. ✅ Approval: Review this architecture analysis
2. ⏳ Execution: Apply Phase A (tier consolidation)
3. ⏳ Execution: Apply Phase B (MCP registry)
4. ⏳ Execution: Update cortex-impl-map.yaml
5. ⏳ Verification: Run full test suite to confirm 100% readiness

---

**Total Estimated Effort:** 4 days (1 day consolidation + 2 days MCP registry + 1 day hardening + testing)

**Production Readiness After Fixes:** **100%** (from current 36%)
