# CORTEX 6.0 Holistic Design Review Package

**Review Date:** 2026-01-10  
**Version:** 6.0.0  
**Review Round:** 2 (Post-Gap Analysis)  
**Current Score:** 83/100  
**Target Score:** 95+/100  

---

## 📋 START HERE

**You are reviewing DESIGN SPECIFICATIONS for CORTEX 6.0.**

### Before Reading Anything Else:

1. ✅ **READ FIRST:** `cx6-reviewer-guidance.md` (10 minutes)
   - **Purpose:** Prevents invalid recommendations
   - **Contains:** Common pitfalls, CORTEX philosophy, scoring calibration

2. ✅ **READ SECOND:** `cx6-review-round2-instructions.md` (15 minutes)
   - **Purpose:** Comprehensive review process
   - **Contains:** Focus areas, review questions, output format

3. ✅ **CONTEXT:** `cx6-path-to-95-summary.md` (5 minutes)
   - **Purpose:** Executive summary of current state
   - **Contains:** Score breakdown, 6 critical AC-IDs, expected progression

---

## 📁 Document Index

### 🚨 CRITICAL (Must Read)

| Document | Purpose | Read Time | Priority |
|----------|---------|-----------|----------|
| `cx6-reviewer-guidance.md` | Prevent invalid recommendations | 10 min | **P0** |
| `cx6-review-round2-instructions.md` | Review process + focus areas | 15 min | **P0** |
| `cx6-path-to-95-summary.md` | Executive summary (83 → 95+) | 5 min | **P0** |

### 📐 Design Specifications (Primary Review Target)

| Document | Lines | Focus Area | Review Time |
|----------|-------|------------|-------------|
| `cx6-security-layer.yaml` | 717 | Threat model, ActionPolicyEngine, path sandboxing | 30 min |
| `cx6-routing-spec.yaml` | ~500 | Pattern matching, conflict detection, normalization | 20 min |
| `cx6-rollout-lifecycle.yaml` | ~400 | SHADOW→CANARY→ACTIVE, rollback triggers | 15 min |
| `cx6-architecture-detailed.yaml` | ~600 | 4-tier governance, orchestration pipeline | 20 min |

### 📊 Supporting Context

| Document | Purpose | When to Read |
|----------|---------|--------------|
| `cx6-gpt-challenges-rebuttal.md` | Technical rebuttal of Round 1 invalid recs | After your review |
| `cx6-implementation-status.yaml` | AC-ID status tracking | Quick reference |
| `gpt-analysis.txt` | Round 1 review (83/100 score) | Historical context |

### 🗂️ Source Files (Reference Only)

| File | Location | Purpose |
|------|----------|---------|
| AC-INDEX.yaml | `cortex-brain/tier1/acceptance-criteria/` | All acceptance criteria (78 total) |
| core-rules.yaml | `cortex-brain/tier0/governance/` | 21 SKULL rules (Tier 0 governance) |
| progress-tracker.json | `cortex-brain/tier1/tracking/` | Epic status, phase tracking |

---

## 🎯 Review Objective

### Current State (Round 1 Results)

**Design Score:** 83/100

**Gaps Identified:**
1. ❌ Approval protocol missing (-10 points)
2. ❌ Path sandboxing holes (-7 points)
3. ❌ Unicode normalization missing (-5 points)
4. ❌ PREFIX tie-breaking incomplete (-1 point)
5. ❌ Rollout triggers naive (-2 points)
6. ⚠️ Command execution flaw (-3 points) - **CHALLENGED**
7. ⚠️ Shadow mode underspecified (-2 points) - **CHALLENGED**

**Invalid Recommendations (Rejected):**
- "dir command requires shell=True" (python/pwsh wrappers solve this)
- "Shadow mode has no side-effect controls" (DRY_RUN exists, undocumented)
- "Argument validation underspecified" (incremental via TDD, not upfront)

---

### Target State (Round 2 Goal)

**Design Score:** 95+/100

**6 Critical AC-IDs Added:**
1. ✅ **AC-SECURITY-005:** Approval State Machine (+10 points)
2. ✅ **AC-SECURITY-006:** Canonical Path Resolution (+7 points)
3. ✅ **AC-ROUTE-004:** Unicode-Safe Normalization (+5 points)
4. ✅ **AC-ROUTE-005:** Complete PREFIX Tie-Breaking (+1 point)
5. ✅ **AC-ROLLOUT-004:** Statistical Trigger Guards (+2 points)
6. ✅ **AC-SECURITY-008:** Cross-Platform File Ops (+3 points)

**Your Task:**
- Validate these 6 AC-IDs fully address the gaps
- Identify any remaining issues (critical/high only)
- Confirm 95+ score achievable

---

**Ready? Start with `cx6-reviewer-guidance.md`**

**End Goal:** YAML findings file confirming 95+ score ✅

---

**Last Updated:** 2026-01-10T22:30:00Z
