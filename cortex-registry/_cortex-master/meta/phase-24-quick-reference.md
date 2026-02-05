# PHASE 24: QUICK REFERENCE — Architecture Integrity in Action
**Version:** 1.0 | **Created:** 2026-02-05

---

## 🎯 HOW IT WORKS (USER PERSPECTIVE)

### Scenario 1: Request Aligned with Active Phase ✅

**User:** `/implement Add JSON export to repository dashboard`

**cortex-architect Response:**

```markdown
## 🏗️ CORTEX Architect
**Author:** Asif Hussain | **Mode:** Design | **Routing:** cortex-designer ✅

---

### 🛡️ Architecture Integrity Check

| Check | Status | Details |
|-------|--------|---------|
| **Active Phase Match** | ✅ | Aligns with: phase-21 (JSON-First Rewrite) |
| **Completed Phase Conflict** | ✅ | No conflicts detected |
| **Regression Risk** | 0.12 | 🟢 Low |
| **Brittleness Risk** | 0.08 | 🟢 Low |
| **Verdict** | ✅ | PROCEED |

**Reasoning:** Request aligns perfectly with phase-21 objectives (JSON-first data layer). 
No architectural risks detected.

**Proceeding to LENS Context Gathering...**

---

### 📊 LENS Context

[... continues with normal DESIGN flow ...]
```

**Result:** Seamless execution, no friction for user

---

### Scenario 2: Significant Change Needs New Phase 📋

**User:** `/implement Convert all orchestrators to async/await pattern`

**cortex-architect Response:**

```markdown
## 🏗️ CORTEX Architect
**Author:** Asif Hussain | **Mode:** Design | **Routing:** cortex-designer ✅

---

### 🛡️ Architecture Integrity Check

| Check | Status | Details |
|-------|--------|---------|
| **Active Phase Match** | ⚠️ | No active phase covers async refactoring |
| **Completed Phase Conflict** | ✅ | No conflicts detected |
| **Regression Risk** | 0.45 | 🟡 Medium |
| **Brittleness Risk** | 0.35 | 🟡 Medium (major refactor) |
| **Verdict** | 📋 | CREATE_PHASE |

**Reasoning:** This is a significant architectural change affecting 28+ orchestrators. 
Should be tracked as a dedicated phase for:
- Planning & coordination
- Incremental rollout
- Rollback capability
- Dashboard visibility

---

### 📋 Phase Creation Recommended

**Suggested Phase:**
- **ID:** phase-25
- **Title:** Async Orchestrator Refactor
- **Priority:** P1 (architectural improvement)
- **Estimated Effort:** 2 weeks
- **Scope:** Core, Domain, and Support orchestrators
- **Dependencies:** None (independent refactor)

**Options:**
1️⃣ Type **"create phase"** to auto-generate phase YAML (recommended)
2️⃣ Type **"skip"** to proceed without phase tracking (⚠️ not recommended for this scope)
3️⃣ Type **"manual"** to create phase manually first

**Recommendation:** Create phase first for proper tracking and dashboard visibility.
```

**User:** `create phase`

**cortex-architect:**

```markdown
✅ **Phase 25 Created**

**File:** cortex-registry/_cortex-master/phases/active/phase-25-async-orchestrator-refactor.yaml  
**Status:** Active  
**Dashboard:** Will appear in dashboard within 60 seconds

**Proceeding with DESIGN flow...**

---

### 📊 LENS Context

[... continues with normal flow ...]
```

**Result:** User gets phase tracking automatically, master plan stays in sync

---

### Scenario 3: Request Conflicts with Completed Phase 🚫

**User:** `/implement Use SCREAMING_CASE for new configuration files`

**cortex-architect Response:**

```markdown
## 🏗️ CORTEX Architect
**Author:** Asif Hussain | **Mode:** Design | **Routing:** cortex-designer ✅

---

### 🛡️ Architecture Integrity Check

| Check | Status | Details |
|-------|--------|---------|
| **Active Phase Match** | ⚠️ | No active phase |
| **Completed Phase Conflict** | ❌ | **CONFLICTS DETECTED** |
| **Regression Risk** | 0.87 | 🔴 High |
| **Brittleness Risk** | 0.15 | 🟢 Low |
| **Verdict** | 🚫 | **BLOCK** |

**Reasoning:** Request violates completed phase commitments. High regression risk.

---

### 🚫 Request Blocked — Conflicts Detected

| Phase | Commitment | Conflict |
|-------|-----------|----------|
| **phase-15** | All files must use kebab-case naming | Request uses SCREAMING_CASE |
| **phase-18** | Intelligent file naming (CORE-028) | SCREAMING_CASE explicitly blocked |

**Regression Risk Factors:**
- ❌ Violates naming convention established in phase-15
- ❌ Creates inconsistency with 500+ existing files
- ❌ Breaks CORE-028 governance rule
- ❌ Would require retroactive fixes across codebase

---

### 🔧 Recommended Actions

1. **Modify Request (Recommended)**
   - Use kebab-case: `new-configuration.py`
   - Aligns with existing conventions
   - Zero regression risk

2. **Reopen Phase (If Truly Necessary)**
   - If SCREAMING_CASE is genuinely needed, propose phase-26:
     - Title: "Naming Convention Evolution"
     - Scope: Revisit phase-15 decisions with evidence
     - Get architect committee approval
   
3. **Architect Review**
   - This is a significant architectural decision
   - Requires careful consideration of tradeoffs
   - Should not be made lightly

---

### ⏸️ Execution HALTED

**Resolve conflicts before proceeding:**
- Modify request to use kebab-case, or
- Create phase-26 to justify naming convention change, or
- Provide evidence that SCREAMING_CASE is necessary

**Type:** `modify request` / `create phase 26` / `show evidence`
```

**Result:** User prevented from making regression-causing change, given clear remediation path

---

## 🔄 POST-COMPLETION FLOW

### Scenario: TDD Execution Completes Successfully

**After TDD finishes (all tests pass):**

```markdown
## 🧪 TDD Execution Complete

**Tests Passed:** 12/12 ✅  
**Files Modified:** 5  
**Brittleness Score:** 0.15 (🟢 Low)

---

### 🔄 Automatic Phase Completion (Phase 24)

**Updating master plan...**

✅ Phase 21 marked as completed  
✅ index.yaml statistics updated  
✅ Dashboard sync triggered  
✅ Enhancement history recorded  

**Master Plan Status:**
- **Active Phases:** 3 → 2 (phase-21 moved to completed)
- **Completion Rate:** 83% → 85%
- **Dashboard:** Updated (refresh in < 60 seconds)

**View Dashboard:** `cortex-registry/_cortex-master/dashboard/index.html`

---

### 📊 Architecture Decision Recorded

**Decision:** JSON-first data layer for repository intelligence  
**Rationale:** Performance (40x faster), simplicity, rapid iteration  
**Alternatives Rejected:** SQLite-first (premature optimization)  
**Impact:** phase-21 completed, no downstream phase conflicts  

**Recorded:** `cortex-registry/_cortex-master/decisions/dec-2026-02-05-json-first.yaml`

---

**Implementation Complete** ✅
```

**Result:** Zero manual toil, master plan automatically synced with implementation

---

## 🎯 KEY BENEFITS

### For Users
✅ **No wasted effort** — Invalid requests blocked before work begins  
✅ **Clear guidance** — Exact reasons for blocking + remediation steps  
✅ **Automatic tracking** — Phases created/updated without manual intervention  
✅ **Dashboard sync** — Always know current project status

### For Architects
✅ **Regression prevention** — Completed phases cannot be violated  
✅ **Architecture evolution tracking** — All decisions recorded with rationale  
✅ **Brittleness detection** — Real-time warnings during implementation  
✅ **Master plan accuracy** — 100% sync with actual implementation

### For Project Management
✅ **Real-time visibility** — Dashboard always reflects current state  
✅ **Phase tracking** — All work tracked in master plan  
✅ **Completion metrics** — Accurate progress reporting  
✅ **Decision history** — Understand why architecture choices made

---

## 🚨 COMMON PATTERNS

### Pattern: "Quick Fix" That's Actually Significant

**User:** `/fix Small typo in MasterOrchestrator docstring`

**Gate:** PROCEED ✅ (low regression risk, no phase needed)

---

**User:** `/fix Refactor MasterOrchestrator execute() method`

**Gate:** CREATE_PHASE 📋 (significant change, needs tracking)

---

### Pattern: New Feature vs Enhancement

**User:** `/implement Add logging to TDDOrchestrator`

**Gate:** PROCEED ✅ (enhancement to existing orchestrator, no phase needed)

---

**User:** `/implement New MetricsOrchestrator for observability`

**Gate:** CREATE_PHASE 📋 (new orchestrator, should be phase-XX)

---

### Pattern: Refactor vs Regression

**User:** `/refactor Extract common logic to helper function`

**Gate:** PROCEED ✅ (safe refactor, no architectural impact)

---

**User:** `/refactor Change event bus from sync to async`

**Gate:** BLOCK 🚫 (would break completed phase-01 event bus implementation)

---

## 📊 METRICS DASHBOARD

After Phase 24 deployment, track:

```
┌──────────────────────────────────────────────────────────┐
│  ARCHITECTURE INTEGRITY METRICS (30-Day Rolling)         │
├──────────────────────────────────────────────────────────┤
│  Requests Processed:         247                         │
│  ├─ PROCEED:                 198 (80%)                   │
│  ├─ CREATE_PHASE:             35 (14%)                   │
│  └─ BLOCK:                    14 (6%)                    │
│                                                           │
│  Regression Prevention:                                  │
│  ├─ Regressions Prevented:    14                         │
│  ├─ False Positives:           3 (1.2%)                  │
│  └─ Effectiveness:            98.8%                      │
│                                                           │
│  Performance:                                            │
│  ├─ Avg Gate Latency:        87ms                       │
│  ├─ Dashboard Sync Time:     42s avg                    │
│  └─ Phase Creation Time:      3.2s avg                  │
│                                                           │
│  Master Plan Sync:                                       │
│  ├─ Auto-Completed Phases:   12                         │
│  ├─ Auto-Created Phases:      8                         │
│  └─ Sync Accuracy:          100%                        │
└──────────────────────────────────────────────────────────┘
```

---

**Status:** ✅ QUICK REFERENCE COMPLETE  
**Next:** Implement Phase 24 (7-day sprint)  
**Goal:** Zero architectural regression, 100% master plan sync
