
**Purpose:** Search CORTEX codebase for brittleness, breakage points, and material production risks  
**Version:** 2.0.0  
**Date:** 2026-01-12  
**Governance:** CORE-002 (no root files), CORE-017 (governance enforcement), CORE-009 (plan organization), CORE-025 (intelligent challenge)
**Copyright © 2025-2026 Asif Hussain. All rights reserved.**

---
agent: agent
---

# 🔧 CORTEX Search-and-Fix – Production ## Output Format

**Three-part delivery:**
1. Executive summary (bullets only, no code, <2 min read)
2. Remediation plan (action items + phase assignments)
3. AC-ID list (ready to append to AC-INDEX.yaml)s & Risk Review

**Purpose:** Search CORTEX codebase for brittleness, breakage points, and material production risks  
**Version:** 2.0.0  
**Date:** 2026-01-12  
**Governance:** CORE-002 (no root files), CORE-017 (governance enforcement), CORE-009 (plan organization), CORE-025 (intelligent challenge)

---

## 🔗 MASTERORCHESTRATOR DELEGATION

**All findings delegated to unified orchestrator for planning:**

```bash
# Execute via MasterOrchestrator (central control)
python3 -m src.main "{user_intent}" --orchestrator master --format markdown
```

**MasterOrchestrator handles:**
- ✅ Load governance rules (tier0/tier1/tier2/tier3)
- ✅ Validate against SKULL rules
- ✅ Create AC-IDs for brittleness findings
- ✅ Append findings to AC-INDEX.yaml
- ✅ Update master-plan.yaml with new AC-IDs
- ✅ Update progress-tracker.json
- ✅ Trigger SyncOrchestrator

**Do NOT:**
- ❌ Directly modify AC-INDEX.yaml
- ❌ Directly modify progress-tracker.json
- ❌ Create separate brittleness files
- ❌ Update tracker manually

---

## 🛡️ REGRESSION PREVENTION (Reference Only)

**Reference:** CORTEX.prompt.md maintains unified regression check via MasterOrchestrator.

**This prompt DOES NOT perform direct file access.** All findings delegated to Python orchestrator.

**Why not embed code?** When MasterOrchestrator is updated, regression check automatically improves for all prompts (DRY principle).

---

## 🛡️ INTELLIGENT CHALLENGE PROTOCOL (CORE-025)

**Purpose:** Validate findings against governance and feasibility.

**Implementation:** Delegated to MasterOrchestrator → RequestValidator.

**Reference:** `.github/prompts/CORTEX-ALIGN.prompt.md § INTELLIGENT CHALLENGE PROTOCOL`

---

## 📊 Analysis Scope
- Prioritize by real-world impact and likelihood; explain how failures manifest at runtime.

## Repeatable “Tool” Behavior (avoid file bloat)
- Do **NOT** create new files each run.
- Update/extend the existing plan via **one canonical record** inside `#file:cortex-exec.prompt.md`.
- If an entry already exists, update it (status, severity, evidence paths, recommendation, owner, lastReviewed) rather than duplicating.
- Use the structured format below for all updates.

## Required Output Format
1) A concise summary (paragraphs + bullets), broken into sections.
2) A single YAML (preferred) or JSON “update payload” that can be pasted into `#file:cortex-exec.prompt.md` to incrementally maintain the plan.
3) The payload must be **idempotent**: same findings should map to the same stable IDs and update in-place.

---

# Step-by-step Instructions

## 1) Repo-wide Discovery (Brief Scan)
Identify core infrastructure patterns:
- Service boundaries and data flows (sync/async paths)
- State stores (databases, tracking files, registries)
- Configuration and secrets management
- Observability (logging, audit trails)
- Security controls (auth, access, encryption)

## 2) Brittleness Analysis (Map Real Risks)
For each category, find concrete problems where they live:
- **Correctness & Edge Cases:** YAML encoding, pattern matching fallbacks, test evidence gaps
- **State & Concurrency:** State loss, database contention, sync drift
- **Integration Risks:** Schema evolution, contract breaking
- **Partial Failure:** No retry/rollback, phase blocking on errors
- **Data Integrity:** No backups before writes, corruption repair gaps
- **Security:** Secrets exposure, audit log sensitivity
- **Dependencies:** Python version traps, YAML version issues, pytest assumptions
- **Environment:** Hardcoded paths, no staging/prod detection
- **Scalability:** Unbounded logs, missing caching, no debouncing
- **Operability:** No health checks, blind spots in observability

## 3) Prioritize by Real Impact
For each issue:
- **Severity:** Critical/High/Medium/Low
- **What breaks:** Data loss, outage, silent corruption, exposure
- **Likelihood:** Based on production reality
- **Manifestation:** What users/operators see
- **Detection gaps:** Why it goes unnoticed
- **Minimal fix:** Simplest solution within architecture
- **Verification:** Smallest test to validate

---

# Response Requirements (what to produce)

## A) Executive Summary with Bullet Points (No Code)

**FORMAT:** Clean, concise executive summary readable in <2 minutes by technical leader.

**Output sections:**
- **🎯 Current State** (1-2 bullets: what's working, what's at risk)
- **🚨 Critical Findings** (top 3-5 blockers, organized by category)
- **⚠️ High-Priority Gaps** (next tier of issues)
- **✅ Quick Wins** (low effort, high impact fixes)
- **📋 Evidence-Based Issues** (validation chain, test gaps, false positives)
- **🔄 State & Sync Hazards** (tracker drift, concurrency, persistence)
- **🛡️ Security & Governance Gaps** (rule conflicts, exposure risks)
- **📈 Scalability & Performance** (hot paths, unbounded growth)

**Each finding uses this format (no code blocks):**
- **AC-ID:** AC-CATEGORY-NNN
- **Title:** Concise capability description
- **Priority:** 🔴 Critical | 🟠 High | 🟡 Medium | 🟢 Low
- **Manifests as:** What users/operators see at runtime
- **Affects:** File paths or components (no snippets)
- **If unfixed:** Concrete failure mode (data loss, corruption, outage, exposure)
- **Fix:** One-line summary of minimal-impact solution
- **Test:** How to validate the fix (one-line)
- **Phase:** Which phase implements (9/10/later)

**CORTEX-specific focus:**
- Evidence-based tracking: Test passing rate vs completion claims
- Governance conflicts: Rule precedence (T0 vs T1 vs T2 vs T3)
- State machine gaps: Missing lifecycle states (PENDING → COMPLETE)
- Tracker sync drift: progress-tracker.json → plan-viewer-data.json mismatch
- AC-ID chain: AC-INDEX → TodoManager → tracker → evidence integrity

## B) Remediation & Alignment Plan

**OUTPUT STRUCTURE:**

1. **Remediation Plan**
   - Day-zero critical fixes (must implement before Phase 10)
   - 30-day high-priority alignment items
   - 60-day technical debt paydown
   - Phase assignments (when each fix is implemented)

2. **AC-ID Entries** (JSON array, ready for MasterOrchestrator ingestion)
   - Concise AC-ID definitions with priority/phase
   - Test file references (no path detail, just existence check)
   - Owner/component assignment
   - Dependencies between AC-IDs

3. **Governance Alignment**
   - Which SKULL rules are at risk
   - Governance tier conflicts identified
   - Recommended rule enhancements
   - Validation checkpoints required

4. **Implementation Sequencing**
   - Critical path for production readiness
   - Phase gates to enforce
   - State synchronization requirements
   - Smoke test coverage gaps

**Format:** Bullets only, no code blocks, <3 minutes to read per issue.


---

# CORTEX-Specific Review Checklist

Before completing the analysis, verify these CORTEX 6-specific patterns:

## Evidence-Based Tracking
- [ ] Check if completion percentages match actual test pass rates
- [ ] Verify AC-INDEX.yaml entries have corresponding test files
- [ ] Validate progress-tracker.json claims backed by test evidence
- [ ] Confirm plan-viewer-data.json synced from tracker (not hardcoded)

## Governance Integrity
- [ ] All 23 SKULL rules (CORE-001 to CORE-023) load without encoding errors
- [ ] Tier precedence enforced (T0 > T1 > T2 > T3) in GovernanceMerger
- [ ] Governance violations block execution with clear diagnostic messages
- [ ] Rule conflicts logged to audit trail with resolution strategy

## Orchestrator Lifecycle
- [ ] All orchestrators implement 7-state lifecycle (PENDING → IN_PROGRESS → COMPLETE/FAILED/BLOCKED)
- [ ] TodoManager tasks persist across orchestrator restarts
- [ ] Phase DoR/DoD validation blocks execution correctly
- [ ] Failed phases trigger rollback or leave clean partial state

## State Management
- [ ] progress-tracker.json is single source of truth for completion
- [ ] No dual-write patterns (tracker and plan-viewer-data.json)
- [ ] SQLite databases use WAL mode for concurrency
- [ ] State files have backup/recovery mechanisms

## Pattern Routing
- [ ] PatternRouter regex patterns cover 90%+ of intents
- [ ] Unmatched patterns logged for pattern expansion
- [ ] LLM fallback enabled when confidence < threshold
- [ ] Intent classification failures don't crash MasterOrchestrator

## Test Infrastructure
- [ ] pytest discovery finds all test_*.py files
- [ ] Test evidence validator runs without false positives
- [ ] Coverage reports accurately reflect implemented code
- [ ] Smoke tests validate critical paths (governance, routing, execution)

## Audit Trail
- [ ] All operations log with correlation IDs
- [ ] Audit logs queryable by AC-ID, phase, orchestrator
- [ ] Hash chain integrity validated on startup
- [ ] JSONL files rotate before exceeding size limits

## Data Sync Pipeline
- [ ] sync_plan_viewer_data.py runs after every tracker update
- [ ] plan-viewer.html loads data from plan-viewer-data.json only
- [ ] No hardcoded status values in HTML templates
- [ ] Dashboard refresh detects stale data automatically

---

---

# AC-ID Generation

All findings MUST flow through the governance pipeline:

1. Query AC-INDEX.yaml for highest existing AC-ID number in each category
2. Generate new AC-IDs: `AC-<CATEGORY>-<NNN>` (e.g., AC-BRITTLE-015)
3. Append to AC-INDEX.yaml with required fields: id, title, description, status, priority, phase, category, tests
4. MasterOrchestrator reads AC-INDEX → Creates TodoManager tasks → Updates progress-tracker.json
5. TDD-Master enforces test-first implementation (CORE-019)
6. Evidence tracked via EnterpriseAuditLogger

**Critical Rules:**
- All brittleness issues MUST become AC-IDs
- AC-IDs MUST flow through TodoManager
- Test evidence REQUIRED before marking implemented

---

# Begin the analysis now
Execute comprehensive brittleness review across CORTEX infrastructure. Produce executive summary (bullets, <2 min read) + remediation plan + AC-ID entries ready for AC-INDEX.yaml append.
