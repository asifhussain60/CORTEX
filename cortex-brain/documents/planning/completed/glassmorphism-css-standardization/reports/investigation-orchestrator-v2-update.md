# Investigation Orchestrator v2.0 Update
**Date:** January 3, 2026  
**Author:** Asif Hussain  
**Type:** Feature Enhancement

---

## 🎯 Summary

Updated Investigation Orchestrator to **v2.0** with **Holistic Architecture Review** mode for comprehensive gap analysis.

---

## ✨ What's New

### Dual Operation Modes

**Mode 1: Targeted Investigation** (existing behavior)
- Trigger: `investigate [issue description]`
- Deep root cause analysis for specific problems
- 6-phase workflow (DISCOVER → ANALYZE → DESIGN → IMPLEMENT → VALIDATE → DOCUMENT)

**Mode 2: Holistic Architecture Review** (NEW)
- Trigger: `investigate` (NO arguments)
- Comprehensive architecture review against acceptance criteria
- 6-phase workflow (H1-H6): Plan alignment → Gap analysis → Robustness → Roadmap → Automated fixes → Executive report

---

## 📋 Holistic Review Capabilities

### Phase H1: Plan Alignment Review
- Validates implementation vs `cortex-v5-holistic-refactor` plan
- Checks acceptance criteria from `FINAL-ACCEPTANCE-CRITERIA.md`
- Identifies missing components, partial implementations, deviations

### Phase H2: 11-Dimension Gap Analysis
1. ⚠️ **Missing Edge Cases** - Boundary conditions, unusual flows
2. 🔥 **Failure Modes** - Single points of failure, cascading failures
3. ⚡ **Race Conditions** - Concurrency issues, state conflicts
4. 🚀 **Integration & Deployment Pitfalls** - Rollout risks, config drift
5. 🔒 **Security Vulnerabilities** - Auth gaps, injection risks, data exposure
6. 🐌 **Performance Bottlenecks** - N+1 queries, memory leaks, slow operations
7. 📈 **Scalability Limits** - Hard limits, resource constraints
8. ⏮️ **Rollback & Recovery** - Backup strategies, disaster recovery
9. ✅ **Data Integrity & Validation** - Schema validation, constraint enforcement
10. 📦 **Dependency Risks** - Version conflicts, supply chain risks
11. 🛠️ **Maintainability Issues** - Technical debt, code duplication, documentation gaps

### Phase H3: Robustness Assessment
- Production-readiness scoring (error handling, logging, resilience, monitoring)
- Brittle pattern detection (hard-coded values, tight coupling, fragile assumptions)
- Robust alternative analysis (industry best practices, trade-offs, migration effort)
- Smarter solutions identification (async/await, Pydantic, event-driven, etc.)

### Phase H4: Implementation Roadmap
- Priority matrix (P0/P1/P2/P3 based on impact vs effort)
- 4-phase roadmap (1-2 weeks → 2-4 weeks → 4-8 weeks → 8-12 weeks)
- Resource estimation (developer hours, testing, documentation, deployment)
- Dependency ordering (Fix A before B)

### Phase H5: Automated Fixes
- Quick wins (try-catch blocks, type hints, docstrings, anti-pattern fixes)
- Configuration hardening (Pydantic validation, default values, schema enforcement)
- Test coverage improvements (unit tests, integration tests, edge case tests)

### Phase H6: Executive Report
- Stakeholder-friendly summary (400+ lines)
- Architecture health score (overall + per-dimension)
- Top 5 critical gaps with fix recommendations
- Top 3 smarter solutions with ROI analysis
- Prioritized implementation roadmap

---

## 📊 Output

**Total Documentation:** 4,300+ lines across 5 documents

**Directory Structure:**
```
cortex-brain/documents/investigations/holistic-review-{timestamp}/
├── architecture/
│   ├── gap-analysis-matrix.md (1500 lines, 11 dimensions)
│   ├── acceptance-criteria-scorecard.md (800 lines, plan validation)
│   └── robustness-assessment.md (1000 lines, production-readiness)
├── recommendations/
│   ├── high-priority-fixes.md (P0/P1 with code examples)
│   ├── architecture-enhancements.md (robust alternatives)
│   └── smarter-solutions.md (future-proof improvements)
├── implementation/
│   ├── implementation-roadmap.md (600 lines, 4-phase)
│   ├── automated-fixes-summary.md (quick wins applied)
│   └── code-changes/ (diffs for automated fixes)
└── reports/
    ├── holistic-review-executive-summary.md (400 lines, stakeholder)
    └── presentation-slides.md (optional deck)
```

---

## 🎯 Use Cases

### When to Use Holistic Review

1. **After major refactoring** - Validate changes didn't introduce regressions
2. **Before production deployment** - Ensure production-readiness
3. **Quarterly architecture reviews** - Proactive gap identification
4. **Post-incident analysis** - Find systemic issues, not just immediate cause
5. **Plan validation** - Check if implementation matches plan (e.g., v5 holistic refactor)

### Example Commands

```bash
# Holistic review (no arguments)
investigate

# Targeted investigation (specific issue)
investigate why continuation prompts not displaying
investigate find root cause of vision API timeout
```

---

## 🔗 Integration

### Master Orchestrator Routing
```yaml
- pattern: "^investigate$"  # NO arguments
  orchestrator: "investigation_orchestrator"
  mode: "holistic_review"
  priority: 8
```

### CORTEX.prompt.md Entry
```markdown
| `investigate` (NO arguments) | 🛡️ **Investigation (Holistic)** | `^investigate$` | 1.00 | regex | Architecture review → 11-dimension gap analysis → Roadmap + automated fixes |
```

---

## 📚 Documentation

**Main Specification:** `.github/prompts/cortex-investigate.prompt.md` (updated to v2.0)  
**Holistic Review Supplement:** `.github/prompts/cortex-investigate-holistic-review.prompt.md` (NEW, 900+ lines)

**Key Changes:**
1. Added "Dual Operation Modes" section
2. Updated trigger patterns to include `investigate` (no args)
3. Added Mode 2 specification reference
4. Split Output Documents into Mode 1 and Mode 2

---

## ✅ Status

- [x] Updated `cortex-investigate.prompt.md` to v2.0
- [x] Created `cortex-investigate-holistic-review.prompt.md` supplement
- [x] Documented 11-dimension gap analysis framework
- [x] Defined 6-phase holistic review workflow (H1-H6)
- [x] Specified output structure (4,300+ lines of docs)
- [x] Added integration points (Master Orch, CORTEX.prompt.md)
- [ ] Implement Python orchestrator (investigation_orchestrator_v2.py)
- [ ] Add holistic review route to Master Orchestrator
- [ ] Create acceptance tests for holistic review
- [ ] Update CORTEX.prompt.md Intent Router table

---

## 🎉 Impact

**Before:** Investigation Orchestrator only handled specific issues (targeted debugging)  
**After:** Investigation Orchestrator now performs comprehensive architecture reviews (proactive gap analysis)

**Benefits:**
- **Proactive:** Find issues before they become incidents
- **Comprehensive:** 11-dimension analysis vs single-issue focus
- **Actionable:** Prioritized roadmap with effort estimates
- **Automated:** Quick wins implemented automatically
- **Stakeholder-friendly:** Executive summary suitable for non-technical audience

**Next Steps:**
1. Implement Python orchestrator for holistic review mode
2. Wire into Master Orchestrator routing
3. Test against `cortex-v5-holistic-refactor` plan
4. Generate first holistic review report

---

**Files Modified:**
- `.github/prompts/cortex-investigate.prompt.md` (v1.0 → v2.0)

**Files Created:**
- `.github/prompts/cortex-investigate-holistic-review.prompt.md` (NEW, 900+ lines)
- `cortex-brain/documents/planning/active/glassmorphism-css-standardization/reports/investigation-orchestrator-v2-update.md` (THIS FILE)

**Total Lines Added:** 1,000+ lines of specification
