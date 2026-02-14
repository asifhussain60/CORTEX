# 🌊 MASTER 5-WAVE PLAN — Quick Reference

**Authority:** MASTER-5-WAVE-PLAN-2026-02-13.yaml  
**Created:** 2026-02-13 | **Status:** APPROVED ✅  
**Total Duration:** 39-48 hours (5-6 days) | **Weighted ROI:** 9.2

---

## 📊 Wave Summary

| Wave | Name | Duration | ROI | Tests | Status | Command |
|------|------|----------|-----|-------|--------|---------|
| **1** | **Foundation Repair** | 3-4h | 9.8 | 6 | ✅ READY | `/implement WAVE-1-FOUNDATION` |
| **2** | **Intelligent Test Generation** | 8-10h | 9.5 | 77 | 🔒 After Wave 1 | `/implement WAVE-2-TEST-GEN` |
| **3** | **Document Coherence** | 10-12h | 9.2 | 196 | 🔒 After Wave 1 | `/implement WAVE-3-DOC-COHERENCE` |
| **4** | **Intelligence Loop** | 12-14h | 9.0 | 159 | 🔒 After Wave 2+3 | `/implement WAVE-4-INTELLIGENCE` |
| **5** | **Consolidation** | 6-8h | 8.5 | 80 | 🔒 After Wave 4 | `/implement WAVE-5-CONSOLIDATION` |

**Total:** 518 tests | 25 commits | 6 new MCP tools

---

## 🎯 What Each Wave Delivers

### WAVE 1: Foundation Repair (P0) — 3-4 hours
**Value:** Unblock test suite, establish baseline
- ✅ Fix 5 test collection errors (no pytest failures)
- ✅ Move ENH-101 to completed/ (registry cleanup)
- ✅ Validate 10,296 tests run clean (baseline)

**User Benefit:** Reliable test suite for all subsequent waves

---

### WAVE 2: Intelligent Test Generation (P0) — 8-10 hours
**Value:** Ship STANDALONE test generation (no Wave 4 dependency)
- ✅ Test Value Scorer (prioritize high-value tests)
- ✅ Blind Spot Detector (find untested code paths)
- ✅ Edge Case Generator (boundary/null/overflow tests)
- ✅ Security Test Generator (OWASP patterns)
- ✅ **MCP Tool:** `/generate-tests path/to/file.py`

**User Benefit:** Instant access to intelligent test generation

---

### WAVE 3: Document Coherence (P1) — 10-12 hours
**Value:** Prevent "chat01.md 52% bloat" forever
- ✅ Auto-sync version headers/footers
- ✅ Post-refactor test verification (safety net)
- ✅ Accumulation pattern detection
- ✅ Auto-consolidation engine (detect → action)
- ✅ Semantic validation per file type

**User Benefit:** Zero manual cleanup after edits

---

### WAVE 4: Intelligence Loop (P1) — 12-14 hours
**Value:** Autonomous "run until production ready"
- ✅ IntelligenceLoopOrchestrator (multi-cycle TDD)
- ✅ DoD Gate (85% production ready threshold)
- ✅ Layer Analyzer (security/architecture/quality)
- ✅ Structured Work Journal (living documentation)
- ✅ Test Harness Integration (consumes Wave 2 tests)
- ✅ **Demo:** Refactor BadMonolith to ≥85% DoD

**User Benefit:** Request feature → CORTEX iterates until production ready

---

### WAVE 5: Consolidation (P2) — 6-8 hours
**Value:** Technical debt paydown + UX polish
- ✅ Orchestrator consolidation (114 → 40 files, 65% reduction)
- ✅ Prompt unbloating (30k → 8k tokens, 73% reduction)
- ✅ Capability feasibility gate (pre-execution validation)
- ✅ Remove 88 orphaned orchestrators
- ✅ Wiring validation (all 15 core orchestrators)

**User Benefit:** Faster responses, cleaner codebase, fewer errors

---

## 🔗 Wave Dependencies

```
WAVE-1 (Foundation)
    ├── WAVE-2 (Test Generation) ───┐
    └── WAVE-3 (Doc Coherence) ──────┼─→ WAVE-4 (Intelligence Loop)
                                     │           ↓
                                     └─────→ WAVE-5 (Consolidation)
```

**Key Points:**
- Wave 1 MUST complete first (fixes tests)
- Wave 2 & 3 can run in parallel (no cross-dependency)
- Wave 4 requires BOTH Wave 2 & 3 (convergence)
- Wave 5 is pure cleanup (can be deferred)

---

## 🎁 What Makes This Plan Better

| Aspect | Original Wave-12 | Enhanced 5-Wave |
|--------|------------------|-----------------|
| **Duration** | 32-40 days | 5-6 days (84% faster) |
| **First Value** | Day 10-14 | 3-4 hours |
| **Test Gen Ships** | With full IDCE (day 32+) | Wave 2 standalone (day 1) |
| **Bundling** | Part A+B together | Unbundled, incremental |
| **Consolidation** | Mixed throughout | Deferred to end (Wave 5) |

**Why Better:**
1. **Incremental value** — Each wave ships independently
2. **Logical flow** — Test generation → coherence → intelligence loop
3. **No over-engineering** — Ship fast, iterate based on feedback
4. **User-facing early** — Wave 2 delivers `/generate-tests` immediately

---

## 🚀 Quick Start

```bash
# Wave 1: Foundation (3-4 hours)
/implement WAVE-1-FOUNDATION
# Fixes: 5 test collection errors → 10,296 tests clean

# Wave 2: Test Generation (8-10 hours)
/implement WAVE-2-TEST-GEN
# Ships: /generate-tests path/to/file.py

# Wave 3: Document Coherence (10-12 hours)
/implement WAVE-3-DOC-COHERENCE
# Ships: Auto-sync, auto-consolidate, post-refactor verification

# Wave 4: Intelligence Loop (12-14 hours)
/implement WAVE-4-INTELLIGENCE
# Ships: /intelligence-loop path/to/project (run until production ready)

# Wave 5: Consolidation (6-8 hours)
/implement WAVE-5-CONSOLIDATION
# Ships: 114→40 files, 30k→8k tokens, capability gate
```

---

## 📋 New MCP Tools

| Wave | MCP Tool | Purpose |
|------|----------|---------|
| 2 | `cortex_generate_tests` | Generate high-value tests for file |
| 3 | `cortex_verify_refactor` | Auto-run affected tests after refactor |
| 3 | `cortex_auto_consolidate` | Auto-consolidate duplicate sections |
| 4 | `cortex_intelligence_loop` | Run TDD cycles until DoD achieved |
| 5 | `cortex_load_core_rules` | Lazy load CORE rules from YAML |
| 5 | `cortex_load_audit_checklist` | Lazy load audit checks from YAML |

---

## 📈 Success Metrics

| Wave | Metric | Target | Measurement |
|------|--------|--------|-------------|
| 1 | Test collection errors | 0 | pytest --collect-only |
| 2 | Test generation accuracy | ≥80% high-value | Manual review |
| 3 | Accumulation prevention | Zero cleanup cycles | 30-day tracking |
| 4 | Intelligence loop success | ≥85% achieve Production Ready | Loop completion tracking |
| 5 | File reduction | 114 → 40 | Count orchestrator files |
| 5 | Token reduction | 30k → 8k (73%) | Token count prompt file |

---

## 🎯 Execution Status

- [ ] **WAVE-1:** Foundation Repair (0/3 stages)
- [ ] **WAVE-2:** Test Generation (0/6 stages)
- [ ] **WAVE-3:** Document Coherence (0/5 stages)
- [ ] **WAVE-4:** Intelligence Loop (0/6 stages)
- [ ] **WAVE-5:** Consolidation (0/5 stages)

**Next Action:** `/implement WAVE-1-FOUNDATION`

---

## 📚 References

- **Full Spec:** `MASTER-5-WAVE-PLAN-2026-02-13.yaml`
- **Original Vision:** `WAVE-12-INTELLIGENT-DEVELOPMENT-COHERENCE-ENGINE.yaml`
- **ENH-087:** Orchestrator Consolidation (Track 1 ✅ complete)
- **ENH-088:** Multi-Cycle TDD (✅ complete, 42 tests)
- **ENH-089:** EventBus Debugger (✅ complete, 68 tests)
- **ENH-101:** Change Coherence Engine (✅ complete, 113 tests)

---

**Last Updated:** 2026-02-13  
**Commit:** d9c87b1c4 (AC-MASTER-5-WAVE-PLAN-001)  
**Status:** ✅ APPROVED — Ready for execution
